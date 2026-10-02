#!/usr/bin/env python3
"""Negative-test the documentation check.

    python tools/negative_test_doc_check.py

`tools/check_docs_match_source.py` is only worth running if it can fail. This
injects each retracted claim back into the README and asserts the check catches
it. A check that silently stops detecting is worse than no check, because it is
read as a green light.

This file exists because that exact failure happened during preparation: the
first version of the check excluded the 'What this is not' section along with the
corrections table. That heading appears near the top of the README, so the
exclusion truncated the document to its opening paragraph and the check became
nearly vacuous -- while still reporting PASS. It was only caught because this
negative test existed to ask the question.

Exits 0 when every injected bad claim is detected and the corrections table is
correctly ignored.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from check_docs_match_source import (  # noqa: E402
    README,
    RETRACTION_HEADING,
    check,
    descriptive_text,
    pattern_type_count,
)


def inject(text: str, addition: str) -> str:
    """Insert into the descriptive region: before the retraction heading."""
    cut = text.find(RETRACTION_HEADING)
    if cut == -1:
        return text + addition
    return text[:cut] + addition + "\n" + text[cut:]


def main() -> int:
    readme = README.read_text(encoding="utf-8")
    n_types = pattern_type_count()

    body = descriptive_text(readme)
    print(f"pattern types in source : {n_types}")
    print(f"descriptive region      : {len(body)} of {len(readme)} chars")
    if len(body) < len(readme) * 0.5:
        print(
            f"\nBROKEN: the descriptive region is only {len(body) / len(readme):.0%} "
            "of the README. The check has probably been truncated into vacuity, "
            "which is the exact bug this script exists to catch."
        )
        return 1

    baseline = check(readme, n_types)
    if baseline:
        print("\nBROKEN: the current README already fails the check:")
        for f in baseline:
            print(f"  - {f}")
        return 1

    cases = [
        (
            "blinding claim restored",
            inject(readme, "\n### Features\n- **Blind Experiment Mode**: "
                           "Anonymous condition IDs supported\n"),
        ),
        (
            "anonymous condition id phrasing",
            inject(readme, "\nAnonymous condition IDs are supported for every run.\n"),
        ),
        (
            "wrong pattern count",
            readme.replace("16 pattern types", "15 pattern types"),
        ),
        (
            "divergence threshold restored",
            inject(readme, "\n| Range | Meaning |\n|---|---|\n"
                           "| 0.5+ | Significant differences in interpretation |\n"),
        ),
        (
            "validated-psychometric phrasing",
            inject(readme, "\nThe divergence score is a validated psychometric instrument.\n"),
        ),
    ]

    print("\ninjecting retracted claims; each must be detected:")
    broken = 0
    for label, text in cases:
        detected = bool(check(text, n_types))
        print(f"  {label:<34} detected={detected}  {'OK' if detected else 'BROKEN'}")
        if not detected:
            broken += 1

    # The corrections table quotes every one of these on purpose. Reading it as a
    # current claim would make the check flag its own audit trail.
    table_present = RETRACTION_HEADING in readme
    table_clean = not check(readme, n_types)
    print(f"\n  corrections table quotes retracted claims without tripping: "
          f"{'OK' if table_present and table_clean else 'BROKEN'}")
    if not (table_present and table_clean):
        broken += 1

    if broken:
        print(f"\n{broken} check(s) cannot detect the defect they exist to catch")
        return 1

    print("\nOK: every injected claim is detected, and the corrections table is ignored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
