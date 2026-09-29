#!/usr/bin/env python3
"""Fetch the v2 record set and apply the same three eligibility rules, so the cost of adopting the
repaired query can be compared against the search as run."""
import json, re, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET

EMAIL="767483570xray@gmail.com"; EUT="https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
def tiab(ts): return "("+" OR ".join(f'"{t}"[tiab]' if " " in t else f"{t}[tiab]" for t in ts)+")"
A1=["spatiotemporal","spatio-temporal","space-time","space time"]
A_LONG=["longitudinal","time series","time-series","repeated measures","continuous monitoring",
        "continuous glucose monitoring","dynamic prediction","follow-up visits","serial imaging"]
B1=["deep learning","neural network","neural networks","transformer","transformers","graph network","graph neural"]
B_FAM=["convolutional neural","graph convolutional","CNN","LSTM","long short-term memory","recurrent neural",
       "GRU","autoencoder","attention mechanism","self-attention","state space model","diffusion model"]
C1=["health","clinical","patient","patients","wearable","wearables"]
C_MED=["disease","diagnosis","diagnostic","medical","healthcare","hospital","physiological","mortality",
       "survival","cohort","depression","diabetes","cardiac"]
TWIN=["digital twin","digital twins","world model","world models"]
W="2015:2026[dp]"

def esearch_all(term):
    ids=[]; ret=10000
    u=(f"{EUT}/esearch.fcgi?db=pubmed&retmode=json&retmax={ret}&email={EMAIL}&term={urllib.parse.quote(term)}")
    d=json.load(urllib.request.urlopen(u,timeout=180))["esearchresult"]
    return int(d["count"]), d.get("idlist",[])

armA=f"({tiab(A1+A_LONG)} AND {tiab(B1+B_FAM)} AND {tiab(C1+C_MED)} AND {W})"
armB=f"({tiab(TWIN)} AND {tiab(B1+B_FAM)} AND {tiab(C1+C_MED)} AND {W})"
na,ida=esearch_all(armA); print(f"arm A v2: {na:,} (fetched {len(ida)})")
nb,idb=esearch_all(armB); print(f"arm B v2: {nb:,} (fetched {len(idb)})")
allids=sorted(set(ida)|set(idb)); print(f"union: {len(allids):,}   overlap: {len(set(ida)&set(idb))}")

recs={}
for i in range(0,len(allids),300):
    batch=allids[i:i+300]
    u=f"{EUT}/efetch.fcgi?db=pubmed&retmode=xml&email={EMAIL}&id="+",".join(batch)
    try: root=ET.fromstring(urllib.request.urlopen(u,timeout=240).read())
    except Exception as e: print("  fetch fail",i,e); continue
    for art in root.iter("PubmedArticle"):
        pmid=art.findtext(".//PMID") or ""
        ti=" ".join((art.findtext(".//ArticleTitle") or "").split())
        ab=" ".join(" ".join(x.itertext()) for x in art.iter("AbstractText"))
        pts=[p.text for p in art.iter("PublicationType")]
        recs[pmid]={"title":ti,"abstract":" ".join(ab.split()),"pubtypes":pts}
    print(f"  fetched {len(recs):,}/{len(allids):,}", end="\r"); time.sleep(0.34)
print()

R1=r"spatiotemporal|spatio-temporal|space.time|(?=.*\bspatial\b)(?=.*\btemporal\b)|longitudinal|time.series|repeated measures|continuous (?:glucose )?monitoring|dynamic prediction|serial (?:imaging|scans)|follow.up visits"
R2=r"clinical|patient|health|disease|diagnos|medical|hospital|mortality|survival|physiolog|wearable"
R3=r"\b(accuracy|AUC|AUROC|RMSE|MAE|MAPE|F1|dice|sensitivity|specificity|correlation|outperform|compared (?:with|to)|baseline|state.of.the.art)\b"
NONRES=re.compile(r"Review|Editorial|Letter|Comment|News|Retract|Published Erratum|Preprint",re.I)

stats={"records":len(recs),"nonresearch":0,"screened":0,"fail_r1":0,"fail_r2":0,"fail_r3":0,"eligible":0}
elig=[]
for pmid,r in recs.items():
    t=r["title"]+" "+r["abstract"]
    if any(NONRES.search(p or "") for p in r["pubtypes"]): stats["nonresearch"]+=1; continue
    stats["screened"]+=1
    if not re.search(R1,t,re.I): stats["fail_r1"]+=1; continue
    if not re.search(R2,t,re.I): stats["fail_r2"]+=1; continue
    if not re.search(R3,t,re.I): stats["fail_r3"]+=1; continue
    stats["eligible"]+=1; elig.append(pmid)

SEEDS={"35625016":"Liu MODMA","39281477":"Thaipisutikul","33969930":"Kong","39728900":"Zhang",
 "31369390":"GluNet","40348812":"Lim","27903059":"XiaoLi","38066222":"Bohoran",
 "35347750":"Lin & Luo","33858815":"Nitski","35992891":"Glaser"}
in_set=[n for p,n in SEEDS.items() if p in recs]
in_elig=[n for p,n in SEEDS.items() if p in set(elig)]
print(json.dumps(stats,indent=1))
print(f"\nseeds retrieved by v2: {len(in_set)}/11 -> {in_set}")
print(f"seeds surviving the rule screen: {len(in_elig)}/11 -> {in_elig}")
json.dump({"counts":stats,"arm_a":na,"arm_b":nb,"union":len(allids),
           "seeds_retrieved":in_set,"seeds_eligible":in_elig,"eligible_pmids":elig},
          open("rerun_v2_results.json","w"),indent=1)
print("\nwritten: rerun_v2_results.json")
