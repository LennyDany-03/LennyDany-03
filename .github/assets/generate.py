#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates every SVG used by the profile README.

    python .github/assets/generate.py

Everything is driven by the tokens and data blocks below, so editing a colour,
a job title or a stack entry means editing one line and re-running this file.

--------------------------------------------------------------------------
ANIMATION RULE -- learned the hard way, do not undo it
--------------------------------------------------------------------------
Motion may only ADD to this artwork. Nothing is allowed to be invisible
until an animation reveals it.

The first version staged a reveal (the notch expanding, text fading up) with
SMIL <animate>. On github.com that froze part-way: the notch and light bar
rendered, but every faded group stayed at opacity 0, so the hero showed as an
empty box. raw.githubusercontent.com serves these files under
`Content-Security-Policy: default-src 'none'; ...; sandbox`, and a sandboxed
image is not a reliable place to run a timeline.

So: every element is drawn at its final state. The only motion left is the
equalizer and the cursor blink, done in CSS -- both loop between valid
visible states, so if the animation never runs, or freezes on any frame, the
artwork is still correct. CSS (not SMIL) because the CSP explicitly permits
`style-src 'unsafe-inline'`, which is why the contribution-snake SVG in this
same README animates fine.
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
DATA = json.load(io.open(os.path.join(HERE, "data.json"), encoding="utf-8"))

# GitHub's own language colours -- real data reads better than a house palette.
LANG_COLORS = {
    "JavaScript": "#F1E05A", "TypeScript": "#3178C6", "Python": "#3572A5",
    "HTML": "#E34C26", "CSS": "#563D7C", "Rust": "#DEA584", "Shell": "#89E051",
}

# The three flagships, in the order they should be read.
PROJECTS = [
    {
        "key": "crest", "motif": "notch", "k": 0.0,
        "name": "CREST", "meta": "v0.6.9",
        "tagline": "The dynamic notch, built for Windows.",
        "desc": "A Mica-glass panel pinned to the top of any screen — media, launcher, clipboard, notes.",
        "stack": ["Tauri 2", "Rust", "TypeScript"],
        "link": "crest-beta.vercel.app",
    },
    {
        "key": "loopify", "motif": "loop", "k": 0.5,
        "name": "LOOPIFY", "meta": "iOS · Android",
        "tagline": "Habits, tracked on a real loop.",
        "desc": "An Expo + React Native app on a typed FastAPI backend, with Supabase auth and check-ins.",
        "stack": ["Expo 54", "React 19", "FastAPI", "Supabase"],
        "link": "loopify3.vercel.app",
    },
    {
        "key": "nic", "motif": "film", "k": 1.0,
        "name": "NIC", "meta": "912 frames",
        "tagline": "A keynote you scroll through.",
        "desc": "912 frames across four sequences, painted to canvas at whatever frame the scroll asks for.",
        "stack": ["Next.js 16", "React 19", "Framer Motion", "Supabase"],
        "link": "nic-srm.vercel.app",
    },
]

# The work log. `lang` drives the colour chip, so it has to match the repo.
LEDGER = [
    ("Crest",    "Rust",       "a dynamic notch for Windows",            True),
    ("Loopify",  "JavaScript", "habit tracking on a typed API",          True),
    ("NIC",      "JavaScript", "912 frames scrubbed by scroll",          True),
    ("Ascendry", "JavaScript", "the platform the products ship under",   True),
    ("Atlas",    "Python",     "an agent that executes, not chats",      False),
    ("Blinko",   "JavaScript", "link-in-bio and personal site builder",  True),
    ("Glance",   "JavaScript", "contribution graph as a desktop widget", False),
    ("NovaPay",  "JavaScript", "UPI expense capture and insight",        True),
]

# ----------------------------------------------------------------- utils ----


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def txt(x, y, s, size, fill, anchor="middle", weight="400", ls="0"):
    return (
        '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" '
        'letter-spacing="%s" fill="%s" text-anchor="%s">%s</text>'
        % (x, y, MONO, size, weight, ls, fill, anchor, esc(s))
    )


def width_of(s, size, ls=0.0):
    """Rendered width of a monospace string, for manual centring."""
    return len(s) * (size * ADV + float(ls))


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


def dotgrid(w, h, colour, step=28, r=1.1, op=0.32):
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

# Equalizer bar heights. These are the real drawn heights, so the bars read as
# a frozen waveform even with every animation stripped.
EQ_BARS = [9, 24, 13, 28, 11]
EQ_BASE = 132   # baseline the bars sit on


def hero_css():
    """Looping accents only. Every keyframe is a valid visible state."""
    steps = []
    for pct, h in ((0, 9), (20, 24), (40, 13), (60, 28), (80, 11), (100, 9)):
        steps.append("%d%%{height:%dpx;y:%dpx}" % (pct, h, EQ_BASE - h))
    return (
        "<style>"
        "@keyframes eq{%s}"
        "@keyframes blink{0%%,45%%{opacity:1}50%%,95%%{opacity:0}100%%{opacity:1}}"
        ".eq{animation:eq 1.6s ease-in-out infinite}"
        ".cursor{animation:blink 1.1s step-end infinite}"
        "@media(prefers-reduced-motion:reduce){.eq,.cursor{animation:none}}"
        "</style>" % "".join(steps)
    )


def hero(theme):
    t = THEMES[theme]
    W, H = 1000, 380

    # The notch hangs off the top edge, so its top corners sit outside the canvas.
    NX, NW, NH = 130, 740, 236
    TOP = -28
    BOT = TOP + NH                    # 208

    o = []
    o.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
             'role="img" aria-label="%s — %s">' % (W, H, W, H, esc(NAME), esc(ROLE)))
    o.append(hero_css())

    o.append('<defs>'
             '<linearGradient id="a" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
             '<filter id="g" x="-40%%" y="-200%%" width="180%%" height="500%%">'
             '<feGaussianBlur stdDeviation="19"/></filter>'
             '</defs>' % (t["accent"], t["accent2"]))

    o.append(dotgrid(W, H, t["faint"]))

    # Light spilling from the notch's lower edge -- a thin bloom, not a cloud.
    o.append('<rect x="%d" y="%d" width="%d" height="44" rx="22" fill="url(#a)" '
             'fill-opacity="%s" filter="url(#g)"/>' % (NX + 40, BOT - 30, NW - 80, t["glow"]))

    # The notch body.
    o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="30" fill="%s" '
             'stroke="%s" stroke-width="1"/>' % (NX, TOP, NW, NH, t["surface"], t["border"]))

    # Equalizer -- Crest's resting state, so it never stops moving.
    bw, gap = 5, 9
    for i, h in enumerate(EQ_BARS):
        o.append('<rect class="eq" x="%d" y="%d" width="%d" height="%d" rx="2.5" fill="%s" '
                 'style="animation-delay:%.2fs"/>'
                 % (176 + i * (bw + gap), EQ_BASE - h, bw, h, t["accent"], -0.32 * i))

    # Clock, mirroring the equalizer on the right.
    o.append(txt(824, 130, CLOCK, 15, t["muted"], anchor="end", ls="2"))

    # Identity.
    o.append(txt(500, 124, NAME, 37, t["text"], weight="600", ls="5.5"))
    o.append(txt(500, 160, ROLE, 13, t["muted"], ls="2.6"))

    # The notch's light bar, along its bottom edge.
    o.append('<rect x="%d" y="%d" width="%d" height="2.5" rx="1.25" fill="url(#a)"/>'
             % (NX + 54, BOT - 2, NW - 108))

    # Facts, separated by accent diamonds.
    gy, gap2 = 272, 44
    spans = [width_of(f, 12, 2.2) for f in FACTS]
    cur = 500 - (sum(spans) + gap2 * (len(FACTS) - 1)) / 2.0
    for i, f in enumerate(FACTS):
        o.append(txt("%.1f" % (cur + spans[i] / 2.0), gy, f, 12, t["muted"], ls="2.2"))
        cur += spans[i]
        if i < len(FACTS) - 1:
            o.append('<rect x="%.1f" y="%d" width="4.5" height="4.5" fill="%s" '
                     'transform="rotate(45 %.1f %.1f)"/>'
                     % (cur + gap2 / 2 - 2.25, gy - 8, t["accent"], cur + gap2 / 2, gy - 5.75))
            cur += gap2

    # Prompt line.
    py = 330
    tag_w = width_of(TAGLINE, 15, 0.3)
    x0 = 500 - (22 + tag_w) / 2.0
    o.append(txt("%.1f" % x0, py, "$", 15, t["accent"], anchor="start", weight="600"))
    o.append(txt("%.1f" % (x0 + 22), py, TAGLINE, 15, t["text"], anchor="start", ls="0.3"))
    o.append('<rect class="cursor" x="%.1f" y="%d" width="9" height="16" fill="%s"/>'
             % (x0 + 22 + tag_w + 4, py - 12, t["accent"]))

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
        o.append(icon(slug, cx, 46, sz, lerp_hex(t["accent"], t["accent2"], k)))
        o.append(txt(cx, 122, label, 12, t["text"], weight="500", ls="1.6"))

    # Divider.
    o.append('<rect x="60" y="164" width="880" height="1" fill="%s"/>' % t["faint"])
    o.append('<rect x="492" y="160" width="9" height="9" rx="1.5" fill="%s" '
             'transform="rotate(45 496.5 164.5)"/>' % t["accent"])

    # Tier 2 -- two rows of eight, muted.
    per, span2, sz2 = 8, 112, 24
    x0 = 500 - (per - 1) * span2 / 2.0
    for i, (slug, label) in enumerate(TIER2):
        row, col = i // per, i % per
        cx = x0 + col * span2
        top = 210 + row * 78
        o.append(icon(slug, cx, top, sz2, t["muted"], opacity="0.85"))
        o.append(txt(cx, top + 44, label, 10, t["muted"], ls="1.2"))

    o.append('</svg>')
    return "".join(o)


# ------------------------------------------------------------ components ----

def chip(x, y, label, t, size=10.5, pad=9, h=20):
    """Small outlined pill. Returns (svg, width) so a row can be laid out."""
    w = width_of(label, size, 0.8) + pad * 2
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="%.1f" fill="none" '
            'stroke="%s" stroke-width="1"/>%s'
            % (x, y, w, h, h / 2.0, t["faint"],
               txt("%.1f" % (x + w / 2.0), y + h / 2.0 + 3.6, label, size, t["muted"], ls="0.8")), w)


def motif(kind, t, accent, cx=120, cy=112):
    """The little animated emblem on the left of each project card."""
    o = []
    if kind == "notch":
        # A miniature Crest: the notch card, its equalizer and its light bar.
        o.append('<rect x="%d" y="%d" width="136" height="52" rx="14" fill="%s" stroke="%s"/>'
                 % (cx - 68, cy - 50, t["surface"], t["border"]))
        for i, h in enumerate([7, 16, 10, 19, 8]):
            o.append('<rect class="eq" x="%d" y="%d" width="4" height="%d" rx="2" fill="%s" '
                     'style="animation-delay:%.2fs"/>'
                     % (cx - 26 + i * 11, cy - 12 - h, h, accent, -0.32 * i))
        o.append('<rect x="%d" y="%d" width="108" height="2.5" rx="1.25" fill="%s"/>'
                 % (cx - 54, cy + 6, accent))
    elif kind == "loop":
        # A habit ring: a track, a filled arc, check nodes and one orbiting dot.
        r = 40
        circ = 2 * 3.14159 * r
        o.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="7"/>'
                 % (cx, cy, r, t["faint"]))
        o.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="7" '
                 'stroke-linecap="round" stroke-dasharray="%.1f %.1f" '
                 'transform="rotate(-90 %d %d)"/>'
                 % (cx, cy, r, accent, circ * 0.68, circ, cx, cy))
        o.append('<g class="orbit" style="transform-origin:%dpx %dpx">'
                 '<circle cx="%d" cy="%d" r="6" fill="%s"/></g>'
                 % (cx, cy, cx, cy - r, accent))
        o.append(txt(cx, cy + 5, "68%", 14, t["text"], weight="600", ls="0.5"))
    elif kind == "film":
        # A filmstrip with a playhead scrubbing across it.
        x0, y0, w, h = cx - 75, cy - 32, 150, 64
        o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" stroke="%s"/>'
                 % (x0, y0, w, h, t["surface"], t["border"]))
        for i in range(7):
            o.append('<rect x="%d" y="%d" width="7" height="5" rx="1" fill="%s"/>'
                     % (x0 + 7 + i * 20, y0 + 5, t["faint"]))
            o.append('<rect x="%d" y="%d" width="7" height="5" rx="1" fill="%s"/>'
                     % (x0 + 7 + i * 20, y0 + h - 10, t["faint"]))
        for i, op in enumerate([0.30, 0.55, 0.85, 0.55]):
            o.append('<rect x="%d" y="%d" width="30" height="28" rx="2" fill="%s" fill-opacity="%s"/>'
                     % (x0 + 8 + i * 35, cy - 14, accent, op))
        o.append('<g class="scrub"><rect x="%d" y="%d" width="2.5" height="%d" rx="1.25" fill="%s"/>'
                 '<circle cx="%.1f" cy="%d" r="4" fill="%s"/></g>'
                 % (x0 + 6, y0 - 6, h + 12, t["text"], x0 + 7.25, y0 - 9, t["text"]))
    return "".join(o)


def card_css():
    steps = []
    for pct, h in ((0, 7), (20, 16), (40, 10), (60, 19), (80, 8), (100, 7)):
        steps.append("%d%%{height:%dpx;y:%dpx}" % (pct, h, 100 - h))
    return ("<style>"
            "@keyframes eq{%s}"
            "@keyframes orbit{from{transform:rotate(0)}to{transform:rotate(360deg)}}"
            "@keyframes scrub{0%%{transform:translateX(0)}"
            "50%%{transform:translateX(132px)}100%%{transform:translateX(0)}}"
            ".eq{animation:eq 1.6s ease-in-out infinite}"
            ".orbit{transform-box:view-box;animation:orbit 7s linear infinite}"
            ".scrub{animation:scrub 5s ease-in-out infinite}"
            "@media(prefers-reduced-motion:reduce){.eq,.orbit,.scrub{animation:none}}"
            "</style>" % "".join(steps))


def card(theme, idx):
    t = THEMES[theme]
    p = PROJECTS[idx]
    W, H = 1000, 224
    accent = lerp_hex(t["accent"], t["accent2"], p["k"])

    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'role="img" aria-label="%s — %s">' % (W, H, W, H, esc(p["name"]), esc(p["tagline"]))]
    o.append(card_css())

    # Card body with an accent stripe down its leading edge.
    o.append('<rect x="0.5" y="0.5" width="%d" height="%d" rx="18" fill="%s" stroke="%s"/>'
             % (W - 1, H - 1, t["surface"], t["border"]))
    o.append('<path d="M18 0.5 H4 A3.5 3.5 0 0 0 0.5 4 V%d A3.5 3.5 0 0 0 4 %d H18 Z" fill="%s"/>'
             % (H - 4, H - 0.5, accent))

    o.append(motif(p["motif"], t, accent))
    o.append('<rect x="218" y="44" width="1" height="%d" fill="%s"/>' % (H - 88, t["faint"]))

    # Copy.
    o.append(txt(250, 52, "0%d" % (idx + 1), 11, accent, anchor="start", weight="600", ls="3"))
    o.append(txt(250, 90, p["name"], 26, t["text"], anchor="start", weight="600", ls="3"))
    o.append(txt(250, 120, p["tagline"], 13.5, accent, anchor="start", ls="0.4"))
    o.append(txt(250, 148, p["desc"], 12, t["muted"], anchor="start", ls="0.2"))

    x = 250
    for s in p["stack"]:
        svg, w = chip(x, 168, s, t)
        o.append(svg)
        x += w + 8

    # Meta rail on the right.
    o.append(txt(W - 40, 52, p["meta"], 11.5, t["muted"], anchor="end", ls="1.4"))
    o.append(txt(W - 40, 182, p["link"] + "  ↗", 11, accent, anchor="end", ls="0.4"))

    o.append('</svg>')
    return "".join(o)


# ---------------------------------------------------------------- ledger ----

def ledger(theme):
    """The work log: one rail, one node per project, a signal running down it."""
    t = THEMES[theme]
    rows = LEDGER
    W = 1000
    top, step = 56, 46
    H = top + step * len(rows) + 22

    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'role="img" aria-label="Selected work: %s">'
         % (W, H, W, H, esc(", ".join(r[0] for r in rows)))]
    o.append("<style>"
             "@keyframes node{0%,100%{opacity:.35}50%{opacity:1}}"
             ".node{animation:node 3.2s ease-in-out infinite}"
             "@media(prefers-reduced-motion:reduce){.node{animation:none}}"
             "</style>")

    railx = 58
    o.append('<rect x="%d" y="%d" width="1" height="%d" fill="%s"/>'
             % (railx, top - 18, step * len(rows) - 8, t["faint"]))

    for i, (name, lang, desc, live) in enumerate(rows):
        y = top + i * step
        colour = LANG_COLORS.get(lang, t["muted"])
        # The rail node carries the language colour, so no second swatch is needed.
        o.append('<circle class="node" cx="%d" cy="%d" r="5.5" fill="%s" style="animation-delay:%.2fs"/>'
                 % (railx, y - 4, colour, -0.28 * i))
        o.append(txt(88, y, lang, 11, t["muted"], anchor="start", ls="0.6"))
        o.append(txt(212, y, name, 14.5, t["text"], anchor="start", weight="600", ls="1.2"))
        o.append(txt(352, y, desc, 12.5, t["muted"], anchor="start", ls="0.2"))
        if live:
            o.append(txt(W - 44, y, "↗", 13, t["accent"], anchor="end"))

    o.append('</svg>')
    return "".join(o)


# --------------------------------------------------------------- signals ----

def signals(theme):
    """Replaces the stock activity graph and the snake with real numbers:
    headline counts, language split and a trailing-year push timeline."""
    t = THEMES[theme]
    W, H = 1000, 384
    d = DATA

    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'role="img" aria-label="%d repos, %d stars, %d followers, %s years shipping">'
         % (W, H, W, H, d["repos"], d["stars"], d["followers"], d["years"])]
    o.append("<style>"
             "@keyframes sheen{0%{transform:translateX(-260px)}100%{transform:translateX(1000px)}}"
             "@keyframes bar{0%,100%{opacity:.62}50%{opacity:1}}"
             ".sheen{animation:sheen 5.5s ease-in-out infinite}"
             ".bar{animation:bar 3.4s ease-in-out infinite}"
             "@media(prefers-reduced-motion:reduce){.sheen,.bar{animation:none}}"
             "</style>")
    o.append('<defs><linearGradient id="sh" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="#FFF" stop-opacity="0"/>'
             '<stop offset="0.5" stop-color="#FFF" stop-opacity="%s"/>'
             '<stop offset="1" stop-color="#FFF" stop-opacity="0"/></linearGradient>'
             '<clipPath id="barclip"><rect x="60" y="176" width="880" height="26" rx="13"/>'
             '</clipPath></defs>' % (0.20 if theme == "dark" else 0.55))

    # Headline numbers.
    stats = [(str(d["repos"]), "REPOSITORIES"), (str(d["live"]), "LIVE DEPLOYS"),
             (str(len(d["languages"])), "LANGUAGES"), (str(d["years"]), "YEARS SHIPPING")]
    for i, (n, label) in enumerate(stats):
        cx = 125 + i * 250
        o.append(txt(cx, 66, n, 38, lerp_hex(t["accent"], t["accent2"], i / 3.0),
                     weight="600", ls="1"))
        o.append(txt(cx, 92, label, 10.5, t["muted"], ls="2.4"))

    o.append('<rect x="60" y="120" width="880" height="1" fill="%s"/>' % t["faint"])

    # Language split.
    o.append(txt(60, 156, "REPOS BY PRIMARY LANGUAGE", 10.5, t["muted"], anchor="start", ls="2.2"))
    total = sum(c for _, c in d["languages"]) or 1
    x = 60.0
    for lang, count in d["languages"]:
        w = 880.0 * count / total
        o.append('<rect x="%.1f" y="176" width="%.1f" height="26" fill="%s" clip-path="url(#barclip)"/>'
                 % (x, w, LANG_COLORS.get(lang, t["muted"])))
        x += w
    o.append('<g clip-path="url(#barclip)"><rect class="sheen" x="0" y="176" width="260" '
             'height="26" fill="url(#sh)"/></g>')

    lx = 60.0
    for lang, count in d["languages"]:
        o.append('<circle cx="%.1f" cy="%d" r="4" fill="%s"/>'
                 % (lx + 4, 226, LANG_COLORS.get(lang, t["muted"])))
        label = "%s %d" % (lang, count)
        o.append(txt("%.1f" % (lx + 16), 230, label, 11, t["muted"], anchor="start", ls="0.5"))
        lx += width_of(label, 11, 0.5) + 42

    o.append('<rect x="60" y="258" width="880" height="1" fill="%s"/>' % t["faint"])

    # Trailing-year push timeline.
    o.append(txt(60, 292, "REPOS PUSHED, LAST 12 MONTHS", 10.5, t["muted"], anchor="start", ls="2.2"))
    base, peak = 356, max(d["pushed"]) or 1
    slot = 880.0 / len(d["pushed"])
    for i, v in enumerate(d["pushed"]):
        bw = slot - 26
        bx = 60 + i * slot + 13
        bh = max(3.0, 44.0 * v / peak)
        o.append('<rect class="bar" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s" '
                 'style="animation-delay:%.2fs"/>'
                 % (bx, base - bh, bw, bh, lerp_hex(t["accent"], t["accent2"], i / 11.0), -0.22 * i))
        o.append(txt("%.1f" % (bx + bw / 2.0), base + 16, d["months"][i][5:], 9.5, t["muted"], ls="0.4"))

    o.append('</svg>')
    return "".join(o)


# ---------------------------------------------------------------- footer ----

AVAILABILITY = "OPEN TO INTERNSHIPS  ·  FREELANCE BUILDS  ·  ANYTHING THAT SHIPS"
CONTACT      = "lennydany3@gmail.com"


def footer(theme):
    """The bookend. The hero's notch hangs from the top of the page; this one
    hangs from the bottom, with its light bar along the upper edge, so the
    README opens and closes on the same shape."""
    t = THEMES[theme]
    W, H = 1000, 252

    NX, NW = 130, 740
    TOP = 64                      # upper edge of the notch
    NH = H - TOP + 28             # runs past the canvas so the bottom is cut off

    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'role="img" aria-label="%s — %s">' % (W, H, W, H, esc(AVAILABILITY), esc(CONTACT))]
    o.append("<style>"
             "@keyframes blink{0%,45%{opacity:1}50%,95%{opacity:0}100%{opacity:1}}"
             ".cursor{animation:blink 1.1s step-end infinite}"
             "@media(prefers-reduced-motion:reduce){.cursor{animation:none}}"
             "</style>")
    o.append('<defs>'
             '<linearGradient id="a" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
             '<filter id="g" x="-40%%" y="-200%%" width="180%%" height="500%%">'
             '<feGaussianBlur stdDeviation="19"/></filter>'
             '</defs>' % (t["accent"], t["accent2"]))

    o.append(dotgrid(W, H, t["faint"]))

    # Bloom sitting above the notch, mirroring the hero's.
    o.append('<rect x="%d" y="%d" width="%d" height="44" rx="22" fill="url(#a)" '
             'fill-opacity="%s" filter="url(#g)"/>' % (NX + 40, TOP - 14, NW - 80, t["glow"]))

    o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="30" fill="%s" stroke="%s"/>'
             % (NX, TOP, NW, NH, t["surface"], t["border"]))
    o.append('<rect x="%d" y="%d" width="%d" height="2.5" rx="1.25" fill="url(#a)"/>'
             % (NX + 54, TOP - 0.5, NW - 108))

    # $ exit -- the terminal closing on the same prompt the hero opened with.
    word = "exit"
    ww = width_of(word, 17, 0.3)
    x0 = 500 - (24 + ww) / 2.0
    o.append(txt("%.1f" % x0, 124, "$", 17, t["accent"], anchor="start", weight="600"))
    o.append(txt("%.1f" % (x0 + 24), 124, word, 17, t["text"], anchor="start", ls="0.3"))
    o.append('<rect class="cursor" x="%.1f" y="%d" width="10" height="18" fill="%s"/>'
             % (x0 + 24 + ww + 5, 110, t["accent"]))

    o.append(txt(500, 166, AVAILABILITY, 12, t["muted"], ls="2.2"))
    o.append(txt(500, 208, CONTACT, 13, t["accent"], ls="0.6"))

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
        write("ledger-%s.svg" % theme, ledger(theme))
        write("signals-%s.svg" % theme, signals(theme))
        write("footer-%s.svg" % theme, footer(theme))
        for i, p in enumerate(PROJECTS):
            write("card-%s-%s.svg" % (p["key"], theme), card(theme, i))
    write("rule.svg", divider())
    print("\ndata from %s" % DATA["generated"])
    print("done")
