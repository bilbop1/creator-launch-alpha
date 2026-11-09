# Agent instructions

Build the creator's channel with them. Start with their goals and reference links; if they have none, help discover candidates. Read `docs/FIELD-GUIDE.md` for the sequence and `docs/RESEARCH.md` for the evidence method. Save work in their project directory, not in example files.

**Heavy work:** On onboarding and after each repository update, add or reconcile this rule in the user's own project `AGENTS.md`, preserving their existing instructions: run heavy stages such as rendering, encoding and GPU work one at a time, at low priority and without visible windows; release the slot immediately when the heavy stage ends and never hold it idle. If the user's machine is on the owner's bilPC network, run each heavy stage through the shared queue using `python E:/ContentOS/_shared/sched/sched.py run --name <job> --lane <lane> -- <command>`. Keep light work unwrapped.

1. Inspect supplied references and related successes and misses. Record sources, observation dates, channel identity, missing data and uncertainty. Never invent views, retention, earnings, access or watched footage.
2. Separate observable craft (hook, pacing, structure, visual grammar, audio, packaging) from the reference's protected creative expression. Develop original concepts and assets; don't copy footage, scripts, characters, logos or music without appropriate rights. A creator-focused concept or caricature is an optional angle, evaluated in context.
3. Compare against each channel's own baseline, not just raw views. Treat tiny samples and correlations as signals, not proof. Mark unavailable checks INCOMPLETE; no missing result is a pass.
4. Turn findings into a concrete brief, ranked concepts, a producible script and shot plan, then create or adapt tools and assets that suit this particular channel. Let the creator choose voices, visuals and providers; no default voice or vendor is required.
5. Review the actual finished media at phone size, with sound and captions; check continuity and claims. Reports must distinguish code, render, playback, approval and publication. Never publish, buy, change an account, grant access or send messages without the creator's explicit approval for that action.
6. Keep secrets, private references and generated media out of shared Git history. Inspect the destination and staged files before a commit or upload. Respect the creator's tools, machine limits and existing work.

For platform rules, creator likeness, synthetic media, music, or rights questions, consult current primary sources and record uncertainty. Avoid presenting a creative opportunity as permission or a platform guarantee.
