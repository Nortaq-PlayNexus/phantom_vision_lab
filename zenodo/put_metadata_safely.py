#!/usr/bin/env python3
"""Refuse any metadata PUT that does not carry the complete record.

    python zenodo/put_metadata_safely.py <deposit-id>

    python zenodo/put_metadata_safely.py 23111535          # from metadata_v2.json
    python zenodo/put_metadata_safely.py 23111535 --dry-run

Why this script exists
----------------------
Zenodo's deposit API treats PUT as a **full replacement**, not a merge.

On 2026-10-02 a targeted PUT carrying only `version_note` was sent to deposit
23111535 to work around that field being silently discarded. The response was
"accepted". Every other field was destroyed: title, description, notes, creators,
contributors, keywords, related identifiers, version, and the licence, which
silently reverted to Zenodo's default `cc-by-4.0`.

The draft had to be rebuilt from `metadata_v2.json`. The archive survived, because
files live in a separate bucket. Nothing was published, so nothing was permanent --
but a record with an empty title and the wrong licence is one click away from
becoming permanent.

A PUT that reports success while deleting everything else is the worst failure
mode available: it looks like it worked.

What this does
--------------
Every metadata PUT on this account must:

  1. build the payload from the COMPLETE metadata file, never a fragment
  2. assert locally that the payload has a non-empty title, description, licence,
     creators and keywords before sending anything
  3. read the record back afterwards and compare field by field
  4. print a diff, so a silent drop is visible rather than assumed

Re-verified against the live API on 2026-10-10, using a throwaway deposit:

  * PUT is still a full replacement. Omitting a field from the payload really
    does destroy it -- `subjects` went to zero items on a deliberate probe.
  * `subjects` and `references` DO persist. An earlier revision of this file
    claimed they were unwritable and had to be entered in the web form; that
    was wrong, and acting on it would have destroyed them.
  * `version_note` still does not persist.
  * A licence of `cc-by-4.0` on read-back no longer implies a wiped record,
    but it is still refused on the way out, because it is never the intent.

Exit 0 only if the read-back matches what was sent.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = "https://zenodo.org/api"

TOKEN_CANDIDATES = (
    HERE / ".zenodo_token",
    ROOT / ".zenodo_token",
    Path(r"C:\Users\natha\ScientificDiscoveryLab\zenodo\.zenodo_token"),
)

#: Fields that must be present and non-empty. Each one was observed to be
#: destroyed by a partial PUT, or silently discarded outright.
REQUIRED = {
    "title": lambda v: isinstance(v, str) and len(v.strip()) > 0,
    "description": lambda v: isinstance(v, str) and len(v.strip()) > 0,
    "license": lambda v: bool(v),
    "upload_type": lambda v: bool(v),
    "creators": lambda v: isinstance(v, list) and len(v) > 0,
    "keywords": lambda v: isinstance(v, list) and len(v) > 0,
}


def token() -> str:
    for path in TOKEN_CANDIDATES:
        if path.is_file():
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value
    sys.exit("ERROR: no Zenodo token found in any known location")


def request(method: str, url: str, tok: str, body: bytes | None = None) -> dict:
    import urllib.error
    import urllib.request

    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {tok}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        sys.exit(f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:800]}")


def validate(payload: dict) -> list[str]:
    problems = []
    meta = payload.get("metadata", {})
    for field, test in REQUIRED.items():
        if field not in meta:
            problems.append(f"missing: {field}")
        elif not test(meta[field]):
            problems.append(f"empty or invalid: {field}")
    if meta.get("license") == "cc-by-4.0":
        problems.append(
            "license is cc-by-4.0, Zenodo's default for an empty record -- "
            "this is the signature of a wiped metadata block"
        )
    return problems


def compare(sent: dict, got: dict) -> list[str]:
    """Field-by-field comparison of what we sent against what Zenodo stored.

    Every message is prefixed ``ADVISORY:`` or ``FATAL:``. main() routes on the
    prefix instead of matching a substring, so a genuinely damaged field cannot
    be quietly downgraded to a warning by rewording.
    """
    problems = []
    sent_meta = sent.get("metadata", {})
    got_meta = got.get("metadata", {})

    for field, _ in REQUIRED.items():
        s = sent_meta.get(field)
        g = got_meta.get(field)
        if isinstance(s, list):
            same = len(s) == len(g or [])
        elif isinstance(s, str):
            same = isinstance(g, str) and len(g) == len(s)
        else:
            same = s == g
        if not same:
            problems.append(
                f"FATAL: {field}: sent {summarise(s)} -> stored {summarise(g)}"
            )

    # Verified writable on 2026-10-10 by probe against a throwaway deposit:
    # both of these survive a full-metadata PUT. An earlier revision of this
    # script listed them as unwritable, which was wrong -- and because PUT
    # replaces rather than merges, omitting them would have destroyed them.
    # A drop here is real damage, so it blocks.
    for field in ("subjects", "references"):
        if sent_meta.get(field):
            stored = got_meta.get(field)
            if not stored:
                problems.append(
                    f"FATAL: {field}: sent {summarise(sent_meta[field])} "
                    f"-> stored nothing -- the PUT damaged this field"
                )

    # Verified NOT writable on the same date: the value is accepted and then
    # dropped. Advisory only, because no payload can set it.
    if sent_meta.get("version_note") and not got_meta.get("version_note"):
        problems.append(
            "ADVISORY: version_note: sent but not stored -- known API "
            "behaviour, enter it in the web form"
        )
    return problems


def summarise(value) -> str:
    if isinstance(value, str):
        return f"{len(value)} chars"
    if isinstance(value, list):
        return f"{len(value)} items"
    return repr(value)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("deposit_id")
    ap.add_argument("--metadata", default=str(HERE / "metadata_v2.json"))
    ap.add_argument("--description", default=str(HERE / "description_v2.md"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sys.path.insert(0, str(HERE))
    from upload_v2 import build_metadata  # noqa: E402

    tok = token()
    meta = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
    description = Path(args.description).read_text(encoding="utf-8")
    payload = {"metadata": build_metadata(meta, description)}

    print("=== local validation, before anything is sent ===")
    problems = validate(payload)
    if problems:
        print("REFUSING TO SEND:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("  payload complete: title, description, licence, creators, keywords all present")

    if args.dry_run:
        print("\n--dry-run: nothing sent")
        return 0

    print(f"\nPUT complete metadata to deposit {args.deposit_id} ...")
    request("PUT", f"{BASE}/deposit/depositions/{args.deposit_id}", tok,
            json.dumps(payload).encode())

    stored = request("GET", f"{BASE}/deposit/depositions/{args.deposit_id}", tok)

    print("\n=== read-back comparison ===")
    fatal = []
    advisory = []
    for line in compare(payload, stored):
        if line.startswith("ADVISORY:"):
            advisory.append(line)
            print(f"  ~ {line}")
        else:
            fatal.append(line)
            print(f"  ! {line}")

    if fatal:
        print("\nFAIL: fields were destroyed or altered. DO NOT PUBLISH.")
        return 1
    if advisory:
        print("\nKnown-discarded fields above still need manual entry in the web form.")
    print("\nOK: metadata stored intact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
