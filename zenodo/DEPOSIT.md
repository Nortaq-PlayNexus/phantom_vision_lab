# Zenodo deposit 23112116 — DRAFT, awaiting publish

## Status

**Created and uploaded. NOT published. No DOI minted.**

```
state        unsubmitted
title        Phantom Vision Lab: a computational instrument for perturbing an
             image-analysis pipeline and measuring how its output changes
upload_type  software
license      mit-license (MIT, with scientific-use restriction)
access_right open
language     eng
version      1.0.0
description  8,161 chars
notes        2,773 chars
creators     1 — Phantom Vision Lab contributors
keywords     10
related_ids  1 — the GitHub repository
files        1
```

Publish at: **https://zenodo.org/deposit/23112116**

## File integrity, local vs Zenodo

| | local | Zenodo | match |
|---|---|---|---|
| size | 73,175 | 73,175 | yes |
| md5 | `4e10066e5fa4e000c92c13098d265d2c` | `4e10066e5fa4e000c92c13098d265d2c` | yes |

SHA-256 `506d0d127a7cacc7bd148787d84d807ca57cfbf94795f7b3524d605bfa5e61bc`
54 files. Byte-reproducible — two independent builds produce an identical digest.

The archive excludes `.git`, `__pycache__`, `.pytest_cache` and `data/`. The last
holds 35 MB of runtime experiment output: git-ignored, untracked, and regenerable
from seeds. Nothing in the tests or the verification tools reads it.

## SUBJECTS: add these by hand before publishing

Zenodo's deposition API accepts `subjects` without error and then silently
discards it — it does not persist the field and does not echo it back on read.
This is the third deposit where that has happened; it is now a known property of
the API rather than a surprise.

| id | title |
|---|---|
| `euroscivoc:307` | Software |
| `mesh:D015203` | Reproducibility of Results |
| `mesh:D012106Q000706` | Research/statistics & numerical data |
| `euroscivoc:1061` | Numerical analysis |

## No references

This deposit cites no literature, deliberately. Every paper that would be cited
here describes neural networks, subjective reports, or psychometric instruments,
and none of those are what this software does. Adding citations would imply a
literature grounding that does not exist.

The one thing this does rest on is its own record, which is in the archive:
`docs/RELEASE_AUDIT.md`.

## Everything else on the record

| Deposit | State | What |
|---|---|---|
| 23101903 | published | consciousness-indicator-battery, `10.5281/zenodo.23101903` |
| 23109117 | published | ScientificDiscoveryLab, `10.5281/zenodo.23109117` |
| 23110728 | unsubmitted | battery v2 attempt, **unusable** — concept linkage failed |
| 23111535 | unsubmitted | battery v2 draft created via the web UI, 0 files |
| **23112116** | **unsubmitted** | **this deposit** |

Nothing was deleted. Two battery drafts remain unsubmitted because discarding a
deposit is the maintainer's decision, not something to do automatically.

## After publishing

Copy the DOI and record it in four places:

- `zenodo/metadata.json` → `doi`
- `CITATION.cff` → `doi:`
- `README.md` → DOI badge
- `RELEASE.md` → DOI row

Any later change must be a **new version**, never an edit. Published Zenodo
records are immutable.
