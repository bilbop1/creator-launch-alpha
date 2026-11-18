#!/usr/bin/env python3
"""Human-copy check for anything that goes on a platform: titles, descriptions, tags,
pinned comments, community posts, Shorts text, on-screen text and the script's voice.
Standard library only.

Usage:
  python copy_check.py file.txt [more files]     check files
  python copy_check.py --text "My title here"    check one string
  python copy_check.py style --ours ours.txt --theirs competitor_titles.txt
      Measures our copy against the most-viewed competitor copy (one item per line, or items
      separated by a line of =====): length, words, sentence length, capitals, numbers,
      questions, how lines open, contractions. Fails any measure outside the competitors' band.
Exit code 0 = clean, 1 = problems found (each printed with line and reason).

The patterns follow Wikipedia's "Signs of AI writing" page
(https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing); the kit keeps a local checklist of it
in handoff-kit/SIGNS-OF-AI-WRITING.md. This catches the mechanical tells only. Passing is not enough:
read the copy once out loud, match the competitor's measured style (the style command), then win a
blind pairwise test against their copy before it is used.
"""
from __future__ import annotations

import argparse
import re
import statistics
import sys
from pathlib import Path

HARD = [
    ("[\u2014\u2013]", "em or en dash (use a comma, period or colon)"),
    ("[\u2018\u2019\u201c\u201d]", "curly quote (use straight quotes)"),
    ("\u2026", "ellipsis character (type three dots or cut it)"),
    (r"\s--\s", "double hyphen used as a dash"),
    (r"\bnot (just |only |merely )?(a |an |the )?[\w' ]{1,30}[,;:] (it'?s|it is|but|this is|they'?re)\b",
     "'not X, it's Y' contrast formula"),
    (r"\bit'?s not (just |only )?about\b", "'it's not about X' formula"),
    (r"\b(isn'?t|wasn'?t|aren'?t) just\b[^.]{0,60}\b(it'?s|it is|they'?re)\b", "'isn't just X, it's Y' formula"),
    (r"\bhere'?s the (thing|kicker|catch|truth)\b", "stock reveal phrase"),
    (r"\b(let'?s|let us) dive (in|into|deep)\b", "AI phrase 'let's dive in'"),
    (r"\bin (today'?s|this) (fast[- ]paced |ever[- ]changing |digital )?(world|landscape|age)\b", "AI phrase 'in today's world'"),
    (r"\b(buckle up|without further ado|the answer may surprise you|you won'?t believe)\b", "stock filler phrase"),
    (r"\b(game[- ]changer|unlock the secrets?|the power of|a testament to|stands as a|serves as a)\b", "AI phrase"),
    # Wikipedia "Signs of AI writing", section by section
    (r"\bnot only\b[^.]{0,80}\bbut\b", "negative parallelism 'not only X but also Y'"),
    (r"\bno [\w' ]{1,20}, no [\w' ]{1,20}, (just|only)\b", "negative parallelism 'no X, no Y, just Z'"),
    (r"\b(nestled|in the heart of|breathtaking|must[- ]see|stunning|rich (cultural )?heritage|renowned|boasts an?)\b",
     "promotional language"),
    (r",\s(highlighting|underscoring|emphasizing|reflecting|symbolizing|showcasing|contributing to|ensuring|fostering)\b",
     "superficial '-ing' analysis tacked onto a clause"),
    (r"\b(marks|represents|serves as|stands as) (a|an) (pivotal|significant|key|important|major) (moment|turning point|step|milestone)\b",
     "inflated significance"),
    (r"\b(plays|played) (a|an) (vital|key|crucial|pivotal|significant) role\b", "inflated significance 'plays a vital role'"),
    (r"\b(experts|observers|critics|industry reports|many people) (say|argue|believe|suggest|note)\b", "vague attribution (weasel words)"),
    (r"\b(in (summary|conclusion)|to sum up|all in all)\b", "summary closer"),
    (r"^\s*overall,", "summary closer 'Overall,'"),
    (r"\bdespite (its|these|the) [\w ]{1,30}, [\w ]{1,40} (faces|continues to face) challenges\b", "challenges and prospects formula"),
    (r"\b(as of my (last|knowledge)|i hope this helps|certainly!|great question|i'?d be happy to|let me know if)\b",
     "chatbot phrase"),
    (r"\bfrom [\w' ]{1,25} to [\w' ]{1,25}, (and )?from\b", "false range 'from X to Y, from A to B'"),
    (r"\bwhether (you'?re|it'?s) [\w' ]{1,30} or\b", "stock 'whether you're X or Y' opener"),
    (r"\b(ever wondered|have you ever wondered)\b", "stock hook 'ever wondered'"),
    ("[\U0001F300-\U0001FAFF]\\s*\\*\\*", "emoji bullet with bold"),
]

AI_WORDS = set(("delve delves delving tapestry testament multifaceted intricate intricacies pivotal "
                "realm landscape navigate navigating embark showcase showcasing showcases underscore underscores "
                "underscoring meticulous meticulously seamless seamlessly vibrant robust leverage leveraging foster "
                "fostering garner garnered unveil unveiled unveils unravel unraveling elevate elevated holistic "
                "paramount bustling captivating enigmatic beacon symphony intricately nuanced "
                "transformative groundbreaking unparalleled ever-evolving crucial furthermore moreover "
                "additionally notably ultimately align aligns boasts bolster bolstered enduring enhance enhances "
                "interplay valuable commendable emphasize emphasizing highlighting profound resonate resonates "
                "synergy").split())


def check(text: str) -> list[str]:
    problems = []
    for i, line in enumerate(text.splitlines() or [text], 1):
        for pat, why in HARD:
            m = re.search(pat, line, re.I)
            if m:
                problems.append(f"line {i}: {why}: {m.group(0)!r}")
        words = re.findall(r"[a-z][a-z-]+", line.lower())
        hits = sorted({w for w in words if w in AI_WORDS})
        if hits:
            problems.append(f"line {i}: AI vocabulary: {', '.join(hits)}")
        if re.search(r"\b\w+, \w+(,)? and \w+\b", line) and len(line) < 140:
            problems.append(f"line {i}: possible rule-of-three list for rhythm (keep only if it is real information)")
        if line.count(":") >= 2:
            problems.append(f"line {i}: several colons in one line")
        if len(re.findall(r"\*\*[^*]+\*\*", line)) >= 3:
            problems.append(f"line {i}: bold overuse")
    if len(re.findall(r"!", text)) > 2:
        problems.append("more than 2 exclamation marks in total")
    return problems


def _items(text: str) -> list[str]:
    parts = re.split(r"\n=====+\n", text) if "=====" in text else text.splitlines()
    return [p.strip() for p in parts if p.strip()]


def measures(item: str) -> dict:
    words = item.split()
    sents = [s for s in re.split(r"[.!?]+\s", item) if s.strip()]
    return {
        "chars": len(item),
        "words": len(words),
        "words_per_sentence": round(len(words) / max(1, len(sents)), 1),
        "caps_words": sum(1 for w in words if len(w) > 1 and w.isupper()),
        "contraction_rate": round(len(re.findall(r"\b\w+'(s|t|re|ve|ll|d|m)\b", item, re.I)) / max(1, len(words)), 3),
        "has_number": int(bool(re.search(r"\d", item))),
        "has_question": int("?" in item),
        "has_exclaim": int("!" in item),
        "starts_number_or_I": int(bool(re.match(r"(\$?\d|I\b|I'|My\b)", item))),
        "starts_how_why_what": int(bool(re.match(r"(how|why|what|who|when)\b", item, re.I))),
    }


def style(ours_text: str, theirs_text: str) -> int:
    ours, theirs = _items(ours_text), _items(theirs_text)
    if len(theirs) < 3 or not ours:
        print("need our copy and at least 3 competitor items to measure a style")
        return 1
    mo = [measures(x) for x in ours]
    mt = [measures(x) for x in theirs]
    bad = 0
    print(f"{'measure':22} {'ours':>8} {'theirs':>18}  result")
    for k in mt[0]:
        tv = sorted(m[k] for m in mt)
        if k.startswith(("has_", "starts_")):  # shares of items: ours must be within a third of theirs
            rate = sum(tv) / len(tv)
            ov = sum(m[k] for m in mo) / len(mo)
            ok = abs(ov - rate) <= 0.34
            band = f"{rate:.2f} +/- 0.34"
        else:
            if len(tv) >= 4:
                q = statistics.quantiles(tv, n=4)
                lo, hi = q[0], q[2]
            else:
                lo, hi = tv[0], tv[-1]
            ov = statistics.median(m[k] for m in mo)
            ok = lo <= ov <= hi
            band = f"{lo:g} to {hi:g}"
        bad += not ok
        print(f"{k:22} {ov:>8.2f} {band:>18}  {'PASS' if ok else 'FAIL'}")
    print(f"\n{bad} measure(s) off the competitor style. Rewrite toward their band, then blind-test against their copy.")
    return 1 if bad else 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "style":
        sp = argparse.ArgumentParser(prog="copy_check.py style")
        sp.add_argument("--ours", required=True)
        sp.add_argument("--theirs", required=True)
        sa = sp.parse_args(sys.argv[2:])
        sys.exit(style(Path(sa.ours).read_text(encoding="utf-8"), Path(sa.theirs).read_text(encoding="utf-8")))
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--text")
    a = ap.parse_args()
    items = [("text", a.text)] if a.text is not None else []
    items += [(f, Path(f).read_text(encoding="utf-8")) for f in a.files]
    if not items:
        ap.error("give a file or --text")
    bad = False
    for name, text in items:
        probs = check(text)
        if probs:
            bad = True
            print(f"{name}: {len(probs)} problem(s)")
            for p in probs:
                print("  " + p)
        else:
            print(f"{name}: clean of AI tells. Now: read it out loud, run the style command against the top competitor copy, and blind-test it.")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
