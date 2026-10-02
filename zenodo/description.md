# Phantom Vision Lab — a computational instrument for perturbing an image-analysis pipeline and measuring how its output changes

**A deterministic structured-light stimulus generator paired with a fixed classical computer-vision pipeline, used to measure how much the pipeline's own output moves when 11 computational parameters are perturbed.**

> **This is classical computer vision, not a neural network.** No model is loaded,
> downloaded, or bundled. The word *perception* in this project is a metaphor for
> output-structure analysis. The software cannot measure consciousness, does not
> attempt to, and makes no claim to.

---

## What it is

Generate 16 deterministic structured-light pattern types from a seed. Run each
through a fixed image-analysis pipeline twice — once unmodified, once perturbed —
and report how much the analysis output changed.

```
seed ──► stimulus generator ──► vision pipeline ──► metrics
              │                       ▲                │
              │                  altered_state        │
              └───────────────────────┴──────► divergence
```

The point is the perturbation. If 11 knobs move and the output does not, that is a
finding about the pipeline. If it moves a lot, that is also a finding — about a
box of image filters.

## What it is not

Stated first because everything else is easy to misread.

- **Not a neural network.** Metrics come from edge detection, symmetry analysis,
  contour finding and clustering. There is no model.
- **Not consciousness.** Nothing here measures subjective experience.
- **Not a psychedelic model.** It does not reproduce a biological altered state.
- **Not a validated instrument.** The divergence score is an algorithmic
  construct, not a validated psychometric measure.
- **Not blind.** No blinding exists at any layer. An earlier version of this
  README claimed otherwise; see the corrections section.

## The divergence score, stated honestly

```python
score = (geometry_diff + novelty_diff + uncertainty_diff) / (3 * max(1, embedding_distance))
```

Two properties matter more than the formula:

1. **It self-normalises.** The denominator is an embedding distance computed from
   the same metric components that appear in the numerator. Raising the
   perturbation moves both. The ratio is bounded by construction, and that bound
   does work a reader would otherwise attribute to the stimulus.
2. **It has no validated interpretation scale.** A previous version of this
   README published a table reading `0.5+` as "significant differences in
   interpretation". **That table was removed.** No experiment in this repository
   establishes 0.5 as a threshold, because no data capable of doing so was ever
   collected.

Use the score to *rank* perturbations against each other on one pipeline. It does
not support a claim that an effect occurred.

## Reproducibility

| | |
|---|---|
| Pattern types | 16, all deterministic from a seed |
| Cross-process determinism | **verified** — all 16 byte-identical across 3 fresh interpreters |
| Test suite | 28 passing |
| Python | 3.12, 3.13, 3.14 in CI |
| PySide6 in CI | deliberately not installed; no test imports it |

Determinism is verified across *processes*, not merely within one. The project's
original test called the generator twice inside a single interpreter, which cannot
detect a module-level RNG, a lazily-initialised global, or a dependence on
`PYTHONHASHSEED` — all of which look perfectly deterministic in-process and drift
between runs. The check runs in CI on a clean checkout on a different platform,
because a determinism claim that holds only on the author's machine is not a
determinism claim.

## Three false claims, found and corrected before first release

Recorded rather than quietly fixed. Anyone who read the previous documentation was
misled by it. Full account in `docs/RELEASE_AUDIT.md`.

| Claim | Reality |
|---|---|
| "Blind Experiment Mode: Anonymous condition IDs supported" | **False.** The string `blind` appears nowhere in the application source. Not unenforced in the UI — absent at every layer. |
| "15 pattern types" (stated twice) | **16.** The same sentence then listed 16, contradicting itself in one line. |
| `## License` containing "Virtual simulation only." | Not a licence. The project had **no LICENSE file at all.** MIT added. |

A fourth claim was removed on the same grounds: an interpretation table for the
divergence score, reading `0.5+` as "significant differences", with no empirical
basis anywhere in the repository.

The project's own `docs/FINAL_AUDIT.md` had flagged the blinding claim, but
described it as "infrastructure is designed but not enforced in the UI layer".
That is **more generous than the evidence supports** — a grep for `blind` returns
nothing, so there is no infrastructure either.

Two of these are now enforced mechanically:

- `tools/check_docs_match_source.py` fails if the README re-asserts a capability
  the source lacks
- `tools/negative_test_doc_check.py` proves that check can still fail

The negative test matters more than it looks. The first version of the
documentation check excluded the "What this is not" section along with the
corrections table. That heading sits near the top of the document, so the
exclusion truncated it to its opening paragraph — and the check reported PASS
while verifying almost nothing. The negative test caught it by asking whether the
check still fires.

## What was checked and found correct

Not everything was wrong, and saying so matters for calibration.

- Determinism genuinely holds, across processes and platforms.
- The scientific-limitations section of the old README was **accurate and
  already honest**. It was kept, not softened.
- Data handling is clean: 35 MB of runtime output in `data/` is git-ignored and
  untracked.
- No credentials anywhere in the tree.

## Limitations

- **Single operator, unblinded.** No second observer, no randomisation. Expectancy
  effects are uncontrolled.
- **Statistics without hypotheses.** The engine computes t-tests and effect sizes,
  but no preregistered hypothesis is tested anywhere in it.
- **No causality.** The design cannot show that a specific parameter, rather than
  the perturbation as a whole, produced a given change.
- **Synthetic stimuli only.** Nothing here is shown to generalise to natural
  images.
- **No validated metrics.** Every score is derived from image features computed by
  this project's own code. There is no independent implementation to check it
  against.

## Use

```bash
pip install -r requirements.txt
python main.py            # GUI
```

Headless:

```bash
python run_experiment.py experiment --pattern fractal --preset "HIGH PREDICTION ERROR" --seed 999
python run_experiment.py batch --iterations 20 --presets "BASELINE,MAXIMUM EXPLORATION"
```

## Verification

```bash
python -m pytest tests/ -q                    # 28 tests
python tools/verify_determinism.py            # cross-process digests
python tools/check_docs_match_source.py       # README vs source
python tools/negative_test_doc_check.py       # proves the check still fails
```

## Files

| Path | Contents |
|---|---|
| `stimuli/generator.py` | 16 pattern types, seed-based determinism |
| `altered_state/engine.py` | 11 parameters, 6 presets, metric transforms |
| `vision/__init__.py` | the classical CV analysis pipeline |
| `analysis/metrics.py` | `compute_perception_divergence` |
| `experiments/engine.py` | baseline/altered orchestration, replay |
| `storage/`, `reports/` | persistence; JSON, CSV, HTML, Markdown export |
| `ui/` | PySide6 desktop interface |
| `tests/test_all.py` | 28 tests |
| `docs/FINAL_AUDIT.md` | feature audit and interpretation guide |
| `docs/RELEASE_AUDIT.md` | what was wrong before release, and what changed |
| `tools/` | reproducibility and documentation-consistency checks |

## Licence

MIT — see `LICENSE`. The licence includes an explicit scientific-use restriction:
you may not present this software's output as evidence about consciousness,
subjective experience, psychedelic phenomenology, or neural-network internal
states. It cannot support such a claim.
