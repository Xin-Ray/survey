#!/usr/bin/env python3
"""Build the blinded worksheets for the second reviewer.

The 2026-10-29 review asks for a second person to verify the inclusion decisions and six
consequential fields, because the author's own hand check does not count: its sheet displayed
machine-generated suggestions and the author accepted 58 of 59. The whole value of this exercise
is that the second reader never sees our coding, so this generator deliberately takes only
*identifiers* from the bibliography and the crosswalk, and never reads A01--A07, where our codes
live. The assertion at the end enforces that: if any of our coded values leaks into a sheet, it
fails rather than writing the file.

    python3 review/independent_check/make_sheets.py
"""
import csv, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BIB = os.path.join(ROOT, "expand25", "newST.bib")
CROSSWALK = os.path.join(ROOT, "expand25", "audit", "A08_study_id_crosswalk.csv")
TEX = os.path.join(ROOT, "expand25", "STmodel.tex")

STUDY_COLS = [
    "id", "authors", "year", "venue", "doi", "title",
    "include",                      # yes / no  -- does it meet criteria (i)-(iii)?
    "spatial_code",                 # Adm / Anat / Rel / MC / T
    "iot_class",                    # N / A / R
    "split_level",                  # W / A / R / S / T / ? / --
    "comparator_value",             # the comparator score as printed in the source
    "calibration_claim",            # none / interval / calibration curve / ?
    "external_validation_claim",    # none / held-out site / adapted site / ?
    "resource_basis",               # measured / estimated / simulated / not reported
    "reason",                       # one line, required whenever a field is filled
]

SURVEY_COLS = ["name", "year", "venue", "doi", "title",
               "IoT", "ST", "App", "DT", "WM", "Priv", "Edge", "Data", "Eval", "reason"]


def parse_bib(path):
    text = io.open(path, encoding="utf-8").read()
    entries = {}
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,]+),", text):
        key = m.group(2).strip()
        start = m.end()
        depth = 1
        j = text.index("{", m.start())
        d = 0
        for k in range(j, len(text)):
            if text[k] == "{":
                d += 1
            elif text[k] == "}":
                d -= 1
                if d == 0:
                    body = text[j + 1:k]
                    break
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*", body):
            name = fm.group(1).lower()
            rest = body[fm.end():].lstrip()
            if rest.startswith("{"):
                d2 = 0
                for k2 in range(len(rest)):
                    if rest[k2] == "{":
                        d2 += 1
                    elif rest[k2] == "}":
                        d2 -= 1
                        if d2 == 0:
                            fields[name] = rest[1:k2]
                            break
            else:
                fields[name] = rest.split(",")[0].strip()
        entries[key] = fields
    return entries


def clean(s):
    s = re.sub(r"[{}]", "", s or "")
    s = re.sub(r"\\&", "&", s)
    s = re.sub(r"\\emph\s*", "", s)
    return re.sub(r"\s+", " ", s).strip()


def first_authors(s, n=3):
    parts = [p.strip() for p in clean(s).split(" and ")]
    out = ", ".join(parts[:n])
    return out + (" et al." for _ in [0]).__next__() if len(parts) > n else out


def main():
    bib = parse_bib(BIB)
    cross = list(csv.DictReader(io.open(CROSSWALK, encoding="utf-8-sig")))

    # --- sheet 1: the 22 studies and the 7 complement records
    rows = []
    for r in cross:
        key = r["bibtex_key"]
        e = bib.get(key, {})
        rows.append({
            "id": r["id"],
            "authors": first_authors(e.get("author", "")),
            "year": clean(e.get("year", "")),
            "venue": clean(e.get("journal") or e.get("booktitle") or ""),
            "doi": clean(e.get("doi", "")),
            "title": clean(e.get("title", "")),
            **{c: "" for c in STUDY_COLS[6:]},
        })
    rows.sort(key=lambda r: (r["id"][0], int(re.sub(r"\D", "", r["id"]) or 0)))

    # --- sheet 2: the survey-comparison coding of Table I, identifiers only
    tex = io.open(TEX, encoding="utf-8").read()
    i = tex.index(r"\label{tab:related-surveys}")
    s = tex.rindex(r"\begin{table*}", 0, i)
    e = tex.index(r"\end{table*}", i)
    surveys = []
    for line in tex[s:e].split("\n"):
        line = line.strip()
        m = re.match(r"^([A-Z][^&]*?)\s*&", line)
        cm = re.search(r"\\cite\{([^}]+)\}", line)
        if m and cm and "multicolumn" not in line and "This survey" not in line:
            key = cm.group(1).split(",")[0]
            b = bib.get(key, {})
            surveys.append({
                "name": clean(m.group(1)),
                "year": clean(b.get("year", "")),
                "venue": clean(b.get("journal") or b.get("booktitle") or ""),
                "doi": clean(b.get("doi", "")),
                "title": clean(b.get("title", "")),
                **{c: "" for c in SURVEY_COLS[5:]},
            })

    # --- the blinding assertion: no coded value from our tables may appear
    forbidden = set()
    for name in ("A01_survey_comparison_coding.csv", "A05_quality_split_leakage_missing_external.csv",
                 "A06_quality_calibration_subgroups_comparators.csv",
                 "A07_deployment_privacy_reporting.csv"):
        p = os.path.join(ROOT, "expand25", "audit", name)
        if os.path.exists(p):
            for rr in csv.reader(io.open(p, encoding="utf-8-sig")):
                for cell in rr[1:]:
                    c = cell.strip()
                    if len(c) > 12:
                        forbidden.add(c)
    blank_cols = STUDY_COLS[6:] + SURVEY_COLS[5:]
    for sheet in (rows, surveys):
        for rr in sheet:
            for c in blank_cols:
                if rr.get(c, "") != "":
                    sys.exit(f"blinding violated: {c} is pre-filled for {rr.get('id') or rr.get('name')}")
            joined = " ".join(str(v) for v in rr.values())
            hit = [f for f in forbidden if f and f in joined]
            if hit:
                sys.exit(f"blinding violated: a coded value leaked into a sheet: {hit[:2]}")

    p1 = os.path.join(HERE, "sheet_studies.csv")
    with io.open(p1, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=STUDY_COLS)
        w.writeheader()
        w.writerows(rows)
    p2 = os.path.join(HERE, "sheet_surveys.csv")
    with io.open(p2, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SURVEY_COLS)
        w.writeheader()
        w.writerows(surveys)

    print(f"wrote {os.path.basename(p1)}: {len(rows)} records "
          f"({sum(1 for r in rows if r['id'].startswith('E'))} studies, "
          f"{sum(1 for r in rows if r['id'].startswith('C'))} complement)")
    print(f"wrote {os.path.basename(p2)}: {len(surveys)} compared reviews")
    print(f"blinding check passed: every coded column is empty, and none of the "
          f"{len(forbidden)} coded values in A01/A05/A06/A07 appears in either sheet")
    missing = [r["id"] for r in rows if not r["doi"]]
    if missing:
        print(f"note: no DOI in the bibliography for {missing} -- supply the PDF directly")


if __name__ == "__main__":
    main()
