#!/usr/bin/env python3
"""Validate and repair the search string against a seed set of known-relevant studies.

The seed set is the eleven studies of Table II that were assembled by reading (Xie and Yao is
dropped from the survey). Standard relative-recall testing: measure how many the query retrieves,
diagnose each miss by concept block, repair the block, re-measure. Every added term is tied to a
concept the protocol already claims to cover, not to a paper.
"""
import json, time, urllib.parse, urllib.request

EMAIL = "767483570xray@gmail.com"
EUT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def esearch(term, retmax=0):
    u = (f"{EUT}/esearch.fcgi?db=pubmed&retmode=json&retmax={retmax}&email={EMAIL}"
         f"&term={urllib.parse.quote(term)}")
    d = json.load(urllib.request.urlopen(u, timeout=120))["esearchresult"]
    return int(d["count"]), d.get("idlist", [])

def tiab(terms):
    return "(" + " OR ".join(f'"{t}"[tiab]' if " " in t else f"{t}[tiab]" for t in terms) + ")"

WINDOW = "2015:2026[dp]"

# ---------- v1: the query as it was actually run ----------
A1 = ["spatiotemporal", "spatio-temporal", "space-time", "space time"]
B1 = ["deep learning", "neural network", "neural networks", "transformer", "transformers",
      "graph network", "graph neural"]
C1 = ["health", "clinical", "patient", "patients", "wearable", "wearables"]

# ---------- v2: each addition names a concept the protocol already claims ----------
# criterion (i) second disjunct: "longitudinal data with an explicit temporal model"
A_LONG = ["longitudinal", "time series", "time-series", "repeated measures", "continuous monitoring",
          "continuous glucose monitoring", "dynamic prediction", "follow-up visits", "serial imaging"]
# the model families the survey itself compares (Section IV)
B_FAM  = ["convolutional neural", "graph convolutional", "CNN", "LSTM", "long short-term memory",
          "recurrent neural", "GRU", "autoencoder", "attention mechanism", "self-attention",
          "state space model", "diffusion model"]
# health concepts beyond the four originally used
C_MED  = ["disease", "diagnosis", "diagnostic", "medical", "healthcare", "hospital", "physiological",
          "mortality", "survival", "cohort", "depression", "diabetes", "cardiac"]

SEEDS = {  # the eleven assembled studies, by PMID
 "35625016": "Liu - MODMA EEG", "39281477": "Thaipisutikul - Thai national",
 "33969930": "Kong - two-site fMRI", "39728900": "Zhang - STANet fMRI",
 "31369390": "Li - GluNet CGM", "40348812": "Lim - life-log CGM",
 "27903059": "Li - BRFSS+ACS spatial", "38066222": "Bohoran - CMR",
 "35347750": "Lin & Luo - TransformerJM", "33858815": "Nitski - SRTR/UHN",
 "35992891": "Glaser - Health ABC DXA"}

def arm(a, b, c):
    return f"({tiab(a)} AND {tiab(b)} AND {tiab(c)} AND {WINDOW})"

def recall(term, label):
    n, ids = esearch(term, retmax=0)
    got, miss = [], []
    for pmid, name in SEEDS.items():
        cnt, _ = esearch(f"({term}) AND {pmid}[uid]")
        (got if cnt else miss).append((pmid, name))
        time.sleep(0.34)
    print(f"\n### {label}\n  records: {n:,}   seed recall: {len(got)}/{len(SEEDS)}")
    for p, nm in miss: print(f"    miss: {nm}")
    return {"label": label, "records": n, "recall": len(got), "of": len(SEEDS),
            "missed": [nm for _, nm in miss]}

out = []
out.append(recall(arm(A1, B1, C1), "v1 as run (arm A only)"))
out.append(recall(arm(A1 + A_LONG, B1, C1), "v2a: + longitudinal concept in block A"))
out.append(recall(arm(A1 + A_LONG, B1 + B_FAM, C1), "v2b: + model families in block B"))
out.append(recall(arm(A1 + A_LONG, B1 + B_FAM, C1 + C_MED), "v2c: + medical concepts in block C"))
json.dump(out, open("query_v2_results.json", "w"), indent=1)
print("\nwritten: query_v2_results.json")
