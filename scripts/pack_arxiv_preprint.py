#!/usr/bin/env python3
"""
pack_arxiv_preprint.py — UTFv2 arXiv Preprint Packager (Phase 8)
----------------------------------------------------------------
Collects TeX + figures + metadata into an arXiv-ready archive,
tags current Git commit, and writes release_manifest.yaml.
"""

import os, tarfile, argparse, subprocess, hashlib, yaml
from datetime import datetime
from pathlib import Path

parser = argparse.ArgumentParser(description="Pack arXiv preprint bundle for UTFv2.")
parser.add_argument("--version", default="v1.0", help="Version tag (e.g. v1.0)")
parser.add_argument("--doi", default=None, help="Zenodo DOI for cross-link")
parser.add_argument("--output", default="dist/arxiv_utfv2.tar.gz", help="Output archive path")
parser.add_argument("--ci", action="store_true", help="Run headless (no prompt)")
args = parser.parse_args()

root = Path(__file__).resolve().parents[1]
dist = root / "dist"
dist.mkdir(exist_ok=True)

# === Git info ===
def get_git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"

commit = get_git_commit()
git_tag = f"arxiv-{args.version}"
timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

# === Manifest build ===
manifest = [
    "main.tex",
    "tex/references.bib",
    "tex/supplementary_s1_kernel.tex",
    "tex/supplementary_s2_latency.tex",
    "tex/supplementary_s3_appendix.tex",
    "tex/supplementary_s4_s6.tex",
    "tex/supplementary_summary.tex",
    "tex/main_supplementary_arxiv.tex",
    "figures/",
]

readme_text = f"""UTFv2 — arXiv Preprint Package
----------------------------------
Version: {args.version}
DOI: {args.doi or 'N/A'}
Git commit: {commit}
Date: {timestamp}
"""

(dist / "README_arxiv.txt").write_text(readme_text)

tar_path = Path(args.output)
with tarfile.open(tar_path, "w:gz") as tar:
    for item in manifest:
        path = root / item
        if path.exists():
            tar.add(path, arcname=path.relative_to(root))
    tar.add(dist / "README_arxiv.txt", arcname="README_arxiv.txt")

sha256 = hashlib.sha256(tar_path.read_bytes()).hexdigest()
size_MB = round(tar_path.stat().st_size / 1e6, 2)

# === Git tag ===
if not args.ci:
    confirm = input(f"Tag Git commit {commit} as {git_tag}? [Y/n] ") or "y"
    if confirm.lower().startswith("y"):
        subprocess.run(["git", "tag", "-a", git_tag, "-m", f"arXiv preprint {args.version}"])
        subprocess.run(["git", "push", "origin", git_tag])
else:
    print(f"CI mode: tagging skipped (commit {commit}).")

# === Ledger output ===
ledger = {
    "phase": "8.0",
    "package": "arxiv",
    "version": args.version,
    "git_commit": commit,
    "zenodo_doi": args.doi,
    "timestamp": timestamp,
    "artifact": str(tar_path),
    "sha256": sha256,
    "size_MB": size_MB,
}

yaml_path = dist / "release_manifest.yaml"
with open(yaml_path, "w") as f:
    yaml.safe_dump({"arxiv": ledger}, f, sort_keys=False)

print(f"✅ arXiv package built → {tar_path} ({size_MB} MB)")
print(f"📜 Ledger written → {yaml_path}")
