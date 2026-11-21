#!/usr/bin/env python3
"""Velmara — The Poster for a Place That Isn't There.

Entry program for the make.fun competition
"the-poster-for-a-place-that-i-2-20261121-0539".

The poster itself is a vintage travel poster for Velmara, a fictional
archipelago of floating islands above a sea of clouds, drawn by
poster_gen.py (same repository) with Pillow and shipped here as
poster.png. This entrypoint needs no network and no third-party
library: it copies the finished poster to /output/entry.png and
checks the copy is a whole 1024x1024 PNG before it finishes.

Run:  python3 main.py
"""
import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "poster.png")
DEST_DIR = "/output"
DEST = os.path.join(DEST_DIR, "entry.png")

EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1_048_576


def read_png_size(path):
    """Return (width, height) from a PNG's IHDR chunk, stdlib only."""
    with open(path, "rb") as fh:
        header = fh.read(33)
    if len(header) < 33 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file: %s" % path)
    if header[12:16] != b"IHDR":
        raise ValueError("PNG has no IHDR chunk: %s" % path)
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def main():
    if not os.path.isfile(SOURCE):
        print("poster.png is missing from the repository", file=sys.stderr)
        return 1
    os.makedirs(DEST_DIR, exist_ok=True)
    shutil.copyfile(SOURCE, DEST)
    # The copy must be byte-for-byte the poster this repository ships,
    # so a truncated or corrupted copy can never pass the checks below.
    with open(SOURCE, "rb") as fh:
        source_hash = hashlib.sha256(fh.read()).hexdigest()
    with open(DEST, "rb") as fh:
        dest_hash = hashlib.sha256(fh.read()).hexdigest()
    if source_hash != dest_hash:
        print("entry.png does not match the shipped poster.png",
              file=sys.stderr)
        return 1
    size = os.path.getsize(DEST)
    if size > MAX_BYTES:
        print("entry.png is %d bytes, over the 1 MiB cap" % size,
              file=sys.stderr)
        return 1
    width, height = read_png_size(DEST)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        print("entry.png is %dx%d, expected 1024x1024" % (width, height),
              file=sys.stderr)
        return 1
    print("wrote %s (%dx%d, %d bytes)" % (DEST, width, height, size))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
