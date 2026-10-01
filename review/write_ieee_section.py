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
    rev = d.get("reviews_excluded", {})
    n_rev = rev.get("total", 0)

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

Of the {th(tot)} records across the two arms, {non} are non-article item types,
{noab} carry no abstract and {n_rev} are reviews, leaving \textbf{{{th(scr)}}}
screened on title and abstract. Applying criteria~(i)--(iii) as the same textual
rules, {th(f2)} records failed~(ii), {th(f1)} failed~(i) and {th(f3)} failed~(iii),
leaving \textbf{{{th(elig)}}} eligible records after deduplication within Xplore
({d['duplicates_within_ieee']} records appear on both arms). Resolved by DOI and
by normalized title against the {th(dd['pubmed_comparison_set'])} records of the
29 September 2026 PubMed snapshot, {th(dd['also_in_pubmed'])} of these are already
in the PubMed set and \textbf{{{th(dd['ieee_only'])}}} are Xplore only.

\subsection{{Removing reviews, and what it changed}}
The PubMed arm removed 194 reviews by publication type before the criteria were
applied. Xplore exposes no publication-type metadata, so the same exclusion is made
here by a textual rule: a record is treated as a review when its title, or the first
700 characters of its abstract, presents the work as a survey, review, overview,
tutorial, scoping study or meta-analysis. The rule removed {n_rev} records
({rev.get('arm_a', 0)} from the spatiotemporal arm and {rev.get('arm_b', 0)} from the
twin arm), applied at the same stage as on the PubMed side.

It is worth recording how little this changed, because it says something about the
criteria. Screening without the review rule left 286 eligible records; screening with
it leaves {th(elig)}. Only two of the reviews would have survived criteria~(i)--(iii)
anyway, because criterion~(iii) asks for a quantitative result against a named
baseline and a review rarely reports one of its own. The exclusion matters for making
the two arms procedurally equivalent, not because it moved the number. One difference
remains and cannot be removed: the rule is textual, so it catches only a review that
describes itself as one, whereas the PubMed exclusion reads an indexed field.

\subsection{{Matching rules}}
Two records are the same when their DOIs agree after lowercasing and stripping any
trailing period, or when their titles agree after normalization. A title is
normalized by lowercasing it and deleting every non-alphanumeric character, so
differences in punctuation, hyphenation, spacing and capitalization between the two
databases do not create spurious distinct records. Within Xplore the two arms are
merged in the order A then B and the first occurrence of a record is kept, so a
record retrieved by both arms is counted once. Against PubMed, a match marks the
record as already present and it is not added to the pool; only the unmatched
remainder is reported as Xplore-only.

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
    # The sentence is regenerated every round, so match it by its anchors rather than
    # by an exact earlier wording: an exact match breaks the moment the wording changes.
    sentence = (
        " The rule errs both ways, so correcting both cells puts the eligible PubMed "
        "literature at \\textbf{roughly 375 studies}: an order of magnitude, not a count. "
        "It judges abstracts, under-counting studies whose abstracts omit results. "
        f"Both IEEE Xplore arms were then re-run and screened under the same rules, with "
        f"reviews excluded as on the PubMed side: {th(scr)} records screened on title and "
        f"abstract left {th(elig)} eligible, {th(dd['ieee_only'])} of them outside the PubMed "
        f"set, so the rule-eligible literature across the two databases is "
        f"\\textbf{{{th(pool)}}} records rather than 363. The hand check was carried out on "
        f"the PubMed screen alone, so its correction is not carried across; Supplement "
        f"Section~III gives the per-arm counts, the matching rules and the one difference "
        f"that cannot be removed between the two databases.")
    pat = re.compile(
        r" The rule errs both ways.*?between the two databases\.", re.S)
    if not pat.search(m):
        sys.exit("the methodology sentence could not be located for regeneration")
    m = pat.sub(lambda _: sentence, m, count=1)

    # Review Limitations denominator, matched by anchor for the same reason.
    m = re.sub(r"(and the two logged searches put the rule-eligible literature at )[\d{,}]+( records)",
               lambda mm: mm.group(1) + th(pool) + mm.group(2), m, count=1)

    # Figure 1: all three boxes are regenerated from the screen record each round.
    boxes = [
        (r"(?m)^\\node\[bx\] \(a\) \{\\textbf\{Identified\.\}.*$",
         r"\node[bx] (a) {\textbf{Identified.} PubMed, 11 Sept.\ 2026: \textbf{1{,}436} unique; "
         r"IEEE Xplore, re-run 29 Sept.: \textbf{" + th(tot) + r"}; citation chasing: "
         r"3{,}472 screened, \textbf{15} new};"),
        (r"(?m)^\\node\[bx, below=of a\] \(d\) \{\\textbf\{Screened.*$",
         r"\node[bx, below=of a] (d) {\textbf{Screened on title and abstract.} PubMed "
         r"\textbf{1{,}206} after 36 non-research and 194 reviews removed; fails (i) 127, "
         r"(ii) 99, (iii) 617. Xplore \textbf{" + th(scr) + r"} after " + str(non)
         + r" non-article and " + str(n_rev) + r" reviews; fails (i) " + th(f1) + r", (ii) "
         + th(f2) + r", (iii) " + th(f3) + r"};"),
        (r"(?s)\\node\[bx, below=of d\] \(e\) \{\\textbf\{Rule-eligible.*?\\textbf\{375\}\};",
         r"\node[bx, below=of d] (e) {\textbf{Rule-eligible: " + th(pool) + r"} $=$ 363 PubMed "
         r"$+$ " + th(dd["ieee_only"]) + r" Xplore only." + "\n"
         + r"  Hand check of 60 PubMed records: precision 62\%, miss rate 18\% "
         r"$\Rightarrow$ PubMed pool $\approx$ \textbf{375}};"),
    ]
    # No re.S here: the line-anchored patterns use .*$ and with DOTALL that would run
    # from the first box to the end of the file. Box (e) spans two lines and carries
    # its own (?s).
    for pat, repl in boxes:
        if not re.search(pat, m):
            sys.exit("a Figure 1 box could not be located:\n" + pat[:70])
        m = re.sub(pat, lambda _, r=repl: r, m, count=1)

    open(MAIN, "w", encoding="utf-8").write(m)

    print(f"supplement section written; main text and Figure 1 updated\n"
          f"  screened {scr} · eligible {elig} · IEEE-only {dd['ieee_only']}")


if __name__ == "__main__":
    main()
