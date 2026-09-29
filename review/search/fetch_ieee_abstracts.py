#!/usr/bin/env python3
"""Fetch the FULL abstract of every IEEE record, per document.

The search endpoint truncates abstracts to about 400 characters, which silently
breaks the screen: criterion (iii) looks for a metric, a number and a comparison
word, and those sit in the second half of most abstracts. Screening the truncated
text returned zero eligible records out of 931, against 30 per cent on the PubMed
arm --- the artefact, not a finding. Each document's own endpoint returns the
whole abstract, and its insertion date, which dates the drift against the
2026-09-22 header counts.

Resumable: rerun after an interruption and it picks up where it stopped.

    python3 fetch_ieee_abstracts.py a
    python3 fetch_ieee_abstracts.py b
"""
import json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")


def get(num):
    req = urllib.request.Request(
        f"https://ieeexplore.ieee.org/rest/document/{num}/abstract",
        headers={"Accept": "application/json", "User-Agent": UA,
                 "Referer": f"https://ieeexplore.ieee.org/document/{num}"})
    for k in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode())
        except Exception:
            if k == 2:
                return None
            time.sleep(2 * (k + 1))


def main():
    arm = sys.argv[1]
    raw = json.load(open(os.path.join(HERE, f"ieee_{arm}_raw.json")))
    out_path = os.path.join(HERE, f"ieee_{arm}_abstracts.json")
    have = json.load(open(out_path)) if os.path.exists(out_path) else {}

    nums = [str(r.get("articleNumber")) for r in raw["records"] if r.get("articleNumber")]
    todo = [n for n in nums if n not in have]
    print(f"arm {arm}: {len(nums)} records, {len(have)} cached, {len(todo)} to fetch",
          file=sys.stderr, flush=True)

    for i, n in enumerate(todo, 1):
        d = get(n)
        have[n] = {"abstract": (d or {}).get("abstract") or "",
                   "insertDate": (d or {}).get("insertDate") or (d or {}).get("dateOfInsertion") or "",
                   "contentType": (d or {}).get("contentType") or "",
                   "ok": d is not None}
        if i % 50 == 0 or i == len(todo):
            json.dump(have, open(out_path, "w"))
            got = sum(1 for v in have.values() if v["abstract"])
            print(f"  {i}/{len(todo)} fetched; {got} with an abstract",
                  file=sys.stderr, flush=True)
        time.sleep(0.5)

    json.dump(have, open(out_path, "w"))
    got = sum(1 for v in have.values() if v["abstract"])
    ln = [len(v["abstract"]) for v in have.values() if v["abstract"]]
    print(f"arm {arm}: {got}/{len(nums)} abstracts; median length "
          f"{sorted(ln)[len(ln)//2] if ln else 0}")


if __name__ == "__main__":
    main()
