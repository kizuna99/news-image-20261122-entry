"""Publish the committed broadsheet poster in the contest sandbox.

The poster (entry.png, drawn by render.py) is committed beside this file.
This program verifies it is a whole, well-formed PNG of exactly
1024 x 1024 and at most 1 MiB — walking every chunk and checking each
chunk's CRC — then copies it byte for byte into the output directory.
Standard library only; no network.
"""
import os
import zlib
from pathlib import Path
from struct import unpack_from

SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576


def check_png(blob):
    if not SIGNATURE == blob[:8]:
        raise ValueError("not a PNG file")
    pos = 8
    width = height = None
    seen_iend = False
    while pos < len(blob):
        if pos + 12 > len(blob):
            raise ValueError("truncated chunk")
        (length,) = unpack_from(">I", blob, pos)
        ctype = blob[pos + 4:pos + 8]
        body = blob[pos + 8:pos + 8 + length]
        if len(body) != length:
            raise ValueError("chunk body runs past the end of the file")
        (crc_stored,) = unpack_from(">I", blob, pos + 8 + length)
        if zlib.crc32(ctype + body) & 0xFFFFFFFF != crc_stored:
            raise ValueError("CRC mismatch in chunk %r" % ctype)
        if ctype == b"IHDR":
            width, height = unpack_from(">II", body, 0)
        if ctype == b"IEND":
            seen_iend = True
            pos += 12 + length
            break
        pos += 12 + length
    if not seen_iend or pos != len(blob):
        raise ValueError("file does not end cleanly with IEND")
    if (width, height) != (1024, 1024):
        raise ValueError("expected 1024 x 1024, got %s x %s" % (width, height))


def main():
    image = Path(__file__).with_name("entry.png").read_bytes()
    if not 33 <= len(image) <= MAX_BYTES:
        raise ValueError("poster must be at most 1 MiB")
    check_png(image)
    output = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    output.mkdir(parents=True, exist_ok=True)
    (output / "entry.png").write_bytes(image)


if __name__ == "__main__":
    main()
