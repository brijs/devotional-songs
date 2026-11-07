#!/usr/bin/env python3
"""Validate song JSON files in songs/.

Usage:  python3 tools/validate.py            # validate every song in catalog.json
        python3 tools/validate.py songs/x.json

Checks
  * required top-level fields exist
  * every verse references a declared section and has unique id
  * each line's `deva` text equals its words joined by spaces (punctuation ignored)
  * each line's `roman` has the same number of tokens as `words`
    (tokens split on spaces; hyphenated compounds count as one), so the
    reader can show a per-word sung transliteration
  * audio timings (if any) refer to real verse ids and increase in order
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUNCT = re.compile(r"[।॥,.;:!?'\"“”‘’()\-–—]")
REQUIRED = ["id", "title", "language", "script", "author", "about", "sections", "verses"]


def norm(s):
    return " ".join(PUNCT.sub(" ", s).split())


def validate(path):
    errors = []
    song = json.loads(Path(path).read_text(encoding="utf-8"))
    for k in REQUIRED:
        if k not in song:
            errors.append(f"missing top-level field '{k}'")
    sections = {s["id"] for s in song.get("sections", [])}
    ids = set()
    for v in song.get("verses", []):
        vid = v.get("id", "?")
        if vid in ids:
            errors.append(f"{vid}: duplicate verse id")
        ids.add(vid)
        if v.get("section") not in sections:
            errors.append(f"{vid}: unknown section '{v.get('section')}'")
        if not v.get("meaning", {}).get("en"):
            errors.append(f"{vid}: missing English meaning")
        for i, ln in enumerate(v.get("lines", []), 1):
            words = ln.get("words", [])
            joined = " ".join(w["deva"] for w in words)
            if norm(joined) != norm(ln["deva"]):
                errors.append(f"{vid} line {i}: words '{joined}' != deva '{ln['deva']}'")
            for w in words:
                if not w.get("gloss"):
                    errors.append(f"{vid} line {i}: word '{w['deva']}' has no gloss")
            if "roman" in ln:
                rtoks = norm(ln["roman"].replace("-", "‐")).split()
                if len(rtoks) != len(words):
                    errors.append(f"{vid} line {i}: roman has {len(rtoks)} tokens, words has {len(words)}: '{ln['roman']}'")
    audio = song.get("audio") or {}
    last = -1
    order = [v["id"] for v in song.get("verses", [])]
    for vid in order:
        t = (audio.get("timings") or {}).get(vid)
        if t is None:
            continue
        if t < last:
            errors.append(f"audio timing for {vid} ({t}) is earlier than the previous verse")
        last = t
    for vid in (audio.get("timings") or {}):
        if vid not in ids:
            errors.append(f"audio timing for unknown verse '{vid}'")
    return song, errors


def main():
    paths = sys.argv[1:]
    if not paths:
        catalog = json.loads((ROOT / "songs" / "catalog.json").read_text(encoding="utf-8"))
        paths = [ROOT / "songs" / f"{s['id']}.json" for s in catalog]
    failed = False
    for p in paths:
        song, errors = validate(p)
        n = len(song.get("verses", []))
        nw = sum(len(l.get("words", [])) for v in song.get("verses", []) for l in v.get("lines", []))
        if errors:
            failed = True
            print(f"✗ {p}: {len(errors)} problem(s)")
            for e in errors:
                print("   -", e)
        else:
            print(f"✓ {p}: {n} verses, {nw} glossed words")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
