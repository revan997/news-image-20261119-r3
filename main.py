"""Entrypoint: draw the front page of THE GLOBAL HERALD for Thursday
19 November 2026 and write it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).

Standard library only. The program runs twice and both runs must write the
same bytes, so the drawing in draw.py is fully deterministic.
"""

import hashlib
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import draw

MAX_BYTES = 1048576
EXPECT_W, EXPECT_H = 1024, 1024


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")

    draw.render(path)

    with open(path, "rb") as fh:
        data = fh.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("entry.png: bad PNG magic", file=sys.stderr)
        return 1
    if len(data) > MAX_BYTES:
        print("entry.png: %d bytes exceeds %d" % (len(data), MAX_BYTES),
              file=sys.stderr)
        return 1
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECT_W, EXPECT_H):
        print("entry.png: %dx%d, expected %dx%d"
              % (width, height, EXPECT_W, EXPECT_H), file=sys.stderr)
        return 1
    print("entry.png: %d bytes, %dx%d" % (len(data), width, height))
    print("sha256: " + hashlib.sha256(data).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
