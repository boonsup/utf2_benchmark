#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utf.models.coupled_superop import UTFParams, CoupledUTFSimulator

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eta", type=float, default=0.1)
    ap.add_argument("--lam", type=float, default=0.1)
    ap.add_argument("--sigma", type=float, default=1e-3)
    ap.add_argument("--steps", type=int, default=4000)
    ap.add_argument("--dt", type=float, default=0.01)
    ap.add_argument("--r", type=float, default=3.80)
    args = ap.parse_args()

    p = UTFParams(lam=args.lam, eta=args.eta, noise_sigma=args.sigma, steps=args.steps, dt=args.dt)
    sim = CoupledUTFSimulator(p)
    E, stats = sim.run(r=args.r)

    plt.figure(figsize=(8,3))
    plt.plot(E, lw=1)
    plt.title(f"E(t) | η={args.eta}, λ={args.lam}, σ={args.sigma} | drift_mean={stats['drift_mean']:.3g}")
    plt.xlabel("step"); plt.ylabel("E")
    plt.tight_layout(); plt.show()

if __name__ == "__main__":
    main()
