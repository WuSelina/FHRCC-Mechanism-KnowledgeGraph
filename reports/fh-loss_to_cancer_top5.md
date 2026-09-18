# Explainable paths: gene:FH -> phenotype:cancer

## Path 1 (cost = 3.316, hops = 7)

1. FH [gene:FH] --causes--> TCA cycle blockade [process:tca_cycle_blockade] (w = 0.90, ev = review_or_consensus, cost = 0.105, pred_pen = 0.00)
    - mechanism: loss of FH activity blocks fumarate to malate, leading to fumarate accumulation
    - notes: Represents effect of FH loss rather than normal FH enzymatic activity.

2. TCA cycle blockade [process:tca_cycle_blockade] --causes--> Fumarate [metabolite:fumarate] (w = 0.90, ev = review_or_consensus, cost = 0.105, pred_pen = 0.00)
    - mechanism: fumarate accumulates upstream of FH blockade

3. Fumarate [metabolite:fumarate] --inhibits_activity_of--> αKG-dependent dioxygenase inhibition [process:akg_dioxygenase_inhibition] (w = 0.75, ev = review_or_consensus, cost = 0.388, pred_pen = 0.10)
    - mechanism: competitive inhibition of αKG-dependent dioxygenases by fumarate

4. αKG-dependent dioxygenase inhibition [process:akg_dioxygenase_inhibition] --causes--> HIF prolyl hydroxylase (PHD) inhibition [process:PHD_inhibition] (w = 0.70, ev = review_or_consensus, cost = 0.357, pred_pen = 0.00)
    - mechanism: PHDs are a subset of αKG-dependent dioxygenases

5. HIF prolyl hydroxylase (PHD) inhibition [process:PHD_inhibition] --causes--> HIF stabilization [state:HIF_stabilization] (w = 0.80, ev = review_or_consensus, cost = 0.223, pred_pen = 0.00)
    - mechanism: reduced hydroxylation reduces HIFα degradation

6. HIF stabilization [state:HIF_stabilization] --causes--> Pseudohypoxia [state:pseudohypoxia] (w = 0.75, ev = review_or_consensus, cost = 0.288, pred_pen = 0.00)
    - mechanism: stabilized HIF activates hypoxia-response transcription in normoxia

7. Pseudohypoxia [state:pseudohypoxia] --enables--> Cancer state [phenotype:cancer] (w = 0.35, ev = hypothesis, cost = 1.850, pred_pen = 0.80)
    - mechanism: pseudohypoxia supports survival, angiogenesis, and growth programs
    - notes: Facilitator edge.

## Path 2 (cost = 3.459, hops = 7)

1. FH [gene:FH] --causes--> TCA cycle blockade [process:tca_cycle_blockade] (w = 0.90, ev = review_or_consensus, cost = 0.105, pred_pen = 0.00)
    - mechanism: loss of FH activity blocks fumarate to malate, leading to fumarate accumulation
    - notes: Represents effect of FH loss rather than normal FH enzymatic activity.

2. TCA cycle blockade [process:tca_cycle_blockade] --causes--> Fumarate [metabolite:fumarate] (w = 0.90, ev = review_or_consensus, cost = 0.105, pred_pen = 0.00)
    - mechanism: fumarate accumulates upstream of FH blockade

3. Fumarate [metabolite:fumarate] --inhibits_activity_of--> αKG-dependent dioxygenase inhibition [process:akg_dioxygenase_inhibition] (w = 0.75, ev = review_or_consensus, cost = 0.388, pred_pen = 0.10)
    - mechanism: competitive inhibition of αKG-dependent dioxygenases by fumarate

4. αKG-dependent dioxygenase inhibition [process:akg_dioxygenase_inhibition] --causes--> TET/KDM demethylase inhibition [process:TET_KDM_inhibition] (w = 0.65, ev = review_or_consensus, cost = 0.431, pred_pen = 0.00)
    - mechanism: TET/KDM enzymes are αKG-dependent dioxygenases inhibited by fumarate

5. TET/KDM demethylase inhibition [process:TET_KDM_inhibition] --causes--> Global DNA hypermethylation [process:DNA_hypermethylation] (w = 0.70, ev = patient_omics, cost = 0.357, pred_pen = 0.00)
    - mechanism: impaired demethylation shifts epigenome toward hypermethylation

6. Global DNA hypermethylation [process:DNA_hypermethylation] --causes--> CpG island methylator phenotype (CIMP) [phenotype:CIMP] (w = 0.70, ev = patient_omics, cost = 0.357, pred_pen = 0.00)
    - mechanism: global hypermethylation manifests as CpG island methylator phenotype

7. CpG island methylator phenotype (CIMP) [phenotype:CIMP] --enables--> Cancer state [phenotype:cancer] (w = 0.40, ev = hypothesis, cost = 1.716, pred_pen = 0.80)
    - mechanism: epigenetic reprogramming may increase evolutionary plasticity / malignant potential
    - notes: Encodes 'necessary vs sufficient' uncertainty.

## Path 3 (cost = 3.810, hops = 5)

1. FH [gene:FH] --causes--> TCA cycle blockade [process:tca_cycle_blockade] (w = 0.90, ev = review_or_consensus, cost = 0.105, pred_pen = 0.00)
    - mechanism: loss of FH activity blocks fumarate to malate, leading to fumarate accumulation
    - notes: Represents effect of FH loss rather than normal FH enzymatic activity.

2. TCA cycle blockade [process:tca_cycle_blockade] --causes--> Fumarate [metabolite:fumarate] (w = 0.90, ev = review_or_consensus, cost = 0.105, pred_pen = 0.00)
    - mechanism: fumarate accumulates upstream of FH blockade

3. Fumarate [metabolite:fumarate] --causes--> Oxidative stress [state:oxidative_stress] (w = 0.55, ev = review_or_consensus, cost = 0.598, pred_pen = 0.00)
    - mechanism: redox imbalance and succination-associated stress under FH loss
    - notes: Simplified: ROS/oxidative stress is context-dependent and may vary by model.

4. Oxidative stress [state:oxidative_stress] --activates--> NRF2-ARE antioxidant response [pathway:NRF2_ARE] (w = 0.55, ev = hypothesis, cost = 0.998, pred_pen = 0.40)
    - mechanism: oxidative stress can impair KEAP1-mediated NRF2 degradation, increasing NRF2-ARE activity.
    - notes: Stress context may increase reliance on NRF2; directionality is conceptual.

5. NRF2-ARE antioxidant response [pathway:NRF2_ARE] --enables--> Cancer state [phenotype:cancer] (w = 0.30, ev = hypothesis, cost = 2.004, pred_pen = 0.80)
    - mechanism: antioxidant adaptation can enable survival under metabolic stress
    - notes: Not claiming NRF2 is an oncogene here; survival-enabling framing.

## Path 4 (cost = 4.520, hops = 7)

1. FH [gene:FH] --causes--> TCA cycle blockade [process:tca_cycle_blockade] (w = 0.90, ev = review_or_consensus, cost = 0.105, pred_pen = 0.00)
    - mechanism: loss of FH activity blocks fumarate to malate, leading to fumarate accumulation
    - notes: Represents effect of FH loss rather than normal FH enzymatic activity.

2. TCA cycle blockade [process:tca_cycle_blockade] --causes--> Fumarate [metabolite:fumarate] (w = 0.90, ev = review_or_consensus, cost = 0.105, pred_pen = 0.00)
    - mechanism: fumarate accumulates upstream of FH blockade

3. Fumarate [metabolite:fumarate] --modifies--> Protein succination [process:protein_succination] (w = 0.85, ev = biochemical_direct, cost = 0.363, pred_pen = 0.20)
    - mechanism: succination of cysteine residues (2SC adducts)

4. Protein succination [process:protein_succination] --inhibits--> KEAP1 [protein:KEAP1] (w = 0.70, ev = cell_model, cost = 0.757, pred_pen = 0.40)
    - mechanism: KEAP1 succination impairs NRF2 degradation

5. KEAP1 [protein:KEAP1] --inhibits--> NRF2 [protein:NRF2] (w = 0.80, ev = review_or_consensus, cost = 0.623, pred_pen = 0.40)
    - mechanism: KEAP1 targets NRF2 for degradation (baseline regulation)

6. NRF2 [protein:NRF2] --activates--> NRF2-ARE antioxidant response [pathway:NRF2_ARE] (w = 0.85, ev = review_or_consensus, cost = 0.563, pred_pen = 0.40)
    - mechanism: NRF2 transcriptional activation of antioxidant response genes

7. NRF2-ARE antioxidant response [pathway:NRF2_ARE] --enables--> Cancer state [phenotype:cancer] (w = 0.30, ev = hypothesis, cost = 2.004, pred_pen = 0.80)
    - mechanism: antioxidant adaptation can enable survival under metabolic stress
    - notes: Not claiming NRF2 is an oncogene here; survival-enabling framing.

## Path 5 (cost = 5.463, hops = 8)

1. FH [gene:FH] --causes--> TCA cycle blockade [process:tca_cycle_blockade] (w = 0.90, ev = review_or_consensus, cost = 0.105, pred_pen = 0.00)
    - mechanism: loss of FH activity blocks fumarate to malate, leading to fumarate accumulation
    - notes: Represents effect of FH loss rather than normal FH enzymatic activity.

2. TCA cycle blockade [process:tca_cycle_blockade] --causes--> Fumarate [metabolite:fumarate] (w = 0.90, ev = review_or_consensus, cost = 0.105, pred_pen = 0.00)
    - mechanism: fumarate accumulates upstream of FH blockade

3. Fumarate [metabolite:fumarate] --inhibits_activity_of--> αKG-dependent dioxygenase inhibition [process:akg_dioxygenase_inhibition] (w = 0.75, ev = review_or_consensus, cost = 0.388, pred_pen = 0.10)
    - mechanism: competitive inhibition of αKG-dependent dioxygenases by fumarate

4. αKG-dependent dioxygenase inhibition [process:akg_dioxygenase_inhibition] --causes--> TET/KDM demethylase inhibition [process:TET_KDM_inhibition] (w = 0.65, ev = review_or_consensus, cost = 0.431, pred_pen = 0.00)
    - mechanism: TET/KDM enzymes are αKG-dependent dioxygenases inhibited by fumarate

5. TET/KDM demethylase inhibition [process:TET_KDM_inhibition] --causes--> Global DNA hypermethylation [process:DNA_hypermethylation] (w = 0.70, ev = patient_omics, cost = 0.357, pred_pen = 0.00)
    - mechanism: impaired demethylation shifts epigenome toward hypermethylation

6. Global DNA hypermethylation [process:DNA_hypermethylation] --causes--> CpG island methylator phenotype (CIMP) [phenotype:CIMP] (w = 0.70, ev = patient_omics, cost = 0.357, pred_pen = 0.00)
    - mechanism: global hypermethylation manifests as CpG island methylator phenotype

7. CpG island methylator phenotype (CIMP) [phenotype:CIMP] --enables--> Genomic instability / chromosomal instability [process:genomic_instability] (w = 0.30, ev = hypothesis, cost = 2.004, pred_pen = 0.80)
    - mechanism: epigenetic silencing of repair programs may increase instability (placeholder)
    - notes: Placeholder until specific repair processes/genes are encoded.

8. Genomic instability / chromosomal instability [process:genomic_instability] --enables--> Cancer state [phenotype:cancer] (w = 0.40, ev = hypothesis, cost = 1.716, pred_pen = 0.80)
    - mechanism: genomic instability can accelerate acquisition of malignant capabilities
    - notes: Facilitator edge.
