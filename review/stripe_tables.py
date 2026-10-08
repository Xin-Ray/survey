#!/usr/bin/env python3
"""Shade alternate data rows of every table, so a wrapped row can be followed by eye.

The tables are set with booktabs: three horizontal rules and nothing between the
rows. That is fine for a short table, but most of ours have cells that wrap to two
or three lines, and with only 1--2pt between rows a reader cannot see where one
study ends and the next begins. IEEE does not require the booktabs look -- its own
template and many published IEEE papers rule their tables differently -- so this is
ours to choose.

Shading is used rather than rules because it costs no vertical space, and the
submission build sits exactly on the eight-page limit.

Only data rows are shaded. Group-header rows (the \\multicolumn task-group lines in
Table II) get a slightly darker tint so they read as dividers, and the note rows
after \\bottomrule are left alone.

    python3 review/stripe_tables.py            # both documents
    python3 review/stripe_tables.py --undo     # remove every \\rowcolor again
"""
import argparse, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = [os.path.join(ROOT, "live", "STmodel.tex"),
         os.path.join(ROOT, "live", "supplement.tex")]
STRIPE = r"\rowcolor{tablestripe}"
GROUP = r"\rowcolor{tablegroup}"


def is_data_row(line):
    s = line.strip()
    return (s.endswith(r"\\") and "&" in s
            and "multicolumn" not in s
            and r"\textbf{Study}" not in s
            and not s.startswith(r"\textbf{"))


def is_group_row(line):
    s = line.strip()
    return bool(re.match(r"\\multicolumn\{\d+\}\{l\}\{\\emph\{", s))


def process(text, undo):
    if undo:
        return re.sub(r"\\rowcolor\{table(stripe|group)\}\s*", "", text)
    out, n_stripe, n_group = [], 0, 0
    in_body = False          # between \midrule and \bottomrule
    parity = 0
    for line in text.split("\n"):
        s = line.strip()
        if r"\midrule" in s and r"\bottomrule" not in s:
            in_body, parity = True, 0
            out.append(line); continue
        if r"\bottomrule" in s:
            in_body = False
            out.append(line); continue
        if in_body and r"\rowcolor" not in s:
            if is_group_row(line):
                out.append(re.sub(r"^(\s*)", r"\1" + GROUP.replace("\\", "\\\\"), line, count=1))
                n_group += 1
                parity = 0          # restart the alternation inside each group
                continue
            if is_data_row(line):
                if parity % 2 == 1:
                    out.append(re.sub(r"^(\s*)", r"\1" + STRIPE.replace("\\", "\\\\"), line, count=1))
                    n_stripe += 1
                else:
                    out.append(line)
                parity += 1
                continue
        out.append(line)
    return "\n".join(out), n_stripe, n_group


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--undo", action="store_true")
    a = ap.parse_args()
    for f in FILES:
        t = open(f, encoding="utf-8").read()
        if a.undo:
            open(f, "w", encoding="utf-8").write(process(t, True))
            print(f"{os.path.basename(f)}: shading removed")
            continue
        new, n_s, n_g = process(t, False)
        open(f, "w", encoding="utf-8").write(new)
        print(f"{os.path.basename(f)}: {n_s} rows shaded, {n_g} group headers tinted")


if __name__ == "__main__":
    main()
