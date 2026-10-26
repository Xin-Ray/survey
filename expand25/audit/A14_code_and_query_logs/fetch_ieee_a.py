#!/usr/bin/env python3
"""Export the records of IEEE Xplore arm A (the spatiotemporal arm).

Arm B was exported from the web interface on 2026-09-22 (`ieee_b.csv`, 274 rows);
arm A never was, because its 928 records exceed what that interface will hand
over in one download. This script pages the same search endpoint the results page
itself calls, and writes the records with the column names of `ieee_b.csv` so the
two arms can be screened by one script.

    python3 fetch_ieee_a.py            # writes ieee_a.csv and ieee_a_raw.json
"""
import csv, json, os, sys, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
COUNTS = os.path.join(HERE, "ieee_counts.json")
OUT_CSV = os.path.join(HERE, "ieee_a.csv")
OUT_RAW = os.path.join(HERE, "ieee_a_raw.json")
ENDPOINT = "https://ieeexplore.ieee.org/rest/search"

# Only the columns ieee_b.csv carries that this endpoint also returns; the rest
# are written empty so the two files have identical headers.
HEADER = ["Document Title", "Authors", "Author Affiliations", "Publication Title",
          "Date Added To Xplore", "Publication Year", "Volume", "Issue", "Start Page",
          "End Page", "Abstract", "ISSN", "ISBNs", "DOI", "Funding Information",
          "PDF Link", "Author Keywords", "IEEE Terms", "Mesh_Terms",
          "Article Citation Count", "Patent Citation Count", "Reference Count",
          "License", "Online Date", "Issue Date", "Meeting Date", "Publisher",
          "Document Identifier"]


def post(query, page):
    body = json.dumps({"queryText": query, "rowsPerPage": 100, "pageNumber": page,
                       "ranges": ["2015_2026_Year"], "returnType": "SEARCH",
                       "returnFacets": ["ALL"]}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={
        "Content-Type": "application/json", "Accept": "application/json",
        "Origin": "https://ieeexplore.ieee.org",
        "Referer": "https://ieeexplore.ieee.org/search/searchresult.jsp",
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))


def row(rec):
    auth = "; ".join(a.get("normalizedName") or a.get("preferredName") or ""
                     for a in rec.get("authors") or [])
    aff = "; ".join((a.get("affiliation") or [""])[0] if isinstance(a.get("affiliation"), list)
                    else (a.get("affiliation") or "") for a in rec.get("authors") or [])
    d = {h: "" for h in HEADER}
    d.update({
        "Document Title": rec.get("articleTitle", ""),
        "Authors": auth,
        "Author Affiliations": aff,
        "Publication Title": rec.get("publicationTitle") or rec.get("displayPublicationTitle", ""),
        "Publication Year": rec.get("publicationYear", ""),
        "Volume": rec.get("volume", ""),
        "Issue": rec.get("issue", ""),
        "Start Page": rec.get("startPage", ""),
        "End Page": rec.get("endPage", ""),
        "Abstract": rec.get("abstract", ""),
        "DOI": rec.get("doi", ""),
        "PDF Link": rec.get("documentLink", ""),
        "Article Citation Count": rec.get("citationCount", ""),
        "Patent Citation Count": rec.get("patentCitationCount", ""),
        "Publisher": rec.get("publisher", ""),
        "Document Identifier": rec.get("contentType", ""),
        "Issue Date": rec.get("publicationDate", ""),
    })
    return d


def main():
    query = json.load(open(COUNTS))["queries"]["A_spatiotemporal"]
    recs, total, page = [], None, 1
    while True:
        j = post(query, page)
        total = j.get("totalRecords", total)
        batch = j.get("records") or []
        if not batch:
            break
        recs.extend(batch)
        print(f"page {page}: +{len(batch)} → {len(recs)} of {total}", file=sys.stderr)
        if len(recs) >= (total or 0):
            break
        page += 1
        time.sleep(1.0)

    json.dump({"run_date": time.strftime("%Y-%m-%d"), "endpoint": ENDPOINT,
               "query": query, "total_reported": total, "records": recs},
              open(OUT_RAW, "w"))
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in recs:
            w.writerow(row(r))
    print(f"total reported {total} · exported {len(recs)} → {OUT_CSV}")


if __name__ == "__main__":
    main()
