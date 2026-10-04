# PUBLISH CHECKLIST — all three records

Everything is staged. Three drafts, each verified, each concept-linked, none
published. What remains cannot be automated: Zenodo's deposition API accepts
`subjects` and `version_note`, reports success, and persists neither.

Each record takes about two minutes.

---

## 1. battery v3.0.0

**https://zenodo.org/deposit/23122664**

Verify the concept reads `10.5281/zenodo.23101902` before publishing. If a draft
ever shows a different concept DOI, close it — a mislinked version is permanent.

**Subjects** — paste these six:

| id | title |
|---|---|
| `mesh:D003243` | Consciousness |
| `euroscivoc:297` | Artificial intelligence |
| `mesh:D009488` | Neurosciences |
| `euroscivoc:307` | Software |
| `euroscivoc:609` | Philosophy |
| `mesh:D015203` | Reproducibility of Results |

**Version note** — from `zenodo/metadata_v2.json`, field `version_note`.

**Publish.** Then record the DOI in `metadata_v2.json`, `CITATION.cff`, the
README badge and `RELEASE.md`.

---

## 2. ScientificDiscoveryLab v2.0.0

**https://zenodo.org/deposit/23122787**

Concept must read `10.5281/zenodo.23109116`.

**Subjects** — paste these eight:

| id | title |
|---|---|
| `mesh:D015203` | Reproducibility of Results |
| `mesh:D010825Q000379` | Physics/methods |
| `mesh:D010825Q000295` | Physics/instrumentation |
| `mesh:D012106Q000706` | Research/statistics & numerical data |
| `euroscivoc:805` | Statistical mechanics |
| `euroscivoc:1061` | Numerical analysis |
| `mesh:D012984` | Software |
| `mesh:D012586Q000941` | Science/ethics |

**References** — already stored, 6 of 6. Nothing to do.

**Version note** — from `zenodo/metadata.json`, field `version_note`.

**Publish.** Then record the DOI in `metadata.json`, `CITATION.cff`, the README
badge and `RELEASE.md`.

---

## 3. Phantom Vision Lab v2.0.0

**https://zenodo.org/deposit/23123095**

Concept must read `10.5281/zenodo.23112115`.

**Subjects** — paste these four:

| id | title |
|---|---|
| `euroscivoc:307` | Software |
| `mesh:D015203` | Reproducibility of Results |
| `mesh:D012106Q000706` | Research/statistics & numerical data |
| `euroscivoc:1061` | Numerical analysis |

**Version note** — from `zenodo/metadata.json`, field `version_note`.

**Publish.** Then record the DOI in `metadata.json`, `CITATION.cff`, the README
badge and `RELEASE.md`.

---

## After each publish

1. `https://zenodo.org/api/records/<id>` and confirm `subjects` and `references`
   are populated. **Do not assume the web form worked** — read it back. All three
   v1 records published with zero subjects because nobody checked.
2. Confirm the archive `checksum` matches the local build.
3. Record the DOI in the four places listed above.
4. Commit and push.
5. Confirm CI is green.

---

## If a publish goes wrong

- **Wrong concept DOI shown** → close the draft without publishing. Every field of
  these three was verified linked before upload; if one is wrong, something
  changed underneath and needs investigating.
- **Subjects missing after publishing** → cannot be fixed in place; becomes a v2.
  Check before clicking.
- **Never delete a deposit.** If a draft is unusable, leave it titled to explain
  itself, as `23110728` is.

---

## Not part of this batch

| | |
|---|---|
| `C:\Users\natha\code\EXP0008` | On hold. `FALSIFICATION_RECORD.md` shows the headline claims are hand-authored, not computed. Publish the null results only — the Q7 refutation, EXP0010's 0/11, and the pooling attribution all reproduce. |
| `C:\Users\natha\code\string-theory-questions` | Never independently verified. |
| `coherent-optical-ai-sandbox` | Already published as `10.5281/zenodo.22849652`. Do not re-upload. |
| `dmt-laser-s9-battery` | Already inside the lab, audited as `SYNTHETIC_DERIVED_OUTPUT_NOT_EMPIRICAL_EVIDENCE`. |

See `HANDOFF.md` at the repository root for the API traps and standing rules.