# Spatiotemporal Deep Learning for IoT-Enabled Digital Health

Working repository for the survey manuscript prepared for the **IEEE Internet of Things Journal**:
*Spatiotemporal Deep Learning for IoT-Enabled Digital Health: From Predictive Models to Digital
Twins and Emerging World Models* — Xin Xiang, Hua (Julia) Fang, Dengyi Liu, Ashikur Nobel,
Honggang Wang (Yeshiva University).

Overleaf is the source of truth for the manuscript:
https://www.overleaf.com/project/67d9bc605fe6221e6aadc7a4

## Layout

| Path | What it is |
|---|---|
| `live/` | **Current submission files.** `STmodel.tex` (8-page IoT-J build), `supplement.tex` (16 pages, tables S0–S9), `newST.bib` |
| `review/check_comments.py` | Acceptance check with 50 sub-items evaluated against the live files |
| `review/check_j28.py` | Acceptance check for the five items of the 2026-09-28 round |
| `review/check_oct1.py` | Acceptance check for the four items of the 2026-10-01 round, plus the grants |
| `review/check_consistency.py` | Cross-document audit: counted claims against table cells, arithmetic chains, labels and the printed supplement numbers |
| `endnote/strict_refcheck.py` | Exact field-by-field reference check against Crossref and arXiv |
| `review/check_supplement.py` | Structural check of the ten supplement tables against Table II |
| `review/search/` | Search and screening pipeline: query definitions, PubMed and IEEE records, the rule-based screen, the 60-record hand check, citation chasing, and the seed-recall repair of the query |
| `endnote/` | `bib2endnote.py` reference verifier (Crossref / arXiv / DBLP) and `ieee_style.py`, which backfills volume, issue, pages and DOI from the publisher record and abbreviates journal names to IEEE style |
| `version1-original/`, `version2-shrink/`, `version3-IOT8page/` | Historical snapshots of the manuscript |

## State of the manuscript

See **[PROGRESS.md](PROGRESS.md)** for what each review round asked for and what was done.

- Submission build 8 pages, supplement 16 pages, both with no errors and no overfull boxes
- 22 synthesized studies in Table II, at five columns, grouped into five comparable task groups
- 14 supplement tables in ten numbered slots S0–S9, the four widest split into an a and a b panel
  sharing one number: survey-comparison evidence, threats by IoT layer, datasets, quality
  assessment, communication substrate, per-study system and privacy reporting, provenance and
  inclusion reason, citation chasing
- Both search strings printed verbatim and verified by re-submission; both IEEE arms screened
  under the same rules as the PubMed arm, reviews excluded on both sides
- 76 cited references, each compared field by field against its publisher record; four cannot be
  compared and each is named with its reason

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
