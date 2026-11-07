#!/usr/bin/env python3
"""Generate the verse illustrations as SVG files.

    python3 tools/art/build.py            # all verses
    python3 tools/art/build.py c18 d3     # just these

Writes assets/art/hanuman-chalisa/<verse-id>.svg and records the art folder and
captions in songs/hanuman-chalisa.json (under "art").
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

from lib import Scene  # noqa: E402
from scenes import SCENES  # noqa: E402

SONG = "hanuman-chalisa"
OUT = os.path.join(ROOT, "assets", "art", SONG)
SONG_JSON = os.path.join(ROOT, "songs", SONG + ".json")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def main(ids):
    os.makedirs(OUT, exist_ok=True)
    song = json.load(open(SONG_JSON, encoding="utf-8"))
    verse_ids = [v["id"] for v in song["verses"]]
    missing = [v for v in verse_ids if v not in SCENES]
    if missing:
        print("no scene for:", ", ".join(missing))
    for vid in ids or verse_ids:
        if vid not in SCENES:
            continue
        caption, fn = SCENES[vid]
        S = Scene(vid)
        fn(S)
        with open(os.path.join(OUT, vid + ".svg"), "w", encoding="utf-8") as fh:
            fh.write(S.svg(esc(caption)))
    song["art"] = {
        "path": f"assets/art/{SONG}/",
        "credit": "Illustrations drawn in code (SVG) for this site",
        "captions": {vid: SCENES[vid][0] for vid in verse_ids if vid in SCENES},
    }
    with open(SONG_JSON, "w", encoding="utf-8") as fh:
        json.dump(song, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print(f"✓ {len(ids or verse_ids)} illustrations → {os.path.relpath(OUT, ROOT)} ({total // 1024} KB total)")


if __name__ == "__main__":
    main(sys.argv[1:])
