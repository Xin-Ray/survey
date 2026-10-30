# Revision progress

State of the IEEE IoT-J revision, and what each review round asked for. Rounds are dated; the
review documents are internal correspondence and are not reproduced, so each item is stated as
the requirement it placed on the manuscript, not as a quotation, and no reviewer is named.

Last updated 2026-10-29. Overleaf is the source of truth:
https://www.overleaf.com/project/67d9bc605fe6221e6aadc7a4

## Which manuscript is current

**`expand25/` is the version under review.** It is a single document with no supplement; the
current build is 26 pages, one over the 25-page target the authors set on 2026-10-15, because
the per-study quality display the 10-29 review requires costs a page.
`live/` holds the earlier 8-page submission build and its 16-page supplement; `expand25` was built
from it on 2026-10-12 (`expand25/CHANGES.md` records the base as byte-identical to `live/` before
work began), and `live/` is kept only as the record of that stage.

| | |
|---|---|
| Manuscript (`expand25/STmodel.tex`) | **26 pages** including references, 0 errors, 0 warnings, 0 undefined references |
| Structure | 10 sections, **3 numbered tables**, 9 figures, one document — no supplementary file |
| Cited references | 114, from a 239-entry bibliography |
| Illustrative studies | 22, identified E01–E22, plus an IoT-engineering complement C1–C7 kept outside the 22 |
| Audit package | `expand25/audit/`, files A01–A16 with a manifest carrying dates and SHA-256 prefixes; cited at tag `audit-2026-10-29.2` |

```bash
python3 review/verify_audit.py        # every audit file against the manifest; also checks coverage
python3 review/check_oct29.py         # the 10-29 review items, recomputed from the artifacts
python3 review/record_sent_pdf.py X   # run before attaching: refuses a PDF already sent
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

### 2026-10-29 — six unresolved majors, one recommended enhancement, eight minors

The review opened by noting the attachment was byte-identical to the previous one, so nothing in it
was newly resolved. Hashing the manuscript PDFs on this machine confirmed the pattern predates that
round: two earlier groups of sent PDFs are byte-identical within the group. `review/record_sent_pdf.py`
now refuses a PDF whose bytes were sent before.

Everything that did not need publisher access or a second reader is done, and
`review/check_oct29.py` recomputes each item from the artifacts rather than checking that a sentence
is present. Two of the review's own items were defects introduced by the 10-26 to 10-28 work (the
"three sources measure nothing" contradiction, and 60 versus 59 in the hand-check disclosure).

| | Requirement | Where it landed |
|---|---|---|
| M5 | Verify the C7 chip figures | Settled from the abstract: it names a 25 mW chip, and 25 mW over 5 us is 125 nJ, inside the quoted 100–150 band once read as nanojoules. So the review's 20–30 W is right, the two quantities do share the end-to-end boundary, and the error is the unit. Recorded as unresolved at the unit, not as verified hardware evidence |
| M2 | Auditable provenance | 60/59 reconciled; "rule-positive search records" throughout; A16 dated selection ledger; the cited release is a tag, and the checker reads the tag name out of the manuscript so the two cannot drift |
| M4 | Study-level evidence display | Fig. 6: 22 studies by 12 fields, four states, every glyph recomputed from A05–A07, no aggregate score |
| M6 | Service-evaluation metric | Outcome-observed indicator in both numerator and denominator of the valid-output loss; label availability, label delay and the zero-denominator case stated |
| m1–m8 | Minor corrections | E18 recoded T in table, crosswalk and legend; VII-B contradiction removed; RQ1 referent named; BLE dated to a 2012 Bluetooth 4.0 measurement; assessed arXiv versions named; AI disclosure 117 → 83 words with all four roles |
| — | Reference list's last page | The column break was triggered at reference 99 of 114, leaving [98] alone. At 100 the final page carries [86]–[99] and [100]–[114] |

Found while recomputing, and not in the review: E19's validation cell held the literal code `0`,
which the legend never defined, and the merged evidence table was 1.07 pt too tall for its page.
Codes used and codes defined are now bijective, and the build has no warnings.

**Blocked, not done.** Full-text assessment of C1–C7 and the E21 descriptors needs IEEE and
ScienceDirect access; this machine's browser has none, and the three "full texts" saved for GluNet
and Nitski in 2026-09 turned out to be Cloudflare challenge pages, so those two were never obtained.
The independent verification needs a second reader: `review/independent_check/` holds the blinded
worksheets, the codebook and the scorer, and the generator refuses to write a sheet if any of our
coded values leaks into it.

## Open

1. **Publisher access for C1--C7 and E21.** The 10-29 review requires the seven complement records
   to be assessed in full text with the same fields as the main studies, and E21's inherited dataset
   descriptors to be verified or relabelled. All seven are IEEE or Elsevier; this machine's browser
   has no institutional access. Nothing in the manuscript can close these without it.
2. **A second reader.** `review/independent_check/` is ready -- blinded worksheets for 29 records and
   15 compared reviews, the codebook, and `score_independent.py`, which produces the agreement
   figures and the adjudication worksheet. Nobel has been asked; he has no publisher access either,
   so the source PDFs have to travel with the sheets.
3. **26 pages versus the 25-page target.** The required quality display costs a page. Either the
   target gives, or Section II is compressed per the review's own minor item 8 (say the scope and
   coding rules once, consolidate the search snapshots). Section II-H and the Limitations section
   were checked for redundancy first: their sub-claims are disjoint, so neither can simply be cut.
4. **The hand check is not an independent check.** Its labelling sheet showed a
   machine-generated suggested decision and reason for each of the 60 records, and the author
   accepted the suggestion on 58 of the 59 records where the exposure was logged. The text now says
   so and A11 deposits the suggestion beside each decision, but the precision (62%) and
   false-omission (18%) estimates — and the ~375 pool estimate drawn from them — rest on a
   confirmation pass, not an independent re-read. Relabelling the 60 records with the suggestions
   hidden is the fix; it would change these numbers. **The highest-priority open item.**
5. **Independent re-coding.** The manuscript states in the Table I note that the coding is by a
   single reviewer and has not been independently re-audited, and the 10-22 round asked for
   conclusion-driving codes to be rechecked independently. A second person has to re-code a
   sample; this cannot be closed by tooling.
6. **Author verification of AI-assisted decisions:** the complement screen (A12), the 10-22 search
   update (A13), and the three new Table I codings (A01).
7. **Search cutoff versus submission date.** Screened through 2026-10-22. If submission slips, the
   searches need re-running: the standing position in this review is that citing 2026 papers does
   not by itself establish coverage to the submission date.
8. **Citation-to-claim relevance.** Every reference is real and bibliographically correct, but no
   pass has confirmed that each supports the sentence it is attached to. One cross-domain misuse
   was found this way earlier; a full pass needs the primary texts.
9. A Zenodo deposit for a citable DOI, if the journal wants one. The package is on GitHub now,
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
| 2026-10-29 | The manuscript cited an audit release that no longer held the package it described: A16 was added after the tag was cut | The check hardcoded the tag name, so it verified a release the article did not necessarily cite. It now reads the name out of the manuscript |
| 2026-10-29 | E19's validation cell held the literal code `0`, which the legend never defined; A05 records no predictive hold-out at all | Nothing compared the codes used in the table against the codes the legend defines. `check_oct29.py` now requires the two sets to be equal in both directions |
