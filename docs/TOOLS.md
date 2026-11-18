**For the agent. Never send the user here; run these yourself.**

# Local tools

`launchkit` is standard-library Python. Start a private working project with `python -m launchkit init my-channel` (or `channels/<slug>/` when the setup wizard builds one). Live YouTube numbers come from `handoff-kit/templates/tools/yt_feed.py` (search channels, pull newest uploads with views and the ratio to the channel median; no key or login). Blind click tests use `handoff-kit/templates/tools/feed_cards.py`; platform copy is checked with `handoff-kit/templates/tools/copy_check.py`.

## Run the example (synthetic data)

The examples are invented, not real channels or results:

```sh
python -m launchkit validate examples/videos.csv
python -m launchkit rank examples/videos.csv --out work/ranking.csv
python -m launchkit overlap examples/videos.csv "What if the moon became a museum?" --out work/overlap.csv
python -m unittest discover -s tests -v
```

Copy the CSV schema into your project and fill it with your own observed video data. `rank` compares each video to other videos on the same channel, using age-matched peers when there are enough. `overlap` finds shared title words; it cannot judge conceptual originality or clear rights. See [method and limitations](docs/RESEARCH.md).

If you already have individual local video metadata JSON files, `python -m launchkit import-json reference1.json reference2.json --observed YYYY-MM-DD --out my-channel/videos.csv` converts compatible yt-dlp-style fields. It does not fetch videos, authenticate, or infer missing values; make sure the date matches when you collected the view counts.

## What's in here

- `launchkit/`: project scaffolding, CSV validation, within-channel comparisons and title-overlap leads.
- `templates/project/`: a blank brief, reference list, study plan, concept slate, production plan, rights notes and review checklist.
- `docs/`: the full workflow, practical prompts, evidence methods, [pilot production](docs/PRODUCTION.md) and release checks.
- `examples/`: synthetic data for testing the tools.
- `AGENTS.md`: operating instructions for coding agents. Adapt them to your own preferences.

Keep `my-channel/` private if it contains your research, analytics, credentials, or unreleased work. The example `.gitignore` excludes common secrets and media, but it is not a substitute for reviewing every file before sharing. No one is granted access by this toolkit.

For a local cut, `python -m launchkit probe path/to/video.mp4 --out work/probe.json` uses a separately installed `ffprobe` to report streams, dimensions and duration. It does not inspect the story or listen to audio; those reviews remain incomplete until someone actually performs them.
