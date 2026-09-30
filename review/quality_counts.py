#!/usr/bin/env python3
"""Derive the quality-assessment headline counts from the supplement tables.

The body of the paper states how the twenty-two studies split, calibrate, report
subgroups, release code and validate clinically. Those counts are classified here
from the cells of Tables S3 and S5 rather than typed, because an earlier draft of
the covering email carried 16/4/2/1 for the split classification when the cells
support 14/4/3/1.

Judgment is involved in exactly two rows and is named in the output:
Kong et al. run ten-fold cross-validation within each site without stating the
subject level, and Lin et al. split within a subject across movement repetitions,
so the same person appears on both sides. Both are counted against the studies.

    python3 review/quality_counts.py
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUPP = os.path.join(ROOT, "live", "supplement.tex")
OUT = os.path.join(ROOT, "review", "quality_counts.json")


def panel(t, label):
    i = t.index("\\label{" + label + "}")
    s = t.rindex("\\begin{table*}", 0, i)
    e = t.index("\\end{table*}", i)
    blk = t[s:e]
    hdr = [c.strip().replace("\\textbf{", "").rstrip("}")
           for c in re.split(r"(?<!\\)&",
                             blk[blk.index("\\toprule") + 8:blk.index("\\midrule")]
                             .strip().rstrip("\\").strip())]
    body = blk[blk.index("\\midrule"):blk.index("\\bottomrule")]
    rows = [[c.strip() for c in re.split(r"(?<!\\)&", r)]
            for r in re.split(r"\\\\", body) if "&" in r and "multicolumn" not in r]
    rows = [r for r in rows if len(r) == len(hdr)]
    return hdr, rows


def name(cell):
    return re.sub(r"~?\\cite\{[^}]*\}", "", cell).strip()


# A split holds out whole people or a later time window.
SUBJECT_LEVEL = re.compile(
    r"leave-one-subject-out|at the subject level|subject-level|subject-wise|"
    r"subject-disjoint|split by patient|split by participant|subjects split|"
    r"subjects held out|per subject|within each subject in time|"
    r"first 90\\% of months", re.I)
# Same person on both sides: the unit split is smaller than a person.
SUB_PERSON = re.compile(r"of samples for training|split of 424 scans|"
                        r"across movement repetitions|clips split into segments", re.I)
NO_HOLDOUT = re.compile(r"^none;", re.I)
NOT_STATED = re.compile(r"^n/r$|not stated at subject level|run separately within each site", re.I)


def main():
    t = open(SUPP, encoding="utf-8").read()
    hdr_a, rows_a = panel(t, "tab:S3a")
    _, rows_a2 = panel(t, "tab:S5a")
    hdr_b, rows_b = panel(t, "tab:S3b")
    _, rows_b2 = panel(t, "tab:S5b")
    A = rows_a + rows_a2          # study, split, leakage, missing, external
    B = rows_b + rows_b2          # study, calibration, subgroups, comparators, repro, clinical
    assert len(A) == len(B) == 22, (len(A), len(B))

    split = {"whole subjects or a later window": [], "unit smaller than a person": [],
             "level not stated": [], "no hold-out at all": []}
    for r in A:
        s = r[1]
        if NO_HOLDOUT.search(s):
            split["no hold-out at all"].append(name(r[0]))
        elif NOT_STATED.search(s):
            split["level not stated"].append(name(r[0]))
        elif SUB_PERSON.search(s):
            split["unit smaller than a person"].append(name(r[0]))
        elif SUBJECT_LEVEL.search(s):
            split["whole subjects or a later window"].append(name(r[0]))
        else:
            split.setdefault("unclassified", []).append(name(r[0]) + " :: " + s[:60])

    cal_nr = [name(r[0]) for r in B if re.search(r"calibration n/r", r[1], re.I)]
    curve = [name(r[0]) for r in B if re.search(r"calibration curve", r[1], re.I)]
    interval = [name(r[0]) for r in B
                if re.search(r"\d+\\%\s*(intervals|bounds)|bootstrap intervals", r[1], re.I)]
    subgroup = [name(r[0]) for r in B if not re.match(r"^n/r", r[2], re.I)]
    subgroup_demo = [name(r[0]) for r in B
                     if re.search(r"subgroups|subpopulations|age groups|per-sex|"
                                  r"male and female|age-stratified", r[2], re.I)]
    code = [name(r[0]) for r in B
            if re.search(r"code public|source code .*released", r[4], re.I)]
    clinical_none = [name(r[0]) for r in B if re.match(r"^none", r[5], re.I)]

    res = {
        "studies": len(A),
        "split": {k: len(v) for k, v in split.items()},
        "split_detail": split,
        "calibration_not_reported": len(cal_nr),
        "calibration_curve_reported": len(curve),
        "any_interval_or_bounds": sorted(interval),
        "subgroup_any_cell": len(subgroup),
        "subgroup_demographic_or_clinical": sorted(subgroup_demo),
        "code_released": sorted(code),
        "clinical_validation_none": len(clinical_none),
    }
    json.dump(res, open(OUT, "w"), indent=1)

    print(f"studies: {res['studies']}")
    print("split classification:")
    for k, v in split.items():
        print(f"  {len(v):2d}  {k}")
        if k == "unclassified" and v:
            for x in v:
                print(f"        {x}")
    print(f"calibration not reported: {res['calibration_not_reported']} of {res['studies']}")
    print(f"calibration curve reported: {res['calibration_curve_reported']}")
    print(f"interval or bounds shown: {len(res['any_interval_or_bounds'])} "
          f"{res['any_interval_or_bounds']}")
    print(f"subgroup breakdown: {len(res['subgroup_demographic_or_clinical'])} "
          f"{res['subgroup_demographic_or_clinical']}")
    print(f"code released: {len(res['code_released'])} {res['code_released']}")
    print(f"no clinical validation: {res['clinical_validation_none']} of {res['studies']}")
    if split.get("unclassified"):
        sys.exit("some split cells were not classified; extend the rules above")


if __name__ == "__main__":
    main()
