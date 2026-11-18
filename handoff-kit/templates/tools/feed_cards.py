#!/usr/bin/env python3
"""Strict blind click test helper. Standard library only, no install, no key.

1) Make a cards file (JSON list). One entry per card:
   {"id": "ours-t1", "side": "ours", "title": "...", "thumb": "thumbs/t1.jpg",
    "channel": "Your Channel", "views": "850K", "age": "2 weeks ago"}
   Give our card the competitors' median view count and a similar age, so view counts never decide.
   {"id": "comp-1", "side": "comp", "title": "...", "thumb": "refs/c1.jpg",
    "channel": "Top Competitor", "views": "2.1M", "age": "3 weeks ago", "views_n": 2100000}
   Competitors are the most-viewed similar videos only. views_n (a number) marks the best one.

2) Build the test:
   python feed_cards.py pairs cards.json --out test1 [--mode full|title|thumb] [--viewer "who the viewer is"]
   Writes test1/pairs.jsonl (every ours-vs-competitor pair in BOTH orders), one judge prompt
   per pair in test1/prompts/, and test1/cards.html (mock mobile feed cards, one screen per pair).
   Judges never see which card is ours, the script, the research or the plan.

3) Give each prompt to each judge (fresh agents, several model families, never the maker).
   Collect answers in a CSV with the header:  pair_id,judge,family,choice,reason
   choice is 1 (top card) or 2 (bottom card).

4) Score:
   python feed_cards.py tally test1 answers.csv
   A pair counts as a win only if the judge picked ours in both orders. Split = tie (half).
   Pass bar: win rate >= 60%, beats the best competitor card, and a majority of families agree.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import sys
from collections import defaultdict
from pathlib import Path

PROMPT = """You are scrolling YouTube on your phone. {viewer}
Two videos appear in your feed, one above the other. You can tap only one.

Card 1 (top):
{c1}

Card 2 (bottom):
{c2}

Which one do you tap? Answer with exactly one line: the number (1 or 2), a colon, then the one main reason in under 20 words.
Example: 2: the thumbnail shows a clear problem I want solved.
Judge only what is on the cards. You know nothing else about either video."""


def card_text(c: dict, mode: str) -> str:
    lines = []
    if mode in ("full", "thumb"):
        lines.append(f"  Thumbnail image file: {c.get('thumb', '')} (open and look at it)")
    if mode in ("full", "title"):
        lines.append(f"  Title: {c.get('title', '')}")
    else:
        lines.append("  Title: (hidden for this test)")
    lines.append(f"  Channel: {c.get('channel', '')}  |  {c.get('views', '')} views  |  {c.get('age', '')}")
    return "\n".join(lines)


def card_html(c: dict, mode: str) -> str:
    thumb = ""
    if mode in ("full", "thumb"):
        thumb = f'<img src="{html.escape(c.get("thumb", ""))}" alt="">'
    title = html.escape(c.get("title", "")) if mode in ("full", "title") else "&nbsp;"
    meta = html.escape(f"{c.get('channel', '')} · {c.get('views', '')} views · {c.get('age', '')}")
    return f'<div class="card">{thumb}<div class="t">{title}</div><div class="m">{meta}</div></div>'


def cmd_pairs(a):
    cards = json.loads(Path(a.cards).read_text(encoding="utf-8"))
    ours = [c for c in cards if c.get("side") == "ours"]
    comps = [c for c in cards if c.get("side") != "ours"]
    if not ours or not comps:
        sys.exit("need at least one card with side=ours and one competitor card")
    out = Path(a.out)
    (out / "prompts").mkdir(parents=True, exist_ok=True)
    viewer = a.viewer or "You watch a lot of videos in this topic."
    rows, screens = [], []
    n = 0
    for o in ours:
        for c in comps:
            for order in ("ours_top", "ours_bottom"):
                n += 1
                pid = f"p{n:03d}"
                top, bottom = (o, c) if order == "ours_top" else (c, o)
                rows.append({"pair_id": pid, "ours": o["id"], "comp": c["id"], "order": order,
                             "top": top["id"], "bottom": bottom["id"], "mode": a.mode})
                (out / "prompts" / f"{pid}.txt").write_text(
                    PROMPT.format(viewer=viewer, c1=card_text(top, a.mode), c2=card_text(bottom, a.mode)),
                    encoding="utf-8")
                screens.append(f'<section><h2>{pid}</h2>{card_html(top, a.mode)}{card_html(bottom, a.mode)}</section>')
    with open(out / "pairs.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    meta = {c["id"]: {k: c.get(k) for k in ("side", "title", "views", "views_n", "channel")} for c in cards}
    (out / "cards.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    css = ("body{background:#0f0f0f;color:#f1f1f1;font-family:Roboto,Arial,sans-serif;margin:0}"
           "section{width:390px;margin:16px auto;border-bottom:1px solid #333}"
           "h2{font-size:11px;color:#777;margin:4px 12px}.card{margin:0 0 18px}"
           ".card img{width:390px;height:219px;object-fit:cover;display:block}"
           ".t{font-size:15px;line-height:20px;font-weight:500;margin:10px 12px 4px}"
           ".m{font-size:12px;color:#aaa;margin:0 12px}")
    (out / "cards.html").write_text(
        f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        f'<title>Feed cards</title><style>{css}</style>' + "".join(screens), encoding="utf-8")
    print(f"{len(rows)} pairs ({len(ours)} ours x {len(comps)} competitors x 2 orders) in {out}")
    print("Next: give every prompt in prompts/ to every judge, collect answers.csv, then run tally.")


def cmd_tally(a):
    out = Path(a.test)
    pairs = {}
    for line in (out / "pairs.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            pairs[r["pair_id"]] = r
    meta = json.loads((out / "cards.json").read_text(encoding="utf-8"))
    # picks[(ours, comp, judge)] = {order: picked_ours}
    picks = defaultdict(dict)
    family = {}
    reasons = defaultdict(list)
    with open(a.answers, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            p = pairs.get(row["pair_id"].strip())
            if not p:
                continue
            choice = row["choice"].strip()[:1]
            picked = p["top"] if choice == "1" else p["bottom"]
            got = picked == p["ours"]
            key = (p["ours"], p["comp"], row["judge"].strip())
            picks[key][p["order"]] = got
            family[row["judge"].strip()] = row.get("family", "").strip() or "unknown"
            if not got:
                reasons[p["ours"]].append(f"vs {p['comp']} ({p['order']}): {row.get('reason', '').strip()}")
    comps = [k for k, v in meta.items() if v.get("side") != "ours"]
    best = max(comps, key=lambda k: float(meta[k].get("views_n") or 0)) if comps else None
    by_ours = defaultdict(lambda: {"score": 0.0, "n": 0, "vs": defaultdict(lambda: [0.0, 0]),
                                   "fam": defaultdict(lambda: [0.0, 0]), "incomplete": 0})
    for (o, c, j), orders in picks.items():
        s = by_ours[o]
        if len(orders) < 2:
            s["incomplete"] += 1
            continue
        v = 1.0 if all(orders.values()) else (0.0 if not any(orders.values()) else 0.5)
        s["score"] += v; s["n"] += 1
        s["vs"][c][0] += v; s["vs"][c][1] += 1
        fam = family.get(j, "unknown")
        s["fam"][fam][0] += v; s["fam"][fam][1] += 1
    fams = sorted(set(family.values()))
    print(f"Judges: {len(family)} in {len(fams)} families ({', '.join(fams)})"
          + ("  WARNING: single family, weaker evidence" if len(fams) < 2 else ""))
    mode = next(iter(pairs.values()))["mode"] if pairs else "?"
    print(f"Mode: {mode}. Best competitor card: {best} ({meta.get(best, {}).get('views')} views)\n")
    for o, s in sorted(by_ours.items(), key=lambda kv: -(kv[1]["score"] / max(kv[1]["n"], 1))):
        rate = s["score"] / max(s["n"], 1)
        vb = s["vs"].get(best, [0, 0])
        beat_best = vb[1] > 0 and vb[0] / vb[1] > 0.5
        agree = sum(1 for f, (w, n) in s["fam"].items() if n and w / n >= 0.5)
        fam_ok = agree * 2 > len(s["fam"]) if s["fam"] else False
        passed = rate >= 0.6 and beat_best and fam_ok
        print(f"{o}: {rate:.0%} over {s['n']} both-order pairs | beats best: {'yes' if beat_best else 'NO'} "
              f"| families agreeing: {agree}/{len(s['fam'])} | {'PASS' if passed else 'NOT YET'}"
              + (f" | {s['incomplete']} pairs missing one order" if s["incomplete"] else ""))
        for c, (w, n) in sorted(s["vs"].items()):
            print(f"    vs {c}: {w:g}/{n}")
        for r in reasons[o][:a.reasons]:
            print(f"    lost: {r}")
    if mode == "title":
        print("\nTitle-only test: any competitor ours scores under 50% against beats us on title alone. Say so in the report.")


def main():
    ap = argparse.ArgumentParser(description="Strict blind click test: pairwise, both orders, no story context.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pairs")
    p.add_argument("cards")
    p.add_argument("--out", required=True)
    p.add_argument("--mode", choices=["full", "title", "thumb"], default="full")
    p.add_argument("--viewer", default="")
    t = sub.add_parser("tally")
    t.add_argument("test")
    t.add_argument("answers")
    t.add_argument("--reasons", type=int, default=8)
    a = ap.parse_args()
    {"pairs": cmd_pairs, "tally": cmd_tally}[a.cmd](a)


if __name__ == "__main__":
    main()
