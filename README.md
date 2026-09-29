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
| `live/` | **Current submission files.** `STmodel.tex` (8-page IoT-J build), `supplement.tex` (14 pages, tables S0–S9), `newST.bib` |
| `review/check_comments.py` | Acceptance check with 50 sub-items evaluated against the live files |
| `review/check_j28.py` | Acceptance check for the five items of the 2026-09-28 review round |
| `review/check_supplement.py` | Structural check of the ten supplement tables against Table II |
| `review/search/` | Search and screening pipeline: query definitions, PubMed and IEEE records, the rule-based screen, the 60-record hand check, citation chasing, and the seed-recall repair of the query |
| `endnote/` | `bib2endnote.py` reference verifier (Crossref / arXiv / DBLP) and `ieee_style.py`, which backfills volume, issue, pages and DOI from the publisher record and abbreviates journal names to IEEE style |
| `version1-original/`, `version2-shrink/`, `version3-IOT8page/` | Historical snapshots of the manuscript |

## State of the manuscript

- 22 synthesized studies in Table II, at six columns, grouped into five comparable task groups
- Fourteen supplement tables in ten numbered slots S0–S9, the four widest split into an a and a b
  panel sharing one number: survey-comparison evidence, threats by IoT layer, datasets, quality
  assessment, communication substrate, per-study system and privacy reporting, provenance and
  inclusion reason, citation chasing
- The verbatim PubMed and IEEE Xplore search strings, and both IEEE arms screened under the same
  three rules as the PubMed arm
- 77 cited references, each checked field by field against its Crossref record, with journal names
  abbreviated to IEEE style and every remaining gap justified against the publisher's own record

## Reproducing the checks

```bash
python3 review/check_comments.py
python3 review/check_j28.py
python3 review/check_supplement.py
python3 endnote/ieee_style.py --no-net
python3 endnote/bib2endnote.py --bib live/newST.bib --tex live/STmodel.tex --out endnote/out_r3
```

## Not in this repository

- **Full texts of the reviewed papers.** The evidence tables were extracted from 22 primary papers
  and 11 comparison reviews. Their PDFs and JATS XML carry mixed licences, several of them not
  redistributable, so none of them is published here. The extraction scripts and the derived tables
  are.
- **Internal review correspondence, the requirements register, and unsent email drafts.**
- The upstream ACM template distribution and the large compiled PDFs.
