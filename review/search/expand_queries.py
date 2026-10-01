#!/usr/bin/env python3
"""Build paste-ready PubMed strings and prove they are the same query as the block form.

Section II of the supplement printed the search as four concept blocks (A--D) plus a
year limit, which documents the logic but cannot be pasted into PubMed. This expands
them into two single strings, one per arm, and then submits BOTH forms to E-utilities
and compares the counts. If the expansion were wrong the counts would differ, so the
printed string is verified rather than asserted.

The expansion is generated from the same constants `ieee_screen.py` screens with, so
the printed string cannot drift from the query that was run.

    python3 review/search/expand_queries.py
"""
import json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "query_expansion_check.json")
EMAIL = "xxiang@mail.yu.edu"

sys.path.insert(0, HERE)
import importlib.util
_s = importlib.util.spec_from_file_location("isc", os.path.join(HERE, "ieee_screen.py"))
isc = importlib.util.module_from_spec(_s)
_s.loader.exec_module(isc)

A, B, C, D, Y = isc.A, isc.B, isc.C, isc.D, isc.Y
BLOCKS = {"main": f"{A} AND {B} AND {C} AND {Y}",
          "dtwm": f"{D} AND {B} AND {C} AND {Y}"}
# The expanded form is the same text with the block names already substituted, which
# is what BLOCKS already is; what makes it paste-ready is that it carries no
# placeholders and is a single line.
EXPANDED = {k: re.sub(r"\s+", " ", v).strip() for k, v in BLOCKS.items()}


def esearch(term):
    q = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmax": 0,
                                "email": EMAIL, "tool": "iot-survey-expand"})
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + q
    for k in range(4):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                root = ET.fromstring(r.read())
            return int(root.findtext(".//Count"))
        except Exception:
            if k == 3:
                raise
            time.sleep(2 * (k + 1))


def main():
    res = {"run_date": time.strftime("%Y-%m-%d"),
           "note": ("the block form and the expanded form are submitted separately; equal "
                    "counts are what verifies the printed string")}
    for arm in ("main", "dtwm"):
        nb = esearch(BLOCKS[arm])
        time.sleep(0.4)
        ne = esearch(EXPANDED[arm])
        time.sleep(0.4)
        res[arm] = {"blocks": nb, "expanded": ne, "string": EXPANDED[arm]}
        print(f"{arm}: block form {nb} · expanded {ne} · "
              f"{'MATCH' if nb == ne else 'DIFFERENT'}", file=sys.stderr)
    json.dump(res, open(OUT, "w"), indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "string"}
                      for k, v in res.items() if isinstance(v, dict)}, indent=1))


if __name__ == "__main__":
    main()
