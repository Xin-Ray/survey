# Survey-methodology findings (2026-09-21 → 09-23)

Everything here is reproducible from the scripts in this folder. Original artefacts live on the
Windows machine at `D:\xxiangworking\2026surveypaper\9-2-2026nobel-feedback\New_version\search\`
(recovered 2026-09-22 via the "Survey paper IEEE transaction改动" session).

## 1. The original search is recovered and verified

Search date **2026-09-11**, PubMed E-utilities, four concept blocks (`fetch_pubmed.py`):

```
A = (spatiotemporal[tiab] OR "spatio-temporal"[tiab] OR "space-time"[tiab] OR "space time"[tiab])
B = ("deep learning"[tiab] OR "neural network"[tiab] OR "neural networks"[tiab] OR transformer[tiab]
     OR transformers[tiab] OR "graph network"[tiab] OR "graph neural"[tiab])
C = (health[tiab] OR clinical[tiab] OR patient[tiab] OR patients[tiab] OR wearable[tiab] OR wearables[tiab])
D = ("digital twin"[tiab] OR "digital twins"[tiab] OR "world model"[tiab] OR "world models"[tiab])
Y = 2015:2026[dp]
main = A AND B AND C AND Y      dtwm = D AND B AND C AND Y
```

Re-run 2026-09-22/23: main 1,173 · dtwm 274 · overlap 3 · union 1,444, against the manuscript's
1,171 / 268 / 3 / 1,436. The difference is new indexing in an open 2026 window, so the manuscript's
numbers stand as the 2026-09-11 snapshot.

The three screening rules were recovered verbatim and are replicated in `replicate_rules.py`.
Replication is consistent with the stored 363-record eligible list for every study tested.

**Defect to fix:** §II says "Figure 1 gives the search string"; Figure 1's TikZ source contains no
search string (the figure was thinned on 2026-09-16 after a "too dense" comment and the sentence was
not updated). The string exists in no build. Put it in the Methodology prose or a footnote.

## 2. The recovery numbers in §II are wrong

§II currently states: *"only one of the 363 is cited here. The query recovers 6 of our 12; the rest
are indexed elsewhere or carry no spatial term to match."*

Measured by exact DOI→PMID join (`recovery_check.py`, `why_missed.py`, `replicate_rules.py`):

| | manuscript | measured |
|---|---|---|
| of the 12, indexed in PubMed at all | "the rest are indexed elsewhere" | **12 of 12** |
| of the 12, retrieved by the query | 6 | **4** |
| of the 12, among the 363 rule-eligible | 1 | **3** |

Retrieved and rule-eligible: Thaipisutikul (39281477), Zhang/STANet (39728900), Bohoran (38066222).
Retrieved but screened out: Xie & Yao (35751197) — criterion (iii), the abstract carries no
quantitative comparison against a named alternative.

Why the other eight were not retrieved (block test reproduces PubMed's retrieval for all 12, so
these attributions are checkable):

| study | PMID | blocked by | reason |
|---|---|---|---|
| Li / GluNet | 31369390 | A | CGM forecasting; no spatial term |
| Lim / life-log | 40348812 | A | same |
| Nitski | 33858815 | A | longitudinal registry; no spatial term (would have passed the rules) |
| Glaser / DXA | 35992891 | A | serial imaging; no spatial term |
| Lin & Luo | 35347750 | A + C | no spatial term, and no health word in title/abstract |
| Kong | 33969930 | B | writes "graph convolutional network", which block B does not match |
| Li 2016 / BRFSS | 27903059 | B | Bayesian spatiotemporal model, not deep learning |
| Liu / MODMA | 35625016 | C | EEG-signal abstract; no health/clinical/patient/wearable term |

This is a precise answer to Prof. Fang's comment 2 ("explain why only six of the 12 were recovered"):
it is four, not six, and each miss has a named cause. Note two of the misses are not accidents —
the 2016 study is not a deep-learning paper, and Kong's wording exposes a real gap in block B.

## 3. The 60-record hand check was labelled by a model, not by a human

Reported by the session that ran it: the 60 abstracts were read and labelled by that Claude session
on 2026-09-16; per-record decisions were never saved, only the aggregate (54/60 agreement; 15 of 21
confirmed → precision 71%, Wilson 95% CI 50–86% → pool ≈ 260, 180–310).

Consequences:
- §II says "We re-read a random 60 decisions **by hand**".
- The Acknowledgment says "All **literature selection** … are the authors' own".

Neither holds as written. Either an author re-labels the same 60 records (`handcheck/`), or the
precision sentence, the ≈260 estimate and the §IX sentence that leans on it come out.
Nothing else in the chain is affected: identification, dedup, item-type and rule counts
(1,436 / 1,206 / 99+127+617 / 363) are all machine-derived and reproducible.

The six records that session disagreed with the rule on: 40538965, 41855851, 42406767, 42456718,
42198080, 40039387 — all over-inclusions, all inside the 21 the rule called eligible. Use these only
as a check **after** independent labelling, not during.

## 4. Database status

| source | status |
|---|---|
| PubMed | fully logged, programmatic, reproducible (`pubmed_search.py`, counts above) |
| IEEE Xplore | counts logged 2026-09-22 with the same concept blocks: **arm A 928, arm B 274** (`ieee_counts.json`). Record export needs a free IEEE personal account — pending |
| Scopus | **no institutional access.** scopus.com shows "Preview" with Check access / Contact sales, document search redirects to the homepage, and the YU Libraries A–Z list returns 0 hits for scopus (also 0 for web of science and embase) |

§II currently claims all three databases were searched. Unless access existed elsewhere on
2026-09-11, that claim must be corrected — the honest form is PubMed + IEEE Xplore + citation
chasing, both databases count-logged.

## 5. Corrections to earlier work in this folder

The 2026-09-21 protocol in `search_protocol.md` used wider ad-hoc concept blocks of my own
(health block of 20 terms vs the original 6, extra spatial and DL terms). It produced 2,121 / 343 /
2,457 / 832 and an IEEE count of 1,723 / 418 — none of which is comparable with the PubMed arm.
Superseded; the original narrow blocks are now used everywhere. `openalex_search.py` was also
discarded (OpenAlex stemming returned 7,929 for arm A against 1,723 fielded).

## 6. Outstanding

1. One author labels the 60 records — `handcheck/handcheck_sheet.html`, then `handcheck/score.py`.
2. IEEE personal account → export arm A and arm B to `ieee_a.csv` / `ieee_b.csv` → `merge_dedup.py`.
3. Decide the Scopus wording.
4. Fix in `STmodel.tex`: the search string, "6 of our 12" → 4, "one of the 363" → 3, drop
   "indexed elsewhere", and the Fig. 1 dashed box.
