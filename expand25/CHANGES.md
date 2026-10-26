# expand25: change log, 8 pages → 25 pages (2026-10-12)

**Base:** the 8-page submission build of `live/STmodel.tex` plus `live/supplement.tex`. Both were confirmed byte-for-byte identical to the Overleaf folder `version2.1-shrink8 IOT` before work began. That folder and `live/` were not modified.

**Result:** `STmodel.tex`, **25 pages including references**. 0 errors, 0 undefined references, 0 overfull boxes. 103 references, 15 tables, 2 figures, 1 algorithm. Abstract: 233 words. It is a single document: the `\ifsubmission` switch is removed, the supplement is merged into the body, and the text no longer points to a separate supplement anywhere.

## Section by section: where each change came from

| Section | Change | Source |
|---|---|---|
| Abstract | Adds datasets, the ten quality fields, communication, and the threat map. "modelled" changed to US spelling | Rewritten; still 150–250 words |
| I Introduction | Restored the motivation material (the shift from static risk to dynamic modeling; spatial context). Added an explicit contributions paragraph, an IoT-venue fit paragraph and a roadmap | Extended branch, rewritten |
| I Introduction | **Table II** gives the section-level evidence for every mark in Table I. A paragraph explains the marks that moved after full-text reading | Supplement S0 + §IV |
| II Methodology | Split into subsections: search strings, eligibility and the PubMed screen, IEEE Xplore screening, selection of the synthesized studies, and citation chasing. Paste-ready verbatim strings for both databases. All three PubMed runs. Review exclusion and matching rules. **Table III** gives provenance and the reason each study was included. The full-text access note is included | Supplement §II, §III, S8, S9, §X |
| II Methodology | Fig. 1 (PRISMA) caption now gives the exclusion reasons at the screening stage | New |
| III Data | Subsections: five data types and where each enters the pipeline; relational structure; overlap coding; sparsity, irregularity and multi-scale structure; data quality and harmonization; datasets | Extended branch, rewritten |
| III Data | **Tables IV and V**: all 23 datasets in two parts (the two former panels per part merged into one table each, with group header rows) | Supplement S2a/b + S4a/b |
| IV Methods | Historical development. **Table VI** is the notation table (new). Foundational architectures with equations. The four model families. **Table VII** compares nine families (new IoT-tier column; also fixes the `\noalign` compile error in the extended branch). Irregular-time and longitudinal methods. **Algorithm 1** gives training and synchronized inference (new) | Extended branch + new material |
| V Evidence | Section labeled as a review of implemented systems. Five subsections by task group cover all 22 studies; the 10 sampled studies are described from table data only. Cross-domain patterns. Quality of the evidence. Longitudinal evidence | Extended branch rewritten + new |
| V Evidence | **Table VIII** (the original Table II, unchanged; footnote abbreviations expanded). **Tables XI and XII**: quality assessment of all 22 studies | Original + supplement S3a/b + S5a/b |
| VI Digital twins | Evidence status stated. Subsections: twins in digital health; data collection and fusion and its limits; human factors; communication and interoperability; per-study deployment reporting; privacy and federated learning; visualization | Extended branch rewritten |
| VI Digital twins | **Table IX**: per-study system and privacy reporting, including the "Inference placement (ours)" column. **Table X**: communication options | Supplement S7, S6 |
| VII World models | Labeled a "proposed framework". Subsections: distinguishing the adjacent concepts; simulation and planning; attack surface; verification, validation and uncertainty. **Table XIII**: necessary and optional components. **Table XIV**: threats and protections by IoT layer | Extended branch + supplement S1 |
| VIII Future | Gap-driven agenda numbered G1–G8. **Table XV** merges the two former agenda tables into one. Networking directions; data sharing | Extended branch, rewritten |
| IX Limitations | Split into five topics. Removed a stale extended-branch claim that counts had not been recorded at each stage | Extended branch, corrected |
| X Conclusion | Answers RQ1–RQ4 one by one, adding no new claims. RQ2 no longer says "generally reported gains"; it now reads "in the twenty-two studies summarized here, … reported gains over their stated baselines" | Rewritten |
| Acknowledgment | AI-use disclosure updated to cover this round of merging, restoring and editing | Updated |

## What was deliberately left out, and why

- **Xie & Yao [7]:** the supplement had already dropped it because no full text could be obtained, so every `\cite{7}` that appeared in the extended branch was removed.
- **Extended-branch Table I** (8 old reviews) and the evidence-b / iot-placement / datasets tables: superseded by the newer 12-review Table I and by supplement S2–S7, so they were not restored.
- **The sentence "the nine misses fail…":** removed. It listed only 5 + 2 + 1 = 8 records, which did not reconcile with nine. It was never in the 8-page version.
- **Seven figures**, removed to fit 25 pages: five images (the DT concept figure, the five data categories, the foundational architectures, and both FL figures) and two TikZ figures (the reference architecture and the dependency graph). The concepts are kept in text or tables.
- **About 30 peripheral references from the extended branch:** not restored. The 22 that were restored all passed verification.

## Data consistency

- All numbers are unchanged: 1,436 / 1,206 / 363 / ≈375 / 593 / 284 / 230 / 22 = 12 + 10 / 3,472 / 15.
- The supplement's quality paragraph said "sixteen of twenty-two split at the subject level", which contradicted the main text's "fourteen … four … three … one". The merged text keeps the main-text figures, which `check_consistency` verifies against `quality_counts.json`.

## Verification (`expand25/review/`)

The checkers were ported by `port_checkers.py`. Only paths and supplement-specific lookups changed; **no threshold was relaxed**. On Windows they must be run with `PYTHONUTF8=1`, because the scripts were written for macOS and assume UTF-8.

| Check | Result |
|---|---|
| `check_comments.py` (09-21 round) | 50/50 |
| `check_j28.py` (09-28 round) | 5/5 |
| `check_oct1.py` (10-01 round) | **8/9**. O7 not satisfied, see below |
| `check_consistency.py` | 45/45. Adds: every former supplement table is in the body and referenced; no pointer to a separate supplement survives |
| `check_supplement.py` | All pass |
| `strict_refcheck.py` | 103 cited, **0 discrepancies**, 7 not compared, each with a reason (the 4 from before + lecun2022jepa, mqtt5standard, ISO2013TRL) |

**Bibliography corrections** (all from publisher records):
- `yu2018spatio` was misattributed to IEEE T-ITS; it is IJCAI 2018, pp. 3634–3640.
- `cho2014gru` changed from arXiv to EMNLP 2014.
- `ha2018worldmodels` gains NeurIPS vol. 31, pp. 2450–2462.
- `ISO2013TRL`: title corrected, and the BSI DOI removed.
- The preprint DOI that the tool added to `Faruqui2024` was undone.
- 7 venue names abbreviated in IEEE style.
- 20 fields backfilled by `ieee_style.py`.

## The one known deviation (needs your decision)

**O7 (10-01 round, table readability):** that round raised the supplement's table bodies one size, from `\scriptsize` to `\footnotesize`. Inside a 25-page limit, the merged tables are back at `\scriptsize` (7 pt), the same size Table II already used in the approved 8-page version. At `\footnotesize` the merged tables come to about 27 pages.

---

# Final round (2026-10-13): formatting checklist, consistency, figures, clean-up

**Result:** still **25 pages** (references included), 0 errors, 0 undefined, 0 overfull boxes. Now 15 tables, **5 figures**, 1 algorithm, 103 references.

## Formatting checklist, compiled from the GitHub commits, Nobel's 09-15 Overleaf review, the r3 revision list, the 09-21/09-28/10-01 rounds and the requests in this round

| # | Item | Source | Status |
|---|---|---|---|
| F1 | Gray stripes and gray group blocks replaced by rules: three-line booktabs, with a `\midrule` between groups | This round (supersedes commit a773d35) | Done; `rowcolor` = 0, and the `xcolor[table]` option is removed |
| F2 | Table III was a half-empty single column (p.5) | This round | Now full width (`table*`) with three columns (Study / Provenance / Reason), one line per row; it shares the page with text and Figs. 2–3 |
| F3 | Sparse float pages (the original p.13 Table IX, p.10 Table V) | This round; 10-01 O7 | `\(dbl)floatpagefraction` raised from 0.6 to 0.88, so a table goes to the top of a page with text beneath. Rendered page by page: every float page is now ≥ ~85% full |
| F4 | Figure text ≥ 8 pt | 09-21 #10; r3-o | New TikZ figures use `\footnotesize`; arch2 at 0.8 text width |
| F5 | Abbreviations defined at first use | r3-m | EHR, CI, DOI, FHIR/HL7, RAM, GCN/GAT, LSTM/GRU, ECG/EEG, CNN/RNN, ODE, DNN, non-IID, MRI, CPU, AUC and PPG are now spelled out at first use |
| F6 | Author names followed directly by `\cite` | Nobel #18 | Kyritsis et al., Jain and Wallace, Serrano and Smith, Wiegreffe and Pinter fixed |
| F7 | Run-in italic labels (option C1-c: kept only for parallel enumerations) | Nobel #22/#23 | 7 removed, including two that repeated their subsection titles |
| F8 | Artificial-sounding words ("substrate", "roll forward") and overuse of "claim" | Nobel #2/#26 | 0 left; subsection retitled "Communication Options and Interoperability" |
| F9 | US spelling, hyphenation, healthcare | r3-l | 0 hits |
| F10 | "Fig." in running text, "Figure" at sentence start | IEEE style | Done throughout |
| F11 | Captions short; abbreviation keys in table notes | Nobel #19; Julia 07-14 | Merged tables carry their keys in the notes |
| F12 | Reference author rule: up to 6 authors listed in full, more than 6 → first author + *et al.* | IEEE Reference Guide | 40 entries corrected from publisher records (Crossref, arXiv or DBLP); 8 by hand from the proceedings. strict_refcheck: 0 discrepancies |
| F13 | Section pointers in Fig. 2 and every `\ref` resolve | r3-c/d | Done |
| F14 | Table VIII (formerly Table II) ≤ 5 columns, cells ≤ 52 characters | 10-01 O6 | Kept |
| F15 | No overfull boxes, no "Float too large" | Commit history | 0 |

## Consistency (contradictory statements removed)

- **"Three of those four *measured* on a phone, a microcontroller or a portable board"**: Table IX shows that the microcontroller study's latency is a toolchain estimate and only its memory footprint was measured. Changed to "obtained on the class of device the work implies…", with that caveat stated. Section VI and the GluNet sentence were made to match.
- **The count of studies with no split or an unstated split level**: Section III said three, counted from Table VIII; the quality paragraph said "three not stated + one with no hold-out". Both now come from the quality assessment: **four** (Li 2016 with no split; Kong, Liu 2025 and Zhu with the level not stated), with each study cited. Kong's quality row no longer contradicts itself ("Low at subject level" → "Low if folds are formed by subject, which is not stated").
- **"published between 2014 and 2026"**: the domain studies date from 2016 to 2026, so the text now says 2016.
- **"together they exercise all five categories and every model family"**: the set contains no GAN, DDPM, Mamba or world-model study. Changed to "cover the main spatiotemporal families (convolutional–recurrent, graph, attention-based and 3D-convolutional)".
- **"The closest the set comes to a validated twin"**: Silfvergren is not among the 22 studies. Changed to "Among the twin work cited here".
- A stray ",." punctuation mark was removed.
- **Ported checkers:** the patterns for the reworded sentences were updated (in `review/port_checkers.py`, with the reason stated). The assertions are unchanged.

## Figures (reused from version2.0-modified)

| Figure | Treatment |
|---|---|
| Fig. 3: five data types | Redrawn in TikZ. The original misspelled "Covide 19", and its Raster panel was drawn as scattered points while the Video panel was drawn as a grid. Now: event (points labeled with type and day), trajectory (path $t_1$…$t_4$), point reference (sensors over a field), raster (grid), video (stack of frames) |
| Fig. 4: foundational architectures (`figures/arch2.png`) | Reused unchanged; it matches equation (4) |
| Fig. 5: federated learning cycle | Redrawn in TikZ from the original Fig5: server/aggregator ↔ N sites, four numbered steps. The caption keeps "updates are protected only if secure aggregation / encryption / DP is added" |
| Frame 34, Fig6 | Not used: Frame 34 is textbook background and misspells "Attention" 4 times; Fig6 shows one specific prototype's pipeline |

## Clean-up (no draft or template content)

Removed: the commented-out figure block, the ACM template comments (the "Institute for Clarity in Documentation" address placeholder, the keyword instructions, the "End of file sample-acmcp.tex" trailer), the change-tracking macros `\cadd`/`\cdel` and `ulem`, the `\Description` shim and all its calls, `makecell`, and the TikZ comments. A search for TODO/TBD/XXX/??/placeholder/draft returns 0.

## Checks

check_comments 50/50 · check_j28 5/5 · check_consistency 45/45 · check_supplement all pass · check_oct1 8/9 (O7, `\scriptsize`, accepted by the user to keep 25 pages) · strict_refcheck 103 cited, 0 discrepancies.

**Still needs verification against the source:** whether Kong et al. 2021 [4] formed its ten folds by subject. If the original paper states that it did, Kong should be reclassified as "whole subjects held out", and the counts become 15/4/2/1 with "three" in place of "four".

---

# Typography round (2026-10-14)

- **One font family in the body.** The four verbatim search-string blocks are now set in the body font (`\footnotesize`, ragged right, hyphenation suppressed so the strings stay paste-ready; the characters are unchanged). The six `\texttt{}` uses (esearch, `[tiab]`, `2015:2026[dp]`, field names) are removed. All 139 `\textbf` (prose, figure labels, table headers and bodies, the PRISMA boxes) and every `\bfseries` are removed; table headers are in plain text, as in IEEE's own template. Italics are kept for run-in labels, group headers and emphasis.
- **Rules between rows** (`\rowrule`, 0.3 pt, 158 rules) in Tables II, IV, V, VII, VIII, IX, X, XI, XII, XIV and XV. Table XII is included so that it matches its part 1, Table XI.
- **Space:** the rules added about 0.15 page. To recover it, two passages that repeated other material were shortened: the interoperability sentence in §VI-C (the note to Table X carries it) and the details of the two compared reviews that lack a citation graph (§II-E). Still 25 pages.
- **Checkers:** three ported patterns now match the bold-free text (the `Comparators` and `Calibration; uncertainty` header cells, and "surfacing 15 eligible ones"). The assertions are unchanged. Results: 50/50, 5/5, 45/45, supplement pass, oct1 8/9 (O7 accepted), strict refcheck 0 discrepancies.
- **Mock review:** `IoTJ_review_form.md` contains a mock IoT-J review (Major Revision, with five major comments) and a checklist of the smallest changes that would answer each one.

---

# Size, grid and reference-column round (2026-10-14)

- **One size for everything outside the body text.** Every table, table note, figure label and the four search-string blocks are 8 pt (`\footnotesize`); the body stays at 10 pt. All `\tiny`, `\scriptsize`, `\small` and the 6.2 pt `\fontsize` are removed.
- **Dataset and quality tables split again by provenance.** Datasets: Tables IV–V cover the twelve studies assembled while drafting, and Tables VI–VII the ten sampled from the 363. Quality: Tables XIII–XIV and XV–XVI. Each part is referenced from the text by its own number.
- **Full grid on every table.** Vertical rules and `\hline` throughout, and a rule under every group-header row (e.g. the task groups of Table X). Row spacing `\arraystretch` 1.22; column gap 3 pt (was 2–2.5 pt). Booktabs is no longer used for rules, because its padding breaks vertical lines.
- **"Ref." column.** In 15 tables (I, II, III, IV–VII, X, XI, XII, XIII–XVI and XVIII), each row's citations are moved out of the cells into a final "Ref." column. A row with no source shows "--".
- **Notation table:** the symbol column is widened to 2.3 cm, so $X_t\in\mathbb{R}^{H\times W\times C}$ no longer overlaps the meaning column.
- **Page budget.** The changes above took the paper to 29 pages. It is back to exactly 25 pages, references included, after condensing the body prose from 10,569 to about 7,600 words:
  - §I: contributions and roadmap tightened.
  - §II: the two screening descriptions de-duplicated, and the search-run and citation-chasing paragraphs shortened.
  - §III: shortened.
  - §IV-B: textbook detail reduced. The attention and state-space equations are now described in words, so the remaining equations are (1) GNN and (2) world model, both cited by `\eqref`. The unused notation rows were removed.
  - §V–§IX: repeated counts and restated table content removed.

  A script compared the old and new prose: every distinct number, every citation key and every label in the previous text is still present. Only repeated mentions were removed, and every table is unchanged in content. Float separation was also reduced to 12 pt (text–float) and 10 pt (float–float).
- **Cross-references.** One caption was reworded from "the twelve studies of Table X that were assembled while drafting" to "the twelve studies assembled while drafting", because the consistency checker forbids any wording that suggests Table X holds twelve studies.
- **Checkers.** In `review/port_checkers.py`:
  - The file readers are wrapped in `_grid_view()`. It restores the booktabs form the parsers expect: `\toprule`/`\midrule`/`\bottomrule`, no vertical rules, and the citation back in the row's first cell. No cell text changes.
  - Column limits such as Table II's "at most five" therefore count content columns, not the reference column the authors asked for.
  - The merged-table adaptations of the earlier round were reverted, since the tables are split again, and S4a/S4b/S5a/S5b were added to the list of former supplement tables.

  Results: check_comments 50/50 · check_j28 5/5 · check_consistency 45/45 · check_supplement all pass · check_oct1 **9/9** (O7 now passes, as no `\scriptsize` remains) · strict_refcheck 103 cited, 0 discrepancies. The bib is unchanged since that run.
- **Build:** 25 pages, 0 errors, 0 undefined references, 0 overfull boxes, no "Float too large".
- **Table captions:** IEEEtran sets table captions in small caps, which have no italic, so the eight `\emph` in table captions were replaced by quotation marks (Full, n/r, Inference placement) or by plain text. This removes the only font warning in the log.

---

# Row rules, search-string table and Fig. 3 (2026-10-14, later)

- **Rules between rows** were added to the four tables that had none: related surveys (Table I), provenance (now Table IV), notation (now Table IX) and the concept components (now Table XVIII). Every table now has a rule after every row.
- **Search strings are now a table.** The four strings were previously set as separate 8 pt blocks inside the text, using raw TeX (`\begingroup … \hyphenpenalty=10000 …`).
  - They are now Table III, a grid table in the same style as the others, with two columns: "Database, arm" and "Search string".
  - The strings are unchanged character for character.
  - The no-hyphenation rule that keeps them paste-ready now lives in one documented column type in the preamble (`\newcolumntype{S}`), so the body contains no raw TeX.
  - The text refers to "Table III". The record counts stay in the text.
  - Because Table III is new, every later table number has shifted up by one.
- **Fig. 3** is now the authors' image `figures/fig3.png` (uploaded to Overleaf), at column width, in place of the TikZ drawing. The caption is unchanged.
- **Space:** the §IV-C model-families paragraph was tightened by about 40 words. Every citation and the attention-cost figures are kept. Still 25 pages.
- **Checks:** check_comments 50/50 · check_j28 5/5 · check_consistency 45/45 · check_supplement all pass · check_oct1 9/9.
---

# Fig. 4 as a vector graphic (2026-10-15)

- **Fig. 4 (five foundational architectures)** was redrawn as an SVG (`figures/fig4_arch.svg`, the editable source) to replace the raster `arch2.png` (1448×1086 px, which blurred when printed). It was converted to a vector PDF for pdflatex (`figures/fig4_arch.pdf`, printed from the SVG with headless Chrome).
  - The figure is drawn at its printed size: 181 mm × 113 mm, at `\textwidth`.
  - All text is set in Times New Roman, the same family as the paper, and is real text rather than pixels. Labels are 8 pt and panel titles 9 pt, with no bold.
  - The PDF contains no raster images, and its fonts are embedded.
- **Content is the same as arch2**, with three corrections:
  - **Panel letters:** the five panels are now labeled (a)–(e), and the caption refers to them.
  - **Notation:** the world-model panel now uses the symbols of equation (2) and the notation table. The predictor is $P_\phi$ (the PNG had $f_\psi$), and the action $a_t$ enters the predictor directly, as in (2) (the PNG had a separate action encoder $A_\phi$). The loss is written $L=\|\hat z_{t+1}-z_{t+1}\|^2$, and the target encoder is $E_{\bar\theta}$.
  - **Diffusion reverse chain:** the PNG placed $x_t$ between $p_\theta(x_0|x_1)$ and $p_\theta(x_{t-1}|x_t)$. The chain now reads $x_T\to x_{T-1}\to\dots\to x_1\to x_0$, with $p_\theta(x_{T-1}|x_T)$ and $p_\theta(x_0|x_1)$ on its arrows.
- The caption was updated for (a)–(e) and for the world-model wording ("predicts the next latent state from it and an action").
- `figures/arch2.png` is kept but no longer used. The paper still has 25 pages, and the PDF shrank from 1.49 MB to 0.47 MB. Checks: 50/50 · 5/5 · 45/45 · supplement pass · oct1 9/9.
---

# Major revision after the IoT-J manuscript evaluation (2026-10-16)

`RESPONSE_TO_EVALUATION.md` maps each recommendation to the change and where it is.

**Decisions (taken with the authors):**
- Consolidate in one document; no supplement.
- The main text stays within 25 pages; the result is 20 pages including references.
- Keep the 22 studies, framed as an illustrative synthesis.
- Adopt the suggested title.

**Structure:**
- The main text has 10 tables, down from 20. The four dataset tables became Table III. Provenance, the four quality tables, and deployment reporting became the integrated Table VI. The model-comparison table became Fig. 5. The survey-evidence table moved to the records.
- **New vector figures:**
  - Fig. 2: sensing-to-decision architecture, which replaces the TikZ taxonomy.
  - Fig. 5: model-family evidence heatmap.
  - Fig. 7: maturity pathway.
  - Their sources are in `review/figure_sources/` (SVG drawn at print size, then printed to PDF by headless Chrome).
- **New tables:** Table V, use-case decision matrix; Table X, the agenda, rewritten with priorities.
- **New subsections:**
  - II-E: search-term sensitivity, with PubMed counts of 16 Oct 2026 (1,194 → 1,501, +307).
  - III-B: what counts as spatial modeling.
  - III-C: IoT status, irregularity and missingness.
  - IV-E: assumptions, costs and evidence.
  - IV-F: from acquisition to model choice.
  - V-A: validation levels and leakage.
  - V-B: within-study comparisons.
  - V-C: uncertainty, calibration and subgroups.
  - VI-B: operational twin requirements.
  - VII-B: prediction, simulation and causal identification.
  - VII-E: evidence stages.
- **Released records:** `extraction/S1–S7` (CSV) hold every cell of the removed tables, corrected as below. The S6 comparator column now carries the re-extracted comparator values.

**Corrections from the full-text re-extraction:**
- Hussein et al.: datasets are CHB-MIT, Kaggle AES and Melbourne, not Freiburg; the CHB-MIT split is leave-one-subject-out.
- Liu et al. (sleep): sample-level split.
- Kong et al.: subject-level, one scan per subject.
- Verbiest et al.: OptoGait reference.
- CiGNN: the figure given is internal-set MAD.
- TransformerJM: below MATCH-net on iAUC.

Resulting validation counts: 13 S / 1 P / 2 W / 4 R / 1 ? / 1 none, and 8 second cohorts or sites, all adapted.

**Claims revised:**
- The integrated Brier score is no longer described as calibration.
- TRL ranges are replaced by evidence phases.
- The 5G, Wi-Fi and MQTT statements in Table VII are qualified.
- The world-model action argument is explicitly not causal.

**References:** 102 cited. ISO 16290 was dropped together with the TRL ratings. Strict check: 0 discrepancies.

**Checkers:**
- New `review/check_revision.py` (50/50) verifies every count in the abstract, prose and figures against Tables III and VI and the records, plus the search arithmetic and cross-references. It replaces the ported `check_consistency.py` (retired as `check_consistency.retired.py`).
- Ported checkers read the released records through `_records_view()`.
- Two earlier column limits on Table II (J28-4: at most 6; O6: at most 5 columns and cells of at most 52 characters) are **superseded**, with the reason stated in `port_checkers.py`. The integrated table is held to at most 10 content columns.
- Results: check_comments 50/50 · check_j28 5/5 · check_supplement all pass · check_oct1 9/9 · check_revision 50/50.

**AI disclosure:** updated to cover the restructuring, the figures, and the AI-assisted retrieval of comparator values. The authors still need to verify those values.

# IoT_v2 revision round (2026-10-22): no supplement, merged tables, IoT complement, 2026 literature

Base: the Overleaf `STmodel.tex` of 2026-10-21 (OpenAI Codex edits), kept as the authors decided, not reverted. The pre-round copy is preserved as `STmodel_before_final_audit_20261021.tex` on Overleaf; the 21 October text is reproduced byte-for-byte in the scratch record (SHA-256 prefix `ca904296de64b822`).

## Principle: one document, no supplement
- Stated in the manuscript as the first reporting principle (Section II-H, `sec:scopeaudit`): every table and figure is in the article; record-level detail is released only as audit data files A01–A14, which add no result the article does not state.
- `SUPPLEMENT_final.tex` is no longer used. Its three tables were merged:
  - S1 search strings → new main-text Table II (`tab:strings`), exact strings, plus the IoT-term variant.
  - S2 datasets duplicated `tab:datasets` (same label); the main Table III is kept, with stable IDs and the Nitski flag.
  - S3 extended comparison duplicated `tab:evidence` with rounded pairs; it is replaced by full-precision pairs in Table V.
- All "Supplementary Table/package" wording removed; checker `check_revision.py` asserts it.

## IoT_v2 items
1. **IoT evidence.** The 230 Xplore-only records and the 307 IoT-term additions were screened (Section II-F): item type and rules (i)–(iii) for the PubMed additions (68 of 307 pass), textual E1 device and E2 system-quantity rules (37 + 21 candidates), and an AI-assisted abstract assessment with one recorded reason per candidate (52 excluded). Six records were retained, and the update added a seventh (C1–C7). They sit in a separately labelled block of Table V and in the "c" cells of Fig. 5, outside the 22.
2. **Audit package.** `audit/` holds A01–A14 and a `MANIFEST.md` with checksums:
   - A01–A07 are the former S1–S7, renamed so that no file name looks like a table number. A01 gains three 2026 rows.
   - A08 is the crosswalk from E01–E22 and C1–C7 to the table rows.
   - A09 is a record-level replay of the 11 September PubMed screen: 1,435 of 1,436 records, 363 rule-positive, 356 of them identical to the original pool.
   - A10 holds the Xplore decisions of the 22 October re-run.
   - A11 is the hand check.
   - A12 is the complement screen.
   - A13 is the search update.
   - A14 holds the code and dated query logs.
   - Builder: `review/build_audit.py`.
3. **Fig. 5 vs IV-E.** The IV-E text now says spatial modeling is shown by convolutional components (alone or in recurrent hybrids), one attention network (E13), graph models and the Bayesian reference. The caption lists the studies behind every D cell. The "Latency" column is renamed "Device" because Verbiest reports memory, and "c" cells mark complement-only evidence.
4. **Nitski.** Checked against the PubMed abstract on 22 October: four deep models against logistic regression, with the Transformer best. AUROC is 0.804 at 1 year and 0.733 at 5 years, with 99% CIs. UHN was evaluated only after fine-tuning. The table row, Val. "Abs.; A", UQ "99% CI", the text and Table III (marked § as unverified) are all updated. The text also states that intervals are not calibration.
5. **Screening and numbers.**
   - Fig. 1 and the text now say "false-omission fraction among rule-negative records".
   - The 54 overlaps were re-identified on 22 October: 54 of the 55 matched records are in the 363 pool, and one fails rule (iii) on its PubMed abstract. The union is therefore 593 under PubMed's verdict and 594 if either database's verdict sufficed; both figures are stated in the text.
   - All score pairs are now printed at source precision, with differences computed from the pairs: GluNet 19.28/21.54 → −2.26 (IEEE abstract); sleep bed 98.42/92.16 → +6.26.
   - The remaining pairs were checked against the sources: Lim 19.49/19.74; CiGNN 3.20/1.85 vs 3.97/2.04 (Table 3 of the PMC full text); Liu EEG 89.63/86.87; Herath 0.834/0.814 and 0.842/0.898; TransformerJM 0.890/0.812 vs 0.895/0.825 (PMC table).
   - `check_revision.py` recomputes all 24 displayed differences.
6. **Citations and illustrations.**
   - Target-trial emulation in VII-B now cites Hernán & Robins (it previously cited Sadée).
   - Fig. 3 is redrawn in TikZ, with the raster as one gridded field at t0–t2 and the video as ordered frames f0–f3. The PNG is no longer used.
   - Calibration and intervals are kept apart throughout.
7. **2026 literature.**
   - The seven sources were added and critically assessed:
     - Table I gains Gao, Wimalasiri and Chen (15 rows).
     - VI-A covers Briggs and Gao.
     - VI-D covers Jun & Ko.
     - VII-B covers EHRWorld, ChronoMedicalWorld, Wimalasiri and Chen, together with a new Table VI separating Ret./Fw./Sim./Sync./Pro. evidence.
     - VIII covers Jun & Ko.
     - The Limitations section gains a "Currency" paragraph.
   - None of these sources enters the 22.
   - The databases were re-searched on 22 October (Section II-G):
     - PubMed, by Entrez date from 12 September to 22 October: 50 new records, 9 rule-positive.
     - Xplore: 961 + 289 records; 44 inserted after 22 September, 12 of them rule-positive. The Xplore-only set grew from 230 to 242.
     - One new record became C7.
8. **Presentation.**
   - Fig. 2 gains five decision diamonds, each with a "no" branch.
   - Stable IDs E01–E22 and C1–C7 are used in Tables III and V and in A08.
   - Hardware is stated explicitly (Raspberry Pi 4B, 97.93 ms).
   - Repeated qualifications are consolidated into five reporting principles (II-H). Sections III-F, IV-F–IV-I, V-E, VI-E, VII-D–VII-E and VIII-A are condensed by 30–50%, which removes repetition with no loss of claims.
   - Table V is split into a part and a continuation under one table number.

## Other
- Acknowledgment: AI-use disclosure extended to this round.
- `\IEEEtriggeratref` moved from 87 to 99 to match the new reference count (114).
- Checkers: `port_checkers.py` reads the audit files and maps sub-items whose wording the 21 October rewrite replaced (marked SUPERSEDED 2026-10-22). It also counts E rows across the continued table, checks the threat and protocol prose sections, and records one documented refcheck exemption (a Crossref title quirk for Hernán & Robins).
- `check_revision.py` is rewritten for the new structure (59 checks).
- Results: check_revision 59/59, check_comments 50/50, J28 5/5, Oct1 9/9, check_supplement all tasks, strict refcheck 114 cited / 0 discrepancies.
- Build: 25 pages including references; 0 errors, 0 overfull boxes, 0 undefined references.
