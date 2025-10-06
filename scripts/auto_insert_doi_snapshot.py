#!/usr/bin/env python3
"""
UTF-2.0 — Auto-Insert DOI Badge & Reproducibility Snapshot
----------------------------------------------------------
Updates README.md after each Zenodo upload with:
  • DOI badge (sandbox or production)
  • Git commit hash
  • Mean α, β, λ values from utf_metadata.json
  • Publication timestamp
"""

import os, json, re
from pathlib import Path
from datetime import datetime

README = Path("README.md")
META_PATH = Path("data/utf_metadata.json")

SECTION_HEADER = "## 📊 Latest Benchmarks"
SNAPSHOT_HEADER = "### 🧬 Reproducibility Snapshot"

def load_metadata():
    if not META_PATH.exists():
        raise FileNotFoundError(f"❌ Missing metadata: {META_PATH}")
    meta = json.load(open(META_PATH, "r", encoding="utf-8"))
    return meta

def make_snapshot_block(meta):
    doi = meta.get("zenodo_doi", "unassigned")
    commit = meta.get("git_commit", "unknown")
    alpha = meta.get("mean_alpha", 0)
    beta = meta.get("mean_beta", 0)
    lam = meta.get("mean_lambda", 0)
    date = meta.get("timestamp", datetime.utcnow().isoformat())

    doi_badge = f"[![DOI](https://zenodo.org/badge/DOI/{doi}.svg)](https://doi.org/{doi})"

    block = f"""{SNAPSHOT_HEADER}

> **UTF-2.0 Reproducibility Snapshot**  
> {doi_badge}  
> Commit: `{commit}`  
> **ᾱ = {alpha:.4f}**, **β̄ = {beta:.3f}**, **λ̄ = {lam:.3f}**  
> *(Published: {date[:10]} UTC)*
"""
    return block

def update_readme():
    if not README.exists():
        print("⚠️ README.md not found — skipping.")
        return

    text = README.read_text(encoding="utf-8")
    meta = load_metadata()
    block = make_snapshot_block(meta)

    # If snapshot already exists, replace it
    pattern = re.compile(rf"{SNAPSHOT_HEADER}.*?(?=\n## |\Z)", re.S)
    if pattern.search(text):
        new_text = pattern.sub(block.strip() + "\n", text)
    else:
        # Insert after “📊 Latest Benchmarks”
        insertion_pattern = re.compile(rf"{SECTION_HEADER}.*?(?=\n## |\Z)", re.S)
        if insertion_pattern.search(text):
            new_text = insertion_pattern.sub(lambda m: m.group(0) + "\n\n" + block, text)
        else:
            new_text = text.rstrip() + "\n\n" + block

    if new_text != text:
        README.write_text(new_text, encoding="utf-8", newline="\n")
        print("✅ README.md updated with DOI snapshot.")
    else:
        print("ℹ️ No update needed — snapshot already up-to-date.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--color", default="blue", help="Badge color (blue=production, gray=sandbox)")
    args = parser.parse_args()

    # inside make_snapshot_block(meta):
    badge_color = args.color
    doi_badge = f"[![DOI](https://img.shields.io/badge/DOI-{doi}-{badge_color}?logo=zenodo)](https://doi.org/{doi})"


    update_readme()
