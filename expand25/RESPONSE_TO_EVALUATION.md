# Response to the IEEE IoT-J Survey Manuscript Evaluation (15 October 2026)

Revision of 16 October 2026 (`expand25/STmodel.tex`).

Section, table and figure numbers refer to the revised PDF. That PDF has 20 pages including references (the limit is 25). The main text has 10 tables (previously 20) and 7 figures, 3 of them new flagship figures.

## Decisions taken with the authors before revising

| Question | Decision |
|---|---|
| Where should the detailed tables go? | Consolidate in one document, with no supplement. The per-study cells are released as seven CSV extraction records (`extraction/S1–S7`). |
| Page budget | The main text stays within 25 pages including references. It now runs to 20. |
| Selection issue (P1) | Keep the 22 studies and frame them strictly as an illustrative, focused synthesis. Do not add studies from the IEEE Xplore-only pool. |
| Title | Adopt the title the evaluation suggests. |

## 3. Major issues

| Issue | What was done | Where |
|---|---|---|
| **P1 Selection and representativeness** | <ul><li>Framing: the 593 rule-eligible records are described as a *map* of the literature and the 22 studies as a *focused critical synthesis*, and no prevalence statement transfers between them.</li><li>The provenance of the 22 is stated, as is the fact that the IEEE Xplore-only pool contributed none.</li><li>Per-study selection reasons and extraction records are released as CSV files.</li><li>A new IoT-term sensitivity check found that the health-term query misses 307 IoT-term records (26%).</li><li>The Limitations section now explains the effect of excluding the Xplore-only records on what can be inferred.</li></ul> | II-D, II-E, IX; `extraction/S2` |
| **P1 Novelty beyond breadth** | <ul><li>New Fig. 2 is a sensing → link/gateway → edge → cloud → synchronized twin → clinician architecture. Each stage carries the data leaving it, model families, resource limits, its validation gate, and the evidence among the 22 studies.</li><li>New Table V is a use-case decision matrix covering cadence, spatial structure, link and placement, candidate families, required verification, and the supporting studies.</li><li>The Introduction now states three contributions.</li></ul> | I, Fig. 2, Table V, IV-F |
| **P1 Comparative performance evidence** | <ul><li>Table VI now integrates headline result, best in-study comparator and difference, validation level, uncertainty and subgroups, and resource figure.</li><li>Comparator values were re-extracted from the full texts. "n/r" is kept separate from unfavorable results (marked ‡), and numbers are compared only within a study and task.</li><li>V-B synthesizes the results by task. Under subject-disjoint splits the margins are at most 0.05 AUC or F1, 2.9 accuracy points or 0.8 mmHg. The largest margins (6.3 points; 0.19 R²) come from record-level splits. Six studies trail an in-study comparator.</li></ul> | Table VI, V-A–V-C |
| **P2 IoT systems grounding** | <ul><li>Every study is coded IoT-native (11), IoT-adaptable (3) or record-based (8).</li><li>Device readiness is never inferred from architecture: a study counts as on-device only where it measured that.</li><li>Placements in Fig. 2 and Table V are labelled as the authors' reading.</li><li>The communication claims are qualified: Table VII and VI-D.</li></ul> | III-C, Tables V–VII |
| **P2 Conceptual status of world models** | <ul><li>New VII-B, "Prediction, Simulation and Causal Identification", separates prediction, simulation, counterfactual identification and decision support.</li><li>It covers confounding by indication, positivity and action coverage, off-policy extrapolation, and prospective safety.</li><li>States that "an action argument … does not make the simulated effect causal."</li><li>New Fig. 7 gives the evidence stages and marks the unsupported transitions.</li></ul> | VII-B, VII-E, Fig. 7, IV-B |

## 4. Section-by-section changes

| Section | Change |
|---|---|
| I | Opens with the unresolved IoT design gap, then the four research questions, three contributions and a roadmap. The generic motivation is cut. |
| II | The search arithmetic is shown inline (1,206 − 99 − 127 − 617 = 363; 1,161 → 289 → 284; 363 + 230 = 593). The extraction and selection records are released. The IoT-term sensitivity count is added. |
| III | <ul><li>New III-B separates geographic, administrative, anatomical/image, relational-sensor, multichannel and temporal-only inputs (11 of 22 model explicit spatial structure; none uses geographic coordinates).</li><li>New III-C covers IoT status and how acquisition drives irregularity and missingness.</li><li>The four dataset tables are merged into Table III, with a spatial-structure column and a device/multisite/twin "fit" column.</li></ul> |
| IV | <ul><li>New IV-E covers assumptions, costs and evidence, with the heatmap in Fig. 5 (D demonstrated / T theoretical / U untested).</li><li>New IV-F covers going from acquisition conditions to model choice (Table V).</li><li>The model-comparison table is replaced by Fig. 5.</li></ul> |
| V | <ul><li>Validation is now graded in levels (subject-disjoint, population time hold-out, within-subject later period, record-level, not stated, none; adapted second cohorts flagged).</li><li>Comparisons are made within each study.</li><li>Calibration, intervals and subgroups are reported separately.</li><li>The integrated Brier score is no longer called calibration.</li></ul> |
| VI | New VI-B gives operational requirements: patient specificity, synchronization, fusion, updating, feedback and validation, each with how it would be demonstrated. |
| VII | Marked throughout as a conceptual framework. Adds causal identification (VII-B) and evidence stages (VII-E, Fig. 7). In Table VIII, readiness numbers are replaced by evidence phases with a stated rubric. |
| VIII | The agenda is prioritized: priority 1 (G1, G7, G2), priority 2 (G4, G3, G6), priority 3 (G5, G8). Each item is a measurable question. |
| IX | Adds the exclusion of Xplore-only and IoT-term records and the likely direction of that bias. |
| X | Recast as design lessons and evidence boundaries, answering each research question. |

## 5. Specific technical checks

| Check | Response |
|---|---|
| Definition of spatiotemporal learning | Studies are coded Geo/Adm/Anat/Rel/MC/T (III-B). Temporal-only longitudinal evidence is labelled as such (V-F). |
| External validation and leakage | Validation is graded in levels. The 4 record-level splits (segment, scan, sample, repetition) are flagged with leakage risk. 8 second cohorts/sites, all adapted; none untouched (V-A, Table VI). |
| Calibration | Discrimination, calibration, intervals and subgroups are reported separately. The integrated Brier score is described as not establishing calibration on its own (V-C). |
| Technology readiness ratings | TRL ranges are removed. They are replaced by qualitative evidence phases (Conceptual / Benchmark / Prototype / Retrospective) with an explicit rubric that describes the cited work, not whole model classes (Table VIII). |
| Communication claims | <ul><li>5G: "1 ms 5G radio target; end-to-end delay is higher".</li><li>Wi-Fi: nominal rates, shared in a cell, with contention delay.</li><li>MQTT: a retained message gives only the last value, so recovery needs a persistent session or a device buffer.</li><li>Layer-specific assumptions are stated in the caption and in VI-D.</li></ul> |
| Causal claims | VII-B covers confounding, identifiability (positivity, no unmeasured confounding) and off-policy extrapolation. Eq. (2) is followed by an explicit caveat. |

## 6. Figures and tables

| Recommendation | Response |
|---|---|
| Flagship Fig. 2: sensor → gateway → edge/cloud → twin → clinician, with model families, resource limits and validation gates | Done (new Fig. 2, vector). |
| Heatmap of model families × spatial modeling, irregular sampling, robustness, latency, external validation, uncertainty and deployment, marked demonstrated / theoretical / untested | Done (Fig. 5). |
| Maturity graphic: offline → individually updated → externally validated twin → intervention simulation → prospective, with unsupported transitions marked | Done (Fig. 7), with counts from the 22 studies. |
| Move detailed datasets and quality coding out of the main text; keep the central synthesis | Done without a supplement: the details are consolidated into Tables III and VI and the full cells released as CSV records. Tables went from 20 to 10. |

## 7. Title, abstract and contributions

<ul><li>Title: adopted as suggested.</li><li>Abstract: 249 words. It opens with the gap, states three contributions, reports three qualified findings, and ends with model-selection and validation insights. World models are presented as conceptual.</li><li>The three contributions follow the evaluation's wording: IoT-aware taxonomy, evidence-grounded comparative assessment, and twin development and evaluation framework.</li></ul>

## 8. Priority checklist

| Priority | Item | Status |
|---|---|---|
| Essential | Qualify study-selection coverage | Done (II-D, II-E, IX). No studies were added, per the authors' decision. |
| Essential | Clarify novelty against adjacent surveys | Done (I, Table I, Fig. 2, Table V). |
| Essential | Comparative analysis built on within-study evidence | Done (Table VI, V-B). |
| High | Spatial structure vs longitudinal-only data | Done (III-B, Table VI). |
| High | Separate twin implementation from world-model proposals | Done (VI-B, VII, Fig. 7). |
| High | Revise strong system and readiness claims | Done (Table VII qualified; TRL removed). |
| High | Redesign the main taxonomy and evidence visualization | Done (Figs. 2, 5, 7). |
| Medium | Reduce table density | Done (20 → 10 tables). |
| Medium | Sharpen the abstract and conclusions | Done. |
| Final QC | Search counts, references, IEEE formatting, disclosure | All acceptance checks pass. Strict reference check: 102 cited, 0 discrepancies. The AI disclosure is updated. |

## Corrections found while re-extracting the full texts

These were wrong in the earlier version and are now fixed in the paper and in the released records:
- **Hussein et al.:** the study uses CHB-MIT (leave-one-subject-out) and the Kaggle AES and Melbourne sets. It does not use Freiburg, and its CHB-MIT split is subject-level, not clip-level.
- **Liu et al. (sleep posture):** the split is sample-level, not "not stated".
- **Kong et al.:** the folds are effectively subject-level, because there is one scan per subject.
- **Verbiest et al.:** the reference system is OptoGait, not GAITRite.
- **CiGNN:** the reported 3.2/1.9 mmHg is from the internal set only; the pooled result is 3.77/2.52.
- **TransformerJM** trails MATCH-net on iAUC. It is now marked unfavorable.

The resulting validation counts are 13 subject-disjoint / 1 population time / 2 within-subject later period / 4 record-level / 1 not stated / 1 none.

## Open items for the authors

1. **Verify the comparator values.** The values in Table VI were retrieved from the full texts with AI assistance and are disclosed as such. The authors should confirm them before submission. Nitski et al. could be checked only against its abstract.
2. **Decide where to host the extraction records.** Options include IEEE DataPort, a public GitHub repository, or supplementary data files at submission. The text states that they accompany the article.
3. **Fix Fig. 3 (the authors' image).** Its labels print at about 4–6 pt, and its "Raster" and "Video" panels appear swapped relative to the definitions in III-A.
