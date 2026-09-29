#!/usr/bin/env python3
"""
bib2endnote.py — verify every cited BibTeX entry against Crossref / arXiv and
emit an EndNote-importable library (EndNote XML + RIS) in which each record
carries the citation metadata and the *actual* link to the paper
(https://doi.org/<doi>, or the arXiv abstract page), plus a verification report.

Stdlib only (no pip installs needed).

Usage:
    python3 bib2endnote.py --bib ../version3-IOT8page/newST.bib \
                           --tex ../version3-IOT8page/STmodel.tex \
                           --out out/

    --all       include every bib entry, not only the keys cited in the .tex
    --no-net    rebuild outputs from cache.json without hitting the network
"""
import argparse
import csv
import difflib
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

MAILTO = "xxiang@mail.yu.edu"          # Crossref "polite pool" contact
UA = f"bib2endnote/1.0 (mailto:{MAILTO})"
TITLE_OK_DOI = 0.80     # title similarity required when the bib already has a DOI
TITLE_OK_SEARCH = 0.90  # stricter when we *search* for a DOI by title

# --------------------------------------------------------------------------- #
# BibTeX parsing
# --------------------------------------------------------------------------- #
LATEX_ACCENTS = {
    r"\'": "", r"\`": "", r'\"': "", r"\^": "", r"\~": "", r"\v": "",
    r"\c": "", r"\u": "", r"\H": "", r"\.": "", r"\=": "", r"\b": "",
    r"\ss": "ss", r"\o": "o", r"\O": "O", r"\l": "l", r"\L": "L",
    r"\ae": "ae", r"\AE": "AE", r"\aa": "a", r"\AA": "A", r"\i": "i",
    r"\&": "&", r"\%": "%", r"\_": "_", r"\#": "#", r"\$": "$",
    r"\textendash": "-", r"\textemdash": "-", r"---": "-", r"--": "-",
    r"\ldots": "...", r"\textquoteright": "'", r"\textquoteleft": "'",
}


def delatex(s: str) -> str:
    """Strip braces and common LaTeX accent commands to plain text."""
    if not s:
        return ""
    s = s.replace("~", " ").replace("\n", " ")
    for k, v in LATEX_ACCENTS.items():
        s = s.replace(k, v)
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)   # any leftover \command
    s = s.replace("{", "").replace("}", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_bib(path: str) -> dict:
    """Minimal but robust BibTeX parser: returns {key: {type, fields...}}."""
    text = open(path, encoding="utf-8", errors="replace").read()
    entries = {}
    i = 0
    n = len(text)
    while True:
        at = text.find("@", i)
        if at < 0:
            break
        m = re.match(r"@(\w+)\s*[{(]", text[at:])
        if not m:
            i = at + 1
            continue
        etype = m.group(1).lower()
        if etype in ("comment", "preamble", "string"):
            i = at + 1
            continue
        body_start = at + m.end()
        # find matching close brace
        depth, j = 1, body_start
        while j < n and depth:
            c = text[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            j += 1
        body = text[body_start:j - 1]
        i = j
        km = re.match(r"\s*([^,\s]+)\s*,", body)
        if not km:
            continue
        key = km.group(1)
        fields = {"type": etype, "key": key}
        rest = body[km.end():]
        # field = {..} | "..." | bareword
        p = 0
        while p < len(rest):
            fm = re.match(r"\s*(\w[\w\-]*)\s*=\s*", rest[p:])
            if not fm:
                nxt = rest.find(",", p)
                if nxt < 0:
                    break
                p = nxt + 1
                continue
            name = fm.group(1).lower()
            p += fm.end()
            if p >= len(rest):
                break
            if rest[p] == "{":
                depth, q = 1, p + 1
                while q < len(rest) and depth:
                    if rest[q] == "{":
                        depth += 1
                    elif rest[q] == "}":
                        depth -= 1
                    q += 1
                val = rest[p + 1:q - 1]
                p = q
            elif rest[p] == '"':
                q = p + 1
                while q < len(rest) and rest[q] != '"':
                    q += 1
                val = rest[p + 1:q]
                p = q + 1
            else:
                q = p
                while q < len(rest) and rest[q] not in ",\n}":
                    q += 1
                val = rest[p:q]
                p = q
            fields[name] = val.strip()
            nxt = rest.find(",", p)
            if nxt < 0:
                break
            p = nxt + 1
        entries[key] = fields
    return entries


def strip_extended(tex: str) -> str:
    """Drop the \\else branch of every \\ifsubmission ... \\else ... \\fi block
    (the 8-page submission build has \\submissiontrue), handling nesting."""
    tex = re.sub(r"\\newif\\if[a-zA-Z@]*", "", tex)   # declarations are not conditionals
    toks = list(re.finditer(r"\\(ifsubmission|if[a-zA-Z@]*|else|fi)\b", tex))
    out, pos = [], 0
    stack = []          # each item: [is_submission_if, in_else_branch]
    for m in toks:
        word = m.group(1)
        # emit text up to this token unless we're inside a dropped else-branch
        if not any(s[0] and s[1] for s in stack):
            out.append(tex[pos:m.start()])
        pos = m.end()
        if word.startswith("if"):
            stack.append([word == "ifsubmission", False])
        elif word == "else":
            if stack:
                stack[-1][1] = True
        elif word == "fi":
            if stack:
                stack.pop()
    if not any(s[0] and s[1] for s in stack):
        out.append(tex[pos:])
    return "".join(out)


def cited_keys(tex_path: str) -> list:
    """Keys cited by the 8-page submission build.

    Preferred source: the .aux file next to the .tex (exactly what the last
    build cited).  Fallback: scan the .tex with the extended-only
    \\ifsubmission\\else...\\fi branches removed."""
    keys = []
    aux_path = os.path.splitext(tex_path)[0] + ".aux"
    if os.path.exists(aux_path):
        aux = open(aux_path, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"\\citation\{([^}]*)\}", aux):
            for k in m.group(1).split(","):
                k = k.strip()
                if k and k not in keys:
                    keys.append(k)
        print(f"cited keys taken from {aux_path}: {len(keys)}")
        return keys
    tex = open(tex_path, encoding="utf-8", errors="replace").read()
    tex = re.sub(r"(?<!\\)%.*", "", tex)  # drop comments
    tex = strip_extended(tex)
    for m in re.finditer(r"\\(?:no)?cite[a-zA-Z]*\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}", tex):
        for k in m.group(1).split(","):
            k = k.strip()
            if k and k not in keys:
                keys.append(k)
    print(f"cited keys scanned from {tex_path} (extended blocks removed): {len(keys)}")
    return keys


# --------------------------------------------------------------------------- #
# Name handling
# --------------------------------------------------------------------------- #
def split_authors(author_field: str) -> list:
    """'F. Tao and H. Zhang and others' -> [('Tao','F.'), ('Zhang','H.')]"""
    out = []
    raw = delatex(author_field)
    for a in re.split(r"\s+and\s+", raw):
        a = a.strip()
        if not a or a.lower() in ("others", "et al", "et al."):
            continue
        if "," in a:
            last, first = [x.strip() for x in a.split(",", 1)]
        else:
            parts = a.split()
            if len(parts) == 1:
                last, first = parts[0], ""
            else:
                # keep particles (van, de, der ...) with the surname
                idx = len(parts) - 1
                while idx > 0 and parts[idx - 1].lower() in ("van", "von", "de", "der", "den", "del", "da", "di", "le", "la"):
                    idx -= 1
                last, first = " ".join(parts[idx:]), " ".join(parts[:idx])
        out.append((last, first))
    return out


def surname_key(last: str) -> str:
    s = unicodedata.normalize("NFKD", last).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s.lower())


def norm_title(t: str) -> str:
    t = delatex(t)
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-z0-9 ]", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def title_sim(a: str, b: str) -> float:
    a, b = norm_title(a), norm_title(b)
    if not a or not b:
        return 0.0
    r = difflib.SequenceMatcher(None, a, b).ratio()
    # also accept when one title is a clean prefix of the other (subtitle dropped)
    if a.startswith(b) or b.startswith(a):
        r = max(r, min(len(a), len(b)) / max(len(a), len(b)) + 0.15)
    return min(r, 1.0)


# --------------------------------------------------------------------------- #
# Network
# --------------------------------------------------------------------------- #
def http_get(url: str, accept: str = "application/json", retries: int = 3):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 429 or e.code >= 500:
                time.sleep(2 * (attempt + 1))
                continue
            return None
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return None


def crossref_by_doi(doi: str):
    body = http_get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))
    if not body:
        return None
    try:
        return json.loads(body)["message"]
    except Exception:
        return None


def crossref_search(title: str, first_author: str, rows: int = 5):
    q = {"query.bibliographic": delatex(title), "rows": rows, "mailto": MAILTO}
    if first_author:
        q["query.author"] = first_author
    body = http_get("https://api.crossref.org/works?" + urllib.parse.urlencode(q))
    if not body:
        return []
    try:
        return json.loads(body)["message"]["items"]
    except Exception:
        return []


def _arxiv_parse(body: str) -> list:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return []
    for e in root.findall("a:entry", ns):
        out.append({
            "title": (e.findtext("a:title", "", ns) or "").strip(),
            "id": (e.findtext("a:id", "", ns) or "").strip(),
            "authors": [a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)],
            "published": (e.findtext("a:published", "", ns) or "")[:4],
            "doi": (e.findtext("{http://arxiv.org/schemas/atom}doi", "") or "").strip(),
        })
    return out


def arxiv_search(title: str, rows: int = 5, author: str = ""):
    """Title search: exact phrase first, then all-words (catches 'Nets' vs 'Networks')."""
    t = norm_title(title)
    q = "ti:" + urllib.parse.quote(f'"{t}"')
    body = http_get(f"http://export.arxiv.org/api/query?search_query={q}&max_results={rows}", accept="application/atom+xml")
    res = _arxiv_parse(body) if body else []
    if res:
        return res
    words = [w for w in t.split() if len(w) > 2][:8]
    if not words:
        return []
    q = "+AND+".join("ti:" + urllib.parse.quote(w) for w in words)
    if author:
        q += "+AND+au:" + urllib.parse.quote(surname_key(author))
    body = http_get(f"http://export.arxiv.org/api/query?search_query={q}&max_results={rows}", accept="application/atom+xml")
    return _arxiv_parse(body) if body else []


def arxiv_by_id(arxiv_id: str):
    body = http_get(f"http://export.arxiv.org/api/query?id_list={urllib.parse.quote(arxiv_id)}", accept="application/atom+xml")
    res = _arxiv_parse(body) if body else []
    return res[0] if res else None


def openalex_search(title: str, rows: int = 5, author: str = ""):
    q = {"search": delatex(title), "per-page": rows, "mailto": MAILTO}
    if author:
        q["filter"] = "raw_author_name.search:" + surname_key(author)
    body = http_get("https://api.openalex.org/works?" + urllib.parse.urlencode(q))
    if not body:
        return []
    try:
        items = json.loads(body)["results"]
    except Exception:
        return []
    out = []
    for it in items:
        auths = []
        for a in it.get("authorships", []):
            nm = (a.get("author") or {}).get("display_name") or ""
            if nm:
                parts = nm.split()
                auths.append((parts[-1], " ".join(parts[:-1])))
        loc = it.get("primary_location") or {}
        src = (loc.get("source") or {}).get("display_name") or ""
        doi = (it.get("doi") or "").replace("https://doi.org/", "")
        out.append({"title": it.get("title") or "", "authors": auths, "year": it.get("publication_year"),
                    "doi": doi, "url": loc.get("landing_page_url") or it.get("id") or "", "venue": src})
    return out


def cr_title(item) -> str:
    t = item.get("title") or []
    return t[0] if t else ""


def cr_authors(item) -> list:
    return [(a.get("family", ""), a.get("given", "")) for a in item.get("author", []) if a.get("family") or a.get("name")]


def cr_year(item):
    for k in ("published-print", "published-online", "issued", "created"):
        dp = item.get(k, {}).get("date-parts", [[None]])
        if dp and dp[0] and dp[0][0]:
            return dp[0][0]
    return None


def dblp_search(title: str, rows: int = 5):
    """DBLP indexes ICLR/NeurIPS/ICML etc. and gives the publisher/OpenReview link."""
    q = {"q": delatex(title), "format": "json", "h": rows}
    body = http_get("https://dblp.org/search/publ/api?" + urllib.parse.urlencode(q))
    if not body:
        return []
    try:
        hits = json.loads(body)["result"]["hits"].get("hit", [])
    except Exception:
        return []
    out = []
    for h in hits:
        info = h.get("info", {})
        auths = info.get("authors", {}).get("author", [])
        if isinstance(auths, dict):
            auths = [auths]
        names = [re.sub(r"\s+\d{4}$", "", a.get("text", "")) for a in auths]
        out.append({"title": (info.get("title") or "").rstrip("."), "year": info.get("year"),
                    "authors": [(n.split()[-1], " ".join(n.split()[:-1])) for n in names if n],
                    "doi": (info.get("doi") or "").lower(), "url": info.get("ee") or info.get("url") or "",
                    "venue": info.get("venue") or ""})
    return out


# --------------------------------------------------------------------------- #
# Verification
# --------------------------------------------------------------------------- #
def author_check(bib_authors, ext_authors) -> str:
    """Compare surname lists. Returns 'match' | 'partial' | 'MISMATCH' | 'n/a'."""
    if not bib_authors or not ext_authors:
        return "n/a"
    b = [surname_key(l) for l, _ in bib_authors]
    e = [surname_key(l) for l, _ in ext_authors]
    if not b or not e:
        return "n/a"
    first_ok = b[0] == e[0] or (b[0] in e[0]) or (e[0] in b[0])
    overlap = sum(1 for s in b if any(s == x or (len(s) > 3 and (s in x or x in s)) for x in e))
    if first_ok and overlap == len(b):
        return "match"
    if first_ok and overlap >= max(1, len(b) - 1):
        return "partial"
    return "MISMATCH"


def _year_close(bib_year, ext_year, tol: int = 1) -> bool:
    try:
        return abs(int(re.sub(r"\D", "", str(bib_year or "")) or 0) - int(ext_year or 0)) <= tol
    except ValueError:
        return True


def _accept_ext(res, entry, authors, *, title, ext_title, ext_authors, ext_year, doi, link, venue, source, note):
    sim = title_sim(title, ext_title)
    ac = author_check(authors, ext_authors)
    year_ok = _year_close(entry.get("year"), ext_year)
    good = (sim >= TITLE_OK_SEARCH and ac in ("match", "partial")) or (sim >= 0.80 and ac == "match")
    if good and year_ok:
        res.update(doi=doi, link=link, source=source, ext_title=ext_title, ext_authors=ext_authors,
                   ext_year=ext_year, ext_venue=venue, title_sim=round(sim, 3), author_check=ac, status="verified")
        res["note"] += note
        return True
    if sim >= 0.95 and ac == "MISMATCH" and year_ok and res["status"] == "unverified":
        # same title exists, but the bib's author list does not match the record -> surface it
        res.update(doi=doi, link=link, source=source, ext_title=ext_title, ext_authors=ext_authors,
                   ext_year=ext_year, ext_venue=venue, title_sim=round(sim, 3), author_check=ac,
                   status="AUTHOR-MISMATCH")
        res["note"] = "title matches this record but bib authors differ: " + "; ".join(f"{l}, {f}" for l, f in ext_authors[:8])
    return False


def verify(entry: dict, cache: dict, use_net: bool) -> dict:
    key = entry["key"]
    if key in cache and not use_net:
        return cache[key]
    if key in cache and cache[key].get("status") not in ("unverified", "error"):
        return cache[key]

    title = entry.get("title", "")
    authors = split_authors(entry.get("author", "") or entry.get("editor", ""))
    first = authors[0][0] if authors else ""
    res = {"key": key, "status": "unverified", "doi": "", "link": "", "source": "",
           "ext_title": "", "ext_authors": [], "ext_year": None, "ext_venue": "",
           "title_sim": 0.0, "author_check": "n/a", "note": ""}

    doi = (entry.get("doi") or "").strip()
    doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", doi, flags=re.I)
    url = (entry.get("url") or "").strip()
    if not doi and url:
        m = re.search(r"doi\.org/(10\.\S+)", url)
        if m:
            doi = m.group(1)
    if not doi:
        m = re.search(r"10\.\d{4,9}/\S+", entry.get("note", "") + " " + entry.get("howpublished", ""))
        if m:
            doi = m.group(0).rstrip(".,")

    if not url:
        m = re.search(r"https?://[^\s}]+", entry.get("note", "") + " " + entry.get("howpublished", ""))
        if m:
            url = m.group(0).rstrip(".,;")

    # 0) arXiv paper: DOI 10.48550/arXiv.<id>, arXiv URL, or 'arXiv:<id>' in journal/note/eprint
    m = re.match(r"10\.48550/arxiv\.(.+)$", doi, flags=re.I) if doi else None
    if not m and url:
        m = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5}(?:v\d+)?|[a-z\-]+/\d{7})", url, flags=re.I)
    if not m:
        m = re.search(r"arxiv:\s*([0-9]{4}\.[0-9]{4,5}(?:v\d+)?)",
                      " ".join(entry.get(f, "") for f in ("journal", "note", "eprint", "howpublished")), flags=re.I)
    if m and use_net:
        a = arxiv_by_id(m.group(1))
        time.sleep(0.3)
        if a:
            ext_auth = [(n.split()[-1], " ".join(n.split()[:-1])) for n in a["authors"] if n]
            sim = title_sim(title, a["title"])
            ac = author_check(authors, ext_auth)
            res.update(doi=doi or a["doi"], link=a["id"].replace("http://", "https://"), source="arxiv:id",
                       ext_title=a["title"], ext_authors=ext_auth, ext_year=a["published"], ext_venue="arXiv",
                       title_sim=round(sim, 3), author_check=ac)
            res["status"] = "verified" if (sim >= TITLE_OK_DOI and ac in ("match", "partial")) else "DOI-TITLE-MISMATCH"
            cache[key] = res
            return res

    # 1) DOI given -> confirm on Crossref
    if doi and use_net:
        item = crossref_by_doi(doi)
        time.sleep(0.15)
        if item:
            sim = title_sim(title, cr_title(item))
            res.update(doi=item.get("DOI", doi), link="https://doi.org/" + item.get("DOI", doi),
                       source="crossref:doi", ext_title=cr_title(item), ext_authors=cr_authors(item),
                       ext_year=cr_year(item), ext_venue=(item.get("container-title") or [""])[0],
                       title_sim=round(sim, 3))
            res["author_check"] = author_check(authors, cr_authors(item))
            year_ok = _year_close(entry.get("year"), cr_year(item))
            if sim >= TITLE_OK_DOI:
                res["status"] = "verified"
            elif sim >= 0.55 and res["author_check"] in ("match", "partial") and year_ok:
                res["status"] = "verified"
                res["note"] = f"title variant on record: '{cr_title(item)}'"
            elif sim >= 0.95 and res["author_check"] == "MISMATCH":
                res["status"] = "AUTHOR-MISMATCH"
                res["note"] = "DOI/title match but bib authors differ: " + "; ".join(f"{l}, {f}" for l, f in cr_authors(item)[:8])
            else:
                res["status"] = "DOI-TITLE-MISMATCH"
                res["note"] = "DOI resolves to a different paper; check entry"
            cache[key] = res
            return res
        else:
            res["note"] = f"DOI {doi} not found on Crossref; "

    # 2) No (valid) DOI -> search Crossref by title + first author
    if use_net and title:
        for item in crossref_search(title, first):
            if _accept_ext(res, entry, authors, title=title, ext_title=cr_title(item), ext_authors=cr_authors(item),
                           ext_year=cr_year(item), doi=item["DOI"], link="https://doi.org/" + item["DOI"],
                           venue=(item.get("container-title") or [""])[0], source="crossref:search",
                           note="DOI found by title search"):
                cache[key] = res
                return res
        time.sleep(0.15)

        # 3) OpenAlex (covers NeurIPS/ICLR/OpenReview and other non-Crossref venues)
        for a in openalex_search(title, author=first):
            link = ("https://doi.org/" + a["doi"]) if a["doi"] else a["url"]
            if link and _accept_ext(res, entry, authors, title=title, ext_title=a["title"], ext_authors=a["authors"],
                                    ext_year=a["year"], doi=a["doi"], link=link, venue=a["venue"],
                                    source="openalex", note="matched on OpenAlex"):
                cache[key] = res
                return res
        time.sleep(0.15)

        # 4) arXiv
        for a in arxiv_search(title, author=first):
            ext_auth = [(n.split()[-1], " ".join(n.split()[:-1])) for n in a["authors"] if n]
            if _accept_ext(res, entry, authors, title=title, ext_title=a["title"], ext_authors=ext_auth,
                           ext_year=a["published"], doi=a["doi"], link=a["id"].replace("http://", "https://"),
                           venue="arXiv", source="arxiv", note="matched on arXiv"):
                cache[key] = res
                return res
        time.sleep(0.3)

        # 5) DBLP
        for a in dblp_search(title):
            link = ("https://doi.org/" + a["doi"]) if a["doi"] else a["url"]
            if link and _accept_ext(res, entry, authors, title=title, ext_title=a["title"], ext_authors=a["authors"],
                                    ext_year=a["year"], doi=a["doi"], link=link, venue=a["venue"],
                                    source="dblp", note="matched on DBLP"):
                cache[key] = res
                return res

    # 6) fall back to whatever link the bib has
    if res["status"] == "AUTHOR-MISMATCH":
        cache[key] = res
        return res
    if url:
        res.update(link=url, source="bib:url", status="unverified-url")
        res["note"] += "not indexed by Crossref/arXiv; using URL from bib"
    elif doi:
        res.update(doi=doi, link="https://doi.org/" + doi, source="bib:doi", status="unverified")
    else:
        res["note"] += "no DOI/URL and no index match — verify by hand"
    cache[key] = res
    return res


# --------------------------------------------------------------------------- #
# Output: EndNote XML + RIS + report
# --------------------------------------------------------------------------- #
REFTYPE = {  # bibtex type -> (EndNote name, EndNote number, RIS TY)
    "article": ("Journal Article", 17, "JOUR"),
    "inproceedings": ("Conference Paper", 47, "CPAPER"),
    "conference": ("Conference Paper", 47, "CPAPER"),
    "proceedings": ("Conference Proceedings", 10, "CONF"),
    "book": ("Book", 6, "BOOK"),
    "inbook": ("Book Section", 5, "CHAP"),
    "incollection": ("Book Section", 5, "CHAP"),
    "techreport": ("Report", 27, "RPRT"),
    "phdthesis": ("Thesis", 32, "THES"),
    "mastersthesis": ("Thesis", 32, "THES"),
    "misc": ("Generic", 13, "GEN"),
    "online": ("Web Page", 12, "ELEC"),
    "unpublished": ("Unpublished Work", 34, "UNPB"),
}


def venue_of(e: dict) -> str:
    return delatex(e.get("journal") or e.get("booktitle") or e.get("publisher") or e.get("institution") or e.get("school") or e.get("howpublished") or "")


def pages_of(e: dict):
    p = delatex(e.get("pages", "")).replace("--", "-").replace("—", "-")
    if "-" in p:
        a, b = p.split("-", 1)
        return a.strip(), b.strip(), p
    return p, "", p


def style(s: str) -> str:
    return f'<style face="normal" font="default" size="100%">{escape(s)}</style>'


def write_endnote_xml(rows, path):
    out = ['<?xml version="1.0" encoding="UTF-8"?>', "<xml><records>"]
    for i, (e, v) in enumerate(rows, 1):
        name, num, _ = REFTYPE.get(e["type"], REFTYPE["misc"])
        if e["type"] == "misc" and "arxiv" in (v.get("link") or "").lower():
            name, num = "Electronic Article", 43
        authors = split_authors(e.get("author", "") or e.get("editor", ""))
        year = re.sub(r"\D", "", e.get("year", ""))[:4]
        sp, ep, pg = pages_of(e)
        r = ["<record>",
             f"<rec-number>{i}</rec-number>",
             f'<ref-type name="{name}">{num}</ref-type>',
             "<contributors><authors>" + "".join(f"<author>{style(f'{l}, {f}'.strip(', '))}</author>" for l, f in authors) + "</authors></contributors>",
             "<titles>",
             f"<title>{style(delatex(e.get('title', '')))}</title>",
             f"<secondary-title>{style(venue_of(e))}</secondary-title>",
             "</titles>",
             f"<periodical><full-title>{style(venue_of(e))}</full-title></periodical>"]
        if pg:
            r.append(f"<pages>{style(pg)}</pages>")
        if e.get("volume"):
            r.append(f"<volume>{style(delatex(e['volume']))}</volume>")
        if e.get("number"):
            r.append(f"<number>{style(delatex(e['number']))}</number>")
        r.append(f"<dates><year>{style(year)}</year></dates>")
        if e.get("publisher"):
            r.append(f"<publisher>{style(delatex(e['publisher']))}</publisher>")
        if e.get("address"):
            r.append(f"<pub-location>{style(delatex(e['address']))}</pub-location>")
        if v.get("doi"):
            r.append(f"<electronic-resource-num>{style(v['doi'])}</electronic-resource-num>")
        if v.get("link"):
            r.append(f"<urls><related-urls><url>{style(v['link'])}</url></related-urls></urls>")
        r.append(f"<label>{style(e['key'])}</label>")
        note = f"bibkey={e['key']}; verification={v['status']}; source={v.get('source') or 'none'}"
        if v.get("author_check") and v["author_check"] != "n/a":
            note += f"; authors={v['author_check']}"
        if v.get("note"):
            note += f"; {v['note']}"
        r.append(f"<notes>{style(note)}</notes>")
        r.append("</record>")
        out.append("".join(r))
    out.append("</records></xml>")
    open(path, "w", encoding="utf-8").write("\n".join(out))


def write_ris(rows, path):
    lines = []
    for e, v in rows:
        _, _, ty = REFTYPE.get(e["type"], REFTYPE["misc"])
        authors = split_authors(e.get("author", "") or e.get("editor", ""))
        year = re.sub(r"\D", "", e.get("year", ""))[:4]
        sp, ep, _ = pages_of(e)
        lines.append(f"TY  - {ty}")
        for l, f in authors:
            lines.append(f"AU  - {l}, {f}".rstrip(", "))
        lines.append(f"TI  - {delatex(e.get('title', ''))}")
        if venue_of(e):
            lines.append(("JO  - " if ty == "JOUR" else "T2  - ") + venue_of(e))
        if year:
            lines.append(f"PY  - {year}")
        if e.get("volume"):
            lines.append(f"VL  - {delatex(e['volume'])}")
        if e.get("number"):
            lines.append(f"IS  - {delatex(e['number'])}")
        if sp:
            lines.append(f"SP  - {sp}")
        if ep:
            lines.append(f"EP  - {ep}")
        if e.get("publisher"):
            lines.append(f"PB  - {delatex(e['publisher'])}")
        if v.get("doi"):
            lines.append(f"DO  - {v['doi']}")
        if v.get("link"):
            lines.append(f"UR  - {v['link']}")
        lines.append(f"LB  - {e['key']}")
        lines.append(f"N1  - bibkey={e['key']}; verification={v['status']}; source={v.get('source') or 'none'}; authors={v.get('author_check')}; {v.get('note', '')}".rstrip("; "))
        lines.append("ER  - ")
        lines.append("")
    open(path, "w", encoding="utf-8").write("\n".join(lines))


def write_report(rows, out_dir):
    csv_path = os.path.join(out_dir, "verification_report.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["bibkey", "status", "author_check", "title_sim", "source", "doi", "link",
                    "bib_title", "index_title", "bib_first_author", "index_first_author", "bib_year", "index_year", "index_authors", "note"])
        for e, v in rows:
            ba = split_authors(e.get("author", "") or e.get("editor", ""))
            w.writerow([e["key"], v["status"], v.get("author_check"), v.get("title_sim"), v.get("source"),
                        v.get("doi"), v.get("link"), delatex(e.get("title", "")), v.get("ext_title"),
                        ba[0][0] if ba else "", v["ext_authors"][0][0] if v.get("ext_authors") else "",
                        e.get("year", ""), v.get("ext_year"),
                        "; ".join(f"{l}, {f}" for l, f in (v.get("ext_authors") or [])), v.get("note")])

    counts = {}
    for _, v in rows:
        counts[v["status"]] = counts.get(v["status"], 0) + 1
    md = [f"# Reference verification report", "",
          f"Entries processed: **{len(rows)}**", ""]
    for k, c in sorted(counts.items(), key=lambda x: -x[1]):
        md.append(f"- {k}: {c}")
    flagged = [(e, v) for e, v in rows if v["status"] != "verified" or v.get("author_check") in ("MISMATCH", "partial")]
    md += ["", f"## Needs attention ({len(flagged)})", "",
           "| bibkey | status | authors | bib authors | authors on record | link | note |",
           "|---|---|---|---|---|---|---|"]
    for e, v in flagged:
        ba = "; ".join(f"{l}, {f}" for l, f in split_authors(e.get("author", "") or e.get("editor", "")))
        ia = "; ".join(f"{l}, {f}" for l, f in (v.get("ext_authors") or [])[:8])
        md.append(f"| {e['key']} | {v['status']} | {v.get('author_check')} | {ba} | {ia} | {v.get('link') or ''} | {v.get('note') or ''} |")
    md += ["", "## All entries", "", "| # | bibkey | status | authors | link |", "|---|---|---|---|---|"]
    for i, (e, v) in enumerate(rows, 1):
        md.append(f"| {i} | {e['key']} | {v['status']} | {v.get('author_check')} | {v.get('link') or ''} |")
    open(os.path.join(out_dir, "verification_report.md"), "w", encoding="utf-8").write("\n".join(md))
    return counts, flagged


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bib", required=True)
    ap.add_argument("--tex", help="only export keys cited in this .tex (default: all entries)")
    ap.add_argument("--out", default="out")
    ap.add_argument("--all", action="store_true", help="ignore --tex and export every entry")
    ap.add_argument("--no-net", action="store_true", help="use cache.json only")
    ap.add_argument("--overrides", help="JSON {bibkey: {link, doi?, note?}} applied after verification (manual links)")
    args = ap.parse_args()
    overrides = json.load(open(args.overrides)) if args.overrides else {}

    os.makedirs(args.out, exist_ok=True)
    cache_path = os.path.join(args.out, "cache.json")
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}

    bib = parse_bib(args.bib)
    if args.tex and not args.all:
        keys = cited_keys(args.tex)
        missing = [k for k in keys if k not in bib]
        keys = [k for k in keys if k in bib]
        if missing:
            print(f"WARNING: {len(missing)} cited keys not in bib: {missing}", file=sys.stderr)
    else:
        keys = list(bib.keys())
    print(f"{len(bib)} bib entries, {len(keys)} to export")

    rows = []
    for n, k in enumerate(keys, 1):
        e = bib[k]
        v = verify(e, cache, use_net=not args.no_net)
        if k in overrides and v["status"] != "verified":
            o = overrides[k]
            v.update(link=o.get("link", v["link"]), doi=o.get("doi", v["doi"]), source="manual",
                     status="manual-link", note=o.get("note", "link supplied manually; not auto-verified"))
        rows.append((e, v))
        print(f"[{n:3}/{len(keys)}] {k:40s} {v['status']:22s} {v.get('author_check', ''):9s} {v.get('link', '')}")
        if n % 10 == 0:
            json.dump(cache, open(cache_path, "w"), indent=1)
    json.dump(cache, open(cache_path, "w"), indent=1)

    write_endnote_xml(rows, os.path.join(args.out, "references_endnote.xml"))
    write_ris(rows, os.path.join(args.out, "references.ris"))
    counts, flagged = write_report(rows, args.out)
    print("\nSummary:", counts)
    print(f"Needs attention: {len(flagged)}  -> see {args.out}/verification_report.md")
    print(f"EndNote import files: {args.out}/references_endnote.xml , {args.out}/references.ris")


if __name__ == "__main__":
    main()
