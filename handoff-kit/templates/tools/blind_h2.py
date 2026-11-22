"""blind_h2: make every blind-judge read an independent sample (Nov 22 2026).

Why: the first script-door harness sent the SAME prompt bytes, in the same order, to the same judge for every "repeat" read. A
repeat then mostly copied the first verdict (Claude 58 of 58, GPT 44 of 58 in the stored MT door runs), so N repeats were not N
opinions. This module varies ONLY neutral bytes per read and leaves the rubric and both texts untouched:
  - a per-read nonce line at the top ("[read 3fa9c2d1]"),
  - the option labels (A/B or 1/2), picked per read with OS randomness,
  - the presentation order (see `balanced_sides`), shuffled with OS randomness, never a fixed seed.
Judges must also be fresh stateless sessions: Codex `exec --ephemeral` from a new empty directory (never resume), Claude one plain
/v1/messages request (no temperature, seed, cache_control or metadata). Identical prompts are one read, not many.

  prompt, meta = build(instr, text_a, text_b)      # meta = {nonce, label_style, prompt_sha1}
  reply = norm(parsed_json, meta['label_style'])   # always back in A/B terms, whatever labels the judge saw
"""
import hashlib, json, random, re, secrets

_RNG = random.SystemRandom()
STYLES = ('alpha', 'num')


def nonce():
    return secrets.token_hex(4)


def pick_style():
    return _RNG.choice(STYLES)


def labels(style):
    return ('A', 'B') if style == 'alpha' else ('1', '2')


def relabel_instr(instr, style):
    """Instruction text with the reply schema in the chosen labels. Only the JSON schema tokens change."""
    if style == 'alpha':
        return instr
    out = instr.replace('"stronger": "A" or "B"', '"stronger": "1" or "2"')
    out = out.replace('"scores": {"A": {', '"scores": {"1": {').replace('}, "B": {', '}, "2": {')
    return out


def build(instr, text_a, text_b, style=None, rid=None):
    """The full prompt for one read: nonce line, the rubric (relabelled), then the two texts under neutral headings."""
    style = style or pick_style()
    rid = rid or nonce()
    la, lb = labels(style)
    prompt = (f'[read {rid}]\n' + relabel_instr(instr, style) +
              f'\n\n---\n\n## SCRIPT {la}\n\n' + text_a + f'\n\n---\n\n## SCRIPT {lb}\n\n' + text_b + '\n')
    return prompt, {'nonce': rid, 'label_style': style, 'prompt_sha1': hashlib.sha1(prompt.encode('utf-8')).hexdigest()[:12]}


def with_nonce(prompt, rid=None):
    """For a prompt that is already built (packet files): prepend a per-read nonce line."""
    rid = rid or nonce()
    return f'[read {rid}]\n' + prompt, rid


def norm(j, style):
    """Parsed reply -> the same dict with 'stronger' and the score keys in A/B terms. None if there is no usable winner."""
    if not isinstance(j, dict):
        return None
    w = str(j.get('stronger', '')).strip().upper().strip('"')
    w = {'A': 'A', 'B': 'B', '1': 'A', '2': 'B'}.get(w)
    if w is None:
        return None
    out = dict(j, stronger=w)
    sc = j.get('scores')
    if isinstance(sc, dict):
        out['scores'] = {{'1': 'A', '2': 'B'}.get(str(k).strip().upper(), str(k).strip().upper()): v for k, v in sc.items()}
    return out


def balanced_sides(n):
    """Which side ours sits on for n reads of one (opponent, family) cell: half A, half B (one more of a random side if n is odd), OS-shuffled."""
    sides = ['A', 'B'] * (n // 2) + ([_RNG.choice('AB')] if n % 2 else [])
    _RNG.shuffle(sides)
    return sides


class DuplicatePrompt(ValueError):
    """Two reads of one test were sent the same prompt bytes: they are one read, not two."""


def hash_prompt(prompt):
    """The same short hash `build` puts in meta['prompt_sha1'], for prompts built outside `build` (packet files plus `with_nonce`)."""
    return hashlib.sha1(prompt.encode('utf-8')).hexdigest()[:12]


def store_read(reads, read, prompt=None):
    """Append one judge read to the test's list of reads, refusing a repeat of an earlier prompt.
    Every stored read carries prompt_sha1 (taken from the read, else computed from `prompt`). A read with no hash, or whose hash is already
    on an earlier read of the same test, raises and is NOT stored. A result gate that rechecks the hashes refuses the same verdicts later."""
    h = str(read.get('prompt_sha1') or '').strip().lower()
    if not h and prompt is not None:
        h = hash_prompt(prompt)
    if not h:
        raise ValueError('read has no prompt_sha1: pass the meta from build() or the prompt text')
    if any(str(r.get('prompt_sha1') or '').strip().lower() == h for r in reads):
        raise DuplicatePrompt(f'prompt_sha1 {h} already stored for this test: a repeat read must differ in nonce, labels or order, and is not stored')
    reads.append(dict(read, prompt_sha1=h))
    return reads


def parse(txt):
    m = re.search(r'\{.*\}', txt or '', re.S)
    try:
        return json.loads(m.group(0)) if m else None
    except Exception:
        return None
