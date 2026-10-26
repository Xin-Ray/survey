#!/usr/bin/env python3
"""Apply the ORIGINAL screen.py regexes (verbatim, recovered 2026-09-22) to the 12 studies,
to name the rule that excluded each one that the query did retrieve."""
import json, os, re, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
EMAIL = "xxiang@mail.yu.edu"

NONHEALTH = re.compile(r"\b(air quality|air pollution|pm2\.?5|pm10|ozone|aerosol|visibility|water quality|wastewater|activated sludge|lake|river|streamflow|rainfall|precipitation|wildfire|drought|soil|crop|agricultur|remote sensing|satellite|traffic flow|traffic speed|vehicle|pedestrian flow|fault diagnosis|bearing|machinery|battery|power grid|photovoltaic|structural health monitoring|bibliometric|scientometric)\b", re.I)
HUMAN = re.compile(r"\b(patient|patients|clinical|diagnos|prognos|disease|disorder|mortality|morbidity|incidence|prevalence|epidemiolog|surgery|surgical|rehabilitation|therapy|treatment|screening|lesion|tumou?r|cancer|seizure|stroke|cardiac|depress|glucose|diabet|hospital|icu|public health|outbreak|infection|vaccin)\b", re.I)
PRECLIN = re.compile(r"\b(murine|mice|mouse|rat|rats|in vitro|cell line|zebrafish|porcine|canine|phantom only)\b", re.I)
SPACETIME = re.compile(r"\b(spatio-?temporal|spatiotemporal|space-?time|spatial and temporal|temporal and spatial|longitudinal|time series|time-series|sequential|temporal dynamic|dynamic graph|trajector)\w*", re.I)
METRIC = re.compile(r"\b(accurac\w*|auroc|au-?roc|\bauc\b|f1|f-?score|rmse|mae|mape|dice|sensitivit\w*|specificit\w*|precision|recall|c-?index|concordance|r2|r\^2|correlation coefficient)\b", re.I)
NUMBER = re.compile(r"\d+\.\d+|\b\d{1,3}(\.\d+)?\s?%")
COMPARE = re.compile(r"\b(outperform\w*|compared (?:with|to|against)|comparison with|baseline\w*|state[- ]of[- ]the[- ]art|\bsota\b|versus|vs\.?|superior to|better than|higher than|improv\w+ (?:over|upon)|exceed\w*|benchmark\w*)\b", re.I)

rc = json.load(open(os.path.join(HERE, "recovery_check.json")))
pmids = [r["pmid"] for r in rc["rows"] if r["pmid"]]
q = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "xml", "email": EMAIL})
with urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + q, timeout=60) as r:
    root = ET.fromstring(r.read())
rec = {}
for art in root.findall(".//PubmedArticle"):
    pmid = art.findtext(".//PMID")
    ti = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
    ab = " ".join("".join(t.itertext()) for t in art.findall(".//Abstract/AbstractText"))
    pts = [p.text for p in art.findall(".//PublicationTypeList/PublicationType")]
    rec[pmid] = {"text": ti + " " + ab, "pubtypes": pts}

print(f"{'bibkey':34s} {'PMID':10s} ident r1 r2 r3  rule outcome")
rows = []
for r in rc["rows"]:
    d = rec.get(r["pmid"], {"text": "", "pubtypes": []})
    t = d["text"]
    r1 = not ((NONHEALTH.search(t) and not HUMAN.search(t)) or (PRECLIN.search(t) and not HUMAN.search(t)))
    r2 = bool(SPACETIME.search(t))
    r3 = bool(METRIC.search(t) and NUMBER.search(t) and COMPARE.search(t))
    verdict = "eligible" if (r1 and r2 and r3) else ("excluded_r1" if not r1 else "excluded_r2" if not r2 else "excluded_r3")
    rows.append({**r, "r1": r1, "r2": r2, "r3": r3, "replicated_verdict": verdict, "pubtypes": d["pubtypes"]})
    print(f"{r['bibkey']:34s} {r['pmid']:10s} {'Y' if r['in_identified'] else '.':5s} "
          f"{int(r1)}  {int(r2)}  {int(r3)}   {verdict}"
          + ("   <-- retrieved but screened out" if r["in_identified"] and verdict != "eligible" else "")
          + ("   [in the 363]" if r["in_363_eligible"] else ""))
json.dump(rows, open(os.path.join(HERE, "replicate_rules.json"), "w"), indent=1)
ok = all((r["replicated_verdict"] == "eligible") == r["in_363_eligible"] for r in rows if r["in_identified"])
print()
print("replication consistent with the stored 363 list for every retrieved study:", ok)
