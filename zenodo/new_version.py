#!/usr/bin/env python3
"""Create and populate a new Zenodo version through the records API.

    python zenodo/new_version.py <record-id> --metadata <f> --description <f> --archive <zip>

WHAT THIS REPLACES
------------------
An earlier conclusion in this repository was that Zenodo cannot create a new
version programmatically, and that the web interface's "New version" action was
the only route. That was wrong, and wrong in a way that cost real time.

Tested and confirmed on 2026-10-04:

  POST /api/deposit/depositions/<id>/actions/new_version   -> 404
  POST /api/deposit/depositions with metadata.conceptrecid -> 200 but IGNORED
  POST /api/records/<id>/versions                           -> 201, concept linked

The legacy *deposit* API cannot express a new version. The *records* API can.
Both live under /api/ and the difference is easy to miss because the legacy one
is what every example online uses.

Verify after creating, always:

  GET /api/deposit/depositions/<new-id>
  assert metadata.conceptrecid == <concept-recid of the parent>

`conceptrecid` on the parent is not the parent's own id. For the battery,
record 23111535 has conceptrecid 23101902, which is a *different* number. Using
the record id there would silently create a disconnected version.

Safety
------
Never sends a partial metadata PUT. The draft is built from the complete
metadata file, uploaded to first so the record is never in a state with metadata
but no file, and read back field by field afterwards.

    python zenodo/new_version.py <record-id> ... --dry-run   # validate only
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import time
import sys
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = "https://zenodo.org/api"

TOKEN_CANDIDATES = (
    HERE / ".zenodo_token",
    ROOT / ".zenodo_token",
    Path(r"C:\Users\natha\ScientificDiscoveryLab\zenodo\.zenodo_token"),
)

REQUIRED = {
    "title": lambda v: isinstance(v, str) and v.strip(),
    "description": lambda v: isinstance(v, str) and v.strip(),
    "license": lambda v: bool(v),
    "upload_type": lambda v: bool(v),
    "creators": lambda v: isinstance(v, list) and len(v) > 0,
    "keywords": lambda v: isinstance(v, list) and len(v) > 0,
}

KNOWN_UNSETTABLE = ("subjects", "version_note")


def token() -> str:
    env = os.environ.get("ZENODO_TOKEN")
    if env:
        return env.strip()
    for p in TOKEN_CANDIDATES:
        if p.is_file():
            v = p.read_text(encoding="utf-8").strip()
            if v:
                return v
    sys.exit("ERROR: no Zenodo token found")


def request(method: str, url: str, tok: str, body: bytes | None = None,
            content_type: str | None = None, attempts: int = 3) -> dict:
    """Issue a request, retrying transient network failures.

    A 6.7 MB archive upload aborted mid-transfer once during preparation
    (URLError, connection reset by the local host stack). Without a retry that
    leaves a draft with no file and forces a manual re-run, which is exactly the
    kind of interruption that turns into an orphan when the operator gives up.

    Retried: URLError, timeouts, and 5xx. NOT retried: 4xx. A 400 means the
    request is wrong and repeating it will be wrong again.
    """
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("Authorization", f"Bearer {tok}")
        if content_type:
            req.add_header("Content-Type", content_type)
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:1500]
            if exc.code < 500:
                sys.exit(f"HTTP {exc.code} on {method} {url}\n{detail}")
            last = exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
        if attempt < attempts:
            wait = 3 * attempt
            print(f"    transient failure ({type(last).__name__}), "
                  f"retry {attempt}/{attempts - 1} in {wait}s")
            time.sleep(wait)
    sys.exit(f"{method} {url} failed after {attempts} attempts: {last}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def build_payload(meta: dict, description: str) -> dict:
    """Assemble the API payload from the metadata file and the description file.

    Validated as a whole afterwards, because validating the metadata file alone
    gives a false result: the description lives in a separate file, so a check
    for it on `meta` always fails.
    """
    payload: dict = {}
    for key in ("upload_type", "title", "version", "license", "language",
                "access_right", "creators", "keywords", "related_identifiers",
                "notes"):
        if key in meta:
            payload[key] = meta[key]
    payload["description"] = description

    if meta.get("contributors"):
        payload["contributors"] = meta["contributors"]
    if meta.get("communities"):
        # Normalise every accepted local spelling to what Zenodo wants:
        #   "philosophyofmind"                -> {"identifier": "philosophyofmind"}
        #   {"id": "b2789229-..."}            -> {"identifier": "b2789229-..."}
        #   {"identifier": "..."}             -> unchanged
        # A bare string is rejected outright, and because the PUT is all-or-nothing
        # that rejection discards the description, notes and references sent in
        # the same request. This was hit on the lab deposit.
        payload["communities"] = [
            {"identifier": c["identifier"] if isinstance(c, dict) and "identifier" in c
             else c["id"] if isinstance(c, dict) else c}
            for c in meta["communities"]
        ]
    if meta.get("references"):
        # Must be a LIST OF PLAIN STRINGS. Two failure modes, both observed:
        #   * one concatenated string  -> Zenodo iterates it into 722
        #     one-character entries. The battery's v1 defect.
        #   * a list of objects         -> silently dropped, 0 stored. Hit on
        #     the lab deposit, which carried {id, type, title, citation} dicts.
        # Objects are flattened to their citation string, which is the form that
        # demonstrably persists.
        flat = []
        for r in meta["references"]:
            if isinstance(r, str):
                flat.append(r)
            elif isinstance(r, dict):
                citation = r.get("citation")
                if not citation:
                    citation = r.get("title", "")
                    if r.get("id"):
                        citation = f"{citation}. {r['id']}"
                flat.append(citation)
            else:
                flat.append(str(r))
        payload["references"] = flat
    if meta.get("subjects"):
        payload["subjects"] = [{"id": s["id"]} for s in meta["subjects"]]
    if meta.get("version_note"):
        payload["version_note"] = meta["version_note"]
    return payload


def same_text(sent: str | None, stored: str | None) -> bool:
    """Compare text, tolerating Zenodo's HTML escaping of the stored form.

    Zenodo escapes markup-significant characters when storing a description:
    `numpy>=2.5.0` comes back as `numpy&gt;=2.5.0`. The content is identical and
    renders correctly on the record page; only the stored representation differs.

    Found on the lab deposit while comparing a 13021-vs-13019 character
    read-back. Without this, every description containing `>`, `<` or `&` reports
    as a mismatch, and a genuine mismatch would be lost in the noise.

    Anything else still counts as different.
    """
    if not isinstance(sent, str) or not isinstance(stored, str):
        return sent == stored
    if sent == stored:
        return True
    return html.unescape(stored).rstrip("\n") == sent.rstrip("\n")


def validate(payload: dict) -> list[str]:
    problems = []
    for field, test in REQUIRED.items():
        if field not in payload:
            problems.append(f"missing: {field}")
        elif not test(payload[field]):
            problems.append(f"empty or invalid: {field}")
    if payload.get("license") == "cc-by-4.0":
        problems.append(
            "license is cc-by-4.0, Zenodo's default for an empty record -- "
            "signature of a wiped metadata block"
        )
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("record_id", help="the published record to version")
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--description", required=True)
    ap.add_argument("--archive", required=True)
    ap.add_argument("--reuse", type=int, default=None,
                    help="populate an existing draft instead of creating one")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tok = token()
    meta = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
    description = Path(args.description).read_text(encoding="utf-8")
    archive = Path(args.archive).resolve()

    if not archive.is_file():
        sys.exit(f"ERROR: archive not found: {archive}")
    if meta["version"] not in archive.name:
        sys.exit(
            f"ERROR: version {meta['version']} does not appear in archive filename "
            f"{archive.name}. Zenodo files are immutable, so a mismatch is permanent."
        )

    payload = build_payload(meta, description)
    problems = validate(payload)
    if problems:
        print("REFUSING TO PROCEED:")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"parent record  : {args.record_id}")
    print(f"version        : {meta['version']}")
    print(f"archive        : {archive.name}  {archive.stat().st_size:,} bytes")
    print(f"archive sha256 : {sha256_file(archive)}")
    print(f"title          : {meta['title']}")
    print("local validation: OK")

    if args.dry_run:
        print("\n--dry-run: nothing created or sent")
        return 0

    if args.reuse:
        draft_id = args.reuse
        print(f"\nreusing draft {draft_id}")
    else:
        print(f"\ncreating a new version via POST /api/records/{args.record_id}/versions")
        created = request("POST", f"{BASE}/records/{args.record_id}/versions", tok,
                          b"", "application/json")
        draft_id = created.get("id")
        print(f"  draft id {draft_id}")

    # Confirm linkage BEFORE uploading anything.
    parent = request("GET", f"{BASE}/records/{args.record_id}", tok)
    concept = parent.get("conceptrecid")
    draft = request("GET", f"{BASE}/deposit/depositions/{draft_id}", tok)
    linked = draft.get("conceptrecid")
    print(f"  parent concept {concept}   draft concept {linked}")
    if concept and linked != concept:
        sys.exit(
            f"ABORTING: draft concept {linked} != parent concept {concept}. "
            "Uploading would create a permanently mislinked version."
        )
    print("  concept linkage verified")

    print("\nuploading archive...")
    bucket = draft["links"]["bucket"].rstrip("/")
    target = f"{bucket}/{urllib.parse.quote(archive.name)}"
    up = request("PUT", target, tok, archive.read_bytes(), "application/octet-stream")
    print(f"  checksum {up.get('checksum')}")

    print("attaching metadata...")
    request("PUT", f"{BASE}/deposit/depositions/{draft_id}", tok,
            json.dumps({"metadata": payload}).encode(), "application/json")

    got = request("GET", f"{BASE}/deposit/depositions/{draft_id}", tok)
    gm = got.get("metadata", {})

    print("\n" + "=" * 70)
    print(f"  draft      {draft_id}")
    print(f"  concept    {got.get('conceptrecid')}")
    print(f"  title      {gm.get('title')}")
    print(f"  version    {gm.get('version')}")
    print(f"  files      {len(got.get('files') or [])}")
    print(f"  edit       https://zenodo.org/deposit/{draft_id}")
    print("=" * 70)

    print("\nread-back:")
    for key in ("title", "version", "license", "description", "notes",
                "creators", "contributors", "keywords", "references",
                "related_identifiers", "communities"):
        sent = payload.get(key)
        stored = gm.get(key)
        if isinstance(sent, list):
            ok = len(sent) == len(stored or [])
            shown = f"{len(stored or [])}/{len(sent)} items"
        elif isinstance(sent, str):
            ok = same_text(sent, stored)
            shown = f"{len(stored or '')}/{len(sent)} chars"
        else:
            ok = sent == stored
            shown = str(stored)
        print(f"  {'ok' if ok else 'DIFF'} {key:<22} {shown}")

    print("\nfields this API will NOT persist (enter in the web form):")
    for key in KNOWN_UNSETTABLE:
        if payload.get(key):
            stored = gm.get(key)
            print(f"  {key}: {'STORED' if stored else 'not stored -> web form'}")

    print("\nDRAFT. Not published. Nothing irreversible has happened.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
