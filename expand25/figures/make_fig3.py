#!/usr/bin/env python3
"""Generate fig3.svg: the five spatiotemporal data types of connected digital health.

This replaces the hand-coded TikZ version with a vector drawing that follows the
layout the authors supplied, and it keeps the two corrections the 22 October 2026
review asked for: panel (d) shows one gridded field sampled at regular times, and
panel (e) shows ordered image frames. The earlier uploaded artwork had those two
panels wrong -- its "raster" panel showed sparse labelled points (indistinguishable
from the event panel) and its "video" panel showed a single static grid.

Everything is drawn as vector geometry, so the figure stays crisp in print and
carries no third-party or generated bitmap artwork.

    python3 make_fig3.py            # writes fig3.svg next to this script
"""
import math
import os

W, H = 1469, 1080
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig3.svg")

BG      = "#f7f7f7"
BG_EDGE = "#e3e3e3"
PANEL   = "#ffffff"
P_EDGE  = "#e6e6e6"
BLUE    = "#a9c9f2"
PINK    = "#f9c6cc"
GREEN   = "#c7e9a3"
LINK    = "#b9d3f5"
INK     = "#141414"
GRIDLN  = "#8fb3e0"

FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"
out = []
def add(s): out.append(s)


def panel(x, y, w, h, fill=PANEL, edge=P_EDGE):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
        f'fill="{fill}" stroke="{edge}" stroke-width="2"/>')


def caption(cx, y, text):
    add(f'<text x="{cx}" y="{y}" font-family="{FONT}" font-size="27" font-weight="700" '
        f'fill="{INK}" text-anchor="middle">{text}</text>')


def dot_label(cx, cy, colour, l1, l2, dx=30):
    """A filled marker with a two-line label to its right."""
    add(f'<circle cx="{cx}" cy="{cy}" r="22" fill="{colour}"/>')
    for i, line in enumerate((l1, l2)):
        add(f'<text x="{cx+dx}" y="{cy - 6 + i*30}" font-family="{FONT}" font-size="23" '
            f'fill="{INK}">{line}</text>')


def blob(cx, cy, r, squash, seed, fill, stroke="#1a1a1a"):
    """A closed smooth contour: a circle perturbed by a fixed pseudo-random profile."""
    n = 14
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        wob = 1 + 0.085 * math.sin(3 * a + seed) + 0.055 * math.cos(5 * a + 2 * seed)
        pts.append((cx + r * wob * math.cos(a), cy + r * wob * squash * math.sin(a)))
    # Catmull-Rom through the points, emitted as cubic Beziers
    d = f'M {pts[0][0]:.1f} {pts[0][1]:.1f}'
    for k in range(n):
        p0 = pts[(k - 1) % n]; p1 = pts[k]; p2 = pts[(k + 1) % n]; p3 = pts[(k + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += (f' C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}')
    add(f'<path d="{d} Z" fill="{fill}" stroke="{stroke}" stroke-width="2.4"/>')


def arrow(x1, x2, y, label):
    add(f'<line x1="{x1}" y1="{y}" x2="{x2-16}" y2="{y}" stroke="{INK}" stroke-width="3.2"/>')
    add(f'<path d="M {x2} {y} L {x2-18} {y-9} L {x2-18} {y+9} Z" fill="{INK}"/>')
    add(f'<text x="{(x1+x2)/2}" y="{y+34}" font-family="{FONT}" font-size="24" '
        f'fill="{INK}" text-anchor="middle">{label}</text>')


# ---------------------------------------------------------------- canvas
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
add(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="6" fill="{BG}" '
    f'stroke="{BG_EDGE}" stroke-width="2"/>')

# ------------------------------------------------- (a) event: sparse marks
panel(48, 62, 417, 393)
dot_label(291, 147, BLUE,  "Flu", "2025-3-11")
dot_label(113, 225, PINK,  "COVID-19", "2025-1-3")
dot_label(243, 355, GREEN, "COVID-19", "2025-2-20")
caption(256, 497, "(a) Event Data")

# ------------------------------------- (b) trajectory: one subject in order
panel(528, 62, 417, 393)
n1, n2, n3, n4 = (605, 140), (692, 222), (797, 292), (612, 395)
for p, q in ((n1, n2), (n2, n4), (n4, n3)):
    add(f'<line x1="{p[0]}" y1="{p[1]}" x2="{q[0]}" y2="{q[1]}" stroke="{LINK}" '
        f'stroke-width="11" stroke-linecap="round"/>')
for p, l1, l2, dx in ((n1, "Patient A", "2025-1-3", 30),
                      (n2, "Patient A", "2025-1-4", 30),
                      (n3, "Patient A", "2025-2-10", 30),
                      (n4, "Patient A", "2025-2-3", 36)):
    add(f'<circle cx="{p[0]}" cy="{p[1]}" r="22" fill="{BLUE}"/>')
    add(f'<text x="{p[0]+dx}" y="{p[1]-6}" font-family="{FONT}" font-size="23" fill="{INK}">{l1}</text>')
    add(f'<text x="{p[0]+dx}" y="{p[1]+24}" font-family="{FONT}" font-size="23" fill="{INK}">{l2}</text>')
caption(736, 497, "(b) Trajectory Data")

# ------------------------------- (c) point reference: a field read at sites
panel(1009, 62, 419, 393, fill="#fbe3e6", edge="#f3d3d7")
blob(1218, 262, 168, 0.95, 0.0, "#fbdce0")
blob(1224, 256, 124, 0.92, 1.1, "#fad2d7")
blob(1232, 250,  80, 0.90, 2.2, "#f9c6cc")
caption(1218, 497, "(c) Point Reference Data")

# ----------------------- (d) raster: ONE gridded field at regular times
panel(40, 545, 679, 385)
FIELDS = [
    ["PPPPPP", "PPBBPP", "BBBPPG", "BBBPPG", "BBBPPG", "BBPPPG"],
    ["PPPPPP", "PPBBPP", "BBBBPG", "BBBPPG", "BBPPPG", "BBPPPG"],
    ["PPPPPP", "PPBBBP", "BBBBPG", "BBBBPG", "BBBPPG", "BBPPPG"],
]
COL = {"P": PINK, "B": BLUE, "G": GREEN}
cell = 26
for gi, (gx, tlabel) in enumerate(zip((68, 288, 508), ("t = 0", "t = Δt", "t = 2Δt"))):
    gy = 597
    for r, row in enumerate(FIELDS[gi]):
        for c, ch in enumerate(row):
            add(f'<rect x="{gx+c*cell}" y="{gy+r*cell}" width="{cell}" height="{cell}" '
                f'fill="{COL[ch]}" stroke="{GRIDLN}" stroke-width="1.1"/>')
    add(f'<text x="{gx+3*cell}" y="{gy+6*cell+34}" font-family="{FONT}" font-size="24" '
        f'fill="{INK}" text-anchor="middle">{tlabel}</text>')
arrow(72, 648, 872, "Time")
caption(380, 972, "(d) Raster Data")

# ------------------------------- (e) video: ordered frames of one scene
panel(740, 545, 690, 385)


def scene(ox, oy, w, h, walk):
    """One video frame: the same scene with the subject further along the path."""
    g = f'<g transform="translate({ox},{oy})">'
    add(g)
    add(f'<clipPath id="clip{int(walk*100)}"><rect x="0" y="0" width="{w}" height="{h}" rx="3"/></clipPath>')
    add(f'<g clip-path="url(#clip{int(walk*100)})">')
    add(f'<rect x="0" y="0" width="{w}" height="{h}" fill="#cfe9f7"/>')                 # sky
    add(f'<path d="M 0 {h*0.46} L {w*0.26} {h*0.26} L {w*0.46} {h*0.46} Z" fill="#aac4cf"/>')
    add(f'<path d="M {w*0.30} {h*0.47} L {w*0.58} {h*0.22} L {w*0.86} {h*0.47} Z" fill="#bcd2db"/>')
    add(f'<rect x="0" y="{h*0.46}" width="{w}" height="{h*0.20}" fill="#bcd98f"/>')      # grass
    add(f'<rect x="0" y="{h*0.66}" width="{w}" height="{h*0.34}" fill="#e6d3ad"/>')      # path
    # tree
    tx = w * 0.22
    add(f'<rect x="{tx-5}" y="{h*0.28}" width="10" height="{h*0.26}" fill="#8a6239"/>')
    for cxr, cyr, rr in ((0, -0.06, 0.13), (-0.09, 0.0, 0.10), (0.09, 0.0, 0.10)):
        add(f'<circle cx="{tx + cxr*w}" cy="{h*0.28 + cyr*h}" r="{rr*w}" fill="#6fa24d"/>')
    add(f'<circle cx="{tx}" cy="{h*0.20}" r="{0.10*w}" fill="#7fb359"/>')
    # bushes
    for bx in (0.72, 0.80, 0.88):
        add(f'<circle cx="{bx*w}" cy="{h*0.50}" r="{0.055*w}" fill="#79a85c"/>')
    # subject, placed along the path
    px, py = w * walk, h * 0.74
    add(f'<g transform="translate({px:.1f},{py:.1f})">')
    add('<path d="M -9 34 L -2 10" stroke="#243a63" stroke-width="7" stroke-linecap="round" fill="none"/>')
    add('<path d="M 10 34 L 2 10" stroke="#243a63" stroke-width="7" stroke-linecap="round" fill="none"/>')
    add('<rect x="-8" y="-12" width="16" height="24" rx="5" fill="#4a78b8"/>')
    add('<path d="M 7 -10 q 9 4 7 14 q -4 3 -8 1 Z" fill="#e08a3c"/>')
    add('<circle cx="0" cy="-20" r="8" fill="#f0c9a0"/>')
    add('<path d="M -8 -24 a 8 8 0 0 1 16 0 z" fill="#2d2a28"/>')
    add('</g>')
    add('</g>')
    add(f'<rect x="0" y="0" width="{w}" height="{h}" rx="3" fill="none" stroke="#8a8a8a" stroke-width="2"/>')
    add('</g>')


for i, (fx, walk) in enumerate(zip((768, 985, 1202), (0.34, 0.50, 0.66))):
    scene(fx, 592, 200, 205, walk)
    add(f'<text x="{fx+100}" y="{592+205+36}" font-family="{FONT}" font-size="24" '
        f'fill="{INK}" text-anchor="middle">Frame {i+1}</text>')
arrow(790, 1388, 880, "Time")
caption(1085, 972, "(e) Video Data")

add('</svg>')

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print(f"wrote {OUT}  ({len(out)} elements)")
