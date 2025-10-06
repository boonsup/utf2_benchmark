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
