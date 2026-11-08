# Research without fooling yourself

## Collect

Create `videos.csv` with the header in `examples/videos.csv`. Each row is one video at one observation date. Use a stable channel ID or consistent handle in `channel`, and record views as observed on `observed`, not a later estimate. Use ISO dates (`YYYY-MM-DD`), seconds for duration, and source URLs. The validator rejects missing values, duplicate IDs, impossible dates and negative views. Put unknown entries in `references.md`; do not fill them with zero.

Find candidates using a browser or other tools the creator explicitly permits. Respect access restrictions and platform terms. Record selection criteria, search terms, caps, incomplete listings and exclusions. Published views are snapshots, not retention, watch time, earnings or a forecast. If download, transcript or private analytics access fails, keep the missing value and explain the blocker.

## Compare

`python -m launchkit rank my-channel/videos.csv --out my-channel/ranking.csv`

For each video, the tool takes the median of log10 views for **other videos on the same channel**. It uses peers within 0.20 log10(age+1) if at least eight exist; otherwise up to 12 nearest-age peers if there are at least eight. With 2–7 peers it labels the fallback `small-channel-median`; fewer than two gives `insufficient`. View counts of zero use one for the log calculation. `residual_log10` is uncapped; `breakout_ratio` is 10 to that power. Results are descriptive, sensitive to sample selection, snapshot dates, format, and age; they do not estimate causal effects. A channel with one video cannot supply its own baseline.

Collect comparable channel snapshots together where possible. A row observed on a different day is not adjusted for later view growth. Keep video formats separate in the input rather than combining dissimilar Shorts and long-form uploads. Imported JSON must contain each video's stable channel ID, video ID, title, public page URL, views, date and duration; the import fails on missing values instead of guessing.

Observe both winners and ordinary/weak videos. A promising pattern is a hypothesis: state feature, comparison, direction, estimated size and uncertainty, along with alternate explanations. For consequential studies plan channels, selection, sample, outcome, tests and stop conditions before collecting decisive data. If you have sufficient data and statistical expertise, block permutations by channel, correct multiple comparisons, report intervals and replicate on held-out channels or time periods. The simple CLI does not perform those tests; ask the agent to implement and validate them for the specific dataset rather than inventing p-values.

## Originality check

`python -m launchkit overlap my-channel/videos.csv "Your candidate title" --out my-channel/overlap.csv`

The tool reports shared content words, the share of candidate words present in a reference, and Jaccard overlap. It does not compare images, scripts, meaning, characters, sequence, or legal rights. Reworded copies can score low; unrelated ideas can score high. Inspect the closest results and check the premise, execution and intended assets manually. An empty or unrelated corpus cannot clear an idea.

## What a good decision record contains

- Question and choice being made; selection criteria and date.
- Sources, videos, observation dates, sample sizes and missing fields.
- Results per channel and their variability; effect direction and uncertainty.
- Competing explanations and what would change the conclusion.
- Decision: proceed, test with a clear kill rule, or collect more evidence.

Any measurement may be PASS, FAIL or INCOMPLETE. An incomplete visual, audio or rights check is not a pass; a statistical association is not a guarantee of performance.
