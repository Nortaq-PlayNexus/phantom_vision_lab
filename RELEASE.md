# Phantom Vision Lab — release record

## Verified state at time of writing

| | |
|---|---|
| GitHub | `Nortaq-PlayNexus/phantom_vision_lab`, public. Default branch `main` |
| CI | green, 5 jobs: pytest on Python 3.12 / 3.13 / 3.14, cross-process determinism, documentation-consistency. Last green run 2026-10-05 on `49e600c` |
| Test suite | **36 passing**, up from 28, up from 25 |
| Pattern types | **16**, not 15 |
| Cross-process determinism | **verified** — all 16 byte-identical across 3 fresh interpreters, on a clean Linux checkout |
| Published version | **2.0.1** |
| Version DOI | `10.5281/zenodo.23229095` |
| Concept DOI | `10.5281/zenodo.23112115` |
| Published archive | `phantom-vision-lab-v2.0.1.zip`, 99,211 bytes, md5 `4dcc450aee7fb7c04f543bb8ebdfcf7f` |
| Licence | MIT, with an explicit scientific-use restriction |

Earlier published versions, retained because Zenodo records are immutable and
each DOI still resolves: v2.0.0 `10.5281/zenodo.23123095` (archive 90,783 bytes),
v1.0.0 `10.5281/zenodo.23112116`.

> **Note on the local `phantom-vision-lab-v2.0.0.zip`:** it no longer matches the
> published v2.0.0 archive. It is 99,211 bytes, identical to the v2.0.1 archive,
> because a later build overwrote it. Only the v2.0.1 zip on disk still
> corresponds to what Zenodo actually holds. Rebuild any archive with:
>
> ```powershell
> python tools/build_zenodo_package.py --out zenodo/phantom-vision-lab-v2.0.1.zip --verify
> ```

The archive is byte-reproducible. Two independent builds produce an identical
digest, which matters because Zenodo files are immutable after publication —
there is no way to check afterwards whether what was uploaded is what was
intended.

## Publication status

**Published, twice over.** v2.0.0 on 2026-10-03, v2.0.1 on 2026-10-08. The DOI
is recorded in `zenodo/metadata.json`, `CITATION.cff`, `README.md` and this file.

**Any change after publication must be a new version (new version DOI, same
concept DOI), never an edit.**

### Outstanding: one immutable-record defect

The published v2.0.1 record's `related_identifiers` names

    https://github.com/Nortaq-PlayNexus/phantom-vision-lab

which does not exist. The real repository is

    https://github.com/Nortaq-PlayNexus/phantom_vision_lab

(underscores). The same typo is in the v2.0.0 record and in the published
description. It cannot be edited in place. `zenodo/metadata.json` now carries the
correct identifier, so depositing **v2.0.2** from this tree would repair it — and
would also repair a second error in the published description, which claims
"28 passing" where both published archives contain 36 tests.

That deposit has **not** been made: no Zenodo API token is present in this
environment.

## What was wrong before this release

Full account in `docs/RELEASE_AUDIT.md`. Summary:

1. **"Blind Experiment Mode: Anonymous condition IDs supported"** — false. The
   string `blind` appears nowhere in the application source. The feature was
   absent at every layer, not merely unenforced in the UI as the project's own
   earlier audit had suggested.
2. **"15 pattern types"**, stated twice — there are 16. The same sentence listed
   16, contradicting itself in a single line.
3. **No LICENSE file.** The `## License` section contained a disclaimer, not a
   licence, so default copyright applied and nobody could lawfully redistribute
   it.
4. **An interpretation table for the divergence score**, reading `0.5+` as
   "significant differences in interpretation", with no empirical basis anywhere
   in the repository.

## What was checked and found correct

- Determinism genuinely holds, across processes and platforms.
- The prior scientific-limitations section was accurate and has been kept.
- Data handling is clean; no credentials anywhere in the tree.

## What this software does not claim

**Nothing about consciousness.** No neural network is loaded. Metrics come from
classical computer-vision image analysis, and *perception* is a metaphor for
output-structure analysis.

The divergence score self-normalises — its denominator is an embedding distance
built from the same components as its numerator — so it is bounded by
construction. No threshold in this software has been empirically established.
Use it to rank perturbations against one another on a single pipeline, not to
assert that an effect occurred.

## Related

- `10.5281/zenodo.23229094` — the AI-consciousness indicator battery, v3.0.3
  (concept `10.5281/zenodo.23101902`). Unrelated work; neither supersedes the
  other.
- `10.5281/zenodo.23229093` — ScientificDiscoveryLab, v2.0.1
  (concept `10.5281/zenodo.23109116`).
