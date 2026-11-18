#!/usr/bin/env python3
"""Shared YouTube helpers for methods.py and parity.py. Standard library plus yt-dlp.

For the agent. yt-dlp is free and needs no account or key. If it is missing, this module
installs it once with `python -m pip install --user yt-dlp` (routine, free) and carries on.
Every subprocess runs hidden (no window) and at low priority, so the person's screen is never touched.

Functions:
  search(query, n, when)         flat search results (when: relevance, month, year, views_month): id, title, channel, channel_id, view_count, duration
  details(ids)                   full metadata per video (upload_date, tags, description, chapters ...)
  baseline(channel_id, shorts)   median views of the channel's recent uploads (its own baseline)
  uploads(channel_id, shorts, n) the channel's recent uploads with views and duration
  transcript(video_id, outdir)   plain-text transcript: subtitles, then youtube_transcript_api, then local Whisper
"""
from __future__ import annotations

import json
import os
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)
LOWPRI = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
_YTDLP: list | None = None
# small clips for measuring; works without a JS runtime (m3u8 formats); the original audio track, not a dub
SMALL_VIDEO = "bv*[height<=360]+ba[format_note*=original]/bv*[height<=360]+ba/wv*+ba/w"
ORIGINAL_AUDIO = "ba[format_note*=original][abr<=160]/ba[format_note*=original]/ba/w"


def _popen_kwargs():
    kw = {"creationflags": NOWIN | LOWPRI}
    if os.name != "nt":
        kw = {"preexec_fn": lambda: os.nice(10)}
    return kw


def ytdlp() -> list:
    """Command prefix for yt-dlp. Installs it (pip --user) the first time if it is missing."""
    global _YTDLP
    if _YTDLP:
        return _YTDLP
    if shutil.which("yt-dlp"):
        _YTDLP = ["yt-dlp"]
        return _YTDLP
    probe = subprocess.run([sys.executable, "-c", "import yt_dlp"], capture_output=True, **_popen_kwargs())
    if probe.returncode != 0:
        print("note: installing yt-dlp (free, no account)", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--quiet", "--upgrade", "yt-dlp"],
                       capture_output=True, **_popen_kwargs())
    _YTDLP = [sys.executable, "-m", "yt_dlp"]
    return _YTDLP


def run_json(args: list, timeout: int = 900) -> list[dict]:
    cmd = ytdlp() + ["--ignore-errors", "--no-warnings", "-j", *args]
    for attempt in range(3):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=timeout, **_popen_kwargs())
        except subprocess.TimeoutExpired:
            continue
        rows = []
        for line in r.stdout.splitlines():
            if line.startswith("{"):
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        if rows or "429" not in r.stderr:
            return rows
        print("note: YouTube said slow down (429); retrying", file=sys.stderr)
    return []


# YouTube search filters (the sp= value of a results URL)
SEARCH_FILTERS = {"month": "EgIIBA%3D%3D", "year": "EgIIBQ%3D%3D", "views_month": "CAMSAggE"}


def search(query: str, n: int = 25, when: str = "") -> list[dict]:
    """when: "" (relevance), "month", "year" or "views_month" (most viewed this month)."""
    if not when:
        return run_json(["--flat-playlist", f"ytsearch{n}:{query}"])
    import urllib.parse
    url = ("https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
           + "&sp=" + SEARCH_FILTERS[when])
    return run_json(["--flat-playlist", "--playlist-end", str(n), url])


def details(ids: list[str]) -> list[dict]:
    if not ids:
        return []
    urls = ["https://www.youtube.com/watch?v=" + i for i in ids]
    from concurrent.futures import ThreadPoolExecutor
    batches = [urls[k:k + 15] for k in range(0, len(urls), 15)]  # small batches run in parallel
    with ThreadPoolExecutor(4) as ex:
        return [row for rows in ex.map(lambda b: run_json(["--skip-download", "--no-playlist", *b]), batches) for row in rows]


def uploads(channel_id: str, shorts: bool = False, n: int = 30) -> list[dict]:
    base = f"https://www.youtube.com/channel/{channel_id}" if channel_id.startswith("UC") else channel_id.rstrip("/")
    base = re.sub(r"/(videos|shorts|streams|featured)$", "", base)
    tab = "/shorts" if shorts else "/videos"
    return [r for r in run_json(["--flat-playlist", "--playlist-end", str(n), base + tab]) if r.get("view_count") is not None]


def baseline(channel_id: str, shorts: bool = False, n: int = 30) -> tuple[float | None, int]:
    """(median views of the last n uploads, how many uploads it used). A median from under 10 uploads is a hint only."""
    rows = uploads(channel_id, shorts, n)
    views = [r["view_count"] for r in rows if r.get("view_count") is not None]
    if not views:
        return None, 0
    return float(statistics.median(views)), len(views)


def is_short(info: dict) -> bool:
    d = info.get("duration") or 0
    return bool(d and d <= 180) or "/shorts/" in (info.get("url") or info.get("webpage_url") or "")


def vtt_to_text(vtt: str) -> str:
    lines, last = [], None
    for raw in vtt.splitlines():
        s = raw.strip()
        if not s or s.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or "-->" in s or s.isdigit():
            continue
        s = re.sub(r"<[^>]+>", "", s).strip()
        if s and s != last:
            lines.append(s)
            last = s
    text = " ".join(lines)
    # auto captions repeat each phrase as it scrolls: drop repeated runs of words
    words, out = text.split(), []
    for w in words:
        out.append(w)
        for k in (12, 8, 6, 4):
            if len(out) >= 2 * k and out[-k:] == out[-2 * k:-k]:
                del out[-k:]
                break
    return " ".join(out)


def transcript(video_id: str, outdir: Path, whisper_model: str = "small") -> tuple[str, str]:
    """Return (text, method). Tries subtitles, then youtube_transcript_api, then local Whisper on the audio."""
    outdir.mkdir(parents=True, exist_ok=True)
    url = "https://www.youtube.com/watch?v=" + video_id
    subprocess.run(ytdlp() + ["--ignore-errors", "--no-warnings", "--skip-download", "--write-subs", "--write-auto-subs",
                              "--sub-langs", "en.*,en", "--sub-format", "vtt", "-o", str(outdir / "%(id)s.%(ext)s"), url],
                   capture_output=True, timeout=600, **_popen_kwargs())
    subs = sorted(outdir.glob(f"{video_id}*.vtt"), key=lambda p: ("orig" in p.name, p.stat().st_size), reverse=True)
    if subs:
        text = vtt_to_text(subs[0].read_text(encoding="utf-8", errors="replace"))
        for p in subs:
            p.unlink(missing_ok=True)
        if len(text) > 200:
            return text, "subtitles"
    try:
        from youtube_transcript_api import YouTubeTranscriptApi  # optional library
        api = YouTubeTranscriptApi()
        got = api.fetch(video_id) if hasattr(api, "fetch") else YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join((getattr(x, "text", None) or x["text"]) for x in got)
        if len(text) > 200:
            return text, "transcript library"
    except Exception:
        pass
    try:  # local Whisper fallback, on the GPU when there is one
        from faster_whisper import WhisperModel
    except Exception:
        return "", "none (no subtitles; install faster-whisper for the local fallback)"
    audio = outdir / f"{video_id}.audio"
    subprocess.run(ytdlp() + ["--ignore-errors", "--no-warnings", "-f", ORIGINAL_AUDIO, "-o", str(audio), url],
                   capture_output=True, timeout=1800, **_popen_kwargs())
    got = next(iter(outdir.glob(f"{video_id}.audio*")), None)
    if not got:
        return "", "none (audio download failed)"
    try:
        model = WhisperModel(whisper_model, device="auto", compute_type="auto")
        segs, _ = model.transcribe(str(got), vad_filter=True)
        text = " ".join(s.text.strip() for s in segs)
    finally:
        got.unlink(missing_ok=True)
    return text, f"local whisper ({whisper_model})"


def fmt_date(d: str | None) -> str:
    return f"{d[:4]}-{d[4:6]}-{d[6:]}" if d and len(d) == 8 else (d or "")
