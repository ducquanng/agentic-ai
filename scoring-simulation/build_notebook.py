"""
build_notebook.py
=================
Generate scoring_simulation.ipynb directly from scoring_simulation.py so the
notebook and the script are always identical. Splits the script on its
"# ===== Experiment / Figure" banners into one code cell per section, each
preceded by a markdown header. Run:  python build_notebook.py
"""
import json, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
src  = open(os.path.join(HERE, "scoring_simulation.py")).read()

INTRO = r"""# Scoring-logic simulation (Chapter 6)

Reproducible Monte-Carlo study of the comparative risk-scoring logic (SQ3) of the
thesis *"A Model-Validation-Ready Risk Taxonomy, Metrics, and Comparative Scoring
Framework for Agentic AI in Financial Institutions."*

This is a **structural / behavioural analysis of the aggregation operator**: it
establishes properties of the scoring *formula*, not facts about deployed systems
(a verification/exploration exercise in the sense of Sargent, 2010, not an
empirical validation).

**Scoring logic.** The dimension risk score and the use-case composite are

$$R_{id} = 1 - \prod_{j} (1 - \hat{x}_{ij})^{w_j} \qquad (6.2)$$

$$\mathrm{Risk}_i = \max\left( 1 - \prod_{d} (1 - R_{id})^{W_d},\ \ \max_{d \in \mathcal{C}} R_{id} \right) \qquad (6.3)$$

where $\mathcal{C}$ is the set of critical-control dimensions (Access Control,
Action Control, Monitoring and Audit) and the second term is the veto floor.
Risk bands are terciles: Low $< 1/3$, Medium in $[1/3,\ 2/3)$, High $\ge 2/3$.
All randomness is seeded (`SEED = 20260713`); there is no external input data.
"""

banner = re.compile(r'\n# ={60,}\n# (?P<title>[^\n]+)\n# ={60,}\n')
parts, titles, last = [], [], 0
for m in banner.finditer(src):
    parts.append(src[last:m.start()].strip("\n"))
    titles.append(m.group("title").strip())
    last = m.end()
parts.append(src[last:].strip("\n"))     # trailing (figure) section body

SECTION_MD = {
    "Experiment A": "## A. The three illustrative use cases (Table 7.1)",
    "Experiment B:": "## B. Random systems: veto-binding fraction and the analytic bound\nEmpirically confirms mean $\\le$ composite $\\le$ max over 200,000 draws.",
    "Experiment B2": "## B2. Robustness of the veto-binding fraction to the input model\nThe 82.5% is computed under iid Uniform(0,1); here it is re-run under correlated and skewed inputs.",
    "Experiment C": "## C. Sobol' variance-based sensitivity of the composite\nFirst-order $S_i$ (Saltelli et al., 2010) and total-effect $S_{Ti}$ (Jansen, 1999) on independent inputs, with bootstrap 95% CIs.",
    "Experiment D": "## D. Ranking robustness under weight uncertainty (not Sobol')\nDirichlet-perturbed weights; rank-reversal frequency.",
    "Experiment E": "## E. Sensitivity to the ordinal Low/Medium/High encoding",
    "Experiment F": "## F. Aggregation ablation (additive vs geometric vs geometric+veto)",
    "Experiment G": "## G. Consolidated report — every number cited in Section 6.2\nEach line prints the exact value quoted in the thesis, so every figure in the chapter is traceable to computed output.",
    "Figure":       "## Figure: regenerate `sim_scoring.png` (three panels)",
}
def md_for(title):
    for k, v in SECTION_MD.items():
        if title.startswith(k):
            return v
    return "## " + title

cells = [{"cell_type": "markdown", "metadata": {}, "source": INTRO.splitlines(keepends=True)},
         {"cell_type": "markdown", "metadata": {},
          "source": ["## Setup, constants, and scoring functions"]},
         {"cell_type": "code", "execution_count": None, "metadata": {},
          "outputs": [], "source": (parts[0] + "\n").splitlines(keepends=True)}]
for title, body in zip(titles, parts[1:]):
    cells.append({"cell_type": "markdown", "metadata": {},
                  "source": md_for(title).splitlines(keepends=True)})
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": (body + "\n").splitlines(keepends=True)})

nb = {"cells": cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
with open(os.path.join(HERE, "scoring_simulation.ipynb"), "w") as f:
    json.dump(nb, f, indent=1)
print(f"notebook written: {len(cells)} cells")
