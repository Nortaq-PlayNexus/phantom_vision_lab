# Release audit — what was wrong before publication

Found while preparing the Zenodo deposit. Recorded here rather than quietly
fixed, because anyone who read the previous README was misled by it.

## 1. The blind-experiment claim was false

**Claim** (previous README, Features section):

> **Blind Experiment Mode**: Anonymous condition IDs supported

**Reality**: the string `blind` does not appear anywhere in the source tree. Not
in the UI, not in the experiment engine, not in storage. There is no anonymous
condition identifier, no randomisation, and no concealment mechanism of any kind.

The claim was not merely unimplemented in the UI. It was absent.

`docs/FINAL_AUDIT.md` had already flagged it, but under "WHAT DOES NOT WORK" it
said the "infrastructure is designed but not enforced in the UI layer". That is
**more generous than the evidence supports**. A grep for `blind` across `*.py`
returns nothing, so there is no infrastructure either. The audit's own framing
would have let a reader conclude the feature was a UI oversight rather than
absent, and it is not.

Corrected: the feature is removed from the README entirely rather than softened,
because there is nothing to soften it from.

This matters beyond pedantry. A blinding claim is the difference between a
self-report instrument and a measurement. Publishing "blind mode supported" when
no blinding exists would have made every downstream result look better-controlled
than it was.

## 2. The pattern count was wrong, and contradicted itself in one sentence

**Claim**: "15 pattern types", stated twice — once in the feature list and once in
the project-structure listing.

**Reality**: 16. Verified by enumerating the branches on `pattern_type` in
`stimuli/generator.py`:

```
concentric, fractal, high_frequency, interference, interference_field,
kaleidoscopic, lattice, moire, morphing, noise_geometry, polygons,
radial_diffraction, recursive_corridor, rotating_grid, tunnel, warped_grid
```

The old README said 15 and then listed 16 in the same sentence. A reader counting
the list would have found the contradiction; a reader skimming would not have.

## 3. There was no licence

The `## License` section read:

> Virtual simulation only. No physical hardware is controlled.

That is a disclaimer, not a licence. It granted no permissions, imposed no
conditions, and left the repository with **no LICENSE file at all** — meaning
default copyright applied and nobody could lawfully redistribute it.

Replaced with MIT plus an explicit scientific-use restriction, because the
disclaimer that was there was trying to do a licence's job and could not.

## 4. The divergence score had a published interpretation table with no basis

**Claim** (previous README):

| Range | Meaning |
|---|---|
| 0.5+ | Significant differences in interpretation |

**Reality**: nothing in this repository establishes 0.5 as a threshold. No
experiment was run to calibrate it. `docs/FINAL_AUDIT.md` already says the score
"is an algorithmic construct, not a validated psychometric instrument" — which
directly contradicts a table calling a range "significant".

Worse, the score self-normalises:

```python
score = (geometry_diff + novelty_diff + uncertainty_diff) / (3 * max(1, embedding_distance))
```

`embedding_distance` is computed from the same metric components that appear in
the numerator. Increasing perturbation moves both. The ratio is bounded by
construction, and that bound does much of the work that a reader would attribute
to the stimulus.

Removed from the README. The score remains useful for *ranking* perturbations
against each other on one pipeline. It does not support a claim that an effect
occurred.

## What was checked and found correct

Not everything was wrong, and saying so matters for calibration.

- **Determinism holds across processes.** All 16 pattern types produce
  byte-identical output in three separate interpreter invocations. The project's
  own test only checks two calls within one process, which cannot catch a
  module-level RNG or a hash-order dependency. A new test now covers the real
  case.
- **25 tests pass** across the full suite.
- **The scientific limitations section was genuinely honest.** It already said the
  software does not establish subjective consciousness and that metrics come from
  classical CV. That material was accurate and has been kept, not softened.
- **Data handling is clean.** `data/experiments/` (35 MB of runtime output) is
  git-ignored and untracked.
- **No secrets** anywhere in the tree.

## Scope of this audit

This is an audit of *documentation against source*, plus a determinism check. It
is not a review of whether the perturbation model is scientifically useful, and it
did not attempt to validate the divergence score against any external data.

Nothing here establishes that the instrument measures anything real. It
establishes only that the documentation now matches the code.
