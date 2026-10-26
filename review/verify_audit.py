#!/usr/bin/env python3
"""Check every file of the audit package against the checksums in its own manifest.

The manifest exists so a reader can confirm that the copy they obtained is the copy
the article describes. That only works if the checksums are right: when the package
was first assembled, ten of the thirty-five were computed over CRLF line endings
while the files themselves are LF, so they did not verify. This script is what keeps
that from recurring -- run it after anything touches `expand25/audit/`.

It also checks coverage in both directions, because a manifest that silently omits a
file is as misleading as a wrong checksum.

    python3 review/verify_audit.py            # report, exit 1 on any mismatch
    python3 review/verify_audit.py --fix      # rewrite the checksums from the files
"""
import argparse, hashlib, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "expand25", "audit")
MANIFEST = os.path.join(AUDIT, "MANIFEST.md")
ROW = re.compile(r"^\|\s*([^|]+?)\s*\|([^|]*)\|\s*([0-9a-f]{16})\s*\|", re.M)


def digest(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def listed_files():
    """Every file in the package except the manifest, as manifest-relative paths."""
    out = set()
    for r, _, fs in os.walk(AUDIT):
        for f in fs:
            if f == "MANIFEST.md":
                continue
            out.add(os.path.relpath(os.path.join(r, f), AUDIT))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    a = ap.parse_args()

    if not os.path.exists(MANIFEST):
        print("no manifest at", MANIFEST)
        sys.exit(1)
    text = open(MANIFEST, encoding="utf-8").read()
    rows = ROW.findall(text)
    listed = {n.strip().strip("`") for n, _, _ in rows}
    actual = listed_files()

    problems = []
    for name, _, want in rows:
        rel = name.strip().strip("`")
        path = os.path.join(AUDIT, rel)
        if not os.path.exists(path):
            problems.append(f"{rel}: listed in the manifest but not present")
            continue
        got = digest(path)
        if got != want:
            problems.append(f"{rel}: manifest says {want}, file is {got}")
    for rel in sorted(actual - listed):
        problems.append(f"{rel}: present but not listed in the manifest")

    if a.fix:
        def repl(m):
            rel = m.group(1).strip().strip("`")
            p = os.path.join(AUDIT, rel)
            if not os.path.exists(p):
                return m.group(0)
            return f"| {m.group(1)} |{m.group(2)}| {digest(p)} |"
        open(MANIFEST, "w", encoding="utf-8").write(ROW.sub(repl, text))
        print(f"rewrote the checksums of {len(rows)} entries from the files themselves")
        return

    print(f"audit package: {len(rows)} entries listed, {len(actual)} files present")
    for p in problems:
        print("  " + p)
    if problems:
        print(f"\n{len(problems)} problem(s); run with --fix to recompute the checksums")
        sys.exit(1)
    print("every file verifies against the manifest, and the listing is complete")


if __name__ == "__main__":
    main()
