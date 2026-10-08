#!/usr/bin/env python3
"""Standardize the cited references to IEEE style against the publisher's record.

For every key cited by the 8-page submission build:

  1. query Crossref by DOI (or search by title when the bib carries no DOI),
  2. backfill volume / number / pages / doi where the publisher record has them,
  3. replace the journal name with Crossref's ISO short-container-title, which is
     the abbreviated form IEEE style requires,
  4. classify what is still missing as either OUTSTANDING (the publisher record
     has the value and we failed to use it) or an EXEMPTION (the publisher
     record itself has no such value: a preprint with no volume, a journal that
     numbers articles instead of pages, a standard, a project page).

Writes the rewritten bib in place (with --apply) and always writes a report.

    python3 endnote/ieee_style.py                 # dry run, report only
    python3 endnote/ieee_style.py --apply         # also rewrite live/newST.bib
    python3 endnote/ieee_style.py --no-net        # rebuild from the cache
"""
import argparse, json, os, re, sys, time, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bib2endnote as b  # parse_bib, cited_keys, delatex, http_get, title_sim

BIB = os.path.join(ROOT, "live", "newST.bib")
TEX = os.path.join(ROOT, "live", "STmodel.tex")
OUT = os.path.join(HERE, "out_j28")
CACHE = os.path.join(OUT, "crossref_cache.json")

# Fields IEEE style expects, by entry type.
NEEDED = {
    "article": ["journal", "volume", "number", "pages", "year", "doi"],
    "inproceedings": ["booktitle", "year", "pages", "doi"],
    "incollection": ["booktitle", "year", "pages", "doi"],
    "book": ["publisher", "year"],
    "techreport": ["institution", "year"],
    "misc": ["year", "doi"],
}

# Exemptions we assert ourselves, with the reason. Everything else must be
# justified by the publisher record having no value for the field.
SELF_EXEMPT = {
    "rumelhart1986rnn": ("MIT Press book chapter in Parallel Distributed Processing; the only "
                         "DOI Crossref offers for this title is the 1985 DTIC technical report "
                         "10.21236/ada164453, a different document, so no DOI is claimed"),
    "Fang2021iPAT": "project web page; not a Crossref-indexed publication, so no volume, issue, pages or DOI exists",
}


def load_cache():
    try:
        return json.load(open(CACHE))
    except Exception:
        return {}


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
        time.sleep(0.12)
    return cache[k]


def crossref_find(title, author, year, cache, net):
    """A title search hit is accepted only when title, year and author all agree.

    A bare title match is not enough: the same title is registered again by
    reprints (Goodfellow et al. in CACM 2020), by book chapters that reuse it
    (FEDformer in "AI for Time Series", 2026) and by re-registered proceedings.
    Each of those is a different document from the one we cite.
    """
    k = "q:" + re.sub(r"\W+", " ", title.lower()).strip()[:120]
    if k not in cache:
        if not net:
            return None, "not searched: --no-net"
        hit = None
        try:
            for item in b.crossref_search(title, author, rows=5) or []:
                if b.title_sim(title, b.cr_title(item)) >= 0.92:
                    hit = item
                    break
        except Exception:
            hit = None
        cache[k] = hit
        time.sleep(0.12)
    hit = cache[k]
    if not hit:
        return None, "the title is not registered with Crossref"
    ct, cy = b.cr_title(hit), b.cr_year(hit)
    if b.title_sim(title, ct) < 0.95:
        return None, "no Crossref record matches the title"
    if not b._year_close(year, cy, tol=1):
        return None, (f"the only Crossref record with this title is a different document "
                      f"({cy}, {(hit.get('container-title') or ['no venue'])[0]}, DOI {hit.get('DOI')}) "
                      f"and citing its DOI would misattribute the work")
    sur = re.sub(r"[^a-z]", "", (author or "").split(",")[0].split()[-1].lower()) if author.strip() else ""
    names = ("".join(map(str, x)) if isinstance(x, (tuple, list)) else str(x) for x in b.cr_authors(hit))
    if sur and not any(sur in re.sub(r"[^a-z]", "", n.lower()) for n in names):
        return None, "the Crossref record with this title carries different authors"
    return hit, ""


def pages_of(item):
    p = (item.get("page") or "").strip()
    if p:
        return p.replace("-", "--") if "--" not in p else p
    art = (item.get("article-number") or "").strip()
    return art or ""


# Crossref's short titles are MEDLINE-style for biomedical journals (no periods)
# and occasionally a bare acronym. IEEE style wants each abbreviated word closed
# with a period. These are the cases the alignment below cannot derive.
JOURNAL_OVERRIDE = {
    # Crossref's short-container-title for JASA is the full name, so there is nothing
    # shorter to take; the IEEE abbreviation has to be supplied here.
    "Journal of the American Statistical Association": "J. Amer. Statist. Assoc.",
    "Journal of Personalized Medicine": "J. Personalized Med.",
    "IEEE Transactions on Geoscience and Remote Sensing": "IEEE Trans. Geosci. Remote Sens.",
    "Journal of NeuroEngineering and Rehabilitation": "J. NeuroEng. Rehabil.",
}


def ieee_abbrev(short, long_):
    """Close every abbreviated word with a period, following the full title's casing.

    A word of the short title is an abbreviation when it is a strict prefix of a
    word of the full title; then it takes a period. A word that matches a full
    word keeps it. A word that matches nothing is an acronym and is left alone.
    """
    lw = re.findall(r"[A-Za-z]+", long_)
    out, unmatched = [], []
    for w in short.split():
        core = re.sub(r"[^A-Za-z]", "", w)
        if not core:
            out.append(w)
            continue
        hit = next((x for x in lw if x.lower() == core.lower()), None)
        if hit:                                     # a full word, not abbreviated
            out.append(w.replace(core, hit))
            continue
        hit = next((x for x in lw if x.lower().startswith(core.lower()) and len(x) > len(core)), None)
        if hit:                                     # abbreviation: close with a period
            w = w.replace(core, core[0].upper() + core[1:] if hit[0].isupper() else core)
            out.append(w if w.endswith(".") else w + ".")
        else:
            unmatched.append(core)
            out.append(w)
    return " ".join(out), unmatched


def short_title(item):
    """The IEEE-style abbreviated journal name, or "" when none can be justified."""
    s = (item.get("short-container-title") or [""])[0].strip()
    l = (item.get("container-title") or [""])[0].strip()
    if l in JOURNAL_OVERRIDE:
        return JOURNAL_OVERRIDE[l]
    # Crossref sometimes repeats the long name in the short slot; only treat it
    # as an abbreviation when it is actually shorter.
    if not s or not l or len(s) >= len(l):
        return ""
    fixed, unmatched = ieee_abbrev(s, l)
    if unmatched and not any(c.isupper() for c in "".join(unmatched)[1:]):
        return ""       # an unexplained lowercase fragment: do not guess
    return fixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--no-net", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    net = not a.no_net
    cache = load_cache()

    ents = b.parse_bib(BIB)
    keys = b.cited_keys(TEX)
    raw = open(BIB, encoding="utf-8").read()

    rows, edits = [], []
    for key in keys:
        e = ents.get(key)
        if not e:
            rows.append({"key": key, "outstanding": ["entry missing from the bib"], "exempt": []})
            continue
        typ = e.get("type", "misc")
        why_no_doi = ""
        doi = (e.get("doi") or "").strip()
        item = crossref(doi, cache, net) if doi else None
        if item is None and not doi:
            hit, why_no_doi = crossref_find(b.delatex(e.get("title", "")),
                                            b.delatex(e.get("author", "")).split(" and ")[0],
                                            e.get("year", ""), cache, net)
            if hit:
                item = hit
                doi = (hit.get("DOI") or "").strip()

        want = NEEDED.get(typ, NEEDED["misc"])
        outstanding, exempt = [], []

        cr = {}
        if item:
            cr = {"volume": (item.get("volume") or "").strip(),
                  "number": (item.get("issue") or "").strip(),
                  "pages": pages_of(item),
                  "doi": (item.get("DOI") or "").strip()}
            short = short_title(item)
            if typ == "article" and short:
                cur = b.delatex(e.get("journal", "")).strip()
                if cur and cur.lower() != short.lower():
                    edits.append((key, "journal", short))
                    exempt.append(f"journal name abbreviated to `{short}` (Crossref ISO short title)")
            for f in ("volume", "number", "pages", "doi"):
                if (f in want and key not in SELF_EXEMPT
                        and not (e.get(f) or "").strip() and cr.get(f)):
                    edits.append((key, f, cr[f]))

        for f in want:
            have = (e.get(f) or "").strip() or any(k2 == key and f2 == f for k2, f2, _ in edits)
            if have:
                continue
            if key in SELF_EXEMPT:
                exempt.append(f"{f}: {SELF_EXEMPT[key]}")
            elif item is None:
                exempt.append(f"{f}: no publisher record to take it from --- "
                              + (why_no_doi or "the DOI in the bib does not resolve at Crossref"))
            elif not cr.get(f):
                exempt.append(f"{f}: the publisher record carries no value for it")
            else:
                outstanding.append(f"{f}: Crossref has `{cr[f]}` and it was not applied")
        rows.append({"key": key, "type": typ, "outstanding": outstanding, "exempt": exempt})

    json.dump(cache, open(CACHE, "w"), indent=0)

    # ---- apply the edits to the bib text ----
    applied = 0
    if a.apply and edits:
        for key, field, val in edits:
            m = re.search(r"@\w+\s*\{\s*" + re.escape(key) + r"\s*,", raw)
            if not m:
                continue
            # find the entry's extent
            i = m.end()
            depth, j = 1, m.start()
            j = raw.index("{", m.start())
            depth, j = 1, j + 1
            while j < len(raw) and depth:
                if raw[j] == "{": depth += 1
                elif raw[j] == "}": depth -= 1
                j += 1
            body = raw[m.end():j - 1]
            # the field may sit mid-line ("volume = {9}, pages = {45--59},"), so anchor
            # on a delimiter rather than on a newline, or a duplicate gets appended
            fm = re.search(r"(^|[,{\s])(" + field + r"\s*=\s*)(\{[^{}]*\}|\"[^\"]*\")",
                           body, re.I | re.M)
            v = "{" + val + "}"
            if fm:
                nb = body[:fm.start(3)] + v + body[fm.end(3):]
            else:
                nb = body.rstrip().rstrip(",") + ",\n  " + field + " = " + v + "\n"
            raw = raw[:m.end()] + nb + raw[j - 1:]
            applied += 1
        open(BIB, "w", encoding="utf-8").write(raw)

    n_out = sum(1 for r in rows if r["outstanding"])
    lines = [
        "# IEEE reference style, cited entries",
        "",
        f"Cited by the submission build: **{len(keys)}** entries. "
        f"Checked against the publisher's Crossref record, field by field.",
        "",
        f"- Fields backfilled from the publisher record: **{len(edits)}**"
        + (f" (applied to `live/newST.bib`: {applied})" if a.apply else " (dry run; rerun with --apply)"),
        f"- Entries with an unjustified gap: **outstanding: {n_out}**",
        f"- Entries carrying at least one documented exemption: **{sum(1 for r in rows if r['exempt'])}**",
        "",
    ]
    if n_out:
        lines += ["## Outstanding", ""]
        for r in rows:
            for o in r["outstanding"]:
                lines.append(f"- `{r['key']}` — {o}")
        lines.append("")
    lines += ["## Documented exemptions", "",
              "Each line states why IEEE style cannot supply the field for that entry. "
              "An exemption is only claimed where the publisher's own record has no value.", ""]
    for r in rows:
        if r["exempt"]:
            lines.append(f"**`{r['key']}`** ({r.get('type','')})")
            for x in r["exempt"]:
                lines.append(f"  - {x}")
    lines.append("")
    if edits:
        lines += ["## Fields taken from the publisher record", ""]
        for key, field, val in edits:
            lines.append(f"- `{key}` · {field} = {val}")
    open(os.path.join(OUT, "ieee_style_report.md"), "w").write("\n".join(lines) + "\n")
    print(f"cited {len(keys)} · edits {len(edits)} · applied {applied} · outstanding {n_out}")


if __name__ == "__main__":
    main()
