# AlphaDefense — Quantitative Fraud Detection with Explainable AI, Risk Analytics & Fairness Auditing

AlphaDefense is a fraud detection platform that brings quantitative finance rigor — GARCH volatility modeling, Value at Risk, Bayesian reasoning — together with explainable AI and fairness auditing, to detect financial fraud in a way that is accurate, interpretable, and auditable for bias. Most fraud models are black boxes tuned only for accuracy on wildly imbalanced data. AlphaDefense is built to justify every decision it makes and to prove it isn't discriminating against protected groups while doing so — because in real fintech deployments, "the model said so" is not good enough for a regulator, a compliance team, or a customer who got wrongly flagged.

**Dataset:** IEEE-CIS Fraud Detection (590,540 transactions, 394 features, ~3.5% fraud rate — a genuinely hard imbalanced classification problem, not a toy dataset).

---

## Why this project exists

Fraud detection sits at the intersection of three things most ML portfolios treat separately: predictive modeling, financial risk quantification, and responsible AI. Companies like Feedzai, JPMorgan, PayPal Risk, and SEON hire specifically for engineers who can do all three — not just train a classifier, but explain it, stress-test it under risk scenarios, and audit it for fairness before it touches real customers. AlphaDefense is built end-to-end as proof of that full skillset, not a single notebook demo.

---

## Architecture

```
Raw Transaction Data (IEEE-CIS)
        │
        ▼
Phase 1 — EDA & Data Understanding
        │
        ▼
Phase 2 — XGBoost Model (scale_pos_weight for 3.5% fraud imbalance)
        │
        ▼
Phase 3 — SHAP Explainability (every prediction gets a reason)
        │
        ▼
Phase 4 — Quantitative Risk Layer (VaR + GARCH volatility modeling)
        │
        ▼
Phase 5 — Fairness Audit (Fairlearn — bias across protected groups)
        │
        ▼
Phase 6 — Serving Layer (FastAPI backend + Streamlit dashboard)
        │
        ▼
Phase 7 — MLOps (MLflow, Docker, GitHub Actions CI/CD, Evidently AI drift detection)
        │
        ▼
Phase 8 — Cloud Deployment (AWS SageMaker / GCP Vertex AI, live monitoring, automated retraining)
```

---

## Project Status

This project is being built and documented phase by phase, in public, with each phase gate-checked before moving to the next — no phase is marked complete until it's actually built, explained, and stress-tested.

| Phase | Component | Status |
|---|---|---|
| 1 | Exploratory Data Analysis (integrity, imbalance, missingness, distributions, categorical structure, correlation/leakage, temporal structure, findings) | 🔄 In Progress |
| 2 | XGBoost model with `scale_pos_weight` for class imbalance | ⏳ Planned |
| 3 | SHAP explainability layer | ⏳ Planned |
| 4 | Value at Risk + GARCH volatility modeling for risk analytics | ⏳ Planned |
| 5 | Fairlearn fairness auditing | ⏳ Planned |
| 6 | FastAPI backend + Streamlit dashboard | ⏳ Planned |
| 7 | MLOps: MLflow, Docker, GitHub Actions CI/CD, Evidently AI | ⏳ Planned |
| 8 | Cloud deployment (SageMaker/Vertex AI) with monitoring + retraining | ⏳ Planned |

Live, granular progress (sub-phase level, what's built vs. what's just designed) is tracked in [`PROGRESS_LOG.md`](./PROGRESS_LOG.md).

---

## Phase 1 — Exploratory Data Analysis (current phase)

Split into 8 sub-phases, each gated on a real finding, not just a plot:

1. **Integrity & Loading** — memory-safe loading of a 394-column, 590K-row dataset on constrained hardware (explicit dtype specification at read time, not post-hoc downcasting, to avoid peak memory spikes from holding both float64 and float32 copies simultaneously).
2. **Target & Imbalance** — establishing why accuracy is a meaningless metric at 3.5% fraud prevalence, and how `scale_pos_weight` corrects the training gradient without touching inference.
3. **Missing Value Structure** — traced two separate missingness patterns (`id_13`/`id_16`, `addr2`) back to a single root cause: `ProductCD` category, not identity-data presence itself, drives both the missingness rate and the fraud rate. This is a confounder-detection finding, not a surface-level null count.
4. **Numerical Distributions & Outliers** — multicollinearity screening via VIF across the dataset's PCA-derived V-column blocks, distinguishing global multicollinearity (VIF) from pairwise correlation, and why redundant features specifically damage SHAP attribution even when they don't hurt XGBoost's raw accuracy.
5. **Categorical Structure & Cardinality**
6. **Correlation & Leakage Detection**
7. **Temporal Structure** — verified a genuine chronological (non-shuffled) train/test split using `TransactionDT`, caught and fixed a hardcoded-string bug that was masking real fraud-rate output, and confirmed fraud prevalence stability across the time-based split (train 3.51%, test 3.44%).
8. **Findings Report** — consolidated write-up of every EDA finding as input to feature engineering decisions in Phase 2.

### Key finding so far: the ProductCD confounder

`DeviceType`, `id_13`, `id_16`, and `addr2` all show strong-looking correlations between missingness and fraud rate — the kind of pattern that tempts you to engineer a `was_missing` flag as a new feature. Digging into *why* the missingness happens revealed it's not identity-data absence causing fraud risk — it's that `ProductCD` category determines both whether identity/device data gets collected at all *and* the base fraud rate for that transaction type. Engineering a missingness-flag feature here would be redundant with information `ProductCD` already encodes. This is the difference between finding a correlation and finding the actual driver behind it.

*(Chart: missingness rate vs. fraud rate by ProductCD — image embedded below once exported. See "Adding plots to this README" section for the exact steps.)*

---

## Tech Stack

**Data & Modeling:** Python, Pandas, NumPy, XGBoost, scikit-learn
**Explainability:** SHAP
**Quantitative Risk:** `arch` (GARCH), Value at Risk methods
**Fairness:** Fairlearn
**Serving:** FastAPI, Streamlit
**MLOps:** MLflow, Docker, GitHub Actions, Evidently AI
**Deployment:** AWS SageMaker / GCP Vertex AI

*(This list reflects the full planned stack — components move from "planned" to "in use" as each phase is actually built; see Project Status table above.)*

---

## Repository Structure

```
AlphaDefense/
├── README.md                  ← you are here
├── PROGRESS_LOG.md             ← granular sub-phase progress tracking
├── phase_0_setup/               ← environment, data loading foundation
│   └── ...
├── phase_1_eda/                  ← EDA sub-phases 1-8
│   └── ...
└── images/                        ← exported charts referenced in this README
```

---

## Running This Project

```bash
git clone https://github.com/<your-username>/AlphaDefense.git
cd AlphaDefense
pip install -r requirements.txt
```

Detailed run instructions per phase are added as each phase is completed — this section will expand as the FastAPI/Streamlit layer comes online.

---

## About the Author

Krrish — B.Tech CSE (AI & ML) student, building AlphaDefense as a flagship project toward ML engineering roles in fraud detection and fintech risk. Documenting the full build process, including real bugs found and fixed, on :https://www.linkedin.com/in/krrish-malhan-479074384/.
