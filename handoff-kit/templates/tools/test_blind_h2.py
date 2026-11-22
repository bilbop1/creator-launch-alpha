"""Offline tests for blind_h2 (no model calls). Run: python test_blind_h2.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blind_h2 as h2

INSTR = ('# Blind read\n\nPick the stronger.\n\nYour final reply is ONLY this JSON:\n\n{"stronger": "A" or "B", "confidence": 50-100, '
         '"scores": {"A": {"hook": n}, "B": {"hook": n}}, "reasons": "why"}')


def test_prompts_differ_and_keep_content():
    ps = [h2.build(INSTR, 'text one', 'text two') for _ in range(40)]
    assert len({m['prompt_sha1'] for _, m in ps}) == 40            # no two reads share bytes
    assert len({m['nonce'] for _, m in ps}) == 40
    assert {m['label_style'] for _, m in ps} == {'alpha', 'num'}   # both label schemes occur
    for p, m in ps:
        assert 'Pick the stronger.' in p and 'text one' in p and 'text two' in p
        assert p.index('text one') < p.index('text two')
        assert p.startswith('[read ' + m['nonce'] + ']')
        if m['label_style'] == 'num':
            assert '## SCRIPT 1' in p and '"stronger": "1" or "2"' in p and '"1": {"hook": n}, "2": {"hook": n}' in p and '"A"' not in p
        else:
            assert p == h2.build(INSTR, 'text one', 'text two', 'alpha', m['nonce'])[0]


def test_norm_maps_back_to_ab():
    r = h2.norm({'stronger': '2', 'confidence': 70, 'scores': {'1': {'hook': 5}, '2': {'hook': 8}}, 'reasons': 'x'}, 'num')
    assert r['stronger'] == 'B' and r['scores'] == {'A': {'hook': 5}, 'B': {'hook': 8}}
    assert h2.norm({'stronger': 'A', 'scores': {'A': {}, 'B': {}}}, 'alpha')['stronger'] == 'A'
    assert h2.norm({'stronger': 1}, 'num')['stronger'] == 'A'
    assert h2.norm({'stronger': 'C'}, 'alpha') is None and h2.norm(None, 'num') is None


def test_balanced_sides():
    for n in (2, 4, 6, 12):
        s = h2.balanced_sides(n)
        assert s.count('A') == s.count('B') == n // 2
    assert sorted(h2.balanced_sides(3))[:2] in (['A', 'A'], ['A', 'B'], ['B', 'B'])


def test_with_nonce():
    p, rid = h2.with_nonce('body')
    assert p == f'[read {rid}]\nbody'
    assert h2.with_nonce('body')[1] != rid


def test_store_read_refuses_duplicate_prompt_hash():
    reads = []
    (p1, m1), (p2, m2) = h2.build(INSTR, 'text one', 'text two'), h2.build(INSTR, 'text one', 'text two')
    h2.store_read(reads, {'pick': 'A', **m1})
    h2.store_read(reads, {'pick': 'B', **m2})                      # distinct prompt bytes: accepted
    assert len(reads) == 2
    try:
        h2.store_read(reads, {'pick': 'A', **m1})                  # same hash as the first read: refused, not stored
        raise AssertionError('duplicate accepted')
    except h2.DuplicatePrompt:
        pass
    assert len(reads) == 2
    h2.store_read(reads, {'pick': 'A'}, prompt=h2.with_nonce('body')[0])   # hash computed from the prompt text
    assert reads[-1]['prompt_sha1'] and len(reads) == 3
    try:
        h2.store_read(reads, {'pick': 'A'})                        # no hash at all: refused
        raise AssertionError('hashless accepted')
    except ValueError as e:
        assert not isinstance(e, h2.DuplicatePrompt)
    assert len(reads) == 3


if __name__ == '__main__':
    for k, v in list(globals().items()):
        if k.startswith('test_'):
            v(); print('ok', k)
