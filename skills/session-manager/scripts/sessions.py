#!/usr/bin/env python3
"""Claude Code / Codex session bookmark manager.

Bookmarks live in ~/.claude/session-bookmarks.json as a list of:
  {"name": str, "tool": "claude"|"codex", "id": str, "dir": str, "saved": "YYYY-MM-DD",
   "arc": str}   # arc = original transcript path, present once archived

Archived transcript copies live in ~/.claude/session-archive/<tool>-<id>.jsonl so a
session survives Claude Code's cleanupPeriodDays auto-deletion. On resume the copy is
restored to its original path first.

Resume commands are SAFE by default (plain `claude --resume` / `codex resume`, which
still ask for permissions). Export SESSION_MANAGER_YOLO=1 to auto-approve instead
(adds `--dangerously-skip-permissions` / `--yolo`).

Subcommands:
  list                       show all bookmarks grouped by category
  add NAME TOOL ID [--dir D] add a bookmark (auto-archives the transcript)
  current NAME               bookmark the session this script is running inside
  archive NAME               archive an already-saved session's transcript
  remove NAME                delete a bookmark (and its archived copy)
  rename OLD NEW             rename a bookmark
  cat NAME CATEGORY          set a bookmark's category ("" to clear)
  open NAME                  restore if needed, open the session in a new Terminal window
  cmd NAME                   print the resume command (restores if needed)
  clip NAME                  copy the resume command to the clipboard (restores if needed)
"""
import argparse
import datetime
import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import sys

HOME = os.path.expanduser("~")
BOOKMARKS = os.path.join(HOME, ".claude", "session-bookmarks.json")
PROJECTS = os.path.join(HOME, ".claude", "projects")
CODEX_SESSIONS = os.path.join(HOME, ".codex", "sessions")
# ponytail: flat archive dir, one copy per session. No rotation/size cap — add if it grows huge.
ARCHIVE = os.path.join(HOME, ".claude", "session-archive")


def load():
    if not os.path.exists(BOOKMARKS):
        return []
    with open(BOOKMARKS) as f:
        return json.load(f)


def save(entries):
    with open(BOOKMARKS, "w") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
        f.write("\n")


def claude_transcript(session_id):
    hits = glob.glob(os.path.join(PROJECTS, "*", session_id + ".jsonl"))
    return hits[0] if hits else None


def codex_transcript(session_id):
    hits = glob.glob(os.path.join(CODEX_SESSIONS, "*", "*", "*", "*" + session_id + ".jsonl"))
    return hits[0] if hits else None


def live_transcript(entry):
    """Path to the session's transcript if it still exists in Claude Code / Codex storage."""
    if not entry["id"]:
        return None
    if entry["tool"] == "claude":
        return claude_transcript(entry["id"])
    return codex_transcript(entry["id"])


def archive_file(entry):
    return os.path.join(ARCHIVE, "{}-{}.jsonl".format(entry["tool"], entry["id"]))


def is_archived(entry):
    return bool(entry["id"]) and os.path.exists(archive_file(entry))


def restorable(entry):
    """Resumable-from-archive only when both the copy AND its original path (arc) are known."""
    return is_archived(entry) and bool(entry.get("arc"))


def do_archive(entry):
    """Copy the live transcript into the archive and remember its original path.
    Returns True on success, False if the transcript isn't on disk to copy."""
    src = live_transcript(entry)
    if not src:
        return False
    os.makedirs(ARCHIVE, exist_ok=True)
    shutil.copy2(src, archive_file(entry))
    entry["arc"] = src
    return True


def ensure_available(entry):
    """Make the transcript present on disk so resume works.
    Returns 'live', 'restored', or None (not recoverable)."""
    if live_transcript(entry):
        return "live"
    if is_archived(entry):
        target = entry.get("arc")
        if not target:
            return None
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(archive_file(entry), target)
        return "restored"
    return None


def resolve_dir(tool, session_id):
    """Read the session's working directory out of its transcript."""
    path = claude_transcript(session_id) if tool == "claude" else codex_transcript(session_id)
    if not path:
        return None
    with open(path, errors="replace") as f:
        head = f.read(40000)
    m = re.search(r'"cwd"\s*:\s*"([^"]+)"', head)
    return m.group(1) if m else None


def is_alive(entry):
    """Resumable = transcript still on disk OR we have an archived copy to restore."""
    if not entry["id"]:
        return False
    return live_transcript(entry) is not None or restorable(entry)


def find(entries, name):
    """Exact match first, then case-insensitive substring."""
    exact = [e for e in entries if e["name"] == name]
    if exact:
        return exact
    return [e for e in entries if name.lower() in e["name"].lower()]


def resume_command(entry):
    # Default is SAFE: plain resume that still asks for permissions normally.
    # Opt in to auto-approve (skip permission prompts) only if the user exports
    # SESSION_MANAGER_YOLO=1 — off by default so a shared install never surprises anyone.
    yolo = os.environ.get("SESSION_MANAGER_YOLO") == "1"
    if entry["tool"] == "claude":
        flag = "--dangerously-skip-permissions " if yolo else ""
        return "claude {}--resume {}".format(flag, entry["id"])
    return "codex {}resume {}".format("--yolo " if yolo else "", entry["id"])


def open_command(entry):
    """`open`용 resume 명령: 새 Terminal 창은 HOME에서 시작하므로, 저장해둔 작업폴더로
    cd 한 뒤 resume 해야 세션을 찾는다. clip/cmd는 사용자가 원하는 곳에 붙여넣으므로
    cd 없이 bare resume(resume_command)만 쓴다."""
    d = entry.get("dir") or HOME
    return "cd {} && {}".format(shlex.quote(d), resume_command(entry))


CATEGORY_ORDER = ["work", "personal"]  # optional preset ordering; any other category sorts after, 미분류 last


def cmd_list(args):
    entries = load()
    if not entries:
        print("저장된 세션 없음.")
        return
    groups = {}
    for e in entries:
        groups.setdefault(e.get("category") or "미분류", []).append(e)
    ordered = [c for c in CATEGORY_ORDER if c in groups]
    ordered += sorted(c for c in groups if c not in CATEGORY_ORDER and c != "미분류")
    if "미분류" in groups:
        ordered.append("미분류")
    for cat in ordered:
        print("== {} ==".format(cat))
        for e in groups[cat]:
            if not e["id"]:
                status = "TODO(세션 없음)"
            elif live_transcript(e):
                status = "OK(아카이브됨)" if restorable(e) else "OK"
            elif restorable(e):
                status = "ARCHIVED(보관됨, 복원가능)"
            else:
                status = "DEAD(기록 삭제됨)"
            print("{}\t[{}]\t{}\t{}\t{}".format(e["name"], e["tool"], status, e.get("saved", "?"), e["id"]))


def cmd_add(args):
    entries = load()
    existing = [e for e in entries if e["name"] == args.name]
    d = args.dir or resolve_dir(args.tool, args.id) or HOME
    today = datetime.date.today().isoformat()
    if existing:
        # TODO placeholder with same name gets its session attached; real entries stay protected
        if existing[0]["id"]:
            sys.exit("이미 같은 이름 있음: " + args.name)
        entry = existing[0]
        entry.update({"tool": args.tool, "id": args.id, "dir": d, "saved": today})
        note = "TODO 항목에 세션 연결됨"
    else:
        entry = {"name": args.name, "tool": args.tool, "id": args.id, "dir": d, "saved": today}
        entries.append(entry)
        note = "저장됨"
    archived = do_archive(entry)
    save(entries)
    print("{}: {} [{}] {} (dir: {})".format(note, args.name, args.tool, args.id, d))
    if archived:
        print("  📦 대화기록 아카이브됨 — 30일 자동삭제돼도 복원 가능.")
    else:
        print("  ⚠️ 대화기록을 못 찾아 아카이브 못함 — 북마크만 저장됨(세션 ID 확인 필요).")


def cmd_todo(args):
    entries = load()
    if any(e["name"] == args.name for e in entries):
        sys.exit("이미 같은 이름 있음: " + args.name)
    entries.append({
        "name": args.name, "tool": "claude", "id": "", "dir": HOME,
        "saved": datetime.date.today().isoformat(),
    })
    save(entries)
    print("TODO 항목 추가됨 (세션 없음): " + args.name)


def cmd_current(args):
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not sid:
        sys.exit("CLAUDE_CODE_SESSION_ID 없음 — Claude Code 안에서만 동작.")
    args.tool, args.id, args.dir = "claude", sid, os.getcwd()
    cmd_add(args)


def cmd_archive(args):
    entries = load()
    hits = find(entries, args.name)
    if len(hits) != 1:
        sys.exit("매칭 {}개: {}".format(len(hits), ", ".join(e["name"] for e in hits)))
    entry = hits[0]
    if not entry["id"]:
        sys.exit("'{}' 은(는) TODO 항목 — 연결된 세션 없음.".format(entry["name"]))
    if do_archive(entry):
        save(entries)
        print("📦 아카이브됨: {} — 원본이 30일 뒤 삭제돼도 복원 가능.".format(entry["name"]))
    else:
        sys.exit("'{}' 대화기록이 디스크에 없음 — 이미 삭제됐다면 아카이브 불가.".format(entry["name"]))


def cmd_remove(args):
    entries = load()
    hits = find(entries, args.name)
    if len(hits) != 1:
        sys.exit("매칭 {}개: {}".format(len(hits), ", ".join(e["name"] for e in hits)))
    if is_archived(hits[0]):
        os.remove(archive_file(hits[0]))
    entries.remove(hits[0])
    save(entries)
    print("삭제됨: " + hits[0]["name"])


def cmd_rename(args):
    entries = load()
    hits = find(entries, args.old)
    if len(hits) != 1:
        sys.exit("매칭 {}개: {}".format(len(hits), ", ".join(e["name"] for e in hits)))
    hits[0]["name"] = args.new
    save(entries)
    print("이름 변경: {} -> {}".format(args.old, args.new))


def cmd_cat(args):
    entries = load()
    hits = find(entries, args.name)
    if len(hits) != 1:
        sys.exit("매칭 {}개: {}".format(len(hits), ", ".join(e["name"] for e in hits)))
    if args.category:
        hits[0]["category"] = args.category
        msg = "분류됨: {} -> {}".format(hits[0]["name"], args.category)
    else:
        hits[0].pop("category", None)
        msg = "분류 해제됨: " + hits[0]["name"]
    save(entries)
    print(msg)


def _resolve_one(name):
    hits = find(load(), name)
    if not hits:
        sys.exit("'{}' 못 찾음. `list`로 확인.".format(name))
    if len(hits) > 1:
        sys.exit("매칭 {}개: {} — 더 정확한 이름 필요.".format(len(hits), ", ".join(e["name"] for e in hits)))
    return hits[0]


def _prepare_resume(entry):
    """Ensure the transcript is on disk. Returns a note string (or empty)."""
    if not entry["id"]:
        sys.exit("'{}' 은(는) TODO 항목 — 연결된 세션 없음. 새 세션에서 작업 후 같은 이름으로 저장하면 연결됨.".format(entry["name"]))
    state = ensure_available(entry)
    if state is None:
        sys.exit("'{}' 대화기록이 디스크에도 아카이브에도 없음 — resume 불가.".format(entry["name"]))
    return "  📦 아카이브에서 복원함 — 이제 이어갈 수 있음." if state == "restored" else ""


def cmd_cmd(args):
    e = _resolve_one(args.name)
    note = _prepare_resume(e)
    if note:
        print(note, file=sys.stderr)
    print(resume_command(e))


def cmd_clip(args):
    e = _resolve_one(args.name)
    note = _prepare_resume(e)
    shell_cmd = resume_command(e)
    subprocess.run(["pbcopy"], input=shell_cmd.encode(), check=True)
    print("클립보드에 복사됨 — 터미널에 붙여넣기(Cmd+V) 후 실행:")
    print("  세션: {} [{}]".format(e["name"], e["tool"]))
    print("  명령: {}".format(shell_cmd))
    if note:
        print(note)


def cmd_open(args):
    e = _resolve_one(args.name)
    note = _prepare_resume(e)
    shell_cmd = open_command(e)
    script = 'tell application "Terminal"\n  do script "{}"\n  activate\nend tell'.format(
        shell_cmd.replace("\\", "\\\\").replace('"', '\\"'))
    subprocess.run(["osascript", "-e", script], check=True)
    print("새 터미널 창에서 열림: " + e["name"])
    if note:
        print(note)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list").set_defaults(func=cmd_list)

    a = sub.add_parser("add")
    a.add_argument("name")
    a.add_argument("tool", choices=["claude", "codex"])
    a.add_argument("id")
    a.add_argument("--dir", default=None)
    a.set_defaults(func=cmd_add)

    c = sub.add_parser("current")
    c.add_argument("name")
    c.set_defaults(func=cmd_current)

    t = sub.add_parser("todo")
    t.add_argument("name")
    t.set_defaults(func=cmd_todo)

    ar = sub.add_parser("archive")
    ar.add_argument("name")
    ar.set_defaults(func=cmd_archive)

    r = sub.add_parser("remove")
    r.add_argument("name")
    r.set_defaults(func=cmd_remove)

    rn = sub.add_parser("rename")
    rn.add_argument("old")
    rn.add_argument("new")
    rn.set_defaults(func=cmd_rename)

    ct = sub.add_parser("cat")
    ct.add_argument("name")
    ct.add_argument("category")
    ct.set_defaults(func=cmd_cat)

    o = sub.add_parser("open")
    o.add_argument("name")
    o.set_defaults(func=cmd_open)

    cm = sub.add_parser("cmd")
    cm.add_argument("name")
    cm.set_defaults(func=cmd_cmd)

    cl = sub.add_parser("clip")
    cl.add_argument("name")
    cl.set_defaults(func=cmd_clip)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
