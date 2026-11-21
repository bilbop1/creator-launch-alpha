**For the agent. Never tell the user to read this. Follow it yourself.**

# Blind click tests and hill-climbing

Nothing is locked until it wins a strict blind test against the best-performing competitor version. This covers the premise, the script, every title and thumbnail, the hook, every shot type, motion, pacing, the voice, music, captions, the platform copy (section 8) and the finished cut (section 7). A video that skips this is not ready to post. Skip a test only where no competitor makes that thing, and say so.

This is the top priority of every session. The person should never open a review, or come back after an overnight run, and find work that was never climbed against the competition. Time goes into the climb before it goes into making more.

## 1. What counts as a test

A test is strict only if all of these hold:
- **Feed cards, not documents.** Judges see what a viewer sees on a phone: a mock mobile feed card with the thumbnail, the title, the channel name, the view count and the age. Shorts: the Shorts shelf card. Scripts are judged by their premise line, title and the first 15 seconds of narration, the way a viewer meets them.
- **Pairwise.** Each judgment is one of ours against one competitor card: "Which one do you tap?" Never a ranked list of many.
- **Both orders.** Every pair is shown twice, ours on top and ours below. A win counts only when it holds in both orders. A split is a tie.
- **No story context.** Judges never see our script, our research, our reasons, the channel plan or which card is ours. They get only the cards and one line on who the viewer is ("a 25 year old who watches finance news on YouTube"). A story-aware "which one fits our video best" ranking is a relevance ranking, not a test. Never call it one.
- **Different model families.** Use judges from at least two model families when you can reach them (for example Claude plus GPT or Gemini through whatever the person already has). No family supplies more than half the judges, and the agent that made the design never judges it. If only one family is available, use at least 5 fresh agents with no shared context and report the result as "single family, weaker evidence".
- **Fair metadata.** Our card shows the competitors' median view count and a similar age, so the numbers under the card never decide the tap.
- **The right opponents.** Opponents are the most-viewed similar competitor videos from the research (the top performers, never low-viewed ones), shown with their real titles, thumbnails and view counts.
- **Win bar.** A design locks only when it wins at least 60% of both-order pairs against the top competitors, beats the single best competitor card, and a majority of judge families agree. "Beats the single best competitor" has a minimum sample, set out in the next section.

Use `tools/feed_cards.py` (in the channel folder, or `handoff-kit/templates/tools/feed_cards.py`): `pairs` builds the both-order pair list, the judge prompts and an HTML sheet of mobile feed cards; `tally` scores the answers. Standard-library Python, no install.

## Minimum sample against the best competitor

This applies to every element type: premise, script, title, thumbnail, hook, each kind of shot, motion, pacing, voice, music, captions, copy and the finished cut. Two numbers decide, never one read.

1. **Overall.** Ours wins 60% or more of all both-order pairs against the top competitors together. A split pair (one order won, one lost) counts half.
2. **Best competitor.** The best competitor is the highest-viewed reference in the pool. Test against it with at least 6 both-order pairs, which is 12 reads, across two model families where you can reach them. Shuffle the order again for every read, so no judge sees a fixed pattern. Ours must win 60% or more of those reads.
3. **The middle band.** If the best-competitor result lands between 40% and 60%, add 6 more pairs against it, once. The combined total of all pairs then decides: 60% or more wins. Below 40% on the first 6 pairs is not won, and so is a combined total under 60% after the extra 6. Do not add the extra pairs when the first 6 already decided it, and never add them a second time.
4. **A single read never decides.** One lost read, or one won read, moves neither number on its own. A pair that splits is a half, not a loss.

Report both numbers and the best-competitor record in plain words, for example "overall 11 of 14 pairs (79%); against their top video (1.2M views) we took 9 of 12 reads (75%)". If only one model family was reachable, say "single family, weaker evidence" next to the numbers. Anything short of both numbers is "has not beaten the competition yet".

## 2. Titles and thumbnails are tested as a pair

A viewer sees them together, so they are judged together. Run three views of each important pair:
1. Full card (thumbnail plus title) against each competitor card.
2. Title only (text card, no thumbnails on either side).
3. Thumbnail only (same neutral title on both sides, or no title).

When a competitor beats us on title alone, say so plainly in the report ("their title beats ours on its own, 0 of 6"). A locked title can cap every thumbnail, so fix the title first when that happens.

## 3. Hill-climb each design on its own loop

Each candidate design (a thumbnail, a title, a premise, an opening) gets its own continuous loop, and all loops run in parallel:
1. Test it (strict, as above).
2. Read the judges' reasons for every loss, not just the score.
3. Fix exactly what the reasons name. Change nothing else.
4. Retest against the same opponents.
5. Keep the new version only if it scores higher. Otherwise revert to the previous best and try the next fix.

Never batch rounds (make 10, test 10, pick 1, start over). Never restart a design from scratch because one round lost; climb from the current best. Stop a loop when it passes the win bar or when three fixes in a row fail to raise the score, then report the best score with its numbers.

## 4. Thumbnail references

Thumbnail references come only from the most-viewed similar competitor videos: about 16 of the top-viewed ones in the niche. Never use low-viewed thumbnails as references. Keep the reference set with its links and view counts.

## 5. After posting

- Load the top 3 thumbnails from the blind test into YouTube Studio's built-in Test and compare (A/B/C) at upload, when the channel has access to it.
- Keep the ranked title list. If the early click rate trails the competitor benchmark, or a title candidate wins a fresh blind test, switch the title as soon as it wins. Use YouTube's title test when the channel has it.
- Record each switch with the date and the before and after numbers.

## 6. Reporting a test to the person

One short block per design: the score, the number of pairs, the judge families, the strongest competitor and whether we beat it, and any title-alone loss. Never say "it won" without the numbers. Never show the person a design that has not passed.

## 7. Picture, motion, sound, captions and the finished cut

The same loop applies to everything a competitor also makes: the opening seconds, each kind of shot, motion and transitions, pacing, the voice, the music and sound effects, captions and the finished video.
- **Matched clips.** Cut ours and the best-performing competitor's comparable moment to the same length (for example the first 15 seconds, or one explainer beat). Judges watch the real video with sound at phone size, not frame sheets or descriptions.
- **Same strict rules as section 1.** Pairwise, both orders, unlabeled, no story context, judges who did not make it, at least two model families when you can reach them. Ask "Which one would you keep watching?" and for the one concrete reason.
- **Climb per element, as in section 3.** Fix exactly what the losing reasons name, retest against the same competitor clip, keep only what scores higher. Climb each shot or element while it is being built; never render the whole video blind and test only at the end.
- **Overnight and unattended runs.** Spend the run climbing the weakest element first. The morning report leads with a scoreboard (each element, its score, the competitor clip it was tested against) and shows only work that passed, or the best version so far clearly marked "has not beaten the competition yet" with its numbers.

## 8. Copy: descriptions, pinned comments, community posts, Shorts text, script voice
- First it must pass `tools/copy_check.py` (the patterns on Wikipedia's "Signs of AI writing" page, `SIGNS-OF-AI-WRITING.md`), then `tools/copy_check.py style --ours <ours> --theirs research/parity/competitor_titles.txt` (or `competitor_descriptions.txt`): ours sits inside the most-viewed competitor copy's measured band for length, sentence rhythm, capitals, numbers, questions and how it opens.
- Then the same strict pairwise test as section 1: ours against the most-viewed competitor's matching piece (their description against ours, their pinned comment against ours, their first 15 seconds of narration against ours), both orders, unlabeled, no story context, judges who did not write it, two model families when you can reach them. Ask "Which one sounds like a real creator you'd keep watching?" and for the one concrete reason. Titles are tested on feed cards (section 2).
- Climb as in section 3. Copy that has not won is not final, and is shown with "has not beaten the competition yet".

## 9. The scoreboard
Every review, card and morning report starts with it, one line per element: the element, our score (wins of both-order pairs, judges, families), the competitor version it was tested against (link and views), and PASS or "has not beaten the competition yet". Elements with no competitor version say "no competitor makes this, not tested".

