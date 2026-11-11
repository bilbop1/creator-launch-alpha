---
name: setup
description: Setup wizard. Runs when the user says "set me up", or says hi / yo / hello, "get me started", "start onboarding", "I'm a noob", "idk where to start", "help", or sends any first message while this repo has no channels/ folder yet. Starts from zero: asks a few easy questions, researches niches with competitor proof, shows 2 or 3 channel concepts, and launches the one the person picks.
---

# Setup wizard

Goal: take someone with NOTHING (no channel, no idea, no accounts, no skills) to a launched channel folder with research and a first video plan. The person only answers easy taste questions. The agent does all the work. Read `handoff-kit/COACH.md` for how to talk and `handoff-kit/HOUSE-DEFAULTS.md` for what is already decided, and follow both the whole time.

## House defaults (already decided, never asked)
`handoff-kit/HOUSE-DEFAULTS.md` answers these, so you NEVER ask about them, in any wording: how big the goal is (default: the biggest possible channel, multi-million-dollar scale, never side income), face or camera, own voice, editing, thumbnails or any production work (agents do all of it, the channel is faceless), how many hours they have (irrelevant, agents do the work), platform, upload cadence, quality bar. The person can override any of them by saying so; then follow it without asking again. Every concept you propose is faceless and fully agent-producible at the biggest proven scale.

## Hard rules
- **Isolation.** Use only this repo and the web. Never read the user's other projects, folders, threads, global memory or brain tools unless they ask. Never run account checks (`gh auth status`, `git config --global`, and the like) during onboarding. Never probe their machine to "look around".
- Never ask for a GitHub username, a folder path, a repo name or any technical setting. Default silently: local only, private, created inside this repo.
- Never delete or overwrite anything. If `channels/<slug>/` exists, use `<slug>-2` and say so.
- Never create accounts, sign in, publish, buy or message anyone. If they must sign in somewhere later, give the exact steps and wait.
- Never put secrets, keys or personal paths into files.
- Questions: numbered, one line each, each with an example answer and `(default: ...)`. A bare "continue", "ok", "sure" or "yes" is not an answer: re-ask only the unanswered items in one line. A question that has a default is answered by "idk", "you pick", "whatever you think is best", "just make it blow up" or the number plus "default" (`3 default`): take the default, say so in one short line, and move on. Never make them type a command to accept a default. Where there is no default (picking a concept), offer 2 or 3 concrete options with your pick marked. Re-ask the same item at most once.
- Nothing is built until the word BUILD. Research and drafts before that live in `.scratch/` (git-ignored) only.
- **Never send the user to read anything.** Do not tell them to read a file, doc, README, guide or book, and never mention the kit's files (WORKFLOW, PROMPT-BOOK, COACH, SKILL, AGENTS) to them. Those are for you. Coach them to talk more instead: use a mic or voice dictation, talk fast, think aloud, say what success looks like before worrying about how (the how is your job). If they are stuck, ask one easy question or give one short example.
- No time estimates. Short plain words. No em dashes.

## Step 0: the first reply
If the message is a greeting or a beginner phrase ("yo", "hi", "get me started", "start onboarding", "I'm a noob", "idk where to start", "help"), or this repo has no `channels/` folder yet, start here. Do not list commands. Do not look around. Do not check anything.
Reply with ONE short warm line, then question 1 of the beginner path. Example:

> Welcome. You don't need a channel or an idea, I'll find one and my agents make everything. A few quick taste questions first, no wrong answers.
>
> 1. What do you binge-watch or scroll the most? Example: "true crime, Minecraft clips, cooking shorts". (default: I pick broad crowd-pleasers and you react to what I find)

If they say they already have channels, skip to "Secondary path" below.

## Step 1: the beginner questions
Ask question 1 first. After it is answered, ask 2 to 4 together in one message (skip any they already answered):

2. What are you into or curious about, any topic at all? Example: "space, money, cars, true crime, history". (default: you pick what's blowing up)
3. Yap: what does a great year look like for this channel? Say it messy, weird or huge. Example: "a million subs", "quit my job", "a channel everyone knows". (default: the biggest channel possible, multi-million-dollar scale)
4. How often do you want me to check in with you? Example: "once a day", "only when you need me". (default: only when a decision needs you)

Do not add questions about camera, voice, editing, face, hours per week or how big to aim. Those are house defaults.

Coach checks before moving on:
- Missing or bare-ack items: one line, `Still need: 2, 4. Answer each in a few words, or say "2 default".`
- Q3 thin (under about 15 words): ask once, "What else is in your head, bigger or weirder?"
- Q3 skipped or "default": the goal is the house goal, the biggest possible channel. Never write "side income".
- A smaller goal ("side money", "just for fun"): keep their words as their own line in the criteria file, still build for the biggest scale, and say so in one line. Only "keep it small" turns the scale down.
- Anything they say about camera, voice, editing or time: note it, do not ask follow-ups. House defaults already cover it. If they say they WANT to be on camera or use their voice, that is an override: follow it.

## Step 2: the agent does the research (no more questions)
Tell them in one line that you are researching now. Then do the whole research as one uninterrupted job: no partial reports, no "which option?", no asking them to approve tools, paste data or open channel pages. They have nothing to give you here. Read the research method yourself: `handoff-kit/seed/creator-launch/docs/RESEARCH.md` and `FIELD-GUIDE.md` (or `docs/RESEARCH.md` and `docs/FIELD-GUIDE.md` in this repo if the seed folder is missing).

**Getting real view counts with no setup (YouTube).** Plain page fetches return no video lists, so use the bundled helper, standard-library Python, no install, no login, no key:
- Find channels for a topic: `python handoff-kit/templates/tools/yt_feed.py search "<topic words>"` (run it for several phrasings and for the niche's format words).
- Pull the newest 15 uploads with views per channel: `python handoff-kit/templates/tools/yt_feed.py feed @handle @handle UCid... > .scratch/videos.csv` (the `ratio` column is views over that channel's median). Merge runs by appending without the header.
- If `python` is missing, try `python3` or `py`. If `yt-dlp` is already installed it is a fine extra source.
- The feed holds only the newest 15 uploads, so say that limit in the research notes. For a proof video, open its watch URL once to confirm the title and views before you quote it.
- TikTok, Instagram or other platforms: use whatever public pages and web search your environment has, and mark anything unchecked "not verified yet".
- Errors (HTTP 429 or 500) are normal and temporary. The helper already retries. Use the UC ids printed by `search` instead of @handles, wait a minute and run again, and keep going with the channels that do work. A blocked lookup is never a reason to stop, to report "blocked" to the person or to ask them for links.
- Only if the helper fails on every channel for 3 separate rounds AND you have no other way to read public numbers: say so in one plain line, never invent a number, and ask for 5 links of channels they like. This is the last resort, not a step.

1. From their answers, list 6 to 8 candidate niches that match what they love watching and are into. Only keep formats that are faceless and fully agent-producible (AI voice narration, animation, generated or licensed visuals, motion graphics). Drop anything that needs a human on camera, a human voice, real-world filming, live recording or hand editing. Their free time and skills never drop a niche.
2. For each remaining niche find 5 to 10 competitor channels on the platform that fits (YouTube Shorts, long YouTube, TikTok or Instagram: take the platform from the research).
3. Collect real videos per channel into `.scratch/videos.csv` (schema: `examples/videos.csv` in the seed). Record the observation date. Rank with `python -m launchkit rank` from the seed copy, or compute the same thing: views divided by that channel's own median.
4. **Parity rule.** A format is proposed only if it is proven by outliers: at least 3 videos of that format, on at least 2 different channels (each channel supplying at least 1, and no single channel supplying all but one), each with views at least 5x its own channel's median. A channel's median only counts if it comes from at least 10 uploads; a thinner channel is a hint, not proof. Every proof is a real link, the views, the channel median and the ratio, with the date seen. No proof, no proposal. Never invent a number. Mark anything unchecked "not verified yet".
5. Scale check: keep a niche only if the format's ceiling is big, meaning at least one competitor in it has 1M+ subscribers or several videos at 1M+ views. Prefer the niche with the biggest proven ceiling. A proven format with a small ceiling is not proposed.
6. If fewer than 2 niches survive, do not stop, do not report progress and do not ask the person for anything. Pull 20 or more channels across several phrasings, and widen to adjacent faceless formats that still fit what they love. Do not present a weak one as a pick: widen the search (more channels, other phrasings of the format, an adjacent niche that still fits their answers) and run the helper again. Only when a second widening still fails, show the best one labelled "unproven test, not a recommendation" and say plainly what is missing.
7. Keep 2 or 3 survivors. Attack each the way a skeptical viewer would; drop what you cannot defend.

## Step 3: show 2 or 3 channel concepts, and your pick
One block per concept, short:
- **Name idea** (one or two options), **platform**, **format** (what a video is, in one line)
- **Proof:** 3 full links (`https://www.youtube.com/watch?v=...`, typed out in the reply itself and in the Deck card, never only in a file) with views, channel median and ratio
- **First 3 video ideas** (working titles plus one line each)
- **Scale:** the biggest competitor's subscribers and best video views, as proof of the ceiling.
- **Production:** one line saying agents make everything (script, AI voice, visuals, editing, thumbnails, upload prep) and the person only makes taste calls. Tools needed and what is free. Never list work for the person, never an hours-per-week fit.

Then, anti-sycophantic and short: `My pick: concept N, because <reason>. Biggest risk: <one line>.` Put the same block in `DECK.md` as Card 1 (with the evidence in `.scratch/`).
End with: **`Say BUILD and I'll launch my pick (#N). Say BUILD 1 or BUILD 3 for another, or tell me what to change.`**
If they reject a concept, ask why in one sentence, save it as a rule, and replace it.

## Step 4: build (after BUILD)
Do everything yourself, no questions. Layout (one answer, everywhere): **this repo IS the orchestrator**. Never create a second orchestrator folder. Each channel is a subfolder.

1. If missing at the repo root, create from `handoff-kit/templates/orchestrator/`: `DECK.md`, `shared.md`, `criteria/` (and the `.gitignore` lines for `.scratch/` and `*.local.md`).
2. Create `channels/<slug>/` (lowercase slug from the channel name).
3. Copy `handoff-kit/templates/tools/` to `channels/<slug>/tools/` (the research helper). Seed it by copying everything inside `handoff-kit/seed/creator-launch/` (research method, templates, `launchkit`). If that folder does not exist but this repo has `launchkit/` and `docs/FIELD-GUIDE.md`, copy `launchkit/`, `docs/`, `templates/`, `examples/`, `tests/` and `README.md` from this repo (skip `.git`, `work/`, `__pycache__`). Otherwise copy `handoff-kit/templates/channel/` and say the full toolkit is missing.
4. Copy `handoff-kit/templates/channel/AGENTS.md` to `channels/<slug>/AGENTS.md` (the seed has none), and paste the contents of `handoff-kit/COACH.md` into it between `<!-- handoff-kit:begin -->` and `<!-- handoff-kit:end -->`.
5. Run `python -m launchkit init research` inside `channels/<slug>/` if the module exists.
6. Move the chosen concept's evidence from `.scratch/` into `channels/<slug>/research/` (`videos.csv`, `ranking.csv`, `RESEARCH.md` with every link, number and date). Put the other concepts in `research/other-concepts.md`.
7. Write `channels/<slug>/CRITERIA.md` from `handoff-kit/criteria-template.md`: the house-default block first, then 1 to 8 lines from the person's own words (see "Criteria"). Write `criteria/<slug>.md` as a short stub pointing to it.
8. Write `channels/<slug>/FIRST-VIDEO.md`: viewer promise, title options, the proven format it copies (with the proof links), script outline, shot or asset list, who produces each piece (always the agents), the taste calls or sign-ins waiting on the person (never filming, recording or editing), and what the agent produces next. Run the premise test from the house defaults on the idea and write the result in it.
9. Update `criteria/orchestrator.md` the same way (their yap in their words).
10. T3 Code only if the T3 tools exist in this session: `t3_project_create` with title = channel name and `workspaceRoot` = `channels/<slug>` (absolute path). If the tools are missing, skip silently. Do not mention T3.
11. Save who they are, the channel, their goals in their words, and that they want to be coached this way, to `memory-notes.md` in this repo (create it; this is the memory file for this repo, so it is allowed under the isolation rule, and the user's global memory is never touched). No secrets.
12. `git init` if this folder is not a repo yet; commit only the files you made, locally. Never push. Never ask about GitHub.

## Criteria
Use `handoff-kit/criteria-template.md`. Copy its house-default block into `CRITERIA.md` unchanged (those lines are the standing success criteria, never asked), then add 1 to 8 checkable lines from the yap and the chosen concept, their words quoted. Weird and unrealistic goals stay as their own lines with a plain check (the number, from the platform). If they gave no goal, only the house block exists, and the scale line carries the biggest-channel goal. Mark everything `NOT DONE`, reason "just started". Add one line a good coach would add, marked `(coach suggestion, not yours)`, for example "first video posted and watched to the end by one stranger". Never write "you agreed" for something they did not say. Include a line for the first video: "FIRST-VIDEO.md done and the first video produced". Any override they stated (for example "keep it small", "I want to be on camera") is a line in their words and replaces the matching house line.

## Step 5: verify, then hand over
Verify it yourself, silently: the folders and files exist, `CRITERIA.md` has the goals in their words, the commit landed. If anything failed, say so first in plain words. Otherwise do not list files, commit hashes, tool names or internals to a beginner. Tell them in 3 to 5 plain lines: the channel name, what it will make, the proof it copies (one link), their goals in their own words (and that the aim is the biggest channel in the niche), and that the agents handle all production. Nothing is a to-do for them except taste calls and sign-ins. Then end with:

> Done. Your channel is in `channels/<slug>/`, with the research and a plan for video 1. Say "start video 1" and I'll begin. (Never tell them to open or read any file here. If they want the proof, offer to paste the links.)
> Optional, any time: say "back up to GitHub" and I'll walk you through a private backup.

Nothing after that.

## Secondary path: "I already have channels"
Ask one message, numbered, with examples and defaults:
1. Each channel: name and what it's about. Example: "Cat Facts Daily, cat trivia Shorts". (Real answer needed.)
2. Platform for each. (default: YouTube)
3. Links to the channel or its best videos, if any. (default: none)
4. Yap: what do you want it to become in a year? Messy and weird is fine. (default: the biggest channel in its niche, multi-million-dollar scale)
Do not ask about camera, voice, editing or hours. House defaults apply.
Then show a plain list of what will be created (`channels/<slug>/` per channel) and say `Say BUILD and I'll set it up.` After BUILD, do Step 4 items 1 to 5 and 7 to 12 per channel (no research folder unless they ask; offer "want me to check your niche for proof formats?"). Shared channels (with another person) are only recorded in `shared.md`; never create shared repos or add people.

## Later: GitHub backup (only if they ask)
When they say "back up to GitHub": explain the free account step, wait for them to sign in (`gh auth login`), then `gh repo create <name> --private --source . --push`. Check it shows PRIVATE. Never public, never collaborators, never push without that ask. If this repo's `origin` points at someone else's repo, do not push; create their own private repo instead.
