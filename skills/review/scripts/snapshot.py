#!/usr/bin/env python3
"""Make or delete a throwaway snapshot of a change for the review skill.

Usage:
  snapshot.py create CHECKOUT [--rev REV | --pr URL]
  snapshot.py remove PATH

create clones CHECKOUT with `git clone --shared` into a new temporary directory and
checks out the change: HEAD plus the checkout's uncommitted and untracked files, REV,
or the head of the PR at URL. In CHECKOUT it runs only `git rev-parse`, `git diff-index`
and `git ls-files`, which leave its index alone. It prints `repo:`, `head:` and, for a
PR, `base:` lines.

remove deletes a snapshot given its repo path or that path's parent, and refuses any
directory that create didn't make.
"""
import argparse
import os
import shutil
import signal
import stat
import subprocess
import sys
import tempfile

PREFIX = "review-snapshot-"
MARKER = ".review-snapshot"


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
    try:
        open(os.path.join(tmp, MARKER), "w").close()
        repo = os.path.join(tmp, "repo")
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
    except BaseException:
        delete(tmp)
        raise
    print(f"repo: {repo}")
    print(f"head: {head}")
    if base:
        print(f"base: {base}")


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
    # Delete the marker last, so a failed remove can be rerun.
    if os.path.lexists(os.path.join(real, "repo")):
        delete(os.path.join(real, "repo"))
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
