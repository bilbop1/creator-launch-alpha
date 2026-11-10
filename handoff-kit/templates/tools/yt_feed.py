#!/usr/bin/env python3
"""Public YouTube numbers with no install, no login and no API key (Python standard library only).

For the agent. Gives you real view counts so you never have to ask the user to paste data.

  python yt_feed.py search "minecraft challenge"        find channels that rank for a topic
  python yt_feed.py feed @Craftee @Jeracraft UCxxxx...   last 15 uploads per channel with views

`feed` prints CSV rows (channel,video_id,title,url,views,published,observed,ratio) to stdout, where
ratio = views / that channel's median views over the same 15 uploads. Notes go to stderr.
Save the rows to .scratch/videos.csv. Numbers are the public view counts seen today.
Limits: the feed only holds the newest 15 uploads, so an old viral video can be missing.
If this fails on 3 channels in a row, say so plainly and try another source. Never invent numbers.
"""
import csv
import datetime
import re
import statistics
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def channel_id(ref):
    if re.fullmatch(r"UC[\w-]{22}", ref):
        return ref
    if ref.startswith("http"):
        url = ref
    else:
        url = "https://www.youtube.com/" + (ref if ref.startswith("@") else "@" + ref)
    html = get(url)
    m = re.search(r"channel_id=(UC[\w-]{22})", html) or re.search(r'"externalId":"(UC[\w-]{22})"', html)
    if not m:
        raise RuntimeError("no channel id found for " + ref)
    return m.group(1)


def feed(ref, writer, today):
    cid = channel_id(ref)
    xml = get("https://www.youtube.com/feeds/videos.xml?channel_id=" + cid)
    name = re.search(r"<title>(.*?)</title>", xml).group(1)
    rows = []
    for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        vid = re.search(r"<yt:videoId>(.*?)</yt:videoId>", e).group(1)
        title = re.search(r"<media:title>(.*?)</media:title>", e).group(1)
        views = int(re.search(r'statistics views="(\d+)"', e).group(1))
        pub = re.search(r"<published>(.*?)</published>", e).group(1)[:10]
        rows.append((vid, title, views, pub))
    if not rows:
        raise RuntimeError("empty feed for " + ref)
    med = statistics.median(r[2] for r in rows) or 1
    for vid, title, views, pub in rows:
        writer.writerow([name, vid, title, "https://www.youtube.com/watch?v=" + vid, views, pub, today, round(views / med, 2)])
    print(f"{name}: {len(rows)} uploads, median views {int(med)}", file=sys.stderr)


def search(query):
    html = get("https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query))
    seen = {}
    for chunk in html.split('"videoRenderer":{"videoId":"')[1:]:
        vid = chunk[:11]
        t = re.search(r'"title":\{"runs":\[\{"text":"(.*?)"', chunk)
        c = re.search(r'"longBylineText":\{"runs":\[\{"text":"(.*?)".*?"browseId":"(UC[\w-]{22})"', chunk)
        v = re.search(r'"viewCountText":\{"simpleText":"(.*?)"', chunk)
        if c:
            seen.setdefault(c[2], []).append((c[1], vid, t[1] if t else "", v[1] if v else ""))
    for cid, items in seen.items():
        print(f"{items[0][0]}  {cid}  e.g. {items[0][2]} ({items[0][3]}) https://www.youtube.com/watch?v={items[0][1]}")


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("search", "feed"):
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == "search":
        search(" ".join(sys.argv[2:]))
        return
    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(["channel", "video_id", "title", "url", "views", "published", "observed", "ratio"])
    today = datetime.date.today().isoformat()
    for ref in sys.argv[2:]:
        try:
            feed(ref, w, today)
        except Exception as e:
            print(f"{ref}: failed ({e})", file=sys.stderr)


if __name__ == "__main__":
    main()
