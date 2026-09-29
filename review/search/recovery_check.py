#!/usr/bin/env python3
"""How many of the 12 synthesized studies does the PubMed search actually recover?

Replaces two numbers in Section II that were derived by title-substring matching:
  "only one of the 363 is cited here"  and  "The query recovers 6 of our 12".
Method: bibkey -> DOI (from the verified reference cache) -> PMID (PubMed [doi] search),
then set membership against (a) the identified union and (b) the 363 rule-eligible.
"""
import json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
EMAIL = "xxiang@mail.yu.edu"
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# The twelve rows of Table II, in table order, with the PDF reference numbers they carry.
TWELVE = [("2", "[30] Liu et al. - depression, MODMA EEG"),
          ("3", "[57] Thaipisutikul et al. - depression, Thai national"),
          ("4", "[58] Kong et al. - depression, fMRI"),
          ("9", "[31] Zhang et al. - depression, STANet fMRI"),
          ("Li2020GluNet", "[56] Li et al. - diabetes, GluNet CGM"),
          ("Lim2025VirtualCGM", "[32] Lim et al. - diabetes, life-log"),
          ("XiaoLi2016DiabetesSpatiotemporal", "[34] Li et al. - diabetes, BRFSS+ACS"),
          ("5", "[59] Bohoran et al. - cardiac, CMR"),
          ("7", "[61] Xie & Yao - cardiac, EP simulation"),
          ("lin2022deep", "[67] Lin & Luo - longitudinal survival"),
          ("nitski2021long", "[68] Nitski et al. - longitudinal mortality"),
          ("glaser2022deep", "[33] Glaser et al. - longitudinal DXA")]


def get(url, tries=4):
    req = urllib.request.Request(url, headers={"User-Agent": f"survey-recovery/1.0 (mailto:{EMAIL})"})
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read()
        except Exception:
            time.sleep(1.5 * (k + 1))
    return None


def esearch_pmids(term, retmax=5000):
    q = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmode": "json", "retmax": retmax, "email": EMAIL})
    b = get(E + "esearch.fcgi?" + q)
    if not b:
        return []
    return json.load(__import__("io").BytesIO(b))["esearchresult"].get("idlist", [])


def pmid_for(doi=None, title=None):
    if doi:
        ids = esearch_pmids(f'"{doi}"[doi]', 5)
        if ids:
            return ids[0], "doi"
    if title:
        t = re.sub(r"[^A-Za-z0-9 ]", " ", title)
        t = re.sub(r"\s+", " ", t).strip()
        ids = esearch_pmids(f'"{t}"[Title]', 5)
        if ids:
            return ids[0], "title"
    return None, "not found"


# --- the original query, verbatim -------------------------------------------
A = '(spatiotemporal[tiab] OR "spatio-temporal"[tiab] OR "space-time"[tiab] OR "space time"[tiab])'
B = ('("deep learning"[tiab] OR "neural network"[tiab] OR "neural networks"[tiab] OR transformer[tiab] '
     'OR transformers[tiab] OR "graph network"[tiab] OR "graph neural"[tiab])')
C = '(health[tiab] OR clinical[tiab] OR patient[tiab] OR patients[tiab] OR wearable[tiab] OR wearables[tiab])'
D = '("digital twin"[tiab] OR "digital twins"[tiab] OR "world model"[tiab] OR "world models"[tiab])'
Y = "2015:2026[dp]"

print("fetching the identified sets ...")
arm_a = set(esearch_pmids(f"{A} AND {B} AND {C} AND {Y}")); time.sleep(0.4)
arm_b = set(esearch_pmids(f"{D} AND {B} AND {C} AND {Y}"))
identified = arm_a | arm_b
print(f"  arm A {len(arm_a)}  arm B {len(arm_b)}  union {len(identified)}")

eligible = set(open(os.path.join(HERE, "eligible363_pmids.txt")).read().split())
print(f"  rule-eligible (from 2026-09-11 run) {len(eligible)}")

cache = json.load(open(os.path.join(HERE, "..", "..", "endnote", "out_live", "cache.json")))
bib = open(os.path.join(HERE, "..", "..", "endnote", "overleaf-live", "cited8page.bib")).read()

def title_of(key):
    m = re.search(r"@\w+\{" + re.escape(key) + r",(.*?)\n\}", bib, re.S)
    if not m: return None
    t = re.search(r"title\s*=\s*\{+(.+?)\}+,?\s*\n", m.group(1), re.S)
    return re.sub(r"[{}]", "", re.sub(r"\s+", " ", t.group(1))).strip() if t else None

rows = []
for key, label in TWELVE:
    doi = (cache.get(key) or {}).get("doi") or ""
    pmid, how = pmid_for(doi or None, title_of(key))
    rows.append({"bibkey": key, "label": label, "doi": doi, "pmid": pmid, "resolved_by": how,
                 "in_identified": bool(pmid and pmid in identified),
                 "in_arm_a": bool(pmid and pmid in arm_a),
                 "in_arm_b": bool(pmid and pmid in arm_b),
                 "in_363_eligible": bool(pmid and pmid in eligible)})
    time.sleep(0.35)

in_pm = sum(r["pmid"] is not None for r in rows)
in_id = sum(r["in_identified"] for r in rows)
in_el = sum(r["in_363_eligible"] for r in rows)

out = {"identified_union": len(identified), "arm_a": len(arm_a), "arm_b": len(arm_b),
       "eligible_363": len(eligible), "twelve_in_pubmed": in_pm,
       "twelve_in_identified": in_id, "twelve_in_363_eligible": in_el, "rows": rows}
json.dump(out, open(os.path.join(HERE, "recovery_check.json"), "w"), indent=1)

print()
print(f"{'bibkey':34s} {'PMID':10s} ident 363  study")
for r in rows:
    print(f"{r['bibkey']:34s} {str(r['pmid'] or '-'):10s} "
          f"{'Y' if r['in_identified'] else '.':5s} {'Y' if r['in_363_eligible'] else '.':4s} {r['label']}")
print()
print(f"of the 12:  {in_pm} indexed in PubMed at all;  {in_id} recovered by the query;  {in_el} among the 363 rule-eligible")
