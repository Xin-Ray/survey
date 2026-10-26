# Spatiotemporal Deep Learning for IoT-Enabled Digital Health

Working repository for the survey manuscript prepared for the **IEEE Internet of Things Journal**:
*Spatiotemporal Deep Learning for IoT-Enabled Digital Health: A Survey of Model Architectures,
Deployment Constraints, and Digital Twins* — Xin Xiang, Hua Fang, Dengyi Liu, Ashikur Nobel,
Honggang Wang (Yeshiva University). The title was changed at the 2026-10-15 round; the earlier
one ended "From Predictive Models to Digital Twins and Emerging World Models".

Overleaf is the source of truth for the manuscript:
https://www.overleaf.com/project/67d9bc605fe6221e6aadc7a4

## Layout

| Path | What it is |
|---|---|
| `expand25/` | **The manuscript under review.** `STmodel.tex` (25 pages, one document, no supplement), `newST.bib`, `figures/`, the `audit/` package (A01–A14 with a manifest), the `extraction/` CSVs, and the round responses `RESPONSE_TO_EVALUATION.md` (10-15) and `RESPONSE_IoT_v2.md` (10-22) |
| `live/` | The earlier 8-page submission build and its 16-page supplement, from which `expand25` was built. Kept as the record of that stage |
| `review/verify_audit.py` | Checks every audit file against the manifest checksums, and the listing for completeness |
| `review/check_comments.py` | Acceptance check with 50 sub-items for the 2026-09-21 round |
| `review/check_j28.py` | Acceptance check for the five items of the 2026-09-28 round |
| `review/check_oct1.py` | Acceptance check for the four items of the 2026-10-01 round, plus the grants |
| `review/check_consistency.py` | Cross-document audit: counted claims against table cells, arithmetic chains, labels and printed table numbers |
| `review/check_supplement.py` | Structural check of the supplement tables against the evidence table |
| `endnote/strict_refcheck.py` | Exact field-by-field reference check against Crossref and arXiv |
| `review/search/` | Search and screening pipeline: query definitions, records, the rule-based screen, the hand check, citation chasing |
| `endnote/` | `bib2endnote.py` reference verifier and `ieee_style.py`, which backfills publisher metadata and abbreviates journal names to IEEE style |
| `version1-original/`, `version2-shrink/`, `version3-IOT8page/` | Historical snapshots |

Note that the checks under `review/` were written against the 8-page build in `live/`. They remain
the record of those rounds; they do not describe `expand25`, which is verified by its own response
documents and by `review/verify_audit.py`.

## State of the manuscript

See **[PROGRESS.md](PROGRESS.md)** for each review round and what remains open.

- `expand25/STmodel.tex`: 25 pages including references, 0 errors, 0 overfull boxes, 0 undefined
  references; 10 sections, 8 tables, 7 figures, 114 cited references
- One document: every table and figure the argument uses is in the article, and the per-study
  records are released as the `expand25/audit/` package instead of a supplement
- 22 illustrative studies E01–E22, plus an IoT-engineering complement C1–C7 kept outside the 22
- Highest open item: the coding is by a single reviewer and still needs an independent re-check

## Reproducing the checks

```bash
python3 review/check_comments.py      # 50/50  round of 2026-09-21
python3 review/check_j28.py           #   5/5  round of 2026-09-28
python3 review/check_oct1.py          #   9/9  round of 2026-10-01
python3 review/check_consistency.py   # 47/47  cross-document consistency
python3 review/check_supplement.py    #  pass  supplement table integrity
python3 endnote/strict_refcheck.py    # references against publisher records
```

Each one reads the live `.tex` files and asserts against them, and each is wired as a Stop hook
in `.claude/settings.json`.

## Not in this repository

- **Full texts of the reviewed papers.** The evidence tables were extracted from 22 primary papers
  and 11 comparison reviews. Their PDFs and JATS XML carry mixed licences, several of them not
  redistributable, so none of them is published here. The extraction scripts and the derived tables
  are.
- **Internal review correspondence, the requirements register, and unsent email drafts.**
- The upstream ACM template distribution and the large compiled PDFs.
