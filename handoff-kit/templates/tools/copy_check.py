#!/usr/bin/env python3
"""Human-copy check for anything that goes on a platform: titles, descriptions, tags,
pinned comments, community posts, Shorts text, on-screen text. Standard library only.

Usage:
  python copy_check.py file.txt [more files]     check files
  python copy_check.py --text "My title here"    check one string
Exit code 0 = clean, 1 = problems found (each printed with line and reason).

It catches the mechanical tells. It cannot judge voice: after it passes, read the copy
once out loud and ask whether a specific person would really write it that way.
"""
from __future__ import annotations

import argparse
import re
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
]

AI_WORDS = ("delve delves delving tapestry testament multifaceted intricate intricacies pivotal "
            "realm landscape navigate navigating embark showcase showcasing underscore underscores "
            "meticulous meticulously seamless seamlessly vibrant robust leverage leveraging foster "
            "fostering garner unveil unveiled unveils unravel unraveling elevate elevated holistic "
            "paramount bustling captivating enigmatic beacon symphony intricately nuanced "
            "transformative groundbreaking unparalleled ever-evolving crucial furthermore moreover "
            "additionally notably ultimately").split()


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
    if len(re.findall(r"!", text)) > 2:
        problems.append("more than 2 exclamation marks in total")
    return problems


def main():
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
            print(f"{name}: clean (now read it once out loud)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
