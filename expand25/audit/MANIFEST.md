# Audit package: Spatiotemporal Deep Learning for IoT-Enabled Digital Health

Assembled 2026-10-22 by review/build_audit.py. There is no supplementary document: every table is in the article. These files hold record-level detail only. File prefixes A01-A14 are audit-file numbers and never refer to table numbers. This package is published at https://github.com/Xin-Ray/survey under `expand25/audit/`; run `python3 review/verify_audit.py` from the repository root to check every file against the checksums below. Study identifiers E01-E22 (illustrative set) and C1-C7 (IoT-engineering complement, abstract-level) match Tables III and V; see A08.

| File | Content | SHA-256 (first 16) |
|---|---|---|
| A01_survey_comparison_coding.csv | Section-level evidence for every mark of Table I (15 reviews; three 2026 rows added 2026-10-22). | 5da1b2e974729f62 |
| A02_study_provenance_and_inclusion.csv | Provenance (drafting-stage or PubMed-sampled) and reason for inclusion of E01-E22. | d2efbefd183ef23d |
| A03_datasets_descriptors_part1.csv | Dataset descriptors behind Table III (part 1). | 913b4c128dcd9310 |
| A04_datasets_descriptors_part2.csv | Dataset descriptors behind Table III (part 2). | f3a4dc83f296486a |
| A05_quality_split_leakage_missing_external.csv | Quality fields: split, leakage, missing data, external validation. | 2a3d3991e53df141 |
| A06_quality_calibration_subgroups_comparators.csv | Quality fields: calibration and uncertainty, subgroups, comparators, reproducibility. | 1a56e1d3622faf1d |
| A07_deployment_privacy_reporting.csv | Deployment, cost and privacy reporting. | e0c16088777e7cb1 |
| A08_study_id_crosswalk.csv | Crosswalk: stable identifier -> BibTeX key, Table V (evidence) row, Table III (datasets) row, audit files. | aeb47cf652d4e9d8 |
| A09_pubmed_snapshot_20260911_decisions.csv | Record-level replay (run 2026-10-22) of the 11 Sept 2026 PubMed screen: Entrez date <= 2026-09-11, item-type exclusion, rules (i)-(iii); column in_published_363 marks the original pool. Replay summary in A14. | 946350c7408fc1b9 |
| A10_xplore_decisions_20261022.csv | Record-level IEEE Xplore decisions of the 22 Oct 2026 re-run (both arms), with insertion dates, duplicate and PubMed matches, and membership of the 1 Oct 2026 Xplore-only list. | d0d5f27738005fdd |
| A11_handcheck_60.csv | Single-reviewer hand check of 60 PubMed records against the rule verdict, 23 September 2026. Carries the per-record rule flags, the author's decision, and the machine-generated suggestion and reason that the labelling sheet displayed, so the dependence of the check on that suggestion can be assessed (accepted on 58 of the 59 logged records). | 1aca361b1dff46a2 |
| A12_iot_complement_screen.csv | IoT-engineering complement screen (22 Oct 2026): 230 Xplore-only and 307 IoT-term records, E1/E2 rules, AI-assisted abstract assessment with a reason per candidate; retained records C1-C6. | b16d2de653c8d27a |
| A13_search_update_20261022.csv | Search update through 22 Oct 2026: PubMed records by Entrez date 12 Sept-22 Oct, Xplore records inserted after 22 Sept, and the PubMed side of the cross-database overlaps; C7 retained. | e57ce2c7e7ce155f |
| A14_code_and_query_logs/FINDINGS.md | Code or dated query/count log. | c5c77af765273b13 |
| A14_code_and_query_logs/citation_chase.json | Code or dated query/count log. | 9d557af9f7435b47 |
| A14_code_and_query_logs/citation_chase.py | Code or dated query/count log. | 87720c4bb46bba90 |
| A14_code_and_query_logs/db_queries_original_blocks.txt | Code or dated query/count log. | 40e8544cc066fbb7 |
| A14_code_and_query_logs/fetch_ieee_a.py | Code or dated query/count log. | 50c4c2ae513a6ffc |
| A14_code_and_query_logs/fetch_ieee_abstracts.py | Code or dated query/count log. | 5179542e8c3dd30e |
| A14_code_and_query_logs/fetch_iot_complement.py | Code or dated query/count log. | b4d7bb087d48e65c |
| A14_code_and_query_logs/ieee_counts.json | Code or dated query/count log. | d335211446e63ace |
| A14_code_and_query_logs/ieee_screen.json | Code or dated query/count log. | 3f01463c1e85d1ee |
| A14_code_and_query_logs/ieee_screen.py | Code or dated query/count log. | b67a9e91c9517781 |
| A14_code_and_query_logs/merge_dedup.py | Code or dated query/count log. | 78abf9e7675ed38b |
| A14_code_and_query_logs/pubmed_counts.json | Code or dated query/count log. | cb9a06fe6f9b6123 |
| A14_code_and_query_logs/query_expansion_check.json | Code or dated query/count log. | 9cf9915c917a8744 |
| A14_code_and_query_logs/replicate_rules.py | Code or dated query/count log. | 076bb62b77d3c9f7 |
| A14_code_and_query_logs/screen.py | Code or dated query/count log. | d0bdef43a002656f |
| A14_code_and_query_logs/screen_iot_complement.py | Code or dated query/count log. | 4256a49d2e911d3f |
| A14_code_and_query_logs/search_protocol.md | Code or dated query/count log. | 65d81371b40f59ce |
| A14_code_and_query_logs/update_20261022_ieee_screen.json | Code or dated query/count log. | dd4d79996a192147 |
| A14_code_and_query_logs/update_20261022_pubmed_snapshot_replay.json | Code or dated query/count log. | 89bef51b4ff9f092 |
| A14_code_and_query_logs/update_20261022_reconstruct_pubmed_snapshot.py | Code or dated query/count log. | cc47eebedd5f09be |
| A14_code_and_query_logs/update_20261022_update_analysis.py | Code or dated query/count log. | d6f969a4033eaf92 |
| A14_code_and_query_logs/update_20261022_update_summary.json | Code or dated query/count log. | 068bf67e5ddc8ca5 |
