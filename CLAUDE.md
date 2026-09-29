# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A LaTeX survey paper, "Spatiotemporal Deep Learning for IoT-Enabled Digital Health: From Predictive Models to Digital Twins and World Models" (Xiang, Fang, Liu, Wang; Yeshiva University), being revised for submission to the **IEEE Internet of Things Journal**. Not a git repository. No code, tests, or linters; the only build is LaTeX.

`feedback_iotsurvey.txt` at the root is the reviewer/advisor action list driving the current revision (14 numbered items: IoT-centric reframing, survey methodology + PRISMA flowchart, survey-comparison table, two-dimensional IoT-layer x model taxonomy, paper-level comparison tables, less textbook background, IoT threat-surface security, dataset/metrics table, IEEE format, IEEE references). Read it before making content edits; every change should map to one of those items.

## Directory layout: three snapshots, not branches

- `version1-original/` — the ACM `acmsmall` version (1640-line `STmodel.tex`, `unsrtnat` bibliography). Contains the full acmart class distribution and `samples/`, which is upstream template noise, not paper content. Historical only.
- `version2-shrink/` — first IEEEtran conversion, condensed to 581 lines. Historical. Its `figures/` folder is the superset of all figure PNGs (see the extended-build gotcha below).
- `version3-IOT8page/` — **the active version.** Edit here.

Each version has its own `STmodel.tex` and `newST.bib`; they have diverged, so never copy a `.bib` or `.tex` across versions wholesale.

## Building (version3-IOT8page)

Run from inside `version3-IOT8page/`. TeX Live is installed at `/Library/TeX/texbin`.

```bash
# 8-page IEEE IoT-J submission build (the deliverable; must stay <= 8 pages)
latexmk -pdf STmodel.tex

# Extended build with every table/figure/passage restored (~22 pages)
latexmk -pdf STmodel-full.tex

# Clean auxiliary files
latexmk -C
```

Check page count after any edit to the submission build: `grep 'Output written' STmodel.log`.

**Known break:** the extended build currently fails with `File 'digital twin in health care.png' not found`. That figure is inside an `\ifsubmission\else` block and the PNG only exists in `version2-shrink/figures/`. Copy it into `version3-IOT8page/figures/` if you need the extended PDF.

## Single-source, two-build structure of STmodel.tex

`STmodel-full.tex` is a 6-line wrapper that does `\def\EXTENDED{}` then `\input{STmodel}`. Do not put content in it. In `STmodel.tex`:

- `\newif\ifsubmission` defaults true; `\ifdefined\EXTENDED\submissionfalse\fi` flips it for the extended build.
- Prefer the single-branch form `\ifsubmission\else ...extended-only... \fi`. Use the two-branch `\ifsubmission <short> \else <long> \fi` only when a passage genuinely needs two wordings.
- **Every `\ref` must resolve in both builds.** If a float is extended-only, the sentence referring to it must be inside the same conditional.
- `\figw` is `0.72\linewidth` in submission and `\linewidth` in extended; use it for retained figures.
- Float fractions are loosened in the preamble so full-width `table*`/`figure*` share pages with text. Adding floats with `[p]` or `[t]` placement can silently push the submission build past 8 pages.

Other preamble conventions:

- `\graphicspath{{figures/}{./}}`, so `\includegraphics` names are bare filenames. Several figure filenames contain spaces and parentheses (e.g. `Frame 34.png`); keep the braces intact.
- `\cadd{}` / `\cdel{}` are change-tracking macros (green add, red strikethrough) left over from the ACM-to-IEEE conversion. No current usages remain; they are available for a marked-up response-to-reviewers build.
- `\Description{}` is defined as a no-op so acmart-era figure descriptions survive under IEEEtran.
- Bibliography is `\bibliographystyle{IEEEtran}` with `\bibliography{newST}`; citations use the `cite` package. Reviewer item 14 asks that every reference be verified for IEEE style, DOI, venue, and page range.

## Paper structure (version 3)

Introduction -> Spatiotemporal Data in Connected Digital Health -> DL-based Spatiotemporal Modeling Methods -> Spatiotemporal Models in Digital Health -> DNN-based Medical and Longitudinal Models -> Medical Digital Twins (incl. federated learning and privacy) -> World Model Based Digital Twins -> Future Prospects -> Review Limitations -> Conclusion. Seven `table*` floats carry the comparison evidence. The reviewer feedback asks to fold the longitudinal-models section into the taxonomy and to add Survey Methodology and survey-comparison sections; those are pending.
