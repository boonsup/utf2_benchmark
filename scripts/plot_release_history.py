#!/usr/bin/env python3
"""
UTFv2 Release Provenance Visualizer + Auto-Committer
----------------------------------------------------
Plots DOI and environment trends, embeds analytics in README.md,
and (optionally) commits results in CI environments.
"""

import os
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import subprocess
import sys

# === CLI ===
parser = argparse.ArgumentParser(
    description="Plot release provenance, embed analytics, and auto-commit if --ci flag used."
)
parser.add_argument("--csv", default="data/release_history.csv", help="Path to release history CSV.")
parser.add_argument("--figdir", default="figures", help="Directory to save generated plots.")
parser.add_argument("--readme", default="README.md", help="README path to update.")
parser.add_argument("--show", action="store_true", help="Show plots interactively.")
parser.add_argument("--ci", action="store_true", help="Auto-commit README updates in CI.")
args = parser.parse_args()

# === Setup ===
csv_path = Path(args.csv)
fig_dir = Path(args.figdir)
fig_dir.mkdir(parents=True, exist_ok=True)

if not csv_path.exists():
    sys.exit(f"❌ Cannot find {csv_path}. Run build_release_dashboard.py first.")

df = pd.read_csv(csv_path)
if df.empty:
    sys.exit("⚠️ release_history.csv is empty — nothing to visualize.")

df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce")
df = df.dropna(subset=["publication_date"]).sort_values("publication_date").reset_index(drop=True)

env_colors = {"test": "gray", "sandbox": "orange", "production": "royalblue", "unknown": "lightgray"}


def save_plot(name, title):
    """Save a figure and return its relative path for Markdown embedding."""
    path = fig_dir / f"{name}.png"
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    print(f"💾 Saved → {path}")
    if args.show:
        plt.show()
    plt.close("all")
    return str(path).replace("\\", "/")


# === Plotting ===
plt.figure(figsize=(10, 4))
plt.plot(df["publication_date"], range(1, len(df) + 1), marker="o", color="mediumseagreen")
plt.xlabel("Publication Date")
plt.ylabel("Cumulative Releases")
plt.grid(True, linestyle="--", alpha=0.5)
p1 = save_plot("release_doi_growth", "Cumulative DOI Count Over Time")

plt.figure(figsize=(10, 5))
for env, color in env_colors.items():
    subset = df[df["environment"] == env]
    if not subset.empty:
        plt.scatter(
            subset["publication_date"],
            [env] * len(subset),
            color=color,
            s=100,
            edgecolor="black",
            label=env.capitalize(),
        )
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
plt.xlabel("Publication Date")
plt.ylabel("Environment")
plt.legend(title="Deployment Stage")
plt.grid(True, linestyle=":", alpha=0.4)
p2 = save_plot("release_environment_timeline", "Environment Transitions Across Releases")

env_counts = df["environment"].value_counts()
plt.figure(figsize=(6, 4))
env_counts.plot(kind="bar", color=[env_colors.get(e, "gray") for e in env_counts.index])
plt.xlabel("Environment")
plt.ylabel("Number of Releases")
plt.grid(axis="y", linestyle="--", alpha=0.5)
p3 = save_plot("release_environment_density", "Releases Per Environment")

# === Metadata + README update ===
latest = df.iloc[-1]
zenodo_label = latest.get("doi", "unknown")
env = latest.get("environment", "unknown")
ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

readme_path = Path(args.readme)
readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

analytics_md = f"""
## 📈 Release Analytics  
*(Auto-generated on {ts})*  

![DOI Growth]({p1})  
![Environment Timeline]({p2})  
![Environment Density]({p3})  

**Latest DOI:** `{zenodo_label}`  
**Environment:** `{env}`  
**Total Releases:** `{len(df)}`  

---
"""

# Replace or append analytics section
if "## 📈 Release Analytics" in readme:
    before = readme.split("## 📈 Release Analytics")[0]
    # Cut everything after analytics section to avoid duplication
    after = ""
    if "---" in readme.split("## 📈 Release Analytics")[1]:
        after = readme.split("## 📈 Release Analytics")[1].split("---", 1)[-1]
    readme = f"{before}{analytics_md}{after}"
else:
    readme += f"\n\n{analytics_md}"

readme_path.write_text(readme, encoding="utf-8")
print(f"✅ README.md updated with latest analytics → {readme_path}")

# === Optional Auto-Commit (CI mode) ===
if args.ci:
    print("🧩 CI mode enabled — committing analytics update...")
    try:
        subprocess.run(["git", "config", "user.name", "utf-bot"], check=True)
        subprocess.run(["git", "config", "user.email", "utf-bot@users.noreply.github.com"], check=True)
        subprocess.run(["git", "add", str(readme_path), str(fig_dir)], check=True)
        diff_check = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if diff_check.returncode != 0:
            msg = f"📊 Auto-update release analytics ({zenodo_label}, env={env})"
            subprocess.run(["git", "commit", "-m", msg], check=True)
            subprocess.run(["git", "push"], check=True)
            print(f"✅ Auto-commit pushed → {msg}")
        else:
            print("ℹ️ No changes detected — skipping commit.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git commit/push failed: {e}")
    except Exception as ex:
        print(f"⚠️ Unexpected error: {ex}")

print("🎯 Done — reproducibility visual analytics updated successfully.")
