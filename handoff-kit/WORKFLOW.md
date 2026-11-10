# How I work (and how your agent should work with you)

This is the whole method in plain words. You don't need to know AI. You need to say what you want, out loud and messy, and make the agent prove what it did.

Prompts that work, word for word: [PROMPT-BOOK.md](PROMPT-BOOK.md).

## 1. The layout: this repo is the orchestrator, each channel is a folder

```
this repo (the orchestrator)         <- the only place you talk to "everything"
  |-- AGENTS.md, DECK.md, criteria/  <- how the agent behaves, your decisions, one success file per channel
  |-- shared.md                      <- channels you run with other people
  |-- channels/
        |-- channel-a/               <- one channel: AGENTS.md, CRITERIA.md, research/, FIRST-VIDEO.md, launch kit
        |-- channel-b/
```

- One answer, everywhere: the folder you opened IS the orchestrator. Never a second orchestrator folder.
- Each channel is a subfolder, `channels/<name>/`. If you use T3 Code, each channel can also be its own T3 project pointing at that subfolder. Agents in channel A never touch channel B.
- You start from zero. You don't need a channel, an idea, an account or a skill. The agent asks 5 easy questions, researches niches with competitor proof, shows 2 or 3 channel ideas with its pick, and launches the one you choose.
- The orchestrator does three jobs:
  1. **Sweeps.** It reads every channel's criteria file and tells you in a few lines what is done, what is stuck and what needs you.
  2. **Routes your answers.** You answer once, in one place. The orchestrator applies each answer to the channel it belongs to.
  3. **Delegates.** If your environment supports it, it starts helper agents for jobs (research, a draft, a check) and hears back when they finish. You never babysit them.
- Channels you run with a friend live in a shared repo you both use. Private ones stay on your computer, and GitHub backup is optional and only when you ask.

## 1b. Every format is proven first (parity)

Nothing is proposed because it sounds good. A format is proposed only when outlier competitors prove it: at least 3 videos on at least 2 channels, each with views far above that channel's own median, with real links, the numbers and the date seen. No proof, no proposal.

## 2. Every session has a success-criteria file

One file per channel session, in `criteria/`. 3 to 8 lines. Each line is something you can check, in your own words, and is marked:

- `DONE: <line>. Proof: <link, file or number>`
- `NOT DONE: <line>. Reason: <plain reason>`

A session without a criteria file is flagged. A line is never DONE without proof. Template: [criteria-template.md](criteria-template.md).

Example lines: "10 video ideas that each pass the 3-second test", "a first video I'd be proud to post", "the channel has a name I don't hate".

## 3. Yap everything

Before building anything, you dump your whole head into the chat. No structure. Goals, taste, things you hate, channels you admire, money targets, the thing you're embarrassed to say out loud.

- Say the weird and unrealistic goals too ("a million subscribers by summer", "a channel made only of cats reading news"). They are the most useful ones. The agent never shrinks them. It turns them into checkable lines and tells you honestly how hard they are.
- When you reject something, say why in one sentence. The agent writes that reason down as a rule so you never reject the same thing twice.
- When the agent asks "anything else in your head?", answer it. Say "nothing" only if it is true.

## 4. Always ask for proof

"Done" means nothing. Ask: "show me." Proof is a file you can open, a screenshot of the real result, a number with its source, a link. If it was not checked, the agent says "not verified yet". Look at the finished thing the way a viewer would: on a phone, with sound, at full size. A tiny preview hides the mistakes.

## 5. Cheap models for grunt work, strong models for judgment

- Research pulls, renaming, formatting, first drafts, file moves: the cheapest model that does the job.
- Taste, scripts, strategy, final review: the strongest model.
- A second, different agent checks the first one's work. An agent never grades its own homework.

## 6. Run things in parallel

If two jobs don't depend on each other, start both at once. Don't wait idle. Don't poll. The orchestrator starts the helpers and is woken when they finish.

## 7. No time estimates

Never put "about 30 minutes" or a deadline in an instruction to an agent. It will stretch the work to fit. Write "as fast as possible". Be exhaustive about what must be covered, and fast about how.

## 8. Review in one place

Decisions don't live in chat scrollback. They live in `DECK.md` in the orchestrator, one card at a time:

```
### Card 4 (Channel A) - Which title?
1. "..."   2. "..."   3. "..."
Recommended: 2, because <reason>.
Your answer: ____
```

You answer cards; the orchestrator routes the answers. Anything shown for judging (a script, a thumbnail, a before-and-after) sits inside the card, not behind a link.

## 9. Skips come back

If you skip a card or a question, it is deferred, not dropped. It comes back at the next sweep until you answer it. A skip is never treated as a yes.

## 10. Talk plainly

Short, warm, no hype. Always say which channel a thing belongs to. Never use a working code name alone ("v6", "lane 3"); say what it is in brackets. Times in your own time zone.

## 11. Fix the class, not the instance

When you point at one mistake, the agent fixes the cause so that kind of mistake can't happen anywhere else, then checks the whole project. If you've told it something twice, it saves it to its memory so you never tell it a third time.

## 12. Don't make things just to make things

Every new piece must clearly beat what already exists, side by side. If it doesn't, keep the old one.

## What you do vs what the agent does

You: yap, answer cards, make taste calls, sign in to accounts, approve anything public or paid.
The agent: everything else, without asking permission for routine work.
