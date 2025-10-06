# 🧭 UTF-2.0 PROJECT PLAN — Reproducible Research & Falsification Framework

**Repository:** `utf2_benchmark`  
**Version:** v2.0.0-alpha → v2.1.x  
**Maintainer:** Boonsup Waikham  
**License:** MIT  
**Mission:**  
Develop a fully reproducible, falsifiable open-science framework linking quantum decoherence (𝐷̂), classical chaos (𝐹̂), and mass-energy transmutation (𝐓̂).


---

## 📅 Phase Roadmap

| Phase | Goal | Key Tasks | Check-In Milestone |
|:------|:------|:----------|:-------------------|
| **0 — Initialization ✅** | Stand up reproducible skeleton & CI | • Repo init<br>• Conda env<br>• CI workflow<br>• Pre-commit & hooks | 🟢 *Repo builds; pre-commit fires on first commit* |
| **1 — Core Operators** | Implement operator classes | • `Transmutor` (𝐓̂)<br>• `Transducer` (𝐷̂)<br>• `Transfuser` (𝐹̂)<br>• α, β, λ metrics<br>• Unit tests | 🧩 *All operators callable; tests pass* |
| **2 — Falsification Suite** | Enable Popperian falsifiability | • Energy non-conservation (𝐓̂)<br>• Decoherence violation (𝐷̂)<br>• False chaos amp (𝐹̂)<br>• Coupled 𝐷̂⊗𝐹̂ model<br>• Notebook + batch CLI | 🚨 *`pytest` → “✅ all validated”* |
| **3 — Continuous Validation** | Automate metadata + DOI sync | • Update `zenodo.json`<br>• Auto-gen `CITATION.cff` + `citation.bib`<br>• Append to `tex/references.bib`<br>• CI metadata validator<br>• README DOI banner | 🔁 *Each release = valid DOI sync* |
| **4 — Visualization / Notebook** | Colab-ready education demo | • `utf_falsification_notebook.ipynb`<br>• Plot energy/purity/chaos<br>• Export CSV<br>• Zenodo dataset DOI | 📊 *Notebook runs end-to-end with plots* |
| **5 — Publication & Outreach** | Disseminate & evangelize | • Draft arXiv preprint<br>• Zenodo community record<br>• Tutorial for educators<br>• Showcase submission | 🧬 *arXiv ↔ Zenodo ↔ GitHub fully linked* |

---

## 🗓 Check-In Timeline

| Week | Focus | Deliverable |
|:-----|:-------|:------------|
| 1 | Phase 0 – Init | CI + hooks operational |
| 2 | Phase 1 – Operators | α, β, λ metrics validated |
| 3 | Phase 2 – Falsification | Popper tests all pass |
| 4 | Phase 3 – Validation | DOI auto-sync works |
| 5 | Phase 4 – Notebook | Visualization + export |
| 6 | Phase 5 – Publish | Preprint live & linked |

---

## 🧩 Kanban Board (for GitHub Projects / Notion)

| Column | Example Cards | Definition of Done |
|:--------|:----------------|:------------------|
| **To Do** | Operator refactor • Notebook design • README badge | Described, unstarted |
| **In Progress** | Implementing D̂⊗F̂ coupling • Metadata validator | Code committed, not validated |
| **Review** | Pull request open • CI tests running | Awaiting merge or test results |
| **Blocked** | Waiting for Zenodo token • External dependency | Cannot proceed until resolved |
| **Done** | CI green • Metadata synced | Merged + validated + released |

---

## 🧱 Release Tags & Meaning

| Tag | Description |
|:----|:-------------|
| `v2.0.0-alpha` | Core structure operational |
| `v2.0.0-beta` | Falsification suite validated |
| `v2.0.0-rc1` | CI + Zenodo auto-publishing verified |
| `v2.0.0` | Public reproducible release |
| `v2.1.x` | Visualization + educational updates |

---

## 🧪 Milestone Review Template

Use this block at each milestone review:

```markdown
### Phase N Review (YYYY-MM-DD)
**Status:** ✅ / ⚠️ / ❌  
**Key Artifacts:**  
- …
**Metrics:**  
- Unit tests pass = ____/____  
- DOI sync = ✅ / ❌  
**Notes:**  
- …
**Next Actions:**  
- …


# 🧭 UTF-2.0 Zenodo Reproducibility Integration Plan  
**Version:** v2.0.0-α  
**Maintainer:** Bobo (Science Evangelist)  
**Objective:** Achieve a complete, automated, and reproducible open-science release pipeline — local run → Zenodo archive → badge → validation → publication.

---

## ⚙️ Phase 1 — OAuth & Credential Infrastructure

<details><summary>View details</summary>

| Milestone | Deliverable | Status | Check-in |
|------------|--------------|--------|-----------|
| 1.1 | `.env` template with sandbox + production credentials | ✅ | Initial tokens verified |
| 1.2 | `get_access_token()` supporting client_credentials, auth_code, refresh flows | ✅ | OAuth2 verified |
| 1.3 | Automatic refresh-token storage & reuse | ✅ | `.env` auto-updates |
| 1.4 | Fallback logic to static API tokens | ✅ | Manual override confirmed |

**Check-in 1 →** both sandbox and production authenticated with auto-refresh.  
```bash
python zenodo_upload.py --sandbox


# 🔁 Auto-updated Phase 7.5 — UTF-v2 Project Execution Tracker  
*Last updated: $(date +"%Y-%m-%d %H:%M:%S UTC")*

---

# 🧭 UTF-v2: Reproducible Research Deployment Pipeline  
**Phase 7: Full Auto-Reproducibility & Zenodo Synchronization**

> “Every experiment, every DOI, every benchmark — self-validated, self-archived, and self-documenting.”

---

## 📅 Phase Timeline & Check-Ins

| Phase | Goal | Target | Status | Notes |
|:------|:------|:-------|:-------|:------|
| **7.0** | Establish reproducible codebase (`utf_main.ipynb`, `src/utf/operators.py`) | ✅ Complete | ✅ | Baseline validated |
| **7.1** | Integrate falsification suite (`pytest`, chaos energy checks) | ✅ Complete | ✅ | λ stabilized, tests green |
| **7.2** | Add Zenodo upload & DOI automation (`zenodo_upload.py`) | ✅ Complete | ✅ | Sandbox DOI `10.5072/zenodo.344960` |
| **7.3** | Connect GitHub → Zenodo → DOI auto-sync (CI workflow) | ✅ Complete | ✅ | Auto-updates all metadata files |
| **7.4** | Generate analytics plots & embed in README | ✅ Complete | ✅ | Figures auto-commit via `--ci` |
| **7.5** | Archive artifacts per release (figures, CSV, metadata) | 🟡 In progress | ⏳ | Workflow artifact upload live |
| **7.6** | Comment analytics summary on GitHub release page | 🔜 Planned | 🗓 | Next iteration (via `github-script`) |
| **7.7** | Public Zenodo + arXiv joint release | 🔜 Queued | 🗓 | DOI + arXiv bundle release v1.0 |

---

## 🧩 Current Components Summary

| Module | Function | State |
|:--------|:----------|:------|
| `src/utf/operators.py` | Core T̂, D̂, F̂ operators | ✅ Stable |
| `tests/test_utf.py` | Validation + Falsification suites | ✅ Pass |
| `notebooks/utf_main.ipynb` | Monte Carlo + benchmark runner | ✅ Synced |
| `scripts/run_f_tuning.py` | Local tuning / adaptive kernel | ✅ Functional |
| `scripts/zenodo_upload.py` | OAuth upload + bundle generator | ✅ Live |
| `.github/workflows/zenodo_sync.yml` | DOI + metadata auto-sync CI | ✅ Active |
| `scripts/plot_release_history.py` | Visual analytics + auto-commit | ✅ Verified |
| `data/release_history.csv` | Provenance ledger | ✅ Logging enabled |

---

## ✅ Kanban Checklist

### 🧠 Research Validation
- [x] T̂ Energy Conservation validated  
- [x] D̂ Decoherence irreversibility validated  
- [x] F̂ Chaos bounded energy verified  
- [x] D̂⊗F̂ coupling stable across Monte Carlo sweeps  

### 💾 Reproducibility Backbone
- [x] Conda environment + `.gitignore`  
- [x] Automated unit tests (PyTest)  
- [x] Metadata synchronization (`CITATION.cff / zenodo.json / references.bib`)  
- [x] DOI auto-update via GitHub Actions  
- [x] Sandbox vs Production branch staging  
- [ ] Automated artifact archiving (upload to CI)  
- [ ] GitHub release comment summary (auto)  

### 📊 Analytics + Documentation
- [x] `release_history.csv` provenance ledger  
- [x] Auto-generated figures (`f_sweep_results`, chaos kernel)  
- [x] README auto-updated with plots  
- [x] CI auto-commit of analytics (`--ci`)  
- [ ] “📈 Release Analytics” comment on release page (via `github-script`)  
- [ ] Dashboard enhancement (average Δλ vs time, DOI velocity)  

### 🚀 Publishing
- [x] Sandbox upload tested ✅ (`10.5072/zenodo.344960`)  
- [ ] Production Zenodo DOI mint  
- [ ] arXiv cross-submission  
- [ ] Reproducibility re-run (local → Zenodo → re-execute)  

---

## 🧱 Upcoming Milestones

| Milestone | Deliverable | ETA | Owner |
|:-----------|:-------------|:----|:------|
| **M1** | GitHub release comment bot (`actions/github-script`) | Week 1 | CI bot |
| **M2** | Artifact upload QA + public release bundle | Week 2 | DevOps |
| **M3** | Final Zenodo v1.0 DOI mint + arXiv mirror | Week 3 | Bobo |
| **M4** | Project report + release analytics paper draft | Week 4 | Science Evangelist Lead |

---

## 🪜 Integration Flow

