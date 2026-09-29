#!/usr/bin/env python3
"""OpenAlex run of the protocol's two arms (programmatic, logged).

Two scopes are written:
  --scope ieee : restricted to IEEE-published venues (cross-check for the IEEE Xplore UI count)
  --scope all  : all sources (stand-in / cross-check for Scopus)
Outputs: openalex_<scope>_counts.json, openalex_<scope>_records.jsonl
"""
import argparse, datetime, json, os, time, urllib.parse, urllib.request

EMAIL = "xxiang@mail.yu.edu"
HERE = os.path.dirname(os.path.abspath(__file__))
IEEE_PUBLISHER = "P4310319808"   # OpenAlex id for IEEE

ST = '(spatiotemporal OR "spatio-temporal" OR "spatial-temporal" OR "space-time" OR "spatial and temporal")'
DL = '("deep learning" OR "neural network" OR "neural networks" OR transformer OR transformers OR "graph neural" OR LSTM OR recurrent OR convolutional OR "deep neural")'
HL = ('("digital health" OR wearable OR wearables OR "internet of things" OR IoT OR "mobile health" OR mHealth OR "remote monitoring" OR "continuous glucose" '
      'OR "electronic health record" OR "electronic health records" OR diabetes OR depression OR cardiac OR cardiovascular OR diet OR dietary '
      'OR "chronic disease" OR "chronic diseases" OR "public health" OR "clinical prediction" OR "disease prediction" OR clinical OR patient OR patients OR health)')
TW = '("digital twin" OR "digital twins" OR "world model" OR "world models")'
ARMS = {"A_spatiotemporal": f"{ST} AND {DL} AND {HL}", "B_twin_worldmodel": f"{TW} AND {DL} AND {HL}"}


def get(url, tries=4):
    req = urllib.request.Request(url, headers={"User-Agent": f"survey-search/1.0 (mailto:{EMAIL})"})
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception:
            time.sleep(2 * (k + 1))
    raise RuntimeError("fetch failed " + url[:100])


def abstract_of(w):
    inv = w.get("abstract_inverted_index") or {}
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def run_arm(query, scope):
    filt = "from_publication_date:2015-01-01,to_publication_date:2026-12-31,type:article|preprint|book-chapter|dissertation|report"
    if scope == "ieee":
        filt += f",primary_location.source.host_organization:{IEEE_PUBLISHER}"
    base = {"search": query, "filter": filt, "per-page": 200, "mailto": EMAIL,
            "select": "id,doi,title,publication_year,type,primary_location,abstract_inverted_index,authorships"}
    cursor, out = "*", []
    while cursor:
        u = "https://api.openalex.org/works?" + urllib.parse.urlencode({**base, "cursor": cursor})
        j = get(u)
        for w in j["results"]:
            loc = w.get("primary_location") or {}
            src = (loc.get("source") or {})
            out.append({"openalex": w["id"], "doi": (w.get("doi") or "").replace("https://doi.org/", "").lower(),
                        "title": w.get("title") or "", "abstract": abstract_of(w), "year": w.get("publication_year"),
                        "type": w.get("type"), "venue": src.get("display_name") or "", "publisher": src.get("host_organization_name") or "",
                        "authors": [ (a.get("author") or {}).get("display_name", "") for a in w.get("authorships", [])][:6]})
        cursor = j["meta"].get("next_cursor")
        print(f"  {len(out)}/{j['meta']['count']}")
        time.sleep(0.2)
    return j["meta"]["count"], out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--scope", choices=["ieee", "all"], required=True)
    a = ap.parse_args()
    run = {"run_date": datetime.date.today().isoformat(), "database": f"OpenAlex ({a.scope})", "queries": ARMS, "counts": {}}
    recs = {}
    for arm, q in ARMS.items():
        n, rows = run_arm(q, a.scope)
        run["counts"][arm] = n
        print(arm, n)
        for r in rows:
            recs.setdefault(r["openalex"], {**r, "arms": []})["arms"].append(arm)
    run["counts"]["overlap_A_and_B"] = sum(1 for r in recs.values() if len(r["arms"]) == 2)
    run["counts"]["union_unique"] = len(recs)
    with open(os.path.join(HERE, f"openalex_{a.scope}_records.jsonl"), "w") as f:
        for r in recs.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump(run, open(os.path.join(HERE, f"openalex_{a.scope}_counts.json"), "w"), indent=1)
    print(json.dumps(run["counts"], indent=1))


if __name__ == "__main__":
    main()
