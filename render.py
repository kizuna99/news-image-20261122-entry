"""The World in One Day — broadsheet poster renderer (Pillow, deterministic).

Draws a one-page editorial broadsheet for one day's world news at 2048x2048
and downsamples to 1024x1024: giant dated masthead, the day in UTC, a stat
band, region tabs, three illustrated leads, ten story cards, a dot world map
with pins, an "also on" column, a date-check box and a certainty footer.
All artwork is original drawn geometry; no photographs. Day-specific content
lives in data.py beside this file (DAY dict).
Requires Pillow + Liberation fonts (Noto Serif Display if present).
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import data as D

SS = 2  # supersample factor
W = 1024

FONT_DIRS = [
    os.environ.get("LIBERATION_FONTS", "/usr/share/fonts/truetype/liberation"),
    "/usr/share/fonts/truetype/noto",
    "/usr/share/fonts/truetype/dejavu",
]
SERIF = "LiberationSerif-Regular.ttf"
SERIF_B = "LiberationSerif-Bold.ttf"
SERIF_I = "LiberationSerif-Italic.ttf"
SERIF_BI = "LiberationSerif-BoldItalic.ttf"
DISPLAY = "NotoSerifDisplay-Black.ttf"
SANS = "LiberationSans-Regular.ttf"
SANS_B = "LiberationSans-Bold.ttf"
SANS_I = "LiberationSans-Italic.ttf"

PAPER = (246, 241, 229)
PAPER_D = (238, 230, 212)
INK = (20, 22, 26)
NAVY = (18, 34, 56)
NAVY_TXT = (233, 236, 240)
RED = (168, 44, 36)
RED_D = (140, 32, 26)
GOLD = (168, 124, 38)
GREY = (96, 96, 92)
RULE = (30, 30, 30)
SEA = (198, 216, 222)
LAND = (232, 220, 188)
LAND_E = (150, 138, 104)


def font(name, size):
    for d in FONT_DIRS:
        p = Path(d) / name
        if p.exists():
            return ImageFont.truetype(str(p), int(size * SS))
    return ImageFont.truetype(str(Path(FONT_DIRS[-1]) / "DejaVuSerif.ttf"),
                              int(size * SS))


def X(v):
    return v * SS


def text_l(d, x, y, s, fnt, fill=INK, spacing=0):
    if spacing:
        cx = X(x)
        for ch in s:
            d.text((cx, X(y)), ch, font=fnt, fill=fill)
            cx += d.textlength(ch, font=fnt) + spacing * SS
        return (cx - X(x)) / SS
    d.text((X(x), X(y)), s, font=fnt, fill=fill)
    return d.textlength(s, font=fnt) / SS


def text_c(d, cx, y, s, fnt, fill=INK, spacing=0):
    if spacing:
        w = sum(d.textlength(ch, font=fnt) for ch in s) + spacing * SS * (len(s) - 1)
        x0 = X(cx) - w / 2
        for ch in s:
            d.text((x0, X(y)), ch, font=fnt, fill=fill)
            x0 += d.textlength(ch, font=fnt) + spacing * SS
        return
    w = d.textlength(s, font=fnt)
    d.text((X(cx) - w / 2, X(y)), s, font=fnt, fill=fill)


def text_r(d, xr, y, s, fnt, fill=INK):
    w = d.textlength(s, font=fnt)
    d.text((X(xr) - w, X(y)), s, font=fnt, fill=fill)


def wrap(d, s, fnt, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=fnt) <= X(maxw) or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, s, fnt, maxw, leading, fill=INK, max_lines=None):
    lines = wrap(d, s, fnt, maxw)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((X(x), X(y)), ln, font=fnt, fill=fill)
        y += leading
    return y


def hline(d, x0, x1, y, fill=RULE, wdt=1.2):
    d.line([X(x0), X(y), X(x1), X(y)], fill=fill, width=max(1, int(wdt * SS)))


def rect(d, x0, y0, x1, y1, fill=None, outline=None, wdt=1):
    d.rectangle([X(x0), X(y0), X(x1), X(y1)], fill=fill, outline=outline,
                width=max(1, int(wdt * SS)))


def badge(d, xr, y, label, fill):
    """Small certainty badge, right-aligned at (xr, y)."""
    f = font(SANS_B, 7.5)
    w = d.textlength(label, font=f) / SS + 9
    rect(d, xr - w, y, xr, y + 11, fill=fill)
    text_c(d, xr - w / 2, y + 1.6, label, f, (250, 248, 240))


# ---------------------------------------------------------------- frame ---

def masthead(d):
    rect(d, 0, 0, W, 27, fill=NAVY)
    text_l(d, 14, 7.5, "THE WORLD IN ONE DAY", font(SANS_B, 10), NAVY_TXT,
           spacing=1.6)
    text_c(d, 512, 7.5, D.DAY["dayline"], font(SANS_B, 10), NAVY_TXT,
           spacing=1.6)
    text_r(d, 1010, 7.5, "ALL TIMES UTC · RANKED BY CONSEQUENCE",
           font(SANS_B, 10), NAVY_TXT)
    size = 79
    while size > 40 and d.textlength(D.DAY["date_long"],
                                     font=font(DISPLAY, size)) / SS > 984:
        size -= 2
    text_c(d, 512, 34, D.DAY["date_long"], font(DISPLAY, size), INK)
    text_c(d, 512, 114, D.DAY["ticker"], font(SERIF_I, 14.5), RED_D)
    hline(d, 14, 1010, 130, INK, 2.2)
    text_c(d, 512, 136, D.DAY["count_line"], font(SANS_B, 12), INK,
           spacing=1.2)
    hline(d, 14, 1010, 156, INK, 1)


def stat_band(d):
    y0, y1 = 164, 224
    stats = D.DAY["stats"]
    x = 14.0
    wdt = (1010 - 14) / len(stats)
    for i, (num, cap, src) in enumerate(stats):
        cx = x + wdt / 2
        text_c(d, cx, y0 + 1, num, font(SERIF_B, 28), INK)
        for j, ln in enumerate(wrap(d, cap, font(SANS, 8.4), wdt - 16)[:2]):
            text_c(d, cx, y0 + 34 + j * 10.5, ln, font(SANS, 8.4),
                   (52, 52, 50))
        if i:
            d.line([X(x), X(y0 + 4), X(x), X(y1 - 6)], fill=(178, 168, 146),
                   width=SS)
        x += wdt
    hline(d, 14, 1010, y1, INK, 1)


REGION_COLORS = {
    "Europe": (32, 80, 140), "Middle East": (160, 61, 45),
    "Americas": (46, 110, 70), "Africa": (176, 128, 40),
    "South Asia": (122, 74, 140), "East Asia": (179, 84, 30),
    "South-East Asia": (31, 111, 107), "Oceania": (74, 111, 165),
    "Global": (84, 84, 84),
}


TAB_SHORT = {"South Asia": "S ASIA", "East Asia": "E ASIA",
             "South-East Asia": "SE ASIA"}


def region_tabs(d):
    y0, y1 = 232, 254
    tabs = D.DAY["regions"]
    total = sum(n for _, n in tabs)
    widths = [max(56.0, (1010 - 14) * n / total) for _, n in tabs]
    scale = (1010 - 14) / sum(widths)
    widths = [w_ * scale for w_ in widths]
    x = 14.0
    for (name, n), wdt in zip(tabs, widths):
        rect(d, x, y0, x + wdt - 1.5, y1, fill=REGION_COLORS[name])
        label = "%s %d" % (TAB_SHORT.get(name, name).upper(), n)
        text_c(d, x + wdt / 2, y0 + 6.5, label, font(SANS_B, 9.5),
               (250, 248, 240))
        x += wdt


def timeline(d):
    y0 = 264
    text_l(d, 14, y0, "THE DAY IN UTC", font(SANS_B, 9.5), INK)
    x0, x1, yy = 118, 1000, y0 + 5
    hline(d, x0, x1, yy, (120, 116, 104), 1.4)
    for t, label in D.DAY["timeline"]:
        fx = x0 + (x1 - x0) * t
        d.ellipse([X(fx - 2.6), X(yy - 2.6), X(fx + 2.6), X(yy + 2.6)],
                  fill=RED)
        text_c(d, fx, yy + 7, label, font(SANS_B, 8.4), INK)
    return y0 + 30


# ------------------------------------------------------------- painters ---

def _poly(d, pts, fill, outline=None, wdt=1):
    d.polygon([(X(a), X(b)) for a, b in pts], fill=fill, outline=outline,
              width=max(1, int(wdt * SS)))


def _flame(d, cx, cy, s, core=(255, 190, 60), mid=(240, 110, 30)):
    _poly(d, [(cx, cy - 1.5 * s), (cx + 0.62 * s, cy + 0.4 * s),
              (cx + 0.3 * s, cy + s), (cx - 0.3 * s, cy + s),
              (cx - 0.62 * s, cy + 0.4 * s)], mid)
    _poly(d, [(cx, cy - 0.7 * s), (cx + 0.34 * s, cy + 0.5 * s),
              (cx - 0.34 * s, cy + 0.5 * s)], core)


def _dashed(d, pts, fill, dash=5, gap=4, wdt=1.6):
    import math
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dist = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(dist / (dash + gap)))
        for i in range(n):
            t0 = i / n
            t1 = min(1.0, t0 + dash / (dist * n / (dash + gap)) / n * n / n
                     + (dash / dist))
            d.line([X(x0 + (x1 - x0) * t0), X(y0 + (y1 - y0) * t0),
                    X(x0 + (x1 - x0) * min(t1, 1.0)),
                    X(y0 + (y1 - y0) * min(t1, 1.0))],
                   fill=fill, width=max(1, int(wdt * SS)))


def paint_gulf(d, x, y, w, h):
    """Stylised Strait of Hormuz map: Iran NE, Arabia SW, Bahrain ablaze."""
    rect(d, x, y, x + w, y + h, fill=SEA)
    ux, uy = w / 100.0, h / 100.0

    def P(a, b):
        return (x + a * ux, y + b * uy)
    iran = [P(50, 0), P(100, 0), P(100, 40), P(90, 46), P(80, 38), P(70, 26),
            P(60, 16), P(53, 6)]
    _poly(d, iran, LAND, LAND_E, 1)
    arabia = [P(0, 30), P(16, 26), P(30, 30), P(40, 40), P(46, 52),
              P(52, 66), P(56, 82), P(50, 100), P(0, 100)]
    _poly(d, arabia, LAND, LAND_E, 1)
    musandam = [P(76, 100), P(82, 74), P(78, 62), P(88, 58), P(100, 64),
                P(100, 100)]
    _poly(d, musandam, LAND, LAND_E, 1)
    qatar = [P(43.5, 47), P(47.5, 45), P(48.5, 52), P(46, 58), P(43.8, 53)]
    _poly(d, qatar, LAND, LAND_E, 1)
    f = font(SANS_B, 8.5)
    text_l(d, *P(66, 8), "I R A N", f, (110, 96, 66))
    text_l(d, *P(6, 84), "SAUDI ARABIA", f, (110, 96, 66))
    text_l(d, *P(30, 40), "THE GULF", font(SERIF_I, 9), (70, 96, 110))
    text_l(d, *P(86, 84), "OMAN", f, (110, 96, 66))
    text_l(d, *P(36.5, 60), "QATAR", font(SANS_B, 6.5), (110, 96, 66))
    text_l(d, *P(85, 44), "STRAIT OF", font(SANS_B, 7), (52, 84, 100))
    text_l(d, *P(85, 51), "HORMUZ", font(SANS_B, 7), (52, 84, 100))
    # Bahrain island + fire
    bx, by = P(47.5, 44)
    d.ellipse([X(bx - 2.2), X(by - 2.2), X(bx + 2.2), X(by + 2.2)],
              fill=(250, 246, 230), outline=LAND_E)
    _flame(d, bx, by - 3, 6.5)
    text_r(d, bx - 5, by + 8, "BAHRAIN", font(SANS_B, 8), RED_D)
    # Khasab tanker point at the strait
    kx, ky = P(83, 60)
    d.ellipse([X(kx - 2), X(ky - 2), X(kx + 2), X(ky + 2)], fill=RED)
    text_l(d, kx + 4, ky - 3, "Khasab", font(SANS_B, 7.5), RED_D)
    # strike arcs from Iran coast to Bahrain
    _dashed(d, [P(63, 20), P(56, 30), (bx, by)], RED_D)
    _dashed(d, [P(70, 28), P(58, 36), (bx, by)], RED_D)


def paint_ship(d, x, y, w, h):
    """Sparta II ablaze in the Gulf of Finland, with a locator inset."""
    rect(d, x, y, x + w, y + h, fill=(172, 198, 208))
    rect(d, x, y + h * 0.66, x + w, y + h, fill=(70, 106, 128))
    ux, uy = w / 100.0, h / 100.0

    def P(a, b):
        return (x + a * ux, y + b * uy)
    # drones
    for dx, dy in ((16, 16), (30, 9)):
        cx, cy = P(dx, dy)
        _poly(d, [(cx - 5, cy - 2.4), (cx + 5, cy - 2.4), (cx + 1.8, cy),
                  (cx + 5, cy + 2.4), (cx - 5, cy + 2.4), (cx - 1.8, cy)],
              (38, 42, 48))
        _dashed(d, [(cx + 3, cy + 3), P(46, 52)], (90, 60, 40), dash=3.4,
                gap=3, wdt=1.1)
    # smoke + fire amidships
    for i, (sx, sy, r) in enumerate(((47, 34, 7), (53, 28, 9), (60, 22, 11),
                                     (68, 17, 13))):
        cx, cy = P(sx, sy)
        d.ellipse([X(cx - r), X(cy - r * 0.72), X(cx + r), X(cy + r * 0.72)],
                  fill=(104, 106, 108) if i % 2 else (128, 128, 126))
    fx, fy = P(46, 55)
    _flame(d, fx, fy, 12)
    _flame(d, fx + 13, fy + 2, 8)
    # hull + containers + superstructure
    hx0, hy = P(10, 62)
    hx1, _ = P(84, 62)
    _poly(d, [(hx0, hy), (hx1, hy), (hx1 - 8, hy + 13), (hx0 + 5, hy + 13)],
          (34, 38, 44))
    rect(d, hx0 + 2, hy + 11.5, hx1 - 6, hy + 14.5, fill=(150, 52, 40))
    cols = [(176, 84, 44), (52, 96, 140), (64, 128, 88), (150, 120, 52),
            (120, 70, 120)]
    for i in range(5):
        cx = hx0 + 8 + i * 11.5
        rect(d, cx, hy - 9, cx + 10.4, hy - 0.5, fill=cols[i])
        if i % 2 == 0:
            rect(d, cx, hy - 17, cx + 10.4, hy - 9.5, fill=cols[(i + 2) % 5])
    sx0 = hx1 - 17
    rect(d, sx0, hy - 24, sx0 + 11, hy - 0.5, fill=(226, 224, 216),
         outline=(90, 90, 88))
    for r_ in range(3):
        for c_ in range(2):
            rect(d, sx0 + 2 + c_ * 4.4, hy - 21 + r_ * 6.4,
                 sx0 + 4.6 + c_ * 4.4, hy - 18 + r_ * 6.4, fill=(70, 90, 110))
    text_c(d, (hx0 + hx1) / 2, hy + 4.5, "S P A R T A  II",
           font(SANS_B, 8.5), (232, 234, 236))
    # locator inset
    ix, iy, iw, ih = x + w - 86, y + 7, 79, 56
    rect(d, ix, iy, ix + iw, iy + ih, fill=(244, 240, 228),
         outline=(90, 90, 88))
    _poly(d, [(ix + 8, iy + 6), (ix + 30, iy + 4), (ix + 34, iy + 20),
              (ix + 20, iy + 26), (ix + 8, iy + 18)], LAND, LAND_E, 0.8)
    text_l(d, ix + 9, iy + 28, "FINLAND", font(SANS_B, 6), (110, 96, 66))
    _poly(d, [(ix + 22, iy + 30), (ix + 44, iy + 28), (ix + 46, iy + 40),
              (ix + 26, iy + 42)], LAND, LAND_E, 0.8)
    text_l(d, ix + 24, iy + 43, "ESTONIA", font(SANS_B, 6), (110, 96, 66))
    text_l(d, ix + 52, iy + 10, "RUSSIA", font(SANS_B, 6), (110, 96, 66))
    dx_, dy_ = ix + 33, iy + 27
    d.ellipse([X(dx_ - 2.4), X(dy_ - 2.4), X(dx_ + 2.4), X(dy_ + 2.4)],
              fill=RED)


def paint_cop(d, x, y, w, h):
    """COP31: summit sign, the draft text with fossil fuels struck, a clock."""
    rect(d, x, y, x + w, y + h, fill=(226, 232, 220))
    ux = w / 100.0

    def P(a, b):
        return (x + a * ux, y + b * h / 100.0)
    gx, gy = P(4, 12)
    rect(d, gx, gy, gx + 30 * ux, gy + 52, fill=(24, 92, 62))
    text_c(d, gx + 15 * ux, gy + 9, "COP31", font(SERIF_B, 17),
           (240, 246, 238))
    text_c(d, gx + 15 * ux, gy + 32, "ANTALYA · UN", font(SANS_B, 6.5),
           (208, 226, 210))
    text_c(d, gx + 15 * ux, gy + 41, "CLIMATE SUMMIT", font(SANS_B, 6.5),
           (208, 226, 210))
    # draft page
    px_, py_ = P(40, 8)
    pw, ph = 33 * ux, 66
    rect(d, px_, py_, px_ + pw, py_ + ph, fill=(250, 249, 244),
         outline=(120, 118, 108))
    text_l(d, px_ + 5, py_ + 5, "DRAFT TEXT", font(SANS_B, 7.5), (90, 90, 88))
    for i in range(3):
        rect(d, px_ + 5, py_ + 18 + i * 7, px_ + pw - 6, py_ + 20.5 + i * 7,
             fill=(168, 166, 156))
    text_l(d, px_ + 5, py_ + 42, "fossil fuels", font(SERIF_B, 11.5), RED_D)
    d.line([X(px_ + 3), X(py_ + 49), X(px_ + 62), X(py_ + 49)], fill=RED_D,
           width=int(1.8 * SS))
    text_l(d, px_ + 5, py_ + 54, "no mention in the draft", font(SANS_I, 6.8),
           (110, 60, 50))
    # clock
    cx, cy = P(86, 34)
    r = 15.5
    d.ellipse([X(cx - r), X(cy - r), X(cx + r), X(cy + r)],
              fill=(250, 249, 244), outline=INK, width=int(1.6 * SS))
    import math
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        d.line([X(cx + (r - 3) * math.cos(a)), X(cy + (r - 3) * math.sin(a)),
                X(cx + r * math.cos(a)), X(cy + r * math.sin(a))], fill=INK,
               width=SS)
    d.line([X(cx), X(cy), X(cx + 2), X(cy - r + 4)], fill=INK,
           width=int(1.8 * SS))
    d.line([X(cx), X(cy), X(cx + r - 5), X(cy + 3)], fill=INK,
           width=int(1.8 * SS))
    text_c(d, cx, cy + r + 5, "OVERTIME", font(SANS_B, 9.5), RED_D)
    text_c(d, cx, cy + r + 17, "a second day of", font(SANS, 7),
           (70, 70, 66))
    text_c(d, cx, cy + r + 25, "overtime", font(SANS, 7), (70, 70, 66))


def paint_drones(d, x, y, w, h):
    """186 drones over Ukraine: night sky, a moon, searchlights, skyline."""
    rect(d, x, y, x + w, y + h, fill=(16, 22, 38))
    ux, uy = w / 100.0, h / 100.0

    def P(a, b):
        return (x + a * ux, y + b * uy)
    # moon and stars
    mx, my = P(84, 20)
    d.ellipse([X(mx - 6), X(my - 6), X(mx + 6), X(my + 6)],
              fill=(232, 230, 214))
    d.ellipse([X(mx - 9), X(my - 6), X(mx + 3), X(my + 6)],
              fill=(16, 22, 38))
    import random
    rng = random.Random(D.DAY["seed"])
    for _ in range(46):
        sx, sy = P(rng.uniform(2, 98), rng.uniform(3, 52))
        r = rng.uniform(0.5, 1.1)
        d.ellipse([X(sx - r), X(sy - r), X(sx + r), X(sy + r)],
                  fill=(190, 196, 210))
    # searchlight beams from the rooftops (narrow, dimmed against the sky)
    for bx, tx in ((14, 44), (52, 30), (90, 58)):
        bxp, byp = P(bx, 88)
        txp, typ = P(tx, 16)
        _poly(d, [(bxp - 1.3, byp), (bxp + 1.3, byp), (txp + 1.7, typ),
                  (txp - 1.7, typ)], (110, 106, 80))
    # the swarm: drone silhouettes with red blinkers, dashed runs
    swarm = [(18, 26), (30, 18), (42, 30), (55, 14), (63, 26), (72, 36),
             (24, 42), (48, 44), (80, 20)]
    for i, (dx, dy) in enumerate(swarm):
        cx, cy = P(dx, dy)
        _poly(d, [(cx - 4.6, cy - 2.0), (cx + 4.6, cy - 2.0),
                  (cx + 1.6, cy), (cx + 4.6, cy + 2.0), (cx - 4.6, cy + 2.0),
                  (cx - 1.6, cy)], (226, 228, 232))
        d.ellipse([X(cx - 0.9), X(cy - 0.9), X(cx + 0.9), X(cy + 0.9)],
                  fill=(255, 70, 50))
        if i % 2 == 0:
            _dashed(d, [(cx + 3, cy + 3), P(dx + 13, dy + 26)],
                    (150, 120, 90), dash=3.2, gap=3, wdt=1.0)
    # one interception flash
    fx, fy = P(58, 52)
    _flame(d, fx, fy, 7, core=(255, 226, 150), mid=(248, 150, 60))
    # skyline
    blocks = [(2, 26, 66), (16, 18, 76), (30, 30, 60), (46, 20, 72),
              (60, 34, 64), (78, 22, 74), (92, 26, 68)]
    for bx, bw, top in blocks:
        bx0, by0 = P(bx, top)
        bx1, by1 = P(bx + bw, 100)
        rect(d, bx0, by0, bx1, by1, fill=(8, 10, 16))
        for wy in range(int(top) + 6, 96, 9):
            for wx in range(int(bx) + 3, int(bx + bw) - 3, 6):
                if rng.random() < 0.42:
                    wxp, wyp = P(wx, wy)
                    rect(d, wxp, wyp, wxp + 2.2, wyp + 3.0,
                         fill=(238, 196, 110))
    rect(d, x, y + h - 3, x + w, y + h, fill=(4, 5, 8))


PAINTERS = {"gulf": paint_gulf, "ship": paint_ship, "cop": paint_cop,
            "drones": paint_drones}

BADGE_FILL = {"CONFIRMED": (30, 96, 60), "OFFICIAL": (32, 80, 140),
              "REPORTED": (120, 96, 30), "CLAIM": (150, 60, 40)}


def leads(d, y0):
    x = 14.0
    wdt = (1010 - 14 - 2 * 12) / 3
    for lead in D.DAY["leads"]:
        rect(d, x, y0, x + wdt, y0 + 92, fill=(210, 214, 208))
        PAINTERS[lead["art"]](d, x, y0, wdt, 92)
        # chips over the art
        f = font(SANS_B, 8.5)
        cw = d.textlength(lead["chip"], font=f) / SS + 12
        rect(d, x, y0, x + cw, y0 + 15, fill=RED)
        text_l(d, x + 6, y0 + 3.2, lead["chip"], f, (252, 248, 240))
        if lead.get("chip_r"):
            f2 = font(SANS_B, 8.5)
            cw2 = d.textlength(lead["chip_r"], font=f2) / SS + 12
            rect(d, x + wdt - cw2, y0, x + wdt, y0 + 15, fill=NAVY)
            text_l(d, x + wdt - cw2 + 6, y0 + 3.2, lead["chip_r"], f2,
                   (240, 242, 245))
        ky = y0 + 98
        text_l(d, x, ky, lead["kicker"], font(SANS_B, 9.5), RED_D)
        badge(d, x + wdt, ky - 1, lead["badge"], BADGE_FILL[lead["badge"]])
        hy = ky + 14
        for ln in wrap(d, lead["headline"], font(SERIF_B, 22), wdt - 2)[:2]:
            d.text((X(x), X(hy)), ln, font=font(SERIF_B, 22), fill=INK)
            hy += 24
        para(d, x, hy + 1, lead["summary"], font(SERIF, 11), wdt - 4, 12.5,
             INK, max_lines=3)
        text_l(d, x, y0 + 190, lead["sources"], font(SANS_B, 7.5),
               (110, 106, 96))
        x += wdt + 12
    return y0 + 200


def cards(d, y0):
    cards_ = D.DAY["cards"]
    cw = (1010 - 14 - 4 * 9) / 5
    ch = 72
    for i, c in enumerate(cards_):
        col, row = i % 5, i // 5
        x = 14 + col * (cw + 9)
        y = y0 + row * (ch + 7)
        rect(d, x, y, x + cw, y + ch, outline=(176, 168, 146), wdt=1)
        rect(d, x, y, x + cw, y + 12, fill=NAVY)
        text_l(d, x + 5, y + 2.2, "%d · %s" % (c["n"], c["tag"]),
               font(SANS_B, 7.6), (250, 248, 240))
        badge(d, x + cw - 3, y + 1.5, c["badge"], BADGE_FILL[c["badge"]])
        text_l(d, x + 6, y + 16, c["stat"], font(SERIF_B, 19), INK)
        for j, ln in enumerate(wrap(d, c["note"], font(SANS_B, 6.6), 56)[:2]):
            text_l(d, x + 6, y + 38 + j * 8, ln, font(SANS_B, 6.6),
                   (96, 92, 84))
        hy = y + 15
        for ln in wrap(d, c["headline"], font(SERIF_B, 11.5), cw - 74)[:3]:
            d.text((X(x + 68), X(hy)), ln, font=font(SERIF_B, 11.5),
                   fill=INK)
            hy += 13
        det = c["detail"]
        while det and d.textlength(det, font=font(SANS, 8.4)) / SS > cw - 11:
            det = det[:-2].rstrip() + "…" if len(det) > 4 else det[:-1]
        text_l(d, x + 6, y + ch - 20, det, font(SANS, 8.4), (56, 56, 52))
        text_l(d, x + 6, y + ch - 10, c["sources"], font(SANS_B, 6.6),
               (120, 114, 100))
    return y0 + 2 * ch + 7


# ------------------------------------------------------------ world map ---

# Land spans per row of a 92 x 30 dot grid (lon -180..180, lat 84..-49).
LAND_SPANS = [
    [(8, 13), (30, 37), (47, 48), (57, 59), (65, 67), (72, 75)],
    [(6, 16), (29, 38), (55, 62), (66, 71), (74, 80)],
    [(3, 28), (30, 37), (54, 88)],
    [(3, 30), (31, 36), (49, 90)],
    [(4, 31), (33, 35), (41, 42), (48, 90)],
    [(5, 30), (48, 89)],
    [(12, 29), (44, 46), (47, 88)],
    [(13, 28), (44, 46), (45, 86), (86, 89)],
    [(13, 27), (43, 82), (83, 85)],
    [(12, 27), (43, 81), (82, 85)],
    [(12, 26), (43, 46), (49, 51), (52, 81), (82, 84)],
    [(12, 25), (42, 68), (68, 79)],
    [(13, 19), (42, 67), (69, 73), (78, 78)],
    [(14, 20), (42, 66), (69, 73)],
    [(18, 21), (42, 57), (64, 66), (69, 72), (76, 78)],
    [(25, 32), (43, 56), (67, 71), (76, 78)],
    [(25, 34), (44, 56), (66, 74), (79, 82)],
    [(26, 35), (45, 55), (66, 76), (80, 86)],
    [(26, 35), (46, 55), (68, 77), (81, 87)],
    [(27, 36), (46, 55), (72, 78)],
    [(27, 35), (47, 54), (75, 84)],
    [(27, 34), (47, 54), (57, 58), (74, 85)],
    [(27, 33), (48, 53), (57, 59), (74, 85)],
    [(27, 32), (48, 53), (57, 58), (75, 84)],
    [(27, 31), (48, 52), (76, 83)],
    [(27, 30), (49, 52), (77, 82)],
    [(27, 29), (90, 91)],
    [(27, 29), (89, 91)],
    [(27, 28), (88, 90)],
    [(27, 28)],
]
MAP_COLS, MAP_ROWS = 92, 30
MAP_LAT0, MAP_LAT1 = 84.0, -49.0
DOT = (146, 138, 112)
DOT_SEA = (206, 218, 222)


def world_map(d, x, y, w, h):
    text_l(d, x, y, "WHERE IT HAPPENED", font(SANS_B, 10), INK)
    text_l(d, x + 128, y + 1.5,
           "pin numbers match the stories · pin colour is the region",
           font(SANS_I, 8.6), (92, 88, 80))
    gy = y + 17
    gh = h - 17
    cw, chh = w / MAP_COLS, gh / MAP_ROWS
    for r, spans in enumerate(LAND_SPANS):
        land = set()
        for a, b in spans:
            land.update(range(a, b + 1))
        for c in range(MAP_COLS):
            cx = x + (c + 0.5) * cw
            cy = gy + (r + 0.5) * chh
            col = DOT if c in land else DOT_SEA
            rr = min(cw, chh) * 0.30
            d.ellipse([X(cx - rr), X(cy - rr), X(cx + rr), X(cy + rr)],
                      fill=col)
    for num, lon, lat, region in D.PINS:
        fx = (lon + 180) / 360.0
        fy = (MAP_LAT0 - lat) / (MAP_LAT0 - MAP_LAT1)
        cx = x + fx * w
        cy = gy + fy * gh
        col = REGION_COLORS[region]
        r = 7.2
        d.ellipse([X(cx - r), X(cy - r), X(cx + r), X(cy + r)], fill=col,
                  outline=(250, 248, 240), width=SS)
        text_c(d, cx, cy - 4.6, str(num), font(SANS_B, 7.2), (252, 250, 244))
    text_l(d, x, y + h - 1, "story 3’s barrage struck 18 sites across "
           "Ukraine — one pin stands for the whole country",
           font(SANS_I, 8.4), (92, 88, 80))


def also_column(d, x, y, w):
    text_l(d, x, y, D.DAY["also_head"], font(SANS_B, 9.8), INK)
    hline(d, x, x + w, y + 15, INK, 1.2)
    yy = y + 21
    for i, (place, head, src) in enumerate(D.DAY["also"]):
        n = 14 + i
        text_l(d, x, yy, str(n), font(SANS_B, 8.6), RED_D)
        line = "%s — %s" % (place, head)
        text_l(d, x + 17, yy, line, font(SANS, 8.6), INK)
        lw = d.textlength(line, font=font(SANS, 8.6)) / SS
        text_l(d, x + 20 + lw, yy, "· " + src, font(SANS_B, 7.6),
               (110, 104, 92))
        yy += 9.5
    return yy


def bottom_block(d, y0):
    world_map(d, 14, y0, 458, 200)
    also_column(d, 492, y0, 518)
    # date check, full width
    y = 950
    rect(d, 14, y, 1010, y + 28, outline=RED, wdt=1.4)
    text_l(d, 22, y + 4, "DATE CHECK", font(SANS_B, 9), RED_D)
    para(d, 96, y + 3, D.DAY["date_check"], font(SANS, 8.4), 904, 10.4,
         (50, 48, 44), max_lines=2)
    text_l(d, 14, y + 33, D.DAY["how_sure"] + "  ·  " + D.DAY["footer"],
           font(SANS_B, 7.9), (70, 66, 58))
    # closing navy band
    rect(d, 0, 996, W, W, fill=NAVY)
    text_l(d, 14, 1005, "THE WORLD IN ONE DAY", font(SANS_B, 9.5),
           NAVY_TXT, spacing=1.4)
    text_r(d, 1010, 1005, D.DAY["date_long"].upper() + " · ONE PAGE",
           font(SANS_B, 9.5), NAVY_TXT)


def render():
    img = Image.new("RGB", (W * SS, W * SS), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d)
    stat_band(d)
    region_tabs(d)
    ty = timeline(d)
    ly = leads(d, ty + 6)
    cy = cards(d, ly + 10)
    bottom_block(d, cy + 12)
    img = img.resize((W, W), Image.LANCZOS)
    out = Path(__file__).with_name(D.DAY["out_name"])
    img.save(out, format="PNG", optimize=True)
    return out


if __name__ == "__main__":
    p = render()
    print(p, p.stat().st_size)
