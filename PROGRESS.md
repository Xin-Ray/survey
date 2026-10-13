# Revision progress

State of the IEEE IoT-J revision, and what each review round asked for. Review rounds are
dated; the comments themselves are internal correspondence and are not reproduced here, so
each item is stated as the requirement it placed on the manuscript.

Last updated 2026-10-12. Overleaf is the source of truth for the two documents:
https://www.overleaf.com/project/67d9bc605fe6221e6aadc7a4

## Current state

| | |
|---|---|
| Submission build (`live/STmodel.tex`) | **8 pages**, 0 errors, 0 overfull boxes |
| Supplement (`live/supplement.tex`) | **16 pages**, 0 errors, 0 overfull boxes |
| Synthesized studies in Table II | 22, in five comparable task groups, five columns |
| Supplement tables | 14 tables in ten numbered slots, S0–S9 (the four widest split into a/b panels) |
| Cited references | 76, each checked field by field against its publisher record |
| Rule-eligible literature | 593 records across the two databases (363 PubMed + 230 Xplore-only) |

Acceptance checks, all green as of the last commit:

```bash
python3 review/check_comments.py      # 50/50   round of 2026-09-21
python3 review/check_j28.py           #   5/5   round of 2026-09-28
python3 review/check_oct1.py          #   9/9   round of 2026-10-01
python3 review/check_consistency.py   # 47/47   cross-document consistency
python3 review/check_supplement.py    #  pass   supplement table integrity
python3 endnote/strict_refcheck.py    # 76 cited, 0 discrepancies, 4 uncompared with a stated reason
```

Each checker reads the live `.tex` files and asserts against them. They exist because an
earlier checker verified the tables *we had decided to build* and reported everything green
while most of the review comments were still untouched: the standard has to come from the
review document, not from our own task list.

## Round of 2026-09-21 — ten comments

All ten applied; `review/check_comments.py` holds the 50 sub-items.

1. **Selection and sample size.** Evidence set expanded from 12 to 22 studies. Table II states
   two provenances, because they license different claims: twelve assembled while drafting, ten
   drawn from the rule-eligible pool under a stated frame with saturation as the stopping rule.
2. **Reproducibility.** Search strings, dates and per-database counts recorded; duplicate removal
   explained; the paper states plainly that one author ran the searches with no second screener.
   Forward and backward citation chasing was then actually run, surfacing 15 eligible records the
   database query had missed.
3. **Real IoT versus inferred feasibility.** Table II carries an evidence-class column
   (A device-captured, B clinical instrument, C registry or survey, D simulation); what each study
   *reports* about deployment is kept separate from the placement *we* infer.
4. **"Quantitative synthesis."** The phrase is gone; rows are grouped into comparable task groups
   and the table states that metrics are not comparable across rows.
5. **Comparison-table completeness.** Sampling rate, duration, spatial unit, missingness, external
   validation, calibration, uncertainty, subgroups and the principal limitation are recorded per
   study in the supplement.
6. **Novelty against prior surveys.** Eleven of the twelve compared reviews were read in full and
   the supplement names the section behind every mark. Reading them moved eight marks, mostly in
   the compared reviews' favour; two marks were withdrawn against our own interest.
7. **Quality assessment.** All 22 studies assessed on split, leakage, missing data, external
   validation, calibration, uncertainty, subgroups, comparators, reproducibility and clinical
   validation. No adjusted second cohort is called external validation anywhere.
8. **Datasets and benchmarks.** All 23 datasets described, with a suitability code for device or
   edge evaluation, multisite validation, and twin or intervention evaluation. No dataset supports
   all three.
9. **Networking, interoperability and security.** Link technologies compared with the consequence
   for sampling rate, loss and model-update cadence; threats and protections mapped across seven
   layers; the paper states that federated learning supplies neither encryption nor a privacy
   guarantee.
10. **Claims, presentation and references.** RQ1–RQ4 answered explicitly; terminology standardized;
    Figure 1 redrawn; references verified.

## Round of 2026-09-28 — five items

All five applied; `review/check_j28.py`.

1. Both search strings printed verbatim in the supplement; duplicate removal explained; the 363
   eligible records attributed to the PubMed screen; the database that was never searched is no
   longer mentioned.
2. Both IEEE Xplore arms exported and screened under the same three rules as the PubMed arm,
   then deduplicated within Xplore and against PubMed.
3. An inaccurate sentence about federated learning replaced with the reviewer's own wording.
4. Table II trimmed; the four widest supplement tables split into a/b panels that share one
   number, so the numbers the main text cites are unchanged.
5. Every cited reference checked against the publisher record and standardized to IEEE style.

## Round of 2026-10-01 — four items and the grants

All applied; `review/check_oct1.py`.

1. **Three PubMed totals reconciled.** They are three dated runs of the same query —
   1,436 (11 Sep), 1,444 (22–23 Sep), 1,456 (29 Sep). The paper and Figure 1 report the 11 Sep
   snapshot; the 29 Sep run is used only as the comparison set for the Xplore deduplication,
   because it was taken the same day as that export. Using the largest set there is the
   conservative choice: a larger PubMed set can only move records out of the Xplore-only count.
   Both arms are also printed as paste-ready strings, verified by submitting the block form and
   the expanded form separately and confirming identical counts
   (`review/search/expand_queries.py`). Title normalization and duplicate-retention rules stated.
2. **IEEE reviews excluded** rather than qualified: a textual rule at the same stage the PubMed
   arm removed its reviews takes out 37 records. This moved the eligible count only from 286 to
   284, because criterion (iii) wants a quantitative result against a named baseline and a review
   rarely reports one of its own — the exclusion matters for procedural equivalence, not for the
   number. The ten sampled studies are explicitly attributed to the 363 PubMed records.
3. **Table density.** Table II reduced to five columns with the deployment detail moved to the
   supplement. The supplement's sparse pages were a float-settings problem, not a table problem:
   the main paper loosens the LaTeX float parameters and the supplement never did, so it ran on
   the defaults where a float page is accepted at half full. With the parameters set and the table
   bodies raised one size, the supplement is 16 pages instead of 17 at a larger font.
4. **References.** Missing volume, issue and page details supplied; publication status confirmed;
   venue naming brought to one style.

   *No DOI appears in the reference list, by decision.* `IEEEtran.bst`, the official IEEE BibTeX
   style, does not support a `doi` field at all — the current release (v1.14, 2015) contains no
   "doi" handling anywhere in its source, while "url" occurs ninety times — and IEEE style omits
   the DOI for a normally published article, requiring it only for an early-access item. 62 of the
   76 cited entries carry a DOI in the `.bib` regardless, and
   `endnote/out_j28/strict_refcheck.md` is the record that every entry was checked.

**Grants.** NIH R56DK114514-01 and R01DK129432 (PI: Fang); NSF Award 2428595 (PI: Wang).

## Errors found and corrected while checking

Recorded because each one passed an earlier check, and the fix was to make the check real.

| Found | What was wrong | Why it got through |
|---|---|---|
| 2026-09-30 | Five counted claims contradicted the tables, including a leftover "(12)" from the twelve-study version where the tables support sixteen | Nothing compared prose counts against table cells. `check_consistency.py` now does, and found all five |
| 2026-09-30 | Eleven citations had wrong bibliographic data; ten were truncated titles | The verifier accepted a title at 0.80 similarity once the DOI matched, and a truncated title is a high-similarity prefix. `strict_refcheck.py` now demands an exact title |
| 2026-10-01 | Two bib edits were silently lost when a patch script aborted before writing | The strict checker skips entries with no publisher record, so it could not see them. `check_oct1.py` now asserts those fields directly |
| 2026-10-08 | Every plain-numbered supplement table printed one number too high, so six pointers in the paper were wrong — a table added to Section II had consumed an S-number | Every `\ref` inside the supplement still resolved. `check_consistency.py` now simulates the table counter and compares the printed numbers with the ones the main text cites |
| 2026-10-08 | Removing the deployment column deleted the inferred placement, while the main text claimed the supplement carried it | The comment checker looked for the sentence, not for a table backing it. It now asserts the column exists and all 22 rows are filled |

## Open

- Whether the repaired search string becomes the search of record, or the validation is reported
  with the search as actually run. Affects the eligible-pool denominator; a senior-author decision.
- Citation-to-claim relevance: every reference is real and correctly described, but no pass has yet
  confirmed that each one supports the sentence it is attached to. One cross-domain misuse was
  found and fixed this way; a full pass needs the primary texts read.
- Co-author verification of the tabulated numbers.
