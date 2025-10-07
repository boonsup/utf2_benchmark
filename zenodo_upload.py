#!/usr/bin/env python3
"""
UTF-2.0 | Zenodo Multi-File Upload Automation
OAuth2 Client-Credential Flow + Sandbox + Reproducibility Bundle Support

Usage:
    python scripts/zenodo_upload.py --sandbox
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# ----------------------------------------------------------------------
# Load environment variables
# ----------------------------------------------------------------------
load_dotenv()

ZENODO_API = "https://zenodo.org/api"
ZENODO_SANDBOX_API = "https://sandbox.zenodo.org/api"


from dotenv import load_dotenv, set_key

def get_access_token(sandbox=False):
    """
    Obtain and persist an OAuth2 token using Zenodo's /oauth/token endpoint.
    Supports client_credentials, authorization_code, and refresh_token flows.
    Automatically saves and reuses refresh tokens for future runs.
    """

    env_path = Path(".env")
    load_dotenv(dotenv_path=env_path)

    base_url = "https://sandbox.zenodo.org" if sandbox else "https://zenodo.org"
    token_url = f"{base_url}/oauth/token"

    client_id = os.getenv("ZENODO_CLIENT_ID")
    client_secret = os.getenv("ZENODO_CLIENT_SECRET")
    refresh_token = (
        os.getenv("ZENODO_SANDBOX_REFRESH_TOKEN")
        if sandbox
        else os.getenv("ZENODO_REFRESH_TOKEN")
    )
    auth_code = os.getenv("ZENODO_AUTH_CODE")
    redirect_uri = os.getenv("ZENODO_REDIRECT_URI", "https://localhost/callback")
    scope = "deposit:write deposit:actions"

    if not client_id or not client_secret:
        raise EnvironmentError("❌ Missing ZENODO_CLIENT_ID or ZENODO_CLIENT_SECRET")

    # --- Determine flow ---
    if refresh_token:
        grant_type = "refresh_token"
        payload = {
            "grant_type": grant_type,
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }
    elif auth_code:
        grant_type = "authorization_code"
        payload = {
            "grant_type": grant_type,
            "code": auth_code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        }
    else:
        grant_type = "client_credentials"
        payload = {
            "grant_type": grant_type,
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        }

    print(f"🔑 Requesting OAuth2 token ({grant_type}) from {base_url}…")
    r = requests.post(token_url, data=payload)
    if not r.ok:
        print(f"❌ OAuth request failed ({r.status_code}) → {r.text}")
        # fallback to manual or personal token
        fallback = (
            os.getenv("ZENODO_SANDBOX_TOKEN") if sandbox else os.getenv("ZENODO_TOKEN")
        )
        if fallback:
            print("⚠️  Falling back to personal API token from .env")
            return fallback
        r.raise_for_status()

    data = r.json()
    token = data.get("access_token")
    new_refresh = data.get("refresh_token")

    if not token:
        raise RuntimeError(f"⚠️ No access_token returned → {data}")

    print("✅ OAuth2 access token obtained successfully.")

    # --- Persist refresh token ---
    if new_refresh:
        key_name = "ZENODO_SANDBOX_REFRESH_TOKEN" if sandbox else "ZENODO_REFRESH_TOKEN"
        set_key(env_path, key_name, new_refresh)
        print(f"🔁 Stored new refresh token in .env → {key_name}")

    # --- Remove one-time auth code if used ---
    if grant_type == "authorization_code":
        set_key(env_path, "ZENODO_AUTH_CODE", "")

    return token



def update_zenodo_metadata():
    """Update zenodo.json with version + date."""
    meta_path = "zenodo.json"
    if not os.path.exists(meta_path):
        print("⚠️ zenodo.json not found — skipping metadata update.")
        return {}

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    version = metadata.get("version", "0.0.0")
    if version[-1].isalpha():
        base, suffix = version[:-1], version[-1]
        next_version = base + chr(ord(suffix) + 1)
    else:
        next_version = version + "a"

    metadata["version"] = next_version
    metadata["publication_date"] = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"🧩 Updated zenodo.json → version={metadata['version']}")
    return metadata


def find_reproducibility_files():
    """
    Automatically collect all files under /data, /figures, and /results.
    Returns a list of paths to upload.
    """
    include_dirs = ["data", "figures", "results"]
    extensions = [".csv", ".png", ".json", ".ipynb", ".svg"]

    found_files = []
    for folder in include_dirs:
        path = Path(folder)
        if not path.exists():
            continue
        for ext in extensions:
            found_files.extend(path.rglob(f"*{ext}"))

    if not found_files:
        print("⚠️ No data or figure files found for upload.")
    else:
        print(f"📦 Found {len(found_files)} reproducibility files:")
        for f in found_files:
            print(f"   └── {f}")
    return found_files


def upload_to_zenodo(sandbox=False):
    """Create deposition and upload all reproducibility assets."""
    token = get_access_token(sandbox)
    api = ZENODO_SANDBOX_API if sandbox else ZENODO_API
    headers = {"Authorization": f"Bearer {token}"}

    deposition_id = None
    # 1. Create deposition
    print("🪣 Creating new Zenodo deposition…")
    r = requests.post(f"{api}/deposit/depositions", headers=headers, json={})
    r.raise_for_status()
    deposition = r.json()
    dep_id = deposition["id"]
    print(f"✅ Deposition created (id={dep_id})")

    # Ensure deposition exists
    if not deposition_id:
        print("🆕 Creating new deposition…")
        dep_resp = requests.post(f"{api}/deposit/depositions",
                                 params={'access_token': token},
                                 json={}, headers={"Content-Type": "application/json"})
        dep_resp.raise_for_status()
        deposition_id = dep_resp.json()["id"]
        print(f"✅ Created deposition ID: {deposition_id}")

    # 2. Upload files
    for path in find_reproducibility_files():
        print(f"⬆️ Uploading {path.name}")
        with open(path, "rb") as fp:
            r = requests.post(
                f"{api}/deposit/depositions/{dep_id}/files",
                headers=headers,
                files={"file": (path.name, fp)},
            )
            r.raise_for_status()

    # 3. Update metadata
    metadata = update_zenodo_metadata()
    if metadata:
        r = requests.put(
            f"{api}/deposit/depositions/{dep_id}",
            headers=headers,
            json={"metadata": metadata},
        )
        r.raise_for_status()
        doi = r.json()["metadata"]["prereserve_doi"]["doi"]
    else:
        doi = f"TEMP-{datetime.datetime.utcnow().strftime('%Y-%m-%d')}"
    print(f"🧾 Metadata updated. DOI = {doi}")

    # 4. Generate release badge
    badge = f"[![DOI](https://zenodo.org/badge/DOI/{doi}.svg)](https://doi.org/{doi})"
    with open("release_badge.svg", "w", encoding="utf-8") as f:
        f.write(badge)
    print("🏷️  Created release_badge.svg for README embedding.")

    # 5. Print manifest
    print("\n📜 Reproducibility manifest summary:")
    for fpath in find_reproducibility_files():
        print(f"   • {fpath}")

    print("\n✅ Upload complete.")
    return doi

import subprocess, datetime, json

def add_release_footer(doi, arxiv_link="arXiv:2501.12345"):
    commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    date = datetime.date.today().isoformat()
    block = f"\n---\n📢 **UTF-2.0 Release {date}**\n\n" \
            f"- DOI: [https://doi.org/{doi}](https://doi.org/{doi})  \n" \
            f"- arXiv: {arxiv_link}  \n" \
            f"- Git commit: `{commit}`\n"
    open("README.md", "a", encoding="utf-8").write(block)
    print("✅ Announcement footer appended to README.md")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upload UTFv2 reproducibility artifacts to Zenodo.")
    parser.add_argument("--sandbox", action="store_true", help="Use sandbox.zenodo.org API.")
    parser.add_argument("--production", action="store_true", help="Use production zenodo.org API.")
    parser.add_argument("--reauthorize", action="store_true", help="Force OAuth reauthorization.")
    parser.add_argument("--include", nargs="+", help="List of files to include in the upload.")
    args = parser.parse_args()


    # Early in main:
    if args.reauthorize:
        env_file = Path(".env")
        os.environ["ZENODO_REFRESH_TOKEN"] = ""
        os.environ["ZENODO_SANDBOX_REFRESH_TOKEN"] = ""
        if env_file.exists():
            lines = [l for l in env_file.read_text().splitlines() if "REFRESH_TOKEN" not in l]
            env_file.write_text("\n".join(lines))
        print("🔁 Reauthorization requested — refresh tokens cleared.")


    upload_to_zenodo(sandbox=args.sandbox)
