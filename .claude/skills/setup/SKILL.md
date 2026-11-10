---
name: setup
description: Setup wizard. Run when the user says "set me up" (or "set up my channels", "build my layout", "get me started"). Builds their layout - one orchestrator project plus one project and git repo per private channel - writes a criteria file per session, installs the coach rules, and tells them exactly what to type first.
---

# Setup wizard

Goal: turn "set me up" into a working layout without the user having to know anything. Read `handoff-kit/WORKFLOW.md` for what the layout is and `handoff-kit/COACH.md` for how to talk. Follow the coach rules the whole time.

## Hard rules
- Never run anything destructive: no deletes, no force pushes, no overwriting a non-empty folder, no changing existing repos. If a target folder exists and is not empty, pick a new name (`-2`) and say so.
- Never create accounts, sign in, or type passwords or tokens for the user. If they need an account or a login, give the exact steps, wait, then check it worked (`gh auth status`). Don't trust "done"; verify.
- Every repo you create is **private**. Never make anything public. Never add collaborators.
- Never put secrets, keys or personal paths into files that go to GitHub.
- Questions: numbered, one line each, with `(default: ...)`. A bare "continue", "ok", "sure", "yes" or "idk" is not an answer. Re-ask only the unanswered items in one line. Accepting a default needs the number plus the word "default" (`3 default`).
- No time estimates. Short plain words.

## Step 0: look around (silently)
Check without asking: which agent you are (Claude Code or Codex), `git --version`, `python --version`, `gh auth status`, and whether T3 tools exist (try `t3_project_list`). Note what is missing; only mention problems.
If git or Python is missing, tell the user the install steps and stop until they've done it.

## Step 1: the questions (one message, then wait)
Say in two lines what is about to happen, then ask exactly this list:

1. Your channels. One line each: name, and what it's about. (Real answer needed. No default.)
2. Platform for each channel: YouTube, TikTok, Instagram, other? (default: YouTube)
3. For each channel: private (only you) or shared with someone? If shared, with who? (default: private)
4. Your GitHub username, or "none". (default: none, repos stay on this computer)
5. Where should folders live? (default: a folder called ContentOS in your home folder)
6. Yap: what do you want all this to become in a year? Say it messy, big or weird goals included. Nothing is too much.

Check every answer against the coach rules before moving on:
- Missing or bare-ack items: reply with one line, `Still need: 1, 6. Answer each in a few words, or say "3 default".` Nothing else.
- Q6 is thin (under about 15 words): ask for more once: "What else is in your head, bigger or weirder?"
- If a channel idea or goal looks weak, say so in one sentence with the reason and a better option. Don't cheer.
- Then ask once: "Anything you want that you think is unrealistic? Say it anyway." Add whatever they say to Q6.

## Step 2: show the plan, ask for the build word
Show a short table: orchestrator folder, one row per private channel (folder, platform, repo name `<username>/<slug>` or "local only"), and any shared channels (recorded only; you don't create shared repos).
Rules for names: lowercase slugs from channel names. Orchestrator folder: `contentos-orchestrator`.
Then: `Type BUILD to create this, or tell me what to change.` Only the word BUILD (any case) proceeds.

## Step 3: build (after BUILD)
Do everything yourself. Order:

**A. Orchestrator**
1. Create `<root>/contentos-orchestrator`, `git init`.
2. Copy from `handoff-kit/templates/orchestrator/` (AGENTS.md, CLAUDE.md, README.md, DECK.md, shared.md, .gitignore) into it. Create `criteria/`.
3. Copy `handoff-kit/WORKFLOW.md`, `COACH.md`, `PROMPT-BOOK.md`, `criteria-template.md` into its `handoff-kit/` folder, and `.claude/skills/setup/SKILL.md` into `.claude/skills/setup/`.
4. Paste the contents of `handoff-kit/COACH.md` into its `AGENTS.md` between the markers `<!-- handoff-kit:begin -->` and `<!-- handoff-kit:end -->` (replace what is between them).
5. Write `criteria/orchestrator.md` from the template using their answers (see "Criteria files").
6. Write `shared.md` with the shared channels and the usernames they gave.

**B. One folder and repo per private channel**
1. Create `<root>/<slug>`. Seed it by copying everything inside `handoff-kit/seed/creator-launch/` (the channel launch toolkit: research method, templates, `launchkit` tools). If that folder doesn't exist but the current repo has `launchkit/` and `docs/FIELD-GUIDE.md`, copy those, plus `templates/`, `examples/`, `tests/` and `README.md`, from the current repo (skip `.git`, `work/`, `__pycache__`). Otherwise copy `handoff-kit/templates/channel/` instead and say the full toolkit is missing.
2. `git init`. Copy `handoff-kit/templates/channel/AGENTS.md` to `AGENTS.md` (the seed has none) and install the same kit files as in A.3 and A.4 (its AGENTS.md gets the coach block).
3. Run `python -m launchkit init <slug>` inside it if that module exists.
4. Write `CRITERIA.md` from the template using their answers for this channel.
5. Write `ORCHESTRATOR.local.md` (it is git-ignored) holding the orchestrator's local folder path, and add that file to `.gitignore`.
6. Add the channel to the orchestrator's `criteria/` as `criteria/<slug>.md`: a short stub saying where the real file is (`<channel folder>/CRITERIA.md`).

**C. Git and GitHub**
- Commit in each new repo with a clear message.
- If they gave a GitHub username and `gh auth status` is good: `gh repo create <username>/<name> --private --source <folder> --push`. If `gh` isn't signed in: tell them `gh auth login` and wait, then retry. If they said none: leave local-only and say so.
- Check afterwards: `git status` clean, `gh repo view` shows PRIVATE.

**D. T3 projects**
- If T3 tools exist: `t3_project_create` with `title` and `workspaceRoot` for the orchestrator (title "Orchestrator") and for each channel (title = channel name). Then `t3_thread_launch` in the orchestrator project only, title "Orchestrator", message: "Read AGENTS.md. The user will say 'yap'. Run the vision dump." Don't launch threads in the channel projects.
- If T3 tools don't exist: give plain manual steps: open T3 Code, choose Add project, pick each folder (list them), name them. 
- Never run anything else on their machine they didn't agree to.

**E. Criteria files** (for orchestrator and each channel)
Use `handoff-kit/criteria-template.md`. Turn their Q6 yap and channel answers into 3 to 8 checkable lines each, their words quoted, weird and unrealistic goals kept.
- **Never shrink a goal.** A big or weird goal ("a million subs in 6 months") stays as its own line, in their words, with a plain check (the number, from the platform). Then tell them honestly in the plan how unlikely or hard it is and why. Put any smaller milestone you'd suggest on a separate line marked `(coach suggestion, not yours)`. Never write "you agreed" for something they didn't say.
- Mark all `NOT DONE` with the reason "just started".
- Add at least one line the user didn't think of that a good coach would ("first video posted and watched end to end by one stranger"), marked as your suggestion.

**F. Memory**
Save to your memory system: who they are, their channels, their goals in their words, that they want to be coached this way. Don't save secrets.

## Step 4: verify, then hand over
Prove it before claiming done: list the folders created, `git log -1` per repo, whether each is PRIVATE or local-only, and each T3 project created (or the manual steps). If anything failed, say so first.
Then end with exactly one instruction, in this form:

> Open project **Orchestrator** in the T3 sidebar, open the thread **Orchestrator**, and type: `yap`

(If T3 tools weren't available: "Open the folder <path> in your agent and type: `yap`".)
Nothing after that line.
