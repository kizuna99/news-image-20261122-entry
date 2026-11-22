"""The World Brief — deterministic editorial poster generator (22 Nov 2026).

Draws at 2048x2048 (supersampled) and downscales to the contest size
1024x1024. All randomness comes from a fixed seed; no timestamps.
Requires Pillow + Liberation fonts.
"""
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SS = 2  # supersample factor
W = 1024 * SS
SEED = 20261122

FONT_DIR = os.environ.get(
    "LIBERATION_FONTS", "/usr/share/fonts/truetype/liberation"
)


def font(name, size):
    return ImageFont.truetype(str(Path(FONT_DIR) / name), int(size * SS))


SERIF_B = "LiberationSerif-Bold.ttf"
SERIF = "LiberationSerif-Regular.ttf"
SANS_B = "LiberationSans-Bold.ttf"
SANS = "LiberationSans-Regular.ttf"

# palette
PAPER = (246, 239, 220)
PAPER_D = (238, 228, 200)
INK = (18, 26, 48)
NAVY = (16, 32, 64)
NAVY2 = (27, 48, 92)
GOLD = (192, 148, 44)
GOLD_L = (232, 196, 106)
RED = (178, 34, 40)
RED_D = (128, 22, 30)
CREAM_TXT = (250, 245, 228)
TEAL = (14, 92, 96)
TEAL_D = (8, 52, 62)


def X(v):
    return v * SS


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(d, box, top, bot):
    x0, y0, x1, y1 = [X(v) for v in box]
    h = max(1, y1 - y0)
    for i in range(h):
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=lerp(top, bot, i / h))


def text_c(d, cx, y, s, fnt, fill, spacing=0):
    """Centered text with optional letter spacing (drawn char by char)."""
    if spacing:
        widths = [d.textlength(ch, font=fnt) for ch in s]
        total = sum(widths) + spacing * SS * (len(s) - 1)
        x = X(cx) - total / 2
        for ch, w in zip(s, widths):
            d.text((x, X(y)), ch, font=fnt, fill=fill)
            x += w + spacing * SS
        return
    w = d.textlength(s, font=fnt)
    d.text((X(cx) - w / 2, X(y)), s, font=fnt, fill=fill)


def text_l(d, x, y, s, fnt, fill):
    d.text((X(x), X(y)), s, font=fnt, fill=fill)


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


def spark(d, cx, cy, r, col):
    cx, cy, r = X(cx), X(cy), X(r)
    for a in range(0, 360, 45):
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line([(cx, cy), (cx + dx * r, cy + dy * r)], fill=col, width=2 * SS)
    d.ellipse([cx - r * 0.28, cy - r * 0.28, cx + r * 0.28, cy + r * 0.28],
              fill=col)


def build():
    rng = random.Random(SEED)
    img = Image.new("RGB", (W, W), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    # paper grain (deterministic)
    for _ in range(5200):
        gx, gy = rng.randrange(W), rng.randrange(W)
        tone = rng.choice([(232, 222, 192), (252, 247, 232), (240, 231, 205)])
        d.point((gx, gy), fill=tone)

    # outer frame
    d.rectangle([X(10), X(10), X(1014), X(1014)], outline=NAVY, width=3 * SS)
    d.rectangle([X(17), X(17), X(1007), X(1007)], outline=GOLD, width=1 * SS)

    # ---------- masthead ----------
    text_c(d, 512, 26, "INDEPENDENT DAILY PICTURE EDITION · ONE DAY · ONE PAGE",
           font(SANS_B, 10.5), RED, spacing=2)
    text_c(d, 512, 42, "THE WORLD BRIEF", font(SERIF_B, 63), INK)
    d.line([(X(28), X(116)), (X(996), X(116))], fill=RED, width=3 * SS)
    d.line([(X(28), X(121)), (X(996), X(121))], fill=GOLD, width=1 * SS)
    # dateline bar
    d.rectangle([X(28), X(127), X(996), X(153)], fill=NAVY)
    text_l(d, 40, 133, "SUNDAY · 22 NOVEMBER 2026", font(SANS_B, 13.5), GOLD_L)
    r = "40 SOURCED STORIES · 9 REGIONS · 6 ILLUSTRATED"
    f = font(SANS_B, 13.5)
    d.text((X(984) - d.textlength(r, font=f), X(133)), r, font=f, fill=CREAM_TXT)

    # ---------- hero scene ----------
    hx0, hy0, hx1, hy1 = 28, 161, 996, 341
    split = 592
    # left: Baltic night — the Sparta II ablaze in the Gulf of Finland
    vgrad(d, (hx0, hy0, split, hy1), (6, 10, 30), (44, 38, 62))
    # right: COP31 dawn, Antalya (second day of overtime)
    vgrad(d, (split, hy0, hx1, hy1), (16, 84, 96), (238, 178, 92))
    # stars (left only)
    for _ in range(80):
        sx = rng.randrange(X(hx0 + 8), X(split - 8))
        sy = rng.randrange(X(hy0 + 6), X(hy0 + 84))
        d.point((sx, sy), fill=(220, 228, 250))
        if rng.random() < 0.3:
            d.point((sx + 1, sy), fill=(180, 195, 235))
    # crescent moon (left)
    d.ellipse([X(64), X(174), X(96), X(206)], fill=(232, 234, 220))
    d.ellipse([X(76), X(170), X(104), X(202)], fill=(12, 18, 40))
    # sun (right)
    d.ellipse([X(872), X(190), X(968), X(286)], fill=(250, 205, 92))
    d.ellipse([X(884), X(202), X(956), X(274)], fill=(252, 220, 130))
    # globe arc (right)
    gx, gy, gr = 700, 262, 58
    d.ellipse([X(gx - gr), X(gy - gr), X(gx + gr), X(gy + gr)],
              outline=(240, 240, 230), width=2 * SS)
    for k in (-0.6, 0.0, 0.6):
        d.arc([X(gx - gr * (1 - abs(k)) - 4), X(gy - gr),
               X(gx + gr * (1 - abs(k)) + 4), X(gy + gr)], 90, 270,
              fill=(240, 240, 230), width=1 * SS)
        d.arc([X(gx - gr * (1 - abs(k)) - 4), X(gy - gr),
               X(gx + gr * (1 - abs(k)) + 4), X(gy + gr)], 270, 450,
              fill=(240, 240, 230), width=1 * SS)
    for off in (-28, 0, 28):
        d.line([(X(gx - gr + 4), X(gy + off)), (X(gx + gr - 4), X(gy + off))],
               fill=(240, 240, 230), width=1 * SS)

    # --- left scene: Finnish shore, lighthouse, burning freighter, rescue ship
    # distant shore line + shore lights (far left)
    d.polygon([(X(hx0), X(300)), (X(150), X(296)), (X(210), X(302)),
               (X(210), X(318)), (X(hx0), X(318))], fill=(7, 10, 20))
    for lx, ly in [(52, 292), (84, 290), (118, 293), (148, 291), (176, 294)]:
        d.rectangle([X(lx), X(ly), X(lx + 3), X(ly + 3)], fill=(255, 214, 130))
    # lighthouse on the point
    d.polygon([(X(196), X(300)), (X(204), X(300)), (X(202), X(258)),
               (X(198), X(258))], fill=(10, 13, 26))
    d.rectangle([X(195), X(250), X(205), X(258)], fill=(255, 224, 150))
    d.polygon([(X(205), X(252)), (X(268), X(238)), (X(268), X(262))],
              fill=(255, 230, 160, 60))
    # firelight halo behind the freighter so the silhouette reads
    d.ellipse([X(300), X(168), X(500), X(330)], fill=(255, 120, 50, 34))
    d.ellipse([X(330), X(190), X(470), X(310)], fill=(255, 140, 60, 30))
    # the freighter: hull, containers, bridge tower
    hull = (10, 13, 24)
    d.polygon([(X(258), X(290)), (X(540), X(290)), (X(524), X(308)),
               (X(282), X(308))], fill=hull)
    d.rectangle([X(258), X(284), X(540), X(290)], fill=hull)
    d.line([(X(262), X(290)), (X(536), X(290))], fill=(150, 160, 185),
           width=1 * SS)
    for cx, cw, col in [(286, 52, (44, 52, 78)), (344, 52, (88, 52, 44)),
                        (402, 46, (36, 58, 66))]:
        d.rectangle([X(cx), X(266), X(cx + cw), X(284)], fill=col)
        d.rectangle([X(cx), X(250), X(cx + cw - 10), X(266)], fill=col)
        d.line([(X(cx), X(250)), (X(cx + cw - 10), X(250))],
               fill=(190, 195, 210), width=1 * SS)
    d.rectangle([X(478), X(236), X(512), X(284)], fill=(30, 40, 62))
    for wy in (244, 254, 264):
        d.rectangle([X(484), X(wy), X(488), X(wy + 3)], fill=(255, 220, 140))
        d.rectangle([X(496), X(wy), X(500), X(wy + 3)], fill=(255, 220, 140))
    d.line([(X(478), X(236)), (X(512), X(236))], fill=(200, 205, 220),
           width=1 * SS)
    d.line([(X(495), X(236)), (X(495), X(222))], fill=(30, 40, 62), width=2 * SS)
    d.point((X(495), X(220)), fill=(255, 90, 80))
    # smoke column first, then the fire in front of it
    for sx, sy, sr in [(382, 196, 14), (398, 176, 18), (418, 156, 22)]:
        d.ellipse([X(sx - sr), X(sy - sr), X(sx + sr), X(sy + sr)],
                  fill=(128, 126, 136, 95))
    d.ellipse([X(330), X(200), X(430), X(268)], fill=(255, 110, 40, 50))
    d.ellipse([X(344), X(214), X(398), X(258)], fill=(255, 110, 40, 215))
    d.ellipse([X(372), X(204), X(414), X(252)], fill=(255, 130, 50, 200))
    d.ellipse([X(356), X(222), X(388), X(250)], fill=(255, 185, 70, 240))
    d.ellipse([X(382), X(214), X(406), X(244)], fill=(255, 200, 90, 230))
    d.ellipse([X(330), X(280), X(430), X(294)], fill=(255, 110, 45, 90))
    # drone streaks that found the ship
    d.line([(X(560), X(196)), (X(408), X(238))], fill=(255, 170, 90),
           width=2 * SS)
    d.line([(X(548), X(178)), (X(392), X(228))], fill=(255, 150, 80),
           width=1 * SS)
    spark(d, 402, 240, 10, (255, 190, 80))
    # rescue vessel standing off (right, small, lit)
    d.polygon([(X(516), X(304)), (X(576), X(304)), (X(568), X(314)),
               (X(524), X(314))], fill=(26, 34, 54))
    d.rectangle([X(536), X(294), X(558), X(304)], fill=(26, 34, 54))
    d.line([(X(547), X(294)), (X(547), X(286))], fill=(26, 34, 54), width=1 * SS)
    d.point((X(547), X(284)), fill=(255, 224, 150))
    for lx, ly in [(540, 297), (547, 297), (552, 297)]:
        d.rectangle([X(lx), X(ly), X(lx + 2.5), X(ly + 2.5)],
                    fill=(255, 224, 150))
    # sea band + firelight reflections
    d.rectangle([X(hx0), X(318), X(split), X(hy1)], fill=(9, 20, 42))
    for i in range(26):
        wx = rng.randrange(X(hx0 + 10), X(split - 30))
        wy = rng.randrange(X(322), X(hy1 - 4))
        d.line([(wx, wy), (wx + X(rng.randrange(8, 22)), wy)],
               fill=(90, 120, 170), width=1)
    for i in range(9):
        wx = rng.randrange(X(340), X(430))
        wy = rng.randrange(X(322), X(hy1 - 4))
        d.line([(wx, wy), (wx + X(rng.randrange(10, 26)), wy)],
               fill=(255, 150, 80), width=1)

    # Antalya skyline (right bottom): dome + minarets
    sky = TEAL_D
    d.rectangle([X(split), X(310), X(hx1), X(324)], fill=sky)
    d.pieslice([X(748), X(246), X(868), X(324)], 180, 360, fill=sky)
    d.rectangle([X(802), X(232), X(814), X(252)], fill=sky)
    d.polygon([(X(802), X(232)), (X(814), X(232)), (X(808), X(218))], fill=sky)
    for mx in (636, 946):
        d.rectangle([X(mx), X(246), X(mx + 10), X(324)], fill=sky)
        d.polygon([(X(mx - 2), X(246)), (X(mx + 12), X(246)), (X(mx + 5), X(226))],
                  fill=sky)
        d.rectangle([X(mx - 4), X(276), X(mx + 14), X(282)], fill=sky)
    for bx, bw, bh in [(600, 44, 30), (884, 52, 38), (700, 30, 20)]:
        d.rectangle([X(bx), X(324 - bh), X(bx + bw), X(324)], fill=sky)
    # ground line both sides
    d.rectangle([X(hx0), X(324), X(hx1), X(hy1)], fill=(10, 14, 26))
    # hero frame + divider
    d.line([(X(split), X(hy0)), (X(split), X(hy1))], fill=GOLD, width=2 * SS)
    d.rectangle([X(hx0), X(hy0), X(hx1), X(hy1)], outline=INK, width=2 * SS)
    # hero tags
    d.rectangle([X(hx0), X(hy0), X(300), X(hy0 + 24)], fill=RED)
    text_l(d, hx0 + 10, hy0 + 4, "LEAD · BALTIC — SHIP ABLAZE", font(SANS_B, 11.5),
           CREAM_TXT)
    d.rectangle([X(772), X(hy0), X(hx1), X(hy0 + 24)], fill=TEAL_D)
    text_l(d, 782, hy0 + 4, "CLIMATE · COP31 OVERTIME", font(SANS_B, 11.5),
           CREAM_TXT)
    return img, d


# ---------------- panels ----------------

def icon_ship(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (10, 16, 40), (48, 40, 64))
    # freighter silhouette
    d.polygon([(X(x + 8), X(y + 66)), (X(x + w - 6), X(y + 66)),
               (X(x + w - 14), X(y + 78)), (X(x + 16), X(y + 78))],
              fill=(6, 8, 16))
    d.rectangle([X(x + 14), X(y + 54), X(x + 44), X(y + 66)], fill=(16, 20, 36))
    d.rectangle([X(x + 14), X(y + 44), X(x + 38), X(y + 54)], fill=(16, 20, 36))
    d.rectangle([X(x + 62), X(y + 40), X(x + 74), X(y + 66)], fill=(10, 13, 26))
    d.rectangle([X(x + 65), X(y + 45), X(x + 68), X(y + 48)],
                fill=(255, 214, 130))
    # fire + smoke amidships
    d.ellipse([X(x + 40), X(y + 26), X(x + 60), X(y + 52)],
              fill=(255, 110, 40, 215))
    d.ellipse([X(x + 45), X(y + 33), X(x + 56), X(y + 50)],
              fill=(255, 185, 70, 235))
    d.ellipse([X(x + 44), X(y + 12), X(x + 62), X(y + 28)],
              fill=(130, 128, 138, 110))
    # drone streak
    d.line([(X(x + w - 4), X(y + 6)), (X(x + 56), X(y + 32))],
           fill=(255, 170, 90), width=2 * SS)
    spark(d, x + 55, y + 34, 8, (255, 190, 80))
    # sea
    d.rectangle([X(x), X(y + 78), X(x + w), X(y + h)], fill=(9, 20, 42))
    for i, (wx, wy) in enumerate([(10, 86), (30, 92), (52, 88), (66, 94),
                                  (20, 98), (44, 100)]):
        col = (255, 150, 80) if 28 < wx < 62 else (90, 120, 170)
        d.line([(X(x + wx), X(y + wy)), (X(x + wx + 9), X(y + wy))], fill=col,
               width=1)


def icon_globe(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (14, 92, 96), (240, 186, 96))
    cx, cy, r = x + w / 2, y + h / 2 + 2, 28
    d.ellipse([X(cx - r), X(cy - r), X(cx + r), X(cy + r)], fill=(20, 110, 110),
              outline=(245, 242, 225), width=2 * SS)
    for off in (-14, 0, 14):
        d.line([(X(cx - r + 3), X(cy + off)), (X(cx + r - 3), X(cy + off))],
               fill=(245, 242, 225), width=1 * SS)
    d.arc([X(cx - 11), X(cy - r), X(cx + 11), X(cy + r)], 90, 270,
          fill=(245, 242, 225), width=1 * SS)
    d.arc([X(cx - 11), X(cy - r), X(cx + 11), X(cy + r)], 270, 450,
          fill=(245, 242, 225), width=1 * SS)
    d.pieslice([X(x + w - 38), X(y + h - 28), X(x + w + 2), X(y + h + 12)],
               180, 360, fill=TEAL_D)


def icon_drones(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (12, 18, 44), (52, 42, 70))
    # swarm of small quadcopter silhouettes
    for cx, cy, s in [(18, 22, 7), (38, 14, 6), (58, 24, 7), (70, 12, 5),
                      (28, 38, 6), (50, 42, 6), (66, 36, 6), (14, 48, 5),
                      (76, 48, 5)]:
        d.line([(X(x + cx - s), X(y + cy - s)), (X(x + cx + s), X(y + cy + s))],
               fill=(200, 208, 230), width=1 * SS)
        d.line([(X(x + cx - s), X(y + cy + s)), (X(x + cx + s), X(y + cy - s))],
               fill=(200, 208, 230), width=1 * SS)
        d.ellipse([X(x + cx - 2), X(y + cy - 2), X(x + cx + 2), X(y + cy + 2)],
                  fill=(235, 238, 245))
    # intercept bursts
    spark(d, x + 34, y + 58, 9, (240, 244, 255))
    spark(d, x + 62, y + 64, 7, (240, 244, 255))
    # skyline below
    for bx, bw, bh in [(4, 15, 22), (22, 12, 30), (56, 17, 20), (74, 10, 26)]:
        d.rectangle([X(x + bx), X(y + h - 6 - bh), X(x + bx + bw), X(y + h - 6)],
                    fill=(9, 12, 24))
    for wx, wy in [(8, 92), (26, 84), (60, 90), (77, 86)]:
        d.rectangle([X(x + wx), X(y + wy), X(x + wx + 2.5), X(y + wy + 3)],
                    fill=(255, 214, 130))
    d.rectangle([X(x), X(y + h - 6), X(x + w), X(y + h)], fill=(8, 10, 20))


def icon_claim(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (52, 34, 30), (150, 96, 54))
    # industrial plant silhouette
    for bx, bw, bh in [(6, 22, 30), (30, 16, 22), (48, 24, 36)]:
        d.rectangle([X(x + bx), X(y + h - 10 - bh), X(x + bx + bw),
                     X(y + h - 10)], fill=(46, 36, 38))
    d.rectangle([X(x + 66), X(y + 22), X(x + 71), X(y + h - 10)],
                fill=(46, 36, 38))
    for wx, wy in [(10, 84), (18, 88), (34, 90), (52, 80), (58, 86), (62, 76)]:
        d.rectangle([X(x + wx), X(y + wy), X(x + wx + 2.5), X(y + wy + 3)],
                    fill=(255, 190, 90))
    d.rectangle([X(x), X(y + h - 10), X(x + w), X(y + h)], fill=(16, 12, 14))
    # the claim: a gold coin disc with a paragraph mark, top-left
    d.ellipse([X(x + 8), X(y + 8), X(x + 42), X(y + 42)], fill=GOLD,
              outline=GOLD_L, width=2 * SS)
    text_l(d, x + 17, y + 11, "§", font(SERIF_B, 24), (70, 48, 8))


def icon_bottle(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (30, 26, 40), (84, 52, 48))
    # three liquor bottles
    for bx, bw, bh, col in [(16, 16, 52, (44, 56, 46)), (38, 18, 60, (56, 42, 44)),
                            (60, 15, 48, (40, 50, 62))]:
        d.rectangle([X(x + bx + bw / 2 - 3), X(y + h - 14 - bh), X(x + bx + bw / 2 + 3),
                     X(y + h - 14 - bh + 8)], fill=col)
        d.rectangle([X(x + bx), X(y + h - 14 - bh + 8), X(x + bx + bw),
                     X(y + h - 14)], fill=col)
        d.rectangle([X(x + bx + 3), X(y + h - 38), X(x + bx + bw - 3),
                     X(y + h - 24)], fill=(240, 232, 205))
    d.rectangle([X(x + 44), X(y + h - 14 - 60), X(x + 50), X(y + h - 14 - 52)],
                fill=GOLD_L)
    d.rectangle([X(x), X(y + h - 14), X(x + w), X(y + h)], fill=(14, 12, 16))
    # warning badge: red disc, white cross
    d.ellipse([X(x + w - 32), X(y + 8), X(x + w - 8), X(y + 32)], fill=RED,
              outline=(255, 240, 220), width=2 * SS)
    d.rectangle([X(x + w - 23), X(y + 13), X(x + w - 17), X(y + 27)],
                fill=(255, 245, 230))
    d.rectangle([X(x + w - 27), X(y + 17), X(x + w - 13), X(y + 23)],
                fill=(255, 245, 230))


def icon_fire(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (26, 22, 38), (96, 48, 40))
    # factory silhouette
    d.rectangle([X(x + 6), X(y + 52), X(x + 52), X(y + h - 8)], fill=(16, 13, 18))
    d.rectangle([X(x + 56), X(y + 62), X(x + w - 6), X(y + h - 8)],
                fill=(16, 13, 18))
    d.rectangle([X(x + 44), X(y + 30), X(x + 50), X(y + 52)], fill=(16, 13, 18))
    # flames over the main hall
    for fx, fw, fh in [(12, 12, 26), (26, 14, 34), (40, 11, 22)]:
        d.polygon([(X(x + fx), X(y + 54)), (X(x + fx + fw / 2), X(y + 54 - fh)),
                   (X(x + fx + fw), X(y + 54))], fill=(255, 120, 45, 220))
        d.polygon([(X(x + fx + 3), X(y + 54)), (X(x + fx + fw / 2),
                   X(y + 54 - fh * 0.6)), (X(x + fx + fw - 3), X(y + 54))],
                  fill=(255, 190, 80, 235))
    # smoke
    for sx, sy, sr in [(30, 16, 9), (44, 10, 12), (60, 14, 8)]:
        d.ellipse([X(x + sx - sr), X(y + sy - sr), X(x + sx + sr),
                   X(y + sy + sr)], fill=(120, 116, 120, 100))
    # searchlight beams from the right block
    d.polygon([(X(x + 62), X(y + 64)), (X(x + 30), X(y + 30)),
               (X(x + 38), X(y + 26))], fill=(255, 240, 190, 70))
    d.polygon([(X(x + 70), X(y + 64)), (X(x + 52), X(y + 34)),
               (X(x + 59), X(y + 31))], fill=(255, 240, 190, 55))
    d.rectangle([X(x), X(y + h - 8), X(x + w), X(y + h)], fill=(10, 9, 12))


PANELS = [
    ("01 · EUROPE — BALTIC", RED, icon_ship, "REUTERS · YLE",
     "Russian cargo ship burns after Baltic drone strike",
     "Sparta II drifts into Finnish waters; all 16 crew evacuated as Helsinki blames Kyiv's drones."),
    ("02 · CLIMATE — TÜRKİYE", TEAL, icon_globe, "GUARDIAN · REUTERS",
     "COP31 deadlocked into a second day of overtime",
     "New draft concedes warming is on course to pass 1.5°C; fossil wording splits ~200 nations."),
    ("03 · EUROPE — WAR", NAVY2, icon_drones, "QNA · UKR. AIR FORCE",
     "Russia fires 186 drones in one-night barrage",
     "Kyiv says 161 downed or jammed; strikes land at 18 sites, 11 hurt in Sloviansk & Kherson."),
    ("04 · MIDEAST — GULF WAR", (146, 84, 22), icon_claim, "RTM · BERNAMA",
     "Bahrain demands Iran pay for strike damage",
     "Manama holds Tehran fully responsible, seeks compensation and UN action over the plant hit."),
    ("05 · S ASIA — INDIA", RED_D, icon_bottle, "REUTERS",
     "Tainted liquor kills 11 in India's Manipur",
     "Over 180 in hospital after adulterated local alcohol; chief minister orders an investigation."),
    ("06 · SE ASIA — INDONESIA", (30, 90, 140), icon_fire, "RTM · BERNAMA",
     "Search for 36 missing in Indonesia factory fire",
     "Rescuers comb a gutted Serang candy factory after a blaze kills 3; dozens unaccounted for."),
]


WIRE = [
    ("EUROPE", "Drones likely hit Rosgvardiya directorate in Krasnodar"),
    ("EUROPE", "Fourteen feared trapped in Kyiv block hit by drone"),
    ("EUROPE", "Dashcam films missile striking residential Lviv"),
    ("EUROPE", "Fico says Slovakia won't fund €45bn EU Ukraine loan"),
    ("EUROPE", "Estonia opens road link bypassing Russian territory"),
    ("EUROPE", "Italy ex-police chief found dead amid mafia probe"),
    ("EUROPE", "Zagreb rallies over psychiatric hospital death"),
    ("EUROPE", "Floods submerge some 850 homes across France"),
    ("EUROPE", "Costa floats 3% digital tax in EU budget deal"),
    ("MIDEAST", "Iran starts rolling power cuts of up to 2h a day"),
    ("MIDEAST", "Trump seeks permanent deal barring Iran's bomb"),
    ("MIDEAST", "Qatari delegation holds talks in Tehran"),
    ("MIDEAST", "US denies Iran claim its missile damaged an F-16"),
    ("MIDEAST", "Meningitis cases climb unusually in Gaza"),
    ("MIDEAST", "UNIFIL starts handing Lebanon posts to the army"),
    ("AFRICA", "Bandits kill 11 in Nigeria, burn homes & shops"),
    ("AFRICA", "Algeria shoots dead two Moroccan drug smugglers"),
    ("AFRICA", "S. Africa's first woman deputy president dies, 71"),
    ("LATIN AM", "Bolsonaro taken to Brasília hospital, stomach pain"),
    ("LATIN AM", "Brazil moves to shield Raoni's Amazon birthplace"),
    ("N AMERICA", "Canada sees no shift in US military ties — minister"),
    ("N AMERICA", "Democrats draft 100-day agenda after midterm wins"),
    ("GLOBAL", "UN talks agree to draft 'killer robot' rules by 2028"),
    ("GLOBAL", "Swimmer Pugh crosses Hormuz to plead for peace"),
    ("SE ASIA", "Vietnam speeds land seizures for priority projects"),
    ("E ASIA", "S. Korea education minister quits in AI exam scandal"),
    ("E ASIA", "China protests US block on its telecom firms"),
    ("E ASIA", "Maple crowds flock to Japan's Mount Oyama"),
    ("SE ASIA", "Fire guts 32 Baduy homes in Lebak; 132 displaced"),
    ("OCEANIA", "Marles: US budget office 'wrong' on AUKUS subs pact"),
    ("OCEANIA", "England beat All Blacks; Wallabies edge Wales"),
    ("MARKETS", "Bitcoin steadies near $60,000 after $55,000 scare"),
    ("MARKETS", "Nvidia accounting in focus of SEC probe — sources"),
    ("SPORT", "Messi wins 2nd straight MLS Golden Boot; Miami lose 0–3"),
]


def panels_and_wire(img, d):
    # hero caption strip
    cy = 349
    d.rectangle([X(28), X(cy), X(996), X(cy + 40)], fill=INK)
    text_l(d, 40, cy + 4, "GULF OF FINLAND — Sparta II still burns in Finnish",
           font(SANS_B, 12.5), CREAM_TXT)
    text_l(d, 40, cy + 20, "waters; crew of 16 safe · NATO's edge on alert",
           font(SANS_B, 12.5), CREAM_TXT)
    text_l(d, 620, cy + 4, "ANTALYA — COP31 in a second day of overtime;",
           font(SANS_B, 12.5), GOLD_L)
    text_l(d, 620, cy + 20, "draft concedes warming will pass 1.5°C",
           font(SANS_B, 12.5), GOLD_L)

    # panels 3 x 2
    px0, py0, pw, ph, gap = 28, 397, 309, 146, 6
    for i, (tag, col, icon, src, head, summ) in enumerate(PANELS):
        cx = px0 + (i % 3) * (pw + gap)
        cyy = py0 + (i // 3) * (ph + gap)
        d.rectangle([X(cx), X(cyy), X(cx + pw), X(cyy + ph)], fill=(255, 253, 244),
                    outline=INK, width=1 * SS)
        d.rectangle([X(cx), X(cyy), X(cx + pw), X(cyy + 22)], fill=col)
        text_l(d, cx + 9, cyy + 4, tag, font(SANS_B, 11), CREAM_TXT)
        _sf = font(SANS_B, 9)
        _sw = d.textlength(src, font=_sf)
        d.text((X(cx + pw - 9) - _sw, X(cyy + 6)), src, font=_sf,
               fill=(255, 240, 210))
        # icon scene
        ix, iy, iw, ih = cx + 9, cyy + 29, 82, 108
        icon(d, ix, iy, iw, ih)
        d.rectangle([X(ix), X(iy), X(ix + iw), X(iy + ih)], outline=INK,
                    width=1 * SS)
        # headline + summary
        tx = cx + 101
        tw = pw - 101 - 9
        hl = wrap(d, head, font(SANS_B, 15), tw)
        yy = cyy + 31
        for ln in hl[:3]:
            text_l(d, tx, yy, ln, font(SANS_B, 15), INK)
            yy += 20
        yy += 2
        for ln in wrap(d, summ, font(SANS, 12), tw)[:4]:
            text_l(d, tx, yy, ln, font(SANS, 12), (52, 56, 66))
            yy += 15.5

    # world wire
    wy = 703
    d.rectangle([X(28), X(wy), X(996), X(wy + 24)], fill=RED)
    text_l(d, 40, wy + 4,
           "THE WORLD WIRE — 34 MORE STORIES FIRST REPORTED SUNDAY 22 NOV 2026",
           font(SANS_B, 12.5), CREAM_TXT)
    colw, row0, rowh = 474, wy + 32, 14.0
    for i, (region, head) in enumerate(WIRE):
        col = i // 17
        row = i % 17
        x = 36 + col * (colw + 12)
        y = row0 + row * rowh
        text_l(d, x, y, f"{i + 7:02d}", font(SANS_B, 10.5), RED)
        text_l(d, x + 23, y, region, font(SANS_B, 10.5), NAVY)
        rw = d.textlength(region, font=font(SANS_B, 10.5)) / SS
        text_l(d, x + 29 + rw, y, "· " + head, font(SANS, 11), INK)
        if row < 16:
            d.line([(X(x), X(y + 12)), (X(x + colw - 8), X(y + 12))],
                   fill=(216, 206, 178), width=1)

    # footer / date check
    fy = 982
    d.line([(X(28), X(fy - 6)), (X(996), X(fy - 6))], fill=GOLD, width=1 * SS)
    text_c(d, 512, fy,
           "DATE CHECK — ALL 40 ITEMS FIRST REPORTED SUNDAY 22 NOVEMBER 2026 · "
           "FULL SOURCES IN THE REPOSITORY (SOURCES.MD)", font(SANS_B, 10.5), NAVY)
    text_c(d, 512, fy + 15,
           "No news photographs — every image on this page is original drawn geometry.",
           font(SANS, 10), (90, 88, 78))


def main():
    img, d = build()
    panels_and_wire(img, d)
    out = img.resize((1024, 1024), Image.LANCZOS)
    dest = Path(__file__).with_name("entry.png")
    out.save(dest, format="PNG", optimize=True)
    print(f"wrote {dest} {dest.stat().st_size} bytes")


if __name__ == "__main__":
    main()
