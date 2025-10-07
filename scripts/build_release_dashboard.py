#!/usr/bin/env python3
"""
build_release_dashboard.py
--------------------------
Appends or updates a "📦 Release Dashboard" section in README.md
listing all Zenodo DOIs, artifact bundles, and commit tags.

Intended for UTFv2 reproducibility verification.
"""

import os
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path
import pandas as pd

README_PATH = Path("README.md")
ZENODO_PATH = Path("zenodo.json")
ARTIFACT_DIR = Path("data")

def get_current_doi():
    """Extract DOI from zenodo.json."""
    if not ZENODO_PATH.exists():
        return None
    try:
        with open(ZENODO_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("doi")
    except Exception:
        return None

def get_git_info():
    """Get commit hash and latest tag."""
    commit = subprocess.getoutput("git rev-parse --short HEAD").strip()
    tag = subprocess.getoutput("git describe --tags --abbrev=0 || echo 'unreleased'").strip()
    return commit, tag

def get_environment(doi: str):
    if not doi:
        return "unknown", "gray"
    if "5072" in doi:
        return "sandbox", "lightgray"
    return "production", "blue"

def find_artifacts():
    """Return list of artifact paths."""
    figures = list(Path("figures").glob("*.png"))
    data = list(Path("data").glob("*.csv")) + list(Path("data").glob("*.json"))
    return figures + data

def build_table_row(doi, commit, tag, env, color, artifacts):
    """Build one Markdown row; tolerate missing DOI."""
    if doi:
        doi_id = doi.split(".")[-1]
        doi_link = f"[{doi}](https://{'sandbox.' if env=='sandbox' else ''}zenodo.org/record/{doi_id})"
    else:
        doi_link = "—"

    badge_url = f"https://img.shields.io/badge/{env.upper()}-DOI-{color}?logo=zenodo"
    commit_link = f"[`{commit}`](https://github.com/${{ github.repository }}/commit/{commit})"
    artifact_links = (
        " / ".join([f"[{p.name}](./{p})" for p in artifacts[:3]]) if artifacts else "—"
    )

    return f"| {tag} | {doi_link} | ![]({badge_url}) | {commit_link} | {artifact_links} |"


def update_readme_table():
    """Insert or update the dashboard section in README.md."""
    readme = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
    header = "## 📦 Release Dashboard"
    table_header = (
        "| Release | DOI | Status | Commit | Artifacts |\n"
        "|----------|-----|--------|---------|------------|"
    )

    doi = get_current_doi()
    commit, tag = get_git_info()
    env, color = get_environment(doi)
    artifacts = find_artifacts()

    # if no DOI, mark row as draft
    if not doi:
        print("⚠️ No DOI found in zenodo.json — adding draft entry.")
        doi = "unpublished"

    new_row = build_table_row(doi, commit, tag, env, color, artifacts)

    if header in readme:
        pattern = rf"(\| {re.escape(tag)} \|[^\n]*)"
        if re.search(pattern, readme):
            readme = re.sub(pattern, new_row, readme)
        else:
            readme = re.sub(r"(\|[-]+[\s\S]*?)\Z", r"\1\n" + new_row, readme)
    else:
        readme += f"\n\n{header}\n\n{table_header}\n{new_row}\n"

    README_PATH.write_text(readme, encoding="utf-8")
    print(f"✅ Updated README with release dashboard row for {tag} ({env}).")


if __name__ == "__main__":
    update_readme_table()
