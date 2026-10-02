#!/usr/bin/env python3
"""Check that the README's claims still match the source.

    python tools/check_docs_match_source.py

Run in CI. Exits 0 when the README is consistent with the code, 1 otherwise.

Why this exists
---------------
Three of the four defects found in docs/RELEASE_AUDIT.md were the same failure:
the README described a capability the source did not have.

  "Blind Experiment Mode: Anonymous condition IDs supported" -- the string
  `blind` appears nowhere in the source
  "15 pattern types" -- there are 16, and the same sentence listed 16
  a `## License` section holding a disclaimer instead of a licence

And one number had an interpretation table with no empirical basis:

  | 0.5+ | Significant differences in interpretation |

Nothing in the repository establishes 0.5 as a threshold, and the score is
self-normalising by a distance built from the same components as its numerator.

A README that overstates what the code does is the specific failure mode of a
project like this one, so it is checked mechanically rather than trusted not to
recur.

Scope note
----------
This checks the descriptive region of the README only. The
"Corrections to earlier documentation" section quotes the retracted claims on
purpose, in order to correct them; reading that as a current claim would make the
check flag its own audit trail, which would be as useless as a gate that cannot
fail.

`tools/negative_test_doc_check.py` injects each bad claim and asserts this script
detects it, so the check cannot silently stop working.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

RETRACTION_HEADING = "## Corrections to earlier documentation"

BLINDING_PATTERNS = (
    r"blind experiment mode",
    r"anonymous condition id",
    r"double[- ]blind",
)

#: Phrases that would reinstate an interpretation scale for the divergence score.
SCALE_PATTERNS = (
    r"significant differences? in interpretation",
    r"significant perceptual difference",
    r"validated psychometric",
)

#: Words that turn a match into a denial. The README legitimately says "not a
#: validated psychometric instrument"; that is the opposite of the claim the
#: check is looking for, and without this the check flagged its own correct text.
NEGATIONS = (
    "not a", "not an", "is not", "isn't", "no ", "never", "cannot",
    "without", "rather than", "instead of", "does not", "doesn't",
)


def descriptive_text(readme: str) -> str:
    cut = readme.find(RETRACTION_HEADING)
    return readme if cut == -1 else readme[:cut]


def pattern_type_count() -> int:
    sys.path.insert(0, str(ROOT))
    from stimuli.generator import StimulusGenerator

    return len(StimulusGenerator.PATTERN_TYPES)


def check(readme: str, n_types: int) -> list[str]:
    failures: list[str] = []
    body = descriptive_text(readme)

    for pattern in BLINDING_PATTERNS:
        if re.search(pattern, body, re.I):
            failures.append(
                f"README advertises a blinding feature (matched /{pattern}/) but no "
                "blinding exists in the source. If it was added, implement it, test "
                "it, then update this check."
            )

    for m in re.findall(r"(\d+)\s+pattern types", body):
        if int(m) != n_types:
            failures.append(
                f"README says {m} pattern types; stimuli/generator.py has {n_types}"
            )

    for pattern in SCALE_PATTERNS:
        for match in re.finditer(pattern, body, re.I):
            # Look back a short window for a negator. 60 characters covers the
            # constructions this README actually uses without swallowing a whole
            # sentence and missing a real claim elsewhere in it.
            window = body[max(0, match.start() - 60):match.start()].lower()
            if any(neg in window for neg in NEGATIONS):
                continue
            failures.append(
                f"README reintroduces an interpretation scale for the divergence "
                f"score (matched /{pattern}/ at offset {match.start()}). No "
                "threshold in this software has been empirically established."
            )

    return failures


def main() -> int:
    if not README.is_file():
        print(f"ERROR: {README} not found", file=sys.stderr)
        return 1

    readme = README.read_text(encoding="utf-8")
    n_types = pattern_type_count()

    body = descriptive_text(readme)
    print(f"pattern types in source : {n_types}")
    print(f"descriptive region      : {len(body)} of {len(readme)} chars")

    failures = check(readme, n_types)
    if failures:
        print("\nDOCUMENTATION DOES NOT MATCH SOURCE")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("\nOK: README claims are consistent with the source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
