# Phantom Vision Lab

> **New to this repository, or picking up an interrupted session?**
> Read [`HANDOFF.md`](HANDOFF.md) first. It records what exists and where, the
> Zenodo API traps that cost real bugs here, the outstanding work, and the rule
> about never deleting a deposit.

**A computational instrument for perturbing an image-analysis pipeline and
measuring how its output changes.**

[![Tests](https://img.shields.io/badge/tests-28%20passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](requirements.txt)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Zenodo](https://img.shields.io/badge/zenodo-draft%2023112116-lightgrey)](zenodo/DEPOSIT.md)

> **This is classical computer vision, not a neural network.** No model is
> loaded. The "perception" it measures is OpenCV-style image analysis, and the
> word *perception* is a metaphor for output-structure analysis. See
> [What this is not](#what-this-is-not) — it is the most important section here.

---

## What it does

Generates 16 deterministic structured-light pattern types from a seed, runs them
through a fixed image-analysis pipeline twice — once unmodified, once with 11
computational parameters perturbed — and reports how much the analysis output
changed.

```
seed ──► stimulus generator ──► vision pipeline ──► metrics
              │                       ▲                │
              │                  altered_state        │
              └───────────────────────┴──────► divergence
```

The point is the *perturbation*. If you change 11 knobs and the output does not
move, that is a finding about the pipeline. If it moves a lot, that is also a
finding — about a box of image filters, not about consciousness.

## What this is not

Stated first because everything else is easy to misread.

- **Not a neural network.** No model is bundled, loaded, or downloaded. Metrics
  come from edge detection, symmetry analysis, contour finding and clustering.
- **Not consciousness, and not a claim about it.** Nothing here measures
  subjective experience, and the software is not capable of doing so.
- **Not a psychedelic model.** It does not reproduce a biological altered state.
- **Not a validated psychometric instrument.** The perception divergence score is
  an algorithmic construct, not a validated measure of anything.
- **Not blind.** See [Corrections to earlier documentation](#corrections-to-earlier-documentation).

## The divergence score, honestly

```python
score = (geometry_diff + novelty_diff + uncertainty_diff) / (3 * max(1, embedding_distance))
```

Two things about this that matter more than the formula:

1. **It self-normalises.** The denominator is an embedding distance built from the
   same metric components that appear in the numerator. Raising perturbation
   inflates both. A ratio of part-of-a-thing to the whole-of-that-thing is
   bounded by construction, and that bound is doing much of the work.
2. **The score has no validated interpretation scale.** An earlier version of this
   README published a table reading 0.5+ as "significant differences in
   interpretation". **That table was removed.** Nothing in this repository
   establishes 0.5 as a threshold, because no data was ever collected that could.

Read the score as a *relative* quantity — useful for ranking perturbations against
each other on one pipeline, not for asserting that an effect occurred.

## Install

```bash
pip install -r requirements.txt
python main.py
```

Headless, no GUI needed:

```bash
python run_experiment.py experiment --pattern fractal --preset "HIGH PREDICTION ERROR" --seed 999
python run_experiment.py batch --iterations 20 --presets "BASELINE,MAXIMUM EXPLORATION"
```

## Tests

```bash
python -m pytest tests/ -q
```

25 tests. One of them, `test_cross_process_determinism`, is worth calling out: it
generates all 16 pattern types in **three fresh interpreter processes** and
compares digests. The project's other determinism test calls the generator twice
inside one process, which cannot detect a module-level RNG or a hash-order
dependency — the usual real causes of cross-machine drift.

Determinism was independently confirmed at all 16 pattern types across three
separate interpreter starts, and is byte-identical between them.

## Corrections to earlier documentation

Found while preparing this release. Recorded rather than quietly fixed, because a
reader who saw the old text deserves to know it was wrong.

| Claim | Was | Actually |
|---|---|---|
| Pattern count | "15 pattern types" (twice) | **16.** The old text said 15 and then listed 16. |
| Blind experiment mode | "Anonymous condition IDs supported" | **Not implemented.** The string `blind` does not appear anywhere in the source. |
| Licence | "Virtual simulation only. No physical hardware is controlled." | Not a licence — a disclaimer. The project had **no LICENSE file**. MIT added. |

`docs/FINAL_AUDIT.md` had already flagged the blind-mode claim, but described it
as "infrastructure is designed but not enforced in the UI layer". That is more
generous than the evidence supports: there is no implementation at any layer, not
just an unenforced one.

## Limitations

- Single-operator, unblinded, self-reported-divergence. There is no second
  observer and no randomisation, so expectancy effects are not controlled.
- Statistical significance requires more independent observations than this
  repository contains. The bundled statistics engine computes t-tests and effect
  sizes, but no preregistered hypothesis is tested anywhere in it.
- Cross-modal associations are simulated, not computed from a multimodal model.
- No causality: the design cannot show that a *specific* parameter, rather than
  the perturbation as a whole, produced a given change.
- Stimuli are synthetic. Nothing here has been shown to generalise to natural
  images.

## Layout

| Path | Contents |
|---|---|
| `stimuli/generator.py` | 16 pattern types, seed-based determinism |
| `altered_state/engine.py` | 11 parameters, 6 presets, metric transforms |
| `vision/__init__.py` | the CV analysis pipeline |
| `analysis/metrics.py` | `compute_perception_divergence` |
| `experiments/engine.py` | baseline/altered orchestration, replay |
| `storage/`, `reports/` | persistence, JSON/CSV/HTML/Markdown export |
| `ui/` | PySide6 desktop interface |
| `tests/test_all.py` | 25 tests |
| `docs/FINAL_AUDIT.md` | feature audit and interpretation guide |
| `docs/RELEASE_AUDIT.md` | what was wrong before release, and what was fixed |

## Licence

MIT — see [LICENSE](LICENSE). You may not use this to claim evidence about
consciousness, psychedelic experience, or neural-network perception. It cannot
support such a claim, and the licence obliges you not to pretend otherwise.