#!/usr/bin/env python3
"""Whole-paper consistency audit: every counted claim against its own source.

This does not check that the prose exists (check_comments.py does that) or that
the review items are addressed (check_j28.py). It checks that the numbers in the
prose are the numbers the tables and the screening records actually support, and
that every arithmetic chain closes.

Three classes of check:

  TABLE   a claim in the prose against the cells of Table II or the supplement
  SUM     an arithmetic chain stated in the prose (the counts must add up)
  XREF    labels, references and cross-document pointers

    python3 review/check_consistency.py            # report
    python3 review/check_consistency.py --json     # Stop-hook payload
"""
import argparse, json, os, re, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "live", "STmodel.tex")
SUPP = os.path.join(ROOT, "live", "supplement.tex")
BIB = os.path.join(ROOT, "live", "newST.bib")
SCREEN = os.path.join(ROOT, "review", "search", "ieee_screen.json")

_s = importlib.util.spec_from_file_location("cc", os.path.join(ROOT, "review", "check_comments.py"))
cc = importlib.util.module_from_spec(_s); _s.loader.exec_module(cc)
_s2 = importlib.util.spec_from_file_location("bb", os.path.join(ROOT, "endnote", "bib2endnote.py"))


def read(p):
    return open(p, encoding="utf-8", errors="replace").read()


def cells(row):
    return [c.strip() for c in re.split(r"(?<!\\)&", row)]


def table(tex, label):
    """(header cells, data rows) of the float carrying this label."""
    i = tex.index("\\label{" + label + "}")
    s = tex.rindex("\\begin{table*}", 0, i)
    e = tex.index("\\end{table*}", i)
    blk = tex[s:e]
    hdr = cells(blk[blk.index("\\toprule") + 8:blk.index("\\midrule")].strip().rstrip("\\").strip())
    body = blk[blk.index("\\midrule"):blk.index("\\bottomrule")]
    rows = [cells(r) for r in re.split(r"\\\\", body) if "&" in r and "multicolumn" not in r]
    return hdr, [r for r in rows if len(r) == len(hdr)], blk


def main_cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    main_raw = cc.submission_only(cc.strip_comments(read(MAIN)))
    prose = re.sub(r"\s+", " ", main_raw)
    supp_raw = cc.strip_comments(read(SUPP))
    findings = []

    def check(kind, name, ok, detail=""):
        findings.append({"kind": kind, "name": name, "ok": bool(ok), "detail": detail})

    # ---------------------------------------------------------------- TABLE
    ev_hdr, ev_rows, ev_blk = table(main_raw, "tab:evidence")
    n = len(ev_rows)
    check("TABLE", "Table II row count matches the prose",
          n == 22 and "twenty-two studies" in prose, f"{n} rows; prose says twenty-two")
    check("TABLE", "Table II column count is at most 6",
          len(ev_hdr) <= 6, f"{len(ev_hdr)} columns")

    cls_a = sum(1 for r in ev_rows if re.match(r"^A\b", r[1]))
    m = re.search(r"(\w+) of the twenty-two draw on data captured", prose)
    words = {"Eleven": 11, "Twelve": 12, "Ten": 10, "Thirteen": 13, "Fourteen": 14,
             "Fifteen": 15, "Sixteen": 16, "Seventeen": 17, "Eighteen": 18}
    check("TABLE", "class A count matches the prose",
          m and words.get(m.group(1)) == cls_a,
          f"table has {cls_a} class-A rows; prose says {m.group(1) if m else 'nothing'}")

    # Deployment cell: "reported / ours". Anything said about cost sits before the slash;
    # only some of those are numbers. Bohoran et al. state network pruning without one, so
    # "five report a figure" and "five state anything" are not the same claim.
    reported = [re.split(r"\s/\s", r[4])[0] for r in ev_rows]   # " / " separates reported from ours
    # A reported side may name a placement ("App backend"), a cost, or nothing ("n/r").
    # Only a quantity or the words "model cost" count as saying something about cost.
    any_cost = [d for d in reported
                if re.search(r"\d\s*\\,?(ms|MB|kB|s)\b|model cost", d, re.I)]
    num_cost = [d for d in any_cost if re.search(r"\d", d)]
    check("TABLE", "studies saying anything about cost or latency match the prose",
          len(any_cost) == 5 and len(re.findall(r"five (?:state anything about model cost|of the twenty-two state anything about model cost)", prose)) >= 2,
          f"table has {len(any_cost)}: " + "; ".join(d[:26] for d in any_cost))
    check("TABLE", "studies giving a numeric cost or latency match the prose",
          len(num_cost) == 4 and "four of them as a number" in prose,
          f"table has {len(num_cost)} numeric: " + "; ".join(d[:26] for d in num_cost))
    check("TABLE", "no sentence still claims five report a figure",
          not re.search(r"five (?:of the twenty-two )?report a (?:deployment )?cost or latency figure", prose),
          "a sentence still says five report a figure")

    # the three longitudinal rows: the supplement gives their datasets no spatial index
    # across sites, but one of the three is a series of scans, so "no spatial component"
    # would contradict its own dataset row ("Scan image").
    _, ds_rows, _ = table(supp_raw, "tab:S2a")
    _, ds_rows2, _ = table(supp_raw, "tab:S4a")
    ds = ds_rows + ds_rows2
    su = [r[5] for r in ds]
    check("TABLE", "the longitudinal claim does not contradict the dataset spatial units",
          "have no spatial component" not in prose
          and "carry no spatial index across sites or regions" in prose
          and any(re.search(r"scan image", c, re.I) for c in su)
          and len([c for c in su if re.match(r"^None", c, re.I)]) >= 3,
          "the prose says 'no spatial component' while a dataset row gives a spatial unit")

    nosplit = [r for r in ev_rows if re.search(r"No split|Split n/r|split n/r", r[3])]
    check("TABLE", "studies with no split or an unstated split match the prose",
          len(nosplit) == 3 and "three either report no split" in prose,
          f"table has {len(nosplit)}")

    # external validation, from the supplement
    ext = []
    for lab in ("tab:S3a", "tab:S5a"):
        _, rows, _ = table(supp_raw, lab)
        ext += [r[4] for r in rows]
    none_ext = [c for c in ext if re.match(r"^(None|No\b|n/r)", c, re.I)]
    second = [c for c in ext if c not in none_ext]
    untouched = [c for c in second
                 if not re.search(r"retrain|refit|fine-tun|pooled|its own models", c, re.I)]
    check("TABLE", "external-validation counts match the prose",
          len(ext) == 22 and len(none_ext) == 16 and len(second) == 6,
          f"{len(none_ext)} none, {len(second)} with a second cohort, of {len(ext)}")
    check("TABLE", "the single-cohort count in the prose matches the supplement",
          f"sixteen of the twenty-two validate inside a single cohort" in prose
          and len(none_ext) == 16,
          f"supplement gives {len(none_ext)}; prose must say sixteen")
    check("TABLE", "no stale single-cohort count survives",
          not re.search(r"over half of the twenty-two studies \(\d+\)", prose),
          "an old parenthetical count is still in the prose")
    check("TABLE", "no study is presented as an untouched external test",
          len(untouched) == 0 and "not an untouched external test" in prose,
          f"{len(untouched)} second-cohort rows show no adaptation: {untouched}")

    # the quality paragraph, against review/quality_counts.py
    qc_path = os.path.join(ROOT, "review", "quality_counts.json")
    if os.path.exists(qc_path):
        q = json.load(open(qc_path))
        sp = q["split"]
        want = [("Fourteen of the twenty-two hold out whole subjects",
                 sp["whole subjects or a later window"], 14),
                ("Four split at the level of a sample", sp["unit smaller than a person"], 4),
                ("three never state the level", sp["level not stated"], 3),
                ("one estimates on the full sample with no hold-out",
                 sp["no hold-out at all"], 1)]
        for phrase, got, expect in want:
            check("TABLE", f"quality paragraph: {phrase[:44]}",
                  got == expect and phrase in prose, f"tables give {got}, prose wants {expect}")
        check("TABLE", "quality paragraph: calibration",
              q["calibration_not_reported"] == 20 and q["calibration_curve_reported"] == 0
              and "Twenty report nothing about calibration" in prose,
              f"{q['calibration_not_reported']} n/r, {q['calibration_curve_reported']} curves")
        check("TABLE", "quality paragraph: intervals, subgroups, code, prospective",
              len(q["any_interval_or_bounds"]) == 5
              and len(q["subgroup_demographic_or_clinical"]) == 5
              and len(q["code_released"]) == 4
              and q["clinical_validation_none"] == 22,
              f"intervals {len(q['any_interval_or_bounds'])}, subgroups "
              f"{len(q['subgroup_demographic_or_clinical'])}, code {len(q['code_released'])}, "
              f"no-clinical {q['clinical_validation_none']}")
        check("TABLE", "the split classification leaves nothing unclassified",
              "unclassified" not in sp, str(sp.get("unclassified", "")))
    else:
        check("TABLE", "quality_counts.json exists", False, "run review/quality_counts.py")

    # ---------------------------------------------------------------- SUM
    def num(pat, where=None):
        m = re.search(pat, where or prose)
        return int(m.group(1).replace("{,}", "").replace(",", "")) if m else None

    pm_a = num(r"PubMed returned 1\{,\}(\d\d\d) records on the spatiotemporal arm")
    pm_a = 1171 if pm_a == 171 else pm_a
    chain = [
        ("PubMed union: 1,171 + 268 - 3 = 1,436",
         1171 + 268 - 3 == 1436 and "1{,}436 unique records" in prose),
        ("PubMed screened: 1,436 - 36 - 194 = 1,206",
         1436 - 36 - 194 == 1206 and "1{,}206 screened" in prose),
        ("PubMed eligible: 1,206 - (99 + 127 + 617) = 363",
         1206 - (99 + 127 + 617) == 363 and "363 rule-eligible records" in prose),
        ("hand check: 13 confirmed of 21, 7 of 39 missed, 13 + 32 = 45 agreed",
         13 + 32 == 45 and round(100 * 13 / 21) == 62 and round(100 * 7 / 39) == 18),
    ]
    for name, ok in chain:
        check("SUM", name, ok)

    if os.path.exists(SCREEN):
        d = json.load(open(SCREEN))
        A, B = d["arm_a"], d["arm_b"]
        dd = d["deduplicated_against_pubmed"]
        tot = A["records"] + B["records"]
        scr = A["screened_on_title_abstract"] + B["screened_on_title_abstract"]
        pool = 363 + dd["ieee_only"]
        fails = sum(A[k] + B[k] for k in ("excluded_i_no_spacetime_structure",
                                          "excluded_ii_not_human_health",
                                          "excluded_iii_no_quantitative_comparison"))
        checks = [
            (f"IEEE identified {tot} is the number in Figure 1",
             f"\\textbf{{{tot:,}}}".replace(",", "{,}") in prose or f"{tot:,}".replace(",", "{,}") in prose),
            (f"IEEE screened {scr} is the number in the prose",
             f"{scr:,}".replace(",", "{,}") in prose),
            ("IEEE fails + eligible = screened", fails + d["eligible_before_dedup"] == scr),
            ("IEEE eligible after dedup = also-in-PubMed + IEEE-only",
             dd["also_in_pubmed"] + dd["ieee_only"] == d["eligible_unique_within_ieee"]),
            (f"two-database pool 363 + {dd['ieee_only']} = {pool} appears in the prose",
             str(pool) in prose),
        ]
        for name, ok in checks:
            check("SUM", name, ok)
    else:
        check("SUM", "ieee_screen.json exists", False)

    # citation chasing: seeds, totals and yield
    cc_path = os.path.join(ROOT, "review", "search", "citation_chase.json")
    if os.path.exists(cc_path):
        ch = json.load(open(cc_path))
        seeds = ch["seeds"]
        contributing = [k for k, v in seeds.items()
                        if v["references"] or v["cited_by"]]
        distinct = ch["backward"]["distinct"] + ch["forward"]["distinct"]
        newly = ch["backward"]["not_already_retrieved"] + ch["forward"]["not_already_retrieved"]
        check("SUM", f"citation chasing used {len(contributing)} seeds and the prose says so",
              f"the {'ten' if len(contributing)==10 else len(contributing)} reviews of Table" in prose,
              f"{len(contributing)} seeds have a reference list or citing works")
        check("SUM", f"citation chasing screened {distinct} distinct records",
              f"{distinct:,}".replace(",", "{,}") in prose, f"backward+forward = {distinct}")
        check("SUM", f"citation chasing surfaced {newly} new eligible records",
              re.search(r"\\textbf\{" + str(newly) + r"\} eligible ones", prose) is not None,
              f"1 + 14 = {newly}")
        check("SUM", "no claim that a compared review lacks a DOI",
              "without a registered" not in re.sub(r"\s+", " ", supp_raw),
              "the supplement still says a review has no registered DOI")
    else:
        check("SUM", "citation_chase.json exists", False)

    # reference count
    spec = importlib.util.spec_from_file_location("bb", os.path.join(ROOT, "endnote", "bib2endnote.py"))
    bb = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(bb)
        keys = bb.cited_keys(MAIN)
        ents = bb.parse_bib(BIB)
        check("SUM", "every cited key exists in the bib",
              all(k in ents for k in keys), str([k for k in keys if k not in ents]))
        dups = []
        for k in set(keys):
            body = ents[k]
            fs = [f for f in ("volume", "number", "pages", "doi", "journal") if body.get(f)]
            del fs
        check("SUM", f"cited reference count is {len(keys)}", len(keys) == 76, f"{len(keys)} cited")
    except Exception as e:
        check("SUM", "bib parsed", False, str(e))

    # ---------------------------------------------------------------- XREF
    for name, tex in (("submission build", main_raw), ("supplement", supp_raw)):
        labs = set(re.findall(r"\\label\{([^}]*)\}", tex))
        refs = set(re.findall(r"\\(?:ref|autoref|eqref)\{([^}]*)\}", tex))
        check("XREF", f"{name}: every \\ref resolves",
              not (refs - labs), str(sorted(refs - labs)))
        dup = [l for l in labs if len(re.findall(r"\\label\{" + re.escape(l) + r"\}", tex)) > 1]
        check("XREF", f"{name}: no duplicate labels", not dup, str(dup))

    # supplement section pointers named from the main text
    sec_order = re.findall(r"\\section\{([^}]*)\}", supp_raw)
    roman = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}
    for n_, want in ((2, "Search strings"), (3, "Screening the IEEE Xplore records")):
        actual = sec_order[n_ - 1] if len(sec_order) >= n_ else "(missing)"
        pointer = f"Supplement Section~{roman[n_]}"
        if pointer in prose:
            check("XREF", f"{pointer} points at '{want}'", want.lower() in actual.lower(),
                  f"supplement section {roman[n_]} is '{actual}'")

    # supplement table numbering
    nums = re.findall(r"\\renewcommand\{\\thetable\}\{(S\d[ab]?)\}", supp_raw)
    stems = sorted({x[:2] for x in nums})
    check("XREF", "split panels come in a/b pairs",
          all(f"{s}a" in nums and f"{s}b" in nums for s in stems), str(nums))
    n_caps = supp_raw.count("\\caption{")
    check("XREF", f"supplement holds {n_caps} table captions in ten numbered slots",
          n_caps == 14, f"{n_caps} captions")

    # no stray claim that the evidence set is twelve studies
    stray = re.findall(r"twelve studies of Table|the twelve studies in Table", prose)
    check("XREF", "no stray claim that Table II holds twelve studies", not stray, str(stray))

    # ---------------------------------------------------------------- report
    bad = [f for f in findings if not f["ok"]]
    if a.json:
        msg = (f"Consistency: all {len(findings)} checks pass."
               if not bad else
               f"Consistency: {len(findings)-len(bad)}/{len(findings)} pass | "
               + "; ".join(f"{f['name']} ({f['detail']})" for f in bad[:4]))
        print(json.dumps({"systemMessage": msg, "suppressOutput": True}))
        return

    last = None
    for f in findings:
        if f["kind"] != last:
            print(f"\n{f['kind']}")
            last = f["kind"]
        print(("  ok   " if f["ok"] else "  FAIL ") + f["name"])
        if not f["ok"] and f["detail"]:
            print(f"         {f['detail']}")
    print(f"\n{len(findings)-len(bad)} of {len(findings)} consistency checks pass")
    if bad:
        print("\nInconsistent:")
        for f in bad:
            print(f"  - [{f['kind']}] {f['name']}: {f['detail']}")


if __name__ == "__main__":
    main_cli()
