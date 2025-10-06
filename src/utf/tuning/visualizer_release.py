"""
UTF-2.0 Chaos Kernel — Release-Annotated Visualizer

Visualizes the evolution of F̂ chaos kernel parameters (r, tolerance, adapt)
across experiments, color-coded by Zenodo DOI and arXiv version.

Usage:
    python -m src.utf.tuning.visualizer_release
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import os

def _unique_labels(df):
    """Return unique combinations of DOI + arXiv version as categorical labels."""
    return [f"{doi}\n({ver})" for doi, ver in zip(df["zenodo_doi"], df["arxiv_version"])]

def plot_release_annotated(csv_path="data/f_tuning_history.csv", save=False):
    """Plot hyperparameter drift with color-coded release annotations."""
    if not os.path.exists(csv_path):
        print(f"⚠️ No tuning history found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    if df.empty:
        print("⚠️ Empty tuning history file.")
        return

    # --- Generate categorical color map for releases ---
    releases = df[["zenodo_doi", "arxiv_version"]].fillna("unreleased")
    release_labels = _unique_labels(releases)
    unique_releases = sorted(set(release_labels))
    cmap = cm.get_cmap("viridis", len(unique_releases))
    colors = {r: cmap(i) for i, r in enumerate(unique_releases)}

    # --- Plot evolution for r, tolerance, adapt ---
    fig, axes = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    params = ["r_best", "tolerance_best", "adapt_best"]
    titles = ["r (chaos gain)", "tolerance (energy bound)", "adapt (feedback rate)"]

    for idx, ax in enumerate(axes):
        for i, (label, color) in enumerate(colors.items()):
            mask = np.array(release_labels) == label
            ax.plot(
                df.index[mask],
                df[params[idx]][mask],
                "o-",
                color=color,
                label=label if idx == 0 else None,
                alpha=0.8,
            )
        ax.set_ylabel(titles[idx])
        ax.grid(alpha=0.3)

    axes[-1].set_xlabel("Tuning Iteration")
    fig.suptitle("F̂ Chaos Kernel — Release-Annotated Hyperparameter Evolution", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    # Add legend only once
    axes[0].legend(
        bbox_to_anchor=(1.02, 1.0),
        loc="upper left",
        title="Zenodo DOI (arXiv ver)",
        fontsize=8,
    )

    if save:
        out_path = "data/f_tuning_history_annotated.png"
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        print(f"✅ Saved annotated evolution plot → {out_path}")
    else:
        plt.show()
