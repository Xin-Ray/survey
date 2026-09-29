#!/usr/bin/env python3
"""Split the four widest supplement tables by columns, keeping their S-numbers.

Julia's fourth point of 2026-09-28 asks for the widest supplementary tables to be
broken into smaller ones. S2 and S3 carry 11 columns each and S4 and S5 carry 10,
which is what makes them unreadable. Each becomes two panels, a and b, sharing the
study or dataset column; the table counter is frozen across the pair and stamped
locally, so S2 becomes S2a and S2b and every later table keeps the number the main
paper already cites.

    python3 review/split_wide_tables.py            # rewrites live/supplement.tex
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUPP = os.path.join(ROOT, "live", "supplement.tex")

# label -> (S-number, panel a columns by index, panel a spec, b columns, b spec,
#           panel a caption tail, panel b caption tail)
PLAN = {
    "tab:datasets": (
        "S2", [0, 1, 2, 3, 4, 5], r"L{2.5cm} L{2.6cm} L{2.4cm} L{2.8cm} L{2.9cm} X",
        [0, 6, 7, 8, 9, 10], r"L{2.5cm} L{3.4cm} L{2.2cm} L{2.9cm} L{0.75cm} X",
        "population, modality, device, sampling and spatial unit",
        "missingness, access, supported tasks, suitability and principal limitation"),
    "tab:datasets-b": (
        "S4", [0, 1, 2, 3, 4, 5], r"L{2.5cm} L{2.6cm} L{2.4cm} L{2.8cm} L{2.9cm} X",
        [0, 6, 7, 8, 9, 10], r"L{2.5cm} L{3.4cm} L{2.2cm} L{2.9cm} L{0.75cm} X",
        "population, modality, device, sampling and spatial unit",
        "missingness, access, supported tasks, suitability and principal limitation"),
    "tab:quality": (
        "S3", [0, 1, 2, 3, 4], r"L{2.6cm} L{3.6cm} L{3.2cm} L{3.4cm} X",
        [0, 5, 6, 7, 8, 9], r"L{2.6cm} L{3.7cm} L{2.4cm} L{3.0cm} L{2.5cm} X",
        "split, leakage risk, missing data and external validation",
        "calibration and uncertainty, subgroups, comparators, reproducibility and clinical validation"),
    "tab:quality-b": (
        "S5", [0, 1, 2, 3, 4], r"L{2.6cm} L{3.6cm} L{3.2cm} L{3.4cm} X",
        [0, 5, 6, 7, 8, 9], r"L{2.6cm} L{3.7cm} L{2.4cm} L{3.0cm} L{2.5cm} X",
        "split, leakage risk, missing data and external validation",
        "calibration and uncertainty, subgroups, comparators, reproducibility and clinical validation"),
}


def float_extent(t, label):
    """(start, end) of the table* float carrying this label."""
    i = t.index("\\label{" + label + "}")
    start = t.rindex("\\begin{table*}", 0, i)
    end = t.index("\\end{table*}", i) + len("\\end{table*}")
    return start, end


def cells(row):
    return [c.strip() for c in re.split(r"(?<!\\)&", row)]


def split_rows(body):
    """Data rows of the table body, each as a list of cells, plus the note rows."""
    body = body[body.index("\\midrule") + len("\\midrule"):]
    if "\\end{tabularx}" in body:
        body = body[:body.index("\\end{tabularx}")]
    note = ""
    if "\\bottomrule" in body:
        body, note = body.split("\\bottomrule", 1)
    rows = [r.strip() for r in re.split(r"\\\\", body)]
    return [cells(r) for r in rows if r and "&" in r], note.strip()


def build(label, num, panel, cols, spec, caption, tail, rows, note, width):
    head = [r"\begin{table*}[!t]", r"\centering"]
    if panel == "b":
        # the pair occupies one number: undo the step panel a's caption made
        head.append(r"\addtocounter{table}{-1}")
    head += [r"\renewcommand{\thetable}{" + num + panel + r"}",
            r"\caption{" + caption + " Panel " + panel + ": " + tail + r".}",
            r"\label{tab:" + num + panel + r"}",
            r"\scriptsize", r"\setlength{\tabcolsep}{2.5pt}",
            r"\renewcommand{\arraystretch}{1.05}",
            r"\begin{tabularx}{\textwidth}{" + spec + "}", r"\toprule"]
    hdr = [rows[0][i] for i in cols]
    head.append(" & ".join(hdr) + r" \\")
    head.append(r"\midrule")
    for r in rows[1:]:
        if len(r) == 1 or "multicolumn" in r[0]:
            continue
        head.append(" & ".join(r[i] if i < len(r) else "" for i in cols) + r" \\")
    head.append(r"\bottomrule")
    if note:
        n = re.sub(r"\\multicolumn\{\d+\}", r"\\multicolumn{" + str(len(cols)) + "}", note)
        head.append(n.rstrip().rstrip("\\").rstrip() if n.strip().endswith("\\\\") else n)
    head += [r"\end{tabularx}", r"\end{table*}"]
    return "\n".join(head)


def main():
    t = open(SUPP, encoding="utf-8").read()
    if "tab:S2a}" in t:
        sys.exit("already split; nothing to do")


    for label in ("tab:quality-b", "tab:quality", "tab:datasets-b", "tab:datasets"):
        num, ca, sa, cb, sb, ta, tb = PLAN[label]
        s, e = float_extent(t, label)
        blk = t[s:e]
        m = re.search(r"\\caption\{(.*?)\}\s*\n\s*\\label", blk, re.S)
        caption = m.group(1).strip()
        # the header row lives between \toprule and \midrule
        hdr = blk[blk.index("\\toprule") + 8: blk.index("\\midrule")]
        hdr = [c.strip() for c in re.split(r"(?<!\\)&", hdr.strip().rstrip("\\").strip())]
        body_rows, note = split_rows(blk)
        rows = [hdr] + body_rows
        ncol = len(hdr)
        assert max(max(ca), max(cb)) < ncol, (label, ncol)

        new = (build(label, num, "a", ca, sa, caption, ta, rows, note, ncol) + "\n\n"
               + build(label, num, "b", cb, sb, caption, tb, rows, note, ncol))
        t = t[:s] + new + t[e:]
        print(f"{label}: {ncol} cols, {len(body_rows)} rows -> {num}a ({len(ca)}) + {num}b ({len(cb)})")

    open(SUPP, "w", encoding="utf-8").write(t)


if __name__ == "__main__":
    main()
