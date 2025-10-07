#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UTFv2 Supplementary Export Generator
-----------------------------------
Generates CSVs and figures for Supplementary Sections S4–S6:

S4: Chaos–Decoherence Coupling Map (η–λ phase)
S5: Noise Robustness (σ vs τ_crit)
S6: Energy Drift Distribution

Outputs → data/supplementary_S4_S6_*.csv and figures/supplementary_S4_S6_*.png
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from src.utf.models.coupled_superop import UTFParams, CoupledUTFSimulator, tau_crit

DATA_DIR = Path("data")
FIG_DIR = Path("figures")
TEX_DIR = Path("tex")
DATA_DIR.mkdir(exist_ok=True, parents=True)
FIG_DIR.mkdir(exist_ok=True, parents=True)
TEX_DIR.mkdir(exist_ok=True, parents=True)

def generate_s4_eta_lambda_map():
    """S4: DF coupling stability phase map."""
    etas = np.linspace(0, 0.3, 6)
    lams = np.linspace(0, 0.14, 6)
    records = []
    for eta in etas:
        for lam in lams:
            p = UTFParams(lam=lam, eta=eta, steps=3000, dt=0.01)
            sim = CoupledUTFSimulator(p)
            _, stats = sim.run(r=3.8)
            bounded = stats["drift_mean"] < tau_crit(lam)
            records.append({
                "eta": eta,
                "lambda": lam,
                "bounded": 1 if bounded else 0,
                "drift_mean": stats["drift_mean"]
            })

    df = pd.DataFrame(records)
    df.to_csv(DATA_DIR / "supplementary_S4_eta_lambda.csv", index=False)

    # ✅ Corrected pivot usage (must specify keyword arguments)
    pivot = df.pivot(index="eta", columns="lambda", values="bounded")

    plt.figure(figsize=(6, 5))
    plt.imshow(pivot.values, origin="lower", cmap="viridis", aspect="auto",
               extent=[pivot.columns.min(), pivot.columns.max(),
                       pivot.index.min(), pivot.index.max()])
    plt.title("S4: Stability Phase Map (η–λ)")
    plt.xlabel("λ")
    plt.ylabel("η")
    cbar = plt.colorbar(label="Bounded Fraction (1=stable)")
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(["Unstable", "Stable"])
    plt.tight_layout()
    plt.savefig(FIG_DIR / "supplementary_S4_eta_lambda.png", dpi=200)
    plt.close()
    print("✅ Generated S4 phase map")


def generate_s5_noise_vs_tau():
    """S5: Noise robustness vs τ_crit."""
    sigmas = np.linspace(0, 5e-3, 10)
    lams = [0.08, 0.1, 0.12]
    rows = []
    for lam in lams:
        τcrit = tau_crit(lam)
        for sigma in sigmas:
            p = UTFParams(lam=lam, eta=0.1, noise_sigma=sigma, steps=3000)
            sim = CoupledUTFSimulator(p)
            _, stats = sim.run()
            rows.append({
                "lambda": lam, "sigma": sigma,
                "drift_mean": stats["drift_mean"],
                "tau_crit": τcrit,
                "ratio": stats["drift_mean"]/τcrit
            })
    df = pd.DataFrame(rows)
    df.to_csv(DATA_DIR / "supplementary_S5_noise_tau.csv", index=False)

    plt.figure(figsize=(7, 4))
    for lam in lams:
        subset = df[df["lambda"] == lam]
        plt.plot(subset["sigma"], subset["ratio"], label=f"λ={lam}")
    plt.axhline(1, color="red", linestyle="--", label="Critical Threshold")
    plt.xlabel("Noise σ"); plt.ylabel("⟨ΔE⟩ / τ_crit")
    plt.title("S5: Noise Robustness vs τ_crit")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "supplementary_S5_noise_tau.png", dpi=200)
    plt.close()
    print("✅ Generated S5 noise robustness")

def generate_s6_energy_distribution():
    """S6: Energy drift histogram across random seeds."""
    seeds = range(10)
    drifts = []
    for seed in seeds:
        p = UTFParams(lam=0.1, eta=0.1, seed=seed, steps=3000)
        sim = CoupledUTFSimulator(p)
        _, stats = sim.run()
        drifts.append(stats["drift_mean"])
    df = pd.DataFrame({"seed": list(seeds), "drift_mean": drifts})
    df.to_csv(DATA_DIR / "supplementary_S6_energy_distribution.csv", index=False)

    plt.figure(figsize=(6,4))
    plt.hist(df["drift_mean"], bins=8, color="deepskyblue", edgecolor="black")
    plt.xlabel("Drift Mean"); plt.ylabel("Count")
    plt.title("S6: Energy Drift Distribution Across Seeds")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "supplementary_S6_energy_distribution.png", dpi=200)
    plt.close()
    print("✅ Generated S6 energy distribution")

# === S4–S6 Aggregation and Summary ===
def aggregate_s4_s6_summary():
    """Aggregate S4–S6 data and generate combined summary grid."""
    import matplotlib.gridspec as gridspec

    paths = {
        "S4": DATA_DIR / "supplementary_S4_eta_lambda.csv",
        "S5": DATA_DIR / "supplementary_S5_noise_tau.csv",
        "S6": DATA_DIR / "supplementary_S6_energy_distribution.csv",
    }

    dfs = {}
    for key, path in paths.items():
        if not path.exists():
            print(f"⚠️ Missing {path}, skipping {key}.")
            continue
        dfs[key] = pd.read_csv(path)

    # --- Summary statistics ---
    summary = []
    if "S4" in dfs:
        bounded_ratio = dfs["S4"]["bounded"].mean()
        summary.append({"section": "S4", "metric": "bounded_ratio", "value": bounded_ratio})

    if "S5" in dfs:
        avg_taucrit = dfs["S5"]["tau_crit"].mean()
        avg_ratio = dfs["S5"]["ratio"].mean()
        summary.append({"section": "S5", "metric": "avg_tau_crit", "value": avg_taucrit})
        summary.append({"section": "S5", "metric": "avg_ratio", "value": avg_ratio})

    if "S6" in dfs:
        drift_mean = dfs["S6"]["drift_mean"].mean()
        drift_std = dfs["S6"]["drift_mean"].std()
        summary.append({"section": "S6", "metric": "drift_mean", "value": drift_mean})
        summary.append({"section": "S6", "metric": "drift_std", "value": drift_std})

    summary_df = pd.DataFrame(summary)
    summary_csv = DATA_DIR / "supplementary_summary.csv"
    summary_df.to_csv(summary_csv, index=False)
    print(f"✅ Saved aggregate metrics → {summary_csv}")

    # --- Combined figure grid ---
    fig = plt.figure(figsize=(12, 4))
    gs = gridspec.GridSpec(1, 3, wspace=0.3)

    if "S4" in dfs:
        ax = fig.add_subplot(gs[0, 0])
        pivot = dfs["S4"].pivot(index="eta", columns="lambda", values="bounded")
        im = ax.imshow(pivot.values, origin="lower", cmap="viridis", aspect="auto")
        ax.set_title("S4: Stability Map (η–λ)")
        ax.set_xlabel("λ")
        ax.set_ylabel("η")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    if "S5" in dfs:
        ax = fig.add_subplot(gs[0, 1])
        for lam, subset in dfs["S5"].groupby("lambda"):
            ax.plot(subset["sigma"], subset["ratio"], marker="o", label=f"λ={lam}")
        ax.set_title("S5: Noise–τ Ratio")
        ax.set_xlabel("Noise σ")
        ax.set_ylabel("⟨ΔE⟩ / τ_crit")
        ax.legend()

    if "S6" in dfs:
        ax = fig.add_subplot(gs[0, 2])
        ax.hist(dfs["S6"]["drift_mean"], bins=20, color="royalblue", alpha=0.7)
        ax.set_title("S6: Drift Distribution")
        ax.set_xlabel("Mean Drift")
        ax.set_ylabel("Count")

    plt.suptitle("Supplementary S4–S6 Summary Overview", fontsize=14, y=1.03)
    plt.tight_layout()
    out_path = FIG_DIR / "supplementary_S4_S6_summary.png"
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"📊 Combined summary figure saved → {out_path}")
def export_supplementary_tex_table():
    """Export LaTeX-ready table summarizing S4–S6 metrics."""
    summary_csv = DATA_DIR / "supplementary_summary.csv"
    if not summary_csv.exists():
        print("⚠️ No summary CSV found. Run aggregate_s4_s6_summary() first.")
        return

    df = pd.read_csv(summary_csv)
    table_tex = TEX_DIR / "supplementary_summary.tex"
    table_tex.parent.mkdir(parents=True, exist_ok=True)

    tex = "\\begin{table}[h!]\n\\centering\n"
    tex += "\\caption{Summary of Supplementary Analyses (S4–S6).}\n"
    tex += "\\label{tab:supplementary_summary}\n"
    tex += "\\begin{tabular}{lll}\n\\hline\n"
    tex += "Section & Metric & Value \\\\\n\\hline\n"
    for _, row in df.iterrows():
        tex += f"{row['section']} & {row['metric']} & {row['value']:.4f} \\\\\n"
    tex += "\\hline\n\\end{tabular}\n\\end{table}\n"

    table_tex.write_text(tex, encoding="utf-8")
    print(f"📄 Generated LaTeX summary → {table_tex}")


def label_combined_figure_panels():
    """Annotate combined summary figure with (A), (B), (C) panel labels."""
    import matplotlib.image as mpimg

    path = FIG_DIR / "supplementary_S4_S6_summary.png"
    if not path.exists():
        print("⚠️ Cannot label panels — figure missing.")
        return

    img = mpimg.imread(path)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.imshow(img)
    ax.axis("off")

    labels = ["(A)", "(B)", "(C)"]
    x_positions = [0.07, 0.4, 0.73]
    for x, label in zip(x_positions, labels):
        ax.text(x, 0.08, label, transform=ax.transAxes, fontsize=14, fontweight="bold", color="white")

    out_path = FIG_DIR / "supplementary_S4_S6_summary_labeled.png"
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"🅰️🅱️🅲️ Labeled version saved → {out_path}")

# if __name__ == "__main__":
#     generate_s4_eta_lambda_map()
#     generate_s5_noise_vs_tau()
#     generate_s6_energy_distribution()
#     print("🎯 All supplementary data + figures generated.")
if __name__ == "__main__":
    generate_s4_eta_lambda_map()
    generate_s5_noise_vs_tau()
    generate_s6_energy_distribution()
    aggregate_s4_s6_summary()
    export_supplementary_tex_table()
    label_combined_figure_panels()
    print("🎯 All supplementary data + LaTeX + labeled figures exported successfully.")