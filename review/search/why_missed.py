#!/usr/bin/env python3
"""For each of the 12 studies, test the original query's concept blocks against the
record's own title+abstract, so Section II can say exactly why a study was missed."""
import json, os, re, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
EMAIL = "xxiang@mail.yu.edu"
rc = json.load(open(os.path.join(HERE, "recovery_check.json")))

BLOCKS = {
 "A_spatiotemporal": [r"spatiotemporal", r"spatio-temporal", r"space-time", r"space time"],
 "B_deeplearning":   [r"deep learning", r"neural network", r"neural networks", r"transformer", r"transformers", r"graph network", r"graph neural"],
 "C_health":         [r"health", r"clinical", r"patient", r"patients", r"wearable", r"wearables"],
 "D_twin":           [r"digital twin", r"digital twins", r"world model", r"world models"],
}

pmids = [r["pmid"] for r in rc["rows"] if r["pmid"]]
q = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "xml", "email": EMAIL})
with urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + q, timeout=60) as r:
    root = ET.fromstring(r.read())

text = {}
for art in root.findall(".//PubmedArticle"):
    pmid = art.findtext(".//PMID")
    ti = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
    ab = " ".join("".join(t.itertext()) for t in art.findall(".//Abstract/AbstractText"))
    text[pmid] = (ti + " " + ab).lower()

out = []
for r in rc["rows"]:
    t = text.get(r["pmid"], "")
    hits = {b: [w for w in ws if re.search(re.escape(w), t)] for b, ws in BLOCKS.items()}
    armA_ok = bool(hits["A_spatiotemporal"]) and bool(hits["B_deeplearning"]) and bool(hits["C_health"])
    armB_ok = bool(hits["D_twin"]) and bool(hits["B_deeplearning"]) and bool(hits["C_health"])
    fails = [b.split("_")[0] for b in ["A_spatiotemporal", "B_deeplearning", "C_health"] if not hits[b]]
    out.append({**r, "block_hits": {k: v for k, v in hits.items() if v},
                "arm_a_match": armA_ok, "arm_b_match": armB_ok,
                "blocks_failed_for_arm_a": fails,
                "consistent_with_index": (armA_ok or armB_ok) == r["in_identified"]})

json.dump(out, open(os.path.join(HERE, "why_missed.json"), "w"), indent=1)
print(f"{'bibkey':34s} {'PMID':10s} rec  fails   matched terms")
for o in out:
    mt = "; ".join(f"{k[0]}:{','.join(v[:2])}" for k, v in o["block_hits"].items())
    print(f"{o['bibkey']:34s} {o['pmid']:10s} {'Y' if o['in_identified'] else '.':4s} "
          f"{','.join(o['blocks_failed_for_arm_a']) or '-':7s} {mt[:74]}")
bad = [o["bibkey"] for o in out if not o["consistent_with_index"]]
print()
print("block test disagrees with PubMed's own retrieval for:", bad or "none (test reproduces the index exactly)")
from collections import Counter
c = Counter(tuple(o["blocks_failed_for_arm_a"]) for o in out if not o["in_identified"])
print("among the 8 not recovered, which block blocked them:")
for k, n in c.most_common():
    print(f"   {'+'.join(k) or '(none - excluded for another reason)'}: {n}")
