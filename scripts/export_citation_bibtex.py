#!/usr/bin/env python3
"""
UTF-2.0 BibTeX Exporter and References Updater
----------------------------------------------
Converts CITATION.cff → citation.bib
Optionally appends/updates the BibTeX entry inside tex/references.bib
so that Overleaf / arXiv preprints stay citation-synchronized.

Usage:
    python scripts/export_citation_bibtex.py [--append]
"""

import yaml
from datetime import date
from pathlib import Path
import argparse
import re

CITATION_FILE = Path("CITATION.cff")
BIB_FILE = Path("citation.bib")
REFS_FILE = Path("tex/references.bib")

def format_authors(authors):
    """Format authors for BibTeX."""
    if not authors:
        return ""
    formatted = []
    for a in authors:
        fam = a.get("family-names") or a.get("family") or ""
        giv = a.get("given-names") or a.get("name") or ""
        full = f"{fam}, {giv}".strip(", ")
        formatted.append(full)
    return " and ".join(formatted)

def build_bibtex_entry(cff):
    """Build a BibTeX entry from CITATION.cff."""
    authors = format_authors(cff.get("authors", []))
    title = cff.get("title", "Unknown Title")
    year = cff.get("date-released", str(date.today()))[:4]
    doi = cff.get("doi", "")
    version = cff.get("version", "")
    repo = cff.get("repository-code", "")
    commit = cff.get("commit", "")
    key_author = (cff.get("authors", [{}])[0].get("family-names", "UTF2")).lower()
    key = f"{key_author}{year}"

    bib = f"""@misc{{{key},
  author       = {{{authors}}},
  title        = {{{title}}},
  year         = {{{year}}},
  doi          = {{{doi}}},
  version      = {{{version}}},
  url          = {{{repo}}},
  note         = {{Git commit: {commit}}},
  howpublished = {{\\url{{https://doi.org/{doi}}}}}
}}
"""
    return key, bib

def append_to_references(key, bib_entry):
    """Append or update entry in tex/references.bib."""
    if not REFS_FILE.exists():
        REFS_FILE.parent.mkdir(parents=True, exist_ok=True)
        REFS_FILE.write_text("", encoding="utf-8")

    refs = REFS_FILE.read_text(encoding="utf-8")
    pattern = re.compile(rf"@misc\{{{re.escape(key)},.*?\n\}}", re.DOTALL)

    if pattern.search(refs):
        print(f"🧩 Updating existing entry '{key}' in references.bib...")
        refs = pattern.sub(bib_entry.strip(), refs)
    else:
        print(f"➕ Appending new entry '{key}' to references.bib...")
        refs = refs.strip() + "\n\n" + bib_entry

    REFS_FILE.write_text(refs.strip() + "\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Export CITATION.cff → citation.bib and optionally update references.bib.")
    parser.add_argument("--append", action="store_true", help="Also append/update entry in tex/references.bib")
    args = parser.parse_args()

    if not CITATION_FILE.exists():
        raise FileNotFoundError("CITATION.cff not found. Run from repo root.")

    with open(CITATION_FILE, "r", encoding="utf-8") as f:
        cff = yaml.safe_load(f)

    key, bib_entry = build_bibtex_entry(cff)
    BIB_FILE.write_text(bib_entry, encoding="utf-8")
    print(f"✅ Generated {BIB_FILE}")

    if args.append:
        append_to_references(key, bib_entry)
        print(f"📚 references.bib synchronized with DOI entry '{key}'")

    print("\n--- BibTeX Preview ---\n" + bib_entry)

if __name__ == "__main__":
    main()
