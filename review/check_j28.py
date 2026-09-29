#!/usr/bin/env python3
"""Acceptance check for Julia's five items of 2026-09-28.

One task per item of her email, each with concrete assertions against the live files:

    live/STmodel.tex      (submission build only; \\ifsubmission branches kept, extended dropped)
    live/supplement.tex
    review/search/ieee_screen.json
    endnote/out_j28/ieee_style_report.md

Run bare for a report, or --json for a Stop-hook payload. Exit 0 always.
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "live", "STmodel.tex")
SUPP = os.path.join(ROOT, "live", "supplement.tex")
IEEE_SCREEN = os.path.join(ROOT, "review", "search", "ieee_screen.json")
STYLE_REPORT = os.path.join(ROOT, "endnote", "out_j28", "ieee_style_report.md")


def read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def strip_comments(t):
    return re.sub(r"(?<!\\)%.*", "", t or "")


def submission_only(tex):
    tex = re.sub(r"\\newif\\if[a-zA-Z@]*", "", tex)
    out, pos, st = [], 0, []
    for m in re.finditer(r"\\(ifsubmission|if[a-zA-Z@]*|else|fi)\b", tex):
        w = m.group(1)
        if not any(x[0] and x[1] for x in st):
            out.append(tex[pos:m.start()])
        pos = m.end()
        if w.startswith("if"):
            st.append([w == "ifsubmission", False])
        elif w == "else":
            if st: st[-1][1] = True
        elif w == "fi":
            if st: st.pop()
    if not any(x[0] and x[1] for x in st):
        out.append(tex[pos:])
    return "".join(out)


def table_blocks(tex):
    """Every table environment in the file, as (label, block)."""
    out = []
    for m in re.finditer(r"\\begin\{(table\*?|longtable)\}", tex):
        end = tex.find("\\end{" + m.group(1) + "}", m.start())
        if end < 0:
            continue
        blk = tex[m.start():end]
        lab = re.search(r"\\label\{([^}]*)\}", blk)
        out.append((lab.group(1) if lab else "(unlabelled)", blk))
    return out


def max_columns(blk):
    """Widest data row of a table, counted by unescaped ampersands."""
    body = blk[blk.find("\\midrule"):] if "\\midrule" in blk else blk
    widest = 0
    for r in re.split(r"\\\\", body):
        if "&" not in r or "multicolumn" in r:
            continue
        widest = max(widest, len(re.findall(r"(?<!\\)&", r)) + 1)
    return widest


def check():
    main = re.sub(r"\s+", " ", submission_only(strip_comments(read(MAIN))))
    supp_raw = strip_comments(read(SUPP))
    supp = re.sub(r"\s+", " ", supp_raw)
    tasks = []

    def task(key, title, notes):
        tasks.append({"key": key, "title": title, "notes": [n for n in notes if n],
                      "done": not any(notes)})

    # ---- J28-1: exact search strings, dedup, 363 attribution, no Scopus ----
    task("J28-1", "Exact search strings, duplicate removal, 363 attributed, Scopus not mentioned", [
        None if '"spatio-temporal"[tiab]' in supp and "2015:2026[dp]" in supp
             else "supplement does not print the exact PubMed string",
        None if '"Document Title":spatiotemporal' in supp
             else "supplement does not print the exact IEEE Xplore string",
        None if re.search(r"3 on both, giving", main)
             else "main text does not explain duplicate removal across the two arms",
        None if "from the PubMed screen" in main
             else "main text does not attribute the 363 eligible records to the PubMed screen",
        f"main text still mentions Scopus ({main.count('Scopus')}x)" if "Scopus" in main else None,
    ])

    # ---- J28-2: IEEE records screened under the same criteria ----
    notes = []
    if not os.path.exists(IEEE_SCREEN):
        notes.append("review/search/ieee_screen.json does not exist: IEEE records not screened")
    else:
        try:
            d = json.load(open(IEEE_SCREEN))
        except Exception as e:
            d = {}
            notes.append(f"ieee_screen.json is not readable: {e}")
        for arm in ("arm_a", "arm_b"):
            a = (d or {}).get(arm)
            if not isinstance(a, dict):
                notes.append(f"ieee_screen.json has no {arm} block")
                continue
            for f in ("records", "screened_on_title_abstract", "eligible"):
                if f not in a:
                    notes.append(f"{arm} is missing the {f} count")
        if "deduplicated_against_pubmed" not in (d or {}):
            notes.append("ieee_screen.json does not record deduplication against the PubMed set")
    if not re.search(r"IEEE Xplore records", supp):
        notes.append("supplement has no section reporting the IEEE Xplore screen")
    if "without the same record-level screen" in main:
        notes.append("main text still says the IEEE arm was not screened at record level")
    task("J28-2", "IEEE Xplore records screened and deduplicated under the same criteria", notes)

    # ---- J28-3: her replacement sentence, verbatim ----
    task("J28-3", "Federated-learning sentence replaced with her wording", [
        None if "Federated learning sends model updates rather than raw data" in main
             else "her replacement sentence is not in the main text",
        None if "transport encryption, secure aggregation, and differential privacy must be implemented separately" in main
             else "the second half of her sentence is missing",
        "the inaccurate 'encrypted updates' wording is still present" if "encrypted updates" in main else None,
    ])

    # ---- J28-4: Table II trimmed, widest supplement tables split ----
    notes = []
    ev = [b for lab, b in table_blocks(submission_only(strip_comments(read(MAIN))))
          if lab == "tab:evidence"]
    if not ev:
        notes.append("Table II (tab:evidence) not found in the submission build")
    else:
        w = max_columns(ev[0])
        if w > 6:
            notes.append(f"Table II still has {w} columns; keep at most 6")
    wide = [(lab, max_columns(b)) for lab, b in table_blocks(supp_raw) if max_columns(b) > 7]
    for lab, w in wide:
        notes.append(f"supplement table {lab} has {w} columns; split it (at most 7)")
    task("J28-4", "Table II trimmed and the widest supplement tables split", notes)

    # ---- J28-5: every cited reference verified and IEEE-styled ----
    notes = []
    if not os.path.exists(STYLE_REPORT):
        notes.append("endnote/out_j28/ieee_style_report.md does not exist")
    else:
        rep = read(STYLE_REPORT)
        m = re.search(r"outstanding\s*[:=]\s*(\d+)", rep, re.I)
        if not m:
            notes.append("the style report does not state an outstanding count")
        elif int(m.group(1)) != 0:
            notes.append(f"{m.group(1)} cited entries still fall short of IEEE style")
        if not re.search(r"documented exemption", rep, re.I):
            notes.append("the style report does not list the documented exemptions")
    task("J28-5", "Every cited reference verified against the publisher record and IEEE-styled", notes)

    return tasks


def main_cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    tasks = check()
    done = [t for t in tasks if t["done"]]

    if a.json:
        if len(done) == len(tasks):
            msg = f"Julia 09-28: all {len(tasks)} items satisfied."
        else:
            msg = (f"Julia 09-28: {len(done)}/{len(tasks)} done | outstanding: "
                   + "; ".join(f"{t['key']} ({t['notes'][0]})" for t in tasks if not t["done"]))
        print(json.dumps({"systemMessage": msg, "suppressOutput": True}))
        return

    for t in tasks:
        print(("[DONE    ] " if t["done"] else "[not done] ") + f"{t['key']}  {t['title']}")
        for n in t["notes"]:
            print(f"             - {n}")
    print(f"\n{len(done)} of {len(tasks)} items satisfied")


if __name__ == "__main__":
    main_cli()
