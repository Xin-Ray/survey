#!/usr/bin/env python3
"""Acceptance check for the nine remaining updates of 2026-10-01, plus the grant update.

One task per item of the review. Each asserts against the live files or the
screening records, never against a task list of our own:

    live/STmodel.tex                        (submission build only)
    live/supplement.tex
    review/search/ieee_screen.json
    review/search/query_expansion_check.json
    endnote/out_j28/strict_refcheck.md

Run bare for a report, or --json for a Stop-hook payload. Exit 0 always.
"""
import argparse, json, os, re, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "live", "STmodel.tex")
SUPP = os.path.join(ROOT, "live", "supplement.tex")
SCREEN = os.path.join(ROOT, "review", "search", "ieee_screen.json")
QEXP = os.path.join(ROOT, "review", "search", "query_expansion_check.json")
REFCHK = os.path.join(ROOT, "endnote", "out_j28", "strict_refcheck.md")

_s = importlib.util.spec_from_file_location("cc", os.path.join(ROOT, "review", "check_comments.py"))
cc = importlib.util.module_from_spec(_s); _s.loader.exec_module(cc)


def read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def table_rows(tex, label):
    """Data rows of the float carrying this label, as lists of cells."""
    try:
        i = tex.index("\\label{" + label + "}")
    except ValueError:
        return None
    s = tex.rindex("\\begin{table*}", 0, i)
    e = tex.index("\\end{table*}", i)
    blk = tex[s:e]
    body = blk[blk.index("\\midrule"):blk.index("\\bottomrule")]
    rows = [[c.strip() for c in re.split(r"(?<!\\)&", r)]
            for r in re.split(r"\\\\", body) if "&" in r and "multicolumn" not in r]
    widest = max((len(r) for r in rows), default=0)
    return [r for r in rows if len(r) == widest]


def check():
    main_raw = cc.submission_only(cc.strip_comments(read(MAIN)))
    prose = re.sub(r"\s+", " ", main_raw)
    supp_raw = cc.strip_comments(read(SUPP))
    supp = re.sub(r"\s+", " ", supp_raw)
    tasks = []

    def task(key, title, notes):
        notes = [n for n in notes if n]
        tasks.append({"key": key, "title": title, "notes": notes, "done": not notes})

    screen = json.load(open(SCREEN)) if os.path.exists(SCREEN) else {}

    # ---- O1: the three PubMed snapshots reconciled, and the one used named ----
    task("O1", "Three PubMed snapshots reconciled and the one used for dedup named", [
        None if all(n in supp for n in ("1{,}436", "1{,}444", "1{,}456"))
             else "the supplement does not carry all three totals",
        None if all(d in supp for d in ("11 September 2026", "29 September 2026"))
             else "the supplement does not date every snapshot",
        None if re.search(r"29 September[^.]{0,200}cross-database|cross-database[^.]{0,200}29 September", supp)
             else "the supplement does not say which snapshot the cross-database comparison used",
        None if re.search(r"conservative|can only reduce|upper bound on the Xplore-only", supp)
             else "the supplement does not say that the larger comparison set is the conservative choice",
    ])

    # ---- O2: fully expanded, paste-ready strings, verified against the block form ----
    notes = []
    # only the expanded single string carries the year limit joined on with AND;
    # the block form lists Y on its own line
    if not re.search(r"wearables\[tiab\]\) AND 2015:2026\[dp\]", supp):
        notes.append("the supplement does not print a fully expanded, paste-ready PubMed string")
    if not re.search(r'"world models"\[tiab\]\) AND', supp):
        notes.append("the digital-twin arm is not printed in expanded form")
    if not os.path.exists(QEXP):
        notes.append("review/search/query_expansion_check.json does not exist: the expanded "
                     "string was never checked against the block form")
    else:
        try:
            q = json.load(open(QEXP))
            for arm in ("main", "dtwm"):
                a = q.get(arm) or {}
                if a.get("blocks") != a.get("expanded"):
                    notes.append(f"{arm}: block form returns {a.get('blocks')} but the expanded "
                                 f"string returns {a.get('expanded')}")
        except Exception as e:
            notes.append(f"query_expansion_check.json is not readable: {e}")
    task("O2", "Fully expanded paste-ready PubMed strings, verified against the block form", notes)

    # ---- O3: normalization and duplicate-retention rules stated ----
    task("O3", "Title normalization and duplicate-retention rules stated", [
        None if re.search(r"lower ?cas\w+[^.]{0,120}non-alphanumeric|non-alphanumeric[^.]{0,120}lower", supp, re.I)
             else "the supplement does not state how titles are normalized",
        None if re.search(r"first occurrence|the earlier record is kept|keeps the first", supp, re.I)
             else "the supplement does not state which duplicate is retained",
        None if re.search(r"DOI[^.]{0,120}(case|lower)", supp, re.I)
             else "the supplement does not state how DOIs are compared",
    ])

    # ---- O4: IEEE reviews excluded, and every downstream number regenerated ----
    notes = []
    rev = (screen or {}).get("reviews_excluded")
    if not isinstance(rev, dict):
        notes.append("ieee_screen.json has no reviews_excluded block: the review rule was not run")
    else:
        for f in ("rule", "arm_a", "arm_b", "total"):
            if f not in rev:
                notes.append(f"reviews_excluded is missing {f}")
    if screen:
        dd = screen.get("deduplicated_against_pubmed") or {}
        elig = screen.get("eligible_unique_within_ieee")
        only = dd.get("ieee_only")
        if elig is not None and str(elig) not in prose:
            notes.append(f"the prose does not carry the recomputed eligible count {elig}")
        if only is not None:
            if str(only) not in prose:
                notes.append(f"the prose does not carry the recomputed IEEE-only count {only}")
            if str(363 + only) not in prose:
                notes.append(f"the prose does not carry the recomputed pool {363 + only}")
    if not re.search(r"no publication-type metadata|carries no review flag|textual rule", supp, re.I):
        notes.append("the supplement does not state the residual asymmetry with the PubMed screen")
    task("O4", "IEEE review articles excluded and every downstream number regenerated", notes)

    # ---- O5: the ten synthesized studies came from the PubMed pool ----
    task("O5", "The ten sampled studies are attributed to the PubMed pool, not the combined pool", [
        None if re.search(r"363 PubMed rule-eligible|PubMed rule-eligible records", prose)
             else "the prose does not say the ten came from the PubMed rule-eligible records",
        None if re.search(r"contributed no study to Table|after the synthesized set was fixed", prose)
             else "the prose does not say the IEEE arm contributed nothing to Table II",
    ])

    # ---- O6: Table II trimmed to five columns, cells shortened ----
    notes = []
    rows = table_rows(main_raw, "tab:evidence")
    if rows is None:
        notes.append("Table II not found in the submission build")
    else:
        ncol = len(rows[0]) if rows else 0
        if ncol > 5:
            notes.append(f"Table II still has {ncol} columns; keep at most 5")
        if ncol:
            longest = max(len(c) for r in rows for c in r[1:])
            if longest > 52:
                notes.append(f"the longest Table II cell is {longest} characters; keep at most 52")
    if "Deployment: reported / ours" in prose:
        notes.append("the deployment column is still in Table II")
    task("O6", "Table II trimmed to five columns with shorter cells", notes)

    # ---- O7: the supplement packs its pages and uses a readable size ----
    notes = []
    if "dblfloatpagefraction" not in supp_raw:
        notes.append("the supplement preamble still has no float parameters, so a float page "
                     "need only be half full")
    # the table BODY size is the \scriptsize on a line of its own; the smaller size
    # inside a note row is deliberate and stays one step below the body
    n_script = len(re.findall(r"(?m)^\\scriptsize$", supp_raw))
    if n_script:
        notes.append(f"{n_script} supplement table(s) still set \\scriptsize for the body")
    n_bang = len(re.findall(r"\\begin\{table\*\}\[!?t\]", supp_raw))
    if n_bang:
        notes.append(f"{n_bang} float(s) are still top-only; allow [tbp] so text can flow around them")
    task("O7", "Supplement pages pack properly and tables are set at a readable size", notes)

    # ---- O8: references complete and verified ----
    notes = []
    if not os.path.exists(REFCHK):
        notes.append("endnote/out_j28/strict_refcheck.md does not exist")
    else:
        r = read(REFCHK)
        m = re.search(r"entries with a discrepancy:\s*\*\*(\d+)\*\*", r)
        if not m:
            notes.append("the strict reference report does not state a discrepancy count")
        elif int(m.group(1)):
            notes.append(f"{m.group(1)} cited entries still disagree with the publisher record")
        # Four entries can never be compared against a publisher record, each for a
        # reason that is stated in the report. Naming them keeps the exemption honest:
        # a fifth uncompared entry fails this check instead of hiding in a count.
        EXPECTED = {"ieee11073std", "Fang2021iPAT", "rumelhart1986rnn", "goodfellow2014gan"}
        listed = set(re.findall(r"^- \[\d+\] `([^`]+)`", r, re.M))
        extra = listed - EXPECTED
        if extra:
            notes.append(f"entries with no record compared that are not on the documented "
                         f"exemption list: {sorted(extra)}")
        for k in listed:
            if not re.search(r"`" + re.escape(k) + r"` — \S", r):
                notes.append(f"{k} is uncompared with no reason given")
    # The strict checker cannot see these: entries with no publisher record are skipped,
    # so a lost edit to them is invisible to it. Two of these edits were silently lost
    # twice on 2026-10-01 when a patch script aborted before writing. Assert the fields.
    bibtxt = read(os.path.join(ROOT, "live", "newST.bib"))
    def has(key, needle):
        m = re.search(r"@\w+\{" + re.escape(key) + r",(.*?)\n\}", bibtxt, re.S)
        return bool(m and needle in m.group(1))
    for key, needle, what in (
            ("zhou2022fedformer", "27268--27286", "ICML pages"),
            ("zhou2022fedformer", "{162}", "ICML volume"),
            ("tonekaboni2019clinicians", "359--380", "MLHC pages"),
            ("tonekaboni2019clinicians", "{106}", "MLHC volume"),
            ("rubanova2019latent", "{32}", "NeurIPS volume"),
            ("samani2026stdl", "online ahead of issue", "online-first note"),
            ("caroprese2018deepehr", "Proc. 9th Int. Conf.", "IISA name in the common style")):
        if not has(key, needle):
            notes.append(f"{key} is missing its {what}")
    task("O8", "Every cited reference complete and checked against a publisher record", notes)

    # ---- O9: grants ----
    task("O9", "Grant acknowledgment updated", [
        None if "R56DK114514" in prose else "R56DK114514-01 is missing",
        None if "R01DK129432" in prose else "R01DK129432 is missing",
        None if "2428595" in prose else "NSF Award 2428595 is missing",
        None if re.search(r"National Science Foundation", prose) else "NSF is not named",
    ])

    return tasks


def main_cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    tasks = check()
    done = [t for t in tasks if t["done"]]

    if a.json:
        if len(done) == len(tasks):
            msg = f"Review 10-01: all {len(tasks)} items satisfied."
        else:
            msg = (f"Review 10-01: {len(done)}/{len(tasks)} done | outstanding: "
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
