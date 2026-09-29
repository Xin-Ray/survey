#!/usr/bin/env python3
"""Score the human labels against the rule. Input: handcheck60_labels.csv (from the sheet).
Outputs handcheck_result.json + a printed summary with the numbers that go into Section II."""
import csv, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
lab_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "handcheck60_labels.csv")
key = {r["pmid"]: r for r in csv.DictReader(open(os.path.join(HERE, "sample60_key.csv")))}
lab = {r["pmid"]: r for r in csv.DictReader(open(lab_path))}

missing = [p for p in key if p not in lab or not lab[p].get("decision")]
if missing:
    sys.exit(f"{len(missing)} records unlabelled: {missing[:8]}{'...' if len(missing) > 8 else ''}")

def wilson(k, n, z=1.959964):
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0.0, c-h), min(1.0, c+h))

agree = disagree_over = disagree_under = 0
conf = 0; rule_elig = 0
rows = []
for pmid, k in key.items():
    rv = "eligible" if k["rule_verdict"] == "eligible" else "excluded"
    hv = lab[pmid]["decision"].strip().lower()
    ok = rv == hv
    agree += ok
    if not ok:
        if rv == "eligible": disagree_over += 1      # rule said yes, human said no
        else: disagree_under += 1                    # rule said no, human said yes
    if rv == "eligible":
        rule_elig += 1; conf += (hv == "eligible")
    rows.append({"pmid": pmid, "index": int(k["index"]), "rule": k["rule_verdict"], "human": hv,
                 "agree": ok, "fails": lab[pmid].get("fails", ""), "note": lab[pmid].get("note", "")})

n = len(key)
prec = conf / rule_elig if rule_elig else 0
lo, hi = wilson(conf, rule_elig)
ELIGIBLE_TOTAL = 363
pool = ELIGIBLE_TOTAL * prec
res = {"n_checked": n, "agreement": f"{agree}/{n}", "agreement_pct": round(100*agree/n, 1),
       "rule_eligible_in_sample": rule_elig, "human_confirmed": conf,
       "precision": round(prec, 4), "precision_pct": round(100*prec, 1),
       "precision_ci95_wilson": [round(100*lo, 1), round(100*hi, 1)],
       "over_inclusions": disagree_over, "under_inclusions": disagree_under,
       "rule_eligible_total": ELIGIBLE_TOTAL,
       "pool_estimate": round(pool), "pool_ci95": [round(ELIGIBLE_TOTAL*lo), round(ELIGIBLE_TOTAL*hi)],
       "rows": sorted(rows, key=lambda r: r["index"])}
json.dump(res, open(os.path.join(HERE, "handcheck_result.json"), "w"), indent=1)

print(f"agreement           {agree}/{n}  ({100*agree/n:.1f}%)")
print(f"rule said eligible  {rule_elig};  you confirmed {conf}")
print(f"precision           {100*prec:.0f}%  (95% CI {100*lo:.0f}-{100*hi:.0f}%)")
print(f"over-inclusions     {disagree_over}   under-inclusions {disagree_under}")
print(f"pool estimate       {ELIGIBLE_TOTAL} x {prec:.2f} = ~{pool:.0f}  (range {ELIGIBLE_TOTAL*lo:.0f}-{ELIGIBLE_TOTAL*hi:.0f})")
print()
print("Sentence for Section II:")
print(f'  We re-read a random {n} decisions by hand: {agree} agreed, and of the {rule_elig} called')
print(f'  eligible {conf} were confirmed, a precision of {100*prec:.0f}% (95% CI {100*lo:.0f}--{100*hi:.0f}%).')
print(f'  ... the pool is better estimated at about {pool:.0f} studies ({ELIGIBLE_TOTAL*lo:.0f}--{ELIGIBLE_TOTAL*hi:.0f}).')
if disagree_over or disagree_under:
    print()
    print("Disagreements (check these are deliberate):")
    for r in sorted(rows, key=lambda r: r["index"]):
        if not r["agree"]:
            print(f'  #{r["index"]:02d} {r["pmid"]}  rule={r["rule"]:12s} you={r["human"]:8s} {r["note"]}')
