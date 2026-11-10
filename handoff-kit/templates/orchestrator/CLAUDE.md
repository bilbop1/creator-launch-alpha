# Orchestrator for Claude Code

Read [AGENTS.md](AGENTS.md) first. It is the shared guide for Claude Code and Codex: isolation rules, the method, the Deck, sweeps and the coach rules.

Isolation: use only this repo and the web. Never read the user's other projects, threads, global memory or brain tools unless they ask. Never run account checks (`gh auth status` and the like) during onboarding.

Any greeting ("yo", "hi", "help"), any beginner phrase ("get me started", "start onboarding", "I'm a noob", "idk where to start"), and any first message while there is no `channels/` folder yet starts setup: follow `.claude/skills/setup/SKILL.md`. Reply with one short warm line and question 1. Never list commands.
