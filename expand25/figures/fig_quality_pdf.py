#!/usr/bin/env python3
"""Render fig_quality.svg to fig_quality.pdf with PyMuPDF.

The SVG is written by make_fig_quality.py and uses only rect, line, path (one straight stroke)
and text. This renderer draws exactly those, so the dashed outline of the abstract-only glyph
survives -- a generic SVG import drops stroke-dasharray. Nothing is classified here: the PDF is a
drawing of the SVG and of nothing else.

    python3 make_fig_quality.py && python3 fig_quality_pdf.py
"""
import os, re
import xml.etree.ElementTree as ET
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, "fig_quality.svg")
OUT = os.path.join(HERE, "fig_quality.pdf")
K = 0.75  # CSS px to pt


def rgb(h):
    if not h or h == "none":
        return None
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def main():
    root = ET.parse(SVG).getroot()
    W, H = float(root.get("width")), float(root.get("height"))
    doc = fitz.open()
    page = doc.new_page(width=W * K, height=H * K)
    n = {"rect": 0, "line": 0, "path": 0, "text": 0}
    for el in root:
        tag = el.tag.split("}")[1]
        a = el.attrib
        if tag == "rect":
            x, y = float(a.get("x", 0)) * K, float(a.get("y", 0)) * K
            r = fitz.Rect(x, y, x + float(a["width"]) * K, y + float(a["height"]) * K)
            sw = float(a.get("stroke-width", 0)) * K
            dash = a.get("stroke-dasharray")
            dashes = "[%s] 0" % " ".join(str(float(v) * K) for v in dash.split()) if dash else None
            radius = float(a["rx"]) / float(a["width"]) if a.get("rx") else None
            page.draw_rect(r, color=rgb(a.get("stroke")), fill=rgb(a.get("fill")),
                           width=sw if a.get("stroke") else 0, dashes=dashes, radius=radius)
        elif tag == "line":
            page.draw_line((float(a["x1"]) * K, float(a["y1"]) * K), (float(a["x2"]) * K, float(a["y2"]) * K),
                           color=rgb(a["stroke"]), width=float(a["stroke-width"]) * K)
        elif tag == "path":
            v = [float(t) * K for t in re.findall(r"-?\d+\.?\d*", a["d"])]
            page.draw_line((v[0], v[1]), (v[2], v[3]), color=rgb(a["stroke"]),
                           width=float(a["stroke-width"]) * K)
        elif tag == "text":
            x, y, size = float(a["x"]) * K, float(a["y"]) * K, float(a["font-size"]) * K
            text = el.text or ""
            if a.get("transform", "").startswith("rotate(-90"):
                page.insert_text((x, y), text, fontname="helv", fontsize=size, color=rgb(a["fill"]), rotate=90)
            else:
                if a.get("text-anchor") == "end":
                    x -= fitz.get_text_length(text, fontname="helv", fontsize=size)
                page.insert_text((x, y), text, fontname="helv", fontsize=size, color=rgb(a["fill"]))
        else:
            raise SystemExit("unexpected SVG element: " + tag)
        n[tag] += 1
    doc.save(OUT, garbage=3, deflate=True)
    print("wrote", os.path.basename(OUT), n, "page", page.rect)


if __name__ == "__main__":
    main()
