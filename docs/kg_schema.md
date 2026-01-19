# KG Schema
* Current schema version: `0.1.0`

This document defines the minimal, enforceable schema.

## Node
A **node** represents a biological state or entity.

Required:
- `id`: `<type>:<name>` string; unique within the graph; lowercase
- `type`: string; the node type
- `name`: string

Optional:
- `synonyms`: list[string]
- `description`: string
- `xrefs`: dict[string, string]
- `tags`: list[string]

## Edge
An **edge** represents a mechanism path/explanation (with type) connecting two nodes.

Required:
- `subject`: string; the node id
- `predicate`: string; one of the allowed predicates below
- `object`: string
- `weight` in `[0.01, 0.99]` (confidence; not effect size)
- `evidence_level`: string; one of the allowed evidence levels below

Optional:
- `polarity` in `{+, -, 0}`: string; direction of influence
- `mechanism`: string; short phrase describing the mechanism
- `context`: dict[string, string]; Examples: `{ "tissue": "kidney", "cell_type": "renal_epithelial", "species": "human" }`
- `citations`: list[string]
- `notes`: string

## Allowed node types
- `gene`, `protein`, `metabolite`, `complex`, `process`, `state`, `pathway`, `phenotype`, `cell_type`, `compartment`, `therapy`

## Allowed predicates
- `causes`, `enables`, `prevents`
- `increases`, `decreases`, `activates`, `inhibits`, `stabilizes`, `destabilizes`
- `converts_to`, `accumulates`, `inhibits_activity_of`, `modifies`, `binds`, `translocates_to`
- `associates_with` (discouraged; should be penalized in reasoning)

## Evidence levels
- `biochemical_direct` (e.g. enzyme inhibition shown in vitro)
- `genetic_perturbation` (KO/KD/rescue experiments)
- `cell_model` (cell line/ organoid evidence)
- `animal_model`
- `patient_omics` (association in cohorts, profiling studies)
- `clinical` (trial/response evidence)
- `review_or_consensus`
- `hypothesis`

## Weight Semantics
* `0.80–0.99`: Direct biochemical mechanism with multiple studies showing experimental support
* `0.60–0.79`: Multiple sources of evidence but some context dependence
* `0.40–0.59`: Plausible, supported indirectly or inconsistently
* `0.01–0.39`: Speculative, lack of or weak association
