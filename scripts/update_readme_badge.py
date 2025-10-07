#!/usr/bin/env python3
"""
UTF-2.0 | README Auto-Updater
Inserts or updates the Zenodo DOI badge and the latest version plot.
"""

import re, os, subprocess
from datetime import datetime
from pathlib import Path

README = Path("README.md")
BADGE = Path("release_badge.svg")
PLOT = Path("figures/f_tuning_latest.png")

def get_commit_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"

def insert_badge_and_plot():
    if not README.exists():
        print("❌ README.md not found.")
        return

    content = README.read_text(encoding="utf-8")

    # Badge line
    badge_block = f"\n\n[![DOI](https://zenodo.org/badge/latestdoi/123456789.svg)](https://doi.org/10.5281/zenodo.latest)\n"
    content = re.sub(r"\[!\[DOI\]\(.*?\)\]\(.*?\)", badge_block.strip(), content) if "DOI" in content else content + badge_block

    # Plot embedding
    if PLOT.exists():
        img_tag = f"![Latest UTF-2.0 Stability Plot]({PLOT.as_posix()})"
        if "Latest UTF-2.0 Stability Plot" in content:
            content = re.sub(r"!\[Latest UTF-2\.0 Stability Plot\]\(.*?\)", img_tag, content)
        else:
            content += f"\n\n## Stability Visualization\n{img_tag}\n"

    README.write_text(content, encoding="utf-8")
    print(f"✅ Updated README.md → added DOI badge + latest plot @ {datetime.utcnow()}")

if __name__ == "__main__":
    insert_badge_and_plot()
