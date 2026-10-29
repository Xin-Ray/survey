#!/usr/bin/env python3
"""Score the second reviewer's returned sheets against our coding.

Run this only after the sheets come back. It reads our values from the manuscript's own evidence
table and from the audit files, compares them field by field, and writes an adjudication worksheet
listing every disagreement. The disagreements are the product: the review asks us to report their
scope, how they were adjudicated, and which cells changed as a result.

    python3 review/independent_check/score_independent.py [returned_studies.csv] [returned_surveys.csv]
"""
import csv, io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TEX = os.path.join(ROOT, "expand25", "STmodel.tex")
AUDIT = os.path.join(ROOT, "expand25", "audit")

# Which evidence-table column carries each field we asked the reviewer to code.
TABLE_COL = {"iot_class": 1, "spatial_code": 2, "split_level": 6, "resource_basis": 8}


def ours_from_table():
    tex = io.open(TEX, encoding="utf-8").read()
    i = tex.index(r"\label{tab:evidence}")
    s = tex.rindex(r"\begin{table*}", 0, i)
    e = tex.index(r"\end{table*}", i)
    out = {}
    for line in tex[s:e].split("\n"):
        line = line.strip()
        m = re.match(r"^(E\d\d|C\d)\b", line)
        if m and line.count("&") >= 9:
            cells = [c.strip() for c in line.rstrip("\\").split("&")]
            out[m.group(1)] = {f: cells[c] for f, c in TABLE_COL.items()}
            out[m.group(1)]["comparator_value"] = cells[5]
    return out


def norm(v):
    v = re.sub(r"\\[a-zA-Z]+", "", (v or "")).replace("$", "").replace("~", " ")
    v = re.sub(r"[^\w?%.+-]", " ", v)
    return re.sub(r"\s+", " ", v).strip().lower()


def main():
    studies_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "returned_studies.csv")
    surveys_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "returned_surveys.csv")
    if not os.path.exists(studies_path):
        sys.exit(f"no returned sheet at {studies_path} -- nothing to score yet")

    theirs = {r["id"]: r for r in csv.DictReader(io.open(studies_path, encoding="utf-8-sig"))}
    ours = ours_from_table()

    agree = collections.Counter()
    total = collections.Counter()
    disagreements = []
    unfilled = []

    for sid, t in theirs.items():
        o = ours.get(sid, {})
        for field in list(TABLE_COL) + ["comparator_value"]:
            tv, ov = (t.get(field) or "").strip(), (o.get(field) or "").strip()
            if not tv:
                unfilled.append((sid, field))
                continue
            total[field] += 1
            if norm(tv) == norm(ov) or (norm(tv) and norm(tv) in norm(ov)):
                agree[field] += 1
            else:
                disagreements.append({"record": sid, "field": field, "ours": ov,
                                      "second_reviewer": tv, "their_reason": t.get("reason", ""),
                                      "adjudication": "", "cell_changed": ""})

    print("Field-by-field agreement with the second reviewer\n")
    for field in list(TABLE_COL) + ["comparator_value"]:
        n = total[field]
        if n:
            print(f"  {field:26} {agree[field]:3}/{n:<3} = {agree[field]/n:5.1%}")
    n_all, a_all = sum(total.values()), sum(agree.values())
    if n_all:
        print(f"\n  overall{'':19} {a_all:3}/{n_all:<3} = {a_all/n_all:5.1%}")
    print(f"\n  {len(disagreements)} disagreement(s); {len(unfilled)} field(s) left blank")

    out = os.path.join(HERE, "adjudication.csv")
    with io.open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["record", "field", "ours", "second_reviewer",
                                          "their_reason", "adjudication", "cell_changed"])
        w.writeheader()
        w.writerows(disagreements)
    print(f"\n  wrote {os.path.relpath(out, ROOT)} -- fill 'adjudication' and 'cell_changed' per row.")
    print("  Inclusion decisions are reported separately: "
          f"{sum(1 for t in theirs.values() if (t.get('include') or '').strip().lower() == 'no')} "
          "record(s) the second reviewer would exclude.")
    if unfilled:
        print("\n  Blank fields (could not reach the information, or the sheet is partial):")
        for sid, field in unfilled[:20]:
            print(f"    {sid} {field}")
        if len(unfilled) > 20:
            print(f"    ... and {len(unfilled) - 20} more")


if __name__ == "__main__":
    main()
