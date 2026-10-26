#!/usr/bin/env python3
"""Fetch the records for the IoT-engineering complement screen (revision of 22 October 2026).

Two record sets that the original synthesis sized but did not screen beyond the rules:
  1. the 230 IEEE Xplore-only rule-eligible records (ieee_screen.json, ieee_only_records):
     full abstracts are fetched per document (the search endpoint truncates them);
  2. the PubMed records added when an IoT block is ORed into the health block of the
     spatiotemporal arm (re-run on the run date below; the 16 October run gave 1194 -> 1501).

Writes iot_complement_records.json; resumable.
    python fetch_iot_complement.py
"""
import json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "iot_complement_records.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
EU = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

ST = '(spatiotemporal[tiab] OR "spatio-temporal"[tiab] OR "space-time"[tiab] OR "space time"[tiab])'
DL = ('("deep learning"[tiab] OR "neural network"[tiab] OR "neural networks"[tiab] OR transformer[tiab] '
      'OR transformers[tiab] OR "graph network"[tiab] OR "graph neural"[tiab])')
HL = '(health[tiab] OR clinical[tiab] OR patient[tiab] OR patients[tiab] OR wearable[tiab] OR wearables[tiab]'
IOT = (' OR "internet of things"[tiab] OR IoT[tiab] OR sensor[tiab] OR sensors[tiab] OR smartphone[tiab] '
       'OR smartphones[tiab] OR mHealth[tiab] OR "mobile health"[tiab] OR "edge computing"[tiab] '
       'OR "body area network"[tiab] OR "remote monitoring"[tiab]')
YR = " AND 2015:2026[dp]"
Q_BASE = f"{ST} AND {DL} AND {HL}){YR}"
Q_IOT = f"{ST} AND {DL} AND {HL}{IOT}){YR}"


def http(url, headers=None, data=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})}, data=data)
    for k in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace"), r.geturl()
        except Exception as e:
            if k == 2:
                print("  fail", url[:90], e, file=sys.stderr)
                return None, None
            time.sleep(2 * (k + 1))


def ieee_number(doi):
    req = urllib.request.Request("https://doi.org/" + doi, headers={"User-Agent": UA}, method="HEAD")
    opener = urllib.request.build_opener(type("NR", (urllib.request.HTTPRedirectHandler,),
                                              {"redirect_request": lambda *a, **k: None})())
    try:
        opener.open(req, timeout=30)
    except urllib.error.HTTPError as e:
        m = re.search(r"/document/(\d+)", e.headers.get("Location", "") or "")
        return m.group(1) if m else None
    except Exception:
        return None


def ieee_abstract(num):
    txt, _ = http(f"https://ieeexplore.ieee.org/rest/document/{num}/abstract",
                  {"Accept": "application/json", "Referer": f"https://ieeexplore.ieee.org/document/{num}"})
    if not txt:
        return {}
    try:
        d = json.loads(txt)
    except ValueError:
        return {}
    return {"abstract": d.get("abstract") or "", "onlineDate": d.get("onlineDate") or "",
            "insertDate": d.get("insertDate") or "", "contentType": d.get("contentType") or ""}


def esearch_all(term):
    q = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmax": 10000, "retmode": "json"})
    txt, _ = http(EU + "esearch.fcgi?" + q)
    d = json.loads(txt)["esearchresult"]
    return int(d["count"]), d["idlist"]


def efetch(pmids):
    out = {}
    for i in range(0, len(pmids), 150):
        data = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids[i:i + 150]), "retmode": "xml"}).encode()
        txt, _ = http(EU + "efetch.fcgi", data=data)
        root = ET.fromstring(txt)
        for art in root.findall(".//PubmedArticle"):
            pmid = art.findtext(".//PMID")
            title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
            ab = " ".join("".join(a.itertext()) for a in art.findall(".//Abstract/AbstractText"))
            doi = next((x.text for x in art.findall(".//ArticleId") if x.get("IdType") == "doi"), "")
            yr = art.findtext(".//PubDate/Year") or (art.findtext(".//PubDate/MedlineDate") or "")[:4]
            types = [t.text for t in art.findall(".//PublicationType")]
            journal = art.findtext(".//Journal/ISOAbbreviation") or ""
            out[pmid] = {"title": title, "abstract": ab, "doi": doi, "year": yr, "types": types, "venue": journal}
        time.sleep(0.4)
    return out


def main():
    have = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    have.setdefault("run_date", time.strftime("%Y-%m-%d"))
    # 1. Xplore-only records
    src = json.load(open(os.path.join(HERE, "ieee_screen.json"), encoding="utf-8"))["ieee_only_records"]
    xs = have.setdefault("xplore_only", {})
    for i, r in enumerate(src, 1):
        if r["doi"] in xs and xs[r["doi"]].get("abstract"):
            continue
        num = ieee_number(r["doi"])
        rec = dict(r, number=num or "")
        if num:
            rec.update(ieee_abstract(num))
        xs[r["doi"]] = rec
        if i % 20 == 0:
            json.dump(have, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
            print(f"xplore {i}/{len(src)}", file=sys.stderr, flush=True)
        time.sleep(0.5)
    json.dump(have, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    # 2. PubMed IoT-term additions
    nb, base = esearch_all(Q_BASE)
    ni, iot = esearch_all(Q_IOT)
    added = sorted(set(iot) - set(base))
    have["pubmed_iot"] = {"query_base": Q_BASE, "query_iot": Q_IOT, "count_base": nb, "count_iot": ni,
                          "added": len(added), "records": efetch(added)}
    json.dump(have, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"done: xplore {len(xs)} ({sum(1 for v in xs.values() if v.get('abstract'))} with abstract); "
          f"pubmed base {nb}, iot {ni}, added {len(added)}", file=sys.stderr)


if __name__ == "__main__":
    main()
