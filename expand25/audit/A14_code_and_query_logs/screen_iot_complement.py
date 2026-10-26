#!/usr/bin/env python3
"""Second-stage IoT-engineering screen of the records the synthesis had sized but not screened.

Input: iot_complement_records.json (fetch_iot_complement.py).
  * Xplore-only records: already rule-eligible under criteria (i)-(iii).
  * PubMed IoT-term additions: first screened under the same three rules and item-type exclusion.
Second stage (all must hold; textual rules over title + abstract):
  E1 device acquisition -- data from a body-worn, ambient, smartphone, camera or IoT/sensor device;
  E2 system measurement -- an inference time, latency, energy/power, memory/model-size, bandwidth
     or on-device/embedded/edge execution is reported or evaluated;
  E3 human health task (criterion ii, re-applied).
Every record gets one decision row; E1-E3 positives are listed for hand assessment.
Writes iot_complement_screen.csv.
"""
import csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
src = open(os.path.join(HERE, "replicate_rules.py"), encoding="utf-8").read()
ns = {"re": re}
for line in src.splitlines():
    if re.match(r"^(NONHEALTH|HUMAN|PRECLIN|SPACETIME|METRIC|NUMBER|COMPARE)\s*=", line):
        exec(line, ns)

E1 = re.compile(r"\b(wearables?|body-worn|wrist|smart ?watch\w*|smartphones?|mobile phones?|IMUs?|inertial|"
                r"acceleromet\w+|gyroscop\w+|PPG|photoplethysmo\w+|internet of things|IoT|sensor networks?|"
                r"ambient|radar|wi-?fi|cameras?|webcams?|edge devices?|insoles?|e-?textile|patch(es)?|"
                r"continuous glucose|CGM|portable)\b", re.I)
E2 = re.compile(r"\b(latenc\w+|inference time|run ?time|real[- ]time|milliseconds?|\d+(\.\d+)?\s?ms\b|"
                r"energy|power consumption|mW|memory|RAM|flash|model size|parameters?|FLOPs?|MACs?|"
                r"bandwidth|throughput|on-device|on device|embedded|microcontroller|MCU|FPGA|"
                r"raspberry pi|jetson|edge (computing|device|deployment|inference)|lightweight|quantiz\w+|"
                r"pruning|compress\w+)\b", re.I)
REVIEW = re.compile(r"\b(review|systematic|meta-analys\w+|survey|scoping)\b", re.I)
NONRES = {"Review", "Systematic Review", "Meta-Analysis", "Editorial", "Comment", "Letter", "News",
          "Erratum", "Published Erratum", "Retraction of Publication", "Guideline"}


def rules(text):
    r2 = not ((ns["NONHEALTH"].search(text) and not ns["HUMAN"].search(text))
              or (ns["PRECLIN"].search(text) and not ns["HUMAN"].search(text)))
    r1 = bool(ns["SPACETIME"].search(text))
    r3 = bool(ns["METRIC"].search(text) and ns["NUMBER"].search(text) and ns["COMPARE"].search(text))
    return r1, r2, r3


def main():
    d = json.load(open(os.path.join(HERE, "iot_complement_records.json"), encoding="utf-8"))
    rows = []
    for doi, r in d["xplore_only"].items():
        t = (r.get("title") or "") + " " + re.sub(r"<[^>]+>", " ", r.get("abstract") or "")
        e1, e2 = bool(E1.search(t)), bool(E2.search(t))
        dec = ("no_abstract" if not r.get("abstract") else
               "candidate" if (e1 and e2) else "excluded_E1_no_device" if not e1 else "excluded_E2_no_system_measure")
        rows.append({"set": "xplore_only", "id": doi, "doi": doi, "year": r.get("year", ""),
                     "online_date": r.get("onlineDate", ""), "venue": r.get("venue", ""),
                     "rule_i": True, "rule_ii": True, "rule_iii": True, "E1_device": e1,
                     "E2_system": e2, "decision": dec, "title": r.get("title", "")})
    for pmid, r in d["pubmed_iot"]["records"].items():
        t = (r.get("title") or "") + " " + (r.get("abstract") or "")
        r1, r2, r3 = rules(t)
        e1, e2 = bool(E1.search(t)), bool(E2.search(t))
        if NONRES & set(r.get("types") or []) or REVIEW.search(r.get("title") or ""):
            dec = "excluded_item_type_or_review"
        elif not r.get("abstract"):
            dec = "no_abstract"
        elif not r2:
            dec = "excluded_ii_not_human_health"
        elif not r1:
            dec = "excluded_i_no_spacetime_structure"
        elif not r3:
            dec = "excluded_iii_no_quantitative_comparison"
        else:
            dec = "candidate" if (e1 and e2) else "excluded_E1_no_device" if not e1 else "excluded_E2_no_system_measure"
        rows.append({"set": "pubmed_iot_term", "id": pmid, "doi": r.get("doi", ""), "year": r.get("year", ""),
                     "online_date": "", "venue": r.get("venue", ""), "rule_i": r1, "rule_ii": r2, "rule_iii": r3,
                     "E1_device": e1, "E2_system": e2, "decision": dec, "title": r.get("title", "")})
    out = os.path.join(HERE, "iot_complement_screen.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) + ["hand_decision", "reason"])
        w.writeheader()
        for r in rows:
            w.writerow(dict(r, hand_decision="", reason=""))
    from collections import Counter
    for s in ("xplore_only", "pubmed_iot_term"):
        print(s, dict(Counter(r["decision"] for r in rows if r["set"] == s)))


if __name__ == "__main__":
    main()
