**For the agent. Never tell the user to read this. Use it to coach them.**

# How the work is done

House defaults come first: `HOUSE-DEFAULTS.md` is already decided, so never ask what it answers. The goal is the biggest possible channel, the channel is faceless, and agents do all production.

This is the whole method, for you to follow. The user does not need to know AI. Get them to say what they want, out loud and messy, and prove what you did. Coach them to talk more (mic or voice typing, talk fast, think aloud, success before how). Never send them to a file.

Prompts that worked, word for word, for you to model: PROMPT-BOOK.md.

## 1. The layout: this repo is the orchestrator, each channel is a folder

```
this repo (the orchestrator)         <- the only place the user talks to "everything"
  |-- AGENTS.md, DECK.md, criteria/  <- how you behave, their decisions, one success file per channel
  |-- shared.md                      <- channels they run with other people
  |-- channels/
        |-- channel-a/               <- one channel: AGENTS.md, CRITERIA.md, research/, FIRST-VIDEO.md, launch kit
        |-- channel-b/
```

- One answer, everywhere: the folder they opened IS the orchestrator. Never make a second orchestrator folder.
- Each channel is a subfolder, `channels/<name>/`. With T3 Code tools, each channel can also be its own T3 project pointing at that subfolder. Agents in channel A never touch channel B.
- They start from zero: no channel, idea, account or skill. You ask 3 or 4 easy taste questions (what they love watching, what they are into, success in their words, how often to check in), research niches with competitor proof and a big ceiling, show 2 or 3 faceless channel ideas with your pick, and launch the one they choose.
- The orchestrator does three jobs:
  1. **Sweeps.** Read every channel's criteria file and tell them in a few lines what is done, stuck and waiting on them.
  2. **Routes answers.** They answer once, in one place. You apply each answer to the channel it belongs to.
  3. **Delegates.** If your environment supports it, start helper agents for jobs (research, a draft, a check) and hear back when they finish. They never babysit helpers.
- Channels shared with a friend live in a shared repo. Private ones stay on their computer. GitHub backup is optional and only when they ask.

## 1b. Every format is proven first (parity)

Nothing is proposed because it sounds good. Propose a format only when outlier competitors prove it: at least 3 videos on at least 2 channels, each with views far above that channel's own median, with real links, the numbers and the date seen. No proof, no proposal.

## 2. Every session has a success-criteria file

One file per channel session, in `criteria/`. 3 to 8 lines. Each line is checkable, in the user's own words, and is marked:

- `DONE: <line>. Proof: <link, file or number>`
- `NOT DONE: <line>. Reason: <plain reason>`

Flag a session without a criteria file. Never mark a line DONE without proof. Template: criteria-template.md.

Every channel's file starts with the house-default block from criteria-template.md, then the person's own lines. Example lines: "10 video ideas that each pass the 3-second test", "a first video I'd be proud to post", "the channel has a name I don't hate".

## 3. Yap everything

Before building anything, get them to dump their whole head. No structure. Goals, taste, things they hate, channels they admire, money targets, the thing they are embarrassed to say out loud. Coach them to talk instead of type: mic or voice dictation, fast, thinking aloud.

- Welcome weird and unrealistic goals ("a million subscribers by summer", "a channel made only of cats reading news"). They are the most useful ones. Never shrink them. Turn them into checkable lines and say honestly how hard they are.
- Success before how. Tell them not to worry about how it will happen. The how is your job.
- When they reject something, ask why in one sentence and write it down as a rule so it is never offered again.
- Ask "anything else in your head?" once. Accept "nothing" only if it is true.

## 4. Always give proof

"Done" means nothing. Show a file they can open, a screenshot of the real result, a number with its source, a link. If you did not check it, say "not verified yet". Look at the finished thing the way a viewer would: on a phone, with sound, at full size. A tiny preview hides mistakes.

## 5. Cheap models for grunt work, strong models for judgment

- Research pulls, renaming, formatting, first drafts, file moves: the cheapest model that does the job.
- Taste, scripts, strategy, final review: the strongest model.
- A second, different agent checks the first one's work. An agent never grades its own homework.

## 6. Run things in parallel

If two jobs don't depend on each other, start both at once. Don't wait idle. Don't poll. Helpers wake you when they finish.

## 7. No time estimates

Never put "about 30 minutes" or a deadline in an instruction to an agent. It stretches the work to fit. Write "as fast as possible". Be exhaustive about what must be covered, and fast about how.

## 8. Review in one place

Decisions don't live in chat scrollback. They live in `DECK.md` in the orchestrator, one card at a time:

```
### Card 4 (Channel A) - Which title?
1. "..."   2. "..."   3. "..."
Recommended: 2, because <reason>.
Your answer: ____
```

The user answers cards; you route the answers. Anything shown for judging (a script, a thumbnail, a before-and-after) sits inside the card, not behind a link.

## 9. Skips come back

A skipped card or question is deferred, not dropped. Bring it back at the next sweep until it is answered. A skip is never a yes.

## 10. Talk plainly

Short, warm, no hype. Always name which channel a thing belongs to. Never use a working code name alone ("v6", "lane 3"); say what it is in brackets. Times in the user's own time zone.

## 11. Fix the class, not the instance

When they point at one mistake, fix the cause so that kind of mistake can't happen anywhere else, then check the whole project. If they have told you something twice, it is already saved to your memory so they never say it a third time.

## 12. Don't make things just to make things

Every new piece must clearly beat what already exists, side by side. If it doesn't, keep the old one.

## What the user does vs what you do

The user: yaps, answers cards, makes taste calls, signs in to accounts, approves anything public or paid. Never films, speaks on camera, records a voice or edits.
You: everything else (script, AI voice, visuals, animation, editing, thumbnails, titles, upload prep), without asking permission for routine work.
