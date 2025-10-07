[![DOI](https://zenodo.org/badge/DOI/10.5072/zenodo.344960.svg)](https://doi.org/10.5072/zenodo.344960)
[![Zenodo DOI Sync](https://github.com/YOURUSER/utfv2/actions/workflows/zenodo_sync.yaml/badge.svg)](https://github.com/YOURUSER/utfv2/actions/workflows/zenodo_sync.yaml)



# Unified Transmutation Framework (UTF-2.0)
### A Reproducible Benchmark for Cross-Scale Energy and Information Flow

**Author:** Boonsup Waikham  
**Version:** UTF-2.0 / Benchmark Release 1.0  
**License:** MIT  
**DOI (pending):** [Zenodo DOI here]  
**arXiv link:** [arXiv preprint link here]

---

## 🧩 Overview

UTF-2.0 formalizes three operators describing the full spectrum of energy/information transformation:

| Operator | Domain | Description |
|-----------|---------|-------------|
| `T̂` | Quantum (QFT/Dirac) | Transmutation — mass–energy conversion |
| `D̂` | Thermodynamic / Statistical | Transduction — energy down-conversion & decoherence |
| `F̂` | Classical / Chaotic | Transfusion — macroscopic diffusion & cascade |

The framework bridges **quantum decoherence, thermodynamic dissipation, and classical chaos**, offering a reproducible simulation to benchmark multi-scale energy transport.

---

## ⚙️ Reproducible Simulation

### 1. Dependencies
```bash
pip install numpy scipy matplotlib pandas

---

### 🚀 Getting Started

```bash
git clone https://github.com/<youruser>/utf2_benchmark.git
cd utf2_benchmark
conda env create -f environment.yml
conda activate utf2
pre-commit install
pytest


### 🔒 Developer Setup (Pre-Commit Hooks)

To ensure metadata consistency and clean commits, run:
```bash
pip install pre-commit
pre-commit install

## 📊 Latest Benchmarks

![f_chaos_kernel](figures/f_chaos_kernel.png)
![f_sweep_results](figures/f_sweep_results.png)
![release_environment_density](figures/release_environment_density.png)
![release_environment_timeline](figures/release_environment_timeline.png)
![release_doi_growth](figures/release_doi_growth.png)

### 🧪 Peer-Review Addendum: Composite Superoperator Toy

We added a toy model for the reviewer-requested coupling:
\[
\mathcal{L}_{\mathrm{UTF}} = \mathcal{L}_T + \mathcal{L}_D + \mathcal{L}_F + \eta[\mathcal{L}_D, \mathcal{L}_F].
\]

- **Run noise-robustness grid** (Windows-friendly):
  ```cmd
  python scripts\run_noise_robustness.py --etas 0.0,0.05,0.1,0.2 --lams 0.08,0.10,0.12 --sigmas 0.0,1e-3,2e-3,5e-3


## 📦 Release Dashboard

| Release | DOI | Status | Commit | Artifacts |
|----------|-----|--------|---------|------------|
| v0.9.0-beta | [10.5072/zenodo.344960](https://sandbox.zenodo.org/record/344960) | ![](https://img.shields.io/badge/SANDBOX-DOI-lightgray?logo=zenodo) | [`d707d6d`](https://github.com/${ github.repository }/commit/d707d6d) | [f_chaos_kernel.png](./figures_chaos_kernel.png) / [f_sweep_results.png](./figures_sweep_results.png) / [release_doi_growth.png](./figures
elease_doi_growth.png) |









## 📈 Release Analytics  
*(Auto-generated on 2025-10-06 16:06:37 UTC)*  

![DOI Growth](figures/release_doi_growth.png)  
![Environment Timeline](figures/release_environment_timeline.png)  
![Environment Density](figures/release_environment_density.png)  

**Latest DOI:** `10.5072/zenodo.344960`  
**Environment:** `sandbox`  
**Total Releases:** `2`  

---




### 📘 Supplementary Figures (S4–S6)

| Section | Description | CSV | Figure |
|----------|--------------|------|---------|
| S4 | DF Coupling Phase Stability (η–λ) | [`data/supplementary_S4_eta_lambda.csv`](data/supplementary_S4_eta_lambda.csv) | ![](figures/supplementary_S4_eta_lambda.png) |
| S5 | Noise Robustness vs τ_crit | [`data/supplementary_S5_noise_tau.csv`](data/supplementary_S5_noise_tau.csv) | ![](figures/supplementary_S5_noise_tau.png) |
| S6 | Energy Drift Distribution | [`data/supplementary_S6_energy_distribution.csv`](data/supplementary_S6_energy_distribution.csv) | ![](figures/supplementary_S6_energy_distribution.png) |
