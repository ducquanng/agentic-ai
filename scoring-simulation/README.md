# Scoring-logic simulation — reproducibility package

Supplementary material for the thesis *"A Model-Validation-Ready Risk Taxonomy,
Metrics, and Comparative Scoring Framework for Agentic AI in Financial
Institutions."* It reproduces the Monte-Carlo study of the comparative
risk-scoring logic (Chapter 6) and the figure `sim_scoring.png`.

This is a **structural / behavioural analysis of the aggregation operator**: it
establishes properties of the scoring *formula* under stated input assumptions.
It is a verification/exploration exercise (Sargent, 2010), **not** an empirical
validation of risk levels in deployed systems — that would need real system data,
which do not yet exist.

## Contents
- `scoring_simulation.ipynb` — documented Jupyter notebook (equations, all
  experiments, printed results, and the figure). Ships already executed.
- `scoring_simulation.py`    — the same logic as a plain script (`python scoring_simulation.py`).
- `outputs/`                 — generated results:
  - `sim_scoring.png`          the three-panel figure used in the thesis
  - `use_cases.csv`            the three illustrative use cases, their scores and risk bands
  - `random_summary.csv`       veto-binding rate (+ MCSE), mean scores, analytic-bound check
  - `binding_robustness.csv`   veto-binding rate under correlated / skewed input models
  - `sobol_indices.csv`        Sobol' first-order and total-effect indices (+ 95% bootstrap CIs)
  - `rank_stability.csv`       each use case's rank distribution over 20,000 weight draws (+ MCSE)
  - `encoding_sensitivity.csv` scores/bands under alternative Low/Medium/High encodings
  - `aggregation_ablation.csv` scores under additive vs geometric vs geometric+veto
  - `section_6_2_numbers.csv`  **every number quoted in Section 6.2 next to its computed value** (traceability)
- `requirements.txt`         — dependencies (numpy, scipy, matplotlib; jupyter/nbconvert for the notebook).

## Reproducibility
All randomness is Monte-Carlo and seeded (`SEED = 20260713`, NumPy `default_rng`;
Sobol' sampling via `scipy.stats.qmc.Sobol` with the same seed). There is **no
external input data**: the profiles are generated in code, so re-running
reproduces every number and the figure exactly.

**Traceability.** Every figure quoted in Chapter 6, Section 6.2 (e.g. "82.5% of
cases", "0.29 under a plain average", "93% of the movement") is printed by the
script as computed output — see the final "SECTION 6.2 numbers" block (Experiment
G) and `outputs/section_6_2_numbers.csv`, which lists each thesis value beside the
number the code actually produces. Nothing in the text is asserted by hand.

## How to run
```bash
pip install -r requirements.txt
python scoring_simulation.py                       # -> writes outputs/
# or, for the notebook:
jupyter nbconvert --to notebook --execute --inplace scoring_simulation.ipynb
```

## What it shows (results)
1. **Illustrative use cases.** UC-A = 0.50 (Medium), UC-B = 0.80 (High), UC-C =
   0.80 (High). UC-A's score is set by the veto floor (Medium on Monitoring &
   Audit), so it is Medium, not Low; UC-B and UC-C tie on the composite and are
   separated only by the seven-dimension fingerprint.
2. **Analytic bound (checked empirically).** For every one of 200,000 random
   systems, arithmetic-mean ≤ composite ≤ maximum, so the rule is *partly
   compensatory* — strictly between the fully-compensatory mean and the
   non-compensatory maximum (means 0.50 / 0.61 / 0.77 / 0.88).
3. **Veto floor binds — and it is not an artefact of the uniform assumption.**
   Under iid Uniform(0,1) inputs the veto term is the binding term in 82.5% of
   systems (MCSE 0.08 pp). This is partly mechanical (E[max of 3] = 0.75 vs
   E[mean of 7] = 0.50). Correlating the dimensions (ρ = 0.3, 0.6) or skewing the
   risk marginals only raises it (to ≈ 87%), so the uniform reference is a
   conservative floor, not a fragile artefact.
4. **Sobol' sensitivity.** Of the composite's output variance, the three
   critical-control dimensions carry **93%** of the total-effect (each S_Ti ≈
   0.41 vs ≈ 0.02 for the other four); first-order indices sum to 0.73, the
   remaining ≈ 27% being interaction variance from the `max()`. This is a proper
   variance decomposition on independent inputs, where the classic estimators are
   valid.
5. **Ranking robustness (weight uncertainty).** Over 20,000 Dirichlet weight
   perturbations the rankings are stable (modal rank held in 91-100% of draws; 0
   of 15 pairs "too close to call"), because veto-bound scores do not depend on
   the weights. This is a rank-reversal robustness analysis, **not** a Sobol'
   index.
6. **Ordinal-encoding robustness.** Under five monotone Low/Medium/High encodings
   (including an asymmetric one) UC-A stays Medium and UC-B, UC-C stay High, and
   the ordering never flips — the conclusion does not depend on the 0.2/0.5/0.8
   choice.

## Method note (equations, Chapter 6)
Dimension score  R_id = 1 - prod_j (1 - x_hat_ij)^{w_j}                    (Eq. 6.2)
Composite        Risk_i = max( 1 - prod_d (1-R_id)^{W_d}, max_{d in C} R_id ) (Eq. 6.3)
with C = {Access Control, Action Control, Monitoring & Audit} (the veto floor).
Risk bands are terciles: Low < 1/3 ≤ Medium < 2/3 ≤ High.

Sobol' estimators: first-order S_i (Saltelli et al., 2010), total-effect S_Ti
(Jansen, 1999), on a Sobol' quasi-random Saltelli design; 95% CIs by bootstrap.
