"""Small local tools for a creator's own research; no account access."""
import argparse
import csv
import datetime as dt
import json
import math
import re
import statistics
import subprocess
import sys
from pathlib import Path

FIELDS = ('channel', 'video_id', 'title', 'url', 'views', 'published', 'observed', 'duration_seconds')
STOP = set('a an and are as at be by for from how i if in is it of on or that the this to was what when why with you your'.split())


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError('CSV has no header')
        rows = list(reader)
        return reader.fieldnames, rows


def date(value):
    return dt.date.fromisoformat(value)


def validate(rows, fields):
    missing = set(FIELDS) - set(fields)
    if missing:
        raise ValueError('Missing columns: ' + ', '.join(sorted(missing)))
    seen, parsed, errors = set(), [], []
    for number, row in enumerate(rows, 2):
        try:
            if not all(row.get(k, '').strip() for k in FIELDS):
                raise ValueError('all fields required; omit incomplete rows and record the gap separately')
            video_id = row['video_id'].strip()
            if video_id in seen:
                raise ValueError('duplicate video_id ' + video_id)
            views, duration = int(row['views']), float(row['duration_seconds'])
            if views < 0 or not math.isfinite(duration) or duration <= 0:
                raise ValueError('views must be nonnegative and duration positive')
            published, observed = date(row['published']), date(row['observed'])
            if observed < published:
                raise ValueError('observed date precedes publication')
            if not row['url'].startswith(('https://', 'http://')):
                raise ValueError('URL must begin with http:// or https://')
            seen.add(video_id)
            parsed.append({**row, 'views': views, 'duration_seconds': duration,
                           'age_days': max((observed - published).days, 1)})
        except (ValueError, TypeError) as exc:
            errors.append(f'row {number}: {exc}')
    if errors:
        raise ValueError('\n'.join(errors))
    if not parsed:
        raise ValueError('No complete video rows')
    return parsed


def rank(rows):
    """Leave-one-out same-channel log-view baseline; never cap residuals."""
    groups = {}
    for row in rows:
        groups.setdefault(row['channel'].strip().casefold(), []).append(row)
    out = []
    for row in rows:
        peers = [p for p in groups[row['channel'].strip().casefold()] if p is not row]
        age = math.log10(row['age_days'] + 1)
        peers.sort(key=lambda p: (abs(math.log10(p['age_days'] + 1) - age), p['video_id']))
        matched = [p for p in peers if abs(math.log10(p['age_days'] + 1) - age) <= .20]
        if len(matched) >= 8:
            pool, method = matched, 'age-matched'
        elif len(peers) >= 8:
            pool, method = peers[:12], 'nearest-age'
        elif len(peers) >= 2:
            pool, method = peers, 'small-channel-median'
        else:
            pool, method = [], 'insufficient'
        result = dict(row)
        result['baseline_method'] = method
        result['peer_count'] = len(pool)
        if pool:
            base = statistics.median(math.log10(max(1, p['views'])) for p in pool)
            residual = math.log10(max(1, row['views'])) - base
            result.update(baseline_views=round(10 ** base, 2), residual_log10=round(residual, 5),
                          breakout_ratio=round(10 ** residual, 3))
        else:
            result.update(baseline_views='', residual_log10='', breakout_ratio='')
        out.append(result)
    return sorted(out, key=lambda r: (r['residual_log10'] == '', -(r['residual_log10'] or 0)))


def tokens(text):
    return {x for x in re.findall(r"[a-z0-9]+", text.casefold()) if len(x) > 2 and x not in STOP}


def overlap(candidate, rows):
    words = tokens(candidate)
    if not words:
        raise ValueError('Candidate has no content words')
    out = []
    for row in rows:
        other = tokens(row['title'])
        common = words & other
        out.append({'title': row['title'], 'channel': row['channel'], 'url': row['url'],
                    'shared_words': ', '.join(sorted(common)),
                    'candidate_coverage': round(len(common) / len(words), 3),
                    'jaccard': round(len(common) / len(words | other), 3)})
    return sorted(out, key=lambda r: (r['candidate_coverage'], r['jaccard']), reverse=True)


def write_csv(path, rows, fields):
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def import_metadata(paths, observed):
    """Convert locally supplied yt-dlp-style JSON. Never fetches or logs metadata."""
    date(observed)
    converted = []
    for path in paths:
        obj = json.loads(Path(path).read_text(encoding='utf-8-sig'))
        if not isinstance(obj, dict) or isinstance(obj.get('entries'), list):
            raise ValueError(f'{path}: expected one video object, not a playlist')
        uploaded = str(obj.get('upload_date') or '')
        if re.fullmatch(r'\d{8}', uploaded):
            uploaded = f'{uploaded[:4]}-{uploaded[4:6]}-{uploaded[6:8]}'
        video_id = obj.get('id') or ''
        converted.append({'channel': obj.get('channel_id') or obj.get('channel_url') or '',
                          'video_id': video_id, 'title': obj.get('title') or '',
                          'url': obj.get('webpage_url') or '',
                          'views': str(obj['view_count']) if obj.get('view_count') is not None else '',
                          'published': uploaded, 'observed': observed,
                          'duration_seconds': str(obj['duration']) if obj.get('duration') is not None else ''})
    validate(converted, FIELDS)
    return converted


def scaffold(path):
    dest = Path(path)
    if dest.exists():
        raise ValueError(f'{dest} already exists; refusing to overwrite')
    source = Path(__file__).resolve().parent.parent / 'templates' / 'project'
    import shutil
    shutil.copytree(source, dest)
    return dest


def probe_media(path):
    source = Path(path)
    if not source.is_file():
        raise ValueError(f'Local media file not found: {source}')
    command = ['ffprobe', '-v', 'error', '-show_entries',
               'format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate',
               '-of', 'json', str(source)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False,
                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except FileNotFoundError as exc:
        raise ValueError('ffprobe is not installed or not on PATH') from exc
    if result.returncode:
        raise ValueError('ffprobe could not read this file: ' + result.stderr.strip()[:500])
    info = json.loads(result.stdout)
    return {'file': str(source), 'duration_seconds': info.get('format', {}).get('duration'),
            'streams': info.get('streams', []),
            'visual_story_review': 'INCOMPLETE', 'full_audio_review': 'INCOMPLETE'}


def main(argv=None):
    p = argparse.ArgumentParser(description='Local tools for original, evidence-led channel research')
    commands = p.add_subparsers(dest='command', required=True)
    new = commands.add_parser('init', help='create a new project from blank templates')
    new.add_argument('directory')
    imp = commands.add_parser('import-json', help='convert locally collected video metadata JSON into CSV')
    imp.add_argument('json', nargs='+'); imp.add_argument('--observed', required=True, help='observation date YYYY-MM-DD')
    imp.add_argument('--out', required=True)
    probe = commands.add_parser('probe', help='inspect technical media metadata with ffprobe')
    probe.add_argument('file'); probe.add_argument('--out', required=True)
    v = commands.add_parser('validate', help='check a video CSV')
    v.add_argument('csv')
    r = commands.add_parser('rank', help='calculate within-channel age-aware residuals')
    r.add_argument('csv'); r.add_argument('--out', required=True)
    o = commands.add_parser('overlap', help='find title word overlap; manual idea review remains necessary')
    o.add_argument('csv'); o.add_argument('candidate'); o.add_argument('--out', required=True)
    args = p.parse_args(argv)
    try:
        if args.command == 'init':
            print(f'Created {scaffold(args.directory)}'); return 0
        if args.command == 'import-json':
            if any(Path(path).resolve() == Path(args.out).resolve() for path in args.json):
                raise ValueError('Output must differ from every input JSON')
            result = import_metadata(args.json, args.observed)
            write_csv(args.out, result, FIELDS)
            print(f'Wrote {len(result)} rows to {args.out}; verify the observation date and metadata sources.')
            return 0
        if args.command == 'probe':
            if Path(args.file).resolve() == Path(args.out).resolve():
                raise ValueError('Output must differ from the media file')
            result = probe_media(args.file)
            dest = Path(args.out); dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
            print(f'Wrote technical metadata to {dest}; picture and audio reviews remain INCOMPLETE.')
            return 0
        fields, raw = read_csv(args.csv)
        rows = validate(raw, fields)
        if args.command == 'validate':
            print(f'OK: {len(rows)} videos, {len({r["channel"].casefold() for r in rows})} channels'); return 0
        if Path(args.csv).resolve() == Path(args.out).resolve():
            raise ValueError('Output must differ from the input CSV')
        if args.command == 'rank':
            result = rank(rows)
            write_csv(args.out, result, list(FIELDS) + ['age_days', 'peer_count', 'baseline_method', 'baseline_views', 'residual_log10', 'breakout_ratio'])
            print(f'Wrote {len(result)} rows to {args.out}; small-channel and insufficient baselines are flagged.')
        else:
            result = overlap(args.candidate, rows)
            write_csv(args.out, result, ['title', 'channel', 'url', 'shared_words', 'candidate_coverage', 'jaccard'])
            print(f'Wrote {len(result)} comparisons to {args.out}; word overlap is a lead, not a clearance decision.')
        return 0
    except (ValueError, OSError, csv.Error) as exc:
        print(f'Error: {exc}', file=sys.stderr); return 2
