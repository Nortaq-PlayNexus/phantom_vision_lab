#!/usr/bin/env python3
"""Create the Zenodo deposit for ScientificDiscoveryLab.

Draft-first by default. The deposit is created and the archive uploaded, but
nothing is published unless --publish is passed, because publishing mints an
immutable DOI and cannot be undone.

Two things this script will not do, deliberately:

  * It never deletes a deposit. Earlier sessions created orphan deposits while
    learning the API's shape and then removed them. Each one is a real record
    with a real ID, and "cleaning up" is not something to do automatically. If a
    deposit needs discarding, say so out loud and do it deliberately.

  * It never publishes without --publish.

Zenodo's API requires every metadata field nested under a `metadata` key. A flat
payload is rejected with "Unknown field" for every key at once, which reads like
the API being broken rather than the payload being wrong.

Usage:
    python zenodo/upload_to_zenodo.py --metadata zenodo/metadata.json \\
        --archive zenodo/ScientificDiscoveryLab-v1.0.0.zip
    python zenodo/upload_to_zenodo.py ... --publish
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import hashlib
import urllib.parse
import urllib.request
import urllib.error

HERE = Path(__file__).resolve().parent
TOKEN_FILE = HERE / ".zenodo_token"
BASE = "https://zenodo.org/api"


def token() -> str:
    """Find the Zenodo token.

    One token serves every deposit on this account, so it lives once, in the
    ScientificDiscoveryLab repository. Both locations are checked, then the
    environment. A hard failure here after the archive has been built and
    verified is an annoying way to learn about a missing file.
    """
    candidates = [
        TOKEN_FILE,
        Path(r"C:\Users\natha\ScientificDiscoveryLab\zenodo\.zenodo_token"),
    ]
    env = os.environ.get("ZENODO_TOKEN")
    if env:
        return env.strip()
    for candidate in candidates:
        if candidate.is_file():
            value = candidate.read_text(encoding="utf-8").strip()
            if value:
                return value
    sys.exit(
        "ERROR: no Zenodo token found. Looked in:\n"
        + "".join(f"  {c}\n" for c in candidates)
        + "Set ZENODO_TOKEN, or create one at\n"
        "  https://zenodo.org/account/settings/applications/tokens/new"
    )


def request(method: str, url: str, tok: str, body: bytes | None = None,
            content_type: str | None = None) -> dict:
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {tok}")
    if content_type:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:2000]
        sys.exit(f"HTTP {exc.code} on {method} {url}\n{detail}")
    except urllib.error.URLError as exc:
        sys.exit(f"network error: {exc}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def build_metadata(meta: dict, description: str) -> dict:
    """Wrap the local metadata.json in the shape the API accepts.

    Every key goes inside `metadata`. A flat payload is rejected with "Unknown
    field" once per key, which reads like a broken API rather than a wrong shape.

    Optional blocks are included only when the local metadata defines them, so a
    field that Zenodo does not accept costs nothing to leave out -- and a rejected
    PUT would discard the whole update, including the fields that did validate.
    """
    payload: dict = {
        "upload_type": meta["upload_type"],
        "title": meta["title"],
        "description": description,
        "version": meta["version"],
        "license": meta["license"],
        "language": meta.get("language", "eng"),
        "creators": [
            {"name": c["name"], "affiliation": c.get("affiliation", "independent")}
            for c in meta["creators"]
        ],
        "keywords": meta["keywords"],
        "related_identifiers": meta.get("related_identifiers", []),
        "notes": meta["notes"],
    }

    if "access_right" in meta:
        payload["access_right"] = meta["access_right"]
    if "subjects" in meta:
        # Controlled vocabulary. The identifier is authoritative; Zenodo fills the
        # title from its own list, and a guessed id is worse than none because it
        # silently classifies the work under the wrong subject.
        payload["subjects"] = [{"id": s["id"]} for s in meta["subjects"]]
    if "communities" in meta:
        payload["communities"] = [{"identifier": c["id"]} for c in meta["communities"]]
    if "references" in meta:
        payload["references"] = meta["references"]
    if meta.get("grants"):
        payload["grants"] = meta["grants"]

    return payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--description", required=True)
    ap.add_argument("--archive", required=True)
    ap.add_argument("--reuse", type=int, default=None,
                    help="resume an existing deposit id instead of creating one. "
                         "Use this after a partial failure so no deposit is "
                         "orphaned; never delete a deposit to recover from one.")
    ap.add_argument("--publish", action="store_true",
                    help="publish immediately (mints an immutable DOI)")
    args = ap.parse_args()

    tok = token()
    meta = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
    description = Path(args.description).read_text(encoding="utf-8")
    archive = Path(args.archive).resolve()

    print(f"archive : {archive.name}  ({archive.stat().st_size:,} bytes)")
    print(f"sha256  : {sha256_file(archive)}")
    print(f"title   : {meta['title']}")

    # 1. obtain the deposition.
    #    Only `metadata` is accepted here. Passing a sibling `bucket` key -- which
    #    some examples show -- is rejected with "Unknown field", the same error a
    #    completely flat payload produces for every key at once.
    if args.reuse:
        print(f"\nresuming deposit {args.reuse}")
        dep = request("GET", f"{BASE}/deposit/depositions/{args.reuse}", tok)
    else:
        print("\ncreating deposition...")
        dep = request("POST", f"{BASE}/deposit/depositions", tok,
                      json.dumps({"metadata": {}}).encode(),
                      "application/json")
    dep_id = dep["id"]
    print(f"  id {dep_id}")
    print(f"  bucket {dep['links']['bucket']}")

    # 2. upload the archive.
    #    The bucket is a PUT target, not a POST target, and the filename must be
    #    part of the path. POSTing to the bare bucket returns 405 Method Not
    #    Allowed, which reads like a permissions problem rather than a verb
    #    mismatch.
    print("\nuploading archive...")
    bucket = dep["links"]["bucket"].rstrip("/")
    target = f"{bucket}/{urllib.parse.quote(archive.name)}"
    #     The bucket accepts only application/octet-stream. Sending
    #     application/zip returns 415 with the expected value spelled out.
    uploaded = request("PUT", target, tok, archive.read_bytes(),
                       "application/octet-stream")
    print(f"  file id {uploaded.get('id')}  checksum {uploaded.get('checksum')}")

    # 3. attach metadata
    print("\nattaching metadata...")
    body = json.dumps({"metadata": build_metadata(meta, description)}).encode()
    updated = request("PUT", f"{BASE}/deposit/depositions/{dep_id}", tok, body,
                      "application/json")
    print(f"  state: {updated.get('state', 'n/a')}")

    print("\n" + "=" * 70)
    print(f"DEPOSIT {dep_id}")
    print(f"  edit   https://zenodo.org/deposit/{dep_id}")
    print(f"  local  C:\\Users\\natha\\ScientificDiscoveryLab\\zenodo\\DEPOSIT_{dep_id}.txt")
    print("=" * 70)

    record = {
        "id": dep_id,
        "bucket": dep["links"]["bucket"],
        "file_id": uploaded.get("id"),
        "checksum": uploaded.get("checksum"),
        "archive": archive.name,
        "archive_bytes": archive.stat().st_size,
        "archive_sha256": sha256_file(archive),
        "title": meta["title"],
        "version": meta["version"],
        "published": bool(args.publish),
        "created": "2026-10-03",
    }
    out = HERE / f"DEPOSIT_{dep_id}.txt"
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    if args.publish:
        print("\npublishing...")
        pub = request(
            "POST", f"{BASE}/deposit/depositions/{dep_id}/actions/publish", tok,
            b"", "application/json")
        print(f"  DOI: {pub.get('doi')}")
        print(f"  concept DOI: {pub.get('conceptdoi')}")
        record["published"] = True
        record["doi"] = pub.get("doi")
        record["concept_doi"] = pub.get("conceptdoi")
        out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    else:
        print("\nDRAFT. Nothing published, no DOI minted.")
        print("Publish at the edit URL above when ready.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
