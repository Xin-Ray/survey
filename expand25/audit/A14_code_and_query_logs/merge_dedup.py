#!/usr/bin/env python3
"""Merge PubMed (jsonl) + IEEE Xplore CSV export(s) + Scopus CSV export(s), de-duplicate, log counts.

Place exports in this folder named  ieee_*.csv  and  scopus_*.csv  (any number of files per source).
Dedup key order: DOI (lower-cased) -> normalized title (lower-case alphanumerics only).
Outputs: merged_records.jsonl (fields: source, sources, doi, title, abstract, year, pubtypes), merge_counts.json
"""
import csv, glob, json, os, re, datetime, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))


def norm_title(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", t)


def read_pubmed():
    p = os.path.join(HERE, "pubmed_records.jsonl")
    if not os.path.exists(p):
        return []
    out = []
    for l in open(p):
        r = json.loads(l); r["source"] = "pubmed"; out.append(r)
    return out


def read_ieee():
    out = []
    for f in glob.glob(os.path.join(HERE, "ieee_*.csv")):
        for row in csv.DictReader(open(f, encoding="utf-8-sig")):
            out.append({"source": "ieee", "pmid": "", "doi": (row.get("DOI") or "").lower().strip(),
                        "title": row.get("Document Title", ""), "abstract": row.get("Abstract", ""),
                        "year": row.get("Publication Year", ""), "journal": row.get("Publication Title", ""),
                        "pubtypes": [row.get("Document Identifier", "")], "ieee_url": row.get("PDF Link", "")})
    return out


def read_scopus():
    out = []
    for f in glob.glob(os.path.join(HERE, "scopus_*.csv")):
        for row in csv.DictReader(open(f, encoding="utf-8-sig")):
            out.append({"source": "scopus", "pmid": row.get("PubMed ID", ""), "doi": (row.get("DOI") or "").lower().strip(),
                        "title": row.get("Title", ""), "abstract": row.get("Abstract", ""),
                        "year": row.get("Year", ""), "journal": row.get("Source title", ""),
                        "pubtypes": [row.get("Document Type", "")]})
    return out


def main():
    srcs = {"pubmed": read_pubmed(), "ieee": read_ieee(), "scopus": read_scopus()}
    merged, by_doi, by_title = [], {}, {}
    dup = {"by_doi": 0, "by_title": 0}
    for name in ["pubmed", "ieee", "scopus"]:
        for r in srcs[name]:
            key_d = r.get("doi") or ""
            key_t = norm_title(r.get("title", ""))
            hit = by_doi.get(key_d) if key_d else None
            if hit is None and key_t:
                hit = by_title.get(key_t)
                if hit is not None:
                    dup["by_title"] += 1
            elif hit is not None:
                dup["by_doi"] += 1
            if hit is not None:
                hit["sources"].append(name)
                if not hit.get("abstract") and r.get("abstract"):
                    hit["abstract"] = r["abstract"]
                if not hit.get("pmid") and r.get("pmid"):
                    hit["pmid"] = r["pmid"]
                continue
            r = {**r, "sources": [name]}
            merged.append(r)
            if key_d:
                by_doi[key_d] = r
            if key_t:
                by_title[key_t] = r
    with open(os.path.join(HERE, "merged_records.jsonl"), "w") as f:
        for r in merged:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    counts = {"run_date": datetime.date.today().isoformat(),
              "per_source_records": {k: len(v) for k, v in srcs.items()},
              "total_before_dedup": sum(len(v) for v in srcs.values()),
              "duplicates_removed": dup, "unique_after_dedup": len(merged),
              "in_more_than_one_source": sum(1 for r in merged if len(set(r["sources"])) > 1)}
    json.dump(counts, open(os.path.join(HERE, "merge_counts.json"), "w"), indent=1)
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
