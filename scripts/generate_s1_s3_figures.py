#!/usr/bin/env python3
"""
UTFv2 Supplementary Figure Generator (S1–S3)
--------------------------------------------
Generates reproducible toy data and figures for:
    S1: Kernel Simulation Architecture
    S2: Latency Scaling Benchmark
    S3: Quantum–Classical Coupling Test
Output: CSV files and publication-ready figures.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Directory setup --------------------------------------------------
os.makedirs("data", exist_ok=True)
os.makedirs("figures", exist_ok=True)

# ----------------------------------------------------------------------
# S1: Kernel Simulation Architecture (α, β, λ evolution)
# ----------------------------------------------------------------------
np.random.seed(42)
steps = np.arange(0, 100)
alpha = 0.001 + 0.0001 * np.sin(0.1 * steps)
beta = 0.6 + 0.05 * np.cos(0.05 * steps)
lam = 0.1 * (1 + 0.1 * np.sin(0.2 * steps))

s1_df = pd.DataFrame({"step": steps, "alpha": alpha, "beta": beta, "lambda": lam})
s1_df.to_csv("data/supplementary_S1_kernel.csv", index=False)

plt.figure(figsize=(8, 4))
plt.plot(steps, alpha, label=r"$\alpha(t)$", color="teal")
plt.plot(steps, beta, label=r"$\beta(t)$", color="orange")
plt.plot(steps, lam, label=r"$\lambda(t)$", color="crimson")
plt.xlabel("Simulation Step")
plt.ylabel("Parameter Value")
plt.title("S1: UTFv2 Kernel Parameter Evolution")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("figures/supplementary_S1_kernel_architecture.png", dpi=200)
plt.close()

print("✅ Generated S1 kernel architecture figure and CSV")

# ----------------------------------------------------------------------
# S2: Latency Scaling Benchmark
# ----------------------------------------------------------------------
N = np.logspace(8, 16, 9, base=2)
tau_gpu = 0.1 + 0.00002 * N ** 0.45
tau_cpu = 0.5 + 0.00008 * N ** 0.6

s2_df = pd.DataFrame({
    "parallelism_N": N.astype(int),
    "latency_gpu_ms": tau_gpu,
    "latency_cpu_ms": tau_cpu
})
s2_df.to_csv("data/supplementary_S2_latency.csv", index=False)

plt.figure(figsize=(8, 4))
plt.loglog(N, tau_gpu, "o-", label="GPU", color="royalblue")
plt.loglog(N, tau_cpu, "s-", label="CPU", color="darkorange")
plt.xlabel("Parallelism (N)")
plt.ylabel("Latency (ms)")
plt.title("S2: Latency Scaling Benchmark")
plt.legend()
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("figures/supplementary_S2_latency_scaling.png", dpi=200)
plt.close()

print("✅ Generated S2 latency scaling figure and CSV")

# ----------------------------------------------------------------------
# S3: Quantum–Classical Coupling Variation
# ----------------------------------------------------------------------
eta_vals = np.linspace(0.05, 1.0, 25)
lambda_vals = [0.08, 0.10, 0.12]

records = []
for lam in lambda_vals:
    drift = np.tanh(5 * (eta_vals - 0.5)) * (0.1 * lam)
    for e, d in zip(eta_vals, drift):
        records.append({"eta": e, "lambda": lam, "drift": d})

s3_df = pd.DataFrame(records)
s3_df.to_csv("data/supplementary_S3_coupling.csv", index=False)

plt.figure(figsize=(8, 4))
for lam in lambda_vals:
    subset = s3_df[s3_df["lambda"] == lam]
    plt.plot(subset["eta"], subset["drift"], label=f"$\\lambda$={lam:.2f}")
plt.axhline(0, color="black", linestyle="--", linewidth=1)
plt.xlabel(r"Coupling Strength $\eta$")
plt.ylabel("Energy Drift (a.u.)")
plt.title("S3: Quantum–Classical Coupling Variation")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("figures/supplementary_S3_coupling_variation.png", dpi=200)
plt.close()

print("✅ Generated S3 coupling variation figure and CSV")

# ----------------------------------------------------------------------
# Summary manifest
# ----------------------------------------------------------------------
summary = pd.DataFrame([
    {"Section": "S1", "File": "data/supplementary_S1_kernel.csv", "Figure": "figures/supplementary_S1_kernel_architecture.png"},
    {"Section": "S2", "File": "data/supplementary_S2_latency.csv", "Figure": "figures/supplementary_S2_latency_scaling.png"},
    {"Section": "S3", "File": "data/supplementary_S3_coupling.csv", "Figure": "figures/supplementary_S3_coupling_variation.png"},
])
summary.to_csv("data/supplementary_manifest_S1_S3.csv", index=False)
print("📦 Exported manifest → data/supplementary_manifest_S1_S3.csv")
