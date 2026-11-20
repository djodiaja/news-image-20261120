"""Draw the 20 November 2026 world-news page to assets/entry.png.

Run once locally (Pillow + Windows fonts); main.py only copies the result, so the
entry itself needs no fonts, no network and is byte-for-byte deterministic.
Everything is drawn at 2x and downsampled with LANCZOS for clean text at 1024 px.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from stories import DATE_LINE, KEYFIGS, MARKETS, SOURCES, STORIES, TIMELINE

S = 2  # supersampling factor
W = H = 1024
FONTS = Path("C:/Windows/Fonts")

INK = (24, 28, 38)
PAPER = (250, 247, 240)
NAVY = (18, 38, 74)
RULE = (190, 182, 166)
MUTED = (92, 96, 108)
SEA = (214, 228, 238)
LAND = (236, 230, 214)
LAND_EDGE = (178, 168, 146)
REGION_COL = {
    "Europe": (52, 92, 170),
    "Middle East": (196, 120, 30),
    "Africa": (60, 140, 72),
    "Asia-Pacific": (190, 50, 60),
    "North America": (110, 70, 160),
    "Latin America": (20, 140, 150),
    "Global": (90, 90, 90),
}
TIER_COL = {1: (200, 30, 40), 2: (226, 120, 20), 3: NAVY}


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size * S)


F = {
    "mast": font("georgiab.ttf", 34),
    "mast_sub": font("georgiai.ttf", 13),
    "kv": font("georgiab.ttf", 19),
    "kl": font("ARIALN.TTF", 10),
    "lead_h": font("georgiab.ttf", 15),
    "lead_d": font("arial.ttf", 10),
    "sec_h": font("ARIALNB.TTF", 11),
    "sec_d": font("ARIALN.TTF", 9),
    "tag": font("ARIALNB.TTF", 8),
    "also": font("ARIALN.TTF", 10.5),
    "also_b": font("ARIALNB.TTF", 11),
    "pin": font("ARIALNB.TTF", 7),
    "pin_lead": font("ARIALNB.TTF", 9),
    "sect": font("ARIALNB.TTF", 10),
    "small": font("ARIALN.TTF", 8),
    "box_h": font("ARIALNB.TTF", 10),
    "box": font("ARIALN.TTF", 9),
}


def P(*v):
    """Scale layout units (1024 frame) to canvas pixels."""
    return [round(x * S) for x in v] if len(v) > 1 else round(v[0] * S)


def wrap(d, text, fnt, width, max_lines):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if d.textlength(t, font=fnt) <= width * S:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while d.textlength(last + "...", font=fnt) > width * S and " " in last:
            last = last.rsplit(" ", 1)[0]
        lines[-1] = last.rstrip(",;:") + "..."
    return lines


def text_block(d, x, y, text, fnt, width, max_lines, fill, lh):
    for i, line in enumerate(wrap(d, text, fnt, width, max_lines)):
        d.text(P(x, y + i * lh), line, font=fnt, fill=fill)
    return y + len(wrap(d, text, fnt, width, max_lines)) * lh


# ---------------------------------------------------------------- icons
def icon(d, kind, cx, cy, r, col):
    """Small pictograms drawn from primitives; r is the half-size in layout units."""
    X = lambda v: (cx + v * r) * S
    Y = lambda v: (cy + v * r) * S
    lw = max(2, round(r * S * 0.12))
    if kind == "vote":
        d.rectangle([X(-0.8), Y(-0.1), X(0.8), Y(0.9)], outline=col, width=lw)
        d.rectangle([X(-0.35), Y(-0.85), X(0.35), Y(0.1)], fill=col)
        d.line([X(-0.4), Y(-0.1), X(0.4), Y(-0.1)], fill=PAPER, width=lw)
    elif kind == "missile":
        d.polygon([(X(-0.9), Y(0.9)), (X(0.5), Y(-0.5)), (X(0.9), Y(-0.9)), (X(0.6), Y(-0.4))], fill=col)
        d.polygon([(X(-0.9), Y(0.9)), (X(-0.6), Y(0.3)), (X(-0.3), Y(0.6))], fill=col)
        for a, b in ((-0.95, 0.3), (-0.3, 0.95)):
            d.line([X(-0.9), Y(0.9), X(a), Y(b)], fill=col, width=lw)
    elif kind == "court":
        d.polygon([(X(-0.9), Y(-0.45)), (X(0), Y(-0.95)), (X(0.9), Y(-0.45))], fill=col)
        for v in (-0.65, -0.22, 0.22, 0.65):
            d.rectangle([X(v - 0.1), Y(-0.35), X(v + 0.1), Y(0.6)], fill=col)
        d.rectangle([X(-0.95), Y(0.7), X(0.95), Y(0.9)], fill=col)
    elif kind == "money":
        d.line([X(-0.9), Y(0.9), X(0.9), Y(0.9)], fill=col, width=lw)
        d.line([X(-0.9), Y(0.9), X(-0.9), Y(-0.9)], fill=col, width=lw)
        pts = [(-0.8, 0.5), (-0.4, 0.1), (0, 0.35), (0.4, -0.3), (0.85, -0.7)]
        d.line([(X(a), Y(b)) for a, b in pts], fill=col, width=lw + 1)
    elif kind == "down":
        d.line([X(-0.9), Y(0.9), X(0.9), Y(0.9)], fill=col, width=lw)
        pts = [(-0.85, -0.7), (-0.4, -0.3), (0, -0.5), (0.4, 0.2), (0.85, 0.6)]
        d.line([(X(a), Y(b)) for a, b in pts], fill=col, width=lw + 1)
    elif kind == "storm":
        d.ellipse([X(-0.9), Y(-0.6), X(0.2), Y(0.3)], fill=col)
        d.ellipse([X(-0.4), Y(-0.9), X(0.8), Y(0.2)], fill=col)
        d.polygon([(X(0.1), Y(0.25)), (X(-0.25), Y(0.65)), (X(0), Y(0.65)), (X(-0.2), Y(1.0)), (X(0.35), Y(0.5)), (X(0.1), Y(0.5)), (X(0.3), Y(0.25))], fill=(240, 190, 30))
    elif kind == "quake":
        pts = [(-1, 0), (-0.6, 0), (-0.45, -0.6), (-0.25, 0.7), (-0.05, -0.9), (0.15, 0.8), (0.35, -0.4), (0.5, 0), (1, 0)]
        d.line([(X(a), Y(b)) for a, b in pts], fill=col, width=lw + 1)
    elif kind == "fire":
        d.polygon([(X(0), Y(-0.95)), (X(0.6), Y(-0.1)), (X(0.55), Y(0.6)), (X(0), Y(0.95)), (X(-0.55), Y(0.6)), (X(-0.6), Y(0)), (X(-0.25), Y(-0.35))], fill=col)
        d.ellipse([X(-0.25), Y(0.1), X(0.25), Y(0.8)], fill=(250, 200, 60))
    elif kind == "ship":
        d.polygon([(X(-0.95), Y(0.2)), (X(0.95), Y(0.2)), (X(0.6), Y(0.7)), (X(-0.7), Y(0.7))], fill=col)
        d.rectangle([X(-0.4), Y(-0.3), X(0.3), Y(0.2)], fill=col)
        d.rectangle([X(-0.1), Y(-0.8), X(0.05), Y(-0.3)], fill=col)
    elif kind == "plane":
        d.polygon([(X(-0.95), Y(0.1)), (X(0.8), Y(-0.1)), (X(0.95), Y(0)), (X(0.8), Y(0.1)), (X(-0.95), Y(-0.1))], fill=col)
        d.polygon([(X(0.1), Y(0)), (X(-0.3), Y(-0.8)), (X(-0.1), Y(-0.8)), (X(0.4), Y(0))], fill=col)
        d.polygon([(X(0.1), Y(0)), (X(-0.3), Y(0.8)), (X(-0.1), Y(0.8)), (X(0.4), Y(0))], fill=col)
    elif kind == "ball":
        d.ellipse([X(-0.85), Y(-0.85), X(0.85), Y(0.85)], outline=col, width=lw)
        d.regular_polygon((cx * S, cy * S, r * S * 0.35), 5, fill=col)
    elif kind == "trophy":
        d.pieslice([X(-0.7), Y(-1.2), X(0.7), Y(0.3)], 0, 180, fill=col)
        d.rectangle([X(-0.12), Y(-0.45), X(0.12), Y(0.6)], fill=col)
        d.rectangle([X(-0.5), Y(0.6), X(0.5), Y(0.85)], fill=col)
    elif kind == "flask":
        d.polygon([(X(-0.2), Y(-0.9)), (X(0.2), Y(-0.9)), (X(0.2), Y(-0.2)), (X(0.8), Y(0.85)), (X(-0.8), Y(0.85)), (X(-0.2), Y(-0.2))], outline=col, width=lw)
        d.polygon([(X(-0.45), Y(0.25)), (X(0.45), Y(0.25)), (X(0.75), Y(0.8)), (X(-0.75), Y(0.8))], fill=col)
    elif kind == "dove":
        d.ellipse([X(-0.8), Y(-0.2), X(0.5), Y(0.5)], fill=col)
        d.ellipse([X(0.25), Y(-0.45), X(0.75), Y(0.05)], fill=col)
        d.polygon([(X(0.7), Y(-0.25)), (X(1.0), Y(-0.15)), (X(0.7), Y(-0.05))], fill=(230, 150, 30))
        d.polygon([(X(-0.4), Y(0)), (X(-0.1), Y(-0.95)), (X(0.2), Y(0))], fill=col)
    elif kind == "factory":
        d.polygon([(X(-0.9), Y(0.9)), (X(-0.9), Y(-0.1)), (X(-0.4), Y(-0.4)), (X(-0.4), Y(-0.1)), (X(0.1), Y(-0.4)), (X(0.1), Y(-0.1)), (X(0.5), Y(-0.4)), (X(0.5), Y(-0.9)), (X(0.8), Y(-0.9)), (X(0.8), Y(0.9))], fill=col)
    elif kind == "oil":
        d.polygon([(X(0), Y(-0.95)), (X(0.6), Y(0.1)), (X(0.6), Y(0.4)), (X(0), Y(0.95)), (X(-0.6), Y(0.4)), (X(-0.6), Y(0.1))], fill=col)
    elif kind == "chip":
        d.rectangle([X(-0.55), Y(-0.55), X(0.55), Y(0.55)], fill=col)
        for v in (-0.3, 0, 0.3):
            for a, b, c, e in ((v, -0.55, v, -0.85), (v, 0.55, v, 0.85), (-0.55, v, -0.85, v), (0.55, v, 0.85, v)):
                d.line([X(a), Y(b), X(c), Y(e)], fill=col, width=lw)
    elif kind == "health":
        d.rectangle([X(-0.25), Y(-0.85), X(0.25), Y(0.85)], fill=col)
        d.rectangle([X(-0.85), Y(-0.25), X(0.85), Y(0.25)], fill=col)
    elif kind == "handshake":
        d.rounded_rectangle([X(-0.95), Y(-0.2), X(0.1), Y(0.3)], radius=r * S * 0.2, fill=col)
        d.rounded_rectangle([X(-0.1), Y(-0.3), X(0.95), Y(0.2)], radius=r * S * 0.2, outline=col, width=lw)
    elif kind == "space":
        d.polygon([(X(0), Y(-0.95)), (X(0.3), Y(-0.3)), (X(0.3), Y(0.5)), (X(-0.3), Y(0.5)), (X(-0.3), Y(-0.3))], fill=col)
        d.polygon([(X(-0.3), Y(0.1)), (X(-0.6), Y(0.7)), (X(-0.3), Y(0.5))], fill=col)
        d.polygon([(X(0.3), Y(0.1)), (X(0.6), Y(0.7)), (X(0.3), Y(0.5))], fill=col)
        d.polygon([(X(-0.15), Y(0.55)), (X(0.15), Y(0.55)), (X(0), Y(0.95))], fill=(240, 150, 30))
    elif kind == "people":
        for ox in (-0.5, 0.5):
            d.ellipse([X(ox - 0.22), Y(-0.75), X(ox + 0.22), Y(-0.3)], fill=col)
            d.pieslice([X(ox - 0.42), Y(-0.2), X(ox + 0.42), Y(0.9)], 180, 360, fill=col)
        d.ellipse([X(-0.25), Y(-0.55), X(0.25), Y(-0.05)], fill=col)
        d.pieslice([X(-0.48), Y(0.05), X(0.48), Y(1.1)], 180, 360, fill=col)
    elif kind == "flag":
        d.rectangle([X(-0.75), Y(-0.9), X(-0.6), Y(0.95)], fill=col)
        d.polygon([(X(-0.6), Y(-0.85)), (X(0.85), Y(-0.6)), (X(0.3), Y(-0.3)), (X(0.85), Y(0.05)), (X(-0.6), Y(0.1))], fill=col)
    elif kind == "game":
        d.rounded_rectangle([X(-0.95), Y(-0.45), X(0.95), Y(0.55)], radius=r * S * 0.4, fill=col)
        d.rectangle([X(-0.62), Y(-0.08), X(-0.22), Y(0.18)], fill=PAPER)
        d.rectangle([X(-0.55), Y(-0.15), X(-0.29), Y(0.25)], fill=PAPER)
        for ox, oy in ((0.45, -0.1), (0.65, 0.12)):
            d.ellipse([X(ox - 0.1), Y(oy - 0.1), X(ox + 0.1), Y(oy + 0.1)], fill=PAPER)
    else:  # "news": generic newspaper
        d.rectangle([X(-0.8), Y(-0.85), X(0.8), Y(0.85)], outline=col, width=lw)
        d.rectangle([X(-0.6), Y(-0.6), X(0.6), Y(-0.3)], fill=col)
        for v in (0, 0.25, 0.5):
            d.line([X(-0.6), Y(v), X(0.6), Y(v)], fill=col, width=lw)


# ---------------------------------------------------------------- map
LANDS = [
    [(-168, 66), (-162, 70), (-140, 70), (-128, 70), (-115, 73), (-95, 72), (-80, 73), (-62, 67), (-55, 52), (-66, 45), (-70, 41), (-76, 35), (-81, 31), (-80, 25), (-82, 27), (-84, 30), (-90, 29), (-97, 27), (-97, 22), (-92, 18), (-87, 21), (-88, 15), (-83, 10), (-79, 9), (-85, 11), (-92, 14), (-105, 20), (-110, 24), (-112, 31), (-117, 32), (-124, 40), (-124, 48), (-133, 56), (-146, 61), (-158, 58), (-165, 61)],
    [(-73, 78), (-60, 82), (-30, 83), (-20, 76), (-22, 70), (-40, 64), (-50, 61), (-54, 67), (-60, 76)],
    [(-79, 9), (-72, 12), (-62, 11), (-52, 5), (-50, 0), (-44, -3), (-35, -6), (-39, -14), (-41, -22), (-48, -26), (-53, -34), (-58, -39), (-65, -41), (-66, -48), (-69, -52), (-74, -53), (-72, -45), (-73, -37), (-71, -28), (-70, -18), (-76, -14), (-81, -6), (-80, 0), (-77, 4)],
    [(-10, 36), (-9, 43), (-2, 44), (-5, 48), (2, 51), (5, 53), (8, 54), (8, 57), (5, 58), (5, 62), (11, 64), (15, 69), (22, 71), (30, 70), (40, 67), (44, 68), (60, 69), (60, 55), (50, 47), (48, 42), (40, 41), (36, 41), (29, 41), (26, 40), (22, 37), (20, 40), (19, 42), (16, 44), (13, 45), (16, 41), (18, 40), (16, 38), (12, 38), (9, 44), (4, 43), (0, 39), (-2, 37), (-6, 36)],
    [(-6, 50), (1, 51), (2, 53), (-1, 55), (-2, 58), (-5, 58), (-6, 56), (-4, 54), (-5, 52)],
    [(-10, 52), (-6, 52), (-6, 55), (-8, 55), (-10, 54)],
    [(-24, 64), (-14, 64), (-14, 66), (-22, 66)],
    [(-85, 22), (-74, 20), (-77, 21), (-82, 23)],
    [(-17, 21), (-16, 27), (-10, 30), (-6, 36), (10, 37), (11, 33), (20, 31), (25, 32), (32, 31), (34, 28), (37, 22), (43, 12), (51, 12), (51, 10), (41, -2), (40, -10), (40, -16), (35, -24), (33, -29), (26, -34), (20, -35), (18, -31), (12, -18), (13, -12), (9, -1), (9, 4), (5, 6), (-3, 5), (-8, 4), (-13, 8), (-17, 14)],
    [(44, -25), (47, -25), (50, -15), (49, -12), (44, -17)],
    [(28, 41), (36, 36), (35, 32), (35, 29), (39, 21), (43, 13), (45, 13), (52, 16), (57, 19), (59, 22), (56, 26), (52, 24), (50, 26), (48, 30), (50, 30), (57, 27), (62, 25), (67, 24), (70, 21), (73, 16), (77, 8), (80, 10), (80, 15), (86, 20), (91, 22), (94, 17), (98, 16), (98, 8), (101, 3), (104, 1), (103, 6), (100, 13), (105, 9), (109, 12), (108, 17), (106, 20), (110, 21), (117, 23), (121, 29), (122, 31), (119, 35), (122, 37), (118, 39), (122, 41), (126, 38), (127, 35), (129, 35), (129, 40), (135, 43), (141, 47), (141, 53), (137, 55), (141, 59), (150, 59), (156, 57), (163, 60), (165, 62), (178, 64), (180, 68), (170, 70), (160, 70), (150, 72), (140, 72), (130, 71), (113, 74), (105, 78), (95, 76), (80, 73), (70, 73), (66, 70), (60, 69), (60, 55), (50, 47), (48, 42), (40, 41)],
    [(130, 31), (132, 34), (136, 35), (140, 35), (141, 38), (142, 41), (140, 41), (139, 38), (136, 37), (133, 36), (130, 33)],
    [(140, 42), (145, 43), (145, 44), (142, 45), (140, 43)],
    [(120, 22), (122, 25), (121, 25), (120, 23)],
    [(95, 5), (98, 4), (104, -2), (106, -6), (102, -4), (97, 1)],
    [(105, -6), (114, -7), (114, -8), (106, -7)],
    [(109, 1), (111, -3), (116, -4), (118, 1), (117, 7), (113, 3)],
    [(119, -5), (120, 1), (125, 1), (121, -1), (122, -5)],
    [(131, -1), (138, -2), (147, -6), (150, -10), (141, -9), (138, -8), (132, -4)],
    [(120, 18), (122, 18), (124, 12), (126, 7), (122, 7), (121, 14)],
    [(114, -22), (122, -18), (129, -15), (136, -12), (137, -16), (141, -17), (142, -11), (145, -15), (153, -25), (151, -34), (146, -39), (140, -38), (135, -35), (131, -31), (124, -34), (115, -34), (114, -26)],
    [(172, -34), (178, -38), (175, -42), (172, -41)],
    [(172, -41), (174, -41), (171, -46), (167, -46)],
    [(80, 6), (82, 7), (81, 10), (80, 9)],
]
LAT_TOP, LAT_BOT = 72.0, -48.0


def draw_map(d, x0, y0, w, h):
    def proj(lon, lat):
        return x0 + (lon + 180) / 360 * w, y0 + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * h

    d.rectangle(P(x0, y0, x0 + w, y0 + h), fill=SEA)
    for lon in range(-150, 180, 30):
        d.line(P(*proj(lon, LAT_TOP), *proj(lon, LAT_BOT)), fill=(200, 216, 228), width=1)
    for lat in (60, 30, 0, -30):
        d.line(P(*proj(-180, lat), *proj(180, lat)), fill=(200, 216, 228), width=1)
    for poly in LANDS:
        d.polygon([tuple(P(*proj(*pt))) for pt in poly], fill=LAND, outline=LAND_EDGE)

    # pins: anchor at the place, label circle relaxed away from its neighbours
    pins = []
    for s in STORIES:
        ax, ay = proj(s["lon"], s["lat"])
        rad = {1: 7.5, 2: 6.0, 3: 5.0}[s["tier"]]
        pins.append({"s": s, "ax": ax, "ay": ay, "x": ax, "y": ay, "r": rad})
    for _ in range(200):
        moved = False
        for i, a in enumerate(pins):
            for b in pins[i + 1:]:
                dx, dy = b["x"] - a["x"], b["y"] - a["y"]
                dist = (dx * dx + dy * dy) ** 0.5
                need = a["r"] + b["r"] + 0.8
                if dist < need:
                    push = min((need - dist) / 2, 2.0)
                    if dist > 0.01:
                        ux, uy = dx / dist, dy / dist
                    else:  # same place: split along a fixed, deterministic direction
                        ux, uy = 0.94, 0.34
                    a["x"] -= ux * push; a["y"] -= uy * push
                    b["x"] += ux * push; b["y"] += uy * push
                    moved = True
        for p in pins:  # keep inside the frame
            p["x"] = min(max(p["x"], x0 + p["r"] + 1), x0 + w - p["r"] - 1)
            p["y"] = min(max(p["y"], y0 + p["r"] + 1), y0 + h - p["r"] - 1)
        if not moved:
            break
    for p in pins:
        d.line(P(p["ax"], p["ay"], p["x"], p["y"]), fill=(90, 90, 90), width=S)
        d.ellipse(P(p["ax"] - 1.4, p["ay"] - 1.4, p["ax"] + 1.4, p["ay"] + 1.4), fill=INK)
    for p in sorted(pins, key=lambda p: -p["s"]["tier"]):
        col = TIER_COL[p["s"]["tier"]]
        r = p["r"]
        d.ellipse(P(p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r), fill=col, outline=PAPER, width=S)
        fnt = F["pin_lead"] if p["s"]["tier"] == 1 else F["pin"]
        d.text(P(p["x"], p["y"]), str(p["s"]["n"]), font=fnt, fill=(255, 255, 255), anchor="mm")
    d.rectangle(P(x0, y0, x0 + w, y0 + h), outline=RULE, width=S)


# ---------------------------------------------------------------- page
def tag(d, x, y, s):
    label = f"{s['place'].upper()}"
    col = REGION_COL[s["region"]]
    tw = d.textlength(label, font=F["tag"]) / S
    d.rectangle(P(x, y, x + tw + 6, y + 11), fill=col)
    d.text(P(x + 3, y + 1.5), label, font=F["tag"], fill=(255, 255, 255))
    return x + tw + 10


def render(out):
    img = Image.new("RGB", (W * S, H * S), PAPER)
    d = ImageDraw.Draw(img)
    STORIES.sort(key=lambda s: s["tier"])  # stable: numbers run leads, cards, list
    for i, s in enumerate(STORIES, 1):
        s["n"] = i
    leads = [s for s in STORIES if s["tier"] == 1]
    secs = [s for s in STORIES if s["tier"] == 2]
    alsos = [s for s in STORIES if s["tier"] == 3]

    # masthead
    d.rectangle(P(0, 0, W, 64), fill=NAVY)
    d.text(P(14, 8), "THE WORLD ON FRIDAY, 20 NOVEMBER 2026", font=F["mast"], fill=(255, 255, 255))
    regions = sorted({s["region"] for s in STORIES})
    sub = f"One day's world news in one page  |  {len(STORIES)} stories from {len(regions)} regions  |  numbers on the map match the stories"
    d.text(P(16, 46), sub, font=F["mast_sub"], fill=(200, 210, 230))

    # key-figure strip
    y = 70
    n = len(KEYFIGS)
    bw = (W - 16 - (n - 1) * 6) / n
    for i, (val, lab) in enumerate(KEYFIGS):
        x = 8 + i * (bw + 6)
        d.rectangle(P(x, y, x + bw, y + 44), fill=(255, 255, 255), outline=RULE, width=S)
        d.text(P(x + bw / 2, y + 15), val, font=F["kv"], fill=(170, 30, 40), anchor="mm")
        d.text(P(x + bw / 2, y + 34), lab, font=F["kl"], fill=INK, anchor="mm")

    # lead cards
    y = 120
    cw = (W - 16 - 12) / 3
    for i, s in enumerate(leads):
        x = 8 + i * (cw + 6)
        d.rectangle(P(x, y, x + cw, y + 150), fill=(255, 255, 255), outline=RULE, width=S)
        d.rectangle(P(x, y, x + 76, y + 150), fill=(244, 236, 226))
        icon(d, s["icon"], x + 38, y + 68, 33, REGION_COL[s["region"]])
        d.ellipse(P(x + 6, y + 6, x + 24, y + 24), fill=TIER_COL[1])
        d.text(P(x + 15, y + 15), str(s["n"]), font=F["pin_lead"], fill=(255, 255, 255), anchor="mm")
        d.text(P(x + 38, y + 132), s["region"], font=F["small"], fill=MUTED, anchor="mm")
        tx = x + 84
        tag(d, tx, y + 7, s)
        yy = text_block(d, tx, y + 22, s["head"], F["lead_h"], cw - 92, 3, INK, 17)
        yy = text_block(d, tx, yy + 3, s["detail"], F["lead_d"], cw - 92, 6, (50, 54, 64), 12)
        d.text(P(tx, y + 138), f"Source: {s['src']}", font=F["small"], fill=MUTED)

    # UTC timeline strip
    ty0 = 276
    d.rectangle(P(8, ty0, W - 8, ty0 + 32), fill=(236, 240, 247), outline=RULE, width=S)
    d.text(P(14, ty0 + 9), "FRIDAY, UTC", font=F["sect"], fill=NAVY)
    step = (W - 16 - 84) / len(TIMELINE)
    for i, (when, what) in enumerate(TIMELINE):
        tx = 84 + i * step
        d.ellipse(P(tx - 3, ty0 + 6, tx + 3, ty0 + 12), fill=(200, 30, 40))
        d.text(P(tx + 6, ty0 + 3), when, font=F["box_h"], fill=(170, 30, 40))
        text_block(d, tx, ty0 + 14, what, F["small"], step - 6, 2, INK, 8.5)

    # map + region tally
    my, mw, mh = 314, 560, 186.7
    d.text(P(8, my), "WHERE IT HAPPENED", font=F["sect"], fill=NAVY)
    draw_map(d, 8, my + 14, mw, mh)
    ty = my + 14 + mh + 6
    x = 8
    for reg in REGION_COL:
        c = sum(1 for s in STORIES if s["region"] == reg)
        if not c:
            continue
        seg = mw * c / len(STORIES)
        d.rectangle(P(x, ty, x + seg - 1, ty + 14), fill=REGION_COL[reg])
        lab = f"{reg} {c}" if seg > 70 else str(c)
        d.text(P(x + seg / 2, ty + 7), lab, font=F["tag"], fill=(255, 255, 255), anchor="mm")
        x += seg

    # secondary cards (right of the map)
    sx, sy = 576, my
    d.text(P(sx, sy), "ALSO MAKING NEWS", font=F["sect"], fill=NAVY)
    cols, rows = 2, (len(secs) + 1) // 2
    gw = (W - 8 - sx - 6) / cols
    gh = (mh + 50) / max(rows, 1)
    sec_bottom = sy + 14 + rows * gh
    for i, s in enumerate(secs):
        cx = sx + (i % cols) * (gw + 6)
        cy = sy + 14 + (i // cols) * gh
        d.rectangle(P(cx, cy, cx + gw, cy + gh - 4), fill=(255, 255, 255), outline=RULE, width=S)
        icon(d, s["icon"], cx + 15, cy + (gh - 4) / 2, 10, REGION_COL[s["region"]])
        d.ellipse(P(cx + 2, cy + 2, cx + 13, cy + 13), fill=TIER_COL[2])
        d.text(P(cx + 7.5, cy + 7.5), str(s["n"]), font=F["pin"], fill=(255, 255, 255), anchor="mm")
        tx = cx + 30
        d.text(P(tx, cy + 2), s["place"].upper(), font=F["tag"], fill=REGION_COL[s["region"]])
        yy = text_block(d, tx, cy + 10, s["head"], F["sec_h"], gw - 34, 1, INK, 12)
        text_block(d, tx, yy, s["detail"], F["sec_d"], gw - 34, 2, (60, 64, 74), 9)

    # also list
    ay = max(ty + 22, sec_bottom + 6)
    d.line(P(8, ay - 4, W - 8, ay - 4), fill=RULE, width=S)
    d.text(P(8, ay), "MORE FROM THE DAY", font=F["sect"], fill=NAVY)
    ncol = 3
    colw = (W - 16 - (ncol - 1) * 10) / ncol
    per = (len(alsos) + ncol - 1) // ncol
    box_top = 958
    for i, s in enumerate(alsos):
        c, r = divmod(i, per)
        x = 8 + c * (colw + 10)
        line_h = (box_top - ay - 18) / max(per, 1)
        dl = 2 if line_h >= 40 else 1
        yy = ay + 15 + r * line_h
        d.ellipse(P(x, yy + 1, x + 13, yy + 14), fill=TIER_COL[3])
        d.text(P(x + 6.5, yy + 7.5), str(s["n"]), font=F["pin"], fill=(255, 255, 255), anchor="mm")
        head = f"{s['place']}: {s['head']}"
        text_block(d, x + 17, yy, head, F["also_b"], colw - 19, 1, INK, 13)
        hw = d.textlength(head, font=F["also_b"]) / S
        src = f"  {s['src']}"
        if 17 + hw + d.textlength(src, font=F["small"]) / S <= colw - 2:
            d.text(P(x + 17 + hw, yy + 2.5), src, font=F["small"], fill=(150, 120, 60))
        text_block(d, x + 17, yy + 14, s["detail"], F["also"], colw - 19, dl, (60, 64, 74), 12)

    # date-check box + footer
    d.rectangle(P(8, box_top, W - 8, box_top + 42), fill=(255, 250, 225), outline=(200, 160, 40), width=S)
    d.text(P(16, box_top + 4), "DATE CHECK", font=F["box_h"], fill=(140, 90, 0))
    text_block(d, 90, box_top + 4, DATE_LINE, F["box"], W - 112, 1, INK, 11)
    text_block(d, 90, box_top + 16, MARKETS, F["box"], W - 112, 1, INK, 11)
    text_block(d, 90, box_top + 28, "Sources: " + SOURCES, F["box"], W - 112, 1, MUTED, 11)
    d.text(P(W / 2, H - 9), "Compiled 20 Nov 2026 from published reports; no event shown predates 20 November 2026.", font=F["small"], fill=MUTED, anchor="mm")

    img = img.resize((W, H), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out


if __name__ == "__main__":
    p = render(Path(__file__).resolve().parent / "assets" / "entry.png")
    print(p, p.stat().st_size)
