#!/usr/bin/env python3
"""Verify stimulus determinism across fresh interpreter processes.

    python tools/verify_determinism.py

Generates every pattern type in three separate interpreters and compares
SHA-256 digests of the raw pixel bytes.

Why subprocesses
----------------
The project's own `test_lattice_determinism` calls the generator twice inside one
process. That cannot detect the usual real causes of drift:

  * a module-level RNG seeded once at import
  * a lazily-initialised global cache
  * anything depending on PYTHONHASHSEED or dict iteration order

All of those are perfectly deterministic within a process and change between
runs. A determinism claim tested only in-process is not tested.

Run in CI on a different platform and a clean checkout, because a determinism
claim that holds only on the author's machine is not a claim.

Exits 0 if all pattern types are byte-identical across all three runs.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from stimuli.generator import StimulusGenerator, StimulusConfig  # noqa: E402

CHILD = """
import hashlib, sys
import numpy as np
sys.path.insert(0, {root!r})
from stimuli.generator import StimulusGenerator, StimulusConfig

gen = StimulusGenerator()
digests = []
for pattern in StimulusGenerator.PATTERN_TYPES:
    image, _ = gen.generate(StimulusConfig(seed=42, pattern_type=pattern))
    digests.append(
        hashlib.sha256(np.ascontiguousarray(image).tobytes()).hexdigest()
    )
print("|".join(digests))
"""


def main() -> int:
    patterns = list(StimulusGenerator.PATTERN_TYPES)
    print(f"pattern types: {len(patterns)}")
    print(f"seed         : 42")
    print(f"interpreter  : {sys.executable}")

    runs = []
    for i in range(3):
        proc = subprocess.run(
            [sys.executable, "-c", CHILD.format(root=str(ROOT))],
            capture_output=True, text=True, timeout=900, cwd=str(ROOT),
        )
        if proc.returncode != 0:
            print(f"\nsubprocess {i + 1} failed:\n{proc.stderr[-3000:]}")
            return 1
        runs.append(proc.stdout.strip())

    unique = set(runs)
    if len(unique) != 1:
        print(f"\nNOT deterministic: {len(unique)} distinct outputs across 3 processes")
        first = runs[0].split("|")
        for idx, run in enumerate(runs[1:], 2):
            for pattern, a, b in zip(patterns, first, run.split("|")):
                if a != b:
                    print(f"  run 1 vs run {idx}: {pattern}")
                    print(f"    {a[:32]}")
                    print(f"    {b[:32]}")
        return 1

    digests = unique.pop().split("|")
    if len(digests) != len(patterns):
        print(f"\nexpected {len(patterns)} digests, got {len(digests)}")
        return 1

    print()
    for pattern, digest in zip(patterns, digests):
        print(f"  {pattern:<22} {digest[:32]}")
    print(f"\nOK: all {len(patterns)} pattern types byte-identical across 3 fresh interpreters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
