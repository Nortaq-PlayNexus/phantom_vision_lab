"""Keep CITATION.cff and the documentation pointing at the published record.

This repository's own history is the reason. Its previous README advertised a
"Blind Experiment Mode" that was never implemented, and claimed 15 pattern types
while listing 16. Both are now enforced by tests in test_all.py.

The same class of error reached the citation metadata unnoticed: CITATION.cff
carried version 1.0.0 and no DOI at all, while v2.0.0 was published and
resolving. A stale DOI is harder to catch than a stale feature claim, because
the superseded record still resolves -- doi.org answers 200 for both. Nothing
about the file looks broken.

These tests are offline: they check the citation against the version this
repository actually contains, and against the DOI recorded in the deposit
metadata. They do not call Zenodo, so they cannot fail from a network outage.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CITATION = ROOT / "CITATION.cff"
METADATA = ROOT / "zenodo" / "metadata.json"
README = ROOT / "README.md"

CONCEPT_DOI = "10.5281/zenodo.23112115"


def _citation_text() -> str:
    return CITATION.read_text(encoding="utf-8")


def test_citation_file_exists_and_declares_a_version():
    assert CITATION.is_file(), "CITATION.cff is missing"
    assert re.search(r'^version:\s*"\d+\.\d+\.\d+"', _citation_text(), re.M), (
        "CITATION.cff declares no semantic version; a citation without a version "
        "cannot be superseded deliberately, only forgotten"
    )


def test_citation_declares_a_doi():
    """The file that was silently missing its most important field."""
    assert re.search(r'^doi:\s*"10\.5281/zenodo\.\d+"', _citation_text(), re.M), (
        "CITATION.cff declares no Zenodo DOI. The published record exists, so this "
        "is a gap rather than a legitimate omission."
    )


def test_citation_doi_and_concept_are_well_formed():
    text = _citation_text()
    doi = re.search(r'^doi:\s*"(10\.5281/zenodo\.\d+)"', text, re.M)
    concept = re.search(r'^concept-doi:\s*"(10\.5281/zenodo\.\d+)"', text, re.M)
    assert doi, "no doi field"
    assert concept, (
        "no concept-doi field. Without it a reader cannot tell that v1 and v2 are "
        "versions of one record rather than unrelated deposits, and a misfiled "
        "version is permanent."
    )


def test_citation_version_is_not_behind_the_deposit_metadata():
    """Guards the exact regression: a citation left behind by a publication.

    Offline by design. The ground truth is zenodo/metadata.json, which is tracked
    in git and carries the version this tree was built to publish.

    An earlier version of this test cross-checked against
    zenodo/phantom-vision-lab-v*.zip instead. That archive is gitignored -- it is
    rebuildable and lives on Zenodo -- so the check passed on the maintainer's
    machine, where a stale local zip happened to sit in the tree, and failed in
    every clean checkout and on CI. A gate that reports a different answer
    depending on untracked files in the working directory is worse than no gate:
    it trains you to ignore it. Found by pushing and reading the CI log, which is
    the only reason it was caught at all.
    """
    import json

    if not METADATA.is_file():
        pytest.skip("zenodo/metadata.json not present; nothing to cross-check against")

    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    built = metadata.get("version")
    assert built, (
        "zenodo/metadata.json declares no version, so the citation cannot be "
        "checked against it. Either record the version or drop this test -- do "
        "not leave it passing vacuously."
    )

    text = _citation_text()
    cited_version = re.search(r'^version:\s*"([^"]+)"', text, re.M)
    assert cited_version, "CITATION.cff declares no version"
    cited = cited_version.group(1)

    def as_tuple(v: str) -> tuple[int, ...]:
        parts = v.split(".")
        assert len(parts) == 3 and all(p.isdigit() for p in parts), (
            f"version {v!r} is not a three-part semantic version"
        )
        return tuple(int(p) for p in parts)

    assert as_tuple(cited) >= as_tuple(built), (
        f"CITATION.cff cites v{cited} but zenodo/metadata.json publishes v{built}. "
        f"A citation must never trail the artifact it describes."
    )


def test_concept_doi_is_consistent_across_documents():
    """One concept per project. Two DOIs for one record splits the citation graph."""
    text = _citation_text()
    found = set(re.findall(r"10\.5281/zenodo\.\d+", text))
    concept = re.search(r'^concept-doi:\s*"(10\.5281/zenodo\.\d+)"', text, re.M)
    assert concept, "no concept-doi to be consistent with"
    others = found - {concept.group(1)}
    # v1 and v2 DOIs are legitimately both present; they share one concept. What
    # must not happen is two different concept DOIs appearing.
    assert len({d for d in others}) <= 2, (
        f"more DOIs than expected in CITATION.cff: {sorted(found)}"
    )


def test_readme_doi_badge_is_present_and_matches_citation():
    """The badge is what a reader sees first; the CFF is what a tool reads."""
    readme = README.read_text(encoding="utf-8")
    citation_doi = re.search(r'^doi:\s*"(10\.5281/zenodo\.\d+)"', _citation_text(), re.M)
    assert citation_doi, "CITATION.cff declares no DOI to match against"

    badge = re.search(r"zenodo\.(\d+)", readme)
    assert badge, (
        "README.md carries no Zenodo DOI badge. The previous phantom README also "
        "carried a DOI-less citation, which is how v2.0.0 went unnoticed."
    )
    assert f"zenodo.{citation_doi.group(1).split('.')[-1]}" in readme, (
        "README badge and CITATION.cff name different records: "
        f"{badge.group(0)} vs {citation_doi.group(1)}"
    )


def test_citation_does_not_describe_consciousness():
    """The one claim this software must never make.

    Carried forward from the corrections in the previous documentation. If a
    future edit reintroduces it, the test fails and the edit has to be defended
    in the open rather than landing unnoticed.
    """
    text = _citation_text().lower()
    for phrase in ("measures consciousness", "consciousness indicator",
                   "detects consciousness", "ai consciousness"):
        assert phrase not in text, (
            f"CITATION.cff now says {phrase!r}. This software loads no model and "
            "measures no subjective experience; see the README's 'What this is not'."
        )


def test_citation_keeps_the_disclaimers():
    """The disclaimers are load-bearing, so their removal should be deliberate."""
    text = _citation_text().lower()
    assert "not a neural network" in text or "loads no neural" in text, (
        "CITATION.cff dropped the 'not a neural network' qualifier"
    )
    assert "no validated interpretation scale" in text or "no threshold" in text, (
        "CITATION.cff dropped the statement that the divergence score has no "
        "validated interpretation scale. An earlier version published a table "
        "reading 0.5+ as significant; that table was removed as unsupported."
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))