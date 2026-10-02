# Contributing

## Read this first

`docs/RELEASE_AUDIT.md` records three false claims that were in this project's
documentation until shortly before its first release. The README has been
rewritten to match the source, and the tests now enforce two of those corrections.

If you are about to write a summary of this software, read
**[What this is not](README.md#what-this-is-not)** first.

## The one rule

**Never let documentation claim a capability the source does not have.**

This is not aspirational. Three of the four defects found in `docs/RELEASE_AUDIT.md`
were exactly this failure:

- "Blind Experiment Mode: Anonymous condition IDs supported" — the string `blind`
  appears nowhere in the source
- "15 pattern types" — there are 16, and the same sentence listed 16
- a `## License` section containing a disclaimer instead of a licence

A test, `test_no_blind_mode_implementation`, now greps the source for blinding
keywords and fails if they appear without the feature existing. It is a crude
guard, but it converts a silent divergence into a build failure.

## Adding a feature

1. Implement it
2. Add a test that fails without it
3. Only then document it

If a step is not done, the feature does not go in the README. `docs/FINAL_AUDIT.md`
shows what happens otherwise: it flagged the blinding claim as "not enforced in
the UI layer", which let a reader conclude the feature existed but was buggy,
when in fact nothing implemented it at any layer.

## Determinism

Stimulus generation must remain byte-identical for a given seed **across
processes**, not merely within one. `test_cross_process_determinism` spawns three
fresh interpreters and compares SHA-256 digests of all 16 pattern types.

The failure modes this catches are the ones an in-process test cannot: a
module-level RNG seeded at import, a lazily-initialised global, or any dependence
on `PYTHONHASHSEED` or dict ordering. All of those look deterministic in-process
and drift between runs.

If you touch `stimuli/generator.py`, this test is the one that matters.

## The divergence score

`compute_perception_divergence` self-normalises — the denominator is an embedding
distance computed from the same metric components as the numerator. Treat the
score as a **relative** quantity for ranking perturbations against each other on
one pipeline. Do not add an interpretation table. No threshold has been
empirically established, and if one ever is, it needs data in this repository
first.

## What would help

- An independent implementation of the vision pipeline, so metrics are validated
  against something other than themselves
- A second observer, to test whether divergence scores are reproducible across
  raters
- Any experiment that could establish — or refute — a real interpretation scale
- Tests that stimuli generalise beyond synthetic patterns

## What would not help

- Adding an interpretation table for the divergence score
- Softening a limitation into ambiguity
- Describing classical CV output as "AI perception" without immediately qualifying it

## Running

```bash
pip install -r requirements.txt
python -m pytest tests/ -q
```

28 tests, about 10 seconds. No GPU required.
