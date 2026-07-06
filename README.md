# claude-session-manager

**[한국어](#한국어) · [English](#english)**

A [Claude Code](https://claude.com/claude-code) skill that bookmarks your Claude Code / Codex sessions by name — list, resume, and reopen them later from a new terminal. Installable as a **plugin** (one command) or by **copying the skill folder**.

---

## 한국어

### 🔖 이게 뭔가요? (한 줄)

작업하던 Claude Code / Codex 대화(세션)에 **이름표를 붙여 저장**해두고, 나중에 그 이름만 대면 **다시 그 대화로 돌아가게** 해주는 스킬입니다.

### 🤔 왜 필요한가요?

Claude Code로 여러 작업을 하다 보면 대화 세션이 수십 개씩 쌓입니다. 😵‍💫 "어제 그 API 고치던 대화 어디 갔지?" 하고 찾으려면 긴 세션 ID(예: `a1b2c3d4-...`)를 뒤져야 하는데, 사람이 그걸 외우거나 관리하긴 어렵습니다.

이 스킬은 그 세션에 **"API 리팩터링" 같은 사람이 읽는 이름**을 붙여 책갈피처럼 저장합니다. 🔖 나중엔 이름만 대면 Claude가 알아서 그 대화를 찾아 이어줍니다. **세션 ID를 직접 만질 일이 전혀 없습니다.** ✨

### 💬 이렇게 씁니다 (실제 대화 예시)

설치하면, Claude Code에게 **평소처럼 한국어로 말하면** 됩니다. 명령어를 외울 필요 없습니다. 🙆

| 🗣️ 이렇게 말하면 | ✅ 이런 일이 일어납니다 |
|---|---|
| 💾 *"지금 이 세션 'API 리팩터링'으로 저장해줘"* | 지금 하던 대화를 그 이름으로 책갈피 저장 + **대화기록 자동 아카이브(영구보관)** 📦 |
| 📋 *"세션 목록 보여줘"* | 저장해둔 세션들을 카테고리별 표로 정리해 보여줌 (살아있음/보관됨 표시까지) |
| 🪟 *"API 리팩터링 세션 열어줘"* | 새 터미널 창이 열리며 그 대화가 그대로 이어짐 (필요하면 아카이브에서 자동 복원) |
| 📎 *"API 리팩터링 코드 줘"* | 그 세션을 여는 명령어를 클립보드에 복사 → 원하는 터미널에서 Cmd+V |
| 🗄️ *"API 리팩터링 아카이브해줘"* | (이미 저장된 세션을) 지금 영구보관 사본으로 복사 |
| 🗑️ *"API 리팩터링 세션 삭제해줘"* | 그 책갈피와 아카이브 사본을 함께 지움 |

이름은 **일부만 말해도** 찾아줍니다(부분 일치). 🔍 예를 들어 *"리팩터 열어줘"* 라고만 해도 됩니다.

> 💡 **팁:** 세션을 여는 방식은 두 가지예요. **"열어줘"** 🪟 = 새 터미널 창을 자동으로 띄움. **"코드 줘"** 📎 = 명령어만 클립보드에 복사(이미 열어둔 터미널에서 직접 붙여넣고 싶을 때).

### 📂 저장된 목록은 이렇게 보입니다

*"세션 목록 보여줘"* 라고 하면 Claude가 이런 표로 정리해 줍니다 👇

| 🗂️ 카테고리 | 📌 이름 | 🛠️ 도구 | 상태 | 📅 저장일 |
|---|---|---|---|---|
| work | API 리팩터링 | claude | ✅ 살아있음 | 2026-07-06 |
| work | 결제 버그 추적 | claude | ✅ 살아있음 | 2026-07-04 |
| personal | 블로그 초안 | codex | ✅ 살아있음 | 2026-06-30 |
| 미분류 | 로그 파서 실험 | claude | 📦 보관됨(복원가능) | 2026-05-20 |
| 미분류 | 나중에 할 리서치 | — | ⏳ 예정(세션 없음) | 2026-07-05 |

- ✅ **살아있음** — 원본이 그대로 있어 지금 바로 이어서 열 수 있음
- 📦 **보관됨(복원가능)** — 30일이 지나 원본은 지워졌지만 **아카이브 사본이 남아있음** → 열면 자동 복원돼 이어갈 수 있음
- ⏳ **예정** — 이름만 먼저 예약해둔 상태(아직 세션이 연결 안 됨. 나중에 같은 이름으로 저장하면 자동 연결)
- 💀 **삭제됨(복구불가)** — 아카이브되기 전에 지워졌거나 아카이브에 실패한 경우에만. 이건 되살릴 수 없음

### 필요 환경

- **macOS** — 클립보드 복사(`pbcopy`), 새 터미널 창 열기(`osascript` + Terminal.app)에 사용
- **Claude Code** — 현재 세션 저장(`current`)은 Claude Code가 넣어주는 `CLAUDE_CODE_SESSION_ID` 환경변수가 필요
- **Python 3** — 표준 라이브러리만 사용, 설치할 의존성 없음

> 리눅스/윈도우: `list`·`add`·`cmd`·`remove`·`rename`·`cat`·`todo`는 어디서든 동작합니다. `clip`(pbcopy)·`open`(Terminal.app)만 macOS 전용입니다.

### 설치 — 방법 A: 플러그인 (권장, 명령 2줄)

Claude Code 안에서:

```
/plugin marketplace add jazznyeop/claude-session-manager
/plugin install session-manager@jazznyeop
```

자동으로 설치되고, 이후 `/plugin`에서 업데이트도 됩니다. 세션 관련 요청에 자동 발동합니다.

### 설치 — 방법 B: 스킬 폴더 복사

repo를 클론한 뒤 `skills/session-manager` 폴더를 Claude Code 스킬 폴더로 복사합니다:

```bash
git clone https://github.com/jazznyeop/claude-session-manager.git
cp -r claude-session-manager/skills/session-manager ~/.claude/skills/
```

또는 Claude Code에게 **말로** 시켜도 됩니다:
> "https://github.com/jazznyeop/claude-session-manager 클론해서 스킬로 등록해줘"

둘 다 `~/.claude/skills/session-manager/`에 설치됩니다. Claude Code를 다시 켜면 자동 발동합니다.

> 설치 전에 `skills/session-manager/scripts/sessions.py`를 한 번 열어보세요 — 표준 라이브러리만 쓰는 250줄 남짓 파이썬, 네트워크 호출 없음. **코드 확인하고 쓰는 걸 권장합니다.**

### 🗄️ 세션을 영구보관합니다 (자동 아카이브)

Claude Code는 기본적으로 30일(`cleanupPeriodDays`)이 지난 대화기록을 **자동으로 삭제**합니다. 이 스킬은 그걸 막기 위해, **세션을 저장하는 순간 대화기록(`.jsonl`)을 `~/.claude/session-archive/`로 복사(아카이브)** 해둡니다. 그래서 👇

- 🛟 30일이 지나 Claude Code가 원본을 지워도 **아카이브 사본이 남아** 그대로 이어갈 수 있습니다.
- 📦 세션을 열 때(*"열어줘"* / *"코드 줘"*) 원본이 없으면 **아카이브에서 자동 복원**한 뒤 이어줍니다.
- 📂 목록에서 그런 세션은 `📦 보관됨(복원가능)`으로 표시됩니다.
- ✋ 이미 저장돼 있던(살아있는) 세션을 지금 명시적으로 보관하고 싶으면 *"OO 아카이브해줘"* 라고 하면 됩니다.

> ⚠️ **솔직한 주의:**
> - 이건 **파일을 복사·복원하는 방식**이라 대개 잘 되지만, Claude Code 내부 구조가 크게 바뀌면 복원 후 이어가기가 깨질 수 있습니다(best-effort).
> - 아카이브 사본은 세션당 1개씩 `~/.claude/session-archive/`에 쌓입니다. 대화가 크면 용량이 커질 수 있어요. (북마크를 지우면 아카이브 사본도 같이 지워집니다.)
> - 그래도 **정말 중요한 결과물은 세션에만 두지 말고 파일·커밋으로도** 남기는 걸 권장합니다.

### 저장되는 정보

북마크는 `~/.claude/session-bookmarks.json`에 저장됩니다 (첫 저장 시 생성, **이 repo에는 포함 안 됨**). 항목 형식:

```json
{"name": "이름", "tool": "claude", "id": "UUID", "dir": "/작업/폴더", "saved": "YYYY-MM-DD"}
```

### 명령어 (참고용 — 직접 칠 필요 없음)

> 위 "이렇게 씁니다"처럼 **말로만** 쓰면 됩니다. 아래 표는 내부적으로 어떤 동작이 있는지 궁금한 사람을 위한 참고입니다. Claude가 상황에 맞는 걸 알아서 실행하며, 스크립트 경로도 설치 방식에 맞춰 자동으로 찾습니다.

| 서브커맨드 | 기능 |
|---|---|
| `list` | 저장된 북마크 전체를 카테고리별로 보기 |
| `current NAME` | 지금 실행 중인 이 세션을 저장 + 자동 아카이브 (Claude Code 전용) |
| `add NAME TOOL ID [--dir D]` | resume 명령의 UUID로 북마크 추가 + 자동 아카이브 |
| `archive NAME` | 이미 저장된 세션의 대화기록을 지금 아카이브(영구보관) |
| `todo NAME` | 세션 생기기 전에 이름만 예약, 나중에 저장하면 자동 연결 |
| `open NAME` | 새 터미널 창에서 세션 열기 (macOS) |
| `cmd NAME` | resume 명령어만 출력 (실행 안 함) |
| `clip NAME` | resume 명령어를 클립보드에 복사 (macOS) |
| `remove NAME` | 북마크 삭제 |
| `rename OLD NEW` | 북마크 이름 변경 |
| `cat NAME CATEGORY` | 카테고리 지정/해제 |

이름은 **부분 일치**로 찾습니다. `list`에서 `📦 보관됨`은 원본이 지워졌어도 아카이브로 복원 가능하다는 뜻이고, `DEAD`는 아카이브조차 없어 복구 불가라는 뜻입니다.

---

## English

Bookmark your Claude Code / Codex sessions by name, then list, resume, and reopen them from a new terminal. Ask Claude in plain language — you never touch a session ID; a small bundled Python script does.

**Why:** after a while you have dozens of sessions, each identified only by a long UUID. This skill lets you tag one "API refactor" and jump back into it later just by naming it.

**💬 How you use it** — just talk to Claude Code:

| 🗣️ You say | ✅ What happens |
|---|---|
| 💾 *"save this session as 'API refactor'"* | bookmarks the current conversation + **auto-archives the transcript** 📦 |
| 📋 *"show my sessions"* | prints your bookmarks as a table (alive / archived marked) |
| 🪟 *"open the API refactor session"* | a new terminal opens, resuming that conversation (auto-restored from archive if needed) |
| 📎 *"give me the API refactor code"* | copies the resume command to your clipboard |
| 🗄️ *"archive the API refactor session"* | makes a permanent copy of an already-saved session |
| 🗑️ *"delete the API refactor session"* | removes the bookmark and its archived copy |

Names match partially — *"open refactor"* is enough. 🔍

### 📂 What the list looks like

Say *"show my sessions"* and Claude renders a table like 👇

| 🗂️ Category | 📌 Name | 🛠️ Tool | Status | 📅 Saved |
|---|---|---|---|---|
| work | API refactor | claude | ✅ alive | 2026-07-06 |
| personal | blog draft | codex | ✅ alive | 2026-06-30 |
| 미분류 | log parser | claude | 📦 archived (restorable) | 2026-05-20 |
| 미분류 | research later | — | ⏳ pending (no session) | 2026-07-05 |

- ✅ **alive** — original still there, resume right away
- 📦 **archived (restorable)** — original was auto-deleted after 30 days, but the archived copy survives → opening it auto-restores and resumes
- ⏳ **pending** — a name reserved before a session exists (auto-links when you later save under the same name)
- 💀 **dead (unrecoverable)** — only if it was deleted before archiving, or archiving failed

### Requirements

- **macOS** — uses `pbcopy` (clipboard) and `osascript` + Terminal.app (open in new window)
- **Claude Code** — the `current` command needs the `CLAUDE_CODE_SESSION_ID` env var Claude Code sets
- **Python 3** — standard library only, no dependencies

> Linux/Windows: `list`, `add`, `cmd`, `remove`, `rename`, `cat`, `todo` work anywhere. `clip` (pbcopy) and `open` (Terminal.app) are macOS-only.

### Install — Method A: plugin (recommended)

Inside Claude Code:

```
/plugin marketplace add jazznyeop/claude-session-manager
/plugin install session-manager@jazznyeop
```

### Install — Method B: copy the skill folder

```bash
git clone https://github.com/jazznyeop/claude-session-manager.git
cp -r claude-session-manager/skills/session-manager ~/.claude/skills/
```

Or just tell Claude Code: *"clone https://github.com/jazznyeop/claude-session-manager and register it as a skill"*.

Restart Claude Code. Read `skills/session-manager/scripts/sessions.py` before installing — ~250 lines of stdlib Python, no network calls. Look before you run.

### 🗄️ It keeps sessions alive (auto-archive)

Claude Code deletes transcripts older than `cleanupPeriodDays` (default 30). To prevent losing them, this skill **copies the transcript (`.jsonl`) into `~/.claude/session-archive/` the moment you save a session**. So 👇

- 🛟 Even after Claude Code deletes the original at 30 days, the **archived copy survives** and you can still resume.
- 📦 When you open a session (*"open"* / *"give me the code"*) and the original is gone, it's **auto-restored from the archive** first.
- 📂 Such sessions show as `📦 archived (restorable)` in `list`.
- ✋ To archive an already-saved live session right now, say *"archive NAME"*.

> ⚠️ **Honest caveats:**
> - It works by **copying/restoring files** — reliable in practice, but a major change to Claude Code's internals could break resume-after-restore (best-effort).
> - One archived copy per session accumulates in `~/.claude/session-archive/`; large conversations take space. (Deleting a bookmark deletes its archived copy too.)
> - Still, don't keep important work *only* in a session — save it to files/commits as well.

### What it stores

Bookmarks live in `~/.claude/session-bookmarks.json` (created on first save, **not** part of this repo):

```json
{"name": "...", "tool": "claude", "id": "UUID", "dir": "/work/dir", "saved": "YYYY-MM-DD"}
```

### Commands

The SKILL.md resolves the correct script path for either install method. Subcommands:

| Subcommand | Does |
|---|---|
| `list` | show all bookmarks, grouped by category |
| `current NAME` | bookmark the session this is running inside + auto-archive (Claude Code only) |
| `add NAME TOOL ID [--dir D]` | add a bookmark from a resume command's UUID + auto-archive |
| `archive NAME` | archive an already-saved session's transcript now |
| `todo NAME` | reserve a name before a session exists; auto-links when saved later |
| `open NAME` | open the session in a new Terminal window (macOS) |
| `cmd NAME` | print the resume command without running it |
| `clip NAME` | copy the resume command to the clipboard (macOS) |
| `remove NAME` | delete a bookmark |
| `rename OLD NEW` | rename a bookmark |
| `cat NAME CATEGORY` | set/clear a bookmark's category |

Name matching is partial. `📦 archived` in `list` means the original was deleted but the archived copy can restore it; `DEAD` means no archive exists either, so it's unrecoverable.

---

## License

MIT — see [LICENSE](LICENSE).
