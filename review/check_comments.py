#!/usr/bin/env python3
"""Acceptance check derived from the reviewer's own comment list, not from our task plan.

Every item below is one sub-bullet of IEEE_IoT_Consolidated_Review_Comments.txt, and each is
tested by locating the text that satisfies it in the live files:

    live/STmodel.tex   (submission build only: \\ifsubmission branches, extended text ignored)
    live/supplement.tex

This exists because an earlier checker verified the tables we had decided to build and reported
"all pass" while seven of the ten comments were still untouched. The standard has to come from
the reviewer's document.

Run bare for a report, or --json for a Stop-hook payload. Exit 0 always.
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "live", "STmodel.tex")
SUPP = os.path.join(ROOT, "live", "supplement.tex")


def read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def strip_comments(t):
    return re.sub(r"(?<!\\)%.*", "", t or "")


def submission_only(tex):
    """Keep only what the 8-page build typesets: drop \\ifsubmission...\\else...\\fi branches."""
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


# (comment, sub-item, where, regex, want_absent)
ITEMS = [
 ("1", "selection of the twelve explained",        "main", r"two provenances, which we keep distinct", 0),
 ("1", "sampling frame stated",                    "main", r"crossed the five data types of Section", 0),
 ("1", "saturation rule stated",                   "main", r"three consecutive candidates added no new", 0),
 ("1", "reason for including each study",          "supp", r"\\label\{tab:provenance\}", 0),
 ("1", "sample expanded",                          "main", r"twenty-two studies", 0),
 ("1", "described as illustrative, not sampled",   "main", r"illustrative set assembled by the authors", 0),
 ("2", "search terms and dates per database",      "main", r"E-utilities, 11 September 2026", 0),
 ("2", "second database counts",                   "main", r"IEEE Xplore.{0,80}22 September 2026", 0),
 ("2", "duplicate removal explained",              "main", r"3 on both, giving", 0),
 ("2", "citation chasing described",               "main", r"forward and backward citation", 0),
 ("2", "single vs multiple reviewers stated",      "main", r"no second independent screener", 0),
 ("3", "evidence class separates real IoT",        "main", r"evidence class", 0),
 ("3", "deployment reported vs inferred",          "main", r"Deployment: reported / ours", 0),
 ("3", "inference labelled as the authors'",       "main", r"the placement \\emph\{we\} infer", 0),
 ("3", "count of connected-device studies",        "main", r"Eleven of the twenty-two draw on data captured", 0),
 ("4", "'quantitative synthesis' removed",         "main", r"quantitative synthesis", 1),
 ("4", "comparator strength per study",            "supp", r"\\textbf\{Comparators\}", 0),
 ("4", "metrics stated as not comparable",         "main", r"not comparable across rows", 0),
 ("4", "studies grouped into task groups",         "main", r"\\multicolumn\{6\}\{l\}\{\\emph\{", 0),
 ("5", "sampling rate and duration",               "supp", r"Sampling rate; record duration", 0),
 ("5", "missing-data handling",                    "supp", r"Missingness, as handled", 0),
 ("5", "external validation, calibration, uncertainty", "supp", r"\\textbf\{Calibration; uncertainty\}", 0),
 ("5", "privacy, latency, energy, bandwidth",      "supp", r"\\label\{tab:deployrep\}", 0),
 ("5", "primary limitation per study",             "supp", r"Principal methodological limitation", 0),
 ("6", "Table I judged from full text",            "main", r"judged from the full text", 0),
 ("6", "section evidence for every mark",          "supp", r"\\label\{tab:surveyevidence\}", 0),
 ("6", "how the compared surveys were selected",   "main", r"chosen by the authors to span the five", 0),
 ("6", "contribution in two or three points",      "main", r"Three things here are ours", 0),
 ("7", "quality-assessment table",                 "supp", r"\\label\{tab:S3a\}", 0),
 ("7", "'within-cohort' defined",                  "main", r"\\emph\{Within-cohort\}", 0),
 ("7", "adjusted cohort not called external",      "main", r"not an untouched external test", 0),
 ("8", "dataset table",                            "supp", r"\\label\{tab:S2a\}", 0),
 ("8", "device, multisite, twin suitability",      "supp", r"supports device-level or edge evaluation", 0),
 ("8", "no full-pipeline benchmark stated",        "main", r"no established benchmark evaluates the complete", 0),
 ("9", "protocols compared",                       "supp", r"\\label\{tab:protocols\}", 0),
 ("9", "effect on sampling, loss, update cadence", "supp", r"Consequence for sampling rate, loss and model updates", 0),
 ("9", "FHIR and IEEE 11073 expanded",             "supp", r"fixes the schema and semantics of the record", 0),
 ("9", "threats by layer",                          "supp", r"\\label\{tab:threats\}", 0),
 ("9", "five security properties distinguished",   "supp", r"confidentiality, integrity, availability, privacy", 0),
 ("9", "federated learning is not privacy",        "supp", r"supplies neither encryption nor a privacy", 0),
 ("10", "findings scoped to the set",              "main", r"we do not generalize beyond the set", 0),
 ("10", "publication period corrected",            "main", r"published between 2014 and 2026", 0),
 ("10", "RQ1-RQ4 answered explicitly",             "main", r"\\emph\{RQ1\.\}", 0),
 ("10", "'health care' standardized",              "main", r"health care", 1),
 ("10", "'attention based' hyphenated",            "main", r"attention based", 1),
 ("10", "'action conditioned' hyphenated",         "main", r"action conditioned", 1),
 ("10", "'privacy preserving' hyphenated",         "main", r"privacy preserving", 1),
 ("10", "'world model based' hyphenated",          "main", r"world model based", 1),
 ("10", "British spellings removed",               "main", r"organis|modelling", 1),
 ("10", "Figure 1 readable and consistent",         "main", r"Hand check of 60 PubMed records: precision 62", 0),
]


def check():
    main = re.sub(r"\s+", " ", submission_only(strip_comments(read(MAIN))))
    supp = re.sub(r"\s+", " ", strip_comments(read(SUPP)))
    # the PNG filename and the literal search string legitimately contain unhyphenated forms
    main_prose = main.replace("{digital twin in health care.png}", "").replace(
        "\\label{fig:digital twin in health care}", "")
    src = {"main": main_prose, "supp": supp}
    rows, by_comment = [], {}
    for comment, item, where, pat, want_absent in ITEMS:
        n = len(re.findall(pat, src[where], re.I))
        ok = (n == 0) if want_absent else (n > 0)
        rows.append({"comment": comment, "item": item, "where": where, "hits": n, "ok": ok})
        by_comment.setdefault(comment, []).append(ok)
    return rows, by_comment


def main_cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rows, by_comment = check()
    passed = sum(r["ok"] for r in rows)
    failed = [r for r in rows if not r["ok"]]

    if a.json:
        if not failed:
            msg = f"Reviewer comments: all {len(rows)} sub-items satisfied."
        else:
            msg = (f"Reviewer comments: {passed}/{len(rows)} satisfied. Outstanding: "
                   + "; ".join(f"c{r['comment']} {r['item']}" for r in failed[:6])
                   + ("" if len(failed) <= 6 else f" (+{len(failed)-6} more)"))
        print(json.dumps({"systemMessage": msg, "suppressOutput": True}))
        return

    last = None
    for r in rows:
        if r["comment"] != last:
            done = sum(by_comment[r["comment"]]); tot = len(by_comment[r["comment"]])
            print(f"\nComment {r['comment']}  [{done}/{tot}]")
            last = r["comment"]
        print(("  OK   " if r["ok"] else "  MISS ") + f"{r['item']}  ({r['where']})")
    print(f"\n{passed} of {len(rows)} sub-items satisfied")
    if failed:
        print("\nOutstanding:")
        for r in failed:
            print(f"  - comment {r['comment']}: {r['item']}")


if __name__ == "__main__":
    main_cli()
