#!/usr/bin/env python3
"""
UTFv2 Repository Cleanup, Packaging & Provenance Auditor
--------------------------------------------------------
Performs cleanup, packaging, SHA256 manifest updates, Zenodo uploads,
and deep ZIP+per-file verification.  Outputs full YAML audit report
with system provenance metadata (Python version, OS, git commit, etc.).
"""

import os, re, zipfile, hashlib, subprocess, requests, yaml, shutil, argparse, platform, sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# === CLI ===
parser = argparse.ArgumentParser(description="UTFv2 reproducibility packager / provenance auditor")
parser.add_argument("--ci", action="store_true", help="Quiet CI mode")
parser.add_argument("--dry-run", action="store_true", help="Simulate packaging only")
parser.add_argument("--verify", action="store_true", help="Verify all SHA256 hashes (ZIP + internal files)")
parser.add_argument("--report", type=str, help="Save structured audit YAML report")
args = parser.parse_args()

# === Globals ===
ROOT = Path(__file__).resolve().parents[1]
TIMESTAMP_ISO = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
TIMESTAMP_SAFE = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
PEER_REVIEW_ZIP = ROOT / f"utfv2_peer_review_{TIMESTAMP_SAFE}.zip"
PLACEHOLDER_ZIP = ROOT / f"utfv2_placeholder_{TIMESTAMP_SAFE}.zip"
MANIFEST = ROOT / "release_manifest.yaml"

ZENODO_JSON = ROOT / "zenodo.json"

load_dotenv(ROOT / ".env")
ZENODO_TOKEN = os.getenv("ZENODO_TOKEN") or os.getenv("ZENODO_SANDBOX_TOKEN")

# === Helpers ===
def log(msg):
    if not args.ci:
        print(msg)

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=False).stdout.strip()

import subprocess

# === Git Metadata Helpers ===
def get_git_commit() -> str:
    """Return current short Git commit hash."""
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"

def get_git_branch() -> str:
    """Return current Git branch name."""
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"

def get_git_tag() -> str:
    """Return current Git tag if available."""
    try:
        return (
            subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except Exception:
        return "untagged"

def get_git_metadata():
    return {
        "commit": run(["git", "rev-parse", "HEAD"]),
        "tag": run(["git", "describe", "--tags", "--always"]),
        "branch": run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    }

def get_env_metadata():
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "arch": platform.machine(),
        "git_branch": get_git_branch(),
        "git_commit": get_git_commit(),
        "git_tag": get_git_tag(),
        "timestamp_utc": TIMESTAMP_ISO,
    }


def get_doi():
    if not ZENODO_JSON.exists():
        return None
    match = re.search(r'"doi"\s*:\s*"([^"]+)"', ZENODO_JSON.read_text(encoding="utf-8"))
    return match.group(1) if match else None

def detect_env(doi):
    if not doi:
        return "unknown", "https://zenodo.org/api/deposit/depositions"
    if "5072" in doi or "sandbox" in doi:
        return "sandbox", "https://sandbox.zenodo.org/api/deposit/depositions"
    return "production", "https://zenodo.org/api/deposit/depositions"

def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def summarize_zip_hashes(zip_path):
    file_hashes = {}
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            file_hashes[name] = hashlib.sha256(zf.read(name)).hexdigest()
    return file_hashes

# === Core Ops ===
def clean_repo():
    log("🧹 Cleaning temporary files…")
    patterns = ["*.aux","*.log","*.out","*.bbl","*.blg","*.toc",
                "__pycache__",".ipynb_checkpoints","*.DS_Store"]
    for pattern in patterns:
        for p in ROOT.rglob(pattern):
            try:
                if p.is_file(): p.unlink()
                elif p.is_dir(): shutil.rmtree(p)
            except Exception: pass
    log("✅ Cleanup complete.")

def zip_dir(zip_path, patterns):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for pattern in patterns:
            for f in ROOT.rglob(pattern):
                if f.is_file():
                    zf.write(f, f.relative_to(ROOT))
    log(f"📦 Created {zip_path.name}")
    return zip_path

def build_peer_review_zip():
    includes = [
        "src/**/*","notebooks/**/*","scripts/**/*","tex/**/*",
        "figures/**/*","data/**/*",
        "environment.yml","README.md","CITATION.cff","zenodo.json","PROJECT_PLAN.md"
    ]
    return zip_dir(PEER_REVIEW_ZIP, includes)

def build_placeholder_zip():
    tmp = ROOT / "_placeholder_temp"; tmp.mkdir(exist_ok=True)
    placeholders = {
        "src/__init__.py": "# placeholder",
        "notebooks/template.ipynb": "{}",
        "tex/template.tex": "% placeholder",
        "data/.keep": "",
        "figures/.keep": ""
    }
    for rel, content in placeholders.items():
        path = tmp / rel; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    with zipfile.ZipFile(PLACEHOLDER_ZIP,"w",zipfile.ZIP_DEFLATED) as zf:
        for f in tmp.rglob("*"): zf.write(f, f.relative_to(tmp))
    shutil.rmtree(tmp)
    log(f"🧬 Created {PLACEHOLDER_ZIP.name}")
    return PLACEHOLDER_ZIP

def update_manifest(doi, env, git_meta, zip_path):
    manifest = {}
    if MANIFEST.exists():
        manifest = yaml.safe_load(MANIFEST.read_text()) or {}
    if "releases" not in manifest:
        manifest["releases"] = []

    entry = {
        "artifact": str(zip_path.name),
        "sha256": compute_sha256(zip_path),
        "doi": doi,
        "environment": env,
        "git_commit": git_meta["commit"],
        "git_branch": git_meta["branch"],
        "git_tag": git_meta["tag"],
        "timestamp": TIMESTAMP_ISO,     # ✅ fixed
    }

    # optional per-file hashes
    entry["contents_hashes"] = summarize_zip_hashes(zip_path)
    manifest["releases"].append(entry)
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False))
    return entry

def upload_to_zenodo(env, zip_path):
    env_name, base_url = detect_env(env)
    headers = {"Authorization": f"Bearer {ZENODO_TOKEN}"}
    log(f"🚀 Uploading {zip_path.name} → {env_name} Zenodo…")
    dep = requests.post(base_url, headers=headers, json={}); dep.raise_for_status()
    dep_id = dep.json()["id"]
    with open(zip_path,"rb") as f:
        r = requests.post(f"{base_url}/{dep_id}/files", headers=headers, files={"file":(zip_path.name,f)})
        r.raise_for_status()
    publish = requests.post(f"{base_url}/{dep_id}/actions/publish", headers=headers)
    publish.raise_for_status()
    return publish.json().get("doi","unknown")

def git_commit_final(msg):
    subprocess.run(["git","add","."],check=False)
    subprocess.run(["git","commit","-m",msg],check=False)
    subprocess.run(["git","push"],check=False)

# === Deep Verify with Provenance Report ===
def verify_manifest(deep=True, report_path=None):
    if not MANIFEST.exists():
        print("⚠️ No manifest found."); return False
    manifest = yaml.safe_load(MANIFEST.read_text()) or {}
    if "releases" not in manifest:
        print("⚠️ Empty manifest."); return False

    git_meta = get_git_metadata()
    env_meta = get_env_metadata()
    audit = {
        "timestamp": TIMESTAMP_ISO,
        "summary": None,
        "provenance": {
            "git": git_meta,
            "environment": env_meta,
        },
        "results": []
    }

    all_ok = True
    for rel in manifest["releases"]:
        art = ROOT / rel.get("artifact","")
        expected = rel.get("sha256")
        per_file = rel.get("contents_hashes",{})
        entry_result = {"artifact": art.name, "zip_ok": None, "files": {}, "status": "OK"}

        print(f"\n🔎 Verifying {art.name} …")
        if not art.exists():
            print(f"❌ Missing file: {art}")
            entry_result["status"] = "MISSING"
            all_ok = False; audit["results"].append(entry_result); continue

        actual = compute_sha256(art)
        if actual != expected:
            print(f"❌ ZIP hash mismatch!\n   expected={expected}\n   actual  ={actual}")
            entry_result["zip_ok"] = False; entry_result["status"] = "ZIP_MISMATCH"; all_ok = False
        else:
            print("✅ ZIP-level checksum OK")
            entry_result["zip_ok"] = True

        if deep and per_file:
            with zipfile.ZipFile(art,"r") as zf:
                for name, exp in per_file.items():
                    if name not in zf.namelist():
                        print(f"⚠️ Missing internal file: {name}")
                        entry_result["files"][name] = "MISSING"
                        all_ok = False; continue
                    act = hashlib.sha256(zf.read(name)).hexdigest()
                    if act != exp:
                        print(f"❌ Modified: {name}")
                        entry_result["files"][name] = "MISMATCH"; all_ok = False
                    else:
                        entry_result["files"][name] = "OK"
            print("🧩 Deep verification done.")

        audit["results"].append(entry_result)

    audit["summary"] = "ALL OK ✅" if all_ok else "INCONSISTENCIES FOUND ❌"
    print(f"\n🎯 Verification summary: {audit['summary']}")

    if report_path:
        rp = Path(report_path)
        rp.write_text(yaml.safe_dump(audit, sort_keys=False))
        print(f"🧾 Audit report saved → {rp}")
    return all_ok

# === MAIN ===
if __name__ == "__main__":
    if args.verify:
        verify_manifest(deep=True, report_path=args.report)
        exit(0)

    clean_repo()
    git_meta = get_git_metadata(); doi = get_doi(); env,_ = detect_env(doi)
    peer = build_peer_review_zip(); build_placeholder_zip()
    entry = update_manifest(doi, env, git_meta, peer)

    if args.dry_run:
        print("🧪 Dry run complete."); exit(0)

    try:
        new_doi = upload_to_zenodo(env, peer)
        entry["new_doi"] = new_doi
    except Exception as e:
        print(f"⚠️ Zenodo upload failed: {e}")

    git_commit_final(f"Auto cleanup + manifest update @ {TIMESTAMP_ISO}")
    if args.ci:
        print(f"OK: utfv2 release packaged @ {TIMESTAMP_ISO}")
    else:
        print("🎯 Packaging + audit-ready manifest complete.")
