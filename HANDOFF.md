# HANDOFF — read this first in a new session

**Written 2026-10-03, corrected 2026-10-04. Authored for whoever picks this up
next, including an AI assistant with no memory of the session that produced it.**

Everything here was learned the hard way. Most of it cost a bug, a wasted
deposit, or a near-miss. If you change nothing else, preserve the following.

---

## 1. What exists

| Project | Location | GitHub | Zenodo |
|---|---|---|---|
| consciousness-indicator-battery | `C:\Users\natha\AI_RESEARCH\consciousness-indicator-battery` | `Nortaq-PlayNexus/consciousness-indicator-battery` | published **v3 `10.5281/zenodo.23122664`**, concept `10.5281/zenodo.23101902` |
| phantom_vision_lab | `C:\Users\natha\code\phantom_vision_lab` | `Nortaq-PlayNexus/phantom-vision-lab` | published **v2 `10.5281/zenodo.23123095`**, concept `10.5281/zenodo.23112115` |
| ScientificDiscoveryLab | git copy `C:\Users\natha\AI_RESEARCH\ScientificDiscoveryLab`; **source of truth** `C:\Users\natha\ScientificDiscoveryLab` | `Nortaq-PlayNexus/ScientificDiscoveryLab` | published **v2 `10.5281/zenodo.23122787`**, concept `10.5281/zenodo.23109116` |

**All CI green.** Battery 48 tests. Phantom Vision Lab 28 tests, 5 jobs. Lab 543
tests, 5 jobs, 20 expected excluded-data failures.

### Twelve records published 2026-10-04

**All twelve are published and verified.** This section previously described the
three umbrella records as staged drafts awaiting a publish click; the maintainer
published them. `PUBLICATION_VERIFICATION.md` in the laboratory repository is the
record of truth, built from public-API read-backs rather than a publish click.

| Record | Version | DOI |
|---|---|---|
| battery | 3.0.0 | `10.5281/zenodo.23122664` |
| ScientificDiscoveryLab | 2.0.0 | `10.5281/zenodo.23122787` |
| phantom vision lab | 2.0.0 | `10.5281/zenodo.23123095` |
| speckle contrast law | 1.0.0 | `10.5281/zenodo.23132744` |
| vortex density | 1.0.0 | `10.5281/zenodo.23132746` |
| discrete vortex detection bias | 1.0.0 | `10.5281/zenodo.23132748` |
| topology-measurement definition | 1.0.0 | `10.5281/zenodo.23132753` |
| RNG certification | 1.0.0 | `10.5281/zenodo.23132759` |
| percolation thresholds and exponents | 1.0.0 | `10.5281/zenodo.23132761` |
| Feigenbaum universality | 1.0.0 | `10.5281/zenodo.23132763` |
| prime gap statistics | 1.0.0 | `10.5281/zenodo.23132767` |
| water acoustic response | 1.0.0 | `10.5281/zenodo.23132771` |

**Subjects: 0 of 12.** The web form did not persist the field either, and
published records are immutable, so this is permanent for all twelve. Fixing it
means a new version of each with subjects typed into the form. See D2 in
`PUBLICATION_VERIFICATION.md`.

One record remains staged: **battery v3.0.1**, draft `23137224`, unsubmitted.
It exists because battery v3.0.0 does not rebuild byte-for-byte from its
repository. Not a scientific change.

### Not published, and why

| Directory | Why |
|---|---|
| `C:\Users\natha\code\EXP0008` | `FALSIFICATION_RECORD.md` finds the headline claims are **hand-authored** — `restore_csvs.py` writes them as string literals. Publish the null results only. |
| `C:\Users\natha\code\string-theory-questions` | Never independently verified. |
| `C:\Users\natha\code\coherent-optical-ai-sandbox` | **Already published** as `10.5281/zenodo.22849652`. Do not re-upload. 1.4 GB folder, only **142 MB real** — `.venv` 1.3 GB, `.pyc` 222 MB. |
| `C:\Users\natha\code\dmt-laser-s9-battery` | Already inside the lab at `AUDIT/S9_PROVENANCE_20260924/`, classified `SYNTHETIC_DERIVED_OUTPUT_NOT_EMPIRICAL_EVIDENCE`. |

---

## 2. Zenodo API — every trap, verified

**The most valuable part of this document.** The API accepts fields it does not
store, and reports success. Nothing warns you.

### Creating a new version — CORRECTED 2026-10-04

An earlier version of this file said Zenodo could not create a version
programmatically. **That was wrong.** Two APIs live under `/api/`:

| endpoint | result |
|---|---|
| `POST /api/deposit/depositions/<id>/actions/new_version` | **404** |
| `POST /api/deposit/depositions` with `metadata.conceptrecid` | 200, field **ignored**, draft lands on a *different concept* |
| **`POST /api/records/<id>/versions`** | **201, concept correctly linked** |

Use the third. Every example online uses the legacy one, which is why this cost
time.

`zenodo/new_version.py` (in all three repos) does it, and **verifies the linkage
before uploading anything** — it aborts if the draft's concept does not match the
parent's.

Note: the parent's `conceptrecid` is **not** the parent's own id. The battery's
record 23111535 has concept `23101902`. Using the record id there would silently
create a disconnected version.

### Fields accepted and silently discarded

Verified by read-back on three separate deposits:

| Field | Behaviour |
|---|---|
| `subjects` | accepted, success reported, **not persisted** |
| `version_note` | same |
| `conceptrecid` (legacy endpoint) | same |
| any partial metadata payload | **destroys every other field** |

### `references` — two distinct failure modes, both observed

- A **single concatenated string** → Zenodo iterates it into 722 one-character
  entries. This was battery v1's defect.
- A **list of objects** (`{id, type, title, citation}`) → **silently dropped**,
  0 stored. This hit the lab.

Both are wrong. It must be a **list of plain strings**. `new_version.py` flattens
objects to their citation string.

### `communities`

Must be `{"identifier": ...}`. A bare string or a `{"id": ...}` dict is rejected
with a 400 — and because the PUT is all-or-nothing, that rejection discards the
description, notes and references sent in the same request.

### PUT is a FULL REPLACEMENT, not a merge

Sending `{"metadata": {"version_note": "..."}}` wiped a draft's title,
description, notes, creators, keywords, version, and licence. The licence
silently reverted to Zenodo's default `cc-by-4.0`. It replied **"accepted"**.

**Never send a partial metadata PUT.** Guard: `zenodo/put_metadata_safely.py`
validates locally, rejects `cc-by-4.0` as the signature of a wiped record, and
compares field-by-field after sending.

### Description read-back needs HTML unescaping

Zenodo escapes `>` → `&gt;` when storing a description. A byte comparison always
fails. Found via a 13021-vs-13019 diff that was twelve escaped blockquote markers
and nothing else. Unescape before comparing, or a real difference hides in noise.

### Other specifics

- All fields nested under a `metadata` key. A flat payload is rejected with
  `"Unknown field"` once per key.
- Create: `POST /api/deposit/depositions` with **only** `{"metadata": {}}`. A
  sibling `bucket` key is rejected.
- Upload: **`PUT`** to `{bucket}/{filename}` with
  `Content-Type: application/octet-stream`. POST to the bare bucket → 405;
  `application/zip` → 415.
- Uploads can abort mid-transfer on a large archive. Retry transient failures;
  never retry 4xx.

### Token

`C:\Users\natha\ScientificDiscoveryLab\zenodo\.zenodo_token` — one token, all
deposits. Git-ignored. Regenerate at
`https://zenodo.org/account/settings/applications/tokens/new`.

### NEVER delete a deposit

The maintainer has said so explicitly. Discarding one is their decision.

`23110728` is a known-dead draft: `[UNUSABLE DRAFT]` in its title, no files, wrong
concept, notes explaining itself. Leave it or delete it yourself. **Do not create
another.**

---

## 3. Rules learned here

### A gate that cannot fail is worse than no gate

Three cases, all of which reported success while verifying nothing:

1. A CI step grepped `FAILED` lines for exception text. Those lines contain only
   node ids. 20 failures sat unexamined.
2. A script read UTF-8 when the writer produced UTF-16. Zero lines parsed, which
   looks like a clean run.
3. A documentation check excluded a section whose heading sat near the top of the
   file, truncating it to its opening paragraph.

**Every check needs a negative test** — inject the defect, confirm the check
fires. Two of the three were caught only because someone wrote one.

### A commit message claiming a fix is not the fix

The lab's v2 version note said "byte-identical to v1" when it was a rebuild of a
newer tree. A commit message asserted the correction had been made. It had not.
Re-read the claim instead of trusting the commit.

### If two files disagree, find out which is which

The battery's three files disagreed on one number. The live Zenodo API settled it
in one call — the record was published and the checkpoint note was stale.
**Verify against the source of truth before reasoning from a summary.**

### Do not run a staging script from inside its destination

`build_publishable.py --dest .` wipes the tree it is standing in. Twice. It
preserves `.git` and `zenodo-deposit`, nothing else. Always run it from the source
of truth: `C:\Users\natha\ScientificDiscoveryLab`.

### Documentation claiming what the code lacks

Phantom Vision Lab's README advertised "Blind Experiment Mode"; `blind` appeared
nowhere in the source. Also "15 pattern types" when there were 16 — and the same
sentence listed 16. And a `## License` section holding a disclaimer, with no
LICENSE file. Two are now enforced by tests, including a negative test proving the
enforcement fires.

### Determinism means cross-process

Calling the generator twice inside one process cannot catch a module-level RNG, a
lazily-initialised global, or a `PYTHONHASHSEED` dependence.

---

## 4. Before publishing anything else

- [ ] Read the project's own limitations section, and believe it
- [ ] Grep for `TODO`, `FIXME`, `hardcoded`, `_BACKUP`, `fix_`, `restore_`
- [ ] Check for post-hoc data repair. If results were patched after generation,
      the seed→result chain is broken and that must be disclosed
- [ ] Confirm every headline number is *computed*, not a literal
- [ ] Run tests in a clean checkout, not your working directory
- [ ] Byte-verify the archive against what the server stored
- [ ] **Set every metadata field before publishing**

---

## 5. Quick reference

```
verify a published record (no auth needed):
  https://zenodo.org/api/records/<id>

list your deposits:
  GET https://zenodo.org/api/deposit/depositions      (Bearer token)

create a new version:
  python zenodo/new_version.py <record-id> --metadata <f> --description <f> --archive <zip>
  # add --dry-run to validate without sending

rebuild + verify an archive:
  python zenodo/build_zenodo_package.py --out <zip> --verify
```

**If you are an AI assistant reading this:** Zenodo will accept fields it does not
store, and a partial PUT will delete everything else while reporting success. Do
not trust a success response. Read the record back. If two sources disagree,
query the live API rather than reasoning from a file. The user prefers to be asked
before anything irreversible, and does not want deposits deleted.

---

## Working-copy locations � do not use %TEMP%

| Repository | Location |
|---|---|
| consciousness-indicator-battery | `C:\Users\natha\AI_RESEARCH\consciousness-indicator-battery` |
| phantom_vision_lab | `C:\Users\natha\code\phantom_vision_lab` |
| ScientificDiscoveryLab (git) | `C:\Users\natha\AI_RESEARCH\ScientificDiscoveryLab` |
| ScientificDiscoveryLab (source of truth) | `C:\Users\natha\ScientificDiscoveryLab` |

The battery repository lived at
`C:\Users\natha\AppData\Local\Temp\opencode\cib-clean` until 2026-10-04, when
**that directory was cleared and the working copy was lost.** It was recovered by
cloning from GitHub � no committed work was lost � but uncommitted work would
have been, and a Zenodo working directory is not the place for that.

The twelve records published on 2026-10-04 live on Zenodo's servers and were never
at risk. So is battery v3.0.1 (draft `23137224`, still unsubmitted).

**Never keep a working copy under `%TEMP%`.** See `PUBLISH_CHECKLIST.md`.
