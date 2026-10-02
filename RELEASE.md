# Phantom Vision Lab — release record

## Verified state at time of writing

| | |
|---|---|
| GitHub | `Nortaq-PlayNexus/phantom-vision-lab`, public |
| CI | green, 5 jobs: pytest on Python 3.12 / 3.13 / 3.14, cross-process determinism, documentation-consistency |
| Test suite | **28 passing**, up from 25 |
| Pattern types | **16**, not 15 |
| Cross-process determinism | **verified** — all 16 byte-identical across 3 fresh interpreters, on a clean Linux checkout |
| Archive | `phantom-vision-lab-v1.0.0.zip`, 54 files, 73,175 bytes |
| SHA-256 | `506d0d127a7cacc7bd148787d84d807ca57cfbf94795f7b3524d605bfa5e61bc` |
| MD5 as uploaded | `4e10066e5fa4e000c92c13098d265d2c` |
| Zenodo | draft **23112116**, unsubmitted |
| DOI | none yet |
| Licence | MIT, with an explicit scientific-use restriction |

The archive is byte-reproducible. Two independent builds produce an identical
digest, which matters because Zenodo files are immutable after publication —
there is no way to check afterwards whether what was uploaded is what was
intended.

```powershell
python tools/build_zenodo_package.py --out zenodo/phantom-vision-lab-v1.0.0.zip --verify
```

## Publication status

**NOT published.** Publish at https://zenodo.org/deposit/23112116 after adding
the four subject identifiers listed in `zenodo/DEPOSIT.md` — Zenodo's deposition
API accepts that field and then silently discards it, so it must be entered in
the web form.

Then record the DOI in `zenodo/metadata.json`, `CITATION.cff`, `README.md` and
this file.

**Any change after publication must be a new version (new version DOI, same
concept DOI), never an edit.**

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

- `10.5281/zenodo.23101903` — the AI-consciousness indicator battery. Unrelated
  work; neither supersedes the other.
- `10.5281/zenodo.23109117` — ScientificDiscoveryLab.
