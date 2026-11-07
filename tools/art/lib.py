"""Tiny SVG drawing library for the verse illustrations.

Everything is hand-composed from simple shapes: gradient skies, layered hills,
miniature-style waves and clouds, lotuses, lamps, and jointed figures drawn as
rounded strokes (the look of a shadow-puppet / paper-cut silhouette with gold
ornaments). No external images or models are used.
"""
import math
import random

W, H = 600, 900
DEVA_FONT = "'Kohinoor Devanagari','Noto Sans Devanagari','Noto Serif Devanagari','Mangal','Nirmala UI',sans-serif"


def f(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def pt(p):
    return f"{f(p[0])},{f(p[1])}"


def smooth(pts, closed=False):
    """Catmull-Rom spline through pts, as an SVG path 'd' (without fill commands)."""
    if len(pts) < 3:
        return "M" + " L".join(pt(p) for p in pts)
    P = list(pts)
    if closed:
        P = [pts[-1]] + list(pts) + [pts[0], pts[1]]
        rng = range(1, len(P) - 2)
        d = "M" + pt(P[1])
    else:
        P = [pts[0]] + list(pts) + [pts[-1]]
        rng = range(1, len(P) - 2)
        d = "M" + pt(P[1])
    for i in rng:
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{pt(c1)} {pt(c2)} {pt(p2)}"
    return d + (" Z" if closed else "")


def rot(p, a, c=(0, 0)):
    s, co = math.sin(a), math.cos(a)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * co - y * s, c[1] + x * s + y * co)


class Scene:
    def __init__(self, key):
        self.key = key
        self.defs = []
        self.out = []
        self.n = 0
        self.r = random.Random(key)

    def uid(self, p="g"):
        self.n += 1
        return f"{p}{self.n}"

    @staticmethod
    def _stops(stops):
        s = ""
        for st in stops:
            o, c = st[0], st[1]
            a = st[2] if len(st) > 2 else 1
            s += f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a != 1 else "") + "/>"
        return s

    def lin(self, stops, x1=0, y1=0, x2=0, y2=1, user=False):
        i = self.uid()
        u = ' gradientUnits="userSpaceOnUse"' if user else ""
        self.defs.append(f'<linearGradient id="{i}" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"{u}>{self._stops(stops)}</linearGradient>')
        return f"url(#{i})"

    def rad(self, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None):
        i = self.uid()
        fxy = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
        self.defs.append(f'<radialGradient id="{i}" cx="{cx}" cy="{cy}" r="{r}"{fxy}>{self._stops(stops)}</radialGradient>')
        return f"url(#{i})"

    def filt_blur(self, sd):
        i = self.uid("b")
        self.defs.append(f'<filter id="{i}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{sd}"/></filter>')
        return f"url(#{i})"

    def add(self, *xs):
        self.out.extend(xs)

    def group(self, inner, **attrs):
        a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        return f"<g {a}>{''.join(inner)}</g>"

    def svg(self, title=""):
        t = f"<title>{title}</title>" if title else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">{t}'
                f'<defs>{"".join(self.defs)}</defs>{"".join(self.out)}</svg>')


# ───────────────────────── atmosphere ─────────────────────────

def sky(S, stops):
    S.add(f'<rect width="{W}" height="{H}" fill="{S.lin(stops)}"/>')


def glow(S, cx, cy, r, color, a=0.8, mid=0.35):
    g = S.rad([(0, color, a), (mid, color, a * 0.45), (1, color, 0)])
    S.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{g}"/>')


def sun(S, cx, cy, r, core="#fffbe6", rim="#ffb340", halo="#ffcf6e", rays=True, ray_color="#ffe6a3", ray_a=0.45, n=36):
    glow(S, cx, cy, r * 4.2, halo, 0.6)
    if rays:
        out = []
        for i in range(n):
            a = 2 * math.pi * i / n
            L = r * (2.3 if i % 2 == 0 else 1.65)
            w = math.radians(2.6 if i % 2 == 0 else 1.8)
            p1 = (cx + r * 1.08 * math.cos(a - w), cy + r * 1.08 * math.sin(a - w))
            p2 = (cx + L * math.cos(a), cy + L * math.sin(a))
            p3 = (cx + r * 1.08 * math.cos(a + w), cy + r * 1.08 * math.sin(a + w))
            out.append(f"M{pt(p1)} L{pt(p2)} L{pt(p3)} Z")
        S.add(f'<path d="{" ".join(out)}" fill="{ray_color}" opacity="{ray_a}"/>')
    S.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{S.rad([(0, core), (0.62, core), (1, rim)])}"/>')


def moon(S, cx, cy, r, color="#fff6d8", sky_glow="#cfd8ff", phase=0.38, a=1):
    glow(S, cx, cy, r * 4, sky_glow, 0.35)
    m = S.uid("m")
    S.defs.append(f'<mask id="{m}"><rect x="{f(cx - r * 2)}" y="{f(cy - r * 2)}" width="{f(r * 4)}" height="{f(r * 4)}" fill="#fff"/>'
                  f'<circle cx="{f(cx + r * phase * 2)}" cy="{f(cy - r * phase)}" r="{f(r * 0.95)}" fill="#000"/></mask>')
    S.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{color}" mask="url(#{m})" opacity="{a}"/>')


def full_moon(S, cx, cy, r, color="#fff3d1", halo="#d7dcff"):
    glow(S, cx, cy, r * 4.5, halo, 0.4)
    S.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{S.rad([(0, "#fffdf2"), (0.7, color), (1, "#f0d9a8")])}"/>')


def stars(S, n, y0=0, y1=500, color="#fff8e0", rmax=1.7, a=0.85, x0=0, x1=W):
    out = []
    for _ in range(n):
        x, y = S.r.uniform(x0, x1), S.r.uniform(y0, y1)
        r = S.r.uniform(0.4, rmax)
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" opacity="{f(S.r.uniform(0.35, 1))}"/>')
    S.add(f'<g fill="{color}" opacity="{a}">{"".join(out)}</g>')
    # a few twinkles
    tw = []
    for _ in range(max(2, n // 25)):
        x, y = S.r.uniform(x0, x1), S.r.uniform(y0, y1)
        s = S.r.uniform(3, 6)
        tw.append(f"M{f(x - s)},{f(y)} L{f(x + s)},{f(y)} M{f(x)},{f(y - s)} L{f(x)},{f(y + s)}")
    S.add(f'<path d="{" ".join(tw)}" stroke="{color}" stroke-width=".8" opacity="{a * 0.8}"/>')


def particles(S, n, x0=0, y0=0, x1=W, y1=H, color="#ffe3a0", rmax=2.4, a=0.7):
    out = []
    for _ in range(n):
        x, y = S.r.uniform(x0, x1), S.r.uniform(y0, y1)
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(S.r.uniform(0.6, rmax))}" opacity="{f(S.r.uniform(0.25, 1))}"/>')
    S.add(f'<g fill="{color}" opacity="{a}">{"".join(out)}</g>')


def vignette(S, a=0.45, color="#000"):
    S.add(f'<rect width="{W}" height="{H}" fill="{S.rad([(0, color, 0), (0.62, color, 0), (1, color, a)], r=0.75)}"/>')


def beams(S, cx, cy, n, length, color, a=0.25, a0=-math.pi, a1=0, width=0.06):
    out = []
    for i in range(n):
        ang = a0 + (a1 - a0) * (i + 0.5) / n
        p1 = (cx + length * math.cos(ang - width), cy + length * math.sin(ang - width))
        p2 = (cx + length * math.cos(ang + width), cy + length * math.sin(ang + width))
        out.append(f"M{f(cx)},{f(cy)} L{pt(p1)} L{pt(p2)} Z")
    g = S.rad([(0, color, a), (1, color, 0)], r=0.5)
    S.add(f'<path d="{" ".join(out)}" fill="{color}" opacity="{a}"/>')


def rings(S, cx, cy, r0, n, step, color, a=0.5, w=1.5, dash=None):
    out = []
    for i in range(n):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r0 + i * step)}" fill="none" stroke="{color}" stroke-width="{w}" opacity="{f(a * (1 - i / (n + 1)))}"{d}/>')
    S.add(*out)


def mandala(S, cx, cy, r, color="#f3c35b", a=0.55, petals=16, w=1.3):
    out = [f'<g fill="none" stroke="{color}" stroke-width="{w}" opacity="{a}">',
           f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}"/>',
           f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * 0.9)}" stroke-dasharray="2 5"/>',
           f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * 0.62)}"/>']
    for i in range(petals):
        a_ = 2 * math.pi * i / petals
        base1 = (cx + r * 0.62 * math.cos(a_ - math.pi / petals), cy + r * 0.62 * math.sin(a_ - math.pi / petals))
        base2 = (cx + r * 0.62 * math.cos(a_ + math.pi / petals), cy + r * 0.62 * math.sin(a_ + math.pi / petals))
        tip = (cx + r * 0.88 * math.cos(a_), cy + r * 0.88 * math.sin(a_))
        c1 = (cx + r * 0.8 * math.cos(a_ - math.pi / petals * 0.9), cy + r * 0.8 * math.sin(a_ - math.pi / petals * 0.9))
        c2 = (cx + r * 0.8 * math.cos(a_ + math.pi / petals * 0.9), cy + r * 0.8 * math.sin(a_ + math.pi / petals * 0.9))
        out.append(f'<path d="M{pt(base1)} Q{pt(c1)} {pt(tip)} Q{pt(c2)} {pt(base2)}"/>')
        dot = (cx + r * 0.95 * math.cos(a_), cy + r * 0.95 * math.sin(a_))
        out.append(f'<circle cx="{f(dot[0])}" cy="{f(dot[1])}" r="{f(w * 1.2)}" fill="{color}"/>')
    out.append("</g>")
    S.add(*out)


# ───────────────────────── land, water, cloud ─────────────────────────

def ridge(S, base, top, color, n=8, x0=-30, x1=W + 30, seed=None, a=1, sharp=False, bottom=H):
    r = random.Random(seed if seed is not None else S.r.random())
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    pts = []
    for i, x in enumerate(xs):
        y = r.uniform(top, top + (base - top) * 0.75) if i % 2 == 0 or not sharp else r.uniform(top + (base - top) * 0.4, base)
        pts.append((x + r.uniform(-15, 15), y))
    d = (smooth(pts) if not sharp else "M" + " L".join(pt(p) for p in pts))
    S.add(f'<path d="{d} L{f(x1)},{f(bottom)} L{f(x0)},{f(bottom)} Z" fill="{color}" opacity="{a}"/>')


def peak(S, x, base, w, h, color, snow=None, a=1):
    pts = [(x - w / 2, base), (x - w * 0.18, base - h * 0.62), (x - w * 0.06, base - h * 0.9), (x, base - h), (x + w * 0.09, base - h * 0.88), (x + w * 0.24, base - h * 0.55), (x + w / 2, base)]
    S.add(f'<path d="M{" L".join(pt(p) for p in pts)} Z" fill="{color}" opacity="{a}"/>')
    if snow:
        sp = [(x - w * 0.11, base - h * 0.78), (x - w * 0.06, base - h * 0.9), (x, base - h), (x + w * 0.09, base - h * 0.88), (x + w * 0.14, base - h * 0.74), (x + w * 0.06, base - h * 0.79), (x + 0, base - h * 0.72), (x - w * 0.05, base - h * 0.8)]
        S.add(f'<path d="M{" L".join(pt(p) for p in sp)} Z" fill="{snow}" opacity="{a}"/>')


def ocean(S, y0, top, bottom, line="#ffffff", a=0.35, y1=H, w0=26):
    S.add(f'<rect x="0" y="{f(y0)}" width="{W}" height="{f(y1 - y0)}" fill="{S.lin([(0, top), (1, bottom)])}"/>')
    out = []
    y, k = y0 + 6, 0
    while y < y1 + 10:
        t = (y - y0) / max(1, (y1 - y0))
        w = w0 * (0.5 + 1.6 * t)
        amp = w * 0.3
        x = -((k * w * 0.5) % w) - w
        d = f"M{f(x)},{f(y)}"
        while x < W + w:
            d += f" q{f(w / 2)},{f(-amp)} {f(w)},0"
            x += w
        out.append(f'<path d="{d}" opacity="{f(a * (0.35 + 0.65 * t))}" stroke-width="{f(0.8 + 1.4 * t)}"/>')
        y += 5 + 26 * t
        k += 1
    S.add(f'<g fill="none" stroke="{line}" stroke-linecap="round">{"".join(out)}</g>')


def river(S, y0, y1, top, bottom, line="#fff", a=0.3):
    ocean(S, y0, top, bottom, line, a, y1=y1, w0=40)


def cloud(S, cx, cy, s, fill="#fff", a=1, hi=None, flip=False):
    blobs = [(-34, 2, 14), (-18, -9, 18), (2, -16, 22), (24, -6, 17), (40, 3, 12), (8, 4, 16)]
    out = []
    for (x, y, r) in blobs:
        x = -x if flip else x
        out.append(f'<circle cx="{f(cx + x * s)}" cy="{f(cy + y * s)}" r="{f(r * s)}"/>')
    out.append(f'<rect x="{f(cx - 46 * s)}" y="{f(cy)}" width="{f(92 * s)}" height="{f(10 * s)}" rx="{f(5 * s)}"/>')
    S.add(f'<g fill="{fill}" opacity="{a}">{"".join(out)}</g>')
    if hi:
        # miniature-style curl on the cloud
        S.add(f'<path d="M{f(cx - 14 * s)},{f(cy - 4 * s)} q{f(6 * s)},{f(-10 * s)} {f(14 * s)},{f(-4 * s)} q{f(4 * s)},{f(4 * s)} {f(-2 * s)},{f(6 * s)}" fill="none" stroke="{hi}" stroke-width="{f(1.6 * s)}" stroke-linecap="round" opacity="{a * 0.8}"/>')


def cloudbank(S, y, color, a=1, s=1.2, n=7, hi=None, seed=None):
    r = random.Random(seed if seed is not None else S.r.random())
    for i in range(n):
        cloud(S, -40 + i * (W + 80) / (n - 1) + r.uniform(-20, 20), y + r.uniform(-14, 14), s * r.uniform(0.8, 1.25), color, a, hi=hi)


def swirl(S, cx, cy, r, color, a=0.6, w=2, turns=1.4, start=0, cw=1):
    pts = []
    N = 40
    for i in range(N + 1):
        t = i / N
        ang = start + cw * t * turns * 2 * math.pi
        rr = r * (1 - 0.8 * t)
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    S.add(f'<path d="{smooth(pts)}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" opacity="{a}"/>')


def wind(S, y, color, a=0.5, w=2, x0=-20, x1=W + 20, amp=14, curl=True, seed=None):
    r = random.Random(seed if seed is not None else S.r.random())
    pts = []
    n = 7
    for i in range(n + 1):
        pts.append((x0 + (x1 - x0) * i / n, y + r.uniform(-amp, amp)))
    S.add(f'<path d="{smooth(pts)}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" opacity="{a}"/>')
    if curl:
        swirl(S, pts[-2][0], pts[-2][1] - 14, 14, color, a, w, 1.1, math.pi / 2, -1)


def rain(S, n, color="#cfe0ff", a=0.35, angle=0.25, y0=0, y1=H):
    out = []
    for _ in range(n):
        x, y = S.r.uniform(-50, W + 50), S.r.uniform(y0, y1)
        L = S.r.uniform(14, 34)
        out.append(f"M{f(x)},{f(y)} l{f(-L * angle)},{f(L)}")
    S.add(f'<path d="{" ".join(out)}" stroke="{color}" stroke-width="1.2" opacity="{a}" stroke-linecap="round"/>')


def lightning(S, x, y, length, color="#fff7d6", w=3, seed=None):
    r = random.Random(seed if seed is not None else S.r.random())
    pts = [(x, y)]
    cx, cy = x, y
    while cy < y + length:
        cx += r.uniform(-22, 22)
        cy += r.uniform(18, 38)
        pts.append((cx, cy))
    d = "M" + " L".join(pt(p) for p in pts)
    glow(S, x, y + length / 2, length * 0.7, color, 0.25)
    S.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="bevel"/>')


# ───────────────────────── objects ─────────────────────────

def petal(cx, cy, w, h, a):
    tip = rot((cx, cy - h), a, (cx, cy))
    c1 = rot((cx - w, cy - h * 0.45), a, (cx, cy))
    c2 = rot((cx - w * 0.5, cy - h * 0.95), a, (cx, cy))
    c3 = rot((cx + w * 0.5, cy - h * 0.95), a, (cx, cy))
    c4 = rot((cx + w, cy - h * 0.45), a, (cx, cy))
    return f"M{f(cx)},{f(cy)} C{pt(c1)} {pt(c2)} {pt(tip)} C{pt(c3)} {pt(c4)} {f(cx)},{f(cy)} Z"


def lotus(S, cx, cy, s=1, c1="#f7b8c6", c2="#e06688", leaf="#3f7d5a", pad=True, a=1, gold=None):
    if pad:
        S.add(f'<ellipse cx="{f(cx)}" cy="{f(cy + 3 * s)}" rx="{f(46 * s)}" ry="{f(9 * s)}" fill="{leaf}" opacity="{a}"/>')
    back = " ".join(petal(cx, cy, 9 * s, 34 * s, math.radians(d)) for d in (-78, -52, 52, 78))
    mid = " ".join(petal(cx, cy, 10 * s, 40 * s, math.radians(d)) for d in (-30, 30))
    front = " ".join(petal(cx, cy, 11 * s, 44 * s, math.radians(d)) for d in (-12, 12, 0))
    g1 = S.lin([(0, c1), (1, c2)])
    S.add(f'<path d="{back}" fill="{c2}" opacity="{a * 0.85}"/>', f'<path d="{mid}" fill="{g1}" opacity="{a}"/>', f'<path d="{front}" fill="{g1}" opacity="{a}"/>')
    if gold:
        S.add(f'<path d="{front}" fill="none" stroke="{gold}" stroke-width="{f(0.8 * s)}" opacity="{a * 0.8}"/>')


def lotus_seat(S, cx, cy, s, c1="#f5c16c", c2="#c77a2a"):
    """A flat lotus throne (pedestal) seen from the side."""
    out = []
    for i in range(-6, 7):
        out.append(petal(cx + i * 9 * s, cy, 6 * s, 16 * s, math.radians(i * 7)))
    S.add(f'<path d="{" ".join(out)}" fill="{S.lin([(0, c1), (1, c2)])}"/>')
    S.add(f'<ellipse cx="{f(cx)}" cy="{f(cy + 2 * s)}" rx="{f(62 * s)}" ry="{f(7 * s)}" fill="{c2}"/>')


def flame(S, x, y, w, h, colors=("#fff6c8", "#ffc03a", "#f0641e"), a=1):
    g = S.lin([(0, colors[0]), (0.45, colors[1]), (1, colors[2])], 0, 1, 0, 0)
    d = f"M{f(x)},{f(y)} C{f(x - w)},{f(y - h * 0.25)} {f(x - w * 0.35)},{f(y - h * 0.6)} {f(x)},{f(y - h)} C{f(x + w * 0.35)},{f(y - h * 0.6)} {f(x + w)},{f(y - h * 0.25)} {f(x)},{f(y)} Z"
    S.add(f'<path d="{d}" fill="{g}" opacity="{a}"/>')


def diya(S, cx, cy, s=1, body="#a8461d", rim="#e3a24a", glow_c="#ffbf55", glow_r=6):
    glow(S, cx, cy - 18 * s, 18 * s * glow_r, glow_c, 0.55)
    flame(S, cx + 6 * s, cy - 6 * s, 6 * s, 26 * s)
    S.add(f'<path d="M{f(cx - 22 * s)},{f(cy - 5 * s)} Q{f(cx)},{f(cy + 16 * s)} {f(cx + 22 * s)},{f(cy - 5 * s)} L{f(cx + 28 * s)},{f(cy - 9 * s)} Q{f(cx)},{f(cy - 1 * s)} {f(cx - 22 * s)},{f(cy - 5 * s)} Z" fill="{body}"/>',
          f'<path d="M{f(cx - 22 * s)},{f(cy - 5 * s)} Q{f(cx)},{f(cy + 1 * s)} {f(cx + 28 * s)},{f(cy - 9 * s)}" fill="none" stroke="{rim}" stroke-width="{f(1.6 * s)}"/>')


def tree(S, x, base, s, color, a=1, kind="round", flowers=None, seed=None):
    r = random.Random(seed if seed is not None else S.r.random())
    trunk = f"M{f(x - 7 * s)},{f(base)} C{f(x - 4 * s)},{f(base - 50 * s)} {f(x - 10 * s)},{f(base - 80 * s)} {f(x - 2 * s)},{f(base - 110 * s)} L{f(x + 4 * s)},{f(base - 110 * s)} C{f(x + 2 * s)},{f(base - 80 * s)} {f(x + 6 * s)},{f(base - 50 * s)} {f(x + 9 * s)},{f(base)} Z"
    out = [f'<path d="{trunk}"/>']
    out.append(f'<path d="M{f(x)},{f(base - 70 * s)} q{f(-30 * s)},{f(-10 * s)} {f(-48 * s)},{f(-36 * s)} M{f(x)},{f(base - 85 * s)} q{f(30 * s)},{f(-6 * s)} {f(46 * s)},{f(-34 * s)}" fill="none" stroke="{color}" stroke-width="{f(5 * s)}" stroke-linecap="round"/>')
    blobs = []
    if kind == "round":
        for _ in range(16):
            blobs.append((x + r.uniform(-70, 70) * s, base - (130 + r.uniform(-34, 34)) * s, r.uniform(20, 34) * s))
    elif kind == "ashoka":
        for _ in range(22):
            blobs.append((x + r.uniform(-62, 62) * s, base - (140 + r.uniform(-46, 46)) * s, r.uniform(14, 24) * s))
    for (bx, by, br) in blobs:
        out.append(f'<circle cx="{f(bx)}" cy="{f(by)}" r="{f(br)}"/>')
    S.add(f'<g fill="{color}" opacity="{a}">{"".join(out)}</g>')
    if kind == "ashoka":
        # drooping leaves
        dl = []
        for _ in range(26):
            bx = x + r.uniform(-80, 80) * s
            by = base - r.uniform(90, 160) * s
            dl.append(f"M{f(bx)},{f(by)} q{f(r.uniform(-3, 3) * s)},{f(14 * s)} {f(r.uniform(-6, 6) * s)},{f(r.uniform(22, 34) * s)}")
        S.add(f'<path d="{" ".join(dl)}" fill="none" stroke="{color}" stroke-width="{f(3 * s)}" stroke-linecap="round" opacity="{a}"/>')
    if flowers:
        fl = []
        for _ in range(30):
            bx = x + r.uniform(-66, 66) * s
            by = base - (140 + r.uniform(-50, 40)) * s
            fl.append(f'<circle cx="{f(bx)}" cy="{f(by)}" r="{f(r.uniform(1.6, 3.4) * s)}"/>')
        S.add(f'<g fill="{flowers}" opacity="{a}">{"".join(fl)}</g>')


def palm(S, x, base, s, color, lean=0.0):
    top = (x + lean * 120 * s, base - 150 * s)
    S.add(f'<path d="M{f(x - 4 * s)},{f(base)} Q{f(x + lean * 40 * s)},{f(base - 80 * s)} {pt(top)} L{f(top[0] + 4 * s)},{f(top[1])} Q{f(x + lean * 40 * s + 6 * s)},{f(base - 80 * s)} {f(x + 5 * s)},{f(base)} Z" fill="{color}"/>')
    fr = []
    for a in (-160, -130, -100, -70, -40, -15, 15):
        ang = math.radians(a)
        L = 60 * s
        end = (top[0] + L * math.cos(ang), top[1] + L * math.sin(ang) + 22 * s)
        ctrl = (top[0] + L * 0.5 * math.cos(ang), top[1] + L * 0.5 * math.sin(ang) - 12 * s)
        fr.append(f"M{pt(top)} Q{pt(ctrl)} {pt(end)}")
    S.add(f'<path d="{" ".join(fr)}" fill="none" stroke="{color}" stroke-width="{f(5 * s)}" stroke-linecap="round"/>')


def tulsi(S, x, base, s, pot="#b45a2a", leaf="#2f6b45"):
    S.add(f'<path d="M{f(x - 16 * s)},{f(base - 30 * s)} L{f(x + 16 * s)},{f(base - 30 * s)} L{f(x + 12 * s)},{f(base)} L{f(x - 12 * s)},{f(base)} Z" fill="{pot}"/>',
          f'<rect x="{f(x - 19 * s)}" y="{f(base - 36 * s)}" width="{f(38 * s)}" height="{f(7 * s)}" fill="{pot}"/>')
    out = []
    for i in range(14):
        a = math.radians(-90 + (i - 6.5) * 13)
        L = (28 + (i % 3) * 8) * s
        sx, sy = x, base - 36 * s
        ex, ey = sx + L * math.cos(a), sy + L * math.sin(a)
        out.append(f'<path d="M{f(sx)},{f(sy)} L{f(ex)},{f(ey)}" stroke="{leaf}" stroke-width="{f(1.6 * s)}"/>')
        out.append(f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="{f(3.4 * s)}" ry="{f(5.5 * s)}" fill="{leaf}" transform="rotate({f(math.degrees(a) + 90)} {f(ex)} {f(ey)})"/>')
    S.add(*out)


def gada(S, hand, ang, s, gold="#e9b649", dark="#8a5a12", L=30, back=7, shaft=None):
    dx, dy = math.cos(ang), math.sin(ang)
    hx, hy = hand
    head = (hx + dx * L * s, hy + dy * L * s)
    tail = (hx - dx * back * s, hy - dy * back * s)
    S.add(f'<path d="M{pt(tail)} L{pt(head)}" stroke="{shaft or dark}" stroke-width="{f(3 * s)}" stroke-linecap="round"/>')
    r = 7.5 * s
    g = S.rad([(0, "#fff2c4"), (0.45, gold), (1, dark)], cx=0.38, cy=0.35, r=0.7)
    S.add(f'<circle cx="{f(head[0])}" cy="{f(head[1])}" r="{f(r)}" fill="{g}"/>')
    # ridges
    px, py = -dy, dx
    for k in (-0.45, 0.0, 0.45):
        c = (head[0] + dx * k * r, head[1] + dy * k * r)
        a1 = (c[0] + px * r * 0.95, c[1] + py * r * 0.95)
        a2 = (c[0] - px * r * 0.95, c[1] - py * r * 0.95)
        S.add(f'<path d="M{pt(a1)} Q{f(c[0] + dx * 2 * s)},{f(c[1] + dy * 2 * s)} {pt(a2)}" fill="none" stroke="{dark}" stroke-width="{f(0.8 * s)}" opacity=".7"/>')
    tip = (head[0] + dx * (r + 3 * s), head[1] + dy * (r + 3 * s))
    S.add(f'<circle cx="{f(tip[0])}" cy="{f(tip[1])}" r="{f(2.4 * s)}" fill="{gold}"/>')
    S.add(f'<circle cx="{f(hx + dx * (L - 9) * s)}" cy="{f(hy + dy * (L - 9) * s)}" r="{f(2.2 * s)}" fill="{gold}"/>')


def banner(S, hand, s, color="#e0601e", gold="#e9b649", pole="#6b3d12", L=70, flip=1):
    hx, hy = hand
    top = (hx, hy - L * s)
    S.add(f'<path d="M{f(hx)},{f(hy + 12 * s)} L{pt(top)}" stroke="{pole}" stroke-width="{f(2.4 * s)}" stroke-linecap="round"/>')
    fx = flip
    d = (f"M{pt(top)} C{f(hx + fx * 18 * s)},{f(top[1] - 6 * s)} {f(hx + fx * 30 * s)},{f(top[1] + 10 * s)} {f(hx + fx * 50 * s)},{f(top[1] + 6 * s)} "
         f"L{f(hx + fx * 34 * s)},{f(top[1] + 16 * s)} L{f(hx + fx * 48 * s)},{f(top[1] + 28 * s)} "
         f"C{f(hx + fx * 30 * s)},{f(top[1] + 30 * s)} {f(hx + fx * 16 * s)},{f(top[1] + 22 * s)} {f(hx)},{f(top[1] + 26 * s)} Z")
    S.add(f'<path d="{d}" fill="{color}"/>', f'<circle cx="{pt(top).split(",")[0]}" cy="{f(top[1] - 2 * s)}" r="{f(2.6 * s)}" fill="{gold}"/>')


def bow(S, hand, s, color="#e9b649", L=40, face=1):
    hx, hy = hand
    t, b = (hx, hy - L * s), (hx, hy + L * s)
    c = (hx + face * 20 * s, hy)
    S.add(f'<path d="M{pt(t)} Q{pt(c)} {pt(b)}" fill="none" stroke="{color}" stroke-width="{f(2.6 * s)}" stroke-linecap="round"/>',
          f'<path d="M{pt(t)} L{pt(b)}" stroke="{color}" stroke-width="{f(0.7 * s)}" opacity=".8"/>')


def ring(S, cx, cy, r, gold="#ffd36b", gem="#e2483d", sparkle=True):
    glow(S, cx, cy, r * 6, "#fff0b0", 0.6)
    S.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="none" stroke="{gold}" stroke-width="{f(r * 0.35)}"/>',
          f'<circle cx="{f(cx)}" cy="{f(cy - r)}" r="{f(r * 0.38)}" fill="{gem}"/>')
    if sparkle:
        s = r * 2.2
        S.add(f'<path d="M{f(cx - s)},{f(cy - r)} L{f(cx + s)},{f(cy - r)} M{f(cx)},{f(cy - r - s)} L{f(cx)},{f(cy - r + s)}" stroke="#fffbe0" stroke-width="1" opacity=".9"/>')


def deva_text(S, x, y, size, text, color, a=1, weight=600, anchor="middle"):
    S.add(f'<text x="{f(x)}" y="{f(y)}" font-family="{DEVA_FONT}" font-size="{f(size)}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}" opacity="{a}">{text}</text>')


def kalash(S, cx, cy, s, body="#d79a3a", dark="#8a5612", leaf="#3e7d4b", coconut="#8a5a2b"):
    g = S.rad([(0, "#ffe4a1"), (0.5, body), (1, dark)], cx=0.38, cy=0.35, r=0.75)
    S.add(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(26 * s)}" ry="{f(23 * s)}" fill="{g}"/>',
          f'<rect x="{f(cx - 10 * s)}" y="{f(cy - 32 * s)}" width="{f(20 * s)}" height="{f(12 * s)}" fill="{body}"/>',
          f'<ellipse cx="{f(cx)}" cy="{f(cy - 32 * s)}" rx="{f(15 * s)}" ry="{f(4 * s)}" fill="{body}"/>')
    lv = []
    for a in (-60, -35, -12, 12, 35, 60):
        ang = math.radians(a - 90)
        e = (cx + 22 * s * math.cos(ang), cy - 34 * s + 22 * s * math.sin(ang) + 10 * s)
        lv.append(f'<path d="M{f(cx)},{f(cy - 34 * s)} Q{f((cx + e[0]) / 2 + 4 * s)},{f((cy - 34 * s + e[1]) / 2 - 6 * s)} {pt(e)} Q{f((cx + e[0]) / 2 - 4 * s)},{f((cy - 34 * s + e[1]) / 2 + 4 * s)} {f(cx)},{f(cy - 34 * s)} Z"/>')
    S.add(f'<g fill="{leaf}">{"".join(lv)}</g>', f'<ellipse cx="{f(cx)}" cy="{f(cy - 44 * s)}" rx="{f(11 * s)}" ry="{f(13 * s)}" fill="{coconut}"/>')
    S.add(f'<path d="M{f(cx - 20 * s)},{f(cy - 6 * s)} Q{f(cx)},{f(cy + 2 * s)} {f(cx + 20 * s)},{f(cy - 6 * s)}" fill="none" stroke="#c0392b" stroke-width="{f(2 * s)}"/>')


def wheel(S, cx, cy, r, color="#f2c35a", a=1, spokes=24, w=2.4):
    out = [f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="none" stroke="{color}" stroke-width="{f(w * 2.2)}"/>',
           f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * 0.86)}" fill="none" stroke="{color}" stroke-width="{f(w * 0.6)}"/>',
           f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * 0.16)}" fill="{color}"/>']
    sp = []
    for i in range(spokes):
        ang = 2 * math.pi * i / spokes
        sp.append(f"M{f(cx + r * 0.16 * math.cos(ang))},{f(cy + r * 0.16 * math.sin(ang))} L{f(cx + r * 0.86 * math.cos(ang))},{f(cy + r * 0.86 * math.sin(ang))}")
    out.append(f'<path d="{" ".join(sp)}" stroke="{color}" stroke-width="{f(w)}"/>')
    S.add(f'<g opacity="{a}">{"".join(out)}</g>')


def mala(S, cx, cy, r, n=108, color="#c98b3a", guru="#e04a2a", br=None, a=1):
    br = br or max(1.6, r * 2 * math.pi / n * 0.42)
    out = []
    for i in range(n):
        ang = -math.pi / 2 + 2 * math.pi * (i + 0.5) / n
        out.append(f'<circle cx="{f(cx + r * math.cos(ang))}" cy="{f(cy + r * math.sin(ang))}" r="{f(br)}"/>')
    S.add(f'<g fill="{color}" opacity="{a}">{"".join(out)}</g>', f'<circle cx="{f(cx)}" cy="{f(cy - r - br * 2.2)}" r="{f(br * 1.6)}" fill="{guru}" opacity="{a}"/>')
    S.add(f'<path d="M{f(cx)},{f(cy - r - br * 1)} l{f(-br * 1.5)},{f(br * 6)} M{f(cx)},{f(cy - r - br)} l{f(br * 1.5)},{f(br * 6)}" stroke="{guru}" stroke-width="{f(br * 0.7)}" opacity="{a}"/>')


def chain_broken(S, x, y, s, color="#c9b38a", a=1, n=4, ang=0.0, gap=True):
    out = []
    for i in range(n):
        cx = x + math.cos(ang) * i * 16 * s
        cy = y + math.sin(ang) * i * 16 * s
        rot_deg = math.degrees(ang) + (90 if i % 2 else 0)
        out.append(f'<rect x="{f(cx - 10 * s)}" y="{f(cy - 5.5 * s)}" width="{f(20 * s)}" height="{f(11 * s)}" rx="{f(5.5 * s)}" fill="none" stroke="{color}" stroke-width="{f(3 * s)}" transform="rotate({f(rot_deg)} {f(cx)} {f(cy)})"/>')
    S.add(f'<g opacity="{a}">{"".join(out)}</g>')


def ghost(S, x, y, s, color="#1c2430", a=0.8, flip=1):
    d = (f"M{f(x)},{f(y)} C{f(x - 16 * s)},{f(y)} {f(x - 20 * s)},{f(y + 26 * s)} {f(x - 16 * s)},{f(y + 46 * s)} "
         f"C{f(x - 12 * s - flip * 30 * s)},{f(y + 66 * s)} {f(x - flip * 50 * s)},{f(y + 62 * s)} {f(x - flip * 70 * s)},{f(y + 80 * s)} "
         f"C{f(x - flip * 36 * s)},{f(y + 78 * s)} {f(x + 6 * s)},{f(y + 66 * s)} {f(x + 14 * s)},{f(y + 44 * s)} "
         f"C{f(x + 20 * s)},{f(y + 24 * s)} {f(x + 16 * s)},{f(y)} {f(x)},{f(y)} Z")
    S.add(f'<path d="{d}" fill="{color}" opacity="{a}"/>',
          f'<g fill="#000" opacity="{a * 0.6}"><ellipse cx="{f(x - 6 * s)}" cy="{f(y + 16 * s)}" rx="{f(2.6 * s)}" ry="{f(4 * s)}"/><ellipse cx="{f(x + 6 * s)}" cy="{f(y + 16 * s)}" rx="{f(2.6 * s)}" ry="{f(4 * s)}"/></g>')


def hut(S, x, base, s, color, roof=None, glow_c=None):
    roof = roof or color
    S.add(f'<rect x="{f(x - 34 * s)}" y="{f(base - 36 * s)}" width="{f(68 * s)}" height="{f(36 * s)}" fill="{color}"/>',
          f'<path d="M{f(x - 46 * s)},{f(base - 32 * s)} Q{f(x)},{f(base - 86 * s)} {f(x + 46 * s)},{f(base - 32 * s)} Z" fill="{roof}"/>')
    if glow_c:
        S.add(f'<path d="M{f(x - 9 * s)},{f(base)} L{f(x - 9 * s)},{f(base - 20 * s)} Q{f(x)},{f(base - 30 * s)} {f(x + 9 * s)},{f(base - 20 * s)} L{f(x + 9 * s)},{f(base)} Z" fill="{glow_c}"/>')
        glow(S, x, base - 12 * s, 50 * s, glow_c, 0.4)


def shikhara(S, x, base, w, h, color, flag=None, a=1):
    """North-Indian temple spire (curvilinear tower) with an amalaka and kalash."""
    d = (f"M{f(x - w / 2)},{f(base)} L{f(x - w / 2)},{f(base - h * 0.25)} "
         f"C{f(x - w * 0.5)},{f(base - h * 0.62)} {f(x - w * 0.22)},{f(base - h * 0.86)} {f(x - w * 0.12)},{f(base - h * 0.9)} "
         f"L{f(x + w * 0.12)},{f(base - h * 0.9)} C{f(x + w * 0.22)},{f(base - h * 0.86)} {f(x + w * 0.5)},{f(base - h * 0.62)} {f(x + w / 2)},{f(base - h * 0.25)} "
         f"L{f(x + w / 2)},{f(base)} Z")
    S.add(f'<g fill="{color}" opacity="{a}"><path d="{d}"/><ellipse cx="{f(x)}" cy="{f(base - h * 0.92)}" rx="{f(w * 0.2)}" ry="{f(h * 0.03 + 2)}"/>'
          f'<path d="M{f(x - w * 0.06)},{f(base - h * 0.94)} L{f(x)},{f(base - h * 1.02)} L{f(x + w * 0.06)},{f(base - h * 0.94)} Z"/></g>')
    if flag:
        tx, ty = x, base - h * 1.02
        S.add(f'<path d="M{f(tx)},{f(ty)} L{f(tx)},{f(ty - 26)}" stroke="{color}" stroke-width="1.6"/>',
              f'<path d="M{f(tx)},{f(ty - 26)} L{f(tx + 22)},{f(ty - 20)} L{f(tx)},{f(ty - 13)} Z" fill="{flag}"/>')


def onion(S, x, base, w, h, color):
    S.add(f'<path d="M{f(x - w / 2)},{f(base)} C{f(x - w * 0.7)},{f(base - h * 0.45)} {f(x - w * 0.05)},{f(base - h * 0.6)} {f(x)},{f(base - h)} C{f(x + w * 0.05)},{f(base - h * 0.6)} {f(x + w * 0.7)},{f(base - h * 0.45)} {f(x + w / 2)},{f(base)} Z" fill="{color}"/>')


def city(S, base, x0, x1, color, win="#ffbf55", scale=1.0, burning=False, seed=None, hmin=60, hmax=190, golden=False):
    r = random.Random(seed if seed is not None else S.r.random())
    x = x0
    tops = []
    shapes = []
    wins = []
    while x < x1:
        w = r.uniform(28, 62) * scale
        h = r.uniform(hmin, hmax) * scale
        shapes.append(f'<rect x="{f(x)}" y="{f(base - h)}" width="{f(w + 1)}" height="{f(h)}"/>')
        kind = r.choice(["onion", "spire", "tier", "onion", "flat"])
        cx = x + w / 2
        if kind == "onion":
            tops.append(("onion", cx, base - h, w * 0.86, w * 0.9))
        elif kind == "spire":
            tops.append(("spire", cx, base - h, w * 0.7, w * 1.7))
        elif kind == "tier":
            shapes.append(f'<rect x="{f(x + w * 0.15)}" y="{f(base - h - w * 0.35)}" width="{f(w * 0.7)}" height="{f(w * 0.36)}"/>')
            tops.append(("onion", cx, base - h - w * 0.35, w * 0.5, w * 0.6))
        # windows
        for wy in range(int(base - h + 14 * scale), int(base - 8), int(max(10, 24 * scale))):
            for wx in (x + w * 0.28, x + w * 0.62):
                if r.random() < 0.55:
                    wins.append(f'<path d="M{f(wx)},{f(wy + 8 * scale)} L{f(wx)},{f(wy + 2 * scale)} Q{f(wx + 3 * scale)},{f(wy - 2 * scale)} {f(wx + 6 * scale)},{f(wy + 2 * scale)} L{f(wx + 6 * scale)},{f(wy + 8 * scale)} Z"/>')
        x += w
    if burning:
        glow(S, (x0 + x1) / 2, base - 120 * scale, (x1 - x0) * 0.75, "#ff7a1a", 0.55)
    S.add(f'<g fill="{color}">{"".join(shapes)}</g>')
    for (k, cx, by, w, h) in tops:
        if k == "onion":
            onion(S, cx, by, w, h, color)
        else:
            S.add(f'<path d="M{f(cx - w / 2)},{f(by)} L{f(cx)},{f(by - h)} L{f(cx + w / 2)},{f(by)} Z" fill="{color}"/>')
    S.add(f'<g fill="{win}" opacity="{0.9 if not golden else 0.6}">{"".join(wins)}</g>')
    if burning:
        for (k, cx, by, w, h) in tops:
            if r.random() < 0.8:
                for j in range(3):
                    flame(S, cx + r.uniform(-w / 2, w / 2), by + r.uniform(0, 30), r.uniform(8, 16) * scale, r.uniform(40, 110) * scale, a=0.92)


def fort(S, base, color, y_wall=None, accent="#ffbf55", seed=None):
    r = random.Random(seed if seed is not None else S.r.random())
    yw = y_wall or base - 150
    out = [f'<rect x="-10" y="{f(yw)}" width="{W + 20}" height="{f(base - yw)}"/>']
    x = -10
    while x < W + 10:
        out.append(f'<rect x="{f(x)}" y="{f(yw - 12)}" width="11" height="13"/>')
        x += 20
    S.add(f'<g fill="{color}">{"".join(out)}</g>')
    # arches along the wall
    arches = []
    for i in range(9):
        ax = 20 + i * 66
        arches.append(f'<path d="M{f(ax)},{f(base - 20)} L{f(ax)},{f(yw + 50)} Q{f(ax + 16)},{f(yw + 26)} {f(ax + 32)},{f(yw + 50)} L{f(ax + 32)},{f(base - 20)} Z"/>')
    S.add(f'<g fill="#000" opacity=".28">{"".join(arches)}</g>')
    # chhatris (domed pavilions)
    for cx in (70, 230, 400, 540):
        h = r.uniform(40, 70)
        S.add(f'<g fill="{color}"><rect x="{f(cx - 22)}" y="{f(yw - 12 - h)}" width="4" height="{f(h)}"/><rect x="{f(cx + 18)}" y="{f(yw - 12 - h)}" width="4" height="{f(h)}"/>'
              f'<rect x="{f(cx - 28)}" y="{f(yw - 18 - h)}" width="56" height="7"/></g>')
        onion(S, cx, yw - 18 - h, 46, 36, color)


def sacred_fire(S, cx, cy, s):
    glow(S, cx, cy - 20 * s, 140 * s, "#ff9d3a", 0.55)
    S.add(f'<path d="M{f(cx - 30 * s)},{f(cy)} L{f(cx + 30 * s)},{f(cy)} L{f(cx + 22 * s)},{f(cy - 14 * s)} L{f(cx - 22 * s)},{f(cy - 14 * s)} Z" fill="#6b3416"/>')
    for (dx, w, h) in ((-12, 9, 40), (10, 9, 46), (0, 12, 64)):
        flame(S, cx + dx * s, cy - 12 * s, w * s, h * s)


def veena(S, x, y, s, color="#e9b649", ang=-0.5):
    a = (x + math.cos(ang) * 40 * s, y + math.sin(ang) * 40 * s)
    b = (x - math.cos(ang) * 40 * s, y - math.sin(ang) * 40 * s)
    S.add(f'<path d="M{pt(a)} L{pt(b)}" stroke="{color}" stroke-width="{f(2.6 * s)}" stroke-linecap="round"/>',
          f'<circle cx="{f(b[0])}" cy="{f(b[1])}" r="{f(8 * s)}" fill="{color}"/>',
          f'<circle cx="{f(x - math.cos(ang) * 8 * s)}" cy="{f(y - math.sin(ang) * 8 * s + 9 * s)}" r="{f(5.5 * s)}" fill="{color}"/>')


def footprints(S, cx, cy, s, color, a=1):
    """A pair of sacred feet (charaṇa) seen from above."""
    out = []
    for side in (-1, 1):
        x = cx + side * 16 * s
        out.append(f'<path d="M{f(x - 8 * s)},{f(cy + 22 * s)} C{f(x - 12 * s)},{f(cy)} {f(x - 10 * s)},{f(cy - 16 * s)} {f(x)},{f(cy - 18 * s)} C{f(x + 10 * s)},{f(cy - 16 * s)} {f(x + 11 * s)},{f(cy)} {f(x + 8 * s)},{f(cy + 22 * s)} C{f(x + 6 * s)},{f(cy + 30 * s)} {f(x - 6 * s)},{f(cy + 30 * s)} {f(x - 8 * s)},{f(cy + 22 * s)} Z"/>')
        toes = [(-7, -22, 3.4), (-2.2, -25, 2.6), (2.2, -25.5, 2.4), (6, -24, 2.2), (9, -21.5, 1.9)]
        for (tx, ty, tr) in toes:
            tx = tx * side
            out.append(f'<circle cx="{f(x + tx * s)}" cy="{f(cy + ty * s)}" r="{f(tr * s)}"/>')
    S.add(f'<g fill="{color}" opacity="{a}">{"".join(out)}</g>')
    # auspicious marks
    S.add(f'<g fill="none" stroke="#c0392b" stroke-width="{f(1.1 * s)}" opacity="{a * 0.9}"><circle cx="{f(cx - 16 * s)}" cy="{f(cy + 6 * s)}" r="{f(4 * s)}"/><circle cx="{f(cx + 16 * s)}" cy="{f(cy + 6 * s)}" r="{f(4 * s)}"/></g>')


def paduka(S, cx, cy, s, color="#9a5a22", knob="#e9b649"):
    for side in (-1, 1):
        x = cx + side * 15 * s
        S.add(f'<rect x="{f(x - 9 * s)}" y="{f(cy - 26 * s)}" width="{f(18 * s)}" height="{f(52 * s)}" rx="{f(9 * s)}" fill="{color}"/>',
              f'<circle cx="{f(x)}" cy="{f(cy - 12 * s)}" r="{f(3.6 * s)}" fill="{knob}"/>')


def palm_leaf(S, x, y, w, h, color="#e9c987", line="#8a6a3a", ang=0):
    S.add(f'<g transform="rotate({f(ang)} {f(x)} {f(y)})"><rect x="{f(x - w / 2)}" y="{f(y - h / 2)}" width="{f(w)}" height="{f(h)}" rx="{f(h / 2)}" fill="{color}"/>'
          + "".join(f'<path d="M{f(x - w * 0.4)},{f(y - h * 0.25 + i * h * 0.25)} L{f(x + w * 0.4)},{f(y - h * 0.25 + i * h * 0.25)}" stroke="{line}" stroke-width=".8" stroke-dasharray="3 2"/>' for i in range(3))
          + f'<circle cx="{f(x - w * 0.25)}" cy="{f(y)}" r="{f(h * 0.08)}" fill="{line}"/></g>')


def steps(S, base, top, color, n=7, a=1, line="#000"):
    S.add(f'<rect x="-10" y="{f(top)}" width="{W + 20}" height="{f(base - top)}" fill="{color}" opacity="{a}"/>')
    out = []
    for i in range(n):
        y = top + (base - top) * i / n
        out.append(f"M-10,{f(y)} L{W + 10},{f(y)}")
    S.add(f'<path d="{" ".join(out)}" stroke="{line}" stroke-width="1.2" opacity=".25"/>')


def boat(S, x, y, s, color, lamp=False):
    S.add(f'<path d="M{f(x - 40 * s)},{f(y - 6 * s)} Q{f(x)},{f(y + 12 * s)} {f(x + 40 * s)},{f(y - 6 * s)} L{f(x + 46 * s)},{f(y - 12 * s)} L{f(x - 46 * s)},{f(y - 12 * s)} Z" fill="{color}"/>')
    if lamp:
        diya(S, x, y - 12 * s, s * 0.4, glow_r=4)


def leaf_diya(S, x, y, s):
    glow(S, x, y - 6 * s, 50 * s, "#ffbf55", 0.5)
    S.add(f'<path d="M{f(x - 16 * s)},{f(y)} Q{f(x)},{f(y + 9 * s)} {f(x + 16 * s)},{f(y)} Q{f(x)},{f(y - 4 * s)} {f(x - 16 * s)},{f(y)} Z" fill="#3e6b3a"/>')
    flame(S, x, y - 2 * s, 3.5 * s, 13 * s)
    S.add(f'<path d="M{f(x - 30 * s)},{f(y + 6 * s)} L{f(x + 30 * s)},{f(y + 6 * s)}" stroke="#ffcf70" stroke-width="{f(1.2 * s)}" opacity=".5"/>')


# ───────────────────────── figures ─────────────────────────
# Joint coordinates in "figure units": feet at y=0, a standing figure is ~100 tall,
# facing right (+x). l = far side, r = near side.

KINDS = {
    "hanuman": dict(head=8, arm=6.6, leg=8.6, ws=11, wp=7.5, tail=True, muzzle=True, crown="mukut", kundal=True, sash=True),
    "baby": dict(head=12.5, arm=6.4, leg=7.6, ws=10.5, wp=9.5, tail=True, muzzle=True, tuft=True),
    "vanara": dict(head=7.6, arm=5.8, leg=7.6, ws=9.6, wp=7, tail=True, muzzle=True),
    "sugriva": dict(head=7.6, arm=6, leg=7.8, ws=10, wp=7, tail=True, muzzle=True, crown="mukut", kundal=True),
    "rama": dict(head=7, arm=5.2, leg=6.6, ws=9, wp=6, crown="kirita", hair=True, halo=True, kundal=True, sash=True),
    "lakshmana": dict(head=7, arm=5.2, leg=6.6, ws=9, wp=6, crown="kirita", hair=True, kundal=True, sash=True),
    "sita": dict(head=6.6, arm=4.6, leg=6, ws=7.6, wp=5.6, veil=True, sari=True, halo=True),
    "sage": dict(head=7, arm=5.4, leg=7, ws=9, wp=7, jata=True, beard=True),
    "poet": dict(head=7, arm=5.4, leg=7, ws=9, wp=7, shikha=True),
    "person": dict(head=7, arm=5.4, leg=7, ws=8.6, wp=6.6, bun=True),
    "child": dict(head=8.4, arm=4.6, leg=5.6, ws=7.2, wp=5.8),
    "rakshasa": dict(head=9, arm=8.4, leg=10, ws=13.5, wp=9, horns=True),
    "shiva": dict(head=7.2, arm=5.8, leg=7.2, ws=10, wp=7, jata=True, moon=True, halo=True),
}

_STAND = dict(h=(1, -90), n=(0, -80), sl=(-8, -77), sr=(8, -77), el=(-11, -62), hl=(-10, -48), er=(13, -63), hr=(12, -49),
              p=(0, -46), kl=(-5, -24), fl=(-7, 0), kr=(6, -24), fr=(10, 0),
              tail=[(-4, -44), (-18, -42), (-25, -58), (-20, -76), (-13, -74)])


def _pose(base, **kw):
    d = dict(base)
    d.update(kw)
    return d


_SEATED = dict(h=(0, -60), n=(0, -50), sl=(-8, -47), sr=(8, -47), el=(-11, -34), hl=(4, -40), er=(12, -35), hr=(4, -40),
               p=(0, -18), seat=True, tail=[(-10, -8), (-26, -6), (-31, -22), (-22, -28)])

POSES = {
    "stand": _STAND,
    "namaste": _pose(_STAND, el=(-9, -63), hl=(6, -69), er=(13, -63), hr=(6, -69)),
    "guard": _pose(_STAND, er=(17, -62), hr=(17, -50), el=(-15, -64), hl=(-7, -50)),
    "heart": _pose(_STAND, el=(-16, -62), hl=(-6, -69), er=(17, -62), hr=(7, -69)),
    "bless": _pose(_STAND, er=(15, -65), hr=(17, -80), el=(-10, -63), hl=(-9, -50)),
    "embrace": _pose(_STAND, el=(10, -67), hl=(20, -70), er=(16, -63), hr=(25, -64), h=(3, -90)),
    "hold_up": _pose(_STAND, er=(14, -88), hr=(14, -104), el=(-12, -62), hl=(-10, -48)),
    "carry": _pose(_STAND, el=(-4, -90), hl=(2, -104), er=(12, -90), hr=(8, -104), h=(1, -90)),
    "kneel": dict(h=(3, -78), n=(2, -68), sl=(-5, -65), sr=(9, -65), el=(-2, -53), hl=(11, -60), er=(16, -55), hr=(11, -60),
                  p=(0, -36), kl=(-4, -3), fl=(-24, -2), kr=(20, -32), fr=(21, 0),
                  tail=[(-3, -34), (-18, -30), (-30, -20), (-40, -26), (-36, -34)]),
    "kneel_offer": dict(h=(4, -78), n=(2, -68), sl=(-5, -65), sr=(9, -65), el=(6, -56), hl=(18, -62), er=(16, -56), hr=(22, -60),
                        p=(0, -36), kl=(-4, -3), fl=(-24, -2), kr=(20, -32), fr=(21, 0),
                        tail=[(-3, -34), (-18, -30), (-30, -20), (-40, -26), (-36, -34)]),
    "fly": dict(h=(32, -58), n=(27, -49), sl=(22, -50), sr=(27, -45), el=(32, -56), hl=(44, -63), er=(36, -46), hr=(48, -50),
                p=(0, -30), kl=(-20, -24), fl=(-40, -20), kr=(-17, -35), fr=(-36, -41),
                tail=[(-4, -30), (-18, -16), (-38, -12), (-52, -22), (-46, -30)]),
    "fly_carry": dict(h=(32, -58), n=(27, -49), sl=(22, -50), sr=(27, -45), el=(16, -42), hl=(8, -34), er=(32, -62), hr=(32, -78),
                      p=(0, -30), kl=(-20, -24), fl=(-40, -20), kr=(-17, -35), fr=(-36, -41),
                      tail=[(-4, -30), (-18, -16), (-38, -12), (-52, -22), (-46, -30)]),
    "fly_back": dict(h=(32, -58), n=(27, -49), sl=(22, -50), sr=(27, -45), el=(34, -54), hl=(38, -60), er=(36, -50), hr=(38, -60),
                     p=(0, -30), kl=(-20, -24), fl=(-40, -20), kr=(-17, -35), fr=(-36, -41),
                     tail=[(-4, -30), (-18, -16), (-38, -12), (-52, -22), (-46, -30)]),
    "leap": dict(h=(19, -76), n=(14, -66), sl=(10, -66), sr=(16, -64), el=(18, -78), hl=(26, -90), er=(26, -74), hr=(36, -84),
                 p=(0, -40), kl=(-10, -26), fl=(-26, -18), kr=(8, -26), fr=(2, -8),
                 tail=[(-3, -40), (-16, -46), (-28, -36), (-36, -44), (-30, -50)]),
    "seated": _SEATED,
    "dhyana": _pose(_SEATED, el=(-11, -30), hl=(-1, -21), er=(11, -30), hr=(1, -21)),
    "write": _pose(_SEATED, el=(-2, -32), hl=(12, -36), er=(13, -34), hr=(16, -30)),
    "play": _pose(_SEATED, el=(-9, -34), hl=(6, -44), er=(14, -36), hr=(12, -52)),
    "teach": _pose(_SEATED, er=(14, -40), hr=(16, -54), el=(-11, -32), hl=(0, -22)),
    "sit_bless": dict(h=(0, -80), n=(0, -70), sl=(-7, -67), sr=(8, -67), el=(-8, -54), hl=(6, -44), er=(14, -56), hr=(16, -70),
                      p=(0, -38), kl=(15, -36), fl=(15, 0), kr=(17, -37), fr=(19, -1)),
    "giant": dict(h=(4, -91), n=(2, -81), sl=(-9, -78), sr=(10, -78), el=(-20, -68), hl=(-24, -80), er=(19, -90), hr=(17, -104),
                  p=(0, -48), kl=(-12, -26), fl=(-21, 0), kr=(13, -26), fr=(23, 0),
                  tail=[(-4, -46), (-22, -50), (-32, -70), (-22, -90), (-14, -86)]),
    "roar": dict(h=(7, -89), n=(2, -81), sl=(-9, -78), sr=(10, -78), el=(-18, -64), hl=(-22, -50), er=(20, -64), hr=(24, -50),
                 p=(0, -48), kl=(-12, -26), fl=(-21, 0), kr=(13, -26), fr=(23, 0),
                 tail=[(-4, -46), (-22, -50), (-32, -70), (-22, -90), (-14, -86)]),
    "uproot": dict(h=(10, -84), n=(6, -75), sl=(-2, -73), sr=(12, -72), el=(16, -84), hl=(24, -94), er=(22, -82), hr=(28, -92),
                   p=(0, -44), kl=(-14, -24), fl=(-24, 0), kr=(12, -26), fr=(18, 0),
                   tail=[(-4, -42), (-22, -42), (-32, -60), (-24, -78), (-17, -74)]),
    "run": dict(h=(6, -86), n=(4, -76), sl=(-4, -73), sr=(10, -73), el=(-14, -66), hl=(-20, -76), er=(18, -80), hr=(22, -92),
                p=(0, -44), kl=(10, -26), fl=(4, -2), kr=(-10, -30), fr=(-22, -14),
                tail=[(-4, -42), (-20, -48), (-30, -62)]),
    "carry_stone": _pose(_STAND, el=(-6, -88), hl=(0, -100), er=(10, -88), hr=(6, -100), kl=(-2, -24), fl=(-12, 0), kr=(10, -22), fr=(16, -2)),
}


def figure(S, pose, x, y, s=1.0, face=1, kind="hanuman", fill="#1b0f12", gold="#ebb84c", accent="#d9531e", sash=None,
           halo=None, heart=None, glowc=None, tail_fire=False):
    K = KINDS[kind]
    J = POSES[pose]

    def m(p):
        return (x + s * face * p[0], y + s * p[1])

    def add(p, q):
        return (p[0] + q[0], p[1] + q[1])

    h, n, p = J["h"], J["n"], J["p"]
    hr_ = K["head"]
    ux, uy = h[0] - n[0], h[1] - n[1]
    L = math.hypot(ux, uy) or 1
    ux, uy = ux / L, uy / L                    # head "up" (local)
    rx, ry = -uy, ux                           # head "right" (toward the face)

    def hp(a, b):                              # point in head-local frame
        return m((h[0] + rx * a * hr_ + ux * b * hr_, h[1] + ry * a * hr_ + uy * b * hr_))

    out = []
    stroke = f'fill="none" stroke="{fill}" stroke-linecap="round" stroke-linejoin="round"'

    if glowc:
        c = m(((h[0] + p[0]) / 2, (h[1] + p[1]) / 2))
        glow(S, c[0], c[1], 110 * s, glowc, 0.55)
    halo_c = halo if halo is not None else (gold if K.get("halo") else None)
    if halo_c:
        c = m(h)
        S.add(f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(hr_ * 2.3 * s)}" fill="{S.rad([(0, halo_c, 0.55), (1, halo_c, 0.05)])}"/>',
              f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(hr_ * 2.3 * s)}" fill="none" stroke="{halo_c}" stroke-width="{f(1.2 * s)}" opacity=".9"/>')

    # tail (behind everything)
    if K.get("tail") and "tail" in J:
        tp = [m(q) for q in J["tail"]]
        tw = (3.3 if kind != "baby" else 3.0) * s
        out.append(f'<path d="{smooth(tp)}" {stroke} stroke-width="{f(tw)}"/>')
        end = tp[-1]
        out.append(f'<circle cx="{f(end[0])}" cy="{f(end[1])}" r="{f(tw * 0.75)}" fill="{fill}"/>')
        if tail_fire:
            for i, q in enumerate(tp[2:]):
                flame(S, q[0], q[1] + 2 * s, 3.2 * s, (10 + i * 3) * s, a=0.95)

    # veil / hair behind the head
    if K.get("veil"):
        out.append(f'<path d="{smooth([hp(0.2, 1.15), hp(-0.9, 0.9), hp(-1.35, -0.4), m(add(n, (-K["ws"] * 1.1, 8))), m(add(n, (-K["ws"] * 1.2, 26)))])} L{pt(m(add(n, (0, 10))))} Z" fill="{fill}"/>')
    if K.get("hair"):
        out.append(f'<path d="M{pt(hp(-0.2, 0.9))} Q{pt(hp(-1.6, 0.2))} {pt(m(add(n, (-K["ws"] * 0.9, 12))))} L{pt(m(add(n, (-2, 4))))} Z" fill="{fill}"/>')

    # far limbs
    if not J.get("seat"):
        out.append(f'<path d="M{pt(m(p))} L{pt(m(J["kl"]))} L{pt(m(J["fl"]))}" {stroke} stroke-width="{f(K["leg"] * s)}"/>')
    out.append(f'<path d="M{pt(m(J["sl"]))} L{pt(m(J["el"]))} L{pt(m(J["hl"]))}" {stroke} stroke-width="{f(K["arm"] * s)}"/>')

    # torso
    ax, ay = p[0] - n[0], p[1] - n[1]
    La = math.hypot(ax, ay) or 1
    px_, py_ = -ay / La, ax / La
    ws, wp = K["ws"], K["wp"]
    def tp(t, w):
        return m((n[0] + ax * t + px_ * w, n[1] + ay * t + py_ * w))
    # tapered torso: rounded shoulders, broad chest, narrow waist
    torso = [tp(-0.06, ws * 0.55), tp(0.04, ws * 1.0), tp(0.3, ws * 1.02), tp(0.7, wp * 1.0), tp(1.0, wp * 1.05),
             tp(1.0, -wp * 1.05), tp(0.7, -wp * 1.0), tp(0.3, -ws * 1.02), tp(0.04, -ws * 1.0), tp(-0.06, -ws * 0.55)]
    out.append(f'<path d="{smooth(torso, closed=True)}" fill="{fill}"/>')
    hip = m(p)
    out.append(f'<circle cx="{f(hip[0])}" cy="{f(hip[1])}" r="{f((wp + 1.5) * s)}" fill="{fill}"/>')

    if K.get("sari"):
        fl_, fr_ = J.get("fl", (p[0] - 6, 0)), J.get("fr", (p[0] + 6, 0))
        if J.get("seat"):
            out.append(f'<ellipse cx="{f(hip[0])}" cy="{f(hip[1] + 6 * s)}" rx="{f(22 * s)}" ry="{f(10 * s)}" fill="{fill}"/>')
        else:
            out.append(f'<path d="M{pt(m(add(p, (-wp - 1, -4))))} L{pt(m(add(p, (wp + 1, -4))))} Q{pt(m(add(fr_, (6, -14))))} {pt(m(add(fr_, (10, 0))))} L{pt(m(add(fl_, (-10, 0))))} Q{pt(m(add(fl_, (-4, -14))))} {pt(m(add(p, (-wp - 1, -4))))} Z" fill="{fill}"/>')

    # near limbs
    if J.get("seat"):
        out.append(f'<ellipse cx="{f(hip[0])}" cy="{f(hip[1] + 5 * s)}" rx="{f(19 * s)}" ry="{f(7.5 * s)}" fill="{fill}"/>')
        for side in (-1, 1):
            kx = m(add(p, (side * 15, 6)))
            out.append(f'<circle cx="{f(kx[0])}" cy="{f(kx[1])}" r="{f(6 * s)}" fill="{fill}"/>')
    else:
        out.append(f'<path d="M{pt(m(p))} L{pt(m(J["kr"]))} L{pt(m(J["fr"]))}" {stroke} stroke-width="{f(K["leg"] * s)}"/>')
        for fk in ("fl", "fr"):
            q = m(J[fk])
            out.append(f'<ellipse cx="{f(q[0] + face * 3 * s)}" cy="{f(q[1] - 1 * s)}" rx="{f(K["leg"] * 0.85 * s)}" ry="{f(K["leg"] * 0.45 * s)}" fill="{fill}"/>')
    out.append(f'<path d="M{pt(m(J["sr"]))} L{pt(m(J["er"]))} L{pt(m(J["hr"]))}" {stroke} stroke-width="{f(K["arm"] * s)}"/>')
    for hk in ("hl", "hr"):
        q = m(J[hk])
        out.append(f'<circle cx="{f(q[0])}" cy="{f(q[1])}" r="{f(K["arm"] * 0.62 * s)}" fill="{fill}"/>')

    # neck + head
    out.append(f'<path d="M{pt(m(n))} L{pt(m(h))}" {stroke} stroke-width="{f(hr_ * 1.0 * s)}"/>')
    hc = m(h)
    out.append(f'<circle cx="{f(hc[0])}" cy="{f(hc[1])}" r="{f(hr_ * s)}" fill="{fill}"/>')
    if K.get("muzzle"):
        mc = hp(0.72, -0.28)
        out.append(f'<ellipse cx="{f(mc[0])}" cy="{f(mc[1])}" rx="{f(hr_ * 0.62 * s)}" ry="{f(hr_ * 0.55 * s)}" fill="{fill}"/>')
        ear = hp(-0.45, 0.25)
        out.append(f'<circle cx="{f(ear[0])}" cy="{f(ear[1])}" r="{f(hr_ * 0.34 * s)}" fill="{fill}"/>')
    if K.get("tuft"):
        out.append(f'<path d="M{pt(hp(-0.3, 0.9))} Q{pt(hp(0.1, 1.7))} {pt(hp(0.5, 1.15))}" {stroke} stroke-width="{f(2.4 * s)}"/>')
    if K.get("horns"):
        for side in (-0.55, 0.45):
            b = hp(side, 0.75)
            t = hp(side * 1.7, 1.75)
            out.append(f'<path d="M{pt(hp(side - 0.25, 0.7))} Q{pt(hp(side * 1.6, 1.0))} {pt(t)} Q{pt(hp(side * 1.0, 1.1))} {pt(hp(side + 0.25, 0.8))} Z" fill="{fill}"/>')
    if K.get("jata"):
        j = hp(-0.15, 1.05)
        out.append(f'<ellipse cx="{f(j[0])}" cy="{f(j[1])}" rx="{f(hr_ * 0.6 * s)}" ry="{f(hr_ * 0.75 * s)}" fill="{fill}"/>')
    if K.get("bun"):
        j = hp(-0.75, 0.55)
        out.append(f'<circle cx="{f(j[0])}" cy="{f(j[1])}" r="{f(hr_ * 0.5 * s)}" fill="{fill}"/>')
    if K.get("shikha"):
        out.append(f'<path d="M{pt(hp(-0.5, 0.85))} Q{pt(hp(-1.3, 1.0))} {pt(hp(-1.2, 0.2))}" {stroke} stroke-width="{f(1.6 * s)}"/>')
    if K.get("beard"):
        out.append(f'<path d="M{pt(hp(-0.2, -0.45))} L{pt(hp(0.85, -0.35))} L{pt(hp(0.25, -1.9))} Z" fill="{fill}"/>')
    S.add(*out)

    # ornaments (drawn over the silhouette)
    crown = K.get("crown")
    if crown == "mukut":
        pts = [hp(-0.82, 0.5), hp(-0.7, 1.15), hp(-0.42, 1.0), hp(-0.2, 1.65), hp(0.05, 1.25), hp(0.25, 2.1), hp(0.45, 1.25), hp(0.66, 1.55), hp(0.85, 0.5)]
        S.add(f'<path d="M{" L".join(pt(q) for q in pts)} Z" fill="{gold}"/>')
        g = hp(0.05, 0.75)
        S.add(f'<circle cx="{f(g[0])}" cy="{f(g[1])}" r="{f(hr_ * 0.2 * s)}" fill="{accent}"/>')
    elif crown == "kirita":
        pts = [hp(-0.75, 0.55), hp(-0.62, 1.9), hp(-0.25, 2.35), hp(0, 2.85), hp(0.25, 2.35), hp(0.62, 1.9), hp(0.75, 0.55)]
        S.add(f'<path d="M{" L".join(pt(q) for q in pts)} Z" fill="{gold}"/>')
        g = hp(0, 1.4)
        S.add(f'<circle cx="{f(g[0])}" cy="{f(g[1])}" r="{f(hr_ * 0.22 * s)}" fill="{accent}"/>')
    if K.get("moon"):
        c = hp(0.35, 1.25)
        S.add(f'<path d="M{f(c[0] - 4 * s)},{f(c[1])} a{f(4 * s)},{f(4 * s)} 0 0 0 {f(8 * s)},0 a{f(3.2 * s)},{f(2.6 * s)} 0 0 1 {f(-8 * s)},0 Z" fill="#fff4c8"/>')
    if K.get("kundal"):
        k = hp(-0.35, -0.55)
        S.add(f'<circle cx="{f(k[0])}" cy="{f(k[1])}" r="{f(hr_ * 0.3 * s)}" fill="none" stroke="{gold}" stroke-width="{f(1.3 * s)}"/>')
    if (sash if sash is not None else K.get("sash")) and accent:
        a1 = m(J["sl"])
        a2 = m(J["p"])
        mid = m(((J["sl"][0] + J["p"][0]) / 2 + 4, (J["sl"][1] + J["p"][1]) / 2))
        S.add(f'<path d="M{pt(a1)} Q{pt(mid)} {pt(m(add(J["p"], (wp * 0.8, 2))))}" fill="none" stroke="{gold}" stroke-width="{f(1.1 * s)}" opacity=".9"/>')
        # waist sash
        w1 = m(add(J["p"], (-wp - 1, -2)))
        w2 = m(add(J["p"], (wp + 1, -2)))
        S.add(f'<path d="M{pt(w1)} L{pt(w2)}" stroke="{accent}" stroke-width="{f(3.2 * s)}" stroke-linecap="round"/>')
    if heart:
        c = m(((n[0] + p[0]) / 2, (n[1] + p[1]) / 2 - 4))
        glow(S, c[0], c[1], 40 * s, "#fff2c0", 0.9)
        S.add(f'<ellipse cx="{f(c[0])}" cy="{f(c[1])}" rx="{f(8.5 * s)}" ry="{f(12 * s)}" fill="{S.rad([(0, "#fffbe8"), (0.7, "#ffe08a"), (1, "#f0a43c")])}"/>')
        figure(S, "bless", c[0] - 3.2 * s, c[1] + 10 * s, s * 0.17, 1, "rama", fill="#2a4a8a", gold="#c7871f", halo="#e0a53a", sash=False)
        figure(S, "stand", c[0] + 3.6 * s, c[1] + 10 * s, s * 0.155, -1, "sita", fill="#9b2a3a", halo="#e0a53a")
    return {k: m(v) for k, v in J.items() if isinstance(v, tuple)}
