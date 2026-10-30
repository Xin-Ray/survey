#!/usr/bin/env python3
"""Check the 2026-10-29 review items against the artifacts, not against the prose.

Every earlier round failed the same way: a checker confirmed that a sentence was
present while the table cell, the audit row or the deposited file behind it was
wrong or absent (PROGRESS.md keeps the running list). So the assertions here
recompute from the manuscript's own table cells and from the audit CSVs, and
compare the two. A task that cannot be closed by tooling -- a full text someone
has to read, a second person's independent coding -- reports PENDING rather than
passing, because reporting those as done is how three rounds were lost.

    python3 review/check_oct29.py           # human-readable
    python3 review/check_oct29.py --json    # for the Stop hook
"""
import argparse, csv, io, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "expand25", "STmodel.tex")
AUDIT = os.path.join(ROOT, "expand25", "audit")
# The tag is read out of the manuscript, so the two cannot drift apart: whatever release the
# article cites is the release this check verifies.
_m = re.search(r"tagged \\texttt\{(audit-[0-9.\-]+)\}",
               io.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    "expand25", "STmodel.tex"), encoding="utf-8").read())
TAG = _m.group(1) if _m else "audit-unnamed"

tex = io.open(TEX, encoding="utf-8").read()
tasks = []


def task(name, state, detail):
    """state: 'pass' | 'fail' | 'pending' | 'manual'"""
    tasks.append({"task": name, "state": state, "detail": detail})


def evidence_rows():
    """The evidence table's data rows, parsed from the manuscript itself."""
    i = tex.index(r"\label{tab:evidence}")
    s = tex.rindex(r"\begin{table*}", 0, i)
    e = tex.index(r"\end{table*}", i)
    out = {}
    for line in tex[s:e].split("\n"):
        line = line.strip()
        m = re.match(r"^(E\d\d|C\d)\b", line)
        if m and line.count("&") >= 9:
            out[m.group(1)] = [c.strip() for c in line.rstrip("\\").split("&")]
    return out


def audit_csv(name):
    path = os.path.join(AUDIT, name)
    return list(csv.DictReader(io.open(path, encoding="utf-8-sig")))


ROWS = evidence_rows()
VAL = {k: v[6] for k, v in ROWS.items()}

# ---------------------------------------------------------------- major items

# M1 + M5: full-text assessment of the complement, and the C7 power check.
a15 = os.path.join(AUDIT, "A15_complement_fulltext.csv")
if not os.path.exists(a15):
    strong = "names and measures its hardware" in tex
    task("M1/M5 complement assessed in full text", "pending",
         "A15_complement_fulltext.csv absent; C1--C7 are still abstract-level. "
         + ("The manuscript still claims C7 'names and measures its hardware', which the review "
            "rejects as too strong for an abstract-only assessment."
            if strong else
            "The overclaiming phrase has been removed; the figures still need the abstract-reported label."))
else:
    rows = audit_csv("A15_complement_fulltext.csv")
    ids = {r.get("id", "") for r in rows}
    want = {f"C{i}" for i in range(1, 8)}
    noboundary = [r.get("id") for r in rows if not (r.get("latency_boundary") or "").strip()
                  or not (r.get("energy_boundary") or "").strip()]
    if want - ids:
        task("M1/M5 complement assessed in full text", "fail",
             f"missing rows for {sorted(want - ids)}")
    elif noboundary:
        task("M1/M5 complement assessed in full text", "fail",
             f"no measurement boundary recorded for {noboundary} -- the review asks specifically "
             "for the boundaries of latency and energy")
    else:
        task("M1/M5 complement assessed in full text", "pass",
             f"{len(rows)} records with hardware, runtime and both measurement boundaries")

# C7's arithmetic: the review derived 20-30 W from 100-150 uJ over 5 us.
c7 = " ".join(ROWS.get("C7", []))
if re.search(r"5\s*\\,?\$?\\mu\$?s", c7) or "5\\,$\\mu$s" in tex:
    labelled = "abstract-reported" in tex or "abstract-level" in c7
    task("M5 C7 energy/latency qualified", "pass" if labelled else "fail",
         "the 5 us / 100--150 uJ pair is marked as abstract-reported"
         if labelled else
         "the pair implies 20--30 W at one boundary; until the full text settles the two "
         "boundaries it must be labelled abstract-reported")
else:
    task("M5 C7 energy/latency qualified", "pass", "the unverified pair is no longer printed")

# M2: provenance.
has60 = re.search(r"\b60\b", tex) and re.search(r"\b59\b", tex)
reconciled = bool(re.search(r"59 of (them|the 60)|for 59 of", tex))
task("M2 60-vs-59 reconciled", "pass" if (has60 and reconciled) else "fail",
     "both counts appear and the text says which 59 of the 60 carry a logged suggestion"
     if (has60 and reconciled) else
     "the review flags '60 checked records but 59 logged records'; both numbers must appear "
     "with their relationship stated")

leftover = tex.count("rule-eligible")
task("M2 'rule-positive search records' used consistently", "pass" if leftover == 0 else "fail",
     "no 'rule-eligible' remains" if leftover == 0 else f"{leftover} occurrences of 'rule-eligible' left")

try:
    r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", TAG + "^{commit}"],
                       cwd=ROOT, capture_output=True, text=True)
    tagged = r.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", tagged):
        tagged = ""
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()
    if not tagged:
        task("M2 audit package cited at a fixed release", "fail",
             f"the manuscript cites tag {TAG}, which does not exist yet")
    else:
        # What matters is not that the tag is HEAD -- work continues after it -- but that the
        # audit package a reader fetches at that tag is the one this manuscript describes.
        drift = subprocess.run(["git", "diff", "--quiet", tagged, "HEAD", "--",
                                "expand25/audit"], cwd=ROOT).returncode
        if drift:
            changed = subprocess.run(["git", "diff", "--name-only", tagged, "HEAD", "--",
                                      "expand25/audit"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.split()
            task("M2 audit package cited at a fixed release", "fail",
                 f"the audit package has changed since {TAG}: {changed}. Re-tag before sending, "
                 "or the cited release will not be the package described here.")
        else:
            task("M2 audit package cited at a fixed release", "pass",
                 f"tag {TAG} exists at {tagged[:8]} and its audit package matches the working tree")
except Exception as exc:                                      # pragma: no cover
    task("M2 audit package cited at a fixed release", "fail", f"git check failed: {exc}")

task("M2 cited release named in the manuscript",
     "pass" if TAG in tex else "fail",
     f"the manuscript names {TAG}" if TAG in tex else f"the manuscript does not name {TAG}")

ledger = os.path.exists(os.path.join(AUDIT, "A16_selection_ledger.csv"))
legacy = "legacy purposive set" in tex or "retained from drafting" in tex
task("M2 selection ledger and legacy set", "pass" if (ledger and legacy) else "pending",
     "A16 ledger present and the original twelve are named as a legacy set"
     if (ledger and legacy) else
     f"ledger: {'present' if ledger else 'absent'}; legacy wording: {'present' if legacy else 'absent'}")

# M3: independent verification -- tooling cannot close this one.
icheck = os.path.join(ROOT, "review", "independent_check")
if not os.path.isdir(icheck):
    task("M3 independent verification", "pending",
         "no second-reviewer worksheet yet; the review states that disclosure does not resolve "
         "possible confirmation or extraction errors")
else:
    sheets = [f for f in os.listdir(icheck) if f.endswith(".csv")]
    leaked = []
    for f in sheets:
        cols = (audit_csv.__defaults__ and []) or list(
            csv.DictReader(io.open(os.path.join(icheck, f), encoding="utf-8-sig")).fieldnames or [])
        leaked += [f"{f}:{c}" for c in cols
                   if re.search(r"ours|existing|current|suggest|prior_|our_", c, re.I)]
    if leaked:
        task("M3 worksheet is blinded", "fail",
             f"columns that would show the existing coding: {leaked}. A11 failed exactly this way.")
    else:
        task("M3 worksheet is blinded", "pass",
             f"{len(sheets)} worksheet(s), none exposing the existing coding")

# M4: the study-level evidence display.
grid = os.path.join(ROOT, "expand25", "figures", "make_fig_quality.py")
task("M4 study-level evidence display", "pass" if os.path.exists(grid) else "pending",
     "generator present" if os.path.exists(grid) else
     "no compact per-study quality display yet (review asks for reported / not reported / unclear / "
     "abstract-only, and forbids an aggregate score)")

# M6: the service-evaluation metric.
def brace_arg(s, start):
    """Return the balanced {...} argument beginning at s[start] == '{'."""
    assert s[start] == "{"
    d = 0
    for j in range(start, len(s)):
        if s[j] == "{":
            d += 1
        elif s[j] == "}":
            d -= 1
            if d == 0:
                return s[start + 1:j], j + 1
    return "", start


k = tex.find(r"\widehat{e}_{\mathrm{valid}}=")
f = tex.find(r"\frac{", k) if k >= 0 else -1
if f < 0:
    task("M6 outcome-observed indicator in Eq. (4)", "fail", "could not locate the loss expression")
else:
    num, nxt = brace_arg(tex, f + len(r"\frac"))
    den, _ = brace_arg(tex, nxt)
    both = "O_i" in num and "O_i" in den
    task("M6 outcome-observed indicator in Eq. (4)", "pass" if both else "fail",
         "O_i appears in both numerator and denominator"
         if both else f"numerator has O_i: {'O_i' in num}; denominator has O_i: {'O_i' in den}")

zero = bool(re.search(r"=0\$? the error term is undefined|zero denominator|undefined and should be reported", tex))
delay = "delay between" in tex and "Label availability" in tex
task("M6 label availability, delay and zero denominator", "pass" if (zero and delay) else "fail",
     "all three stated" if (zero and delay) else
     f"zero-denominator handling: {zero}; label availability and delay reported separately: {delay}")

# M7: the worked example.
worked = bool(re.search(r"[Ww]orked (model-selection )?example", tex))
task("M7 worked model-selection example", "pass" if worked else "pending",
     "present" if worked else "recommended enhancement, not yet added")

# ---------------------------------------------------------------- minor items

# m1: E18 coded as a temporal hold-out everywhere.
e18_tex = VAL.get("E18", "")
cross = {r["id"]: r.get("validation_code", "") for r in audit_csv("A08_study_id_crosswalk.csv")}
legend = re.search(r"Val\.: ([^.]*)\.", tex)
legend_txt = legend.group(1) if legend else ""
ok = e18_tex == "T" and cross.get("E18") == "T" and "T temporal" in legend_txt
task("m1 E18 validation code", "pass" if ok else "fail",
     "table, crosswalk and legend all say T (temporal hold-out), matching A05's 90/10 month split"
     if ok else f"table={e18_tex!r} crosswalk={cross.get('E18')!r} legend defines T: {'T temporal' in legend_txt}")

# Legend and table must agree in both directions -- no undefined code, none unused.
used = set()
for v in VAL.values():
    used |= set(re.findall(r"[WARSCPT]", v))
    if "?" in v:
        used.add("?")
    if v == "--":
        used.add("--")
defined = set(re.findall(r"\b([WARSCPT])\b", legend_txt))
if "?" in legend_txt:
    defined.add("?")
if "--" in legend_txt or "no predictive hold-out" in legend_txt:
    defined.add("--")
task("m1 validation legend matches the cells", "pass" if used == defined else "fail",
     f"codes used == codes defined ({sorted(used)})" if used == defined else
     f"defined but unused: {sorted(defined - used)}; used but undefined: {sorted(used - defined)}")

# m2: the VII-B contradiction.
bad = "implement nothing and measure nothing" in tex
fixed = "implement no new patient-level world model" in tex
task("m2 reviews and frameworks described accurately", "pass" if (fixed and not bad) else "fail",
     "restated as implementing no new patient-level world model or connected service, with their "
     "evidence audits described" if (fixed and not bad) else
     f"old contradictory phrase present: {bad}; corrected phrase present: {fixed}")

# m3: RQ1's referent.
rq1 = "studies explicitly model spatial structure" in tex
task("m3 spatial finding explicit in the conclusion", "pass" if rq1 else "fail",
     "RQ1 names the referent" if rq1 else "'ten studies model it' still has an unclear referent")

# m4: E21's inherited descriptors.
inherited = "not established from the assessed source" in tex
task("m4 E21 inherited descriptors", "pass" if inherited else "pending",
     "unverified descriptors are marked as not established from the assessed source"
     if inherited else "E21's inherited descriptors still need the full text or the explicit label")

# m5: the BLE measurement's historical context.
ble = "Bluetooth~4.0 configuration measured in 2012" in tex and "Bluetooth Core" in tex
task("m5 BLE throughput in context", "pass" if ble else "fail",
     "dated to 2012 and Bluetooth 4.0, with current capability pointed at the Core Specification"
     if ble else "the figure still reads as a general current throughput limit")

# m6: density, and the machine-readable strings.
small = tex.count(r"\scriptsize")
strings_file = os.path.exists(os.path.join(AUDIT, "A14_code_and_query_logs",
                                           "db_queries_original_blocks.txt"))
task("m6 machine-readable search strings retained", "pass" if strings_file else "fail",
     "db_queries_original_blocks.txt is in the audit package" if strings_file else "absent")
task("m6 table density", "manual" if small else "pass",
     f"{small} \\scriptsize use(s) remain -- the review asks that the final two-column PDF be "
     "checked at normal reading size, which only a person can do" if small else
     "no \\scriptsize remains")

# m7: the assessed preprint versions.
vers = "arXiv:2602.03569" in tex and "arXiv:2605.21963" in tex
task("m7 world-model additions retain their limits", "pass" if vers else "fail",
     "the assessed arXiv versions are named" if vers else "the assessed source version is not identified")

# m8: the disclosure.
m = re.search(r"The authors disclose[^\n]*", tex)
words = len(m.group(0).split()) if m else 0
seg = (m.group(0) if m else "").lower()
roles = all(k in seg for k in ("screen", "extract", "fig", "verif"))
task("m8 AI disclosure simplified but complete", "pass" if (m and words <= 90 and roles) else "pending",
     f"{words} words, four roles present: {roles}" if m else "disclosure not found")

# The reference list's final page.
trig = re.search(r"\\IEEEtriggeratref\{(\d+)\}", tex)
task("reference list final page balanced", "manual",
     f"trigger is at {trig.group(1)} of 114 references; the balance of the last page can only be "
     "confirmed by looking at the compiled PDF" if trig else "no trigger set")

# The delivery gate.
log = os.path.join(ROOT, "review", "sent_pdfs.json")
gate = os.path.join(ROOT, "review", "record_sent_pdf.py")
if not os.path.exists(log):
    task("delivery gate: no PDF sent twice",
         "pending" if os.path.exists(gate) else "fail",
         "record_sent_pdf.py is in place and refuses a repeat send; no send has been recorded yet, "
         "so run it on the PDF before attaching it"
         if os.path.exists(gate) else
         "no gate at all; the 10-29 review's first finding was that the attachment was "
         "byte-identical to the previous one")
else:
    sent = json.load(io.open(log, encoding="utf-8"))
    hashes = [e.get("sha256") for e in sent]
    dup = len(hashes) != len(set(hashes))
    task("delivery gate: no PDF sent twice", "fail" if dup else "pass",
         "a hash appears twice in the send log" if dup else f"{len(sent)} send(s), all distinct")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    n = {s: sum(1 for t in tasks if t["state"] == s) for s in ("pass", "fail", "pending", "manual")}
    if a.json:
        msg = (f"R29: {n['pass']} pass, {n['fail']} fail, {n['pending']} pending, "
               f"{n['manual']} manual")
        print(json.dumps({"systemMessage": msg,
                          "hookSpecificOutput": {"hookEventName": "Stop",
                                                 "additionalContext": json.dumps(tasks)}}))
        return
    mark = {"pass": "PASS", "fail": "FAIL", "pending": "PEND", "manual": "MANU"}
    for t in tasks:
        print(f"[{mark[t['state']]}] {t['task']}")
        print(f"        {t['detail']}")
    print(f"\n{n['pass']} pass, {n['fail']} fail, {n['pending']} pending, {n['manual']} manual")
    print("\nPENDING items need a full text, a second reader or a compiled PDF. They are not "
          "failures, and they are not done either -- reporting them as done is how the last "
          "three rounds were lost.")


if __name__ == "__main__":
    main()
