#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UTF-2.0 — DOI Auto-Sync Utility
Updates README.md, CITATION.cff, zenodo.json, and references.bib
with a newly minted DOI. Creates .bak backups before modifying files.

Usage examples:
  python scripts/update_doi_references.py --doi 10.5072/zenodo.344960 --sandbox
  python scripts/update_doi_references.py --doi 10.5281/zenodo.1234567
  python scripts/update_doi_references.py --doi 10.5281/zenodo.1234567 --dry-run
"""

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# ---------- Helpers ----------

def backup_file(p: Path):
    if p.exists():
        bak = p.with_suffix(p.suffix + ".bak")
        shutil.copyfile(p, bak)
        print(f"  • Backup created: {bak.name}")

def write_if_changed(path: Path, new_content: str, dry_run: bool) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == new_content:
        print(f"  • No changes needed: {path}")
        return False
    if dry_run:
        print(f"  • [DRY-RUN] Would update: {path}")
        return True
    backup_file(path)
    path.write_text(new_content, encoding="utf-8", newline="\n")
    print(f"  ✓ Updated: {path}")
    return True

def doi_to_badge(doi: str, sandbox: bool) -> str:
    host = "sandbox.zenodo.org" if sandbox else "zenodo.org"
    return f"[![DOI](https://{host}/badge/DOI/{doi}.svg)](https://doi.org/{doi})"

def normalize_newlines(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")

# ---------- README.md ----------

def update_readme(readme_path: Path, doi: str, sandbox: bool, dry_run: bool) -> bool:
    print(f"\n🔧 Updating README: {readme_path}")
    badge_md = doi_to_badge(doi, sandbox)
    content = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

    content = normalize_newlines(content)
    badge_pattern = re.compile(
        r"\[!\[DOI\]\(https?://(?:sandbox\.)?zenodo\.org/badge/DOI/[^)]+\.svg\)\]\(https?://doi\.org/[^)]+\)"
    )

    if badge_pattern.search(content):
        new_content = badge_pattern.sub(badge_md, content)
    else:
        # Insert at very top, separated by a blank line
        new_content = f"{badge_md}\n\n{content}" if content else f"{badge_md}\n"

    return write_if_changed(readme_path, new_content, dry_run)

# ---------- CITATION.cff (YAML-ish, line edit) ----------

def update_citation_cff(cff_path: Path, doi: str, dry_run: bool) -> bool:
    print(f"\n🔧 Updating CITATION.cff: {cff_path}")
    lines = []
    if cff_path.exists():
        lines = normalize_newlines(cff_path.read_text(encoding="utf-8")).split("\n")

    if not lines:
        # Minimal CFF skeleton
        lines = [
            "cff-version: 1.2.0",
            "message: Please cite this repository using the DOI below.",
            "title: UTF-2.0 Reproducibility Framework",
            "type: software",
        ]

    # Ensure identifiers section exists, update/add DOI
    # Strategy: if 'identifiers:' exists, replace or append DOI entry; else create it.
    content = "\n".join(lines)
    if "identifiers:" in content:
        # Replace existing DOI or append under identifiers
        # 1) Try replacing an existing DOI line in identifiers block
        pattern = re.compile(r"(identifiers:\s*(?:\n\s*-\s*type:.*\n(?:\s+.*\n)*)*)", re.M)
        # safer approach: rebuild identifiers block
        lines = content.split("\n")
        out = []
        in_ident = False
        found_doi = False
        i = 0
        while i < len(lines):
            line = lines[i]
            if re.match(r"^\s*identifiers:\s*$", line):
                in_ident = True
                out.append(line)
                i += 1
                # collect block
                while i < len(lines) and (lines[i].strip().startswith("-") or lines[i].startswith("  ")):
                    # copy through, but remember DOI entries
                    if re.search(r"^\s*-\s*type:\s*doi\s*$", lines[i]):
                        found_doi = True
                        # skip possible following 'value:' line(s) for doi; we’ll inject our own
                        out.append(lines[i])  # keep the type line
                        i += 1
                        # If next line is value, replace it
                        if i < len(lines) and re.search(r"^\s*value:\s*", lines[i]):
                            out.append(f"  value: {doi}")
                            i += 1
                        else:
                            out.append(f"  value: {doi}")
                    else:
                        out.append(lines[i])
                        i += 1
                if not found_doi:
                    out.append("  - type: doi")
                    out.append(f"    value: {doi}")
                # continue without losing context
                continue
            else:
                in_ident = False
                out.append(line)
                i += 1
        new_content = "\n".join(out)
    else:
        # append identifiers block
        new_content = content.rstrip("\n") + "\n" + "\n".join([
            "identifiers:",
            "  - type: doi",
            f"    value: {doi}",
        ]) + "\n"

    return write_if_changed(cff_path, new_content, dry_run)

# ---------- zenodo.json ----------

def update_zenodo_json(zjson_path: Path, doi: str, dry_run: bool) -> bool:
    print(f"\n🔧 Updating zenodo.json: {zjson_path}")
    data = {}
    if zjson_path.exists():
        try:
            data = json.loads(zjson_path.read_text(encoding="utf-8"))
        except Exception:
            print("  ! zenodo.json not valid JSON; rebuilding minimal structure.")
            data = {}
    if "metadata" not in data:
        data["metadata"] = {}
    data["metadata"]["doi"] = doi
    data["metadata"].setdefault("version", "v2.0.0-alpha")
    data["metadata"].setdefault("publication_date", datetime.utcnow().strftime("%Y-%m-%d"))
    new_content = json.dumps(data, indent=2) + "\n"
    return write_if_changed(zjson_path, new_content, dry_run)

# ---------- references.bib ----------

BIB_TEMPLATE = """@misc{{utf2,
  title        = {{UTF-2.0 Reproducibility Framework}},
  author       = {{Waikham, Boonsup}},
  year         = {{{year}}},
  doi          = {{{doi}}},
  howpublished = {{Zenodo}},
  url          = {{https://doi.org/{doi}}}
}}
"""

def update_references_bib(bib_path: Path, doi: str, dry_run: bool) -> bool:
    print(f"\n🔧 Updating references.bib: {bib_path}")
    year = datetime.utcnow().year
    if not bib_path.exists():
        new_content = BIB_TEMPLATE.format(doi=doi, year=year)
        return write_if_changed(bib_path, new_content, dry_run)

    content = normalize_newlines(bib_path.read_text(encoding="utf-8"))
    # Replace DOI inside @misc{utf2,...} if exists; else append a new entry.
    entry_pattern = re.compile(r"@misc\s*\{\s*utf2\s*,.*?\}\s*", re.S | re.I)
    doi_line_pattern = re.compile(r"(doi\s*=\s*\{)([^}]*)(\})", re.I)

    if entry_pattern.search(content):
        def _repl(entry: re.Match) -> str:
            block = entry.group(0)
            if doi_line_pattern.search(block):
                block = doi_line_pattern.sub(rf"\1{doi}\3", block)
            else:
                # inject DOI before closing brace
                block = block.rstrip("}\n")
                block += f",\n  doi          = {{{doi}}}\n}}\n"
            # also update url if present
            block = re.sub(r"(url\s*=\s*\{)https?://doi\.org/[^}]+(\})",
                           rf"\1https://doi.org/{doi}\2", block, flags=re.I)
            # update year if missing
            if "year" not in block.lower():
                block = block.rstrip("}\n")
                block += f",\n  year         = {{{year}}}\n}}\n"
            return block
        new_content = entry_pattern.sub(_repl, content)
    else:
        # append new entry with a separating blank line
        addition = ("\n" if not content.endswith("\n") else "") + BIB_TEMPLATE.format(doi=doi, year=year)
        new_content = content + addition

    return write_if_changed(bib_path, new_content, dry_run)

# ---------- Main ----------

def main():
    ap = argparse.ArgumentParser(description="Sync DOI across README.md, CITATION.cff, zenodo.json, references.bib")
    ap.add_argument("--doi", required=True, help="The DOI to insert/update (e.g., 10.5281/zenodo.1234567)")
    ap.add_argument("--sandbox", action="store_true", help="Use sandbox badge host (sandbox.zenodo.org)")
    ap.add_argument("--dry-run", action="store_true", help="Print changes without writing files")
    ap.add_argument("--readme", default="README.md", help="Path to README.md")
    ap.add_argument("--cff", default="CITATION.cff", help="Path to CITATION.cff")
    ap.add_argument("--zenodo", default="zenodo.json", help="Path to zenodo.json")
    ap.add_argument("--bib", default="tex/references.bib", help="Path to references.bib (default: tex/references.bib)")
    args = ap.parse_args()

    # Validate DOI shape minimally
    if not re.match(r"^10\.\d{4,9}/\S+$", args.doi):
        print(f"⚠️  DOI format looks unusual: {args.doi}. Continuing anyway…")

    changed = []
    changed.append(update_readme(Path(args.readme), args.doi, args.sandbox, args.dry_run))
    changed.append(update_citation_cff(Path(args.cff), args.doi, args.dry_run))
    changed.append(update_zenodo_json(Path(args.zenodo), args.doi, args.dry_run))
    changed.append(update_references_bib(Path(args.bib), args.doi, args.dry_run))

    any_changed = any(changed)
    print("\nSummary:")
    print(f"  Changes applied: {any_changed and not args.dry_run}")
    print(f"  Dry-run: {args.dry_run}")

if __name__ == "__main__":
    main()
