#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Monte Carlo over (η, λ, σ) to test bounded chaos under DF coupling and commutator term.
Saves CSV to data/noise_robustness.csv and figures/noise_robustness_map.png
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from src.utf.models.coupled_superop import UTFParams, CoupledUTFSimulator, tau_crit

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--etas", type=str, default="0.0,0.05,0.1,0.2")
    ap.add_argument("--lams", type=str, default="0.08,0.10,0.12")
    ap.add_argument("--sigmas", type=str, default="0.0,1e-3,2e-3,5e-3")
    ap.add_argument("--steps", type=int, default=4000)
    ap.add_argument("--dt", type=float, default=0.01)
    ap.add_argument("--omega", type=float, default=1.0)
    ap.add_argument("--gamma", type=float, default=0.6)
    ap.add_argument("--r", type=float, default=3.80)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--outcsv", type=str, default="data/noise_robustness.csv")
    ap.add_argument("--fig", type=str, default="figures/noise_robustness_map.png")
    args = ap.parse_args()

    etas = [float(x) for x in args.etas.split(",")]
    lams = [float(x) for x in args.lams.split(",")]
    sigs = [float(x) for x in args.sigmas.split(",")]

    Path("data").mkdir(exist_ok=True, parents=True)
    Path("figures").mkdir(exist_ok=True, parents=True)

    rows = []
    for eta in etas:
        for lam in lams:
            for sigma in sigs:
                p = UTFParams(
                    omega=args.omega, gamma=args.gamma,
                    lam=lam, eta=eta, dt=args.dt, steps=args.steps,
                    seed=args.seed, noise_sigma=sigma
                )
                sim = CoupledUTFSimulator(p)
                E, stats = sim.run(r=args.r)

                τcrit = tau_crit(lam)
                # bounded if drift_mean < τcrit (toy criterion)
                bounded = stats["drift_mean"] < τcrit

                rows.append({
                    "eta": eta, "lam": lam, "sigma": sigma,
                    "E_mean": stats["E_mean"], "E_std": stats["E_std"],
                    "drift_mean": stats["drift_mean"], "drift_max": stats["drift_max"],
                    "tau_crit": τcrit, "bounded": bool(bounded)
                })

    df = pd.DataFrame(rows)
    df.to_csv(args.outcsv, index=False)
    print(f"✅ wrote {args.outcsv} with {len(df)} rows")

    # Simple heatmap: proportion bounded across eta × lam, aggregated over sigma
    pivot = df.groupby(["eta","lam"])["bounded"].mean().reset_index()
    pivot_tbl = pivot.pivot(index="eta", columns="lam", values="bounded")

    plt.figure(figsize=(6,4))
    plt.imshow(pivot_tbl.values, aspect="auto", origin="lower", vmin=0, vmax=1)
    plt.yticks(range(len(pivot_tbl.index)), [f"η={v:g}" for v in pivot_tbl.index])
    plt.xticks(range(len(pivot_tbl.columns)), [f"λ={v:g}" for v in pivot_tbl.columns], rotation=45)
    plt.colorbar(label="Fraction bounded over σ")
    plt.title("Noise Robustness Map (bounded fraction)")
    plt.tight_layout()
    plt.savefig(args.fig, dpi=200)
    print(f"🖼  saved {args.fig}")

if __name__ == "__main__":
    main()
