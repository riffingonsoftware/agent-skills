#!/usr/bin/env python3
"""Collect agent session signals for the agent-retro skill.

Usage:
  collect.py --since YYYY-MM-DD [--until YYYY-MM-DD] [--repo PATH]...
  collect.py --context SESSION_ID_PREFIX REGEX [--around N]

Reads the session logs of each supported harness that exists on this machine
and skips the rest. Prints tab-separated sections: harnesses, sessions,
signals, repeated commands, PR comments, memories, and Remove-When trailers.
PR comments need an authenticated gh and are skipped without one. Subagent sessions are
folded into the session that started them; sessions that ran agent-retro, or a skill
named like it (see RETRO_SKILL), are listed but their signals are skipped; one-shot sessions (see one_shot) are dropped. Exits 2 when a log line can't be parsed.

Supported: Claude Code (~/.claude/projects), Codex (~/.codex/sessions), Cursor (~/.cursor/projects).
Repeated-command detection is a heuristic: it groups shell commands by program
and subcommand, and inline scripts by the paths and hosts they touch.
"""
import argparse
import collections
import concurrent.futures
import datetime as dt
import glob
import json
import os
import re
import shlex
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.parse

HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude", "projects")
CODEX = os.path.join(HOME, ".codex", "sessions")
CODEX_MEMORIES = os.path.join(HOME, ".codex", "memories")
CURSOR = os.path.join(HOME, ".cursor", "projects")

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
# agent-retro, or a wrapper skill that runs it, such as team-retro.
RETRO_SKILL = r"[\w:-]+-retro"
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
    unrecognized_messages = 0
    for record in read_jsonl(path):
        kind = record.get("type")
        if kind not in ("user", "assistant"):
            unrecognized_messages += "message" in record
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
                    if re.search(rf"<command-name>/{RETRO_SKILL}<", text):
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
                    if name == "Skill" and re.fullmatch(RETRO_SKILL, str(data.get("skill"))):
                        session.retro = True
                    if name == "Bash" and isinstance(data.get("command"), str):
                        session.commands.append((ts, data["command"]))
                    session.add(ts, "call", f"{name} {json.dumps(data, ensure_ascii=False)}")
    # A session closed before any message holds only metadata records. A format change that also
    # renames the `message` field would slip past this check.
    if not recognized and unrecognized_messages and not session.parent:
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
            if not text.lstrip().startswith(SKIP_USER) and re.search(rf"\${RETRO_SKILL}(?![\w:-])|\b(use|run)\b[^.\n]{{0,40}}\b{RETRO_SKILL}(?![\w:-])", text, re.I):
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


CURSOR_MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}
CURSOR_TS = re.compile(
    r"<timestamp>\s*(?:[A-Za-z]+,\s*)?([A-Za-z]{3})\s+(\d{1,2}),\s*(\d{4}),\s*"
    r"(\d{1,2}):(\d{2})\s*([AP]M)\s*\(UTC(?:([+-])(\d{1,2})(?::(\d{2}))?)?\)\s*</timestamp>"
)
CURSOR_WRAPPER_TAGS = re.compile(
    r"<(timestamp|image_files|t3_code_orchestration_instructions|runtime_info|"
    r"pull_request_linking|attached_files|system_reminder)\b[^>]*>.*?</\1>",
    re.S,
)
CURSOR_SKILL_BLOCK = re.compile(
    r"(?:The user invoked these skills\. Follow their instructions:\s*)?<skill\b[^>]*>.*?</skill>",
    re.S,
)
CURSOR_RETRO = re.compile(
    rf"<skill\b[^>]*\bname=[\"']{RETRO_SKILL}[\"']|(?<![\w/.-])[/$]{RETRO_SKILL}(?![\w:-])|"
    rf"\b(?:use|run)\s+(?:the\s+)?{RETRO_SKILL}(?![\w:-])",
    re.I,
)
CURSOR_COMPACTION = ("<available_subagent_types", "<dynamic_tool_catalog", "<user_info")


def cursor_id(raw):
    return raw[6:] if raw and raw.startswith("agent-") else raw


def parse_cursor_ts(text):
    match = CURSOR_TS.search(text or "")
    if not match:
        return None
    mon, day, year, hour, minute, ampm, sign, oh, om = match.groups()
    month = CURSOR_MONTHS.get(mon)
    if not month:
        return None
    h24 = int(hour) % 12 + (12 if ampm == "PM" else 0)
    if sign:
        delta = dt.timedelta(hours=int(oh), minutes=int(om or 0))
        tz = dt.timezone(-delta if sign == "-" else delta)
    else:
        tz = dt.timezone.utc
    return dt.datetime(int(year), month, int(day), h24, int(minute), tzinfo=tz)


def cursor_user_text(raw):
    has_image = "[Image]" in raw or "<image_files>" in raw
    ts = parse_cursor_ts(raw)
    match = re.search(r"<user_request>\s*(.*?)\s*</user_request>", raw, re.S) or re.search(
        r"<user_query>\s*(.*?)\s*</user_query>", raw, re.S
    )
    body = CURSOR_WRAPPER_TAGS.sub("", match.group(1) if match else raw)
    retro = not body.lstrip().startswith(SKIP_USER) and bool(CURSOR_RETRO.search(body))
    body = CURSOR_SKILL_BLOCK.sub("", body)
    body = re.sub(r"(?:^|\n)\[Image\](?=\n|$)", "", body).strip()
    return ts, body, has_image, retro


def resolve_cursor_slug(slug, cache={}):
    if slug not in cache:
        def walk(cur, rem):
            if not rem:
                return cur
            try:
                entries = sorted(os.listdir(cur), key=len, reverse=True)
            except OSError:
                return None
            for entry in entries:
                norm = re.sub(r"[^A-Za-z0-9]+", "-", entry.lstrip(".")).strip("-")
                if not norm or (rem != norm and not rem.startswith(norm + "-")):
                    continue
                cand = os.path.join(cur, entry)
                if not os.path.isdir(cand):
                    continue
                if rem == norm:
                    return cand
                hit = walk(cand, rem[len(norm) + 1:])
                if hit:
                    return hit
            return None
        cache[slug] = walk("/", slug) or "" if slug else ""
    return cache[slug]


def cursor_tool_result(msg):
    args = msg.get("args") if isinstance(msg.get("args"), dict) else {}
    name = msg.get("name", "")
    if name == "mcp":
        provider, tool = args.get("providerIdentifier", ""), args.get("toolName", "")
        label = f"{provider}:{tool}" if provider and tool else (tool or name)
    else:
        label = name
    res = msg.get("result") if isinstance(msg.get("result"), dict) else {}
    val = res.get("value")
    if name == "shell":
        body = " ".join(
            x for x in ((val.get("stdout") or "", val.get("stderr") or "") if isinstance(val, dict) else (text_of(val),)) if x
        )
        code = val.get("exitCode") if isinstance(val, dict) else None
        if res.get("status") != "success" or (isinstance(code, int) and code != 0):
            detail = f"exit {code}: {body}" if isinstance(code, int) and code != 0 else (text_of(res.get("error")) or body or str(res.get("status", "")))
            return "result-error", f"{label}: {detail}"
        return "result", f"{label}: {body}"
    if res.get("status") != "success":
        err = res.get("error") or res
        return "result-error", f"{label}: {text_of(err) or json.dumps(err, ensure_ascii=False)}"
    if isinstance(val, dict) and val.get("isError") is True:
        return "result-error", f"{label}: {text_of(val.get('content', val))}"
    return "result", f"{label}: {text_of(val) if val is not None else ''}"


def cursor_index(cache={}):
    # Cursor's JSONL transcripts omit tool results and cwd; sdk-agent-store supplies both for SDK runs.
    if CURSOR in cache:
        return cache[CURSOR]
    data = {}
    for db in glob.glob(os.path.join(CURSOR, "*", "sdk-agent-store", "*", "index.db")):
        conn = None
        try:
            conn = sqlite3.connect(f"file:{urllib.parse.quote(db, safe='/:')}?mode=ro", uri=True, timeout=1.0)
            by_run = {}
            for agent_id, workspace_ref in conn.execute("SELECT agent_id, workspace_ref FROM agents"):
                sid = cursor_id(agent_id)
                data[sid] = {"cwd": workspace_ref or "", "start": None, "events": []}
            for run_id, agent_id, status, error_code, started_at, finished_at, cancelled_at in conn.execute(
                "SELECT run_id, agent_id, status, error_code, started_at, finished_at, cancelled_at FROM runs ORDER BY turn_number"
            ):
                sid = cursor_id(agent_id)
                entry = data.setdefault(sid, {"cwd": "", "start": None, "events": []})
                by_run[run_id] = entry
                if started_at and entry["start"] is None:
                    entry["start"] = parse_ts(started_at)
                if cancelled_at or status in ("CANCELLED", "ABORTED"):
                    entry["events"].append((parse_ts(cancelled_at or finished_at or started_at), "interrupt", f"run {status}"))
                elif error_code or status == "ERROR":
                    entry["events"].append((parse_ts(finished_at or started_at), "result-error", f"run: {error_code or status}"))
            for run_id, created_at, payload_json in conn.execute(
                "SELECT run_id, created_at, payload_json FROM run_events WHERE payload_json IS NOT NULL ORDER BY run_id, seq"
            ):
                entry = by_run.get(run_id)
                if entry is None:
                    continue
                try:
                    record = json.loads(payload_json)
                except json.JSONDecodeError:
                    continue
                msg = record.get("message") or {}
                if msg.get("type") == "tool_call" and msg.get("status") == "completed":
                    entry["events"].append((parse_ts(created_at), *cursor_tool_result(msg)))
        except sqlite3.Error as exc:
            errors.append(f"{db}: {exc}")
        finally:
            if conn is not None:
                conn.close()
    cache[CURSOR] = data
    return data


def load_cursor(path):
    parts = path.split(os.sep)
    sid = cursor_id(os.path.basename(path)[:-6])
    session = Session("cursor", sid, path)
    if "subagents" in parts:
        index = parts.index("subagents")
        parent_dir = parts[index - 1]
        session.parent = cursor_id(parent_dir)
        session.root_path = os.path.join(os.sep.join(parts[:index]), parent_dir + ".jsonl")
        session.is_subagent = True
    slug = parts[parts.index("agent-transcripts") - 1] if "agent-transcripts" in parts else ""
    db = cursor_index()
    cwd_info = db.get(session.parent if session.is_subagent else session.id) or {}
    info = None if session.is_subagent else cwd_info
    session.cwd = cwd_info.get("cwd") or resolve_cursor_slug(slug)
    ts = (info or {}).get("start") or dt.datetime.fromtimestamp(os.path.getmtime(path), dt.timezone.utc)
    recognized = 0
    last_user = None
    replayed = False
    for record in read_jsonl(path):
        role = record.get("role")
        if role not in ("user", "assistant"):
            if record.get("type") == "turn_ended":
                recognized += 1
                status = record.get("status")
                if status and status != "success":
                    kind = "interrupt" if re.search(r"cancel|abort|interrupt", str(status), re.I) else "result-error"
                    session.add(ts, kind, f"turn_ended: {status}")
            continue
        recognized += 1
        content = (record.get("message") or {}).get("content")
        blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content or []
        if role == "user":
            raw_parts = []
            has_img_block = False
            for block in blocks:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "text":
                    raw_parts.append(block.get("text", ""))
                elif btype == "image":
                    has_img_block = True
            raw = "\n".join(raw_parts)
            msg_ts, body, has_image, retro = cursor_user_text(raw)
            if msg_ts:
                ts = msg_ts
            if retro:
                session.retro = True
            if body.lstrip().startswith(CURSOR_COMPACTION):
                replayed = True
                continue
            if replayed and (ts, body) == last_user:
                replayed = False
                continue
            replayed = False
            if body:
                last_user = (ts, body)
            if has_img_block or has_image:
                session.add(ts, "image", "")
            if body:
                session.add(ts, "user", body)
        else:
            for block in blocks:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "text":
                    session.add(ts, "assistant", block.get("text", ""))
                elif btype == "tool_use":
                    name, data = block.get("name", ""), block.get("input") or {}
                    if name == "Shell" and isinstance(data.get("command"), str):
                        session.commands.append((ts, data["command"]))
                    if name == "CallDynamicTool":
                        ns, tn = data.get("namespace", ""), data.get("toolName", "")
                        call_name = f"{ns}:{tn}" if ns and tn else (tn or name)
                        call_data = data.get("arguments") if isinstance(data.get("arguments"), dict) else data
                    else:
                        call_name, call_data = name, data
                    session.add(ts, "call", f"{call_name} {json.dumps(call_data, ensure_ascii=False)}")
    if info and info["events"]:
        for ev_ts, kind, text in info["events"]:
            session.add(ev_ts or ts, kind, text)
        session.events.sort(key=lambda e: e[0] or dt.datetime.max.replace(tzinfo=dt.timezone.utc))
    if not recognized and os.path.getsize(path) > 0 and not session.parent:
        errors.append(f"{path}: no recognized records; the log format may have changed")
    return session


def find_files(root, pattern, since):
    if not os.path.isdir(root):
        return []
    cutoff = since.timestamp()
    return [p for p in glob.glob(os.path.join(root, pattern), recursive=True) if os.path.getmtime(p) >= cutoff]


LOADERS = {"claude-code": load_claude, "codex": load_codex, "cursor": load_cursor}


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
        ("cursor", CURSOR, "*/agent-transcripts/**/*.jsonl", load_cursor),
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
    # Scans whole messages, since git reads trailers only from the last paragraph.
    rows = []
    for repo in sorted(repos):
        # Every worktree's HEAD, so a fix committed on a worktree branch counts before the main checkout has it.
        listing = subprocess.run(["git", "-C", repo, "worktree", "list", "--porcelain"], capture_output=True, text=True)
        heads = sorted({"HEAD"} | {line[5:] for line in listing.stdout.splitlines() if line.startswith("HEAD ")})
        result = subprocess.run(
            ["git", "-C", repo, "log", "--date=short", "--format=%x1e%h%x09%ad%x09%s%x09%B", *heads],
            capture_output=True, text=True,
        )
        if result.returncode:
            errors.append(f"{repo}: git log failed: {clip(result.stderr)}")
            continue
        for record in result.stdout.split("\x1e")[1:]:
            fields = record.split("\t", 3)
            if len(fields) < 4:
                continue
            values, continued = [], False
            for line in fields[3].splitlines():
                match = re.match(r"Remove-When:(.*)", line, re.I)
                if match:
                    values.append(match.group(1).strip())
                elif continued and line.strip() and not re.match(r"[\w-]+:", line):
                    values[-1] += " " + line.strip()
                else:
                    continued = False
                    continue
                continued = True
            rows.extend((repo, *fields[:3], value) for value in values if value)
    return rows


def gh_json(endpoint, *fields):
    args = ["gh", "api", "-X", "GET", "--paginate", "--slurp", endpoint] + [f for field in fields for f in ("-f", field)]
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        errors.append(f"gh api {endpoint}: {clip(result.stderr)}")
        return []
    pages = json.loads(result.stdout)
    if any(isinstance(page, dict) and page.get("incomplete_results") for page in pages):
        errors.append(f"gh api {endpoint}: search timed out with incomplete results")
    return [item for page in pages for item in (page.get("items", []) if isinstance(page, dict) else page)]


def review_comments(since, until):
    """Rows of (pr, time, author, where, excerpt) for other people's comments and review summaries on PRs the user took part in.

    `where` is the file of an inline comment, `review` for a review summary, or `conversation`.
    Returns a skip reason instead when gh is missing or signed out.
    """
    if not shutil.which("gh"):
        return "gh not found"
    me = subprocess.run(["gh", "api", "user", "--jq", ".login"], capture_output=True, text=True)
    if me.returncode:
        if re.search(r"HTTP 401|gh auth login", me.stderr):
            return "gh not signed in: " + clip(me.stderr, 120)
        errors.append(f"gh api user: {clip(me.stderr)}")
        return "gh api user failed"
    me = me.stdout.strip()
    # `updated` is the PR's latest update, so a PR updated after the window can still hold comments inside it:
    # search with only the lower bound, as a UTC date, and apply both bounds to each comment.
    window = f"updated:>={since.astimezone(dt.timezone.utc).date()}"
    prs = set()
    # `involves` covers author, assignee, mentions, and commenter, but not a review without comments.
    for role in ("involves", "reviewed-by"):
        for item in gh_json("search/issues", f"q=is:pr {role}:{me} {window}", "per_page=100"):
            prs.add(item["pull_request"]["url"].split("/repos/", 1)[1])

    def fetch(pr):
        return pr, (
            [(c.get("path", ""), c) for c in gh_json(f"repos/{pr}/comments", "per_page=100")]
            + [("review", c) for c in gh_json(f"repos/{pr}/reviews", "per_page=100")]
            + [("conversation", c) for c in gh_json(f"repos/{pr.replace('/pulls/', '/issues/')}/comments", "per_page=100")]
        )

    rows = []
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        for pr, comments in pool.map(fetch, sorted(prs)):
            for where, c in comments:
                ts = parse_ts(c.get("created_at") or c.get("submitted_at"))
                author = (c.get("user") or {}).get("login", "")
                body = re.sub(r"<!--.*?-->|</?(details|summary)>", " ", c.get("body") or "", flags=re.S).strip()
                # Replies are discussion of a finding, not new findings; a pending review has no time yet.
                if not body or c.get("in_reply_to_id") or author == me or not ts or ts < since or (until and ts >= until):
                    continue
                rows.append((pr.replace("/pulls/", "#"), local(ts), author, where, clip(body, 300)))
    return rows


def git_root(path, cache={}):
    if path not in cache:
        cache[path] = None
        if path and os.path.isdir(path):
            # A linked worktree maps to its main checkout, so each repo is listed once.
            dirs = subprocess.run(["git", "-C", path, "rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir"],
                                  capture_output=True, text=True)
            if dirs.returncode == 0:
                git_dir, common = (os.path.realpath(d) for d in dirs.stdout.split("\n")[:2])
                if git_dir != common:
                    cache[path] = os.path.dirname(common)
                else:
                    top = subprocess.run(["git", "-C", path, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
                    cache[path] = os.path.realpath(top.stdout.strip()) if top.returncode == 0 else common
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

    rows = review_comments(since, until)
    if isinstance(rows, str):
        print(f"\n## PR comments skipped: {rows}")
    else:
        print("\n## PR comments and reviews on PRs you took part in (repeats folded)\npr\ttime\tauthor\twhere\texcerpt")
        # Bots post the same status text on every PR; print it once with a count of the other PRs.
        groups = collections.defaultdict(list)
        for row in rows:
            groups[row[2:]].append(row)
        for group in groups.values():
            pr, *rest = group[0]
            print("\t".join([pr + (f" (+{len(group) - 1} more)" if len(group) > 1 else "")] + rest))

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
    if os.path.isdir(CURSOR):
        for path in glob.glob(os.path.join(CURSOR, "*", "agent-transcripts", "**", "*.jsonl"), recursive=True):
            parts = path.split(os.sep)
            raw_root = parts[parts.index("subagents") - 1] if "subagents" in parts else os.path.basename(path)[:-6]
            root_id = cursor_id(raw_root)
            if root_id.startswith(prefix) or raw_root.startswith(prefix) or prefix in os.path.basename(path):
                groups[("cursor", root_id)].add(path)
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
