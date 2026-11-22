"""Contest entry point for The World Brief, Sunday 22 November 2026.

The artwork ships in this repository as entry.png, already rendered. The
harness expects the program to place that exact file into the output
directory, so this module first proves the committed bytes form a whole,
undamaged PNG of the required shape and only then publishes them.
"""

import os
import zlib
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SIZE_LIMIT = 1_048_576  # the contest caps the image at 1 MiB
EXPECTED_EDGE = 1024    # and at 1024 x 1024 pixels


def check_png(blob):
    """Walk the chunk list; raise ValueError on any structural defect."""
    if len(blob) > SIZE_LIMIT:
        raise ValueError("poster exceeds the 1 MiB contest limit")
    if not blob.startswith(PNG_MAGIC):
        raise ValueError("poster is missing the PNG signature")

    pos = len(PNG_MAGIC)
    seen_iend = False
    while pos < len(blob):
        if pos + 12 > len(blob):
            raise ValueError("truncated chunk header")
        length = int.from_bytes(blob[pos:pos + 4], "big")
        kind = blob[pos + 4:pos + 8]
        body = blob[pos + 8:pos + 8 + length]
        if len(body) != length or pos + 12 + length > len(blob):
            raise ValueError(f"chunk {kind!r} runs past the end of file")
        stored_crc = int.from_bytes(
            blob[pos + 8 + length:pos + 12 + length], "big")
        if zlib.crc32(kind + body) & 0xFFFFFFFF != stored_crc:
            raise ValueError(f"chunk {kind!r} fails its CRC check")

        if kind == b"IHDR":
            width = int.from_bytes(body[0:4], "big")
            height = int.from_bytes(body[4:8], "big")
            if (width, height) != (EXPECTED_EDGE, EXPECTED_EDGE):
                raise ValueError(f"poster is {width}x{height}, not 1024x1024")
        elif kind == b"IEND":
            seen_iend = True
            pos += 12 + length
            break
        pos += 12 + length

    if not seen_iend:
        raise ValueError("poster has no IEND chunk")
    if pos != len(blob):
        raise ValueError("trailing bytes after IEND")


def publish():
    poster = Path(__file__).resolve().with_name("entry.png")
    blob = poster.read_bytes()
    check_png(blob)
    target_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "entry.png").write_bytes(blob)


if __name__ == "__main__":
    publish()
