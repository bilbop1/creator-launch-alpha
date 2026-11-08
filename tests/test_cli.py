import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from launchkit.cli import FIELDS, import_metadata, main, overlap, rank, read_csv, validate

ROOT = Path(__file__).resolve().parents[1]


class LaunchkitTests(unittest.TestCase):
    def setUp(self):
        fields, raw = read_csv(ROOT / 'examples' / 'videos.csv')
        self.rows = validate(raw, fields)

    def test_baseline_excludes_video_and_flags_small_samples(self):
        ranked = rank(self.rows)
        item = next(x for x in ranked if x['video_id'] == 'a05')
        self.assertEqual(item['peer_count'], 4)
        self.assertEqual(item['baseline_method'], 'small-channel-median')
        self.assertGreater(item['breakout_ratio'], 4)
        self.assertEqual(next(x for x in rank([self.rows[0]]) )['baseline_method'], 'insufficient')

    def test_overlap_finds_shared_words(self):
        result = overlap('A museum on the moon', self.rows)
        self.assertEqual(result[0]['video_id'] if 'video_id' in result[0] else result[0]['title'], 'The museum on the moon')
        self.assertEqual(result[0]['candidate_coverage'], 1)

    def test_rejects_invalid_and_duplicate_data(self):
        row = {k: str(self.rows[0][k]) for k in FIELDS}
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            validate([row, row], FIELDS)
        row['observed'] = '2020-01-01'
        with self.assertRaisesRegex(ValueError, 'precedes'):
            validate([row], FIELDS)

    def test_cli_project_and_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            project = Path(d) / 'project'
            self.assertEqual(main(['init', str(project)]), 0)
            self.assertTrue((project / 'brief.md').is_file())
            with redirect_stderr(io.StringIO()):
                self.assertEqual(main(['init', str(project)]), 2)
            output = Path(d) / 'rank.csv'
            self.assertEqual(main(['rank', str(ROOT / 'examples' / 'videos.csv'), '--out', str(output)]), 0)
            with output.open(encoding='utf-8', newline='') as f:
                self.assertEqual(len(list(csv.DictReader(f))), 8)
            with redirect_stderr(io.StringIO()):
                self.assertEqual(main(['rank', str(output), '--out', str(output)]), 2)

    def test_import_metadata_requires_complete_fields(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / 'video.json'
            source.write_text(json.dumps({'id': 'id1', 'title': 'Example', 'channel_id': 'channel1',
                'webpage_url': 'https://example.com/video', 'view_count': 0,
                'upload_date': '20260101', 'duration': 55}), encoding='utf-8')
            result = import_metadata([source], '2026-04-01')
            self.assertEqual(result[0]['published'], '2026-01-01')
            self.assertEqual(result[0]['views'], '0')
            source.write_text('{"id":"missing"}', encoding='utf-8')
            with self.assertRaises(ValueError):
                import_metadata([source], '2026-04-01')


if __name__ == '__main__':
    unittest.main()
