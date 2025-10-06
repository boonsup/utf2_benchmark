#!/usr/bin/env python3
"""
UTF-2.0: Manual Zenodo Upload Script
-----------------------------------
Creates a reproducibility bundle (zenodo_utfv2.zip) and uploads it manually
to Zenodo or sandbox. Returns DOI and deposition ID.

Usage:
    python scripts/manual_zenodo_upload.py --sandbox
    python scripts/manual_zenodo_upload.py --publish
"""

import os
import json
import requests
import zipfile
import argparse
from datetime import datetime
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 1. Load environment and configuration
# ---------------------------------------------------------------------------
load_dotenv()
parser = argparse.ArgumentParser(description="Manual Zenodo Upload (UTF-2.0)")
parser.add_argument("--sandbox", action="store_true", help="Use sandbox.zenodo.org")
parser.add_argument("--publish", action="store_true", help="Publish immediately")
args = parser.parse_args()

ZENODO_TOKEN = (
    os.getenv("ZENODO_SANDBOX_TOKEN")
    if args.sandbox
    else os.getenv("ZENODO_TOKEN")
)
if not ZENODO_TOKEN:
    raise SystemExit("❌ Missing Zenodo token in .env file!")

ZENODO_API = "https://sandbox.zenodo.org/api" if args.sandbox else "https://zenodo.org/api"
HEADERS = {"Authorization": f"Bearer {ZENODO_TOKEN}"}

# ---------------------------------------------------------------------------
# 2. Prepare reproducibility ZIP
# ---------------------------------------------------------------------------
BUNDLE_NAME = "zenodo_utfv2.zip"
paths_to_include = [
    "data/f_tuning_history.csv",
    "data/f_sweep_results.csv",
    "figures/",
    "scripts/run_f_tuning.py",
    "src/",
    "PROJECT_PLAN.md",
    "README.md",
    "zenodo.json",
    "CITATION.cff"
]

print(f"📦 Building reproducibility archive: {BUNDLE_NAME}")
with zipfile.ZipFile(BUNDLE_NAME, "w", zipfile.ZIP_DEFLATED) as zipf:
    for path in paths_to_include:
        if os.path.exists(path):
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, ".")
                        zipf.write(full_path, arcname)
                        print(f"  • Added: {arcname}")
            else:
                zipf.write(path)
                print(f"  • Added: {path}")
        else:
            print(f"  ⚠️ Skipped missing: {path}")
print("✅ Archive built successfully.\n")

# ---------------------------------------------------------------------------
# 3. Create new Zenodo deposition
# ---------------------------------------------------------------------------
print("🌐 Creating new deposition on Zenodo...")
r = requests.post(f"{ZENODO_API}/deposit/depositions", headers=HEADERS, json={})
r.raise_for_status()
deposition = r.json()
deposition_id = deposition["id"]
bucket_url = deposition["links"]["bucket"]
print(f"🆔 Deposition created (ID={deposition_id})")

# ---------------------------------------------------------------------------
# 4. Upload ZIP file to deposition bucket
# ---------------------------------------------------------------------------
print("📤 Uploading bundle...")
with open(BUNDLE_NAME, "rb") as fp:
    r = requests.put(
        f"{bucket_url}/{BUNDLE_NAME}",
        data=fp,
        headers={"Authorization": f"Bearer {ZENODO_TOKEN}"},
    )
    r.raise_for_status()
print("✅ Upload complete.")

# ---------------------------------------------------------------------------
# 5. Attach metadata from zenodo.json
# ---------------------------------------------------------------------------
print("🧾 Updating metadata...")
if os.path.exists("zenodo.json"):
    with open("zenodo.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
else:
    metadata = {
        "metadata": {
            "title": "UTF-2.0 Reproducibility Framework",
            "upload_type": "software",
            "description": "Initial reproducible release for UTF-2.0 framework.",
            "creators": [{"name": "Boonsup Waikham", "affiliation": "Independent Science Evangelist"}],
            "version": "v2.0.0-alpha",
            "publication_date": datetime.utcnow().strftime("%Y-%m-%d"),
        }
    }

r = requests.put(
    f"{ZENODO_API}/deposit/depositions/{deposition_id}",
    headers=HEADERS,
    data=json.dumps(metadata),
)
r.raise_for_status()
print("✅ Metadata updated successfully.")

# ---------------------------------------------------------------------------
# 6. Optionally publish
# ---------------------------------------------------------------------------
if args.publish:
    print("🚀 Publishing deposition…")
    r = requests.post(
        f"{ZENODO_API}/deposit/depositions/{deposition_id}/actions/publish",
        headers=HEADERS,
    )
    r.raise_for_status()
    print("✅ Published successfully!")

# ---------------------------------------------------------------------------
# 7. Display deposition info
# ---------------------------------------------------------------------------
r = requests.get(f"{ZENODO_API}/deposit/depositions/{deposition_id}", headers=HEADERS)
deposition_info = r.json()
doi = deposition_info["metadata"].get("prereserve_doi", {}).get("doi", "N/A")
print(f"\n🎯 Deposition complete.")
print(f"   • Deposition ID: {deposition_id}")
print(f"   • DOI: {doi}")
print(f"   • Sandbox: {'Yes' if args.sandbox else 'No'}")
print(f"   • Published: {args.publish}")
print(f"   • Upload: {BUNDLE_NAME}")
print("\nTo view deposition:")
print(f"👉 {ZENODO_API.replace('/api','')}/deposit/{deposition_id}")
