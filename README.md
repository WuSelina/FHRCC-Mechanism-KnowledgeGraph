# FHRCC Mechanism Knowledge Graph

[![CI](https://github.com/WuSelina/FHRCC-Mechanism-KnowledgeGraph/actions/workflows/ci.yml/badge.svg)](https://github.com/WuSelina/FHRCC-Mechanism-KnowledgeGraph/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A typed, schema-validated knowledge graph of how loss of fumarate hydratase (*FH*) may lead to cancer in FH-deficient renal cell carcinoma (FHRCC / HLRCC-associated RCC) — and a small reasoning engine that ranks the competing explanations by how well each one is supported.

**[Open the interactive explorer →](https://wuselina.github.io/FHRCC-Mechanism-KnowledgeGraph/)**

![Mechanism knowledge graph for FH-deficient RCC](docs/figures/graph_overview.png)

## Why I built it

*FH* inactivation alone is not sufficient for tumorigenesis in mouse models. Downstream metabolic, redox, epigenetic, and signaling adaptations appear to be required for transformation. I could not find a comprehensive pathway diagram for FHRCC tumor formation, so I drew one to study from — and then realized that a static diagram hides the thing I actually wanted to reason about: **which steps are well established, and which ones I am assuming.**

So instead of a diagram, I encoded the biology as a graph where every causal claim carries a confidence weight and an evidence level. That turns a vague "FH loss causes cancer" story into something queryable: I can ask for the best-supported explanation, compare it against the alternatives, and see exactly where the argument gets thin.

## What the graph shows

Querying `gene:FH → phenotype:cancer` returns the metabolic route as the lowest-cost explanation:

> FH loss → TCA cycle blockade → fumarate accumulation → αKG-dependent dioxygenase inhibition → PHD inhibition → HIF stabilization → pseudohypoxia → cancer

But the more interesting result is what the ranking exposes about the evidence behind it:

![Competing explanations and convergence points](docs/figures/path_comparison.png)

- **Every route to cancer passes through at least one hypothesis-level edge.** No path from FH loss to the cancer phenotype can be drawn using supported edges alone — all 6 edges into the cancer node are hypotheses. The graph is confident about the biochemistry and speculative about transformation, which is a fair reflection of the literature.
- **The final step carries most of the uncertainty.** On the best-ranked path, the single weakest edge (pseudohypoxia → cancer, weight 0.35) accounts for 56% of the path's total cost.
- **The top explanations diverge late, not early.** Fumarate accumulation and TCA blockade appear in 100% of the top 8 paths; αKG-dependent dioxygenase inhibition in 75%. The metabolic trunk is forced by the graph's structure; the branching happens downstream, among the metabolic, epigenetic, immune-mediated, and stress-response explanations.

![Evidence levels across the graph and along the best path](docs/figures/evidence_audit.png)

- **53% of all 43 causal claims are hypothesis-level**, and no edge in the graph rests on clinical, genetic-perturbation, or animal-model evidence. Of the 20 supported edges, 16 are review-or-consensus rather than primary data.

That last number is the honest headline of the project. Making it visible was the point of building the graph rather than drawing a diagram — a diagram would have rendered the speculative arrows exactly like the well-established ones.

Full auto-generated summary: [`reports/graph_audit.md`](reports/graph_audit.md). Example query output: [`reports/fh-loss_to_cancer_top5.md`](reports/fh-loss_to_cancer_top5.md).

## How it works

**Nodes** are biological entities or states (gene, protein, metabolite, process, state, pathway, phenotype). **Edges** are directed mechanism claims carrying a typed predicate (`causes`, `inhibits`, `enables`, …), a confidence weight in `[0.01, 0.99]`, an evidence level, and an optional mechanism note.

Path search is Dijkstra-style over an interpretable additive cost:

```
edge cost = −ln(confidence weight) + predicate penalty
```

Low-confidence edges and vague predicates both make a path more expensive, so the lowest-cost path is the explanation that leans least on weak claims and hand-waving verbs. `associates_with` costs 2.0; `causes` costs 0. Ranking the top *k* paths surfaces competing explanations instead of a single answer.

The schema is enforced at load time: node IDs must match their declared type, weights must be in range, self-loops and dangling edges are rejected. `scripts/kg.py lint` adds softer warnings — overused vague predicates, hypothesis edges with suspiciously high weights, high-weight edges with no stated mechanism, and contradictory edge pairs.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .                 # add ".[viz]" to regenerate the figures
```

```bash
# Validate the graph against the schema
python scripts/kg.py validate data/fhrcc_pathway_v1.json

# Summary counts, and lint warnings about graph hygiene
python scripts/kg.py summarize data/fhrcc_pathway_v1.json
python scripts/kg.py lint data/fhrcc_pathway_v1.json

# Find nodes by keyword
python scripts/kg.py find data/fhrcc_pathway_v1.json hif

# Rank the top 5 mechanistic explanations, with per-edge mechanism notes
python scripts/kg.py explain data/fhrcc_pathway_v1.json gene:FH phenotype:cancer \
    -k 5 --max-hops 14 --verbose

# ...and save it as a Markdown report
python scripts/kg.py explain data/fhrcc_pathway_v1.json gene:FH phenotype:cancer \
    -k 5 --max-hops 14 --verbose --out-md reports/fh-loss_to_cancer_top5.md
```

Regenerate every figure, the interactive explorer, and the audit report:

```bash
python scripts/build_showcase.py
```

## Reading the output

- **Path** — one plausible mechanistic explanation, *not* a prediction.
- **Cost** — lower is better supported. Rises with lower confidence, vaguer predicates, and hypothesis-level claims.
- **Hops** — number of mechanistic steps.
- **Top *k*** — the *k* lowest-cost paths, so metabolic, epigenetic, immune-mediated, and stress-response explanations can be compared side by side.

In the explorer, "fade hypothesis-level edges" is the fastest way to see how much of the map is assumption.

## Scope and limitations

This is a study tool and an exploratory side project, not a clinical or predictive instrument. See [`docs/scope_and_goals.md`](docs/scope_and_goals.md) and [`docs/biological_assumptions.md`](docs/biological_assumptions.md), which state what the graph claims and what it explicitly does not.

In short, the graph does **not** claim that FH loss alone is sufficient for cancer, that all FH-deficient tumors follow one trajectory, that NRF2 activation / HIF stabilization / CIMP are independently oncogenic, or that pathway activation implies a therapeutic vulnerability. Paths are explanations, not predictions. Weights encode confidence and specificity, never effect size.

Known limitations: incomplete coverage; literature bias toward well-studied pathways (HIF, NRF2); loss of cell-type, timing, and dosage context; and `gene:FH` standing in for biallelic FH loss rather than the wild-type gene.

**Citations are not yet populated.** The schema supports a `citations` field on every edge, but v1 leaves it empty — my references live in my study notes. This is the single biggest gap, and the next thing I would fix.

## Next steps

- Populate edge citations (PMIDs/DOIs) so each claim is independently checkable.
- Distinguish `gene:FH` (wild-type) from `state:FH_loss` explicitly.
- Sensitivity analysis: how much do the rankings move when weights are perturbed?
- Compare the FH-deficient graph against a VHL-driven ccRCC graph to separate shared phenotypes from shared causes.

## Repository layout

```
data/     graph JSON (full v1 graph + a minimal FH→NRF2 example)
src/      library: schema, graph, IO, path search, analysis, layout, figures, explorer
scripts/  CLI (kg.py) and the showcase builder
docs/     assumptions, scope, schema, generated figures, GitHub Pages explorer
reports/  example query output and the auto-generated graph audit
tests/    34 tests covering schema, IO, ranking, layout, and rendering
```

## References and tools

- Background reading on knowledge graphs and design brainstorming
    - https://doi.org/10.1093/bioinformatics/btaf383
    - https://doi.org/10.1093/bioinformatics/btad418
    - https://pmc.ncbi.nlm.nih.gov/articles/PMC7327409/
    - https://samadritaghosh.medium.com/knowledge-graphs-what-why-and-how-84f920316ca5
    - https://lopezyse.medium.com/knowledge-graphs-from-scratch-with-python-f3c2a05914cc
    - https://www.kaggle.com/code/nageshsingh/build-knowledge-graph-using-python
- Typed schema approach
    - https://pmc.ncbi.nlm.nih.gov/articles/PMC9372416/
    - https://academic.oup.com/bioinformatics/article/41/7/btaf383/8177146
    - https://neo4j.com/blog/knowledge-graph/how-to-build-knowledge-graph/
    - https://neo4j.com/developer/graph-database/
- Interactive explorer rendered with [Cytoscape.js](https://js.cytoscape.org/)
- AI assistants (ChatGPT, Claude) helped with code drafting, figure scripting, and documentation. The biological model, the curated data, and the interpretation are my own.

## License

MIT — see [LICENSE](LICENSE).
