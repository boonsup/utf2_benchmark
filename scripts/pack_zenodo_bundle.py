#!/usr/bin/env python3
"""
pack_zenodo_bundle.py — UTFv2 Reproducibility Bundle Builder (Phase 8)
---------------------------------------------------------------------
Packs code, data, and metadata into zenodo_utfv2.zip, tags commit,
and updates release_manifest.yaml for provenance.
"""

import os, zipfile, json, argparse, subprocess, hashlib, yaml
from datetime import datetime
from pathlib import Path

parser = argparse.ArgumentParser(description="Pack Zenodo reproducibility bundle.")
parser.add_argument("--output", default="dist/zenodo_utfv2.zip", help="Output zip path")
parser.add_argument("--sandbox", action="store_true", help="Mark as Zenodo sandbox bundle")
parser.add_argument("--doi", default=None, help="Zenodo DOI")
parser.add_argument("--ci", action="store_true", help="Run headless (no prompt)")
args = parser.parse_args()

root = Path(__file__).resolve().parents[1]
dist = root / "dist"
dist.mkdir(exist_ok=True)

def get_git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"

commit = get_git_commit()
timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
tag = f"zenodo-{args.doi.split('.')[-1]}" if args.doi else f"zenodo-sandbox-{commit}"

manifest = [
    "data/",
    "figures/",
    "src/",
    "scripts/",
    "utf_metadata.json",
    "zenodo.json",
    "README.md",
    "CITATION.cff",
    "tex/references.bib",
]

zip_path = Path(args.output)
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for item in manifest:
        path = root / item
        if path.is_dir():
            for sub in path.rglob("*"):
                if sub.is_file():
                    zf.write(sub, arcname=sub.relative_to(root))
        elif path.exists():
            zf.write(path, arcname=path.relative_to(root))

sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()
size_MB = round(zip_path.stat().st_size / 1e6, 2)

# === Git tagging ===
if not args.ci:
    confirm = input(f"Tag Git commit {commit} as {tag}? [Y/n] ") or "y"
    if confirm.lower().startswith("y"):
        subprocess.run(["git", "tag", "-a", tag, "-m", f"Zenodo bundle for DOI {args.doi}"])
        subprocess.run(["git", "push", "origin", tag])
else:
    print(f"CI mode: skipping tag (commit {commit}).")

# === Ledger merge ===
ledger_path = dist / "release_manifest.yaml"
if ledger_path.exists():
    ledger = yaml.safe_load(ledger_path)
else:
    ledger = {}

ledger["zenodo"] = {
    "phase": "8.0",
    "package": "zenodo",
    "sandbox": args.sandbox,
    "doi": args.doi,
    "git_commit": commit,
    "timestamp": timestamp,
    "artifact": str(zip_path),
    "sha256": sha256,
    "size_MB": size_MB,
}

with open(ledger_path, "w") as f:
    yaml.safe_dump(ledger, f, sort_keys=False)

print(f"✅ Zenodo bundle built → {zip_path} ({size_MB} MB)")
print(f"📜 Updated ledger → {ledger_path}")
