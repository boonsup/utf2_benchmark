[![DOI](https://sandbox.zenodo.org/badge/DOI/10.5072/zenodo.344960.svg)](https://doi.org/10.5072/zenodo.344960)
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


## 📦 Release Dashboard

| Release | DOI | Status | Commit | Artifacts |
|----------|-----|--------|---------|------------|
| v0.9.0-beta | [unpublished](https://zenodo.org/record/unpublished) | ![](https://img.shields.io/badge/UNKNOWN-DOI-gray?logo=zenodo) | [`e22c218`](https://github.com/${ github.repository }/commit/e22c218) | [f_chaos_kernel.png](./figures\f_chaos_kernel.png) / [f_sweep_results.png](./figures\f_sweep_results.png) / [f_sweep_results.csv](./data\f_sweep_results.csv) |







## 📈 Release Analytics  
*(Auto-generated on 2025-10-06 14:53:28 UTC)*  

![DOI Growth](figures/release_doi_growth.png)  
![Environment Timeline](figures/release_environment_timeline.png)  
![Environment Density](figures/release_environment_density.png)  

**Latest DOI:** `10.5072/zenodo.344960`  
**Environment:** `sandbox`  
**Total Releases:** `2`  

---


