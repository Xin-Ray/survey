#!/usr/bin/env python3
"""Backward and forward citation chasing from the reviews compared in Table I.

Backward: the reference list of each seed review.
Forward:  works that cite each seed review.
Both via OpenAlex. Records are then put through the same three textual eligibility
rules used for the database screen, and deduplicated against the 1,436 PubMed records
already retrieved, so the output says how many genuinely new eligible records the
chase surfaces.
"""
import json, re, time, urllib.parse, urllib.request, sys

UA = {"User-Agent": "survey-citation-chase/1.0 (mailto:767483570xray@gmail.com)"}
OA = "https://api.openalex.org"

SEEDS = {  # bibkey -> DOI of the reviews compared in Table I
 "wang2022deep": "10.1109/TKDE.2020.3025580",
 "samani2026stdl": "10.1007/s11063-026-11874-x",
 "swinckels2024ehr": "10.2196/48320",
 "Busnatu2022": "10.3390/jpm12101656",
 "sun2026irregularmedical": "10.34133/hds.0456",
 "Wang2023Survey": "10.1109/JIOT.2023.3263909",
 "Sel2025VVUQ": "10.1038/s41746-025-01447-y",
 "chen2024genaitwin": "10.1109/JIOT.2024.3421918",
 "amin2021edgeintel": "10.1109/ACCESS.2020.3045115",
 "nguyen2022FLsmarthealthcare": "10.1145/3501296",
 "zhang2022harreview": "10.3390/s22041476",
}

# the three eligibility rules, as textual blocks (same as the database screen)
A = r"spatiotemporal|spatio-temporal|space-time|spatial and temporal"
B = r"deep learning|neural network|transformer|graph neural|convolutional|recurrent|LSTM|GRU"
C = r"health|clinical|patient|wearable|medical|disease|diagnos|hospital"
QUANT = r"\b(accuracy|AUC|AUROC|RMSE|MAE|F1|dice|sensitivity|specificity|error|correlation|outperform|compared with|baseline)\b"

def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1:
                print("   ! fail", url[:90], e, file=sys.stderr); return None
            time.sleep(2 * (i + 1))

def work_by_doi(doi):
    return get(f"{OA}/works/doi:{urllib.parse.quote(doi)}")

def abstract_of(w):
    inv = w.get("abstract_inverted_index") or {}
    if not inv: return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs: pos[i] = word
    return " ".join(pos[k] for k in sorted(pos))

def eligible(w):
    t = (w.get("title") or "") + " " + abstract_of(w)
    if not t.strip(): return False, "no text"
    yr = w.get("publication_year") or 0
    if yr < 2015 or yr > 2026: return False, "outside window"
    if not re.search(A, t, re.I): return False, "no spatial/temporal term"
    if not re.search(B, t, re.I): return False, "no deep-learning term"
    if not re.search(C, t, re.I): return False, "no health term"
    if not re.search(QUANT, t, re.I): return False, "no quantitative result"
    return True, "eligible"

def main():
    have_pmids = set()
    have_dois = set()
    for line in open("pubmed_records.jsonl"):
        try: r = json.loads(line)
        except: continue
        have_pmids.add(str(r.get("pmid")))
        if r.get("doi"): have_dois.add(r["doi"].lower())
    print(f"already retrieved by the database search: {len(have_pmids)} records, {len(have_dois)} with a DOI\n")

    backward, forward = {}, {}
    seed_ids = {}
    for key, doi in SEEDS.items():
        w = work_by_doi(doi)
        if not w: print(f"  {key}: seed not in OpenAlex"); continue
        seed_ids[key] = w["id"]
        refs = w.get("referenced_works") or []
        backward[key] = refs
        n_cit = w.get("cited_by_count") or 0
        forward[key] = n_cit
        print(f"  {key:30s} references: {len(refs):4d}   cited by: {n_cit:5d}")
        time.sleep(0.3)

    # ---- backward: fetch the referenced works in batches ----
    all_refs = sorted({r for v in backward.values() for r in v})
    print(f"\nbackward: {len(all_refs)} distinct referenced works")
    ref_works = []
    for i in range(0, len(all_refs), 50):
        ids = "|".join(x.rsplit("/", 1)[-1] for x in all_refs[i:i+50])
        d = get(f"{OA}/works?filter=openalex_id:{ids}&per-page=50&select=id,doi,title,publication_year,abstract_inverted_index")
        if d: ref_works += d.get("results", [])
        time.sleep(0.3)
    print(f"  fetched {len(ref_works)}")

    # ---- forward: fetch citing works per seed, capped ----
    cit_works, CAP = [], 400
    for key, sid in seed_ids.items():
        sid_short = sid.rsplit("/", 1)[-1]
        cursor, got = "*", 0
        while cursor and got < CAP:
            d = get(f"{OA}/works?filter=cites:{sid_short},from_publication_date:2015-01-01"
                    f"&per-page=200&cursor={cursor}&select=id,doi,title,publication_year,abstract_inverted_index")
            if not d: break
            res = d.get("results", [])
            cit_works += res; got += len(res)
            cursor = (d.get("meta") or {}).get("next_cursor")
            time.sleep(0.3)
        print(f"  forward {key:30s} fetched {got}")
    print(f"forward: {len(cit_works)} records fetched (cap {CAP} per seed)")

    # ---- screen and dedupe ----
    out = {"backward": {}, "forward": {}}
    for label, works in (("backward", ref_works), ("forward", cit_works)):
        seen, elig, new_elig, reasons = set(), [], [], {}
        for w in works:
            if w["id"] in seen: continue
            seen.add(w["id"])
            ok, why = eligible(w)
            reasons[why] = reasons.get(why, 0) + 1
            if not ok: continue
            elig.append(w)
            doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
            if doi and doi in have_dois: continue
            new_elig.append({"id": w["id"], "doi": doi, "title": w.get("title"),
                             "year": w.get("publication_year")})
        out[label] = {"distinct": len(seen), "rule_eligible": len(elig),
                      "not_already_retrieved": len(new_elig), "reasons": reasons,
                      "new": new_elig[:60]}
        print(f"\n{label}: {len(seen)} distinct -> {len(elig)} rule-eligible -> "
              f"{len(new_elig)} not already retrieved by the database search")
    out["seeds"] = {k: {"doi": SEEDS[k], "references": len(backward.get(k, [])),
                        "cited_by": forward.get(k)} for k in SEEDS}
    json.dump(out, open("citation_chase.json", "w"), indent=1)
    print("\nwritten: citation_chase.json")

if __name__ == "__main__":
    main()
