#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates every SVG used by the profile README.

    python .github/assets/generate.py

Everything is driven by the tokens and data blocks below, so editing a colour,
a job title or a stack entry means editing one line and re-running this file.

Animation is SMIL only (<animate> / <animateTransform>). GitHub serves README
images through camo, which runs SMIL and CSS but never scripts -- sticking to a
single animation technology keeps the failure modes down to one.
"""

import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- tokens ----

THEMES = {
    "dark": {
        "surface":  "#12171F",
        "border":   "#252C38",
        "text":     "#E6EDF3",
        "muted":    "#8B949E",
        "faint":    "#30363D",
        "accent":   "#00D9FF",
        "accent2":  "#7C3AED",
        "glow":     0.20,
    },
    "light": {
        "surface":  "#FFFFFF",
        "border":   "#D8DEE4",
        "text":     "#1F2328",
        "muted":    "#636C76",
        "faint":    "#D0D7DE",
        "accent":   "#0B8FA8",
        "accent2":  "#6D28D9",
        "glow":     0.12,
    },
}

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

# Monospace advance width as a fraction of font-size, for centring text by hand.
ADV = 0.6

# Every animation runs on one shared timeline and every element's *base*
# attributes hold its FINAL value, so a renderer that ignores SMIL (GitHub's
# mobile app, link previews, reduced-motion) still shows the finished design
# rather than an empty frame.
TL = 2.6

# ------------------------------------------------------------------ data ----

NAME     = "LENNY DANY DEREK D"
ROLE     = "FULL-STACK DEVELOPER  ·  DESKTOP APPS  ·  AI AGENTS"
FACTS    = ["SRM UNIVERSITY", "B.TECH CSE · 3RD YEAR", "CHENNAI, IN"]
TAGLINE  = "I ship products, not just projects."
CLOCK    = "09:41"

# Icons that define what makes this profile unusual -- rendered large, in colour.
TIER1 = [
    ("rust",        "RUST"),
    ("tauri",       "TAURI 2"),
    ("typescript",  "TYPESCRIPT"),
    ("nextdotjs",   "NEXT.JS"),
    ("react",       "REACT"),
    ("python",      "PYTHON"),
]

# Everything else -- rendered small and muted, two rows of eight.
TIER2 = [
    ("javascript",    "JS"),
    ("tailwindcss",   "TAILWIND"),
    ("framer",        "MOTION"),
    ("fastapi",       "FASTAPI"),
    ("flask",         "FLASK"),
    ("supabase",      "SUPABASE"),
    ("postgresql",    "POSTGRES"),
    ("expo",          "EXPO"),
    ("electron",      "ELECTRON"),
    ("docker",        "DOCKER"),
    ("vercel",        "VERCEL"),
    ("git",           "GIT"),
    ("githubactions", "ACTIONS"),
    ("razorpay",      "RAZORPAY"),
    ("c",             "C"),
    ("cplusplus",     "C++"),
]

ICONS = json.load(io.open(os.path.join(HERE, "icons.json"), encoding="utf-8"))

# ----------------------------------------------------------------- utils ----


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def txt(x, y, s, size, fill, anchor="middle", weight="400", ls="0", opacity="1"):
    return (
        '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" '
        'letter-spacing="%s" fill="%s" fill-opacity="%s" text-anchor="%s">%s</text>'
        % (x, y, MONO, size, weight, ls, fill, opacity, anchor, esc(s))
    )


def width_of(s, size, ls=0.0):
    """Rendered width of a monospace string, for manual centring."""
    return len(s) * (size * ADV + float(ls))


def _track(tag, attr, a, b, t0, t1, extra=""):
    """Hold at `a`, ease to `b` between t0 and t1, hold -- on the shared timeline.

    The element keeps `b` as its base attribute, so dropping SMIL loses the
    motion and nothing else.
    """
    # keyTimes must start at 0 and end at 1 or the animation is ignored outright,
    # so the value list is padded with a leading and trailing hold.
    k0, k1 = max(0.0, t0 / TL), min(1.0, t1 / TL)
    return ('<%s attributeName="%s"%s values="%s;%s;%s;%s" keyTimes="0;%.4f;%.4f;1" '
            'dur="%ss" fill="freeze" calcMode="spline" '
            'keySplines="0 0 1 1;0.16 1 0.3 1;0 0 1 1"/>'
            % (tag, attr, extra, a, a, b, b, k0, k1, TL))


def anim(attr, a, b, t0, t1):
    return _track("animate", attr, a, b, t0, t1)


def fade(t0, dur=0.45, rise=8):
    """Fade-and-rise for a group whose base state is already fully visible."""
    out = anim("opacity", "0", "1", t0, t0 + dur)
    if rise:
        out += _track("animateTransform", "transform", "0 %s" % rise, "0 0",
                      t0, t0 + dur, extra=' type="translate"')
    return out


def lerp_hex(a, b, k):
    """Blend two #rrggbb colours. Used to grade a row of icons across the
    accent range, giving each icon one flat colour instead of letting a shared
    gradient split a single glyph in half."""
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(int(round(x + (y - x) * k)) for x, y in zip(pa, pb))


def icon(slug, cx, top, size, fill, opacity="1"):
    if slug not in ICONS:
        return ""
    s = size / 24.0
    return ('<g transform="translate(%.2f,%.2f) scale(%.4f)" fill="%s" fill-opacity="%s">'
            '<path d="%s"/></g>' % (cx - size / 2.0, top, s, fill, opacity, ICONS[slug]["d"]))


def dotgrid(w, h, colour, step=28, r=1.1, op=0.5):
    d = []
    y = step
    while y < h:
        x = step
        while x < w:
            d.append('<circle cx="%d" cy="%d" r="%s"/>' % (x, y, r))
            x += step
        y += step
    return '<g fill="%s" fill-opacity="%s">%s</g>' % (colour, op, "".join(d))


def write(name, body):
    path = os.path.join(HERE, name)
    io.open(path, "w", encoding="utf-8", newline="\n").write(body)
    print("  %-22s %6d bytes" % (name, len(body.encode("utf-8"))))


# ------------------------------------------------------------------ hero ----

def hero(theme):
    t = THEMES[theme]
    W, H = 1000, 380

    # The notch: hangs off the top edge, so its top corners sit outside the canvas.
    c = dict(x=400, w=200, h=96)      # collapsed (peek)
    e = dict(x=130, w=740, h=236)     # expanded (card)
    TOP = -28
    BOT = TOP + e["h"]                # 208

    o = []
    o.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
             'role="img" aria-label="%s — %s">' % (W, H, W, H, esc(NAME), esc(ROLE)))

    o.append('<defs>'
             '<linearGradient id="a" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
             '<filter id="g" x="-40%%" y="-200%%" width="180%%" height="500%%">'
             '<feGaussianBlur stdDeviation="19"/></filter>'
             '</defs>' % (t["accent"], t["accent2"]))

    o.append(dotgrid(W, H, t["faint"], op=0.32))

    # Light spilling from the notch's lower edge -- a thin bloom, not a cloud.
    o.append('<g>%s<rect x="%d" y="%d" width="%d" height="44" rx="22" fill="url(#a)" '
             'fill-opacity="%s" filter="url(#g)"/></g>'
             % (anim("opacity", "0", "1", 0.55, 1.3),
                e["x"] + 40, BOT - 30, e["w"] - 80, t["glow"]))

    # The notch body. Base attributes are the expanded card.
    o.append('<rect y="%d" rx="30" fill="%s" stroke="%s" stroke-width="1" x="%d" width="%d" height="%d">'
             '%s%s%s</rect>'
             % (TOP, t["surface"], t["border"], e["x"], e["w"], e["h"],
                anim("x", c["x"], e["x"], 0.25, 1.0),
                anim("width", c["w"], e["w"], 0.25, 1.0),
                anim("height", c["h"], e["h"], 0.25, 1.0)))

    # Equalizer -- Crest's resting state, so it never stops moving.
    base, bw, gap = 132, 5, 9
    hs = [9, 24, 13, 28, 11, 19, 9]
    o.append('<g>%s' % fade(1.15, 0.4, 0))
    for i in range(5):
        seq = (hs[i:] + hs[:i])[:6]
        seq = seq + [seq[0]]
        vals = ";".join(str(v) for v in seq)
        ys = ";".join(str(base - v) for v in seq)
        o.append('<rect x="%d" width="%d" rx="2.5" fill="%s" y="%d" height="%d">'
                 '<animate attributeName="height" values="%s" dur="1.6s" repeatCount="indefinite"/>'
                 '<animate attributeName="y" values="%s" dur="1.6s" repeatCount="indefinite"/>'
                 '</rect>'
                 % (176 + i * (bw + gap), bw, t["accent"], base - seq[0], seq[0], vals, ys))
    o.append('</g>')

    # Clock, mirroring the equalizer on the right.
    o.append('<g>%s%s</g>' % (fade(1.15, 0.4, 0),
             txt(824, 130, CLOCK, 15, t["muted"], anchor="end", ls="2")))

    # Identity.
    o.append('<g>%s%s</g>' % (fade(0.85),
             txt(500, 124, NAME, 37, t["text"], weight="600", ls="5.5")))
    o.append('<g>%s%s</g>' % (fade(1.02),
             txt(500, 160, ROLE, 13, t["muted"], ls="2.6")))

    # The notch's light bar, along its bottom edge.
    o.append('<rect y="%d" height="2.5" rx="1.25" fill="url(#a)" x="%d" width="%d">%s%s</rect>'
             % (BOT - 2, e["x"] + 54, e["w"] - 108,
                anim("x", 500, e["x"] + 54, 0.55, 1.25),
                anim("width", 0, e["w"] - 108, 0.55, 1.25)))

    # Facts, separated by accent diamonds.
    gy, gap2 = 272, 44
    o.append('<g>%s' % fade(1.35))
    spans = [width_of(f, 12, 2.2) for f in FACTS]
    cur = 500 - (sum(spans) + gap2 * (len(FACTS) - 1)) / 2.0
    for i, f in enumerate(FACTS):
        o.append(txt("%.1f" % (cur + spans[i] / 2.0), gy, f, 12, t["muted"], ls="2.2"))
        cur += spans[i]
        if i < len(FACTS) - 1:
            o.append('<rect x="%.1f" y="%d" width="4.5" height="4.5" fill="%s" '
                     'transform="rotate(45 %.1f %.1f)"/>'
                     % (cur + gap2 / 2 - 2.25, gy - 8, t["accent"],
                        cur + gap2 / 2, gy - 5.75))
            cur += gap2
    o.append('</g>')

    # Prompt line.
    py = 330
    tag_w = width_of(TAGLINE, 15, 0.3)
    x0 = 500 - (22 + tag_w) / 2.0
    o.append('<g>%s' % fade(1.62))
    o.append(txt("%.1f" % x0, py, "$", 15, t["accent"], anchor="start", weight="600"))
    o.append(txt("%.1f" % (x0 + 22), py, TAGLINE, 15, t["text"], anchor="start", ls="0.3"))
    o.append('<rect x="%.1f" y="%d" width="9" height="16" fill="%s">'
             '<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.45;0.5;0.95;1" '
             'dur="1.1s" repeatCount="indefinite"/></rect>'
             % (x0 + 22 + tag_w + 4, py - 12, t["accent"]))
    o.append('</g>')

    o.append('</svg>')
    return "".join(o)


# ----------------------------------------------------------------- stack ----

def stack(theme):
    t = THEMES[theme]
    W, H = 1000, 372

    labels = ", ".join(l for _, l in TIER1 + TIER2)
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'role="img" aria-label="Tech stack: %s">' % (W, H, W, H, esc(labels))]

    # Tier 1 -- six across, colour-graded left to right.
    n1 = len(TIER1)
    span, sz = 160, 42
    x0 = 500 - (n1 - 1) * span / 2.0
    for i, (slug, label) in enumerate(TIER1):
        cx = x0 + i * span
        k = i / float(n1 - 1) if n1 > 1 else 0
        o.append('<g>%s%s%s</g>' % (
            fade(0.1 + i * 0.07, 0.45, 10),
            icon(slug, cx, 46, sz, lerp_hex(t["accent"], t["accent2"], k)),
            txt(cx, 122, label, 12, t["text"], weight="500", ls="1.6")))

    # Divider.
    o.append('<g>%s'
             '<rect x="60" y="164" width="880" height="1" fill="%s"/>'
             '<rect x="492" y="160" width="9" height="9" rx="1.5" fill="%s" transform="rotate(45 496.5 164.5)"/>'
             '</g>' % (fade(0.55, 0.5, 0), t["faint"], t["accent"]))

    # Tier 2 -- two rows of eight, muted.
    per, span2, sz2 = 8, 112, 24
    x0 = 500 - (per - 1) * span2 / 2.0
    for i, (slug, label) in enumerate(TIER2):
        row, col = i // per, i % per
        cx = x0 + col * span2
        top = 210 + row * 78
        o.append('<g>%s%s%s</g>' % (
            fade(0.72 + i * 0.035, 0.4, 8),
            icon(slug, cx, top, sz2, t["muted"], opacity="0.85"),
            txt(cx, top + 44, label, 10, t["muted"], ls="1.2")))

    o.append('</svg>')
    return "".join(o)


# --------------------------------------------------------------- divider ----

def divider():
    """One rule for both themes.

    A <picture> block per divider would be five copies of the same markup, so
    this uses a neutral grey at low opacity and a mid teal -- both legible on
    GitHub's white and on #0D1117 -- and ships as a single file.
    """
    W, H = 1000, 22
    grey, teal = "#7D8590", "#00B8D4"
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="presentation">'
        '<defs><linearGradient id="d" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="%s" stop-opacity="0"/>'
        '<stop offset="0.5" stop-color="%s" stop-opacity="0.42"/>'
        '<stop offset="1" stop-color="%s" stop-opacity="0"/>'
        '</linearGradient></defs>'
        '<rect x="0" y="10" width="1000" height="1" fill="url(#d)"/>'
        '<rect x="495" y="6" width="9" height="9" rx="1.5" fill="%s" transform="rotate(45 499.5 10.5)"/>'
        '</svg>' % (W, H, W, H, grey, grey, grey, teal)
    )


# ------------------------------------------------------------------ main ----

if __name__ == "__main__":
    print("generating profile assets\n")
    for theme in ("dark", "light"):
        write("hero-%s.svg" % theme, hero(theme))
        write("stack-%s.svg" % theme, stack(theme))
    write("rule.svg", divider())
    print("\ndone")
