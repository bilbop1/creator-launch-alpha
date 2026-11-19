#!/usr/bin/env python3
"""State-of-the-art research: how people are making this kind of video with Claude and agents right now.

For the agent. Run it at the start of every install, before building, and again when the person starts a
new format or when `due` says the research is stale. Standard library plus yt-dlp (installed on first use).

  python methods.py scan --formats shorts,longform --styles edit,2d,3d [--query "extra words"] [--days 90] [--out research/methods]
      Searches YouTube (relevance, this month, this year, most viewed this month) for recent videos about making videos with Claude,
      Claude Code, agents and AI, for the person's case. Keeps videos from the last --days, measures each
      against its uploader's own baseline (median views of their recent uploads) and writes
      <out>/videos.csv and <out>/top.md ranked by that ratio. "Viral" = high views against the uploader's own
      median, recent, and many videos, never 2 or 3.
  python methods.py transcripts [--top 25 | --ids ID ID ...] [--out research/methods]
      Pulls transcripts of the top videos into <out>/transcripts/<id>.txt (subtitles, then a transcript
      library, then local Whisper as the fallback) and records the method used per video.
  python methods.py skeleton [--out research/methods] [--file METHODS.md]
      Writes the METHODS.md skeleton with every source cited (URL, views, date, ratio). You then watch or
      read the transcripts and fill in the techniques, separating PROVEN (shown working on screen with a
      result) from CLAIMED (said, not shown).
  python methods.py check METHODS.md
      Exit 1 unless at least 10 sources are marked "read: in full" and "fits this case: yes" and the
      proven-techniques and pipeline sections are filled. Run it before showing the person the plan.
  python methods.py due METHODS.md [--days 30] [--format shorts]
      Exit 0 if the research is fresh and covers that format, 1 if it must be refreshed.

Formats: shorts, reels, longform. Styles: edit (editing real footage), 2d, 3d. Any mix is fine.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ytkit  # noqa: E402

BASE = [
    "claude code video editing", "claude code youtube automation", "claude code video", "claude ai video editing",
    "ai agent video editing", "agentic video editing", "ai agents make youtube videos", "claude code faceless youtube",
    "automate youtube channel with ai agents", "claude code remotion", "claude skills video", "codex video editing",
]
BY_FORMAT = {
    "shorts": ["claude code youtube shorts", "ai youtube shorts automation", "ai shorts editing agent", "faceless shorts ai",
               "make viral shorts with claude", "ai animated shorts workflow", "claude shorts full workflow"],
    "reels": ["ai instagram reels editing", "claude reels automation"],
    "longform": ["claude code long form youtube video", "ai documentary youtube channel", "ai long form video editing",
                 "faceless youtube long form ai", "claude code edit full youtube video", "ai edit 20 minute youtube video"],
}
BY_STYLE = {
    "edit": ["claude code edit talking head", "ai edit my raw footage", "ai video editor agent", "claude code premiere davinci",
             "auto edit podcast clips ai", "claude code cut silences and retakes", "ai edit talking head youtube video",
             "claude code b-roll captions edit", "automate youtube editing with claude code"],
    "2d": ["claude code motion graphics", "ai 2d animation youtube", "claude code animated explainer", "hyperframes video",
           "ai whiteboard animation channel"],
    "3d": ["claude code blender", "ai 3d animation youtube", "claude code three.js video", "ai 3d explainer video",
           "claude 3d animated shorts", "ai 3d animation shorts tutorial", "blender mcp claude animation",
           "make 3d animations with claude", "ai 3d story shorts"],
}
FIELDS = ["video_id", "url", "title", "channel", "channel_id", "views", "upload_date", "duration_s", "is_short",
          "channel_median", "median_from", "ratio", "query", "observed"]


def cmd_scan(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    queries = list(BASE)
    for f in [x.strip().lower() for x in a.formats.split(",") if x.strip()]:
        queries += BY_FORMAT.get(f, [])
    for s in [x.strip().lower() for x in a.styles.split(",") if x.strip()]:
        queries += BY_STYLE.get(s, [])
    queries += a.query or []
    cands: dict[str, dict] = {}

    def one(q_when):
        q, when = q_when
        return q, ytkit.search(q, a.per_query, when)

    when = ["", "month", "views_month"] if a.days <= 45 else ["", "month", "year", "views_month"]
    with ThreadPoolExecutor(4) as ex:
        for q, rows in ex.map(one, [(q, w) for q in queries for w in when]):
            for r in rows:
                v = r.get("view_count")
                if r.get("id") and (v is None or v >= a.min_views):
                    cands.setdefault(r["id"], {**r, "query": q})
    # on topic only: the title must name an AI tool or agent AND a video-making word
    ai = re.compile(r"\b(claude|codex|agent|agents|agentic|ai|a\.i\.|gpt|chatgpt|opus|sonnet|llm|automat\w*|remotion|hyperframes)\b", re.I)
    vid = re.compile(r"\b(edit\w*|video\w*|shorts?|reels?|animat\w*|motion|youtube|channel|faceless|content|render\w*|blender|3d|2d|clips?|tiktok)\b", re.I)
    cands = {k: r for k, r in cands.items() if ai.search(r.get("title") or "") and vid.search(r.get("title") or "")}
    print(f"{len(queries)} searches, {len(cands)} on-topic candidates with {a.min_views}+ views", file=sys.stderr)
    ranked = sorted(cands.values(), key=lambda r: r.get("view_count") or 0, reverse=True)[: a.cap]
    info = {d["id"]: d for d in ytkit.details([r["id"] for r in ranked])}
    cutoff = (dt.date.today() - dt.timedelta(days=a.days)).strftime("%Y%m%d")
    recent = [r for r in ranked if (info.get(r["id"], {}).get("upload_date") or "0") >= cutoff]
    print(f"{len(recent)} from the last {a.days} days", file=sys.stderr)
    chans = {(info[r["id"]].get("channel_id") or r.get("channel_id"), ytkit.is_short(info[r["id"]])) for r in recent}
    with ThreadPoolExecutor(4) as ex:
        base = dict(zip(chans, ex.map(lambda c: ytkit.baseline(c[0], c[1]) if c[0] else (None, 0), chans)))
    today = dt.date.today().isoformat()
    rows = []
    for r in recent:
        d = info[r["id"]]
        key = (d.get("channel_id") or r.get("channel_id"), ytkit.is_short(d))
        med, n = base.get(key, (None, 0))
        views = d.get("view_count") or r.get("view_count") or 0
        rows.append({"video_id": r["id"], "url": d.get("webpage_url") or "https://www.youtube.com/watch?v=" + r["id"],
                     "title": d.get("title") or r.get("title"), "channel": d.get("channel") or r.get("channel"),
                     "channel_id": key[0], "views": views, "upload_date": ytkit.fmt_date(d.get("upload_date")),
                     "duration_s": d.get("duration"), "is_short": key[1], "channel_median": int(med) if med else "",
                     "median_from": n, "ratio": round(views / med, 2) if med else "", "query": r["query"], "observed": today})
    # a baseline from under 10 uploads is a hint only: rank those after the measured ones
    rows.sort(key=lambda x: ((x["median_from"] or 0) >= 10, x["ratio"] or 0, x["views"]), reverse=True)
    with open(out / "videos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    lines = [f"# Recent videos about making videos with Claude and agents (seen {today}, last {a.days} days)", "",
             "Ranked by views over the uploader's own median. A median from under 10 uploads is a hint only.", "",
             "| # | ratio | views | date | channel (median, uploads) | title | link |", "|---|---|---|---|---|---|---|"]
    for i, x in enumerate(rows[: a.top], 1):
        lines.append(f"| {i} | {x['ratio']} | {x['views']:,} | {x['upload_date']} | {x['channel']} ({x['channel_median']}, {x['median_from']}) "
                     f"| {str(x['title']).replace('|', '/')} | {x['url']} |")
    (out / "top.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out / 'videos.csv'} ({len(rows)} videos) and {out / 'top.md'}", file=sys.stderr)
    if len(rows) < 15:
        print("WARNING: fewer than 15 recent videos. Add --query phrasings for the person's case or widen --days.", file=sys.stderr)


def _rows(out: Path) -> list[dict]:
    p = out / "videos.csv"
    if not p.exists():
        sys.exit(f"run scan first ({p} missing)")
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cmd_transcripts(a):
    out = Path(a.out)
    tdir = out / "transcripts"
    rows = _rows(out)
    rows = [r for r in rows if r["video_id"] in set(a.ids)] if a.ids else rows[: a.top]
    log = []

    def one(r):
        dst = tdir / f"{r['video_id']}.txt"
        if dst.exists() and dst.stat().st_size > 200:
            return r, "cached"
        text, how = ytkit.transcript(r["video_id"], tdir)
        if text:
            dst.write_text(f"{r['title']}\n{r['url']}\n\n{text}\n", encoding="utf-8")
        return r, how

    with ThreadPoolExecutor(3) as ex:
        for r, how in ex.map(one, rows):
            log.append(f"{r['video_id']}\t{how}\t{r['title']}")
            print(f"{r['video_id']}: {how}", file=sys.stderr)
    (out / "transcripts.log").write_text("\n".join(log) + "\n", encoding="utf-8")
    got = sum(1 for x in log if not x.split("\t")[1].startswith("none"))
    print(f"{got} of {len(rows)} transcripts in {tdir}", file=sys.stderr)


def cmd_skeleton(a):
    out = Path(a.out)
    rows = _rows(out)[: a.top]
    today = dt.date.today().isoformat()
    src = "\n".join(f"- S{i}: {r['title']} | {r['channel']} | {int(float(r['views'])):,} views | {r['upload_date']} | "
                    f"ratio {r['ratio']} vs its own median | {r['url']} | read: <in full / title only> | fits this case: <yes / no>"
                    for i, r in enumerate(rows, 1))
    body = f"""# How this kind of video is made with Claude and agents right now

Researched: {today}. Formats covered: <shorts / reels / longform>. Styles covered: <edit / 2d / 3d>.
Refresh when: the person starts a new format, or 30 days after the date above.
Raw data: research/methods/ (videos.csv, top.md, transcripts/) in this channel folder.

## Sources (cite as S1, S2 ...)
At least 10 must be `read: in full` and `fits this case: yes` before this research counts as done. "Fits" depends on the input. If the person gave footage: any source showing an agent (Claude, Codex or similar) editing real recorded footage (talking head, podcast, vlog, screen recording) into a finished video fits. If they gave nothing: any source showing agents generating finished videos in the same visual family (3D, 2D or motion graphics) fits. Matching the output length (Shorts or long-form) is a plus, not a requirement. A product ad, or a source for the other input type, never fits.
{src}

## Proven techniques (shown working on screen, with a visible result)
- <technique>: <what exactly they do, tools, prompt or command shown>. Sources: S?, S?.

## Claimed only (said, not shown; treat as untested)
- <claim>. Source: S?.

## Tools and pipelines seen (with what each is for)
- <tool or pipeline>: <use>. Sources: S?.

## Prompts worth copying (word for word where shown)
- "<prompt>" (S?)

## Our pipeline for this channel, and why
- <stage>: <choice>, because <which proven source and what it beat>.

## Gaps: what no source shows for this exact case, and how we test it first
- <gap>: <the small test we run before relying on it>.
"""
    dst = Path(a.file)
    if dst.exists() and not a.force:
        sys.exit(f"{dst} exists; pass --force to overwrite")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(body, encoding="utf-8")
    print(f"wrote {dst}", file=sys.stderr)


def cmd_check(a):
    p = Path(a.file)
    if not p.exists():
        sys.exit("check: no methods file yet")
    t = p.read_text(encoding="utf-8")
    src = [l for l in t.splitlines() if re.match(r"- S\d+:", l)]
    full_fit = [l for l in src if re.search(r"read: *in full", l, re.I) and re.search(r"fits this case: *yes", l, re.I)]
    probs = []
    if len(full_fit) < a.need:
        probs.append(f"{len(full_fit)} sources are read in full AND fit this case (need {a.need}); read more, or scan again with --query for this exact case")
    unmarked = [l.split(":")[0] for l in src if "<in full" in l or "<yes" in l]
    if unmarked:
        probs.append("sources still unmarked: " + " ".join(s_[2:] for s_ in unmarked[:12]))
    for k in ("Formats covered:", "Styles covered:"):
        m = re.search(k + r" *(.*)", t)
        if not m or "<" in m.group(1):
            probs.append(f"'{k}' line not filled")
    for sec in ("## Proven techniques", "## Our pipeline for this channel", "## Gaps"):
        body = t.split(sec, 1)[1].split("\n## ", 1)[0] if sec in t else ""
        if not body.strip() or "<technique>" in body or "<stage>" in body or "<gap>" in body:
            probs.append(f"section '{sec[3:]}' not filled")
    for x in probs:
        print("PROBLEM: " + x)
    print("methods research ready" if not probs else f"{len(probs)} problem(s)")
    sys.exit(1 if probs else 0)


def cmd_due(a):
    p = Path(a.file)
    if not p.exists():
        print("due: no methods file yet")
        sys.exit(1)
    t = p.read_text(encoding="utf-8")
    m = re.search(r"Researched: (\d{4}-\d{2}-\d{2})", t)
    if not m:
        print("due: no research date")
        sys.exit(1)
    age = (dt.date.today() - dt.date.fromisoformat(m.group(1))).days
    covered = re.search(r"Formats covered: (.*)", t)
    if a.format and covered and a.format.lower() not in covered.group(1).lower():
        print(f"due: {a.format} not covered yet")
        sys.exit(1)
    if age > a.days:
        print(f"due: {age} days old (refresh every {a.days})")
        sys.exit(1)
    print(f"fresh: {age} days old")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--formats", default="shorts,longform")
    s.add_argument("--styles", default="edit,2d,3d")
    s.add_argument("--query", action="append")
    s.add_argument("--days", type=int, default=90)
    s.add_argument("--per-query", type=int, default=20)
    s.add_argument("--min-views", type=int, default=5000)
    s.add_argument("--cap", type=int, default=150, help="most candidates to fetch full details for")
    s.add_argument("--top", type=int, default=40)
    s.add_argument("--out", default="research/methods")
    s.set_defaults(fn=cmd_scan)
    t = sub.add_parser("transcripts")
    t.add_argument("--top", type=int, default=25)
    t.add_argument("--ids", nargs="*", help="pull these video ids (from videos.csv) instead of the top N")
    t.add_argument("--out", default="research/methods")
    t.set_defaults(fn=cmd_transcripts)
    k = sub.add_parser("skeleton")
    k.add_argument("--top", type=int, default=25)
    k.add_argument("--out", default="research/methods")
    k.add_argument("--file", default="METHODS.md")
    k.add_argument("--force", action="store_true")
    k.set_defaults(fn=cmd_skeleton)
    c = sub.add_parser("check", help="exit 1 unless 10+ sources are read in full and fit this case, and the sections are filled")
    c.add_argument("file")
    c.add_argument("--need", type=int, default=10)
    c.set_defaults(fn=cmd_check)
    d = sub.add_parser("due")
    d.add_argument("file")
    d.add_argument("--days", type=int, default=30)
    d.add_argument("--format")
    d.set_defaults(fn=cmd_due)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
