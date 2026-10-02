#!/usr/bin/env python3
"""Build the Zenodo archive for Phantom Vision Lab, byte-reproducibly.

    python tools/build_zenodo_package.py --out zenodo/phantom-vision-lab-v1.0.0.zip --verify

Determinism requires three things, all of which are easy to get wrong:

  fixed mtimes       every zip entry is stamped with a constant, never the source
                     file's mtime, which changes on every copy
  sorted entries     a fixed traversal order, not filesystem order
  fixed mode bits    0o644 written explicitly, so the archive does not encode the
                     building machine's umask

Verified by building twice and comparing digests. Zenodo files are immutable
after publication, so there is no way to check afterwards whether what was
uploaded is what was intended. The digest printed here is what to compare against
the file Zenodo reports.

Excluded: .git, __pycache__, .pytest_cache, and data/ -- the last holds 35 MB of
runtime experiment output that is git-ignored, regenerable from seeds, and not
needed to run or verify anything here.
"""

from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: 1980-01-01, the earliest a zip entry can represent.
FIXED_DATE = (1980, 1, 1, 0, 0, 0)

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv",
                "build", "dist", "data", ".ruff_cache", ".mypy_cache"}
EXCLUDE_SUFFIX = {".pyc", ".pyo", ".zip", ".exe", ".spec"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def collect() -> list[Path]:
    found = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.suffix.lower() in EXCLUDE_SUFFIX:
            continue
        if not path.is_file():
            continue
        found.append(path)
    # Sort on the POSIX form so Windows and Linux builds agree.
    return sorted(found, key=lambda p: p.relative_to(ROOT).as_posix())


def build(out: Path) -> tuple[int, int]:
    files = collect()
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(filename=rel, date_time=FIXED_DATE)
            info.external_attr = (0o644 & 0xFFFF) << 16
            info.create_system = 3  # Unix, so the attr above is honoured
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, path.read_bytes())
    return len(files), out.stat().st_size


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    out = Path(args.out).resolve()
    count, size = build(out)
    digest = sha256_file(out)
    print(f"files   : {count}")
    print(f"bytes   : {size:,}")
    print(f"sha256  : {digest}")
    print(f"output  : {out}")

    if args.verify:
        probe = out.with_suffix(".probe.zip")
        build(probe)
        probe_digest = sha256_file(probe)
        probe.unlink()
        if probe_digest == digest:
            print("\nARCHIVE VERIFIED: two independent builds are byte-identical")
            return 0
        print(f"\nARCHIVE NOT REPRODUCIBLE: {digest} != {probe_digest}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
