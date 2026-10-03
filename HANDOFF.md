# HANDOFF — read this first in a new session

**Written 2026-10-03. Authored for whoever picks this up next, including an AI
assistant with no memory of the session that produced it.**

Everything here was learned the hard way. Most of it cost a bug, a wasted
deposit, or a near-miss. If you change nothing else, preserve the following.

---

## 1. What exists

| Project | Location | GitHub | Zenodo |
|---|---|---|---|
| consciousness-indicator-battery | `C:\Users\natha\AppData\Local\Temp\opencode\cib-clean` | `Nortaq-PlayNexus/consciousness-indicator-battery` | **v2 `10.5281/zenodo.23111535`**, concept `10.5281/zenodo.23101902` |
| phantom_vision_lab | `C:\Users\natha\code\phantom_vision_lab` | `Nortaq-PlayNexus/phantom-vision-lab` | **`10.5281/zenodo.23112116`** |
| ScientificDiscoveryLab | `C:\Users\natha\AI_RESEARCH\ScientificDiscoveryLab` (git copy); source of truth `C:\Users\natha\ScientificDiscoveryLab` | `Nortaq-PlayNexus/ScientificDiscoveryLab` | **`10.5281/zenodo.23109117`** |

**All CI is green.** Battery: 48 tests. Phantom Vision Lab: 28 tests, 5 CI jobs.
Lab: 543 tests, 5 CI jobs, 20 expected excluded-data failures.

### Not published, and why

| Directory | Why |
|---|---|
| `C:\Users\natha\code\EXP0008` | `FALSIFICATION_RECORD.md` finds the headline claims are **hand-authored**, not computed. Publish the null results only. See §5. |
| `C:\Users\natha\code\string-theory-questions` | Never independently verified. Disposition in `AUDIT_OF_AUDITS.md` is decent but unchecked. |
| `C:\Users\natha\code\coherent-optical-ai-sandbox` | **Already published** as `10.5281/zenodo.22849652`. Do not re-upload. Folder is 1.4 GB but only **142 MB is real** — `.venv` is 1.3 GB, `.pyc` 222 MB. |
| `C:\Users\natha\code\dmt-laser-s9-battery` | Already inside the lab at `AUDIT/S9_PROVENANCE_20260924/`, classified `SYNTHETIC_DERIVED_OUTPUT_NOT_EMPIRICAL_EVIDENCE`. Do not re-upload. |

---

## 2. Zenodo API — every trap, in the order you will hit them

**This is the most valuable part of this document.** The API accepts fields it
does not store, and reports success. Nothing warns you.

### Fields that are accepted, and silently discarded

Verified on this account:

| Field | Behaviour |
|---|---|
| `subjects` | Accepted, reports success, **not persisted**, not echoed on read |
| `version_note` | Same |
| `conceptrecid` | Accepted, reports success, **ignored** — the draft lands on a NEW concept |

All three must be set in the **web form**, or via a web-UI-created draft.

### `references` is NOT one of them

`references` works correctly **as a list of strings**. v1 of the battery sent it
as a single concatenated string and Zenodo iterated that string into 722
one-character entries — which looked exactly like the API dropping the field. It
wasn't. The field was malformed. This cost real time to establish; do not
re-investigate it.

### PUT is a FULL REPLACEMENT, not a merge

Sending `{"metadata": {"version_note": "..."}}` **wiped every other field** of a
draft: title, description, notes, creators, keywords, version, and the licence —
which silently reverted to Zenodo's default `cc-by-4.0`. It replied "accepted".

**Never send a partial metadata PUT.** Always rebuild from the complete metadata
file. Guard: `zenodo/put_metadata_safely.py` (battery repo) validates locally,
rejects `cc-by-4.0` as the signature of an already-wiped record, and compares
field-by-field after sending. Exit non-zero on any destructive change.

### Other API specifics

- Every field must be nested under a `metadata` key. A flat payload is rejected
  with `"Unknown field"` once per key — which reads like a broken API.
- Creating a deposition: `POST /api/deposit/depositions` with **only**
  `{"metadata": {}}`. Passing a sibling `bucket` key is rejected.
- Uploading a file: **`PUT`** to `{bucket}/{filename}` with
  `Content-Type: application/octet-stream`. POST to the bare bucket gives 405;
  `application/zip` gives 415.
- `communities` with legacy string ids (`philosophyofmind`) must be sent as
  objects: `{"identifier": "philosophyofmind"}`. The bare string is rejected, and
  because the PUT is all-or-nothing that failure discards everything else in the
  same request.
- To make a **new version** of a published record: use the web UI's *New version*
  action. The API cannot do it.

### Token

`C:\Users\natha\ScientificDiscoveryLab\zenodo\.zenodo_token` — one token serves
all deposits. Git-ignored. Regenerate at
`https://zenodo.org/account/settings/applications/tokens/new` (the
`/applications/` path redirects to login and looks broken).

### NEVER delete a deposit

The maintainer has said so explicitly. Discarding a deposit is their decision.

`23110728` is a known-dead draft — `[UNUSABLE DRAFT]` in its title, no files, on
the wrong concept, with notes explaining itself. Leave it or delete it yourself.
**Do not create another.**

---

## 3. Current deposits

| ID | State | What |
|---|---|---|
| 23101903 | done | battery **v1** — superseded on metadata, still citable |
| 23111535 | done | battery **v2 — cite this** |
| 23109117 | done | ScientificDiscoveryLab |
| 23112116 | done | Phantom Vision Lab |
| 23110728 | unsubmitted | dead battery draft. Leave alone. |

### Outstanding work

| # | Work | Why | Effort |
|---|---|---|---|
| 1 | **battery v3** | v2 has zero subjects and no version note. v3 should also retitle to `Consciousness Indicator Battery: calibrated indicators for AI consciousness, and what survives perturbing them` — v2 kept v1's title because the retitle was attempted while the record was being published and the PUT 404'd. | ~10 min, but **create the draft in the web UI**, not the API |
| 2 | **lab v2** | `10.5281/zenodo.23109117` has zero subjects and zero references. Values in `zenodo/DEPOSIT_23109117.md`. | Same |
| 3 | **phantom-vision-lab v2** | `10.5281/zenodo.23112116` has zero subjects. Values in `zenodo/DEPOSIT.md`. | Same |

For all three: **set every field before publishing.** Zenodo is immutable and a
new version needs the web UI.

---

## 4. Rules learned here

### A gate that cannot fail is worse than no gate

Three separate cases this session:

1. A CI step grepped `FAILED` lines for exception text. Those lines contain only
   node ids. It reported success with 20 failures unexamined.
2. A script read its input as UTF-8 when the writer produced UTF-16. Zero lines
   parsed, which looked like a clean run.
3. A documentation check excluded a section whose heading sat near the top of the
   file, truncating it to its opening paragraph. It reported PASS while verifying
   almost nothing.

**Every check that gates anything needs a negative test** — inject the defect,
confirm the check fires. Two of these three were caught only because someone wrote
that test.

### A promise must be stronger than the environment it lives in

- The S9 provenance audit hardcoded `C:\Users\natha\code\...`. Unrunnable
  everywhere else. Now resolves from `S9_EXTERNAL_ROOT`.
- A stored provenance report contained absolute paths. It could only verify on
  one machine.
- `build_publishable.py` walked the filesystem without consulting `.gitignore`,
  so a **Zenodo token's SHA-256** landed in the published `manifest.json`.

### Documentation claiming what the code lacks

Phantom Vision Lab's README advertised "Blind Experiment Mode". The string
`blind` appeared nowhere in the source. Also: "15 pattern types" when there were
16 — and the same sentence listed 16. And a `## License` section containing a
disclaimer rather than a licence, with no LICENSE file at all.

Two of these are now enforced by tests, including a negative test proving the
enforcement still fires.

### Determinism means cross-process

`test_lattice_determinism` called the generator twice inside one process. That
cannot catch a module-level RNG, a lazily-initialised global, or a
`PYTHONHASHSEED` dependence. The real check spawns three interpreters.

### If two files disagree, find out which is which

The battery's three files disagreed on one number. Checking the live Zenodo API
settled it in one call — the record was published, the checkpoint note was stale.
**Verify against the source of truth before reasoning from a summary.**

---

## 5. Before publishing anything else

- [ ] Read the project's own limitations section, and believe it
- [ ] Grep the repo for `TODO`, `FIXME`, `hardcoded`, `_BACKUP`, `fix_`, `restore_`
- [ ] Check for post-hoc data repair scripts. If results were patched after
      generation, the seed→result chain is broken and that must be disclosed
- [ ] Confirm every headline number is *computed*, not a literal. `EXP0008` failed
      this: `restore_csvs.py` writes its results table as string literals
- [ ] Run the tests in a clean checkout, not your working directory
- [ ] Byte-verify the archive against what the server actually stored
- [ ] Set every metadata field *before* publishing

---

## 6. Conventions

- Commit messages explain **why**, and name the failure that prompted the change
- Failed attempts and defects are recorded, never quietly deleted
- `RESEARCH_RULES.md` in the lab: claim layers, mandatory controls, kill-the-
  hypothesis, evidence grading E0–E6, read-only raw data, fail-closed runners
- Byte-reproducible archives: fixed mtimes, sorted entries, fixed mode bits
- `* -text` in `.gitattributes` wherever a manifest records file digests

---

## 7. Quick reference

```
verify a published record (no auth needed):
  https://zenodo.org/api/records/<id>

list your deposits:
  GET https://zenodo.org/api/deposit/depositions   (Bearer token)

rebuild + verify an archive:
  python zenodo/build_zenodo_package.py --out <zip> --verify

safe metadata update:
  python zenodo/put_metadata_safely.py <deposit-id> --dry-run
```

**If you are an AI assistant reading this:** the Zenodo API will accept fields it
does not store. Do not trust a success response. Read the record back. If two
sources disagree, query the live API rather than reasoning from a file. The user
prefers to be asked before anything irreversible, and does not want deposits
deleted.
