#!/usr/bin/env python3
"""Run the protocol's PubMed search (both arms), fetch all records, log counts.

Outputs (same folder):
  pubmed_counts.json   - run date, query strings, counts per arm, overlap, union
  pubmed_records.jsonl - one record per line: pmid, doi, title, abstract, year, journal, pubtypes, arms
Stdlib only.
"""
import json, re, time, urllib.parse, urllib.request, datetime, os
import xml.etree.ElementTree as ET

EMAIL = "xxiang@mail.yu.edu"
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
HERE = os.path.dirname(os.path.abspath(__file__))

ST = '("spatiotemporal"[tiab] OR "spatio-temporal"[tiab] OR "spatial-temporal"[tiab] OR "space-time"[tiab] OR "spatial and temporal"[tiab])'
DL = '("deep learning"[tiab] OR "neural network*"[tiab] OR "transformer*"[tiab] OR "graph neural"[tiab] OR "LSTM"[tiab] OR "recurrent"[tiab] OR "convolutional"[tiab] OR "deep neural"[tiab])'
HL = ('("digital health"[tiab] OR "wearable*"[tiab] OR "internet of things"[tiab] OR "IoT"[tiab] OR "mobile health"[tiab] OR "mHealth"[tiab] '
      'OR "remote monitoring"[tiab] OR "continuous glucose"[tiab] OR "electronic health record*"[tiab] OR "diabetes"[tiab] OR "depression"[tiab] '
      'OR "cardiac"[tiab] OR "cardiovascular"[tiab] OR "diet*"[tiab] OR "chronic disease*"[tiab] OR "public health"[tiab] OR "clinical prediction"[tiab] '
      'OR "disease prediction"[tiab] OR "clinical"[tiab] OR "patient*"[tiab] OR "health"[tiab])')
TW = '("digital twin*"[tiab] OR "world model*"[tiab])'
WIN = '("2015/01/01"[dp] : "2026/12/31"[dp])'
ARMS = {"A_spatiotemporal": f"{ST} AND {DL} AND {HL} AND {WIN}",
        "B_twin_worldmodel": f"{TW} AND {DL} AND {HL} AND {WIN}"}


def get(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except Exception as e:
            time.sleep(2 * (k + 1))
    raise RuntimeError("fetch failed: " + url[:120])


def esearch(term):
    q = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmode": "json", "usehistory": "y", "retmax": 0, "email": EMAIL})
    j = json.loads(get(BASE + "esearch.fcgi?" + q))["esearchresult"]
    return int(j["count"]), j["webenv"], j["querykey"]


def efetch_all(count, webenv, qk, batch=200):
    recs = []
    for start in range(0, count, batch):
        q = urllib.parse.urlencode({"db": "pubmed", "query_key": qk, "WebEnv": webenv, "retstart": start, "retmax": batch, "retmode": "xml", "email": EMAIL})
        root = ET.fromstring(get(BASE + "efetch.fcgi?" + q))
        for art in root.findall(".//PubmedArticle"):
            pmid = art.findtext(".//PMID")
            title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
            abstract = " ".join("".join(t.itertext()) for t in art.findall(".//Abstract/AbstractText"))
            year = art.findtext(".//PubDate/Year") or (art.findtext(".//PubDate/MedlineDate") or "")[:4]
            journal = art.findtext(".//Journal/Title") or ""
            pubtypes = [p.text for p in art.findall(".//PublicationTypeList/PublicationType")]
            doi = ""
            for aid in art.findall(".//ArticleIdList/ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = (aid.text or "").lower()
            recs.append({"pmid": pmid, "doi": doi, "title": title, "abstract": abstract, "year": year,
                         "journal": journal, "pubtypes": pubtypes})
        print(f"  fetched {min(start + batch, count)}/{count}")
        time.sleep(0.4)
    return recs


def main():
    run = {"run_date": datetime.date.today().isoformat(), "database": "PubMed (E-utilities)", "queries": ARMS, "counts": {}}
    allrecs = {}
    for arm, term in ARMS.items():
        n, webenv, qk = esearch(term)
        print(f"{arm}: {n}")
        run["counts"][arm] = n
        for r in efetch_all(n, webenv, qk):
            allrecs.setdefault(r["pmid"], {**r, "arms": []})["arms"].append(arm)
    both = sum(1 for r in allrecs.values() if len(r["arms"]) == 2)
    run["counts"]["overlap_A_and_B"] = both
    run["counts"]["union_unique"] = len(allrecs)
    with open(os.path.join(HERE, "pubmed_records.jsonl"), "w") as f:
        for r in allrecs.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump(run, open(os.path.join(HERE, "pubmed_counts.json"), "w"), indent=1)
    print(json.dumps(run["counts"], indent=1))


if __name__ == "__main__":
    main()
