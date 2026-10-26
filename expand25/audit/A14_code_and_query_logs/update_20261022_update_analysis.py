#!/usr/bin/env python3
"""Search update through 22 October 2026, and the PubMed side of the 54 Xplore-PubMed overlaps.

1. PubMed: both original arms restricted to Entrez dates 2026/09/12-2026/10/22 (records first
   indexed after the 11 September screening snapshot); each record screened under the item-type
   exclusion and criteria (i)-(iii), with its Entrez and electronic-publication dates.
2. IEEE Xplore: records of the 22 October re-run whose Xplore insertion date is after 22 September
   2026 (the original export), screened by ieee_screen.py's rules (already in ieee_screen.json here).
3. Overlaps: the Xplore rule-eligible records matched to the PubMed set (by normalized DOI or title)
   are re-identified, and for each matched PubMed record we record whether it is in the 363-record
   PubMed rule-eligible pool of 11 September and, if not, the PubMed-side rule verdict.
Writes update_records.csv and update_summary.json.
"""
import csv, json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("isc", os.path.join(HERE, "ieee_screen.py"))
isc = importlib.util.module_from_spec(spec); spec.loader.exec_module(isc)
EU = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
NONRES = {"Review", "Systematic Review", "Meta-Analysis", "Editorial", "Comment", "Letter", "News",
          "Erratum", "Published Erratum", "Retraction of Publication", "Guideline"}


def eu(path, params, post=False):
    params = dict(params, email=isc.EMAIL, tool="iot-survey-update")
    data = urllib.parse.urlencode(params).encode()
    for k in range(4):
        try:
            req = urllib.request.Request(EU + path, data=data) if post else EU + path + "?" + data.decode()
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception:
            if k == 3: raise
            time.sleep(2 * (k + 1))


def efetch(ids):
    out = {}
    for i in range(0, len(ids), 150):
        root = ET.fromstring(eu("efetch.fcgi", {"db": "pubmed", "id": ",".join(ids[i:i + 150]), "retmode": "xml"}, True))
        for art in root.findall(".//PubmedArticle"):
            pmid = art.findtext(".//PMID")
            ti = art.find(".//ArticleTitle")
            ab = " ".join("".join(a.itertext()) for a in art.findall(".//Abstract/AbstractText"))
            doi = next((x.text or "" for x in art.findall(".//ArticleId") if x.get("IdType") == "doi"), "")
            types = [t.text for t in art.findall(".//PublicationType")]
            ed = art.find(".//PubMedPubDate[@PubStatus='entrez']")
            ep = art.find(".//ArticleDate[@DateType='Electronic']")
            fmt = lambda e: "-".join((e.findtext(x) or "").zfill(2) for x in ("Year", "Month", "Day")) if e is not None else ""
            out[pmid] = {"title": "".join(ti.itertext()) if ti is not None else "", "abstract": ab, "doi": doi,
                         "types": types, "entrez_date": fmt(ed), "epub_date": fmt(ep)}
        time.sleep(0.4)
    return out


def pubmed_verdict(r):
    if NONRES & set(r["types"]):
        return "excluded_non_research_or_review"
    if not r["abstract"].strip():
        return "excluded_no_abstract"
    return isc.verdict(r["title"] + " " + r["abstract"])[0]


def main():
    rows, summ = [], {"run_date": time.strftime("%Y-%m-%d")}
    # 1. PubMed update by Entrez date
    win = "2026/09/12:2026/10/22[edat]"
    ids = set()
    for name, q in isc.ARMS.items():
        root = ET.fromstring(eu("esearch.fcgi", {"db": "pubmed", "term": f"({q}) AND {win}", "retmax": 5000}))
        got = [e.text for e in root.findall(".//IdList/Id")]
        summ[f"pubmed_{name}_new"] = len(got); ids |= set(got)
    recs = efetch(sorted(ids))
    from collections import Counter
    c = Counter()
    for pmid, r in recs.items():
        v = pubmed_verdict(r); c[v] += 1
        rows.append({"set": "pubmed_update", "id": pmid, "doi": r["doi"], "entrez_or_insert_date": r["entrez_date"],
                     "epub_date": r["epub_date"], "decision": v, "title": r["title"]})
    summ["pubmed_update_window"] = win
    summ["pubmed_update_unique"] = len(recs)
    summ["pubmed_update_decisions"] = dict(c)
    # 2. Xplore records inserted after 22 September
    xs = json.load(open(os.path.join(HERE, "ieee_screen.json")))
    full = {}
    for arm in ("a", "b"):
        full.update(json.load(open(os.path.join(HERE, f"ieee_{arm}_abstracts.json"))))
    cx = Counter()
    for arm in ("a", "b"):
        raw = json.load(open(os.path.join(HERE, f"ieee_{arm}_raw.json")))
        for r in raw["records"]:
            info = full.get(str(r.get("articleNumber")), {}) or {}
            ins = info.get("insertDate") or ""
            m = re.search(r"(\d{1,2}) (\w+)\.? (\d{4})", ins)
            try:
                dt = time.strptime(" ".join(m.groups()), "%d %B %Y") if m else None
            except ValueError:
                dt = time.strptime(" ".join(m.groups()), "%d %b %Y") if m else None
            if not dt or dt <= time.strptime("2026-09-22", "%Y-%m-%d"):
                continue
            ti, ab = r.get("articleTitle") or "", info.get("abstract") or ""
            v = ("excluded_review" if isc.is_review(ti, ab) else isc.verdict(ti + " " + ab)[0]) if ab else "excluded_no_abstract"
            cx[v] += 1
            rows.append({"set": f"xplore_update_arm_{arm}", "id": str(r.get("articleNumber")), "doi": r.get("doi") or "",
                         "entrez_or_insert_date": time.strftime("%Y-%m-%d", dt), "epub_date": "", "decision": v, "title": ti})
    summ["xplore_inserted_after_2026-09-22"] = dict(cx)
    summ["xplore_rerun"] = {k: xs[k] for k in ("eligible_unique_within_ieee", "deduplicated_against_pubmed")}
    summ["xplore_rerun"]["records"] = {"a": xs["arm_a"]["records"], "b": xs["arm_b"]["records"]}
    # 3. PubMed side of the overlaps
    pub = json.load(open(os.path.join(HERE, "pubmed_orig.json")))
    bydoi = {isc.ndoi(r["doi"]): r["pmid"] for r in pub["records"] if r["doi"]}
    bytit = {isc.ntitle(r["title"]): r["pmid"] for r in pub["records"] if r["title"]}
    only = {(isc.ndoi(r["doi"]), isc.ntitle(r["title"])) for r in xs["ieee_only_records"]}
    kept = []
    for arm in ("a", "b"):
        _, k, _ = isc.screen_arm(json.load(open(os.path.join(HERE, f"ieee_{arm}_raw.json"))), arm)
        kept += k
    seen, matched = set(), []
    for r in kept:
        key = (isc.ndoi(r["doi"]), isc.ntitle(r["title"]))
        if key in seen or key in only: continue
        seen.add(key)
        pmid = bydoi.get(key[0]) or bytit.get(key[1])
        if pmid: matched.append((pmid, r))
    pool = set(open(os.path.join(UP, "eligible363_pmids.txt")).read().split())
    pm = efetch(sorted({p for p, _ in matched}))
    co = Counter()
    for pmid, r in matched:
        inpool = pmid in pool
        v = "in_363_pool" if inpool else "not_in_pool:" + pubmed_verdict(pm.get(pmid, {"types": [], "abstract": "", "title": ""}))
        co["in_363_pool" if inpool else "not_in_363_pool"] += 1
        rows.append({"set": "overlap_pubmed_side", "id": pmid, "doi": r["doi"],
                     "entrez_or_insert_date": pm.get(pmid, {}).get("entrez_date", ""), "epub_date": "", "decision": v,
                     "title": r["title"]})
    summ["overlaps_matched"] = len(matched)
    summ["overlaps_pubmed_side"] = dict(co)
    summ["overlaps_not_in_pool_reasons"] = dict(Counter(r["decision"] for r in rows if r["set"] == "overlap_pubmed_side" and r["decision"] != "in_363_pool"))
    with open(os.path.join(HERE, "update_records.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump(summ, open(os.path.join(HERE, "update_summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
