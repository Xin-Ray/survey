#!/usr/bin/env python3
"""Record-level replay of the 11 September 2026 PubMed screen.

The original run kept only aggregate counts. This replays it record by record: the two original
arms restricted to Entrez dates up to 2026/09/11 (so later indexing is excluded), the item-type
exclusion by PublicationType, and the three recovered rules of replicate_rules.py (the same
verdict function ieee_screen.py applies to Xplore). Output: pubmed_snapshot_20260911_decisions.csv
and a comparison of the replayed counts with the published ones and with eligible363_pmids.txt.
"""
import csv, json, os, sys, time
import xml.etree.ElementTree as ET
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("ua", os.path.join(HERE, "update_analysis.py"))
ua = importlib.util.module_from_spec(spec); spec.loader.exec_module(ua)
isc = ua.isc
NON_RESEARCH = {"Editorial", "Comment", "Letter", "News", "Erratum", "Published Erratum", "Retraction of Publication",
                "Retracted Publication", "Guideline", "Practice Guideline", "Video-Audio Media", "Historical Article",
                "Clinical Trial Protocol", "Congress", "Lecture", "Interview", "Biography"}
REVIEWS = {"Review", "Systematic Review", "Scoping Review", "Meta-Analysis"}
PUBLISHED = {"unique": 1436, "non_research": 36, "reviews": 194, "screened": 1206, "fail_ii": 99, "fail_i": 127,
             "fail_iii": 617, "eligible": 363}


def main():
    arms, ids = {}, set()
    for name, q in isc.ARMS.items():
        root = ET.fromstring(ua.eu("esearch.fcgi", {"db": "pubmed", "term": f"({q}) AND 1800/01/01:2026/09/11[edat]",
                                                     "retmax": 5000}))
        arms[name] = [e.text for e in root.findall(".//IdList/Id")]; ids |= set(arms[name])
    recs = ua.efetch(sorted(ids))
    rows, c = [], {"unique": len(ids), "non_research": 0, "reviews": 0, "no_abstract": 0, "fail_ii": 0, "fail_i": 0,
                   "fail_iii": 0, "eligible": 0}
    for pmid in sorted(ids):
        r = recs.get(pmid, {"types": [], "abstract": "", "title": "", "doi": "", "entrez_date": ""})
        t = set(r["types"])
        if t & NON_RESEARCH: d = "excluded_non_research"; c["non_research"] += 1
        elif t & REVIEWS: d = "excluded_review"; c["reviews"] += 1
        elif not r["abstract"].strip(): d = "excluded_no_abstract"; c["no_abstract"] += 1
        else:
            v, r1, r2, r3 = isc.verdict(r["title"] + " " + r["abstract"])
            d = v; key = {"excluded_ii_not_human_health": "fail_ii", "excluded_i_no_spacetime_structure": "fail_i",
                          "excluded_iii_no_quantitative_comparison": "fail_iii", "eligible": "eligible"}[v]
            c[key] += 1
        rows.append({"pmid": pmid, "arm": "+".join(a for a in arms if pmid in arms[a]), "entrez_date": r["entrez_date"],
                     "doi": r["doi"], "decision": d, "title": r["title"]})
    pool = set(open(os.path.join(UP, "eligible363_pmids.txt")).read().split())
    elig = {x["pmid"] for x in rows if x["decision"] == "eligible"}
    c["screened"] = c["unique"] - c["non_research"] - c["reviews"] - c["no_abstract"]
    comp = {"replayed": c, "published": PUBLISHED, "arm_counts": {k: len(v) for k, v in arms.items()},
            "eligible_in_published_363": len(elig & pool), "published_363_not_replayed": len(pool - elig),
            "replayed_eligible_not_in_363": len(elig - pool), "run_date": time.strftime("%Y-%m-%d")}
    for x in rows:
        x["in_published_363"] = x["pmid"] in pool
    with open(os.path.join(HERE, "pubmed_snapshot_20260911_decisions.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump(comp, open(os.path.join(HERE, "pubmed_snapshot_replay.json"), "w"), indent=1)
    print(json.dumps(comp, indent=1))


if __name__ == "__main__":
    main()
