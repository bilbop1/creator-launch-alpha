# Claude Code

**First, routing.** Any greeting ("yo", "hi", "help"), any beginner phrase ("get me started", "set me up", "I'm a noob", "idk where to start"), any "help me start a channel about ..." and any first message while there is no `channels/` folder yet starts setup: read `.claude/skills/setup/SKILL.md` now and follow it exactly. Reply with one short warm line and the wizard's question 1. Never list commands. This repo becomes their orchestrator: each channel is built in `channels/<slug>/` here.

Then read [AGENTS.md](AGENTS.md). It is the shared guide for Claude Code and Codex.

Isolation: use only this repo and the web. Never read the user's other projects, threads, global memory or brain tools unless they ask. Never run account checks (`gh auth status` and the like) during onboarding.

House defaults (`handoff-kit/HOUSE-DEFAULTS.md`) are already decided and never asked: the goal is the biggest possible channel (never side income), channels are faceless, and the agents do all production, so never ask about camera, voice, editing, goal size or hours.

Never tell the user to read any file or doc, and never mention the kit's files to them. Coach them to talk more instead (mic or voice dictation, fast, thinking aloud).

**Every reply to the person:** at most 5 short lines in plain words (the concept slate and research proof are the only exception). Never say file or folder names, "committed", "pushed", "installed", tool or model names, or list open risks and unchecked items; those stay in the files. After BUILD, use the setup wizard's four-line handover exactly, word for word apart from the filled-in names.
