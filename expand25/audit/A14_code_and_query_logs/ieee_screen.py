#!/usr/bin/env python3
"""Screen the IEEE Xplore records under the same eligibility rules as the PubMed arm.

Until now the IEEE arm was reported as header counts only, which made the search
look like a two-database review without a two-database screen. This applies the
three recovered rules of `replicate_rules.py` verbatim to every IEEE record,
deduplicates within IEEE and against the PubMed set, and writes `ieee_screen.json`.

The PubMed comparison set is refetched here from the original 2026-09-11 concept
blocks (FINDINGS.md section 1), not from `merged_records.jsonl`, because that file
holds a later and wider re-run (2,457 records) rather than the 1,436 the paper reports.

    python3 ieee_screen.py            # refetches both sides
    python3 ieee_screen.py --no-net   # reuses ieee_*_raw.json and pubmed_orig.json
"""
import argparse, csv, json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
EMAIL = "xxiang@mail.yu.edu"
OUT = os.path.join(HERE, "ieee_screen.json")
PUB = os.path.join(HERE, "pubmed_orig.json")

# ---- the three rules, taken verbatim from replicate_rules.py -----------------
_spec = importlib.util.spec_from_file_location("rr", os.path.join(HERE, "replicate_rules_regexes.py"))
if os.path.exists(os.path.join(HERE, "replicate_rules_regexes.py")):
    _rr = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_rr)
    NONHEALTH, HUMAN, PRECLIN = _rr.NONHEALTH, _rr.HUMAN, _rr.PRECLIN
    SPACETIME, METRIC, NUMBER, COMPARE = _rr.SPACETIME, _rr.METRIC, _rr.NUMBER, _rr.COMPARE
else:  # read them out of replicate_rules.py without running its network code
    src = open(os.path.join(HERE, "replicate_rules.py")).read()
    ns = {"re": re}
    for line in src.splitlines():
        if re.match(r"^(NONHEALTH|HUMAN|PRECLIN|SPACETIME|METRIC|NUMBER|COMPARE)\s*=", line):
            exec(line, ns)
    NONHEALTH, HUMAN, PRECLIN = ns["NONHEALTH"], ns["HUMAN"], ns["PRECLIN"]
    SPACETIME, METRIC, NUMBER, COMPARE = ns["SPACETIME"], ns["METRIC"], ns["NUMBER"], ns["COMPARE"]


def verdict(text):
    r1 = not ((NONHEALTH.search(text) and not HUMAN.search(text))
              or (PRECLIN.search(text) and not HUMAN.search(text)))
    r2 = bool(SPACETIME.search(text))
    r3 = bool(METRIC.search(text) and NUMBER.search(text) and COMPARE.search(text))
    if not r1: return "excluded_ii_not_human_health", r1, r2, r3
    if not r2: return "excluded_i_no_spacetime_structure", r1, r2, r3
    if not r3: return "excluded_iii_no_quantitative_comparison", r1, r2, r3
    return "eligible", r1, r2, r3


def ntitle(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def ndoi(d):
    return (d or "").strip().lower().rstrip(".")


# ---- the PubMed set, from the original blocks --------------------------------
A = '(spatiotemporal[tiab] OR "spatio-temporal"[tiab] OR "space-time"[tiab] OR "space time"[tiab])'
B = ('("deep learning"[tiab] OR "neural network"[tiab] OR "neural networks"[tiab] OR transformer[tiab] '
     'OR transformers[tiab] OR "graph network"[tiab] OR "graph neural"[tiab])')
C = ('(health[tiab] OR clinical[tiab] OR patient[tiab] OR patients[tiab] OR wearable[tiab] '
     'OR wearables[tiab])')
D = ('("digital twin"[tiab] OR "digital twins"[tiab] OR "world model"[tiab] OR "world models"[tiab])')
Y = "2015:2026[dp]"
ARMS = {"main": f"{A} AND {B} AND {C} AND {Y}", "dtwm": f"{D} AND {B} AND {C} AND {Y}"}


def eutils(path, params):
    params = dict(params, email=EMAIL, tool="iot-survey-screen")
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{path}?" + urllib.parse.urlencode(params)
    for k in range(4):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return r.read()
        except Exception:
            if k == 3: raise
            time.sleep(2 * (k + 1))


def fetch_pubmed():
    arms, allids = {}, set()
    for name, q in ARMS.items():
        root = ET.fromstring(eutils("esearch.fcgi", {"db": "pubmed", "term": q, "retmax": 5000}))
        ids = [e.text for e in root.findall(".//IdList/Id")]
        arms[name] = ids
        allids |= set(ids)
        print(f"pubmed {name}: {len(ids)}", file=sys.stderr)
    recs = {}
    ids = sorted(allids)
    for i in range(0, len(ids), 200):
        root = ET.fromstring(eutils("efetch.fcgi", {"db": "pubmed", "id": ",".join(ids[i:i+200]),
                                                    "retmode": "xml"}))
        for art in root.findall(".//PubmedArticle"):
            pmid = art.findtext(".//PMID")
            ti = art.find(".//ArticleTitle")
            doi = ""
            for aid in art.findall('.//ArticleId[@IdType="doi"]'):
                doi = aid.text or ""
            recs[pmid] = {"pmid": pmid, "doi": doi,
                          "title": "".join(ti.itertext()) if ti is not None else ""}
        time.sleep(0.34)
    out = {"run_date": time.strftime("%Y-%m-%d"), "queries": ARMS,
           "counts": {k: len(v) for k, v in arms.items()},
           "overlap": len(set(arms["main"]) & set(arms["dtwm"])),
           "union": len(allids), "records": list(recs.values())}
    json.dump(out, open(PUB, "w"))
    return out


# ---- IEEE records -----------------------------------------------------------
def load_ieee(arm, net):
    raw = os.path.join(HERE, f"ieee_{arm}_raw.json")
    if os.path.exists(raw):
        return json.load(open(raw))
    if not net:
        raise SystemExit(f"{raw} missing and --no-net given")
    spec = importlib.util.spec_from_file_location("f", os.path.join(HERE, "fetch_ieee_a.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    q = json.load(open(os.path.join(HERE, "ieee_counts.json")))["queries"][
        "A_spatiotemporal" if arm == "a" else "B_twin_worldmodel"]
    recs, page, total = [], 1, None
    while True:
        j = m.post(q, page); total = j.get("totalRecords")
        batch = j.get("records") or []
        if not batch: break
        recs += batch
        print(f"ieee {arm} page {page}: {len(recs)}/{total}", file=sys.stderr)
        if len(recs) >= total: break
        page += 1
        time.sleep(1.0)
    d = {"run_date": time.strftime("%Y-%m-%d"), "query": q, "total_reported": total,
         "records": recs}
    json.dump(d, open(raw, "w"))
    return d


# Non-article item types, the IEEE analogue of PubMed's non-research item types.
NON_ARTICLE = re.compile(r"\b(Books?|Standards?|Courses?)\b", re.I)

# Reviews. The PubMed arm removed 194 of them by PublicationType before applying the
# three criteria. Xplore exposes no publication-type field, so the same exclusion has
# to be made textually, from the title and the opening of the abstract. The rule is
# deliberately broad: over-removing a primary study costs us a record, while leaving a
# review in makes the two arms non-equivalent, which is the defect being repaired.
REVIEW_TITLE = re.compile(
    r"\b(survey|review|overview|tutorial|systematic|scoping|bibliometric|"
    r"state[- ]of[- ]the[- ]art|taxonomy|comparative study|meta[- ]analys\w+)\b", re.I)
REVIEW_ABSTRACT = re.compile(
    r"\b(this (survey|review|article reviews|paper reviews)|we (review|survey)|"
    r"a (comprehensive|systematic|literature|scoping|narrative|critical) review|"
    r"this paper (surveys|reviews|provides an overview)|we provide an overview|"
    r"review of (the )?(literature|existing|recent|current)|"
    r"(survey|review) (of|on) (recent|existing|current|the))\b", re.I)


def is_review(title, abstract):
    """True when the record presents itself as a review rather than a primary study."""
    return bool(REVIEW_TITLE.search(title or "")
                or REVIEW_ABSTRACT.search((abstract or "")[:700]))


def screen_arm(d, arm):
    """The search endpoint truncates abstracts at about 400 characters, which makes
    criterion (iii) unanswerable; the per-document abstracts are required."""
    ab_path = os.path.join(HERE, f"ieee_{arm}_abstracts.json")
    if not os.path.exists(ab_path):
        raise SystemExit(f"{ab_path} missing: run fetch_ieee_abstracts.py {arm} first")
    full = json.load(open(ab_path))
    recs = d["records"]
    short = sum(1 for r in recs
                if len((full.get(str(r.get("articleNumber")), {}) or {}).get("abstract", "")) < 450)
    out = {"records": len(recs), "total_reported": d.get("total_reported"),
           "excluded_non_article": 0, "excluded_no_abstract": 0, "excluded_review": 0,
           "excluded_ii_not_human_health": 0, "excluded_i_no_spacetime_structure": 0,
           "excluded_iii_no_quantitative_comparison": 0, "eligible": 0,
           "abstracts_shorter_than_450_chars": short}
    kept, reviews = [], []
    for r in recs:
        ct = r.get("contentType") or ""
        if NON_ARTICLE.search(ct):
            out["excluded_non_article"] += 1
            continue
        ti = r.get("articleTitle") or ""
        ab = (full.get(str(r.get("articleNumber")), {}) or {}).get("abstract") or ""
        if not ab.strip():
            out["excluded_no_abstract"] += 1
            continue
        if is_review(ti, ab):
            out["excluded_review"] += 1
            reviews.append({"title": ti, "doi": r.get("doi") or ""})
            continue
        v, r1, r2, r3 = verdict(ti + " " + ab)
        out[v] += 1
        if v == "eligible":
            kept.append({"title": ti, "doi": r.get("doi") or "",
                          "year": r.get("publicationYear") or "",
                          "venue": r.get("publicationTitle") or r.get("displayPublicationTitle") or "",
                          "contentType": ct})
    out["screened_on_title_abstract"] = (out["records"] - out["excluded_non_article"]
                                         - out["excluded_no_abstract"]
                                         - out["excluded_review"])
    return out, kept, reviews


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-net", action="store_true")
    a = ap.parse_args()
    net = not a.no_net

    pub = json.load(open(PUB)) if (a.no_net and os.path.exists(PUB)) else fetch_pubmed()
    pdoi = {ndoi(r["doi"]) for r in pub["records"] if r["doi"]}
    ptit = {ntitle(r["title"]) for r in pub["records"] if r["title"]}

    arms, kept, reviews = {}, {}, {}
    for arm in ("a", "b"):
        d = load_ieee(arm, net)
        arms[arm], kept[arm], reviews[arm] = screen_arm(d, arm)

    # dedupe within IEEE across the two arms, then against PubMed
    seen_doi, seen_tit, uniq = set(), set(), []
    dup_within = 0
    for arm in ("a", "b"):
        for r in kept[arm]:
            dk, tk = ndoi(r["doi"]), ntitle(r["title"])
            if (dk and dk in seen_doi) or (tk and tk in seen_tit):
                dup_within += 1
                continue
            if dk: seen_doi.add(dk)
            if tk: seen_tit.add(tk)
            uniq.append(dict(r, arm=arm))

    in_pubmed = [r for r in uniq if (ndoi(r["doi"]) in pdoi) or (ntitle(r["title"]) in ptit)]
    new_only = [r for r in uniq if r not in in_pubmed]

    res = {
        "run_date": time.strftime("%Y-%m-%d"),
        "method": ("records paged from the Xplore search endpoint that the results page itself "
                   "calls; the same three recovered rules as the PubMed arm, applied to "
                   "title plus abstract"),
        "rule_source": "replicate_rules.py (regexes recovered verbatim 2026-09-22)",
        "arm_a": arms["a"],
        "arm_b": arms["b"],
        "eligible_before_dedup": len(kept["a"]) + len(kept["b"]),
        "duplicates_within_ieee": dup_within,
        "eligible_unique_within_ieee": len(uniq),
        "deduplicated_against_pubmed": {
            "pubmed_comparison_set": pub["union"],
            "pubmed_counts": pub["counts"],
            "pubmed_overlap_between_arms": pub["overlap"],
            "also_in_pubmed": len(in_pubmed),
            "ieee_only": len(new_only),
        },
        "ieee_only_records": new_only,
        "reviews_excluded": {
            "rule": ("title or the first 700 characters of the abstract presents the work as a "
                     "survey, review, overview, tutorial or meta-analysis; applied before the "
                     "three criteria, at the same stage the PubMed arm removed 194 reviews by "
                     "PublicationType"),
            "arm_a": arms["a"]["excluded_review"],
            "arm_b": arms["b"]["excluded_review"],
            "total": arms["a"]["excluded_review"] + arms["b"]["excluded_review"],
            "examples": [r["title"] for r in (reviews["a"] + reviews["b"])[:8]],
        },
        "difference_from_the_pubmed_screen": (
            "Xplore exposes no publication-type metadata, so the review exclusion is made by a "
            "textual rule over title and abstract rather than from a publication-type field. It "
            "can only catch a review that describes itself as one."),
    }
    json.dump(res, open(OUT, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "ieee_only_records"}, indent=1))


if __name__ == "__main__":
    main()
