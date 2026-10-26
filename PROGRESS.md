# Revision progress

State of the IEEE IoT-J revision, and what each review round asked for. Rounds are dated; the
review documents are internal correspondence and are not reproduced, so each item is stated as
the requirement it placed on the manuscript, not as a quotation, and no reviewer is named.

Last updated 2026-10-26. Overleaf is the source of truth:
https://www.overleaf.com/project/67d9bc605fe6221e6aadc7a4

## Which manuscript is current

**`expand25/` is the version under review.** It is a single 25-page document with no supplement.
`live/` holds the earlier 8-page submission build and its 16-page supplement; `expand25` was built
from it on 2026-10-12 (`expand25/CHANGES.md` records the base as byte-identical to `live/` before
work began), and `live/` is kept only as the record of that stage.

| | |
|---|---|
| Manuscript (`expand25/STmodel.tex`) | **25 pages** including references, 0 errors, 0 overfull boxes, 0 undefined references |
| Structure | 10 sections, 8 tables, 7 figures, one document — no supplementary file |
| Cited references | 114, from a 239-entry bibliography |
| Illustrative studies | 22, identified E01–E22, plus an IoT-engineering complement C1–C7 kept outside the 22 |
| Audit package | `expand25/audit/`, files A01–A14 with a manifest carrying dates and SHA-256 prefixes |

```bash
python3 review/verify_audit.py        # every audit file against the manifest; also checks coverage
```

## Rounds

### 2026-09-21 — ten comments, answered in the 8-page build

Selection and sample size; reproducibility; real IoT versus inferred feasibility; the
"quantitative synthesis" claim; comparison-table completeness; novelty against prior surveys;
quality assessment; datasets and benchmarks; networking, interoperability and security; claims,
presentation and references. The evidence set went from 12 to 22 studies, citation chasing was
actually run, and eleven of twelve compared reviews were read in full.
Check: `python3 review/check_comments.py` (50 sub-items).

### 2026-09-28 — five items, answered in the 8-page build

Verbatim search strings; both IEEE Xplore arms screened under the same rules as the PubMed arm;
one inaccurate sentence replaced; Table II trimmed and the widest supplement tables split;
every reference checked against the publisher record.
Check: `python3 review/check_j28.py`.

### 2026-10-01 — four items and the grants, answered in the 8-page build

Three dated PubMed snapshots reconciled; IEEE reviews excluded so the two arms screen alike;
table density; reference completeness. Grants: NIH R56DK114514-01 and R01DK129432 (PI: Fang),
NSF Award 2428595 (PI: Wang).
Check: `python3 review/check_oct1.py`.

### 2026-10-12 — restructure, 8 pages to 25

The `\ifsubmission` switch removed, the supplement merged into the body, the per-study records
moved out to CSV files. This was a structural change, not a response to a comment, and it is the
point after which the earlier 8-page checks no longer describe the manuscript under review.

### 2026-10-15 — manuscript evaluation, answered 2026-10-16

Decisions taken with the authors: one document with no supplement; stay within the 25-page limit;
keep the 22 studies and frame them as an illustrative focused synthesis; adopt the suggested
title. The revision came to 20 pages with 10 tables and 7 figures.
See `expand25/RESPONSE_TO_EVALUATION.md`.

### 2026-10-22 — eight required updates, answered

All eight are in the manuscript, verified against the file rather than against the response:

| | Requirement | Where it landed |
|---|---|---|
| 1 | Expand the IoT evidence synthesis | 230 Xplore-only and 307 IoT-term records screened; C1–C7 in Table V and the `c` cells of Fig. 5; 52 exclusions with reasons in A12 |
| 2 | Complete and label the audit package | A01–A14 with a manifest; filenames cannot be confused with table numbers; screening code included |
| 3 | Reconcile Fig. 5 with its text | Text and caption now agree on which families show explicit spatial modelling, and the caption lists the studies behind every demonstrated cell |
| 4 | Correct the Nitski extraction | Four deep models against logistic regression, AUROC 0.804 and 0.733, 99% CI, UHN only after fine-tuning |
| 5 | Screening and numerical reporting | "False-omission fraction" named; 54 of 55 overlaps inside the 363 pool, giving 593 under PubMed's verdict and 594 if either database's sufficed; differences recomputed at source precision (GluNet 19.28 vs 21.54 = −2.26; bed 98.42 vs 92.16 = +6.26) |
| 6 | Citations and illustrations | Target-trial emulation cites Hernán and Robins; Fig. 3 redrawn as a gridded field and ordered frames |
| 7 | 2026 literature and novelty | All seven sources added and assessed, none entering the 22; Table VI separates implemented models, frameworks, simulation evidence, synchronized services and prospective benefit; a "Currency" paragraph added to the limitations |
| 8 | Presentation and consistency | Decision branches in Fig. 2; E01–E22 and C1–C7 shared across Tables III and V with the A08 crosswalk; hardware stated as Raspberry Pi 4B, 97.93 ms throughout |

Search currency: both databases were re-searched on 2026-10-22 with per-record Entrez and
insertion dates logged (PubMed 50 new records, 9 rule-positive; Xplore 44 newly inserted, 12
rule-positive). See `expand25/RESPONSE_IoT_v2.md`.

## Open

1. **The hand check is not an independent check.** Its labelling sheet showed a
   machine-generated suggested decision and reason for each of the 60 records, and the author
   accepted the suggestion on 58 of the 59 records where the exposure was logged. The text now says
   so and A11 deposits the suggestion beside each decision, but the precision (62%) and
   false-omission (18%) estimates — and the ~375 pool estimate drawn from them — rest on a
   confirmation pass, not an independent re-read. Relabelling the 60 records with the suggestions
   hidden is the fix; it would change these numbers. **The highest-priority open item.**
2. **Independent re-coding.** The manuscript states in the Table I note that the coding is by a
   single reviewer and has not been independently re-audited, and the 10-22 round asked for
   conclusion-driving codes to be rechecked independently. A second person has to re-code a
   sample; this cannot be closed by tooling.
3. **Author verification of AI-assisted decisions:** the complement screen (A12), the 10-22 search
   update (A13), and the three new Table I codings (A01).
4. **Search cutoff versus submission date.** Screened through 2026-10-22. If submission slips, the
   searches need re-running: the standing position in this review is that citing 2026 papers does
   not by itself establish coverage to the submission date.
5. **Citation-to-claim relevance.** Every reference is real and bibliographically correct, but no
   pass has confirmed that each supports the sentence it is attached to. One cross-domain misuse
   was found this way earlier; a full pass needs the primary texts.
6. A Zenodo deposit for a citable DOI, if the journal wants one. The package is on GitHub now,
   which is addressable but not immutable.

## Errors found while checking, and why a check had missed them

Kept because the pattern matters more than the individual fixes: in each case a check reported
success while the artifact behind the claim was wrong or absent.

| Found | What was wrong | Why it got through |
|---|---|---|
| 2026-09-30 | Five counted claims contradicted the tables, including a leftover "(12)" where the tables support sixteen | Nothing compared prose counts against table cells |
| 2026-09-30 | Eleven citations carried wrong bibliographic data; ten were truncated titles | A title was accepted at 0.80 similarity once the DOI matched, and a truncation is a high-similarity prefix |
| 2026-10-01 | Two bib edits were lost when a patch script aborted before writing | The strict checker skips entries with no publisher record, so it could not see them |
| 2026-10-08 | Every plain-numbered supplement table printed one number too high, so six pointers were wrong | Every `\ref` still resolved; nothing compared printed numbers with the numbers the text cites |
| 2026-10-08 | Removing a column deleted the inferred deployment placement while the text claimed a table carried it | The checker looked for the sentence, not for a table backing it |
| 2026-10-26 | Ten of the thirty-five audit checksums did not match their files: they had been computed over CRLF line endings while the files are LF | Nothing re-verified the manifest after it was written. `review/verify_audit.py` now does |
| 2026-10-26 | The hand-check audit file A11 held a blank worksheet, not the labels behind the published 62%/18%. Recovering the real record showed the labelling sheet had displayed a machine-generated suggestion and reason for every record, which the author accepted on 58 of 59 — so the manuscript's "blind to the rule's verdict" was wrong | Nothing recomputed the published statistics from the deposited file, and no check asked how the labels were produced |
