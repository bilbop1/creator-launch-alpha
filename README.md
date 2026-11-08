# Creator Launch Alpha

A free, early-stage toolkit for using YouTube references to research a channel, develop original videos, and make a launch plan with an AI agent. Bring a few links or a direction; the agent helps find more, inspect what works, and turn the findings into a production process you can actually use.

This is an **alpha**, shared as-is with friends. It contains workflows and small local analysis tools. It does not include a finished channel, production assets, automated publishing, a guaranteed growth formula, or a promise of support.

## Start here

1. Install Python 3.10 or newer. No packages or account credentials are required for the built-in tools.
2. In a terminal opened in this folder, create a private working project:

   ```sh
   python -m launchkit init my-channel
   ```

3. Open this folder with your agent and say:

   > Help me build a channel from these references: [paste URLs]. Ask only for decisions you need. Research related channels and videos, compare hits and misses, and propose original directions. Put the evidence and next actions in `my-channel/`.

4. Follow [the field guide](docs/FIELD-GUIDE.md). Use [agent prompts](docs/AGENT-PROMPTS.md) for specific stages and [the research method](docs/RESEARCH.md) when comparing results.

If you don't have references yet, tell the agent an audience, interest, or format. It can find candidates using the research tools available in your own environment. This repository does not fetch YouTube data by itself.

## Run the example

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
