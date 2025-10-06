#!/usr/bin/env python3
"""
UTF-2.0 Metadata Consistency Validator
--------------------------------------
Cross-checks DOI, version, and publication date across:
- zenodo.json
- CITATION.cff
- citation.bib
- tex/references.bib

Fails CI if any field is out of sync.

Usage:
    python scripts/validate_metadata_sync.py
"""

import json
import yaml
import re
import sys
from pathlib import Path

ZENODO = Path("zenodo.json")
CITATION = Path("CITATION.cff")
BIB = Path("citation.bib")
REFS = Path("tex/references.bib")

def extract_zenodo():
    data = json.loads(ZENODO.read_text(encoding="utf-8"))
    return {
        "doi": data.get("doi") or data.get("related_identifiers", [{}])[0].get("identifier", ""),
        "version": data.get("version"),
        "publication_date": data.get("publication_date"),
    }

def extract_citation():
    data = yaml.safe_load(CITATION.read_text(encoding="utf-8"))
    return {
        "doi": data.get("doi"),
        "version": data.get("version"),
        "publication_date": data.get("date-released"),
    }

def extract_bib():
    text = BIB.read_text(encoding="utf-8")
    doi = re.search(r"doi\s*=\s*\{([^}]+)\}", text)
    version = re.search(r"version\s*=\s*\{([^}]+)\}", text)
    year = re.search(r"year\s*=\s*\{([^}]+)\}", text)
    return {
        "doi": doi.group(1).strip() if doi else None,
        "version": version.group(1).strip() if version else None,
        "publication_date": year.group(1).strip() if year else None,
    }

def extract_refs():
    if not REFS.exists():
        return {}
    text = REFS.read_text(encoding="utf-8")
    doi = re.search(r"doi\s*=\s*\{([^}]+)\}", text)
    version = re.search(r"version\s*=\s*\{([^}]+)\}", text)
    year = re.search(r"year\s*=\s*\{([^}]+)\}", text)
    return {
        "doi": doi.group(1).strip() if doi else None,
        "version": version.group(1).strip() if version else None,
        "publication_date": year.group(1).strip() if year else None,
    }

def compare_field(field, values):
    """Compare a field across files; return mismatch info."""
    unique_vals = {v for v in values.values() if v}
    if len(unique_vals) > 1:
        return f"❌ Mismatch in '{field}': {values}"
    if not unique_vals:
        return f"⚠️ Missing '{field}' across all files."
    return None

def main():
    missing = [f for f in [ZENODO, CITATION, BIB] if not f.exists()]
    if missing:
        print(f"❌ Missing files: {', '.join(str(m) for m in missing)}")
        sys.exit(1)

    print("🔍 Checking metadata consistency across Zenodo, CITATION.cff, and .bib files...\n")

    sources = {
        "zenodo": extract_zenodo(),
        "citation": extract_citation(),
        "bib": extract_bib(),
        "refs": extract_refs(),
    }

    fields = ["doi", "version", "publication_date"]
    mismatches = []

    for field in fields:
        vals = {k: v.get(field) for k, v in sources.items()}
        result = compare_field(field, vals)
        if result:
            mismatches.append(result)

    if mismatches:
        print("\n".join(mismatches))
        print("\n🚫 Metadata inconsistency detected — please re-run sync scripts before release.")
        sys.exit(1)

    print("✅ All metadata consistent across zenodo.json, CITATION.cff, citation.bib, and references.bib.")

if __name__ == "__main__":
    main()
