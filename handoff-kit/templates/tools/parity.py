#!/usr/bin/env python3
"""Measured parity spec from the person's competitor link(s), and a gate that holds our video to it.

For the agent. Parity means the best performer per dimension, measured, never guessed. Standard library
plus yt-dlp (installed on first use); ffmpeg and ffprobe are used for the picture and sound measures when
present. Every subprocess runs hidden and at low priority.

  python parity.py build URL [URL ...] [--niche "words"] [--peers 6] [--measure 5] [--out research/parity]
      URL = a competitor video or channel (more links welcome). Pulls that channel's recent uploads, finds its
      top performers against its own median, finds niche peers by search and does the same for them, then
      measures the top performers: runtime, title length, description, tags, chapters, upload rhythm, and
      (with --measure N) cuts per minute, loudness and words per minute from the real videos.
      Writes <out>/parity.json, PARITY.md, competitor_titles.txt, competitor_descriptions.txt,
      cards.json (opponent cards for feed_cards.py) and thumb-refs/ (about 16 most-viewed thumbnails).
  python parity.py refresh research/parity [--drop-channel "Name"] [--drop-id VIDEOID]
      Drops off-niche rows, recomputes every band and the cards, and rewrites PARITY.md with the watching
      notes you filled into parity.json. Run it after every edit to parity.json.
  python parity.py check research/parity
      Exit 1 unless the spec is ready: 6+ top performers from 2+ channels, every watching note filled,
      picture and sound measured. Run it before showing the person the plan.
  python parity.py gate research/parity/parity.json [--video ours.mp4] [--title "..."] [--description d.txt]
                        [--transcript t.txt] [--tags "a,b,c"]
      Measures ours and fails (exit 1) on every dimension outside the top performers' band, and on a
      long-form runtime under 8:00. Run it before anything goes to the person for review.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import statistics
import subprocess
import sys
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ytkit  # noqa: E402

STOP = set("the a an and or of to in on for with is are was be this that you your my i we it at by from how why what "
           "who when vs not do does did can will just new video videos shorts short official full part".split())
LONGFORM_MIN_S = 480


def channel_of(link: str) -> tuple[str, dict | None]:
    """(channel url or UC id, the linked video's metadata or None)."""
    if re.search(r"(watch\?v=|youtu\.be/|/shorts/)", link):
        info = ytkit.run_json(["--skip-download", "--no-playlist", link])
        if not info:
            raise SystemExit(f"could not read {link}")
        d = info[0]
        return d.get("channel_id") or d.get("channel_url"), d
    return link.rstrip("/"), None


def top_of(chan: str, shorts: bool, n: int, k: int) -> tuple[list[dict], float | None, int]:
    rows = ytkit.uploads(chan, shorts, n)
    views = [r["view_count"] for r in rows if r.get("view_count")]
    if not views:
        return [], None, 0
    med = float(statistics.median(views))
    for r in rows:
        r["ratio"] = round((r.get("view_count") or 0) / med, 2) if med else 0
        r["channel_median"] = int(med)
        r["median_from"] = len(views)
    rows.sort(key=lambda r: (r["ratio"], r.get("view_count") or 0), reverse=True)
    return rows[:k], med, len(views)


def tab_reach(chan: str) -> dict:
    """Per tab (shorts, longform): median views of recent uploads, uploads per day, and reach = median x per day."""
    out = {}
    for name, sh in (("shorts", True), ("longform", False)):
        rows = ytkit.uploads(chan, sh, 15)
        views = [r["view_count"] for r in rows if r.get("view_count")]
        if len(views) < 3:
            continue
        ends = ytkit.details([rows[0]["id"], rows[-1]["id"]])
        dates = sorted(d.get("upload_date") for d in ends if d.get("upload_date"))
        per_day = None
        if len(dates) == 2:
            d0, d1 = (dt.date(int(x[:4]), int(x[4:6]), int(x[6:])) for x in dates)
            per_day = (len(rows) - 1) / max(1, (d1 - d0).days)
        med = float(statistics.median(views))
        out[name] = {"median": int(med), "uploads_per_day": round(per_day, 3) if per_day else None,
                     "reach": round(med * (per_day or 0))}
    print(f"channel tabs: {out}", file=sys.stderr)
    return out


def band(vals: list[float]) -> dict:
    vals = sorted(v for v in vals if v is not None)
    if not vals:
        return {}
    if len(vals) >= 4:
        q = statistics.quantiles(vals, n=4)
        lo, hi = q[0], q[2]
    else:
        lo, hi = vals[0], vals[-1]
    return {"n": len(vals), "min": vals[0], "p25": round(lo, 2), "median": round(statistics.median(vals), 2),
            "p75": round(hi, 2), "max": vals[-1]}


def _run(cmd, timeout=1800):
    kw = ytkit._popen_kwargs()
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, **kw)


def measure_media(path: Path) -> dict:
    """Runtime, cuts per minute (scene changes) and integrated loudness. Needs ffmpeg/ffprobe."""
    out = {}
    if not (shutil.which("ffprobe") and shutil.which("ffmpeg")):
        return out
    r = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    try:
        out["duration_s"] = round(float(r.stdout.strip()), 1)
    except ValueError:
        return out
    r = _run(["ffmpeg", "-hide_banner", "-nostats", "-hwaccel", "auto", "-i", str(path), "-an",
              "-vf", "scale=160:-2,select='gt(scene,0.3)',showinfo", "-f", "null", "-"])
    cuts = len(re.findall(r"pts_time:", r.stderr))
    r2 = _run(["ffmpeg", "-hide_banner", "-nostats", "-hwaccel", "auto", "-i", str(path), "-an",
               "-vf", "scale=160:-2,select='gt(scene,0.15)',showinfo", "-f", "null", "-"])
    soft = len(re.findall(r"pts_time:", r2.stderr))
    if out["duration_s"]:
        out["cuts_per_min"] = round(cuts / (out["duration_s"] / 60), 1)
        out["soft_cuts_per_min"] = round(soft / (out["duration_s"] / 60), 1)
    r = _run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af", "ebur128", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    if m:
        out["lufs"] = float(m[-1])
    return out


def text_dims(title: str | None, desc: str | None, tags, chapters, duration, transcript: str | None) -> dict:
    d = {}
    if title:
        d["title_chars"] = len(title)
        d["title_words"] = len(title.split())
        d["title_caps_words"] = sum(1 for w in title.split() if len(w) > 1 and w.isupper())
        d["title_has_number"] = int(bool(re.search(r"\d", title)))
    if desc is not None:
        d["desc_chars"] = len(desc)
    if tags is not None:
        d["tags"] = len(tags)
    if chapters is not None:
        d["chapters"] = len(chapters)
    if transcript and duration:
        d["wpm"] = round(len(transcript.split()) / (duration / 60), 1)
    return d


def cmd_build(a):
    out = Path(a.out)
    (out / "thumb-refs").mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    seeds, linked = [], []
    for link in a.links:
        chan, info = channel_of(link)
        seeds.append(chan)
        if info:
            linked.append(info)
    # format: --format wins; else a linked video's own format; else the channel tab with more reach
    # (median views x uploads per day), because views per video alone hides a daily Shorts habit
    tabs = tab_reach(seeds[0]) if not linked or a.format == "auto" else {}
    mix = False
    if a.format != "auto":
        shorts = a.format == "shorts"
    elif linked:
        shorts = sum(ytkit.is_short(x) for x in linked) * 2 >= len(linked)
    else:
        rs, rl = tabs.get("shorts", {}).get("reach", 0), tabs.get("longform", {}).get("reach", 0)
        shorts = rs >= rl
        mix = min(rs, rl) >= 0.25 * max(rs, rl) > 0
    fmt = "shorts" if shorts else "longform"
    other = "longform" if shorts else "shorts"
    print(f"format: {fmt}" + (f" (the channel is a mix: run again with --format {other} --out <dir>-{other})" if mix else ""), file=sys.stderr)
    pool: dict[str, dict] = {}
    chan_stats = {}
    for chan in dict.fromkeys(seeds):
        rows, med, n = top_of(chan, shorts, a.uploads, a.per_channel)
        chan_stats[chan] = (med, n)
        for r in rows:
            pool.setdefault(r["id"], {**r, "from": "linked channel"})
    # niche words: given, or the most common title words of the linked channel's top performers
    words = a.niche
    if not words:
        c = Counter(w for r in pool.values() for w in re.findall(r"[a-z][a-z']+", (r.get("title") or "").lower()) if w not in STOP)
        words = " ".join(w for w, _ in c.most_common(3))
    print(f"niche search: {words!r}", file=sys.stderr)
    found = ytkit.search(words + (" shorts" if shorts else ""), 40) + ytkit.search(words, 40)
    seen_ids = {str(s) for s in seeds}
    peers = []
    for r in sorted(found, key=lambda r: r.get("view_count") or 0, reverse=True):
        cid = r.get("channel_id")
        if cid and cid not in seen_ids and cid not in peers:
            peers.append(cid)
        if len(peers) >= a.peers:
            break
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda c: (c, top_of(c, shorts, a.uploads, a.per_channel)), peers))
    for c, (rows, med, n) in res:
        chan_stats[c] = (med, n)
        if n < 10:
            continue  # a median from under 10 uploads is a hint, not proof
        for r in rows:
            pool.setdefault(r["id"], {**r, "from": "niche peer"})
    # keep real outliers with scale: ratio >= 2 against their own channel
    top = [r for r in pool.values() if r.get("ratio", 0) >= a.min_ratio]
    top.sort(key=lambda r: (r.get("view_count") or 0), reverse=True)
    top = top[: a.top]
    info = {d["id"]: d for d in ytkit.details([r["id"] for r in top])}
    perf = []
    for r in top:
        d = info.get(r["id"])
        if not d:
            continue
        perf.append({"id": r["id"], "url": d.get("webpage_url"), "title": d.get("title"), "channel": d.get("channel"),
                     "views": d.get("view_count"), "upload_date": ytkit.fmt_date(d.get("upload_date")),
                     "channel_median": r["channel_median"], "median_from": r["median_from"],
                     "ratio": round((d.get("view_count") or 0) / r["channel_median"], 2) if r["channel_median"] else r["ratio"],
                     "from": r["from"], "duration_s": d.get("duration"), "description": d.get("description") or "",
                     "tags": d.get("tags") or [], "chapters": d.get("chapters") or [],
                     "thumbnail": d.get("thumbnail"), "on_niche": None, "on_niche_why": ""})
    # real picture and sound measures on the best few
    if a.measure and perf:
        cdir = out / "clips"
        cdir.mkdir(exist_ok=True)

        def meas(p):
            tx, how = ytkit.transcript(p["id"], out / "transcripts")
            if tx:
                (out / "transcripts" / f"{p['id']}.txt").write_text(tx, encoding="utf-8")
            dst = cdir / f"{p['id']}.mp4"
            if not dst.exists():
                sect = [] if shorts else ["--download-sections", "*0-360"]  # long-form: the first 6 minutes are enough
                _run(ytkit.ytdlp() + ["--no-warnings", "-f", ytkit.SMALL_VIDEO, "--merge-output-format", "mp4", *sect,
                                      "-o", str(dst), p["url"]], timeout=3600)
            m = measure_media(dst) if dst.exists() else {}
            return p["id"], m, tx, how

        with ThreadPoolExecutor(2) as ex:
            for vid, m, tx, how in ex.map(meas, perf[: a.measure]):
                p = next(x for x in perf if x["id"] == vid)
                p["media"] = m
                p["transcript_method"] = how
                if tx and p.get("duration_s"):
                    p["wpm"] = round(len(tx.split()) / (p["duration_s"] / 60), 1)
    spec = {"observed": today, "format": fmt, "mix": mix, "mix_other_format": other if mix else None,
            "channel_tabs": tabs, "links": a.links, "niche_words": words, "min_ratio": a.min_ratio,
            "channels": {str(c): {"median": int(m) if m else None, "median_from": n} for c, (m, n) in chan_stats.items()},
            "rules": {"longform_min_s": LONGFORM_MIN_S if fmt == "longform" else None, "shorts_max_s": 180 if fmt == "shorts" else None},
            "to_fill_by_watching": {k: "" for k in FILL_KEYS},
            "top_performers": perf}
    for q in perf[:16]:
        dst = out / "thumb-refs" / f"{q['id']}.jpg"
        if not dst.exists():
            for name in ("maxresdefault", "hqdefault"):
                try:
                    with urllib.request.urlopen(f"https://i.ytimg.com/vi/{q['id']}/{name}.jpg", timeout=30) as resp:
                        dst.write_bytes(resp.read())
                    break
                except Exception:
                    continue
    write_outputs(spec, out)
    print(f"wrote {out}/parity.json, PARITY.md, cards.json, thumb-refs/ ({len(perf)} top performers)", file=sys.stderr)
    print("NEXT: in parity.json set on_niche true/false (+ on_niche_why) on EVERY top performer, fill to_fill_by_watching, "
          "then `parity.py refresh <dir>` (drops the false rows, recomputes) and `parity.py check <dir>`.", file=sys.stderr)
    if len(perf) < 6:
        print("WARNING: under 6 top performers. Add more links, --niche words, --peers 10 or --min-ratio 1.5.", file=sys.stderr)


FILL_KEYS = ["style", "voice", "pacing", "hook_pattern", "visual_grammar", "music", "captions"]
DIM_KEYS = ["duration_s", "title_chars", "title_words", "title_caps_words", "title_has_number", "desc_chars", "tags",
            "chapters", "cuts_per_min", "soft_cuts_per_min", "lufs", "wpm"]


def perf_dims(p: dict) -> dict:
    x = text_dims(p.get("title"), p.get("description", ""), p.get("tags") or [], p.get("chapters") or [], None, None)
    x["duration_s"] = p.get("duration_s")
    x.update({k: v for k, v in (p.get("media") or {}).items() if k != "duration_s"})
    x["wpm"] = p.get("wpm")
    return {k: v for k, v in x.items() if v is not None}


def write_outputs(spec: dict, out: Path):
    """(Re)compute bands and best performers from spec["top_performers"]; write every output file."""
    perf = spec["top_performers"]
    per = [perf_dims(q) for q in perf]
    dims = {k: band([x.get(k) for x in per]) for k in DIM_KEYS}
    dims = {k: v for k, v in dims.items() if v}
    best = {}
    for key in dims:  # the single most-viewed top performer that has this measure
        src = [(x[key], q) for x, q in zip(per, perf) if key in x]
        if src:
            v, q = max(src, key=lambda t: t[1]["views"] or 0)
            best[key] = {"value": v, "video": q["url"], "views": q["views"]}
    spec["dimensions"] = dims
    spec["best_performer_per_dimension"] = best
    (out / "parity.json").write_text(json.dumps(spec, indent=1), encoding="utf-8")
    (out / "competitor_titles.txt").write_text("\n".join(q["title"] for q in perf) + "\n", encoding="utf-8")
    (out / "competitor_descriptions.txt").write_text("\n\n=====\n\n".join(q.get("description", "") for q in perf) + "\n", encoding="utf-8")
    cards = [{"id": f"comp-{i}", "side": "comp", "title": q["title"], "thumb": f"thumb-refs/{q['id']}.jpg",
              "channel": q["channel"], "views": _short(q["views"]), "views_n": q["views"],
              "age": q["upload_date"], "url": q["url"]} for i, q in enumerate(perf[:10], 1)]
    (out / "cards.json").write_text(json.dumps(cards, indent=1), encoding="utf-8")
    fmt, tabs = spec["format"], spec.get("channel_tabs") or {}
    other = spec.get("mix_other_format")
    md = [f"# Parity spec ({fmt}), measured {spec['observed']}", ""]
    if spec.get("mix"):
        md += [f"The linked channel is a MIX: {other} also earns at least a quarter of its reach ({tabs}). Build the {other} spec too "
               f"(`parity.py build ... --format {other} --out <this dir>-{other}`) and plan both formats, {fmt} first.", ""]
    elif tabs:
        md += [f"Channel tabs (median views, uploads per day, reach): {tabs}", ""]
    md += [f"From: {', '.join(spec['links'])}. Niche words: {spec['niche_words']!r}. {len(perf)} top performers "
           f"(ratio {spec.get('min_ratio', 2.0)}x+ against their own channel median).", ""]
    if spec.get("dropped"):
        md += [f"Dropped as off-niche: {', '.join(spec['dropped'])}.", ""]
    md += ["## What the top performers look and sound like (watched)", ""]
    for k in FILL_KEYS:
        md.append(f"- **{k}:** {spec.get('to_fill_by_watching', {}).get(k) or 'NOT FILLED YET'}")
    md += ["", "## Bands to hit (top performers; the gate fails anything outside p25 to p75)", "",
           "| dimension | p25 | median | p75 | best performer's value (views) |", "|---|---|---|---|---|"]
    for k, v in dims.items():
        b = best.get(k, {})
        md.append(f"| {k} | {v['p25']} | {v['median']} | {v['p75']} | {b.get('value')} ({b.get('views')}) |")
    md += ["", "cuts_per_min counts hard cuts (scene score above 0.3); soft_cuts_per_min also counts big camera moves and "
           "transitions (above 0.15). Smooth animation can show 0 hard cuts: then pace against soft cuts.", "",
           "## Top performers", "", "| views | ratio | median (uploads) | date | channel | title | link |", "|---|---|---|---|---|---|---|"]
    for q in perf:
        md.append(f"| {q['views']:,} | {q['ratio']} | {q['channel_median']} ({q['median_from']}) | {q['upload_date']} | {q['channel']} | "
                  f"{(q['title'] or '').replace('|', '/')} | {q['url']} |")
    (out / "PARITY.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def problems_of(spec: dict) -> list[str]:
    probs = []
    perf = spec.get("top_performers", [])
    if len(perf) < 6:
        probs.append(f"only {len(perf)} top performers (need 6 on-niche)")
    unreviewed = [q["id"] for q in perf if q.get("on_niche") is None]
    if unreviewed:
        probs.append(f"{len(unreviewed)} top performers not reviewed: set \"on_niche\" to true or false and \"on_niche_why\" "
                     "(same kind of video as the person's target? news, macro commentary, ads, off-topic = false) in parity.json, "
                     "then run refresh")
    whys = [(q.get("on_niche_why") or "").strip().lower() for q in perf if q.get("on_niche") is not None]
    if whys and (len(set(whys)) < max(2, len(whys) // 2) or min(len(w) for w in whys) < 15):
        probs.append("on_niche reasons look like one blanket rule: judge each video by its own title and say why in its own words "
                     "(what it promises the viewer, and whether that is the person's kind of video)")
    if len({q["channel"] for q in perf}) < 2:
        probs.append("top performers come from a single channel (need at least 2)")
    fill = spec.get("to_fill_by_watching", {})
    empty = [k for k in FILL_KEYS if len((fill.get(k) or "").strip()) < 12 or (fill.get(k) or "").startswith("edit-only / 2d")]
    if empty:
        probs.append("watching notes missing or placeholder: " + ", ".join(empty))
    if not any((q.get("media") or {}) for q in perf):
        probs.append("no picture and sound measures (run build with --measure 3, ffmpeg needed)")
    return probs


def cmd_refresh(a):
    out = Path(a.dir)
    spec = json.loads((out / "parity.json").read_text(encoding="utf-8"))
    drop_c = {c.lower() for c in a.drop_channel or []}
    drop_i = set(a.drop_id or [])
    keep, gone = [], []
    for q in spec["top_performers"]:
        if (q.get("channel") or "").lower() in drop_c or q["id"] in drop_i or q.get("on_niche") is False:
            gone.append(f"{q.get('channel')}: {q.get('title')}")
        else:
            keep.append(q)
    spec["top_performers"] = keep
    if gone:
        spec["dropped"] = sorted(set(spec.get("dropped", [])) | set(gone))
    write_outputs(spec, out)
    print(f"dropped {len(gone)}, {len(keep)} top performers remain; bands, cards and PARITY.md rewritten", file=sys.stderr)
    for p_ in problems_of(spec):
        print("PROBLEM: " + p_, file=sys.stderr)


def cmd_check(a):
    spec = json.loads((Path(a.dir) / "parity.json").read_text(encoding="utf-8"))
    probs = problems_of(spec)
    for p_ in probs:
        print("PROBLEM: " + p_)
    print("parity spec ready" if not probs else f"{len(probs)} problem(s): fix them before showing the plan")
    sys.exit(1 if probs else 0)


def _short(n):
    n = n or 0
    return f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.0f}K" if n >= 1e3 else str(n)


def cmd_gate(a):
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    dims = spec["dimensions"]
    ours = {}
    if a.video:
        ours.update(measure_media(Path(a.video)))
    desc = Path(a.description).read_text(encoding="utf-8") if a.description else None
    tx = Path(a.transcript).read_text(encoding="utf-8") if a.transcript else None
    tags = [t for t in (a.tags or "").split(",") if t.strip()] if a.tags is not None else None
    ours.update(text_dims(a.title, desc, tags, None, ours.get("duration_s"), tx))
    rows, bad = [], 0
    for k, v in ours.items():
        b = dims.get(k)
        if not b:
            rows.append((k, v, "-", "no competitor data"))
            continue
        ok = b["p25"] <= v <= b["p75"]
        bad += not ok
        rows.append((k, v, f"{b['p25']} to {b['p75']}", "PASS" if ok else "FAIL"))
    r = spec.get("rules", {})
    if r.get("longform_min_s") and "duration_s" in ours and ours["duration_s"] < r["longform_min_s"]:
        rows.append(("longform runtime", ours["duration_s"], ">= 480 s", "FAIL (mid-rolls need 8:00+)"))
        bad += 1
    if r.get("shorts_max_s") and "duration_s" in ours and ours["duration_s"] > r["shorts_max_s"]:
        rows.append(("shorts runtime", ours["duration_s"], "<= 180 s", "FAIL"))
        bad += 1
    print(f"{'dimension':18} {'ours':>10}  {'band':>16}  result")
    for k, v, bnd, res in rows:
        print(f"{k:18} {v!s:>10}  {bnd:>16}  {res}")
    print(f"\n{bad} failing dimension(s). Fix the generator that made them, then re-run.")
    sys.exit(1 if bad else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("links", nargs="+")
    b.add_argument("--niche")
    b.add_argument("--format", choices=["auto", "shorts", "longform"], default="auto")
    b.add_argument("--peers", type=int, default=6)
    b.add_argument("--uploads", type=int, default=40)
    b.add_argument("--per-channel", type=int, default=8)
    b.add_argument("--min-ratio", type=float, default=2.0)
    b.add_argument("--top", type=int, default=24)
    b.add_argument("--measure", type=int, default=0, help="download and measure the N most-viewed top performers")
    b.add_argument("--out", default="research/parity")
    b.set_defaults(fn=cmd_build)
    r = sub.add_parser("refresh", help="drop off-niche rows, recompute bands, rewrite PARITY.md with the watching notes")
    r.add_argument("dir")
    r.add_argument("--drop-channel", action="append")
    r.add_argument("--drop-id", action="append")
    r.set_defaults(fn=cmd_refresh)
    c = sub.add_parser("check", help="exit 1 unless the spec is ready: 6+ on-niche top performers, 2+ channels, notes filled, media measured")
    c.add_argument("dir")
    c.set_defaults(fn=cmd_check)
    g = sub.add_parser("gate")
    g.add_argument("spec")
    g.add_argument("--video")
    g.add_argument("--title")
    g.add_argument("--description")
    g.add_argument("--transcript")
    g.add_argument("--tags")
    g.set_defaults(fn=cmd_gate)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
