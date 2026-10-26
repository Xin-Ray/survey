# Response to "IoTJ Survey Revision Review" (IoT_v2, 22 October 2026)

This revision is built on the 21 October manuscript, which is kept rather than reverted. Principle adopted: **one document, no supplement** (Section II-H). The supplement's tables are merged into the article. The search strings become Table II. The dataset table was a duplicate, so the main Table III is kept. The extended comparison is replaced by the full-precision Table V. Record-level material is released only as audit data files A01–A14 with a manifest.

Table numbers below refer to the revised manuscript:

- I: related reviews
- II: search strings
- III: datasets
- IV: decision matrix
- V: evidence, in two parts
- VI: 2026 sources
- VII: research agenda

## Required updates

**1. IoT evidence synthesis.** Done; see Section II-F, the C1–C7 block of Table V, the c cells of Fig. 5, and audit file A12.

- The 230 Xplore-only records and the 307 IoT-term additions were screened in two stages:
  - The 307 additions first went through item type and rules (i)–(iii); 68 passed.
  - Textual rules then kept records with device data (E1) and a system quantity (E2), leaving 37 + 21 candidates.
  - Each candidate's abstract was assessed with AI assistance, and its reason was recorded for author verification.
- Retained:
  - Six records with a health endpoint and a quantitative system figure, plus C7 from the update.
  - These are extracted from abstracts and kept outside the 22, preserving the focused-review scope.
- Excluded: 52 records, each with a reason. Most are non-health tasks or give no system figure.
- What the complement shows: latency and size reductions are reported for recurrent, distilled and state-space models. Only C7 names and measures its hardware: a 40 nm compute-in-memory chip, 5 µs and 100–150 µJ per beat. None reports a subject-level split or calibration.

**2. Audit package.** Done; see `audit/MANIFEST.md`.

- A01–A07 are the former extraction files S1–S7, renamed so that no file can be confused with a table.
- A08 is the crosswalk from E01–E22 and C1–C7 to the table rows.
- A09 is a record-level replay of the 11 September PubMed screen. It reproduces 1,435 of 1,436 records and 363 rule-positive records, 356 of which match the original pool. The original run kept only aggregate counts, so the residual differences are stated in the text.
- A10 gives the record-level Xplore decisions for 22 October, with insertion dates and duplicate and PubMed matches.
- A11 is the hand check.
- A12 is the complement screen.
- A13 is the search update.
- A14 holds the screening code, the expanded IoT query and the dated query logs.
- Conclusion-driving codes were rechecked against the sources:
  - spatial, IoT and validation codes for every Table V row;
  - eight comparator pairs against the publisher, PubMed or PMC text.
- Recheck caveat: the coding remains a single-reviewer coding with AI assistance, and this is stated in the text.

**3. Fig. 5 vs Section IV-E.** Reconciled.

- The text now states that explicit spatial modeling is shown by convolutional components, either alone or inside the recurrent hybrids that the recurrent row marks. It is also shown by one attention network over an fMRI grid (E13), by graph models and by the Bayesian reference, and never by a recurrent layer on its own.
- The caption explains overlapping hybrid assignments and lists the supporting studies for every D cell.
- The former "Latency" column is renamed "Device" (a latency or memory figure on the implied device), because E05 reports memory.

**4. Nitski.** Corrected against the PubMed abstract (checked 22 October).

- Table V:
  - Four deep models are compared with logistic regression, with the Transformer best (p < 0.0001).
  - AUROC is 0.804 at 1 year and 0.733 at 5 years.
  - The UHN cohort was evaluated only after fine-tuning (Val. "Abs.; A").
  - UQ is given as "99% CI".
- Table III flags the dataset descriptors not verifiable from the abstract (§).
- The text keeps the full protocol as uncertain and states that intervals on AUROC do not establish calibration.

**5. Screening and numerical reporting.**

- Fig. 1 and Section II-B now use the term "false-omission fraction among rule-negative records" (18%).
- 54 overlaps: they had been matched against the full PubMed snapshot rather than the eligible pool.
  - Re-identified on 22 October, 54 of 55 matched records are in the 363 pool.
  - One record fails rule (iii) on its PubMed abstract.
  - Section II-G therefore states 593 under PubMed's verdict and 594 if either database's verdict sufficed.
- Precision:
  - Table V prints each pair at source precision and computes the difference from it.
  - GluNet: 19.28 vs 21.54, giving −2.26.
  - Bed: 98.42% vs 92.16%, giving +6.26 points.
  - Lim, CiGNN, Liu EEG, Herath and TransformerJM were also updated from source tables.
  - Section V-F explains the rule.
  - There is no separate rounded table left to disagree.

**6. Citations and illustrations.**

- Target-trial emulation in VII-C and VII-D now cites Hernán and Robins (Am. J. Epidemiol. 2016).
- Fig. 3 is redrawn: (d) one gridded field shown at regular times, (e) ordered image frames.
- The distinction between calibration and intervals is kept in Table V notes, V-C, VII-D and Fig. 5.

**7. 2026 literature and novelty.** All seven sources were added and assessed, and none is added to the 22.

- Table I: Gao, Wimalasiri and Chen et al. are new rows, and Section I states what the IoT-aware framework adds relative to them.
- VI-A:
  - Briggs: a physics-informed twin, with in vivo, simulated and six-patient evidence; not prospective benefit.
  - Gao: closed-loop control is not equivalent to a twin or world model.
- VI-D and VIII: Jun & Ko, an event-driven AIoT twin; its costs come from simulation only.
- VII-B and Table VI:
  - EHRWorld and ChronoMedicalWorld are implemented retrospective models.
  - Their recorded-action forecasting is not identified treatment response; ChronoMedicalWorld says it does not adjust for confounding.
  - Wimalasiri contributes the on-policy effective planning horizon.
  - Chen et al. contribute the barriers they identify.
- Table VI separates implemented retrospective models, frameworks, simulation evidence, synchronized services and prospective benefit.
- Limitations: a new "Currency" paragraph.
- Search update (Section II-G, A13):
  - Both databases were re-searched on 22 October 2026, with online, Entrez and insertion dates logged.
  - PubMed: 50 new records, 9 rule-positive.
  - Xplore: 44 newly inserted records, 12 rule-positive.
  - The added record (C7) and the exclusions are documented.

**8. Presentation and consistency.**

- Fig. 2: five decision diamonds, each with its alternative branch.
- Stable IDs E01–E22 and C1–C7 are shared by Tables III and V and by the A08 crosswalk. Since the supplement is gone, there is no main-to-supplement mapping left to maintain.
- Hardware is stated as Raspberry Pi 4B, 97.93 ms everywhere.
- Repeated qualifications are consolidated into five reporting principles (II-H), and the deployment, validation, synchronization, intervention and threat subsections are condensed.

## Verification

- Page count and build: 25 pages including references, with 0 errors, 0 overfull boxes and 0 undefined references.
- Checkers:
  - `check_revision.py`: 59/59
  - `check_comments`: 50/50
  - J28: 5/5
  - Oct1: 9/9
  - Supplement-content checks: all passed
- Strict reference check: 114 cited, 0 discrepancies (one documented Crossref quirk).

## Items for the authors

- Verify the AI-assisted complement and update decisions (A12, A13) and the three new Table I codings (A01).
- Confirm deletion of `SUPPLEMENT_final.tex` on Overleaf; Overleaf keeps it in project history.
- Decide where the audit package will be hosted (for example Zenodo or GitHub), and add the link to the manuscript.
