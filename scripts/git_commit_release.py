#!/usr/bin/env python3
"""
git_commit_release.py — Unified release automation helper
with optional CI mode for non-interactive use.

Usage:
  python scripts/git_commit_release.py         # interactive mode
  python scripts/git_commit_release.py --ci --tag v2.0.0   # CI mode (headless)
"""

import os
import re
import subprocess
import json
from datetime import datetime
from pathlib import Path
import argparse

# Paths & config
ZENODO_FILE = Path("zenodo.json")
CITATION_FILE = Path("CITATION.cff")
README_FILE = Path("README.md")
REFERENCE_FILE = Path("tex/references.bib")
WORKFLOWS = [
    ".github/workflows/test_and_publish.yaml",
    ".github/workflows/zenodo_sync.yaml",
    ".github/workflows/zenodo_sync.yml",
]

def run(cmd, cwd=None, capture=False):
    if capture:
        return subprocess.check_output(cmd, shell=True, cwd=cwd, text=True).strip()
    else:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)

def get_doi():
    if not ZENODO_FILE.exists():
        return None
    try:
        data = json.loads(ZENODO_FILE.read_text(encoding="utf-8"))
        return data.get("metadata", {}).get("doi", None)
    except Exception:
        return None

def detect_environment(doi):
    if doi is None:
        return "unknown"
    return "sandbox" if doi.startswith("10.5072") else "production"

def stage_files():
    tracked = [
        "CITATION.cff",
        "PROJECT_PLAN.md",
        "zenodo.json",
        "tex/references.bib",
        "notebooks/utf_main.ipynb",
        *WORKFLOWS,
        "scripts/update_doi_references.py",
        "scripts/auto_embed_figures.py",
        "scripts/auto_insert_doi_snapshot.py",
        "zenodo_upload.py",
        "manual_zenodo_upload.py",
    ]
    for f in tracked:
        if Path(f).exists():
            run(f"git add {f}")
    print("✅ Staged reproducibility + workflow files.")

def summarize_changes():
    print("\n📋 Staged diff summary:")
    try:
        diff = run("git diff --cached --stat", capture=True)
        print(diff or "(no changes)")
    except subprocess.CalledProcessError:
        print("(no changes)")

def confirm(prompt="Proceed with commit? (y/N): ", ci=False):
    if ci:
        print(f"⚙️ CI mode: automatically confirm.")
        return True
    ans = input(prompt).strip().lower()
    return ans in ("y", "yes")

def make_commit(doi, env):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"🔁 UTFv2 Auto-Commit ({env}) DOI={doi or 'none'} at {timestamp}"
    run(f'git commit -m "{msg}"')
    print(f"✅ Created commit: {msg}")

def push_branch(env, tag=None):
    if env == "sandbox":
        branch = "zenodo-dryrun"
        print("🌱 Sandbox DOI → pushing to branch:", branch)
        run(f"git checkout -B {branch}")
        run(f"git push origin {branch} --force")
    else:
        print("🚀 Production push → pushing to main")
        run("git push origin main")

    if tag:
        tag_msg = f"UTFv2 release {tag} [{env}]"
        run(f'git tag -a {tag} -m "{tag_msg}"')
        run(f"git push origin {tag}")
        print(f"🏷️ Tagged release: {tag}")

def main():
    parser = argparse.ArgumentParser(description="Automate staging / commit / push for UTFv2 releases.")
    parser.add_argument("--ci", action="store_true", help="Run in CI (non-interactive mode)")
    parser.add_argument("--tag", default=None, help="Optional release tag (e.g. v2.0.0)")
    args = parser.parse_args()

    doi = get_doi()
    env = detect_environment(doi)
    print("📘 Detected DOI:", doi)
    print("🌍 Release environment:", env)

    # Stage, diff, confirm
    stage_files()
    summarize_changes()
    if not confirm(ci=args.ci):
        print("Aborted (no commit).")
        return

    # Commit
    make_commit(doi, env)

    # Push & Tag
    push_branch(env, tag=args.tag)

    print("\n🎉 Release script done.")

if __name__ == "__main__":
    main()
