#!/usr/bin/env python3
"""Record a manuscript PDF before it is sent, and refuse to send the same bytes twice.

The 2026-10-29 review opens with this: "All 25 pages have identical extracted text and rendered
appearance to the previously reviewed manuscript... No requested correction was newly resolved in
this attachment." A round was spent on an attachment that carried nothing new. Hashing the PDFs on
this machine confirms the pattern is older than that round -- two earlier groups of manuscript PDFs
are byte-identical within the group.

So: run this on the PDF you are about to attach. It hashes the file, compares it with every PDF
already sent, and refuses when the bytes match one of them. It also records the page count and the
commit the build came from, so a later round can say exactly which version the advisor saw.

    python3 review/record_sent_pdf.py ~/Downloads/<the pdf>            # check only
    python3 review/record_sent_pdf.py ~/Downloads/<the pdf> --send \\
        --note "R29: quality grid, C7 unit, E18/E19 codes"             # record as sent
"""
import argparse, hashlib, io, json, os, re, subprocess, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "review", "sent_pdfs.json")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def page_count(path):
    """Count pages without a PDF library: /Type /Page objects, minus /Pages nodes."""
    raw = io.open(path, "rb").read()
    n = len(re.findall(rb"/Type\s*/Page[^s]", raw))
    if n:
        return n
    m = re.findall(rb"/Count\s+(\d+)", raw)
    return max((int(x) for x in m), default=0)


def git_head():
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                           capture_output=True, text=True)
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                               capture_output=True, text=True).stdout.strip()
        return r.stdout.strip() + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def load():
    if os.path.exists(LOG):
        return json.load(io.open(LOG, encoding="utf-8"))
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--send", action="store_true", help="record this PDF as sent")
    ap.add_argument("--note", default="", help="what changed since the last send")
    a = ap.parse_args()

    if not os.path.exists(a.pdf):
        sys.exit(f"no such file: {a.pdf}")

    digest = sha256(a.pdf)
    pages = page_count(a.pdf)
    sent = load()

    clash = [e for e in sent if e["sha256"] == digest]
    print(f"file   {os.path.basename(a.pdf)}")
    print(f"sha256 {digest[:16]}  pages {pages}  commit {git_head()}")
    if clash:
        print(f"\nREFUSED: these exact bytes were already sent on {clash[0]['date']}"
              f" ({clash[0].get('note') or 'no note'}).")
        print("Recompile and download again before attaching, or the advisor receives a file")
        print("identical to one she has already reviewed -- which is what happened on 10-29.")
        sys.exit(1)

    if sent:
        last = sent[-1]
        print(f"\nprevious send: {last['date']}, sha {last['sha256'][:16]}, "
              f"{last.get('pages')} pages, commit {last.get('commit')}")
        print("differs from the previous send: yes")
    else:
        print("\nno previous send recorded")

    if not a.send:
        print("\nCheck only. Re-run with --send --note \"...\" once you actually attach it.")
        return

    if not a.note.strip():
        sys.exit("--send needs --note: one line naming what changed since the last send. "
                 "The 10-29 review's first finding was that nothing had.")

    sent.append({"date": datetime.date.today().isoformat(),
                 "file": os.path.basename(a.pdf),
                 "sha256": digest,
                 "pages": pages,
                 "commit": git_head(),
                 "note": a.note.strip()})
    io.open(LOG, "w", encoding="utf-8").write(json.dumps(sent, indent=2, ensure_ascii=False) + "\n")
    print(f"\nrecorded as send #{len(sent)} in {os.path.relpath(LOG, ROOT)}")


if __name__ == "__main__":
    main()
