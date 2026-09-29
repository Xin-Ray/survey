# Search protocol (revision 3)

Window: 2015-01-01 – 2026-12-31 (date of publication). Fields: title + abstract.
Run date: see `pubmed_counts.json` / `ieee_counts.json` / `scopus_counts.json` (written by the scripts / manual export).

## Concept blocks

| Block | Terms |
|---|---|
| ST (spatiotemporal) | spatiotemporal OR spatio-temporal OR spatial-temporal OR space-time OR "spatial and temporal" |
| DL (deep learning) | "deep learning" OR "neural network*" OR transformer* OR "graph neural" OR LSTM OR recurrent OR convolutional OR "deep neural" |
| HL (health) | "digital health" OR wearable* OR "internet of things" OR IoT OR "mobile health" OR mHealth OR "remote monitoring" OR "continuous glucose" OR "electronic health record*" OR diabetes OR depression OR cardiac OR cardiovascular OR diet* OR "chronic disease*" OR "public health" OR "clinical prediction" OR "disease prediction" OR clinical OR patient* OR health |
| TW (twin / world model) | "digital twin*" OR "world model*" |

Arm A (spatiotemporal): ST AND DL AND HL
Arm B (twin / world model): TW AND DL AND HL
Union = Arm A ∪ Arm B, de-duplicated (PMID / DOI / normalized title).

Longitudinal-only studies (no spatial term) are **not** targeted by the query; they enter through citation chasing, as stated in the manuscript.

## PubMed (E-utilities, programmatic)
`pubmed_search.py` — esearch on each arm with history server, efetch XML, writes `pubmed_records.jsonl` and `pubmed_counts.json`.

## IEEE Xplore (web interface, logged-in session; counts read from the UI, records exported as CSV)
Command search string (Advanced Search → Command Search), Year 2015–2026:

Arm A:
("Abstract":spatiotemporal OR "Abstract":spatio-temporal OR "Abstract":spatial-temporal OR "Abstract":space-time OR "Document Title":spatiotemporal OR "Document Title":spatio-temporal OR "Document Title":spatial-temporal OR "Document Title":space-time) AND ("Abstract":"deep learning" OR "Abstract":"neural network" OR "Abstract":transformer OR "Abstract":"graph neural" OR "Abstract":LSTM OR "Abstract":recurrent OR "Abstract":convolutional) AND ("Abstract":"digital health" OR "Abstract":wearable OR "Abstract":"internet of things" OR "Abstract":IoT OR "Abstract":"mobile health" OR "Abstract":mHealth OR "Abstract":"remote monitoring" OR "Abstract":glucose OR "Abstract":"electronic health record" OR "Abstract":diabetes OR "Abstract":depression OR "Abstract":cardiac OR "Abstract":cardiovascular OR "Abstract":diet OR "Abstract":"chronic disease" OR "Abstract":"public health" OR "Abstract":clinical OR "Abstract":patient OR "Abstract":health)

Arm B:
("Abstract":"digital twin" OR "Abstract":"world model" OR "Document Title":"digital twin" OR "Document Title":"world model") AND ( DL block as above ) AND ( HL block as above )

## Scopus (web interface, institutional login; counts from UI, records exported as CSV)
Arm A:
TITLE-ABS-KEY(spatiotemporal OR "spatio-temporal" OR "spatial-temporal" OR "space-time" OR "spatial and temporal") AND TITLE-ABS-KEY("deep learning" OR "neural network*" OR transformer* OR "graph neural" OR LSTM OR recurrent OR convolutional OR "deep neural") AND TITLE-ABS-KEY("digital health" OR wearable* OR "internet of things" OR IoT OR "mobile health" OR mHealth OR "remote monitoring" OR "continuous glucose" OR "electronic health record*" OR diabetes OR depression OR cardiac OR cardiovascular OR diet* OR "chronic disease*" OR "public health" OR "clinical prediction" OR "disease prediction" OR clinical OR patient* OR health) AND PUBYEAR > 2014 AND PUBYEAR < 2027

Arm B:
TITLE-ABS-KEY("digital twin*" OR "world model*") AND ( DL block ) AND ( HL block ) AND PUBYEAR > 2014 AND PUBYEAR < 2027

## Citation chasing
Backward: reference lists of the reviews in Table I. Forward: OpenAlex `cited_by` for the same reviews (`citation_chase.py`). Logged in `citation_chase.json`.

## Screening (rule-based, `screen.py`; single reviewer; 60-record hand check recorded in `handcheck_60.csv`)
Item-type exclusion: Review, Systematic Review, Meta-Analysis, Editorial, Comment, Letter, News, Erratum, Retraction, Guideline.
Rules on title+abstract (all must hold):
- (i) space–time or longitudinal structure: a spatial term AND a temporal term, or "longitudinal" with a model term.
- (ii) human clinical or public health task: human-subject term present and not a non-human-only study.
- (iii) quantitative result against a named alternative: a metric term AND a comparison term.
Exact regexes are in `screen.py`.

## Note on OpenAlex (tried 2026-09-21, not used)
OpenAlex `search` applies stemming and loose boolean semantics: the IEEE-restricted run returned 7,929 records for Arm A against 1,723 in the IEEE Xplore fielded search. It is therefore not a valid substitute or cross-check for the fielded database searches and is not part of the protocol.
