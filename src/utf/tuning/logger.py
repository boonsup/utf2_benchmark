"""
UTF-2.0 Chaos Kernel Logger
Logs Monte-Carlo tuning sessions with version and metadata consistency.
"""

import os, json, datetime, subprocess, pandas as pd

def get_git_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "no-git"

def get_zenodo_doi(path="zenodo.json"):
    if os.path.exists(path):
        try:
            return json.load(open(path)).get("doi", "pending-doi")
        except Exception:
            return "invalid-json"
    return "no-zenodo-file"

def get_arxiv_version(path="arxiv_metadata.json"):
    if os.path.exists(path):
        try:
            return json.load(open(path)).get("version", "v0")
        except Exception:
            return "invalid-arxiv-meta"
    return "v0"

def log_tuning_result(best_fit, num_samples, log_path="data/f_tuning_history.csv"):
    """Append a tuning result entry with all reproducibility metadata."""
    entry = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "git_commit": get_git_hash(),
        "zenodo_doi": get_zenodo_doi(),
        "arxiv_version": get_arxiv_version(),
        "r_best": best_fit["r"],
        "tolerance_best": best_fit["tolerance"],
        "adapt_best": best_fit["adapt"],
        "num_samples": num_samples,
    }

    dir_ = os.path.dirname(log_path)
    if dir_:
        os.makedirs(dir_, exist_ok=True)

    df = pd.DataFrame([entry])
    header = not os.path.exists(log_path)
    df.to_csv(log_path, mode="a", index=False, header=header)
    print(f"✅ Logged tuning iteration → {log_path}")
    return entry
