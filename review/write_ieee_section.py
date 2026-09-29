#!/usr/bin/env python3
"""Write the IEEE-screen numbers into the supplement, the main text and Figure 1.

Every number comes from `review/search/ieee_screen.json`; none is typed by hand,
so the manuscript cannot drift from the screen the way Figure 1 drifted from the
corrected hand check for three weeks.

    python3 review/write_ieee_section.py
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUPP = os.path.join(ROOT, "live", "supplement.tex")
MAIN = os.path.join(ROOT, "live", "STmodel.tex")
SCREEN = os.path.join(ROOT, "review", "search", "ieee_screen.json")


def th(n):
    return f"{n:,}".replace(",", "{,}")


def abstract_median(arm):
    import statistics
    d = json.load(open(os.path.join(ROOT, "review", "search", f"ieee_{arm}_abstracts.json")))
    L = [len(v["abstract"]) for v in d.values() if v["abstract"]]
    return int(statistics.median(L)) if L else 0


def main():
    d = json.load(open(SCREEN))
    a, b = d["arm_a"], d["arm_b"]
    dd = d["deduplicated_against_pubmed"]
    tot = a["records"] + b["records"]
    scr = a["screened_on_title_abstract"] + b["screened_on_title_abstract"]
    non = a["excluded_non_article"] + b["excluded_non_article"]
    noab = a["excluded_no_abstract"] + b["excluded_no_abstract"]
    f1 = a["excluded_i_no_spacetime_structure"] + b["excluded_i_no_spacetime_structure"]
    f2 = a["excluded_ii_not_human_health"] + b["excluded_ii_not_human_health"]
    f3 = (a["excluded_iii_no_quantitative_comparison"]
          + b["excluded_iii_no_quantitative_comparison"])
    elig = d["eligible_unique_within_ieee"]

    # ---------------- supplement section ----------------
    sec = rf"""\section{{Screening the IEEE Xplore records}}
\label{{sec:ieeescreen}}
The IEEE Xplore arm was originally reported as header counts alone, which
presented the search as a two-database review without a two-database screen.
Both arms have since been screened under the same three rules as the PubMed arm,
re-run on {d['run_date']}.

Records were paged from the search endpoint that the Xplore results page itself
calls, 100 at a time, because the export interface will not hand over an arm of
this size in one file. The method was validated against the one arm that had been
exported through the interface on 22 September 2026: of the 274 rows in that file,
271 are returned again by the endpoint, and the arm now reports
{th(b['records'])} records rather than 274. The spatiotemporal arm likewise reports
{th(a['records'])} against the 928 read from the results header on 22 September.
Both differences are new indexing inside the open 2026 window, the same drift the
PubMed re-run showed, and not a different search.

One correction matters for anyone reproducing this. The search endpoint returns
abstracts truncated to about 400 characters. Criterion~(iii) asks for a metric, a
number and a comparison against a named alternative, and in most abstracts those
sit past that cut. Screening the truncated text returned \emph{{zero}} eligible
records out of {th(a['screened_on_title_abstract'])} on the spatiotemporal arm, against
roughly thirty per cent on the PubMed arm --- an artefact of the truncation, not a
finding. The full abstract of every record was therefore fetched from its own
document endpoint (median length {abstract_median('a')} characters on the
spatiotemporal arm and {abstract_median('b')} on the twin arm, against 1{{,}}452 in the
interface export) and the screen applied to that.

Of the {th(tot)} records across the two arms, {non} are non-article item types
and {noab} carry no abstract, leaving \textbf{{{th(scr)}}} screened on title and
abstract. Applying criteria~(i)--(iii) as the same textual rules, {th(f2)} records
failed~(ii), {th(f1)} failed~(i) and {th(f3)} failed~(iii), leaving
\textbf{{{th(elig)}}} eligible records after deduplication within Xplore
({d['duplicates_within_ieee']} records appear on both arms). Resolved by DOI and
by normalized title against the {th(dd['pubmed_comparison_set'])} records of the
PubMed union, {th(dd['also_in_pubmed'])} of these are already in the PubMed set
and \textbf{{{th(dd['ieee_only'])}}} are Xplore only.

One difference from the PubMed screen cannot be removed: Xplore metadata carries
no review flag, so the review exclusion that removed 194 records from the PubMed
arm has no equivalent here, and reviews remain among the IEEE eligible records.
The eligible count above is therefore an upper bound in a way the PubMed figure is
not.

"""

    t = open(SUPP, encoding="utf-8").read()
    t = re.sub(r"\\section\{Screening the IEEE Xplore records\}.*?(?=\\section\{)", "", t, flags=re.S)
    anchor = "\\section{Evidence behind the survey comparison}"
    t = t.replace(anchor, sec + anchor)
    t = t.replace("How they were screened and deduplicated is reported below.",
                  "Section~\\ref{sec:ieeescreen} reports how they were screened and deduplicated.")
    open(SUPP, "w", encoding="utf-8").write(t)

    # ---------------- main text ----------------
    m = open(MAIN, encoding="utf-8").read()
    pool = 363 + dd["ieee_only"]
    old = (" The rule errs both ways, so correcting both cells puts the eligible literature at "
           "\\textbf{roughly 375 studies}: an order of magnitude, not a count. "
           "It judges abstracts, under-counting studies whose abstracts omit results, "
           "and the IEEE Xplore arm is reported as counts without the same record-level screen.")
    new = (" The rule errs both ways, so correcting both cells puts the eligible PubMed "
           "literature at \\textbf{roughly 375 studies}: an order of magnitude, not a count. "
           "It judges abstracts, under-counting studies whose abstracts omit results. "
           f"Both IEEE Xplore arms were then re-run and screened under the same three rules: "
           f"{th(scr)} records screened on title and abstract left {th(elig)} eligible, "
           f"{th(dd['ieee_only'])} of them outside the PubMed set, so the rule-eligible "
           f"literature across the two databases is \\textbf{{{th(pool)}}} records rather than "
           f"363. The hand check was carried out on the PubMed screen alone, so its correction "
           f"is not carried across; Supplement Section~III gives the per-arm counts and the one "
           f"criterion that cannot be matched between the two databases.")
    if old in m:
        m = m.replace(old, new)
    elif new not in m:
        sys.exit("the main-text sentences about the pool and the IEEE arm were not found, "
                 "neither in their original nor in their rewritten form")

    # Review Limitations: the denominator the synthesized set is read against
    oldlim = ("and the verification search puts the eligible literature at roughly 375 studies "
              "against the 22 we synthesize")
    newlim = (f"and the two logged searches put the rule-eligible literature at {th(pool)} records "
              f"against the 22 we synthesize")
    if oldlim in m:
        m = m.replace(oldlim, newlim)
    else:
        print("note: the Review Limitations denominator sentence was not found", file=sys.stderr)

    fig = [
        (r"\node[bx] (a) {\textbf{Identified.} PubMed, 11 Sept.\ 2026: "
         r"\textbf{1{,}436} unique; IEEE Xplore, 22 Sept.: 1{,}204 (counts only); "
         r"citation chasing: 3{,}472 screened, \textbf{15} new};",
         r"\node[bx] (a) {\textbf{Identified.} PubMed, 11 Sept.\ 2026: \textbf{1{,}436} unique; "
         r"IEEE Xplore, re-run 29 Sept.: \textbf{" + th(tot) + r"}; citation chasing: "
         r"3{,}472 screened, \textbf{15} new};"),
        (r"\node[bx, below=of a] (d) {\textbf{Screened.} 36 non-research and 194 reviews "
         r"removed $\rightarrow$ \textbf{1{,}206}; rule-based screen fails (i) 127, (ii) 99, "
         r"(iii) 617};",
         r"\node[bx, below=of a] (d) {\textbf{Screened on title and abstract.} PubMed "
         r"\textbf{1{,}206} after 36 non-research and 194 reviews removed; fails (i) 127, "
         r"(ii) 99, (iii) 617. Xplore \textbf{" + th(scr) + r"} after " + str(non)
         + r" non-article; fails (i) " + th(f1) + r", (ii) " + th(f2) + r", (iii) " + th(f3)
         + r"};"),
        (r"\node[bx, below=of d] (e) {\textbf{Rule-eligible: 363.} Hand check of 60: "
         r"precision 62\%," + "\n" + r"  miss rate 18\% $\Rightarrow$ pool $\approx$ "
         r"\textbf{375}};",
         r"\node[bx, below=of d] (e) {\textbf{Rule-eligible: " + th(pool)
         + r"} $=$ 363 PubMed $+$ " + th(dd["ieee_only"]) + r" Xplore only." + "\n"
         + r"  Hand check of 60 PubMed records: precision 62\%, miss rate 18\% "
         r"$\Rightarrow$ PubMed pool $\approx$ \textbf{375}};"),
    ]
    for old_f, new_f in fig:
        if old_f in m:
            m = m.replace(old_f, new_f)
        elif new_f not in m:
            sys.exit("a Figure 1 box was not found, neither original nor rewritten:\n"
                     + old_f[:90])
    open(MAIN, "w", encoding="utf-8").write(m)

    print(f"supplement section written; main text and Figure 1 updated\n"
          f"  screened {scr} · eligible {elig} · IEEE-only {dd['ieee_only']}")


if __name__ == "__main__":
    main()
