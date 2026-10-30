#!/usr/bin/env python3
"""Generate fig_quality.svg: the per-study evidence-quality grid.

The 2026-10-29 review asks for a compact study-level display in the manuscript, because the ten
quality fields currently live mainly in the audit files and a reader cannot compare missing-data
handling, leakage, reproducibility or evaluated privacy across studies. It also forbids an
aggregate quality score, which would hide that the weaknesses are different ones.

Every glyph is derived here from A05, A06 and A07 by the published rule below -- nothing is typed
by hand. That is deliberate: the repository's own record of past errors is a list of cases where a
number in the manuscript no longer matched the cell behind it.

Two of the audit columns carry two constructs each ("Calibration; uncertainty" and a
reproducibility cell that reports data and code separately), so they are split rather than forced
into one glyph. That gives twelve fields.

    python3 make_fig_quality.py
"""
import csv, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
AUDIT = os.path.join(PKG, "audit")
OUT = os.path.join(HERE, "fig_quality.svg")

# state -> glyph
REPORTED, NOT_REPORTED, UNCLEAR, ABSTRACT = "reported", "not_reported", "unclear", "abstract"

FIELDS = [
    ("Split",            "A05", "Train and test split",        None),
    ("Leakage",          "A05", "Leakage risk",                None),
    ("Missing data",     "A05", "Missing data",                None),
    ("External val.",    "A05", "External validation",         None),
    ("Calibration",      "A06", "Calibration; uncertainty",    "calibration"),
    ("Uncertainty",      "A06", "Calibration; uncertainty",    "interval"),
    ("Subgroups",        "A06", "Fairness or subgroups",       None),
    ("Comparators",      "A06", "Comparators",                 None),
    ("Data available",   "A06", "Reproducibility",             "data"),
    ("Code available",   "A06", "Reproducibility",             "code"),
    ("Clinical val.",    "A06", "Clinical validation",         None),
    ("Privacy",          "A07", "Privacy or security method",  None),
]

FILES = {"A05": "A05_quality_split_leakage_missing_external.csv",
         "A06": "A06_quality_calibration_subgroups_comparators.csv",
         "A07": "A07_deployment_privacy_reporting.csv"}


def load(tag):
    rows = list(csv.DictReader(io.open(os.path.join(AUDIT, FILES[tag]), encoding="utf-8-sig")))
    return {re.sub(r"[\[\]]", "", r["BibTeX key"]).strip(): r for r in rows}


def classify(cell, part):
    """The published rule. `cell` is the audit value; `part` selects a sub-construct."""
    c = (cell or "").strip()
    if not c:
        return UNCLEAR
    low = c.lower()

    if part == "calibration":
        # the clause about calibration itself, not about intervals
        if "calibration n/r" in low or "calibration not" in low:
            return NOT_REPORTED
        if "brier" in low or "calibration" in low:
            return REPORTED
        return NOT_REPORTED
    if part == "interval":
        if re.search(r"\d+\s*%\s*(interval|bound|ci)|interval|bootstrap|posterior|credible|sd\b", low):
            return REPORTED
        if "no interval" in low or low.startswith("n/r"):
            return NOT_REPORTED
        return NOT_REPORTED
    if part == "data":
        if re.search(r"data(set)?\s+(public|on request|private|available)|public dataset|simulator licensed", low):
            return REPORTED
        return NOT_REPORTED if low.startswith("n/r") else UNCLEAR
    if part == "code":
        if "code n/r" in low:
            return NOT_REPORTED
        if "source code" in low or re.search(r"code\s+(public|released|available)", low):
            return REPORTED
        return NOT_REPORTED

    # single-construct fields
    if low in ("n/r", "n/a", "not reported", "-", "--"):
        return NOT_REPORTED
    if re.search(r"\?|unclear|not stated|cannot be determined", low):
        return UNCLEAR
    if low.startswith("n/r"):
        # "n/r; the authors note ..." -- the field itself is still not reported
        return NOT_REPORTED
    return REPORTED


def main():
    src = {t: load(t) for t in FILES}
    cross = list(csv.DictReader(io.open(os.path.join(AUDIT, "A08_study_id_crosswalk.csv"),
                                       encoding="utf-8-sig")))
    studies = [r for r in cross if r["id"].startswith("E")]
    studies.sort(key=lambda r: int(r["id"][1:]))

    # Nitski is the one record assessed from its abstract; the manuscript marks it with a section sign.
    ABSTRACT_ONLY = {"nitski2021long"}

    grid, missing = {}, []
    for r in studies:
        key, sid = r["bibtex_key"], r["id"]
        row = []
        for label, tag, col, part in FIELDS:
            rec = src[tag].get(key)
            if rec is None:
                missing.append((sid, tag))
                row.append(UNCLEAR)
            elif key in ABSTRACT_ONLY:
                row.append(ABSTRACT)
            else:
                row.append(classify(rec.get(col, ""), part))
        grid[sid] = row
    if missing:
        sys.exit(f"no audit row for {missing} -- refusing to draw a grid with invented cells")

    # ---- layout
    nrow, ncol = len(studies), len(FIELDS)
    cw, ch = 44, 17
    left, top = 146, 100   # the longest label is "E18 Thaipisutikul"
    W = left + ncol * cw + 18
    H = top + nrow * ch + 78
    F = "Helvetica Neue, Helvetica, Arial, sans-serif"
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    for j, (label, *_rest) in enumerate(FIELDS):
        x = left + j * cw + cw / 2
        s.append(f'<text x="{x}" y="{top-8}" font-family="{F}" font-size="11" fill="#141414" '
                 f'text-anchor="start" transform="rotate(-50 {x} {top-8})">{label}</text>')

    def glyph(x, y, st):
        cx, cy, r = x + cw / 2, y + ch / 2, 4.9
        if st == REPORTED:
            return (f'<rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" rx="1.2" '
                    f'fill="#2f5d8a"/>')
        if st == NOT_REPORTED:
            return (f'<rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" rx="1.2" '
                    f'fill="#ffffff" stroke="#9aa6b2" stroke-width="1.1"/>')
        if st == UNCLEAR:
            return (f'<rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" rx="1.2" '
                    f'fill="#ffffff" stroke="#9aa6b2" stroke-width="1.1"/>'
                    f'<path d="M {cx-r} {cy+r} L {cx+r} {cy-r}" stroke="#2f5d8a" stroke-width="1.6"/>')
        return (f'<rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" rx="1.2" '
                f'fill="#ffffff" stroke="#2f5d8a" stroke-width="1.1" stroke-dasharray="2.2 1.6"/>')

    for i, r in enumerate(studies):
        sid = r["id"]
        y = top + i * ch
        if i % 2 == 1:
            s.append(f'<rect x="{left}" y="{y}" width="{ncol*cw}" height="{ch}" fill="#f4f6f8"/>')
        label = re.sub(r"\$\^\{?\\\\?[a-zA-Z]+\}?\$|\\\\[a-zA-Z]+|[${}^]", "",
                       r["study_label"]).strip()
        s.append(f'<text x="{left-8}" y="{y+ch/2+4}" font-family="{F}" font-size="11.5" '
                 f'fill="#141414" text-anchor="end">{sid} {label}</text>')
        for j, st in enumerate(grid[sid]):
            s.append(glyph(left + j * cw, y, st))

    s.append(f'<line x1="{left}" y1="{top}" x2="{left+ncol*cw}" y2="{top}" stroke="#141414" stroke-width="1"/>')
    s.append(f'<line x1="{left}" y1="{top+nrow*ch}" x2="{left+ncol*cw}" y2="{top+nrow*ch}" '
             f'stroke="#141414" stroke-width="1"/>')

    ly = top + nrow * ch + 30
    for k, (st, text) in enumerate([(REPORTED, "reported"), (NOT_REPORTED, "not reported"),
                                    (UNCLEAR, "unclear"), (ABSTRACT, "abstract-only")]):
        x = left + k * 150
        s.append(glyph(x - cw / 2 + 6, ly - ch / 2, st))
        s.append(f'<text x="{x+20}" y="{ly+4}" font-family="{F}" font-size="11.5" '
                 f'fill="#141414">{text}</text>')

    s.append('</svg>')
    io.open(OUT, "w", encoding="utf-8").write("\n".join(s) + "\n")

    counts = {}
    for row in grid.values():
        for st in row:
            counts[st] = counts.get(st, 0) + 1
    print(f"wrote {os.path.basename(OUT)}: {nrow} studies x {ncol} fields = {nrow*ncol} glyphs")
    print("  " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    print("  no aggregate score is computed or drawn, by design")


if __name__ == "__main__":
    main()
