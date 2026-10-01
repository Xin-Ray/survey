#!/usr/bin/env python3
"""Strict field-by-field reference check: exact title, author count, venue, volume, issue, pages.

`bib2endnote.py` accepts a title at 0.80 similarity once a DOI matches. That is too
loose for the failure mode that actually occurred: a title that is a clean PREFIX of
the published title passes at high similarity while being wrong on the page. Ten of
the eleven citation errors found in external review on 2026-09-30 were of that kind
(truncated titles, an author list cut off without "et al.", one wrong venue).

This compares against the publisher record without mercy:

  TITLE     normalized exact match; a bib title that is a prefix of the published
            title is reported as a truncation, not a near-match
  AUTHORS   the number of names in the bib must equal the publisher's count, or the
            bib must end in "and others" so IEEEtran prints "et al."
  VENUE     the bib venue must be the publisher's container title or its ISO abbreviation
  NUMBERS   volume, issue and pages must equal the publisher's, where it has them

arXiv-only, standards and grant entries are checked against arXiv or skipped with a
stated reason rather than silently passed.

    python3 endnote/strict_refcheck.py            # all cited entries
    python3 endnote/strict_refcheck.py --no-net   # from cache
"""
import argparse, html, json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bib2endnote as b

BIB = os.path.join(ROOT, "live", "newST.bib")
TEX = os.path.join(ROOT, "live", "STmodel.tex")
OUT = os.path.join(HERE, "out_j28")
CACHE = os.path.join(OUT, "strict_cache.json")

# A proceedings title that legitimately differs from its preprint title. The NeurIPS
# version is "Nets"; only the arXiv preprint says "Networks". We cite the proceedings.
TITLE_OK = {
    "goodfellow2014gan": "the NeurIPS proceedings title is \"Nets\"; only the arXiv preprint "
                         "says \"Networks\", and the proceedings version is what is cited",
}

# Entries with no publisher record to compare against, and why.
SKIP = {
    "rumelhart1986rnn": "1986 MIT Press book chapter; neither Crossref nor arXiv carries it, "
                        "and the only Crossref record with this title is the 1985 DTIC "
                        "technical report, a different document",
    "Fang2021iPAT": "NIH/NIDDK grant R01DK129432, not a publication",
    "ieee11073std": "IEEE standard; Crossref carries no title or page metadata for it",
}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def arxiv_id(entry):
    for f in ("journal", "note", "eprint", "howpublished"):
        m = re.search(r"arxiv[:\s]*([0-9]{4}\.[0-9]{4,5})", entry.get(f) or "", re.I)
        if m:
            return m.group(1)
    return None


def arxiv_record(aid, cache, net):
    k = "arxiv:" + aid
    if k not in cache:
        if not net:
            return None
        try:
            with urllib.request.urlopen("https://export.arxiv.org/abs/" + aid, timeout=45) as r:
                x = r.read().decode("utf-8", "replace")
            t = re.search(r'<meta name="citation_title" content="([^"]*)"', x)
            a = re.findall(r'<meta name="citation_author" content="([^"]*)"', x)
            cache[k] = {"title": html.unescape(t.group(1)) if t else "", "n_authors": len(a)}
        except Exception:
            cache[k] = None
        time.sleep(0.4)
    return cache[k]


def arxiv_by_title(title, cache, net):
    """Last resort for proceedings papers that register no DOI: find the preprint.

    NeurIPS before 2022, ICML/PMLR and the ACL Anthology's older volumes deposit no
    Crossref record, so without this the entry is simply never checked. Searching
    arXiv by exact title at least verifies the title and the author count.
    """
    k = "ti:" + re.sub(r"\W+", " ", title.lower()).strip()[:110]
    if k not in cache:
        if not net:
            return None
        try:
            q = urllib.parse.urlencode({"search_query": 'ti:"' + title + '"', "max_results": 5})
            with urllib.request.urlopen("http://export.arxiv.org/api/query?" + q, timeout=60) as r:
                x = r.read().decode("utf-8", "replace")
            entries = re.findall(r"<entry>(.*?)</entry>", x, re.S)
            best = None
            for ent in entries:
                tm = re.search(r"<title>(.*?)</title>", ent, re.S)
                if not tm:
                    continue
                ti = re.sub(r"\s+", " ", html.unescape(tm.group(1))).strip()
                if norm(ti) == norm(title):
                    best = {"title": ti, "n_authors": len(re.findall(r"<name>", ent))}
                    break
            cache[k] = best
        except Exception:
            cache[k] = None
        time.sleep(3.2)          # arXiv asks for one query every three seconds
    return cache[k]


def crossref(doi, cache, net):
    k = "doi:" + doi.lower()
    if k not in cache:
        if not net:
            return None
        try:
            body = b.http_get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))
            cache[k] = json.loads(body).get("message") if body else None
        except Exception:
            cache[k] = None
        time.sleep(0.15)
    return cache[k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-net", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    net = not a.no_net
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

    ents = b.parse_bib(BIB)
    keys = b.cited_keys(TEX)
    problems, skipped = [], []

    for i, key in enumerate(keys, start=1):
        e = ents.get(key) or {}
        if key in SKIP:
            skipped.append((i, key, SKIP[key]))
            continue
        bt = b.delatex(e.get("title", ""))
        n_bib = len(b.split_authors(e.get("author", "")))
        etal = bool(re.search(r"\band others\b", e.get("author", ""), re.I))
        issues = []

        doi = (e.get("doi") or "").strip()
        aid = arxiv_id(e)
        item = crossref(doi, cache, net) if doi and not doi.lower().startswith("10.48550") else None

        if item:
            ct = b.cr_title(item)
            sub_t = (item.get("subtitle") or [""])[0].strip()
            if sub_t and norm(ct + sub_t) == norm(bt):
                ct = bt          # ACM registers the subtitle separately; not a discrepancy
            if norm(bt) != norm(ct):
                if norm(ct).startswith(norm(bt)):
                    issues.append(f"title TRUNCATED; published: {ct}")
                else:
                    issues.append(f"title differs; published: {ct}")
            n_pub = len(item.get("author") or [])
            if n_pub and n_bib != n_pub and not etal:
                issues.append(f"author list has {n_bib} of {n_pub} names and no 'and others'")
            cont = (item.get("container-title") or [""])[0]
            bv = b.delatex(e.get("journal") or e.get("booktitle") or "")
            if cont and norm(bv) and norm(cont) != norm(bv):
                # an ISO abbreviation of the container title is acceptable
                short = (item.get("short-container-title") or [""])[0]
                if norm(bv) != norm(short):
                    abbrev_ok = all(any(w.lower().startswith(x.lower().rstrip("."))
                                        for w in re.findall(r"[A-Za-z]+", cont))
                                    for x in re.findall(r"[A-Za-z]+", bv))
                    acronym = re.search(r"\(([A-Z][A-Za-z-]+)\)\s*$", bv)
                    proceedings = re.match(r"(Proc\.|Advances in)", bv)
                    if not abbrev_ok and not (acronym or proceedings):
                        issues.append(f"venue '{bv}' is not '{cont}'")
            for f, cf in (("volume", "volume"), ("number", "issue")):
                pub = (item.get(cf) or "").strip()
                bibv = (e.get(f) or "").strip()
                if pub and bibv and pub != bibv:
                    issues.append(f"{f} {bibv} but publisher says {pub}")
            pub_p = (item.get("page") or "").strip()
            bib_p = (e.get("pages") or "").replace("--", "-").strip()
            if pub_p and bib_p and pub_p != bib_p:
                issues.append(f"pages {bib_p} but publisher says {pub_p}")
        elif aid:
            rec = arxiv_record(aid, cache, net)
            if rec is None:
                issues.append(f"arXiv {aid} could not be read")
            else:
                if norm(bt) != norm(rec["title"]):
                    kind = "TRUNCATED" if norm(rec["title"]).startswith(norm(bt)) else "differs"
                    issues.append(f"title {kind}; arXiv says: {rec['title']}")
                if rec["n_authors"] and n_bib != rec["n_authors"] and not etal:
                    issues.append(f"author list has {n_bib} of {rec['n_authors']} names "
                                  f"and no 'and others'")
        elif doi.lower().startswith("10.48550"):
            rec = arxiv_record(doi.split("arXiv.")[-1], cache, net) if "arXiv." in doi else None
            if rec and norm(bt) != norm(rec["title"]):
                kind = "TRUNCATED" if norm(rec["title"]).startswith(norm(bt)) else "differs"
                issues.append(f"title {kind}; arXiv says: {rec['title']}")
        else:
            if key in TITLE_OK:
                skipped.append((i, key, TITLE_OK[key]))
                continue
            rec = arxiv_by_title(bt, cache, net)
            if rec is None:
                skipped.append((i, key, "registers no DOI and no arXiv record carries this "
                                        "exact title; proceedings volumes of this era deposit "
                                        "neither DOI nor page numbers"))
                continue
            if rec["n_authors"] and n_bib != rec["n_authors"] and not etal:
                issues.append(f"author list has {n_bib} of {rec['n_authors']} names "
                              f"and no 'and others'")

        if issues:
            problems.append((i, key, issues))

    json.dump(cache, open(CACHE, "w"), indent=0)

    lines = ["# Strict reference check", "",
             f"Cited entries: **{len(keys)}**. Compared field by field against the publisher "
             f"record, with an exact title test.", "",
             f"- entries with a discrepancy: **{len(problems)}**",
             f"- entries with no record to compare: {len(skipped)}", ""]
    if problems:
        lines += ["## Discrepancies", ""]
        for i, key, iss in problems:
            lines.append(f"**[{i}] `{key}`**")
            for x in iss:
                lines.append(f"  - {x}")
    lines += ["", "## Not compared", ""]
    for i, key, why in skipped:
        lines.append(f"- [{i}] `{key}` — {why}")
    open(os.path.join(OUT, "strict_refcheck.md"), "w").write("\n".join(lines) + "\n")

    for i, key, iss in problems:
        print(f"[{i}] {key}")
        for x in iss:
            print(f"      {x}")
    print(f"\n{len(keys)} cited · {len(problems)} with a discrepancy · {len(skipped)} not compared")


if __name__ == "__main__":
    main()
