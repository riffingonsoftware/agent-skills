#!/usr/bin/env python3
"""Make or delete a throwaway snapshot of a change for the review skill.

Usage:
  snapshot.py create CHECKOUT [--rev REV | --pr URL]
  snapshot.py remove PATH

create clones CHECKOUT with `git clone --shared` into a new temporary directory and
checks out the change: HEAD plus the checkout's uncommitted and untracked files, REV,
or the head of the PR at URL. In CHECKOUT it runs only `git rev-parse`, `git diff-index`,
`git ls-files` and `mise trust --show`, which leave its index alone. It prints `repo:`, `head:` and, for a
PR, `base:` lines.

mise doesn't carry a checkout's trust over to a clone. create trusts each folder in the
snapshot that holds mise config when the checkout trusts the same folder and every file mise
reads anywhere in the snapshot matches the checkout's working tree byte for byte, with no
miserc file or link among them. It marks every other such folder ignored, so even `mise exec`
and `mise run`, which trust config on their own, skip it, and prints an `untrusted:` line for
it: the snapshot's mise config differs from the checkout's working tree, or the checkout
doesn't trust that folder. Trusted config can still run files the change edits, such as an
`env._.source` script or a `mise.lock` download.

remove deletes a snapshot given its repo path or that path's parent, and refuses any
directory that create didn't make. It first clears the trust and ignore marks create set.
"""
import argparse
import collections
import contextlib
import fnmatch
import os
import shutil
import signal
import stat
import subprocess
import sys
import tempfile

PREFIX = "review-snapshot-"
MARKER = ".review-snapshot"
# Lowercased names of the files mise reads at a config root: config, local and per-env files, and miserc files.
MISE_NAMES = (".miserc*.toml", ".mise.*toml", ".tool-versions", "mise.*toml")
# Folders mise reads every config and conf.d file from; .config/ also holds mise.toml and miserc.toml variants.
MISE_DIRS = ((".config", "mise"), (".mise",), ("mise",))
MISE_CONFIG_NAMES = ("mise.*toml", "miserc*.toml")
MISE_PREFIXES = (".config", ".mise", ".tool-versions", "mise")

class Failure(Exception):
    pass


def run(*args, name=None):
    result = subprocess.run(list(args), capture_output=True, encoding="utf-8", errors="surrogateescape")
    if result.returncode:
        raise Failure(f"{name or ' '.join(args[:2])}: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def git(repo, *args):
    return run("git", "-C", repo, *args, name=f"git {args[0]} in {repo}")


def commit(repo, rev):
    return git(repo, "rev-parse", "--verify", "--end-of-options", f"{rev}^{{commit}}").strip()


def mise_roots(directory):
    # `mise trust --show` prints "<root>: trusted" or "<root>: untrusted" for directory and its parents.
    roots = {}
    for line in run("mise", "-C", directory, "trust", "--show").splitlines():
        root, sep, status = line.rpartition(": ")
        if sep and status in ("trusted", "untrusted"):
            roots[os.path.normcase(os.path.realpath(os.path.expanduser(root)))] = status == "trusted"
    return roots


def fold(name):
    # macOS and Windows open a file whatever the case of its name, and so does mise. APFS folds case (so "ſ" is "s"),
    # and NTFS compares uppercased names (so "ı" is "I"); folding both ways matches either.
    return name.upper().casefold()


def mise_file(parts):
    """Whether a path's folded parts, relative to a config root, name a file or folder mise reads there."""
    if len(parts) == 1:
        return parts[0] in (".config", ".mise", "mise") or any(fnmatch.fnmatchcase(parts[0], name) for name in MISE_NAMES)
    if len(parts) == 2 and parts[0] == ".config":
        return any(fnmatch.fnmatchcase(parts[1], name) for name in MISE_CONFIG_NAMES)
    return any(tuple(parts[:len(folder)]) == folder and len(parts) > len(folder) for folder in MISE_DIRS)


def mise_entries(repo):
    """Map each config root in the snapshot, relative to it, to the mise files and links under that root."""
    # Walks the files, not git's list, so an untracked nested repository copied whole is covered too.
    roots = collections.defaultdict(list)
    for folder, dirs, files in os.walk(repo):
        dirs[:] = [name for name in dirs if name != ".git"]
        # os.walk doesn't descend into a linked folder, so check it as an entry.
        for name in files + [name for name in dirs if is_link(os.path.join(folder, name))]:
            parts = os.path.relpath(os.path.join(folder, name), repo).split(os.sep)
            folded = [fold(part) for part in parts]
            for depth in range(len(parts)):
                if folded[depth].startswith(MISE_PREFIXES) and mise_file(folded[depth:]):
                    roots[os.path.join(*parts[:depth]) if depth else ""].append(os.path.join(*parts))
    return roots


def same_regular_file(a, b):
    if is_link(a) or is_link(b) or not os.path.isfile(a) or not os.path.isfile(b):
        return False
    with open(a, "rb") as left, open(b, "rb") as right:
        return left.read() == right.read()


def trust_mise(checkout, repo, marker):
    # A miserc file can point mise at any file name and applies below its folder, and a link can point at any file,
    # so trust nothing when either appears or any mise file differs from the checkout's working tree.
    if not shutil.which("mise"):
        return []
    roots = mise_entries(repo)
    paths = [path for entries in roots.values() for path in entries]
    unchanged = all("miserc" not in fold(path) and same_regular_file(os.path.join(repo, path), os.path.join(checkout, path))
                    for path in paths)
    untrusted = []
    for root in sorted(roots):
        target = os.path.realpath(os.path.join(repo, root))
        source = os.path.realpath(os.path.join(checkout, root))
        # Record the root before marking it, so remove clears the mark even if create is killed in between.
        with open(marker, "a", encoding="utf-8", errors="surrogateescape") as file:
            file.write(target + "\0")
        if unchanged and os.path.isdir(source) and mise_roots(source).get(os.path.normcase(source), False):
            run("mise", "trust", "--", target)
        else:
            run("mise", "trust", "--ignore", "--", target)
            untrusted.append(target)
    return untrusted


def release_mise(snapshot):
    # Clear create's trust and ignore marks; --untrust clears both. A check can replace a root with a file, or with a
    # link mise would follow out of the snapshot, so delete the repo first and untrust fresh empty folders at each root.
    repo = os.path.join(snapshot, "repo")
    with open(os.path.join(snapshot, MARKER), encoding="utf-8", errors="surrogateescape") as file:
        roots = sorted(set(filter(None, file.read().split("\0"))))
    if not roots:
        return
    if not shutil.which("mise"):
        raise Failure(f"mise isn't on PATH, so the trust marks on {', '.join(roots)} can't be cleared")
    # clear unlinks a repo a check replaced with a link or file, rather than following it.
    clear(repo)
    real = os.path.realpath(repo)
    for root in roots:
        if os.path.commonpath([real, root]) == real:
            os.makedirs(root, exist_ok=True)
            run("mise", "trust", "--untrust", "--", root)
    clear(repo)


def is_link(path):
    # os.path.islink misses Windows junctions.
    return os.path.islink(path) or bool(
        os.path.lexists(path) and getattr(os.lstat(path), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )


def writable(path):
    mode = os.lstat(path).st_mode
    os.chmod(path, mode | (stat.S_IRWXU if stat.S_ISDIR(mode) else stat.S_IWRITE))


def delete(path):
    # rmtree stops at read-only files, such as fetched packs on Windows, and at read-only directories a check left.
    # Make the tree writable first without following links, so nothing outside it changes.
    writable(path)
    for root, dirs, files in os.walk(path):
        dirs[:] = [name for name in dirs if not is_link(os.path.join(root, name))]
        for name in dirs + files:
            if not is_link(os.path.join(root, name)):
                writable(os.path.join(root, name))
    shutil.rmtree(path)


def clear(path):
    if os.path.islink(path) or os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        delete(path)


def copy_uncommitted(checkout, repo):
    changed = git(checkout, "diff-index", "-z", "--name-only", "HEAD").split("\0")
    untracked = git(checkout, "ls-files", "-z", "-o", "--exclude-standard").split("\0")
    root = os.path.normcase(os.path.realpath(repo))
    for path in filter(None, changed + untracked):
        nested = path.endswith("/")
        path = path.rstrip("/")
        source, target = os.path.join(checkout, path), os.path.join(repo, path)
        # A tracked symlink can differ only in case from a new directory on a case-insensitive filesystem.
        parent = os.path.normcase(os.path.realpath(os.path.dirname(target)))
        if os.path.commonpath([root, parent]) != root:
            raise Failure(f"{path}: its directory in the snapshot resolves outside it")
        if nested:
            # ls-files lists an untracked repository as one directory entry.
            clear(target)
            shutil.copytree(source, target, symlinks=True)
            continue
        if os.path.isdir(source) and not os.path.islink(source):
            # A file replaced by a directory; ls-files lists the files in it.
            if not os.path.isdir(target) or os.path.islink(target):
                clear(target)
            continue
        clear(target)
        if not os.path.lexists(source):
            continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if os.path.islink(source):
            os.symlink(os.readlink(source), target, target_is_directory=os.path.isdir(source))
        else:
            shutil.copy2(source, target, follow_symlinks=False)


def create(args):
    checkout = git(os.path.abspath(args.checkout), "rev-parse", "--show-toplevel").strip()
    if args.pr:
        pr = run("gh", "pr", "view", args.pr, "--json", "number,headRefOid,baseRefOid,url", "--jq",
                 '[.number, .headRefOid, .baseRefOid, .url] | @tsv').strip().split("\t")
        number, head, base, url = pr
    else:
        head, base = commit(checkout, args.rev or "HEAD"), None
    tmp = tempfile.mkdtemp(prefix=PREFIX)
    repo, marker = os.path.join(tmp, "repo"), os.path.join(tmp, MARKER)
    made = False
    try:
        open(marker, "w").close()
        run("git", "clone", "-q", "--shared", "--no-checkout", "--", checkout, repo)
        if args.pr:
            git(repo, "fetch", "-q", "--no-tags", "--", url.rsplit("/pull/", 1)[0],
                f"+refs/pull/{number}/head:refs/review/head", f"+{base}:refs/review/base")
            fetched = commit(repo, "refs/review/head")
            if fetched != head:
                raise Failure(f"fetched head {fetched} is not the PR's headRefOid {head}")
        git(repo, "checkout", "-q", "--detach", head)
        if not args.rev and not args.pr:
            copy_uncommitted(checkout, repo)
        untrusted = trust_mise(checkout, repo, marker)
        made = True
    finally:
        if not made:
            try:
                # Report the original error, not a failed cleanup.
                with contextlib.suppress(Failure, OSError):
                    release_mise(tmp)
            finally:
                delete(tmp)
    print(f"repo: {repo}")
    print(f"head: {head}")
    if base:
        print(f"base: {base}")
    for root in untrusted:
        print(f"untrusted: {root}")


def remove(args):
    given = os.path.abspath(args.path)
    if is_link(given):
        sys.exit(f"refusing {given}: it is a symlink")
    snapshot = os.path.dirname(given) if os.path.basename(given) == "repo" else given
    marker = os.path.join(snapshot, MARKER)
    real, temp = os.path.realpath(snapshot), os.path.realpath(tempfile.gettempdir())
    if is_link(snapshot):
        sys.exit(f"refusing {snapshot}: it is a symlink")
    if not os.path.isfile(marker) or is_link(marker):
        sys.exit(f"refusing {snapshot}: it has no {MARKER} marker")
    if os.path.normcase(os.path.dirname(real)) != os.path.normcase(temp):
        sys.exit(f"refusing {snapshot}: it is not directly inside {temp}")
    if not os.path.basename(real).startswith(PREFIX):
        sys.exit(f"refusing {snapshot}: its name doesn't start with {PREFIX}")
    release_mise(real)
    # Delete the marker last, so a failed remove can be rerun.
    clear(os.path.join(real, "repo"))
    delete(real)
    print(f"removed: {real}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    make = commands.add_parser("create", help="snapshot a change")
    make.add_argument("checkout", help="the user's checkout of the repository")
    source = make.add_mutually_exclusive_group()
    source.add_argument("--rev", help="snapshot this commit instead of the uncommitted change")
    source.add_argument("--pr", metavar="URL", help="snapshot this PR's head and fetch its base")
    make.set_defaults(func=create)
    drop = commands.add_parser("remove", help="delete a snapshot")
    drop.add_argument("path", help="the repo path create printed, or its parent")
    drop.set_defaults(func=remove)
    args = parser.parse_args()
    # Turn a harness timeout's SIGTERM into SystemExit, so create deletes its temporary directory.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    try:
        args.func(args)
    except (Failure, OSError) as exc:
        sys.exit(f"error: {exc}")


if __name__ == "__main__":
    main()
