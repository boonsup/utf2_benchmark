#!/usr/bin/env python3
"""
UTF-2.0 CITATION.cff Synchronizer
---------------------------------
Pulls latest Zenodo metadata (creators/contributors) and merges it into
CITATION.cff, preserving local ORCID, affiliation, and role fields.

Usage:
    python scripts/update_citation_from_zenodo.py --token $ZENODO_TOKEN
"""

import argparse
import requests
import yaml
from datetime import date
from pathlib import Path

CITATION_PATH = Path("CITATION.cff")

# -----------------------------------------------------------------------------
# Utility helpers
# -----------------------------------------------------------------------------

def fetch_latest_zenodo_metadata(token: str):
    """Fetch latest Zenodo deposition metadata."""
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://zenodo.org/api/deposit/depositions?size=1"
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()[0]
    dep_id = data["id"]

    full_url = f"https://zenodo.org/api/deposit/depositions/{dep_id}"
    resp = requests.get(full_url, headers=headers, timeout=15)
    resp.raise_for_status()
    meta = resp.json()["metadata"]

    return {
        "doi": meta.get("doi"),
        "version": meta.get("version"),
        "creators": meta.get("creators", []),
        "contributors": meta.get("contributors", []),
        "publication_date": meta.get("publication_date", str(date.today())),
    }


def merge_people(local_list, zenodo_list, role_key=None):
    """
    Merge people lists (authors/contributors) preserving local fields.

    - Matching rule: match by family and given names.
    - Preserve local ORCID and affiliation if Zenodo doesn't have them.
    - Add new entries from Zenodo if not already present.
    """
    def normalize_name(p):
        return (p.get("family-names") or p.get("family") or "").lower(), \
               (p.get("given-names") or p.get("name") or "").lower()

    merged = {normalize_name(p): p for p in local_list}

    for z in zenodo_list:
        fam = z.get("family") or z.get("family-names")
        giv = z.get("name") or z.get("given-names")
        key = (fam.lower(), giv.lower())

        entry = merged.get(key, {"family-names": fam, "given-names": giv})

        # Merge fields carefully
        for k_local, k_remote in [
            ("affiliation", "affiliation"),
            ("orcid", "orcid"),
            ("email", "email")
        ]:
            if k_remote in z and z[k_remote]:
                entry[k_local] = z[k_remote]

        if role_key and "roles" not in entry:
            entry["roles"] = [role_key]

        merged[key] = entry

    return list(merged.values())


def update_citation(citation_data, zen_meta):
    """Merge Zenodo metadata into local CITATION.cff structure."""
    citation_data["doi"] = zen_meta["doi"]
    citation_data["version"] = zen_meta["version"]
    citation_data["date-released"] = zen_meta["publication_date"]

    # Merge creators → authors
    local_authors = citation_data.get("authors", [])
    merged_authors = merge_people(local_authors, zen_meta["creators"])
    citation_data["authors"] = sorted(merged_authors, key=lambda x: x.get("family-names", ""))

    # Merge contributors
    local_contribs = citation_data.get("contributors", [])
    merged_contribs = merge_people(local_contribs, zen_meta["contributors"], role_key="software")
    citation_data["contributors"] = sorted(merged_contribs, key=lambda x: x.get("family-names", ""))

    return citation_data


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Sync CITATION.cff with latest Zenodo metadata.")
    parser.add_argument("--token", required=True, help="Zenodo API token with deposit:read scope")
    args = parser.parse_args()

    if not CITATION_PATH.exists():
        raise FileNotFoundError("CITATION.cff not found. Run from repo root.")

    with open(CITATION_PATH, "r", encoding="utf-8") as f:
        citation_data = yaml.safe_load(f)

    zen_meta = fetch_latest_zenodo_metadata(args.token)
    print(f"🔗 Synced metadata from DOI {zen_meta['doi']} (version {zen_meta['version']})")

    updated = update_citation(citation_data, zen_meta)

    with open(CITATION_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(updated, f, sort_keys=False)

    print("✅ CITATION.cff updated and synchronized with Zenodo metadata.")


if __name__ == "__main__":
    main()
