# Independent verification — instructions and codebook

Two sheets, 44 rows in total. Please work only from the source papers, and **do not open the
manuscript or its tables while you code**. That is not a formality: the previous self-check was
rejected precisely because its sheet showed machine-generated suggestions and the author accepted
58 of 59. Seeing our coding first would reproduce that failure.

| File | Rows | What to code |
|---|---|---|
| `sheet_studies.csv` | 22 illustrative studies (E01–E22) + 7 complement records (C1–C7) | inclusion + six fields |
| `sheet_surveys.csv` | 15 compared reviews | nine coverage marks |

Fill the empty columns. `reason` is required on every row where you fill anything — one line is
enough, but it is what makes a disagreement adjudicable. Leave a field blank only if you could not
reach the information; write `?` if the paper does not state it. Those two are different and the
distinction matters to the review.

## sheet_studies.csv

**`include`** — `yes` / `no`. All three must hold:

- (i) the data carry both a spatial or multi-site structure *and* a temporal structure;
- (ii) the application is health or clinical;
- (iii) the paper reports a quantitative result against a **named** baseline or comparator model.

Criterion (iii) is the one that does most of the excluding: a paper reporting only its own accuracy,
with no named prior method or comparator, fails it.

**`spatial_code`** — what the *predictor* encodes, not what preprocessing used:

| Code | Meaning |
|---|---|
| `Adm` | administrative regions |
| `Anat` | anatomical, voxel or image grid |
| `Rel` | relational sensor or anatomical layout encoded by the model |
| `MC` | multichannel, no spatial prior |
| `T` | temporal only |

A pose extractor may use anatomy while the downstream model treats its outputs as independent
channels; that is `MC`, not `Rel`.

**`iot_class`** — `N` IoT-native (captured by a body-worn, ambient or consumer device),
`A` IoT-adaptable (a signal that such a device could capture, but this study did not),
`R` record-based (registry, EHR, survey or scanner data).

**`split_level`** — the strongest claim the split actually supports:

`W` within-subject · `A` across-time · `R` repetition-level · `S` subject- or patient-disjoint ·
`T` temporal hold-out of a population series · `?` not stated · `--` no predictive hold-out.

If a second cohort was used for fine-tuning, it is **not** an external validation.

**`comparator_value`** — the comparator's score **as printed in the source**, at the source's own
precision, with its metric (e.g. `RMSE 21.54 mg/dL`). If the paper compares only against its own
ablation, write `ablation only`. If no comparator value is given, `n/r`.

**`calibration_claim`** — `none` / `interval` (a prediction or credible interval only) /
`calibration curve` (an actual calibration assessment) / `?`. An interval or a Brier score is not a
calibration assessment.

**`external_validation_claim`** — `none` / `held-out site` (an untouched external site or registry) /
`adapted site` (external data the model was fine-tuned or recalibrated on) / `?`.

**`resource_basis`** — for any latency, energy, memory or FLOP figure the paper reports:
`measured` (on named hardware), `estimated` (from a toolchain or analytic count), `simulated`, or
`not reported`. Where the paper gives a number, please also put the number and its hardware in
`reason` — this is the field the review is most pointed about, and one earlier round went wrong by
counting a toolchain estimate as a measurement.

## sheet_surveys.csv

For each compared review, mark each scope column `●` substantive coverage, `○` partial, `--` not a
focus. These are scope judgments, not quality scores, and `--` means "not established from what you
read", not "absent from the literature".

`IoT` IoT layer / acquisition tier · `ST` spatiotemporal model families · `App` clinical application ·
`DT` digital twin · `WM` world model · `Priv` privacy · `Edge` edge deployment · `Data` datasets ·
`Eval` evaluation.

Please base each mark on the full text where you have it, and say in `reason` which section or table
carried the mark. Two of the fifteen may only be assessable from their abstract; if so, say so.

## Returning the sheets

Send both CSVs back unchanged in structure. I then run
`python3 review/independent_check/score_independent.py`, which reports per-field agreement, lists
every disagreement, and produces the adjudication worksheet. Disagreements are not errors on your
part — they are the output. The manuscript will report the scope of the verification, the
disagreements, how they were adjudicated, and which cells changed as a result.
