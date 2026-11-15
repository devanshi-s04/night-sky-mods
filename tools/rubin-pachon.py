#!/usr/bin/env python3
"""Builds the Rubin on Cerro Pachon scene for the night-sky mod.

Writes hooks/scenes/rubin-pachon.ts (one exported function returning the SVG) and, with --svg PATH, the bare SVG
for previewing. Pure stdlib, seeded, so every run gives the same scene.

The look: an ASCII Vera C. Rubin Observatory on the right, moonlit silver with cyan hints (the Simonyi camera's
teal glows in the dome slit), Gemini South's dome peeking out on a lower shoulder, layered Andes ridges fading into
the last of twilight, a few stray dotted clouds, a navy-to-violet-to-peach ombre sky with a dotted purple Milky Way,
twinkling stars, and a slow comet crossing from the top right toward the lower left every 20 seconds. The dome
turns now and then, as Rubin slews to a new field.
"""
import math
import random
import sys
from pathlib import Path

W, H = 1600, 1000
HORIZON = 790
rng = random.Random(1907)  # Vera Rubin's birth year


def f(v):
    """A compact number."""
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def hash01(x, y, salt):
    h = (x * 374761393 + y * 668265263 + salt * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 15)) * 0x85EBCA6B) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h / 4294967296


def smooth(t):
    return t * t * (3 - 2 * t)


def noise2(x, y, scale, salt):
    gx, gy = math.floor(x / scale), math.floor(y / scale)
    fx, fy = smooth(x / scale - gx), smooth(y / scale - gy)
    a = hash01(gx, gy, salt) * (1 - fx) + hash01(gx + 1, gy, salt) * fx
    b = hash01(gx, gy + 1, salt) * (1 - fx) + hash01(gx + 1, gy + 1, salt) * fx
    return a * (1 - fy) + b * fy


def noise1(x, scale, salt):
    return noise2(x, 0, scale, salt)


def anim(spec):
    """An animation set on the element itself. The desktop app runs these and not ones set by a class rule."""
    return f' style="animation:{spec}"'


def dots_path(points):
    """Round dots as one path of zero-length strokes: `M x y h0`, on whole pixels to keep the scene under the size cap."""
    out, px, py = [], None, None
    for x, y in points:
        x, y = round(x), round(y)
        if px is None:
            out.append(f"M{x} {y}h0")
        else:
            dx, dy = x - px, y - py
            out.append(f"m{dx}{'' if dy < 0 else ' '}{dy}h0")  # relative: short numbers, and a minus needs no space
        px, py = x, y
    return "".join(out)


# ---------------------------------------------------------------- sky



# ---------------------------------------------------------------- times of day
# `--time night|sunset|sunrise|day` picks the palette; sunset (the last of twilight) is the original look.
# Each sets the sky, the glow on the horizon (and where it sits), the ridges, the valley haze, the clouds and the
# ground, and how strongly the Milky Way, the stars and the comet show (0 leaves them out).

TIMES = {
    "sunset": {
        "sky": [
            (0.00, "#050a26"), (0.22, "#0a174c"), (0.42, "#132462"), (0.56, "#1d276a"), (0.60, "#2b296e"),
            (0.66, "#46296f"), (0.70, "#6a3376"), (0.73, "#9a477c"), (0.755, "#cc627a"), (0.78, "#ee8f72"),
            (0.81, "#f6b27a"), (1.00, "#f8c58a"),
        ],
        "glow": ("#ffb07a", ".55", "#e2708a", ".25", "#7a3c8c"), "glow_x": 560,
        "ridges": [
            ("#7c4a86", "#5a3a7a", "#f2a38c"), ("#4c3a7c", "#35306a", "#d98aa8"),
            ("#2c2a62", "#211f50", "#a98ad0"), ("#181a44", "#10112e", None),
        ],
        "haze": ("#c77aa0", "#b874a8", "#8a5aa8"),
        "clouds": ("#8a7cc8", "#c18fc6", "#f7ae98"),
        "rock": ("#1a1f4a", "#11143a", "#080a22"),
        "milky_way": 1, "stars": 1, "comet": True,
    },
    "night": {
        "sky": [
            (0.00, "#010309"), (0.25, "#040922"), (0.50, "#081236"), (0.66, "#0e1844"), (0.74, "#151e50"),
            (0.79, "#1d2558"), (0.82, "#232b5e"), (1.00, "#262d60"),
        ],
        "glow": ("#5a6cc0", ".3", "#36448e", ".16", "#1a2058"), "glow_x": 560,
        "ridges": [
            ("#262b5e", "#1d2150", "#7c8cd0"), ("#1c2050", "#161a44", "#6272b8"),
            ("#141838", "#10132e", "#4c5a9c"), ("#0c0e26", "#080a1c", None),
        ],
        "haze": ("#3a4a8a", "#34428a", "#24306a"),
        "clouds": ("#3c467e", "#5e6eaa", "#aebce4"),
        "rock": ("#151a40", "#0e1134", "#06081c"),
        "milky_way": 1, "stars": 1, "comet": True,
    },
    "sunrise": {
        "sky": [
            (0.00, "#0a1640"), (0.25, "#173270"), (0.45, "#2b4f8e"), (0.60, "#4d6aa6"), (0.68, "#7d86b8"),
            (0.72, "#b294b8"), (0.75, "#e3a3a8"), (0.78, "#f6bf98"), (0.81, "#ffd89a"), (1.00, "#ffe6b0"),
        ],
        "glow": ("#ffe2a0", ".6", "#ffb08a", ".28", "#c08ab0"), "glow_x": 1150,
        "ridges": [
            ("#8a6f9a", "#6a5a8a", "#ffd2a0"), ("#5a5a8c", "#45487a", "#f2b4a0"),
            ("#363c70", "#2a2f60", "#b4a4d4"), ("#1c2048", "#121634", None),
        ],
        "haze": ("#e8a8b0", "#e2a4b4", "#a88ac0"),
        "clouds": ("#9a8cc0", "#f0b4b8", "#ffe2a8"),
        "rock": ("#1e2450", "#141a42", "#0a0e28"),
        "milky_way": 0.22, "stars": 0.45, "comet": True,
    },
    "day": {
        "sky": [
            (0.00, "#1f5bab"), (0.35, "#3878c8"), (0.60, "#68a0da"), (0.74, "#9cc4e8"), (0.79, "#c2dbee"),
            (1.00, "#d8e7f1"),
        ],
        "glow": ("#ffffff", ".4", "#eaf3ff", ".18", "#cfe2f5"), "glow_x": 900,
        "ridges": [
            ("#8ea9cd", "#7d9ac3", "#e2edf8"), ("#7290bb", "#617fae", "#cfdff2"),
            ("#56739f", "#48618f", "#acc4e2"), ("#34476f", "#27375b", None),
        ],
        "haze": ("#e2eef9", "#e6f0fa", "#c8daf0"),
        "clouds": ("#b4c4de", "#e2eaf5", "#ffffff"),
        "rock": ("#34446e", "#26355c", "#18244a"),
        # The rock pile and the ground behind Rubin, lit to match the daytime summit instead of night navy.
        "rockfront": ("#46567f", "#3a4a76", "#34446e"),
        "ground": "#34446e",
        "milky_way": 0, "stars": 0, "comet": False,
    },
}
TIME = sys.argv[sys.argv.index("--time") + 1] if "--time" in sys.argv else "sunset"
PAL = TIMES[TIME]


def sky():
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in PAL['sky'])
    defs = f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient>'
    defs += (
        '<radialGradient id="dusk" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="{0}" stop-opacity="{1}"/>'
        '<stop offset=".45" stop-color="{2}" stop-opacity="{3}"/>'
        '<stop offset="1" stop-color="{4}" stop-opacity="0"/></radialGradient>'.format(*PAL["glow"]) +
        '<radialGradient id="mwglow" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#b08cff" stop-opacity=".62"/>'
        '<stop offset=".5" stop-color="#7c5fd6" stop-opacity=".26"/>'
        '<stop offset="1" stop-color="#4a3c9a" stop-opacity="0"/></radialGradient>'
    )
    body = f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
    body += f'<ellipse cx="{PAL["glow_x"]}" cy="{HORIZON + 10}" rx="1100" ry="230" fill="url(#dusk)"{anim("dusk 40s ease-in-out infinite alternate")}/>'
    return defs, body


# ---------------------------------------------------------------- Milky Way

# The band rises steeply up the left side, beside the chat column rather than behind it.
MW_A = (-120, 900)
MW_B = (820, -200)


def milky_way():
    ax, ay = MW_A
    bx, by = MW_B
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    angle = math.degrees(math.atan2(dy, dx))
    cx, cy = (ax + bx) / 2, (ay + by) / 2

    shades = {
        "core": ("#f7efff", 2.0, []),
        "lilac": ("#cdb6ff", 1.8, []),
        "violet": ("#9a82e8", 1.6, []),
        "orchid": ("#eeaee6", 1.7, []),
        "blue": ("#9cbcff", 1.5, []),
        "rose": ("#ffb8d2", 1.6, []),
        "aqua": ("#a6eef0", 1.5, []),
        "gold": ("#ffe2b0", 1.7, []),
    }
    pitch = 7
    for gy in range(-20, HORIZON - 40, pitch):
        for gx in range(0, W, pitch):
            jx = gx + (hash01(gx, gy, 3) - 0.5) * 5
            jy = gy + (hash01(gx, gy, 4) - 0.5) * 5
            rx, ry = jx - ax, jy - ay
            along = (rx * ux + ry * uy) / length
            across = rx * nx + ry * ny
            if along < -0.05 or along > 1.05:
                continue
            width = 245 + 90 * noise1(along * 900, 140, 9)
            wobble = 40 * (noise1(along * 900, 260, 11) - 0.5)
            a = (across - wobble) / width
            density = math.exp(-a * a * 1.6)
            clump = noise2(jx, jy, 46, 5) * 0.65 + noise2(jx, jy, 15, 6) * 0.35
            density *= 0.35 + 0.95 * clump
            # A dark dust lane just off the spine.
            lane = math.exp(-((a - 0.18) / 0.16) ** 2) * (0.55 + 0.45 * noise2(jx, jy, 30, 8))
            density *= 1 - 0.75 * lane
            # Fade into the twilight near the horizon and at the top.
            density *= min(1, max(0, (HORIZON - 30 - jy) / 140))
            if hash01(gx, gy, 7) > density * 0.85:
                continue
            pick = hash01(gx, gy, 12)
            if density > 0.75:
                key = "core" if pick < 0.5 else ("lilac" if pick < 0.75 else "gold")
            elif density > 0.45:
                key = "lilac" if pick < 0.4 else ("orchid" if pick < 0.6 else ("violet" if pick < 0.8 else "rose"))
            else:
                key = "violet" if pick < 0.45 else ("blue" if pick < 0.7 else ("aqua" if pick < 0.85 else "orchid"))
            if jy > HORIZON - 260 and pick < 0.35:
                key = "orchid" if pick < 0.2 else "rose"
            shades[key][2].append((jx, jy))

    body = (
        f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(length / 2)}" ry="400" fill="url(#mwglow)" '
        f'transform="rotate({f(angle)} {f(cx)} {f(cy)})"/>'
    )
    groups = ["", ""]
    for i, (key, (colour, width, pts)) in enumerate(shades.items()):
        # Alternate dots go to the two breathing groups; raster order keeps the relative path short.
        for g, chunk in enumerate((pts[0::2], pts[1::2])):
            if chunk:
                breathe = anim("mw 36s ease-in-out infinite alternate") if g == 0 else anim("mw 47s ease-in-out infinite alternate-reverse")
                groups[g] += (
                    f'<path d="{dots_path(chunk)}" stroke="{colour}" stroke-width="{width}" '
                    f'stroke-linecap="round" stroke-opacity="{0.95 if key in ("core", "lilac", "gold") else 0.78}"{breathe}/>'
                )
    body += groups[0] + groups[1]
    count = sum(len(v[2]) for v in shades.values())
    return body, count


# ---------------------------------------------------------------- stars

STAR_COLOURS = ["#ffffff", "#ffffff", "#ffffff", "#d6e6ff", "#ffe9cf", "#eadbff"]
TWINKLE_CLASSES = 6


def stars():
    plain = {}
    twinkle = [dict() for _ in range(TWINKLE_CLASSES)]
    sparkles = []
    placed = 0
    while placed < 400:
        x = rng.uniform(0, W)
        y = rng.uniform(0, HORIZON - 40)
        # Fewer stars low in the twilight.
        if rng.random() > min(1, (HORIZON - 40 - y) / 260):
            continue
        placed += 1
        colour = rng.choice(STAR_COLOURS)
        size = rng.choice((1.4, 1.6, 1.9, 2.2, 2.6)) if rng.random() < 0.85 else 3.1
        target = twinkle[rng.randrange(TWINKLE_CLASSES)] if rng.random() < 0.45 else plain
        target.setdefault((colour, size), []).append((x, y))
    # A denser patch of sky above Rubin, clear of the Milky Way.
    for _ in range(130):
        x, y = rng.uniform(960, W), rng.uniform(0, 430)
        colour = rng.choice(STAR_COLOURS)
        size = rng.choice((1.4, 1.6, 1.9, 2.2)) if rng.random() < 0.9 else 2.8
        target = twinkle[rng.randrange(TWINKLE_CLASSES)] if rng.random() < 0.5 else plain
        target.setdefault((colour, size), []).append((x, y))
    for _ in range(15):
        x = rng.uniform(40, W - 40)
        y = rng.uniform(30, HORIZON - 260)
        sparkles.append((x, y, rng.choice(("#ffffff", "#e8f4ff", "#fff1d6")), rng.randrange(TWINKLE_CLASSES)))

    def twinkle_of(i):
        return anim(f"tw {3.2 + i * 0.9:.1f}s ease-in-out -{i * 1.3:.1f}s infinite")

    def paths(buckets, extra=""):
        out = ""
        for (colour, size), pts in buckets.items():
            out += f'<path d="{dots_path(sorted(pts, key=lambda p: (p[1], p[0])))}" stroke="{colour}" stroke-width="{size}" stroke-linecap="round"{extra}/>'
        return out

    body = f'<g opacity=".8">{paths(plain)}</g>'
    for i, buckets in enumerate(twinkle):
        body += paths(buckets, twinkle_of(i))
    for x, y, colour, cls in sparkles:
        # A small four-point sparkle, the pixel-art way.
        body += (
            f'<path d="M{f(x - 1.3)} {f(y - 6)}h2.6v12h-2.6zM{f(x - 6)} {f(y - 1.3)}h12v2.6h-12z" fill="{colour}"{twinkle_of(cls)}/>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="3.4" fill="{colour}" fill-opacity=".35"{twinkle_of(cls)}/>'
        )
    return body


# ---------------------------------------------------------------- ridges and clouds

def ridge_points(base, amp, scale, salt, x0=-20, x1=W + 20, step=10):
    pts = []
    for x in range(x0, x1 + step, step):
        n = noise1(x, scale, salt) * 0.65 + noise1(x, scale / 2.7, salt + 1) * 0.25 + noise1(x, scale / 8, salt + 2) * 0.1
        pts.append((x, base - amp * n))
    return pts


RIDGES = [
    # base, amplitude, scale, salt, top colour, foot colour, rim colour
    (770, 60, 260, 21), (800, 70, 210, 31), (845, 80, 180, 41), (905, 70, 150, 51),
]
RIDGES = [shape + colours for shape, colours in zip(RIDGES, PAL["ridges"])]


def ridges():
    defs, body = "", ""
    for i, (base, amp, scale, salt, top, foot, rim) in enumerate(RIDGES):
        pts = ridge_points(base, amp, scale, salt)
        defs += (
            f'<linearGradient id="r{i}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{foot}"/></linearGradient>'
        )
        d = f"M{pts[0][0]} {H}" + "".join(f"L{x} {f(y)}" for x, y in pts) + f"L{pts[-1][0]} {H}Z"
        body += f'<path d="{d}" fill="url(#r{i})"/>'
        if rim:
            # Rim light from the twilight: a few rows of dots along the crest.
            rim_pts = []
            for x, y in pts:
                for k in range(3):
                    if hash01(x, k, salt) < 0.7 - 0.2 * k:
                        rim_pts.append((x + (hash01(x, k, salt + 3) - 0.5) * 8, y + 2 + k * 4))
            body += f'<path d="{dots_path(rim_pts)}" stroke="{rim}" stroke-width="1.6" stroke-linecap="round" opacity="{0.55 - i * 0.12}"/>'
        if i < len(RIDGES) - 1:
            # Haze pooled in the valley in front of this ridge.
            body += f'<rect y="{base - 10}" width="{W}" height="60" fill="url(#haze)" opacity="{0.5 - i * 0.12}"/>'
    defs += (
        '<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="{0}" stop-opacity="0"/><stop offset=".5" stop-color="{1}" stop-opacity=".35"/>'
        '<stop offset="1" stop-color="{2}" stop-opacity="0"/></linearGradient>'.format(*PAL["haze"])
    )
    return defs, body


CLOUDS = [
    # centre x, centre y, width, height, drift class. Low, drifting in front of the domes and Rubin.
    (240, 878, 220, 22, "c3"),  # across SOAR
    (120, 805, 170, 20, "c1"),
    (430, 850, 160, 18, "c2"),
    (765, 848, 200, 22, "c1"),  # across Gemini
    (590, 795, 150, 18, "c3"),
    (1090, 760, 220, 24, "c2"),  # across Rubin's lower slabs
    (1340, 775, 200, 22, "c3"),
    (1480, 745, 150, 18, "c1"),  # by Rubin's pier
    (1300, 872, 470, 46, "c2"),  # a big, fluffy one rolling over the rubble under Rubin
]


def clouds(items=None, n0=0):
    """Stray clouds as loose dots: puffy lobes on a flat, sunset-lit base, thinning out at their edges."""
    body = ""
    for n, (cx, cy, w, h, cls) in enumerate(CLOUDS if items is None else items, n0):
        crng = random.Random(500 + n)
        lobes = []
        nl = max(7, int(w / 42))
        for k in range(nl):
            t = (k + 0.5) / nl
            lx = cx - w / 2 + t * w + crng.uniform(-w * 0.05, w * 0.05)
            hump = math.sin(t * math.pi) ** 0.8
            lr = h * (0.45 + 0.75 * hump) * crng.uniform(0.75, 1.15)
            lobes.append((lx, cy - lr * 0.55, lr * 1.35, lr))
        lobes.append((cx, cy + h * 0.05, w * 0.55, h * 0.32))  # the flat base
        lit, mid, shade = [], [], []
        pitch = 5
        for gy in range(int(cy - h * 2.2), int(cy + h * 0.6), pitch):
            for gx in range(int(cx - w * 0.8), int(cx + w * 0.8), pitch):
                x = gx + (hash01(gx, gy, 90 + n) - 0.5) * 3.2
                y = gy + (hash01(gx, gy, 95 + n) - 0.5) * 3.2
                inside = max(1 - ((x - lx) / lw) ** 2 - ((y - ly) / lh) ** 2 for lx, ly, lw, lh in lobes)
                if y > cy + h * 0.3:
                    inside = -1  # a flat underside
                if inside <= 0:
                    continue
                keep = min(1, inside * 2.6) * (0.55 + 0.45 * noise2(x, y, 14, 60 + n))
                if hash01(gx, gy, 70 + n) > keep:
                    continue
                v = (y - (cy - h * 1.6)) / (h * 1.9)
                (lit if v > 0.72 else mid if v > 0.38 else shade).append((x, y))
        # Three speeds, each cloud starting part-way through its swing so they never move as one.
        drift = anim({
            "c1": f"drift 46s ease-in-out -{n * 7}s infinite alternate",
            "c2": f"drift 63s ease-in-out -{n * 9}s infinite alternate-reverse",
            "c3": f"drift 38s ease-in-out -{n * 5}s infinite alternate",
        }[cls])
        body += (
            f'<path d="{dots_path(shade)}" stroke="{PAL["clouds"][0]}" stroke-width="2.1" stroke-linecap="round" stroke-opacity=".66"{drift}/>'
            f'<path d="{dots_path(mid)}" stroke="{PAL["clouds"][1]}" stroke-width="2.1" stroke-linecap="round" stroke-opacity=".76"{drift}/>'
            f'<path d="{dots_path(lit)}" stroke="{PAL["clouds"][2]}" stroke-width="2.1" stroke-linecap="round" stroke-opacity=".88"{drift}/>'
        )
    return body


# ---------------------------------------------------------------- Cerro Pachon, Gemini South and Rubin

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
CW = 7.2  # one glyph's width at 12px (0.6em)
LH = 13  # line height at 12px

# The summit's outline, left to right, in scene units. Gemini's shoulder sits on the left, Rubin's on the right.
SUMMIT_KEYS = [
    (480, 1000), (550, 950), (610, 902), (650, 866), (678, 846), (700, 840), (842, 840), (866, 828),
    (892, 814), (918, 804), (940, 800), (1600, 800), (1700, 804), (2200, 820), (2200, 1000),
]


def rough(keys):
    """The key outline with a rocky edge, except where a building stands."""
    out = [keys[0]]
    for (x0, y0), (x1, y1) in zip(keys, keys[1:]):
        steps = max(1, int(abs(x1 - x0) / 12))
        for i in range(1, steps + 1):
            t = i / steps
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            flat = 696 <= x <= 846 or 936 <= x <= 1700 or x >= 2200 or y >= 1000
            if not flat and i < steps:
                y += (noise1(x, 70, 77) - 0.5) * 46 + (noise1(x, 18, 79) - 0.5) * 14 + (hash01(int(x), 0, 78) - 0.5) * 5
            out.append((round(x), round(y)))
    return out


SUMMIT = rough(SUMMIT_KEYS)


def summit_y(x):
    for (x0, y0), (x1, y1) in zip(SUMMIT, SUMMIT[1:]):
        if x0 <= x <= x1 and x1 != x0:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None


def summit():
    defs = (
        '<linearGradient id="rock" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="{0}"/><stop offset=".5" stop-color="{1}"/><stop offset="1" stop-color="{2}"/></linearGradient>'.format(*PAL["rock"]) +
        f'<clipPath id="hill"><path d="M{"L".join(f"{x} {y}" for x, y in SUMMIT)}Z"/></clipPath>'
    )
    body = f'<path d="M{"L".join(f"{x} {y}" for x, y in SUMMIT)}Z" fill="url(#rock)"/>'
    # Rubble: rows of sparse glyphs, clipped to the hill.
    rows = []
    y = 810
    r = 0
    while y < 1000:
        line = ""
        for c in range(0, int((1720 - 480) / CW)):
            v = hash01(c, r, 80)
            line += ".,:;'`"[int(v * 6)] if v < 0.18 else " "
        rows.append(f'<tspan x="480" y="{f(y)}">{line.rstrip()}</tspan>')
        y += 2 * LH
        r += 1
    if True:
        body += f'<text clip-path="url(#hill)" class="glyph" fill="#3a4380" opacity=".6">{"".join(rows)}</text>'
    # The crest in glyphs, picking up moonlight.
    crest = ""
    x = 500.0
    while x < 1640:
        y0, y1 = summit_y(x), summit_y(x + CW)
        if y0 is None or y1 is None:
            break
        slope = (y1 - y0) / CW
        g = "_" if abs(slope) < 0.25 else ("/" if slope < 0 else "\\")
        yy = (y0 + y1) / 2 + (2 if g == "_" else 5)
        crest += f'<tspan x="{f(x)}" y="{f(yy - (8 if g == "_" else 0))}">{esc(g)}</tspan>'
        x += CW
    body += f'<text class="glyph" fill="#8fa8d0" opacity=".75">{crest}</text>'
    return defs, body


GEMINI = [
    r"     .-''''-.     ",
    r"   .'  |  |  '.   ",
    r"  /    |  |    \  ",
    r" |_____|__|_____| ",
    r" |  []      []  | ",
    r"_|______________|_",
]


def gemini():
    x0, base = 704, 837
    top = base - LH * (len(GEMINI) - 1)
    rows = "".join(
        f'<tspan x="{x0}" y="{f(top + i * LH)}">{esc(line)}</tspan>' for i, line in enumerate(GEMINI)
    )
    sil = (
        f'<path d="M{f(x0 + 1.5 * CW)} {base}L{f(x0 + 1.5 * CW)} {f(top + 2 * LH)}'
        f'Q{f(x0 + 9 * CW)} {f(top - LH * 1.6)} {f(x0 + 16.5 * CW)} {f(top + 2 * LH)}L{f(x0 + 16.5 * CW)} {base}Z" fill="#141a40"/>'
    )
    return sil + text_rows(GEMINI, x0, top, 'glyph bold', 'url(#moonlit)')


# SOAR, Gemini's small neighbour on Cerro Pachon, set on the nearest ridge at the left, where the chat leaves room.
SOAR = [
    r"    .-''''-.    ",
    r"  .'   ||   '.  ",
    " /_____||_____\\ ",
    r" |  []    []  | ",
    r"_|____________|_",
]


def soar():
    x0, base = 186, 868
    top = base - LH * (len(SOAR) - 1)
    sil = (
        f'<path d="M{f(x0 + 1.5 * CW)} {base + 6}L{f(x0 + 1.5 * CW)} {f(top + 2 * LH)}'
        f'Q{f(x0 + 8 * CW)} {f(top - LH * 1.7)} {f(x0 + 14.5 * CW)} {f(top + 2 * LH)}L{f(x0 + 14.5 * CW)} {base + 6}Z" fill="#141a40"/>'
    )
    # A thin warm line of light down the open slit, breathing like Rubin's camera.
    slit = (
        f'<rect x="{f(x0 + 7.45 * CW)}" y="{f(top + 2)}" width="{f(1.1 * CW)}" height="{f(LH * 1.9)}" '
        f'fill="#ffd9a8" fill-opacity=".35"{anim("cam 5s ease-in-out infinite alternate")}/>'
    )
    if TIME == "day":
        slit = ""  # no lamplight to see by day
    return sil + slit + text_rows(SOAR, x0, top, 'glyph bold', 'url(#moonlit)')


# Rubin, side-on, traced from the NOIRLab night photo (pixel coordinates there, scaled by 0.8 here) and turned into
# ASCII on a fixed grid. The body is stepped: the top slab is the shortest, under a sloping roof, and each slab below
# reaches further left; under them an inverted wedge tapers down to the ground floor. On the right a raised block and
# the round pier, and on the pier the dome: a tall back wall on the right, a front that slants back so the open slit
# faces the sky, a dark shutter wing beside it, and the camera's cyan glow inside. Rocks pile up in front of the
# right half, as they do on the summit.

RUBIN_X = 960  # scene x of the photo's x = 135
RUBIN_GROUND = 800  # scene y of the photo's y = 790
SCALE = 0.8


def P(px, py):
    """A point from the photo, in local units: x right from the prow, y up from the ground."""
    return ((px - 135) * SCALE, (790 - py) * SCALE)


def poly(*pts):
    return [P(*p) for p in pts]


FACES = [
    # name, polygon (local), fill colour, texture; back to front
    ("pier", poly((655, 700), (655, 445), (832, 445), (832, 700)), "#141a40", "pier"),
    ("block", poly((498, 545), (520, 474), (770, 470), (770, 545)), "#171e48", "block"),
    ("floor", poly((150, 790), (150, 712), (250, 712), (250, 790)), "#11163a", "floor"),
    ("wedge", poly((172, 705), (600, 662), (522, 790), (292, 790)), "#10153a", "wedge"),
    ("slab3", poly((135, 708), (148, 664), (740, 662), (740, 704)), "#141a40", "slab3"),
    ("slab2", poly((160, 664), (182, 620), (740, 618), (740, 662)), "#161d45", "slab2"),
    ("slab1", poly((196, 620), (336, 545), (740, 545), (740, 618)), "#1a2250", "slab1"),
]
# The dome: front slanting back from the bottom left, flat-ish top, tall back wall.
DOME = poly((600, 448), (644, 330), (800, 318), (834, 326), (834, 448))
DOME_BAND = poly((604, 448), (608, 436), (834, 436), (834, 448))
SHUTTER = poly((607, 440), (647, 336), (661, 336), (621, 440))
SLIT = poly((626, 432), (664, 344), (732, 340), (698, 432))
DOME_COLOUR = "#161d46"

ROWS = int(math.ceil(392 / LH)) + 1
COLS = int(math.ceil(560 / CW)) + 1


def inside(pg, x, y):
    hit = False
    for (x0, y0), (x1, y1) in zip(pg, pg[1:] + pg[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            hit = not hit
    return hit


def cell_centre(c, r):
    """Local coordinates of a grid cell's centre; row 0 is the top."""
    return (c + 0.5) * CW, (ROWS - r - 0.5) * LH


def nearest_slope(pg, x, y):
    """The slope of the edge nearest (x, y), and that edge's height at x."""
    best, slope, at = 1e9, 0.0, y
    for (x0, y0), (x1, y1) in zip(pg, pg[1:] + pg[:1]):
        dx, dy = x1 - x0, y1 - y0
        t = max(0, min(1, ((x - x0) * dx + (y - y0) * dy) / (dx * dx + dy * dy)))
        d = math.hypot(x - (x0 + t * dx), y - (y0 + t * dy))
        if d < best:
            best = d
            slope = dy / dx if dx else 1e9
            at = y0 + (x - x0) * dy / dx if dx else y
    return slope, at


def texture(kind, c, r, span, frame=None):
    top, bottom = span
    mid = (top + bottom) // 2
    if kind == "slab1":
        return "." if r == bottom - 1 and c % 2 == 0 else " "
    if kind in ("slab2", "slab3"):
        return "=" if r == mid else " "
    if kind == "floor":
        return {4: "[", 5: "]"}.get(c % 7, " ") if r == mid else " "
    if kind == "block":
        return {5: "[", 6: "]"}.get(c % 9, " ") if r == mid else " "
    if kind == "pier":
        return "|" if c % 4 == 1 else " "
    if kind == "dome":
        # The back wall's grid of louvred panels: ribs, and a louvre row every third line; they slide as it turns.
        x, y = cell_centre(c, r)
        if inside(SLIT, x, y) or inside(SHUTTER, x, y):
            return " "
        if (c + frame) % 3 == 0:
            return "|"
        return "=" if (r - top) % 3 == 1 else " "
    return " "


def rasterise(faces, frame=None, edges=True):
    """Glyph rows for the faces given, back to front: textures inside, line glyphs along every edge."""
    owner = [[None] * COLS for _ in range(ROWS)]
    for i, (_, pg, _, _) in enumerate(faces):
        for r in range(ROWS):
            for c in range(COLS):
                if inside(pg, *cell_centre(c, r)):
                    owner[r][c] = i
    spans = {}
    for i in range(len(faces)):
        rs = [r for r in range(ROWS) if i in owner[r]]
        spans[i] = (min(rs), max(rs)) if rs else (0, 0)
    grid = [[" "] * COLS for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            i = owner[r][c]
            if i is not None:
                grid[r][c] = texture(faces[i][3], c, r, spans[i], frame)
    for r in range(ROWS if edges else 0):
        for c in range(COLS):
            i = owner[r][c]
            if i is None:
                continue
            up = owner[r - 1][c] if r > 0 else None
            down = owner[r + 1][c] if r + 1 < ROWS else None
            left = owner[r][c - 1] if c > 0 else None
            right = owner[r][c + 1] if c + 1 < COLS else None
            if up == i and down == i and left == i and right == i:
                continue
            cx_, cy_ = cell_centre(c, r)
            slope, at = nearest_slope(faces[i][1], cx_, cy_)
            if 0.3 <= abs(slope) < 0.8:
                # A shallow slope: one glyph per cell, picked by where the edge crosses it, so it reads _.-'
                if up != i:
                    frac = (at - (cy_ - LH / 2)) / LH
                    grid[r][c] = "_" if frac < 0.3 else "." if frac < 0.5 else "-" if frac < 0.75 else "'"
                continue
            if abs(slope) < 0.3:
                if up != i and r > 0 and owner[r - 1][c] is None:
                    grid[r - 1][c] = "_"
                if down != i:
                    grid[r][c] = "_"
            elif abs(slope) > 2.8:
                if left != i or right != i:
                    grid[r][c] = "|"
            elif (left != i) or (right != i) or (up != i):
                # Local y is up, so a rising edge is '/'.
                grid[r][c] = "/" if slope > 0 else "\\"
    return ["".join(row) for row in grid]


def text_rows(rows, x0, top, cls, fill, extra=""):
    """One <text> per row, pinned to the grid: textLength spreads each row to exactly its cells, whatever the font."""
    out = ""
    for r, line in enumerate(rows):
        stripped = line.rstrip()
        lead = len(stripped) - len(stripped.lstrip())
        body = stripped.lstrip()
        if not body:
            continue
        out += (
            f'<text x="{f(x0 + lead * CW)}" y="{f(top + r * LH)}" textLength="{f(len(body) * CW)}" '
            f'lengthAdjust="spacingAndGlyphs"{extra}>{esc(body)}</text>'
        )
    return f'<g class="{cls}" fill="{fill}">{out}</g>'


def to_scene(pg):
    return "M" + "L".join(f"{f(RUBIN_X + x)} {f(RUBIN_GROUND - y)}" for x, y in pg) + "Z"


# The telescope through the slit: the secondary's spider, the mirror cell and the camera's bright face.
SCOPE = [
    r"\\|//",
    r"=(O)=",
    r"//|\\",
]

# Rocks piled in front of the right half of the building, in scene units.
ROCKS = [
    (1180, 806), (1222, 794), (1252, 776), (1280, 756), (1306, 742), (1340, 734), (1380, 730), (1430, 727),
    (1480, 724), (1530, 722), (1600, 726), (1700, 736), (2200, 770), (2200, 1000), (1180, 1000),
]


def rocks():
    pts = []
    for (x0, y0), (x1, y1) in zip(ROCKS, ROCKS[1:]):
        steps = max(1, int(abs(x1 - x0) / 9))
        for i in range(steps):
            t = i / steps
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if y < 1000 and x < 2200:
                y += (noise1(x, 22, 140) - 0.5) * 12 + (hash01(int(x), 1, 141) - 0.5) * 5
            pts.append((x, y))
    pts.append(ROCKS[-1])
    d = "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z"
    defs = (
        '<linearGradient id="rockfront" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="{0}"/><stop offset=".22" stop-color="{1}"/><stop offset=".5" stop-color="{2}" stop-opacity="0"/></linearGradient>'.format(
            *PAL.get("rockfront", ("#262b58", "#191e48", "#151a42"))) +
        f'<clipPath id="pile"><path d="{d}"/></clipPath>'
    )
    body = f'<path d="{d}" fill="url(#rockfront)"/>'
    # Boulders in glyphs: denser and brighter near the top of the pile, where the twilight catches them.
    rows_lit, rows_dim = [], []
    for r in range(9):
        y = 724 + r * LH
        lit, dim = "", ""
        for c in range(int((1700 - 1180) / CW)):
            x = 1180 + c * CW
            top = None
            for (x0, y0), (x1, y1) in zip(ROCKS, ROCKS[1:]):
                if x0 <= x <= x1:
                    top = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
                    break
            depth = y - (top if top is not None else 2000)
            v = hash01(c, r, 150)
            g = " "
            if 0 < depth < 30 and v < 0.42:
                g = "o.o,:'o."[int(hash01(c, r, 151) * 8)]
            elif depth >= 30 and v < 0.08:
                g = ".,:'"[int(hash01(c, r, 152) * 4)]
            lit += g if 0 < depth < 30 else " "
            dim += g if depth >= 30 else " "
        rows_lit.append(lit)
        rows_dim.append(dim)
    body += f'<g clip-path="url(#pile)">'
    if True:
        body += text_rows(rows_dim, 1180, 724, "glyph", "#323a6c")
        body += text_rows(rows_lit, 1180, 724, "glyph bold", "url(#rocklit)")
    body += "</g>"
    defs += (
        '<linearGradient id="rocklit" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#8a76a6"/><stop offset=".5" stop-color="#6f7fb0"/><stop offset="1" stop-color="#6a7cac"/></linearGradient>'
    )
    return defs, body


def rubin():
    defs = (
        '<linearGradient id="moonlit" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#f4f8ff"/><stop offset=".45" stop-color="#d6e4f4"/>'
        '<stop offset=".8" stop-color="#aecbdc"/><stop offset="1" stop-color="#8cc4cc"/></linearGradient>'
        '<linearGradient id="aperture" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#b8fdff"/><stop offset=".45" stop-color="#4fe6f2"/><stop offset="1" stop-color="#1f8fc8"/></linearGradient>'
        '<radialGradient id="camera" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#058b8c"/><stop offset=".3" stop-color="#058b8c" stop-opacity=".7"/>'  # Rubin's brand teals
        '<stop offset=".65" stop-color="#0c4a4c" stop-opacity=".35"/><stop offset="1" stop-color="#0c4a4c" stop-opacity="0"/></radialGradient>'
    )
    grid_top = RUBIN_GROUND - ROWS * LH
    baseline = grid_top + LH - 3.5

    body = (
        f'<path d="M{RUBIN_X + 100} {RUBIN_GROUND + 4}L{RUBIN_X + 220} {RUBIN_GROUND - 40}L{RUBIN_X + 330} {RUBIN_GROUND - 70}'
        f'L{RUBIN_X + 600} {RUBIN_GROUND - 74}L{RUBIN_X + 700} {RUBIN_GROUND - 60}L{RUBIN_X + 700} {RUBIN_GROUND + 2}'
        f'L{RUBIN_X + 100} {RUBIN_GROUND + 2}Z" fill="{PAL.get("ground", "#1a1f4a")}"/>'
    )
    for _, pg, colour, _ in FACES:
        body += f'<path d="{to_scene(pg)}" fill="{colour}"/>'
    body += text_rows(rasterise(FACES), RUBIN_X, baseline, "glyph bold", "url(#moonlit)")
    # Lit windows along the ground floor and the wedge, blue as in the photos.
    for px in (175, 200, 330, 352, 420):
        x, y = P(px, 760)
        body += f'<rect class="win" x="{f(RUBIN_X + x)}" y="{f(RUBIN_GROUND - y)}" width="9" height="6" fill="#6fd8ff" opacity=".55"/>'

    # The dome: its louvred back wall slides as it turns (three positions); the slit stays facing the sky.
    sx = [RUBIN_X + x for x, _ in SLIT]
    sy = [RUBIN_GROUND - y for _, y in SLIT]
    cx, cy = sum(sx) / 4, sum(sy) / 4
    scope = text_rows(SCOPE, cx - 2.5 * CW, cy - LH + 4, "glyph bold", "#0b2c44")
    for i in range(3):
        rows = rasterise([("dome", DOME, DOME_COLOUR, "dome")], i, edges=False)
        turn = (' opacity="0"' if i else "") + anim(f"f{i} 45s steps(1,end) infinite")
        body += (
            f'<path d="{to_scene(DOME)}" fill="{DOME_COLOUR}"{turn}/>'
            f'<path d="{to_scene(DOME_BAND)}" fill="#0e1232"{turn}/>'
            f'{text_rows(rows, RUBIN_X, baseline, "glyph bold", "url(#moonlit)", turn)}'
            f'<path d="{to_scene(DOME)}" fill="none" stroke="url(#moonlit)" stroke-width="1.6" stroke-linejoin="round"{turn}/>'
        )
    body += (
        f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="150" ry="125" fill="url(#camera)"{anim("cam 6s ease-in-out infinite alternate")}/>'
        f'<path d="{to_scene(SLIT)}" fill="url(#aperture)" opacity=".95"/>'
        f"{scope}"
        f'<path d="{to_scene(SHUTTER)}" fill="#0e1232"/>'
        f'<path d="{to_scene(SHUTTER)}" fill="none" stroke="#cfe0f2" stroke-width="1.2" opacity=".7"/>'
        f'<path d="{to_scene(SLIT)}" fill="none" stroke="#bff8ff" stroke-width="1.4" opacity=".8"/>'
    )
    rock_defs, rock_body = rocks()
    return defs + rock_defs, body + rock_body


# ---------------------------------------------------------------- comet

# Down the open right side, beside the chat column rather than behind it, passing above the dome.
COMET_FROM = (1590, 30)
COMET_TO = (1010, 400)


def comet():
    (x0, y0), (x1, y1) = COMET_FROM, COMET_TO
    dx, dy = x1 - x0, y1 - y0
    angle = math.degrees(math.atan2(-dy, -dx))  # the tail points back where it came from
    defs = (
        '<linearGradient id="tail" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#eafcff" stop-opacity=".95"/><stop offset=".15" stop-color="#9fe8f0" stop-opacity=".6"/>'
        '<stop offset=".5" stop-color="#7f9cf0" stop-opacity=".22"/><stop offset="1" stop-color="#8a6fd8" stop-opacity="0"/></linearGradient>'
        '<linearGradient id="tail2" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity=".9"/><stop offset=".35" stop-color="#d8f6ff" stop-opacity=".35"/>'
        '<stop offset="1" stop-color="#d8f6ff" stop-opacity="0"/></linearGradient>'
        '<radialGradient id="coma" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#ffffff"/><stop offset=".25" stop-color="#d9fbff" stop-opacity=".8"/>'
        '<stop offset=".6" stop-color="#7fe6f0" stop-opacity=".25"/><stop offset="1" stop-color="#7fe6f0" stop-opacity="0"/></radialGradient>'
    )
    a = math.radians(angle)

    def rot(x, y):
        return f"{f(x * math.cos(a) - y * math.sin(a))} {f(x * math.sin(a) + y * math.cos(a))}"

    # The tail gradients run along the tail, in the shapes' own units.
    defs = defs.replace('id="tail" x1="0" y1="0" x2="1" y2="0"', f'id="tail" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{rot(340, 0).split()[0]}" y2="{rot(340, 0).split()[1]}"')
    defs = defs.replace('id="tail2" x1="0" y1="0" x2="1" y2="0"', f'id="tail2" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{rot(260, 0).split()[0]}" y2="{rot(260, 0).split()[1]}"')
    fly = ' opacity="0"' + anim("comet 20s linear 3s infinite")
    body = (
        f'<g transform="translate({x0} {y0})">'
        f'<path d="M{rot(0, -7)} C{rot(90, -16)} {rot(220, -26)} {rot(340, -30)} L{rot(340, 30)} C{rot(220, 24)} {rot(90, 14)} {rot(0, 7)}Z" fill="url(#tail)"{fly}/>'
        f'<path d="M{rot(0, -2.2)} L{rot(260, -5)} L{rot(260, 5)} L{rot(0, 2.2)}Z" fill="url(#tail2)"{fly}/>'
        f'<circle r="16" fill="url(#coma)"{fly}/><circle r="2.6" fill="#ffffff"{fly}/></g>'
    )
    return defs, body, (dx, dy)


# ---------------------------------------------------------------- daytime only: sun, sky clouds and birds

# Big fluffy fair-weather clouds high in the day sky, drawn behind the summit.
SKY_CLOUDS = [
    (560, 250, 320, 42, "c2"),
    (1010, 170, 270, 36, "c1"),
    (1380, 300, 300, 40, "c3"),
    (300, 430, 240, 32, "c1"),
    (800, 420, 260, 32, "c3"),
    (1200, 520, 220, 28, "c2"),
]


def sun():
    """The sun in the top left: a wide warm glow, a slowly turning ring of rays, and a pale disc."""
    cx, cy = 150, 125
    defs = (
        '<radialGradient id="sunglow" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#fffbe8" stop-opacity=".95"/><stop offset=".18" stop-color="#fff2c4" stop-opacity=".6"/>'
        '<stop offset=".5" stop-color="#ffe6a8" stop-opacity=".18"/><stop offset="1" stop-color="#ffe6a8" stop-opacity="0"/></radialGradient>'
    )
    rays = ""
    for i in range(16):
        a = math.radians(i * 22.5)
        r0, r1 = (58, 96) if i % 2 == 0 else (60, 80)
        rays += f"M{f(cx + r0 * math.cos(a))} {f(cy + r0 * math.sin(a))}L{f(cx + r1 * math.cos(a))} {f(cy + r1 * math.sin(a))}"
    body = (
        f'<circle cx="{cx}" cy="{cy}" r="330" fill="url(#sunglow)"{anim("cam 8s ease-in-out infinite alternate")}/>'
        f'<path d="{rays}" stroke="#fff4cc" stroke-width="3" stroke-linecap="round" opacity=".55">'
        f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="120s" repeatCount="indefinite"/></path>'
        f'<circle cx="{cx}" cy="{cy}" r="44" fill="#fffaea"/>'
        f'<circle cx="{cx}" cy="{cy}" r="44" fill="none" stroke="#fff1c0" stroke-width="6" stroke-opacity=".5"/>'
    )
    return defs, body


# Flocks: (start y, bird count, seconds to cross, delay, scale). Each flies left to right across the whole sky.
FLOCKS = [
    (230, 5, 34, 0, 1.0),
    (380, 3, 46, -20, 0.8),
    (150, 4, 40, -31, 0.65),
]


def birds():
    """Small V-shaped birds that flap (SMIL on the path's shape) as their flock glides across (CSS on the group)."""
    up = "M-9 -4Q-4 -5 0 0Q4 -5 9 -4"
    down = "M-9 3Q-4 -1 0 0Q4 -1 9 3"
    body = ""
    for k, (y0, count, secs, delay, s) in enumerate(FLOCKS):
        brng = random.Random(900 + k)
        flock = ""
        for i in range(count):
            # A loose V: the leader in front, the rest trailing back and to either side.
            row = (i + 1) // 2
            side = -1 if i % 2 else 1
            x = -row * 26 * s + brng.uniform(-4, 4)
            y = side * row * 14 * s + brng.uniform(-3, 3)
            flap = 0.5 + brng.random() * 0.35
            flock += (
                f'<path transform="translate({f(x)} {f(y)}) scale({s})" d="{up}" fill="none" stroke="#2a3a5c" '
                f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                f'<animate attributeName="d" values="{up};{down};{up}" dur="{flap:.2f}s" begin="-{brng.random():.2f}s" repeatCount="indefinite"/></path>'
            )
        body += (
            f'<g transform="translate(0 {y0})"><g{anim(f"fly {secs}s linear {delay}s infinite")}>{flock}</g></g>'
        )
    return body


# By day the buildings are pale concrete and white cladding, their ASCII lines drawn in dark steel instead of moonlight.
DAY_BUILDING = {
    "#141a40": "#b9c7da", "#171e48": "#c3d0e1", "#11163a": "#a9b8cd", "#10153a": "#a3b2c8",
    "#161d45": "#bfccdd", "#1a2250": "#ccd8e7", "#161d46": "#d6e0ec", "#0e1232": "#7d8fab",
    "#cfe0f2": "#4a5f82",
    "#0c4a4c": "#058b8c",  # the camera halo fades out in bright teal, not dark, against white walls
    # the moonlit gradient that colours every building glyph and outline
    "#f4f8ff": "#22345a", "#d6e4f4": "#2c4068", "#aecbdc": "#354c74", "#8cc4cc": "#2f5a78",
}


def daylit(svg):
    if TIME != "day":
        return svg
    for night, day in DAY_BUILDING.items():
        svg = svg.replace(night, day)
    return svg


# ---------------------------------------------------------------- assemble

def build():
    sky_defs, sky_body = sky()
    mw_body, mw_count = milky_way()
    star_body = stars()  # always built, so every time of day draws the same stars from the same random numbers
    mw_body = "" if PAL["milky_way"] == 0 else mw_body if PAL["milky_way"] == 1 else f'<g opacity="{PAL["milky_way"]}">{mw_body}</g>'
    star_body = "" if PAL["stars"] == 0 else star_body if PAL["stars"] == 1 else f'<g opacity="{PAL["stars"]}">{star_body}</g>'
    ridge_defs, ridge_body = ridges()
    cloud_body = clouds()
    day_defs, day_body = "", ""
    if TIME == "day":
        day_defs, sun_body = sun()
        day_body = sun_body + clouds(SKY_CLOUDS, 20) + birds()
    hill_defs, hill_body = summit()
    rubin_defs, rubin_body = rubin()
    comet_defs, comet_body, (cdx, cdy) = comet()
    if not PAL["comet"]:
        comet_defs, comet_body = "", ""

    style = (
        f"text{{font-family:{FONT};font-size:12px;white-space:pre}}"
        ".bold{font-weight:700}.small{font-size:11px}"
        # Each animated element carries its own `animation` (see anim()); the sheet holds only the keyframes.
        "@keyframes tw{0%,100%{opacity:1}50%{opacity:.25}}"
        "@keyframes mw{from{opacity:1}to{opacity:.7}}"
        "@keyframes dusk{from{opacity:1}to{opacity:.7}}"
        "@keyframes drift{from{transform:translateX(-150px)}to{transform:translateX(170px)}}"
        # The comet: 20 s apart, about 7 s to cross. Hidden at rest.
        f"@keyframes comet{{0%{{transform:translate(0,0);opacity:0}}4%{{opacity:1}}28%{{opacity:.9}}"
        f"36%{{transform:translate({f(cdx)}px,{f(cdy)}px);opacity:0}}100%{{transform:translate({f(cdx)}px,{f(cdy)}px);opacity:0}}}}"
        # The dome turns every 15 s, three positions in a 45 s round. Frame 0 is the rest.
        "@keyframes f0{0%{opacity:1}33.3%{opacity:0}100%{opacity:0}}"
        "@keyframes f1{0%{opacity:0}33.3%{opacity:1}66.6%{opacity:0}100%{opacity:0}}"
        "@keyframes f2{0%{opacity:0}66.6%{opacity:1}100%{opacity:1}}"
        "@keyframes cam{from{opacity:.75}to{opacity:1}}"
        "@keyframes fly{from{transform:translateX(-120px)}to{transform:translateX(1760px)}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    )
    defs = sky_defs + day_defs + ridge_defs + hill_defs + daylit(rubin_defs) + comet_defs
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%" '
        f'preserveAspectRatio="xMidYMid slice"><style>{style}</style><defs>{defs}</defs>'
        f"{sky_body}{day_body}{mw_body}{star_body}{comet_body}{ridge_body}{daylit(soar())}"
        + f'<g class="fg">{hill_body}{daylit(gemini() + rubin_body)}</g>' + f"{cloud_body}</svg>"
    )
    return svg, mw_count


# The scene file and its function: sunset keeps the original names.
NAME = ("rubin-pachon.ts", "rubinPachonSvg") if TIME == "sunset" else (f"rubin-pachon-{TIME}.ts", f"rubinPachon{TIME.title()}Svg")


def main():
    svg, mw_count = build()
    root = Path(__file__).resolve().parent.parent
    ts = (
        f"// Rubin on Cerro Pachon ({TIME}): an ASCII Vera C. Rubin Observatory, with a dotted Milky Way,\n"
        "// twinkling stars and a comet every 20 seconds. Generated by tools/rubin-pachon.py: edit that and run it again.\n"
        "// Pure string: no DOM, nothing brought in from outside this file.\n\n"
        f"const SCENE = {svg!r}\n\n"
        f"export function {NAME[1]}(): string {{\n  return SCENE\n}}\n"
    )
    # Python's repr of a str is a valid JS string literal here: the SVG holds no backslash escapes but \\.
    (root / "hooks" / "scenes" / NAME[0]).write_text(ts)
    if "--svg" in sys.argv:
        Path(sys.argv[sys.argv.index("--svg") + 1]).write_text(svg)
    print(f"svg {len(svg)} chars, milky way {mw_count} dots, ts {len(ts)} chars")


if __name__ == "__main__":
    main()
