#!/usr/bin/env python3
"""Collect agent session signals for the agent-retro skill.

Usage:
  collect.py --since YYYY-MM-DD [--until YYYY-MM-DD] [--repo PATH]...
  collect.py --context SESSION_ID_PREFIX REGEX [--around N]

Reads the session logs of each supported harness that exists on this machine
and skips the rest. Prints tab-separated sections: harnesses, sessions,
signals, repeated commands, memories, and Remove-When trailers. Subagent sessions are
folded into the session that started them; sessions that ran agent-retro are
listed but their signals are skipped; one-shot sessions (see one_shot) are dropped. Exits 2 when a log line can't be parsed.

Supported: Claude Code (~/.claude/projects), Codex (~/.codex/sessions).
Repeated-command detection is a heuristic: it groups shell commands by program
and subcommand, and inline scripts by the paths and hosts they touch.
"""
import argparse
import collections
import datetime as dt
import glob
import json
import os
import re
import shlex
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude", "projects")
CODEX = os.path.join(HOME, ".codex", "sessions")
CODEX_MEMORIES = os.path.join(HOME, ".codex", "memories")

CORRECTION = re.compile(
    r"^(no\b|nope|wait\b|hmm|stop\b|actually\b|again\b)|\b(didn'?t|don'?t|doesn'?t|wrong|instead|i said|i asked|"
    r"remind me|why did|why are|that'?s not|not what|you forgot|you missed|still)\b",
    re.I,
)
AUTH = re.compile(
    r"\b(401|403|unauthori[sz]ed|not authenticated|authentication required|(sign|log) ?in again|"
    r"(token|session|credentials?) (has |have )?expired|expired (token|session|credentials?)|re-?authenticate)\b",
    re.I,
)
# Failures a pipe or `;` hid behind exit 0, such as `cmd 2>&1 | tail`; only the shell's, aws's and gh's own wording.
MASKED = re.compile(
    r"\b(?:ba|z)?sh: (?:line \d+: )?[\w./+-]+: command not found|(?:zsh|\(eval\)):(?:\d+:)? command not found: \S+|"
    r"aws: \[ERROR\]: An error occurred \(\w+\)|\(HTTP 40[13]\)"
)
DENIED = re.compile(r"doesn'?t want to proceed|rejected by user|permission denied by|denied by (the )?user|blocked by hook|not approved", re.I)
# checkout --, restore and stash also undo the deliberate breaks of a fail-without-the-fix check.
REVERT = re.compile(r"\bgit (revert\b|reset --hard)")
BROWSER = re.compile(r"preview_|browser|playwright|chrome|puppeteer", re.I)
SKIP_USER = (
    "<task-notification", "Context handoff", "<command-", "<local-command", "Caveat:", "This session is being continued",
    "Delegated task", "<environment_context", "<user_instructions", "# AGENTS.md", "<turn_aborted", "<system-reminder",
    "<artifact-content",
)
# Everyday exploration and shell syntax; repeating these is not a procedure worth a script.
IGNORED_PROGRAMS = {
    "awk", "base64", "basename", "break", "case", "continue", "cat", "cd", "chmod", "command", "cp", "cut", "date", "diff", "dirname", "do",
    "done", "du", "echo", "elif", "else", "env", "esac", "exit", "export", "false", "fi", "file", "find", "for", "grep",
    "head", "if", "jq", "ln", "local", "ls", "mkdir", "mv", "nl", "printf", "pwd", "readlink", "realpath", "return",
    "rg", "rm", "sed", "set", "shasum", "sleep", "sort", "source", "stat", "tail", "tee", "test", "then", "timeout",
    "touch", "tr", "true", "uniq", "until", "wc", "which", "while", "xargs",
}
IGNORED_GIT = {
    "add", "branch", "checkout", "clone", "commit", "diff", "fetch", "grep", "log", "ls-files", "merge-base", "pull",
    "push", "remote", "rev-list", "rev-parse", "show", "stash", "status", "switch", "worktree",
}
SUBCOMMAND_PROGRAMS = {"aws", "brew", "cargo", "chezmoi", "docker", "gh", "git", "go", "kubectl", "make", "mise", "npm", "pnpm", "xcrun"}
INTERPRETERS = {"bash", "node", "perl", "python", "python3", "ruby", "sh", "zsh"}
TARGET = re.compile(r"(?:https?://([\w.-]+))|((?:~|/Users/[^/\s'\"]+|/home/[^/\s'\"]+)(?:/[\w.-]+){1,2})|([\w.-]+\.sqlite3?)")

errors = []


def parse_ts(value):
    if isinstance(value, (int, float)):
        return dt.datetime.fromtimestamp(value, dt.timezone.utc)
    if not value:
        return None
    value = value.replace("Z", "+00:00")
    # Python 3.9's fromisoformat accepts only 3 or 6 fractional digits.
    value = re.sub(r"\.(\d{1,6})\d*(?=[+-])", lambda m: "." + m.group(1).ljust(6, "0"), value)
    return dt.datetime.fromisoformat(value)


def clip(text, n=200):
    text = re.sub(r"[\s\x00-\x1f\x7f]+", " ", text or "").strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def read_jsonl(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError as exc:
            # A live session can end in a half-written, unterminated line.
            if number != len(lines) or line.endswith("\n"):
                errors.append(f"{path}:{number}: {exc}")


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(text_of(block.get("text", block.get("content", ""))) if isinstance(block, dict) else str(block) for block in content)
    if isinstance(content, dict):
        return text_of(content.get("text", content.get("content", "")))
    return "" if content is None else str(content)


class Session:
    def __init__(self, harness, sid, path):
        self.harness, self.id, self.path = harness, sid, path
        self.parent = None
        self.cwd = ""
        self.start = None
        self.events = []  # (ts, kind, text)
        self.commands = []  # (ts, shell command)
        self.retro = False
        self.subagents = 0
        self.is_subagent = False
        self.root_path = None

    def add(self, ts, kind, text):
        self.events.append((ts, kind, text))
        if ts and (self.start is None or ts < self.start):
            self.start = ts


def load_claude(path):
    parts = path.split(os.sep)
    sid = os.path.basename(path)[:-6]
    session = Session("claude-code", sid, path)
    if "subagents" in parts:
        index = parts.index("subagents")
        session.parent = parts[index - 1]
        session.root_path = os.sep.join(parts[:index]) + ".jsonl"
        session.is_subagent = True
    tool_names = {}
    recognized = 0
    for record in read_jsonl(path):
        kind = record.get("type")
        if kind not in ("user", "assistant"):
            continue
        recognized += 1
        ts = parse_ts(record.get("timestamp"))
        session.cwd = session.cwd or record.get("cwd", "")
        content = (record.get("message") or {}).get("content")
        if kind == "user":
            if record.get("isMeta"):
                continue
            blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content or []
            for block in blocks:
                btype = block.get("type")
                if btype == "text":
                    text = block.get("text", "")
                    if "<command-name>/agent-retro" in text:
                        session.retro = True
                    session.add(ts, "user", text)
                elif btype == "image":
                    session.add(ts, "image", "")
                elif btype == "tool_result":
                    result = text_of(block.get("content"))
                    name = tool_names.get(block.get("tool_use_id"), "")
                    session.add(ts, "result-error" if block.get("is_error") else "result", f"{name}: {result}")
        else:
            for block in content or []:
                btype = block.get("type")
                if btype == "text":
                    session.add(ts, "assistant", block.get("text", ""))
                elif btype == "tool_use":
                    name, data = block.get("name", ""), block.get("input") or {}
                    tool_names[block.get("id")] = name
                    if name == "Skill" and data.get("skill") == "agent-retro":
                        session.retro = True
                    if name == "Bash" and isinstance(data.get("command"), str):
                        session.commands.append((ts, data["command"]))
                    session.add(ts, "call", f"{name} {json.dumps(data, ensure_ascii=False)}")
    if not recognized and os.path.getsize(path) > 0 and not session.parent:
        errors.append(f"{path}: no user or assistant records; the log format may have changed")
    return session


CODEX_CMD = re.compile(r"\bcmd\s*:\s*(\"(?:[^\"\\]|\\.)*\"|`(?:[^`\\]|\\.)*`)")


def codex_commands(raw):
    commands = []
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            cmd = data.get("cmd") or data.get("command")
            if isinstance(cmd, list):
                cmd = " ".join(cmd)
            if isinstance(cmd, str):
                return [cmd]
    except (json.JSONDecodeError, TypeError):
        pass
    for match in CODEX_CMD.finditer(raw or ""):
        literal = match.group(1)
        try:
            commands.append(json.loads(literal) if literal.startswith('"') else literal[1:-1])
        except json.JSONDecodeError:
            commands.append(literal[1:-1])
    return commands


def failures(value):
    if isinstance(value, dict):
        code = value.get("exit_code")
        if code is None and isinstance(value.get("metadata"), dict):
            code = value["metadata"].get("exit_code")
        if isinstance(code, int) and code != 0:
            yield f"exit {code}", text_of(value.get("output", ""))
        if value.get("isError") is True:
            yield "error", text_of(value.get("content", ""))
        for child in value.values():
            yield from failures(child)
    elif isinstance(value, list):
        for child in value:
            yield from failures(child)


def codex_result(output):
    chunks = [b.get("text", "") for b in output if isinstance(b, dict)] if isinstance(output, list) else [text_of(output)]
    failed = []
    for chunk in chunks:
        for piece in [chunk] + chunk.splitlines():
            piece = piece.strip()
            if not piece.startswith(("{", "[")):
                continue
            try:
                failed.extend(failures(json.loads(piece)))
            except json.JSONDecodeError:
                continue
            if piece == chunk.strip():
                break
    text = " ".join(chunks)
    if failed:
        return "result-error", " | ".join(f"{label}: {body}" for label, body in failed)
    if re.search(r"Process exited with code [1-9]|^Script failed", text):
        return "result-error", text
    return "result", text


def load_codex(path):
    session = Session("codex", os.path.basename(path)[:-6], path)
    recognized = 0
    for record in read_jsonl(path):
        payload = record.get("payload") or {}
        ts = parse_ts(record.get("timestamp"))
        rtype, ptype = record.get("type"), payload.get("type")
        if rtype == "session_meta":
            recognized += 1
            session.id = payload.get("id", session.id)
            session.cwd = payload.get("cwd", "")
            source = payload.get("source")
            spawn = source.get("subagent", {}).get("thread_spawn", {}) if isinstance(source, dict) and isinstance(source.get("subagent"), dict) else {}
            session.parent = payload.get("parent_thread_id") or spawn.get("parent_thread_id")
            session.is_subagent = bool(session.parent or (isinstance(source, dict) and source.get("subagent")))
            session.add(ts, "meta", "")
        elif rtype == "response_item" and ptype == "message" and payload.get("role") == "user":
            recognized += 1
            text = text_of(payload.get("content"))
            if not text.lstrip().startswith(SKIP_USER) and re.search(r"\$agent-retro\b|\b(use|run)\b[^.\n]{0,40}\bagent-retro\b", text, re.I):
                session.retro = True
            session.add(ts, "user", text)
        elif rtype == "response_item" and ptype == "message" and payload.get("role") == "assistant":
            recognized += 1
            session.add(ts, "assistant", text_of(payload.get("content")))
        elif rtype == "response_item" and ptype in ("function_call", "custom_tool_call"):
            recognized += 1
            raw = payload.get("arguments") if ptype == "function_call" else payload.get("input")
            raw = raw if isinstance(raw, str) else json.dumps(raw)
            session.commands.extend((ts, c) for c in codex_commands(raw))
            session.add(ts, "call", f"{payload.get('name', '')} {raw}")
        elif rtype == "response_item" and ptype in ("function_call_output", "custom_tool_call_output"):
            recognized += 1
            session.add(ts, *codex_result(payload.get("output")))
        elif rtype == "event_msg" and ptype == "turn_aborted" and payload.get("reason") == "interrupted":
            session.add(ts, "interrupt", "")
    if not recognized and os.path.getsize(path) > 0:
        errors.append(f"{path}: no recognized records; the log format may have changed")
    return session


def find_files(root, pattern, since):
    if not os.path.isdir(root):
        return []
    cutoff = since.timestamp()
    return [p for p in glob.glob(os.path.join(root, pattern), recursive=True) if os.path.getmtime(p) >= cutoff]


LOADERS = {"claude-code": load_claude, "codex": load_codex}


def codex_index():
    index = {}
    for path in glob.glob(os.path.join(CODEX, "**", "*.jsonl"), recursive=True):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    break
                if record.get("type") == "session_meta":
                    payload = record.get("payload") or {}
                    source = payload.get("source")
                    sub = source.get("subagent") if isinstance(source, dict) else None
                    spawn = sub.get("thread_spawn", {}) if isinstance(sub, dict) else {}
                    index[("codex", payload.get("id"))] = (payload.get("parent_thread_id") or spawn.get("parent_thread_id"), path)
                    break
    return index


def root_of(session, index):
    root_id, seen = session.parent, set()
    while root_id not in seen and index.get((session.harness, root_id), (None,))[0]:
        seen.add(root_id)
        root_id = index[(session.harness, root_id)][0]
    path = session.root_path or index.get((session.harness, root_id), (None, None))[1]
    return root_id, path


def load_all(since):
    sessions = {}
    found = []
    for harness, root, pattern, loader in (
        ("claude-code", CLAUDE, "**/*.jsonl", load_claude),
        ("codex", CODEX, "**/*.jsonl", load_codex),
    ):
        if not os.path.isdir(root):
            continue
        found.append(harness)
        for path in find_files(root, pattern, since):
            session = loader(path)
            sessions[(harness, session.id, path)] = session
    return found, list(sessions.values())


def mark_briefs(sessions):
    for s in sessions:
        if s.is_subagent:
            s.events = [(ts, "brief" if kind == "user" else kind, text) for ts, kind, text in s.events]


def fold(sessions, index):
    roots = {(s.harness, s.id): s for s in sessions if not s.parent}
    for s in sessions:
        if not s.parent:
            continue
        root_id, path = root_of(s, index)
        root = roots.get((s.harness, root_id))
        if root is None:
            # The root started before the timeframe; load it for its retro mark and folder.
            root = LOADERS[s.harness](path) if path and os.path.exists(path) else Session(s.harness, root_id, None)
            mark_briefs([root])
            root.id, root.parent = root_id, None
            root.cwd = root.cwd or s.cwd
            roots[(s.harness, root_id)] = root
        root.subagents += 1
        root.events.extend(s.events)
        root.commands.extend(s.commands)
        root.retro = root.retro or s.retro
        if s.start and (root.start is None or s.start < root.start):
            root.start = s.start
    return list(roots.values())


def signals(session):
    seen_calls = collections.Counter()
    for ts, kind, text in session.events:
        if kind == "user":
            if text.startswith("[Request interrupted"):
                yield ts, "interrupt", text
            elif text.lstrip().startswith(SKIP_USER):
                continue
            elif "<pasted_content" in text or "[Pasted text" in text:
                yield ts, "paste", text
            elif CORRECTION.search(text):
                yield ts, "correction?", text
        elif kind in ("image", "interrupt"):
            yield ts, kind, text
        elif kind == "result-error":
            if DENIED.search(text):
                yield ts, "denied", text
            elif AUTH.search(text[:300]):
                yield ts, "auth", text
            else:
                yield ts, "tool-error", text
        elif kind == "result":
            match = MASKED.search(text)
            if match:
                yield ts, "masked-error", text[max(0, match.start() - 60):]
        elif kind == "call":
            name = text.split(" ", 1)[0]
            if BROWSER.search(name):
                yield ts, "browser", text
            if REVERT.search(text):
                yield ts, "revert", text
            seen_calls[text] += 1
            if seen_calls[text] == 3:
                yield ts, "repeated-call", text


def split_commands(command):
    parts, current, quote, i = [], [], None, 0
    while i < len(command):
        char = command[i]
        if quote:
            if char == "\\" and quote == '"':
                current.append(command[i : i + 2])
                i += 2
                continue
            if char == quote:
                quote = None
        elif char in "'\"":
            quote = char
        elif char == "#" and (i == 0 or command[i - 1] in " \t\n;|&"):
            while i < len(command) and command[i] != "\n":
                i += 1
            continue
        elif char == "\\":
            current.append(command[i : i + 2])
            i += 2
            continue
        elif char in "\n;|&":
            parts.append("".join(current))
            current = []
            i += 1
            continue
        current.append(char)
        i += 1
    parts.append("".join(current))
    return parts


def command_keys(command):
    stripped = command.strip()
    heredoc = re.search(r"\b(python3?|node|ruby|perl|bash|sh)\b[^\n]*<<\s*-?['\"]?(\w+)", stripped)
    flag = re.search(r"\b(python3?|node)\s+(-I\s+)?-[ce]\b", stripped)
    if heredoc or flag:
        if stripped.count("\n") >= 4 or len(stripped) >= 300:
            targets = set()
            for host, path, db in TARGET.findall(stripped):
                targets.add(host or db or re.sub(r"^/(Users|home)/[^/]+", "~", path))
            interpreter = (heredoc or flag).group(1).rstrip("3")
            if targets:
                yield f"inline {interpreter} touching " + ", ".join(sorted(targets)[:4])
            return
    if re.search(r"\b(while|until)\b", stripped) and re.search(r"\bsleep\b", stripped):
        programs = sorted({k for k in command_keys(re.sub(r"\b(while|until)\b", ";", stripped)) if not k.startswith("polling")})
        yield "polling loop: " + ", ".join(programs[:3])
        return
    # Drop heredoc bodies; they are data or inline scripts, not commands.
    stripped = re.sub(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\s*\1\b", "", stripped, flags=re.S)
    stripped = re.sub(r"\d?>&\d|&>", " ", stripped)
    for segment in split_commands(stripped):
        try:
            words = shlex.split(segment, comments=True)
        except ValueError:
            words = segment.split()
        while words and re.match(r"^\w+=", words[0]):
            words.pop(0)
        if not words:
            continue
        program = os.path.basename(words[0])
        if program in IGNORED_PROGRAMS or program in INTERPRETERS or not re.match(r"^[A-Za-z_][\w.+-]*$", program):
            continue
        args = words[1:]
        rest, skip = [], False
        for word in args:
            if skip:
                skip = False
            elif word in ("-C", "-c", "--git-dir", "--work-tree", "--repo", "-R"):
                skip = True
            elif not word.startswith("-"):
                rest.append(word)
        key = program
        if program in SUBCOMMAND_PROGRAMS and rest:
            if program == "git" and rest[0] in IGNORED_GIT:
                continue
            key += " " + rest[0]
            if program == "gh" and len(rest) > 1:
                key += " " + (re.sub(r"\d+", "N", rest[1]) if rest[0] == "api" else rest[1])
        elif program == "curl":
            hosts = re.findall(r"https?://([\w.-]+)", segment)
            key += " " + (hosts[0] if hosts else "")
        yield key.strip()


def description(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        head = handle.read(4096)
    front = re.match(r"---\n(.*?)\n---\n", head, re.S)
    match = re.search(r"^description:[ \t]*([^|>\s].*)$", front.group(1), re.M) if front else None
    return clip(match.group(1).strip("'\"") if match else head, 160)


def tilde(path):
    for home in {HOME, os.path.realpath(HOME)}:
        if path.startswith(home + os.sep):
            return "~" + path[len(home):]
    return path


def memories():
    """Rows of (harness, modified, sessions, path, description); sessions counts the logs of the Claude projects that load a memory."""
    rows = []
    # Several project folders can link their memory folder to one shared folder; list its files once.
    shared = collections.Counter()
    for folder in glob.glob(os.path.join(CLAUDE, "*", "memory")):
        shared[os.path.realpath(folder)] += len(glob.glob(os.path.join(os.path.dirname(folder), "*.jsonl")))
    for folder, sessions in shared.items():
        rows.extend(("claude-code", p, str(sessions)) for p in glob.glob(os.path.join(folder, "*.md")) if os.path.basename(p) != "MEMORY.md")
    # Codex generates these from its sessions; the rest of ~/.codex/memories is that pipeline's input.
    for path in [os.path.join(CODEX_MEMORIES, "memory_summary.md")] + glob.glob(os.path.join(CODEX_MEMORIES, "skills", "*", "SKILL.md")):
        if os.path.exists(path):
            rows.append(("codex", path, ""))
    return sorted(
        ((h, local(dt.datetime.fromtimestamp(os.path.getmtime(p), dt.timezone.utc)), n, tilde(p), description(p)) for h, p, n in rows),
        key=lambda row: (row[0], row[3]),
    )


def remove_when(repos):
    rows = []
    for repo in sorted(repos):
        result = subprocess.run(
            ["git", "-C", repo, "log", "--date=short",
             "--format=%h%x09%ad%x09%s%x09%(trailers:key=Remove-When,valueonly,unfold,separator=%x1f)"],
            capture_output=True, text=True,
        )
        if result.returncode:
            errors.append(f"{repo}: git log failed: {clip(result.stderr)}")
            continue
        for line in result.stdout.splitlines():
            fields = line.split("\t")
            if len(fields) == 4:
                rows.extend((repo, *fields[:3], value.strip()) for value in fields[3].split("\x1f") if value.strip())
    return rows


def git_root(path, cache={}):
    if path not in cache:
        cache[path] = None
        if path and os.path.isdir(path):
            result = subprocess.run(["git", "-C", path, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
            if result.returncode == 0:
                cache[path] = os.path.realpath(result.stdout.strip())
    return cache[path]


def local_midnight(date, days=0):
    # mktime picks the date's own UTC offset, which differs from today's across a DST change.
    day = dt.datetime.strptime(date, "%Y-%m-%d") + dt.timedelta(days=days)
    return dt.datetime.fromtimestamp(time.mktime((day.year, day.month, day.day, 0, 0, 0, 0, 0, -1))).astimezone()


def local(ts):
    return ts.astimezone().strftime("%Y-%m-%d %H:%M") if ts else ""


def one_shot(session):
    """One prompt, at most one tool call, and no signal but a guessed correction, such as a title generator."""
    kinds = collections.Counter(k for _, k, _ in session.events)
    return kinds["user"] <= 1 and kinds["call"] <= 1 and all(k == "correction?" for _, k, _ in signals(session))


def run_report(args):
    since = local_midnight(args.since)
    until = local_midnight(args.until, days=1) if args.until else None

    def inside(ts):
        return ts is not None and ts >= since and (until is None or ts < until)

    found, sessions = load_all(since)
    mark_briefs(sessions)
    sessions = fold(sessions, codex_index() if "codex" in found else {})
    sessions = [s for s in sessions if not one_shot(s)]
    for s in sessions:
        s.events = [e for e in s.events if inside(e[0])]
        s.commands = [c for c in s.commands if inside(c[0])]
        s.start = min((e[0] for e in s.events), default=None)
    sessions = [s for s in sessions if s.events]
    sessions.sort(key=lambda s: s.start or since)

    counts = collections.Counter(s.harness for s in sessions)
    print("# harnesses read: " + (", ".join(f"{h} ({counts[h]} sessions)" for h in found) or "none"))
    print("\n## sessions\nharness\tsession\tstart\tcwd\tsubagents\tretro\tfirst prompt")
    for s in sessions:
        first = next((t for _, k, t in s.events if k == "user" and not t.lstrip().startswith(SKIP_USER)), "")
        print(f"{s.harness}\t{s.id}\t{local(s.start)}\t{s.cwd}\t{s.subagents}\t{'yes' if s.retro else ''}\t{clip(first, 120)}")

    print("\n## signals (retro sessions skipped)\nsession\ttime\tkind\texcerpt")
    for s in sessions:
        # Ceiling: this also drops other work done in a retro session. Skipping only the retro's own turns would fix it.
        if s.retro:
            continue
        for ts, kind, text in signals(s):
            print(f"{s.id[:8]}\t{local(ts)}\t{kind}\t{clip(text)}")

    print("\n## repeated across sessions (heuristic)\nsessions\tkey\texamples")
    seen = collections.defaultdict(set)
    for s in sessions:
        if s.retro:
            continue
        for _, command in s.commands:
            for key in command_keys(command):
                seen[key].add((s.harness, s.id))
    for key, ids in sorted(seen.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if len(ids) >= 2:
            print(f"{len(ids)}\t{key}\t{', '.join(sorted(i[:8] for _, i in ids)[:5])}")

    print("\n## memories\nharness\tmodified\tsessions\tpath\tdescription")
    for row in memories():
        print("\t".join(row))

    repos = {r for r in (git_root(s.cwd) for s in sessions) if r}
    repos.update(git_root(os.path.expanduser(r)) or os.path.realpath(os.path.expanduser(r)) for r in args.repo)
    print("\n## Remove-When trailers\nrepo\tcommit\tdate\tsubject\tcondition")
    for row in remove_when(repos):
        print("\t".join(row))


def run_context(args):
    prefix, pattern = args.context[0], re.compile(args.context[1], re.I)
    index = codex_index() if os.path.isdir(CODEX) else {}
    groups = collections.defaultdict(set)
    if os.path.isdir(CLAUDE):
        for path in glob.glob(os.path.join(CLAUDE, "**", "*.jsonl"), recursive=True):
            parts = path.split(os.sep)
            root_id = parts[parts.index("subagents") - 1] if "subagents" in parts else os.path.basename(path)[:-6]
            if root_id.startswith(prefix) or prefix in os.path.basename(path):
                groups[("claude-code", root_id)].add(path)
    for (harness, sid), (parent, path) in index.items():
        child = Session(harness, sid, path)
        child.parent = parent
        root_id = root_of(child, index)[0] if parent else sid
        if root_id and (root_id.startswith(prefix) or prefix in os.path.basename(path)):
            groups[(harness, root_id)].add(path)
    if not groups:
        sys.exit(f"no session matches {prefix}")
    for harness, root_id in sorted(groups):
        events = []
        for path in sorted(groups[(harness, root_id)]):
            session = LOADERS[harness](path)
            mark_briefs([session])
            events.extend(session.events)
        events.sort(key=lambda e: e[0] or dt.datetime.max.replace(tzinfo=dt.timezone.utc))
        hits = [i for i, e in enumerate(events) if pattern.search(e[2])]
        shown = set()
        for i in hits:
            for j in range(max(0, i - args.around), min(len(events), i + args.around + 1)):
                if j in shown:
                    continue
                shown.add(j)
                ts, kind, text = events[j]
                print(f"{'>' if j == i else ' '} {local(ts)}\t{kind}\t{clip(text, 600)}")
            print("--")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", help="first local date to include, YYYY-MM-DD")
    parser.add_argument("--until", help="last local date to include, YYYY-MM-DD")
    parser.add_argument("--repo", action="append", default=[], help="extra repo to list Remove-When trailers from")
    parser.add_argument("--context", nargs=2, metavar=("SESSION", "REGEX"), help="print events around REGEX in a session")
    parser.add_argument("--around", type=int, default=3, help="events to show around each --context match")
    args = parser.parse_args()
    if args.context:
        run_context(args)
    elif args.since:
        run_report(args)
    else:
        parser.error("pass --since or --context")
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    sys.exit(2 if errors else 0)


if __name__ == "__main__":
    main()
