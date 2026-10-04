# Zenodo status — Phantom Vision Lab

**Single source of truth. Everything below is current as of 2026-10-04.**

## Published

| | |
|---|---|
| Record | `23112116` |
| DOI | **`10.5281/zenodo.23112116`** |
| Concept DOI | `10.5281/zenodo.23112115` |
| Version | 1.0.0 |
| Published | 2026-10-03 |
| Archive | `phantom-vision-lab-v1.0.0.zip`, 71,479 bytes |
| SHA-256 | `506d0d127a7cacc7bd148787d84d807ca57cfbf94795f7b3524d605bfa5e61bc` |
| MD5 as uploaded | `4e10066e5fa4e000c92c13098d265d2c` |

v1 has **zero subjects**. Zenodo accepts the field, reports success, and does not
persist it. That is why v2 exists.

---

## Draft, ready to publish

| | |
|---|---|
| Draft | **`23123095`** |
| Edit | **https://zenodo.org/deposit/23123095** |
| Concept DOI | `23112115` — **verified linked** |
| Version | 2.0.0 |
| Files | 1 |
| Archive | `phantom-vision-lab-v2.0.0.zip`, 90,783 bytes |
| SHA-256 | `cbef8e74ad7a3084d90d1dd9d0587192a70136c4671106183736aa0bf9465d29` |
| MD5 as uploaded | `6f...` (see `new_version.py` output) |

### What v2 changes

**Metadata only.** No code, no results, no scientific content.

- adds the four subjects v1 lacks
- adds a version note explaining why

### Verified on read-back

| field | status |
|---|---|
| title | ok |
| version | ok |
| license | ok |
| description | ok (Zenodo HTML-escapes `>`; compared after unescaping) |
| notes | ok |
| creators | 1/1 |
| keywords | 10/10 |
| related_identifiers | 1/1 |

### Two steps, then publish

1. **Subjects** — Zenodo's deposition API discards this field. Paste by hand:

   | id | title |
   |---|---|
   | `euroscivoc:307` | Software |
   | `mesh:D015203` | Reproducibility of Results |
   | `mesh:D012106Q000706` | Research/statistics & numerical data |
   | `euroscivoc:1061` | Numerical analysis |

2. **Version note** — from `zenodo/metadata.json`, the `version_note` field.

3. **Publish.**

### After publishing

Record the new DOI in four places: `zenodo/metadata.json`, `CITATION.cff`, the
README badge, `RELEASE.md`. Then commit and push.

Any further change must be a **new version**, never an edit.

---

## Toolbox

| Script | Purpose |
|---|---|
| `new_version.py` | create and populate a version. Uses `POST /api/records/<id>/versions`, verifies concept linkage **before** uploading. `--dry-run` to validate. |
| `put_metadata_safely.py` | update metadata on a draft. Refuses partial PUTs, rejects `cc-by-4.0` as the signature of a wiped record, compares field by field. |
| `upload_to_zenodo.py` | first-time deposit creation via the legacy endpoint. |
| `../tools/build_zenodo_package.py` | byte-reproducible archive, `--verify` builds twice and compares digests. |

## Everything else

See `HANDOFF.md` at the repository root — the Zenodo API traps, the current
deposit states across all three repositories, and the standing instructions.