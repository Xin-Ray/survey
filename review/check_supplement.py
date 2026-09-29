#!/usr/bin/env python3
"""Completion checker for the three supplement tables Prof. Fang asked for.

Reports, from the files themselves rather than from anyone's claim:
  S1  threats x IoT layers table          (her comment 9)
  S2  public-dataset table                (her comment 8)
  S3  study quality-assessment table      (her comment 7)

Run bare for a human-readable report, or with --json for a Stop-hook payload.
Exit 0 always: this reports status, it does not block.
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUPP = os.path.join(ROOT, "live", "supplement.tex")
MAIN = os.path.join(ROOT, "live", "STmodel.tex")

LAYERS = ["device", "communication", "edge", "cloud", "twin", "world model"]
DATASET_COLS = ["population", "modality", "device", "duration", "sampling",
                "spatial", "missing", "access", "task", "limitation"]
QUALITY_COLS = ["split", "leakage", "missing", "external", "calibrat",
                "uncertain", "fairness", "comparator", "reproduc", "clinical"]
PLACEHOLDERS = re.compile(r"\b(TODO|TBD|FIXME|XXX|\?\?|fill in|placeholder)\b", re.I)


def read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None


def strip_comments(t):
    return re.sub(r"(?<!\\)%.*", "", t or "")


def table_block(tex, label):
    """The table environment carrying \\label{label}, or None."""
    for m in re.finditer(r"\\begin\{(table\*?|longtable)\}", tex):
        start = m.start()
        end = tex.find("\\end{" + m.group(1) + "}", start)
        if end < 0:
            continue
        blk = tex[start:end]
        if "\\label{" + label + "}" in blk:
            return blk
    return None


def body_rows(blk):
    """Data rows: after \\midrule (if present), split on \\\\, keep non-empty."""
    body = blk[blk.find("\\midrule"):] if "\\midrule" in blk else blk
    rows = []
    for r in re.split(r"\\\\", body):
        r = r.strip()
        if not r or r.startswith("\\bottomrule") or r.startswith("\\end"):
            continue
        if "&" in r:
            rows.append(r)
    return rows


def submission_only(tex):
    """Drop the \\ifsubmission...\\else...\\fi extended branches (8-page build)."""
    tex = re.sub(r"\\newif\\if[a-zA-Z@]*", "", tex)
    out, pos, st = [], 0, []
    for m in re.finditer(r"\\(ifsubmission|if[a-zA-Z@]*|else|fi)\b", tex):
        w = m.group(1)
        if not any(x[0] and x[1] for x in st):
            out.append(tex[pos:m.start()])
        pos = m.end()
        if w.startswith("if"):
            st.append([w == "ifsubmission", False])
        elif w == "else":
            if st: st[-1][1] = True
        elif w == "fi":
            if st: st.pop()
    if not any(x[0] and x[1] for x in st):
        out.append(tex[pos:])
    return "".join(out)


def studies_in_main():
    """How many study rows the SUBMISSION build's evidence table carries."""
    t = strip_comments(read(MAIN))
    if not t:
        return None
    blk = table_block(submission_only(t), "tab:evidence")
    if not blk:
        return None
    return len([r for r in body_rows(blk) if "\\cite{" in r])


def check():
    supp = strip_comments(read(SUPP))
    n_studies = studies_in_main()
    out = {"supplement_file": SUPP, "studies_in_table_ii": n_studies, "tasks": {}}

    def task(key, title, label, want_rows, want_cols, extra=None, also=None):
        st = {"title": title, "label": label, "done": False, "notes": []}
        if supp is None:
            st["notes"].append("supplement.tex does not exist yet")
            out["tasks"][key] = st
            return
        blk = table_block(supp, label)
        if blk is None:
            st["notes"].append(f"no table carrying \\label{{{label}}}")
            out["tasks"][key] = st
            return
        rows = body_rows(blk)
        for extra_label in (also or []):
            b2 = table_block(supp, extra_label)
            if b2 is None:
                st["notes"].append(f"no continuation table carrying \\label{{{extra_label}}}")
            else:
                rows = rows + body_rows(b2)
                blk = blk + b2
        st["rows"] = len(rows)
        header = rows[0] if rows else ""
        head_src = blk[:blk.find("\\midrule")] if "\\midrule" in blk else blk
        missing_cols = [c for c in want_cols if c.lower() not in head_src.lower()]
        if missing_cols:
            st["notes"].append("header is missing: " + ", ".join(missing_cols))
        if want_rows is not None and len(rows) < want_rows:
            st["notes"].append(f"{len(rows)} data rows, expected at least {want_rows}")
        ph = PLACEHOLDERS.findall(blk)
        if ph:
            st["notes"].append(f"{len(ph)} placeholder marker(s) still in the table")
        empty = [i for i, r in enumerate(rows) if re.search(r"&\s*&", r)]
        if empty:
            st["notes"].append(f"{len(empty)} row(s) contain an empty cell (use n/r or 'not assessable')")
        if extra:
            st["notes"].extend(extra(blk, rows))
        st["done"] = not st["notes"]
        out["tasks"][key] = st

    def s1_extra(blk, rows):
        low = blk.lower()
        return ["layer rows missing: " + ", ".join(l for l in LAYERS if l not in low)] \
            if any(l not in low for l in LAYERS) else []

    def s3_extra(blk, rows):
        notes = []
        if n_studies and len(rows) != n_studies:
            notes.append(f"{len(rows)} data rows for {n_studies} synthesized studies")
        if "not assessable" not in blk.lower() and "n/r" not in blk.lower():
            notes.append("no 'n/r' or 'not assessable' anywhere — every cell claims to be known, "
                         "which is unlikely given the paywalled full texts")
        return notes

    task("S1", "Threats and protections across IoT layers (comment 9)",
         "tab:threats", 7, ["threat", "protection"], s1_extra)
    task("S2", "Dataset table, both parts (comment 8)",
         "tab:datasets", 9, DATASET_COLS, extra=None, also=["tab:datasets-b"])
    task("S3", "Study quality assessment, both parts (comment 7)",
         "tab:quality", n_studies or 12, QUALITY_COLS, s3_extra, also=["tab:quality-b"])
    task("S4", "Survey-comparison evidence (comment 6)",
         "tab:surveyevidence", 12, ["review", "section evidence"])
    task("S5", "Communication substrate (comment 9)",
         "tab:protocols", 6, ["data rate", "latency", "range", "energy"])
    task("S6", "Deployment and privacy reporting (comment 5)",
         "tab:deployrep", n_studies or 12, ["privacy", "latency", "energy", "bandwidth", "limitation"],
         extra=lambda blk, rows: ([f"{len(rows)} rows for {n_studies} studies"] if n_studies and len(rows) != n_studies else []))
    task("S7", "Provenance and inclusion reason (comment 1)",
         "tab:provenance", n_studies or 12, ["provenance", "reason for inclusion"],
         extra=lambda blk, rows: ([f"{len(rows)} rows for {n_studies} studies"] if n_studies and len(rows) != n_studies else []))

    out["all_done"] = all(t["done"] for t in out["tasks"].values())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="emit a Stop-hook JSON payload")
    a = ap.parse_args()
    r = check()

    if a.json:
        done = [k for k, t in r["tasks"].items() if t["done"]]
        todo = [k for k, t in r["tasks"].items() if not t["done"]]
        if r["all_done"]:
            msg = "Supplement tables: all %d pass the completeness check." % len(r["tasks"])
        else:
            parts = []
            for k in todo:
                t = r["tasks"][k]
                parts.append(f"{k} ({t['notes'][0]})")
            msg = ("Supplement check - done: " + (", ".join(done) or "none")
                   + " | outstanding: " + "; ".join(parts))
        print(json.dumps({"systemMessage": msg, "suppressOutput": True}))
        return

    print(f"Table II carries {r['studies_in_table_ii']} study rows\n")
    for k, t in r["tasks"].items():
        mark = "DONE" if t["done"] else "not done"
        print(f"[{mark:8s}] {k}  {t['title']}")
        if "rows" in t:
            print(f"             rows: {t['rows']}")
        for n in t["notes"]:
            print(f"             - {n}")
    print("\nall tasks complete:", r["all_done"])


if __name__ == "__main__":
    main()
