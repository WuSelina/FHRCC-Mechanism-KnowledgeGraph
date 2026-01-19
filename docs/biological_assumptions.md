# Biological Assumptions
This document outlines the biological assumptions and uncertainties in this "FHRCC_mechanismKG" project. It notes what the knowledge graph (KG) *claims*, what it *does not claim*, and how mechanistic uncertainty is represented.

The disease of focus is fumarase-deficient renal cell carcinoma (FHRCC), but other important mechanisms in RCCs are hinted at.

This KG is a study tool and fun side-project. Errors are likely, and there are limitations.

Examples of limitations:
- Context loss: cell type, timing, and dose dependencies are simplified or omitted.
- Literature bias: well-studied pathways are overrepresented relative to understudied mechanisms.


## 1. Causal Premise
**"Biallelic loss of *FH* is the initiating event in FH-deficient RCC tumorigenesis."**
- FH loss results in intracellular accumulation of fumarate due to blockage of the fumarate --> malate step of the TCA cycle.
- Fumarate accumulation is treated as a *local, cell-intrinsic oncometabolite*, not a systemic metabolic state.
- FH loss is considered necessary but not sufficient for cancer transformation.

### 1.1 Interpretation of FH in the KG
Although the node is labeled `gene:FH`, all causal edges from FH in this KG represent **loss of FH function** rather than normal *FH* gene activity. The KG does not currently encode wild-type (WT) FH activity as a separate state. Thus, `gene:FH` should be interpreted as a shorthand for *FH loss* in the context of FHRCC.

The KG encodes FH loss as a *root causal event*, but does not encode FH loss as a direct or certain cause of cancer.

## 2. Primary Biochemical Consequences (Deterministic Layer)
Fumarate accumulation is treated as a high-confidence biochemical consequence of FH loss. Fumarate accumulation results in:
- **Inhibition of alpha-ketoglutarate-dependent dioxygenases (alphaKGDDs)**, including:
    - Prolyl hydroxylases (PHDs)
    - TET DNA demethylases
    - Histone lysine demethylases (KDMs)
- **Protein succination** of cysteine residues

These relationships are encoded as *direct mechanistic edges* with high confidence weights.

## 3. Adaptive Survival Programs (Contextual Layer)
FH loss creates a broadly toxic cellular state. Most cells undergo apoptosis, senescence, or growth arrest. The KG assumes:
- Only a subset of renal epithelial cells can survive long enough to adapt.
- Adaptation, not proliferation, is the immediate consequence of FH loss.

Highlighted adaptive programs:

### 3.1 NRF2 Antioxidant Axis
- Succination of KEAP1 impairs NRF2 degradation.
- Stabilized NRF2 activates antioxidant response (e.g. NRF2-ARE pathway).
- NRF2 activation is considered an adaptation, not an oncogenic driver.

### 3.2 "Pseudohypoxia" and Metabolic Rewiring
- Accumulated fumarate inhibits PHDs, resulting in stabilization of HIF transcription factors (TFs).
- HIF activation induces (highlighted):
    - Glycolysis
    - Angiogenic signaling (e.g. VEGF)
    - Nutrient transport

HIF activation is modeled as a survival and metabolic adaptation rather than a proliferative driver.
The pseudohypoxic state is encoded alongside VHL loss, but they are not the same. VHL loss is included as a reminder of other RCCs.

### 3.3 Epigenetic Reprogramming (CIMP)
- Inhibition of TET and KDM enzymes leads to global DNA and histone hypermethylation.
- Hypermethylation is treated as:
    - Widespread
    - Non-kidney-specific
    - Insufficient alone to cause cancer

Epigenetic changes are encoded as state-altering modifiers that increase fitness rather than direct drivers.

## 4. Mitochondrial Stress and Immune Consequences
Assumptions:
- Fumarate accumulation leads to mitochondrial (mt) damage and elevated reactive oxygen species (ROS).
- Mitochondrial damage can result in mtDNA leakage into the cytosol.
- As a result, chronic activation of innate immune sensing pathways may occur, but innate immune activation does not mean increase in anti-tumor immunity.
- Instead, chronic signaling is modeled as contributing to an immunosuppressive tumor microenvironment (TME).

These edges are encoded with moderate confidence and higher uncertainty. These effects are modeled as tumor-intrinsic! Not systemic immune activation.

## 5. Cancer Progression/Development Is Conditional, Not Universal
Assumptions:
- Many FHRCC tumors show no recurrent secondary driver mutations in genes.
- Some tumors acquire "cooperating alterations" (e.g. NF2 loss, activated RTK signaling).
- Chromosomal and epigenetic instability may drive tumorigenesis over point/indel mutations.

Therefore:
- Secondary pathways (e.g. Hippo, PI3K/AKT/mTOR) are encoded as facilitators, not requirements. Their presence increases the probability of malignancy but is not necessary.

## 6. Comparison to VHL-Driven ccRCC
The KG encodes FH loss and VHL loss as mechanistically distinct despite shared downstream features.
- VHL loss: permissive, broadly tolerated, low intrinsic toxicity
- FH loss: broadly toxic, survival-limited

Shared outputs (e.g. HIF stabilization/activation, angiogenesis) are modeled as shared phenotypes, not shared causes.

## 7. What This KG Does NOT Claim
- FH loss alone is sufficient for cancer
- All FH-deficient tumors follow the same evolutionary trajectory
- NRF2 loss, HIF stabilization, or CIMP phenotype are independently oncogenic
- Secondary alterations are universal (or required)
- Pathway activation implies therapeutic vulnerability

## Reference Network
![FHRCC draft network](.\screenshots\screenshot_pathway_draft.png)
