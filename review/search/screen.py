#!/usr/bin/env python3
"""Rule-based title/abstract screening of the merged search records.

Input : merged_records.jsonl (from merge_dedup.py) or pubmed_records.jsonl
Output: screen_decisions.csv (one row per record with every rule outcome),
        screen_counts.json (PRISMA numbers), handcheck_60.csv (random sample for the single-reviewer hand check)

Rules (all three must hold to be rule-eligible):
  (i)   space-time or longitudinal structure
  (ii)  human clinical or public health task
  (iii) quantitative result against a named alternative
Item-type exclusions are applied first (reviews / non-research).
"""
import argparse, csv, json, os, random, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))

NON_RESEARCH_TYPES = {"Editorial", "Comment", "Letter", "News", "Erratum", "Published Erratum", "Retraction of Publication",
                      "Retracted Publication", "Guideline", "Practice Guideline", "Video-Audio Media", "Historical Article",
                      "Clinical Trial Protocol", "Congress", "Lecture", "Interview", "Biography", "Corrected and Republished Article"}
REVIEW_TYPES = {"Review", "Systematic Review", "Scoping Review", "Meta-Analysis"}
REVIEW_TITLE = re.compile(r"\b(a |an )?(systematic |scoping |narrative |literature |comprehensive |mini-?)?(review|survey|meta-analysis|overview|perspective|roadmap|tutorial|state of the art)\b", re.I)

# (i) structure
SPATIAL = re.compile(r"\b(spatio-?temporal|spatial-?temporal|space-?time|spatial|geograph\w*|location\w*|gps|region\w*|count(y|ies)|neighbou?rhood|graph|connectivity|topolog\w*|map(ping)?|voxel|3d|volumetric|ambient|environmental exposure)\b", re.I)
TEMPORAL = re.compile(r"\b(temporal|time[- ]series|longitudinal|sequen\w*|dynamic\w*|forecast\w*|trajector\w*|recurrent|lstm|gru|transformer\w*|time-?varying|over time|follow-?up|multi-?visit|continuous (glucose )?monitoring|streams?)\b", re.I)
LONGIT = re.compile(r"\blongitudinal\b", re.I)
MODEL = re.compile(r"\b(deep|neural|network|learning|model\w*|transformer|lstm|rnn|cnn|gnn)\b", re.I)

# (ii) human clinical / public health
HUMAN = re.compile(r"\b(patients?|participants?|subjects|cohorts?|clinical|clinic|hospital\w*|human|adults?|children|adolescents?|elderly|older adults|population|individuals|volunteers|persons?|people|residents|users|wearers|epidemiolog\w*|public health|surveillance|incidence|prevalence|mortality|EHR|electronic health)\b", re.I)
NONHUMAN = re.compile(r"\b(mice|mouse|murine|rats?|rodents?|zebrafish|canine|porcine|bovine|animal model|in vitro|cell lines?|organoids?|plants?|crops?|vegetation|soil|traffic|vehicles?|buildings?|bridges?|machinery|bearings?|turbines?|power grid|manufacturing|industrial|robot\w*|drone|satellite|remote sensing|weather|precipitation|air quality|ocean|earthquake|seismic|wildfire|hydrolog\w*)\b", re.I)

# (iii) quantitative result vs named alternative
METRIC = re.compile(r"\b(accuracy|auc|auroc|auprc|rmse|mae|mape|mse|f1|dice|sensitivity|specificity|precision|recall|c-?index|concordance|r\^?2|error rate|correlation|kappa|iou|log-?loss|brier)\b|\d+(\.\d+)?\s?%", re.I)
COMPARE = re.compile(r"\b(outperform\w*|compared (to|with|against)|comparison|baselines?|versus|vs\.?|better than|superior|improv\w* (over|upon|on|by)|state-of-the-art|sota|benchmark\w*|existing (methods|models|approaches)|conventional (methods|models)|traditional (methods|models)|svm|random forest|logistic regression|arima|sarima\w*|xgboost|gradient boosting|lstm|cnn|gru|transformer|linear regression)\b", re.I)


def screen_one(r):
    text = (r.get("title", "") + " " + r.get("abstract", "")).strip()
    types = set(r.get("pubtypes") or [])
    out = {"id": r.get("pmid") or r.get("doi") or r.get("title", "")[:60], "source": r.get("source", "pubmed"),
           "year": r.get("year", ""), "title": r.get("title", ""), "doi": r.get("doi", "")}
    if types & NON_RESEARCH_TYPES:
        out.update(stage="item_type", decision="excluded_non_research"); return out
    if (types & REVIEW_TYPES) or REVIEW_TITLE.search(r.get("title", "")):
        out.update(stage="item_type", decision="excluded_review"); return out
    if not r.get("abstract"):
        out.update(stage="item_type", decision="excluded_no_abstract"); return out
    rule_i = bool((SPATIAL.search(text) and TEMPORAL.search(text)) or (LONGIT.search(text) and MODEL.search(text)))
    rule_ii = bool(HUMAN.search(text)) and not (NONHUMAN.search(text) and not re.search(r"\b(patients?|clinical|hospital)\b", text, re.I))
    rule_iii = bool(METRIC.search(text) and COMPARE.search(text))
    out.update(stage="rules", rule_i=rule_i, rule_ii=rule_ii, rule_iii=rule_iii)
    if not rule_ii:
        out["decision"] = "excluded_ii_not_human_health"
    elif not rule_i:
        out["decision"] = "excluded_i_no_spacetime_structure"
    elif not rule_iii:
        out["decision"] = "excluded_iii_no_quantitative_comparison"
    else:
        out["decision"] = "eligible"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="pubmed_records.jsonl")
    ap.add_argument("--seed", type=int, default=20260921)
    a = ap.parse_args()
    recs = [json.loads(l) for l in open(os.path.join(HERE, a.input))]
    rows = [screen_one(r) for r in recs]
    fields = ["id", "source", "year", "decision", "stage", "rule_i", "rule_ii", "rule_iii", "doi", "title"]
    with open(os.path.join(HERE, "screen_decisions.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    counts = {"input_records": len(rows), "run_date": datetime.date.today().isoformat(), "input_file": a.input}
    for d in ["excluded_non_research", "excluded_review", "excluded_no_abstract", "excluded_ii_not_human_health",
              "excluded_i_no_spacetime_structure", "excluded_iii_no_quantitative_comparison", "eligible"]:
        counts[d] = sum(1 for x in rows if x["decision"] == d)
    counts["screened_on_title_abstract"] = counts["input_records"] - counts["excluded_non_research"] - counts["excluded_review"] - counts["excluded_no_abstract"]
    json.dump(counts, open(os.path.join(HERE, "screen_counts.json"), "w"), indent=1)
    # hand-check sample: 60 random decisions from the rule stage, for the single reviewer to confirm
    random.seed(a.seed)
    pool = [x for x in rows if x["stage"] == "rules"]
    sample = random.sample(pool, 60)
    byid = {r.get("pmid") or r.get("doi") or r.get("title", "")[:60]: r for r in recs}
    with open(os.path.join(HERE, "handcheck_60.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "year", "rule_decision", "title", "abstract", "reviewer_decision (eligible/excluded)", "reviewer_reason"])
        for x in sample:
            w.writerow([x["id"], x["year"], x["decision"], x["title"], byid[x["id"]].get("abstract", ""), "", ""])
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
