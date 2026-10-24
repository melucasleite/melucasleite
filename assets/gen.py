"""Generates the animated terminal SVG for the GitHub profile README."""

import sys
from html import escape
from pathlib import Path

import pyfiglet

OUT = Path(sys.argv[1])

FONT = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"
FS = 14  # font size
CW = 8.43  # nominal char width at FS (used for layout + textLength)
LH = 19  # line height
PAD_X = 28
TOP = 64  # first baseline below the title bar

C = {
    "bg": "#0f1117",
    "bar": "#1a1d27",
    "fg": "#c0caf5",
    "dim": "#565f89",
    "blue": "#7aa2f7",
    "cyan": "#7dcfff",
    "green": "#9ece6a",
    "magenta": "#bb9af7",
    "orange": "#ff9e64",
    "red": "#f7768e",
    "yellow": "#e0af68",
}

banner = [
    l.rstrip()
    for l in pyfiglet.figlet_format("LUCAS LEITE", font="ansi_shadow", width=200).splitlines()
    if l.strip()
]
BW = max(len(l) for l in banner)
banner = [l.ljust(BW) for l in banner]

robot = r"""
          .-------------.
         /  .--.   .--.  \
        |  | () | | () |  |
        |   '--'   '--'   |
        |    .-------.    |
         \   '-------'   /
     .----'-------------'----.
    /  [o]   |  L L  |   [o]  \
   |  ----   |_______|   ----  |
    \_______/   | |   \_______/
                | |
          .-----' '-----.
         |  ___________  |
         '-'           '-'
""".strip("\n").splitlines()

info = [
    ("title", "lucas@leite"),
    ("rule", "-" * 11),
    ("OS", "control & automation engineer -> software"),
    ("Host", "orlando, fl"),
    ("Uptime", "13 years shipping (since 2013)"),
    ("Role", "principal software engineer"),
    ("Shell", "zsh + claude code"),
    ("Langs", "elixir · typescript · python · c++ · swift"),
    ("Stack", "phoenix liveview · django · react · next.js"),
    ("Infra", "aws · gcp · terraform · kubernetes"),
    ("AI", "claude agent sdk · mcp · agents · vectors"),
    ("Metal", "esp32 · c · embedded · cad · 3d printing"),
    ("Award", "1st place worldwide, robotics engineering"),
    ("Status", "building robots, games & ai tooling"),
    ("blocks", ""),
]

LOGO_W = 33  # chars reserved for the robot column
KEY_W = 8

parts = []
y = TOP
t = 0.4  # animation clock (seconds)


def appear(begin, dur=0.12):
    return f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="{dur}s" fill="freeze"/>'


def prompt(cmd, begin, cid):
    """A zsh-style prompt whose command 'types' itself via an expanding clip."""
    global y
    p1, p2 = "lucas@leite", " ~ ❯ "
    x_cmd = PAD_X + (len(p1) + len(p2)) * CW
    w = len(cmd) * CW + 2
    type_dur = max(0.35, len(cmd) * 0.045)
    parts.append(
        f'<clipPath id="{cid}"><rect x="{x_cmd:.1f}" y="{y - FS}" width="0" height="{LH + 4}">'
        f'<animate attributeName="width" from="0" to="{w:.1f}" begin="{begin:.2f}s" dur="{type_dur:.2f}s" fill="freeze"/>'
        f"</rect></clipPath>"
    )
    parts.append(
        f'<g opacity="0">{appear(begin - 0.25, 0.05)}'
        f'<text x="{PAD_X}" y="{y}"><tspan fill="{C["green"]}" font-weight="bold">{p1}</tspan>'
        f'<tspan fill="{C["blue"]}" font-weight="bold">{escape(p2)}</tspan></text>'
        f'<text x="{x_cmd:.1f}" y="{y}" fill="{C["fg"]}" clip-path="url(#{cid})">{escape(cmd)}</text></g>'
    )
    y += LH
    return begin + type_dur + 0.35


# ---- session 1: figlet banner ----------------------------------------------
t = prompt('figlet -f "ANSI Shadow" lucas leite', t, "c1")
# Drawn as vectors, not text: font block glyphs never quite fill the line box,
# which leaves hairline gaps between rows. █ becomes a cell rect, the box-drawing
# "shadow" becomes double strokes.
SHADOW = {  # (from-edge, to-edge) pairs through the cell centre
    "═": [("w", "e")],
    "║": [("n", "s")],
    "╗": [("w", "c"), ("c", "s")],
    "╝": [("w", "c"), ("c", "n")],
    "╔": [("e", "c"), ("c", "s")],
    "╚": [("e", "c"), ("c", "n")],
}
for line in banner:
    top = y - LH + 5
    rects, strokes = [], []
    for i, ch in enumerate(line):
        x0 = PAD_X + i * CW
        if ch == "█":
            rects.append(f'<rect x="{x0:.2f}" y="{top}" width="{CW + 0.3:.2f}" height="{LH + 0.3}"/>')
        elif ch in SHADOW:
            cx, cy = x0 + CW / 2, top + LH / 2
            pts = {"w": (x0, cy), "e": (x0 + CW, cy), "n": (cx, top), "s": (cx, top + LH), "c": (cx, cy)}
            for a, b in SHADOW[ch]:
                (ax, ay), (bx, by) = pts[a], pts[b]
                for off in (-1.6, 1.6):
                    dx, dy = (0, off) if ay == by else (off, 0)
                    strokes.append(f"M{ax + dx:.2f} {ay + dy:.2f}L{bx + dx:.2f} {by + dy:.2f}")
    parts.append(
        f'<g opacity="0">{appear(t)}<g fill="url(#grad)">{"".join(rects)}</g>'
        f'<path d="{" ".join(strokes)}" stroke="url(#grad)" stroke-width="1.1" opacity="0.55" fill="none"/></g>'
    )
    y += LH
    t += 0.07
tag = "control & automation engineer  //  principal software engineer  //  builder of weird things"
parts.append(
    f'<text x="{PAD_X}" y="{y + 4}" fill="{C["dim"]}" xml:space="preserve" opacity="0">{escape(tag)}{appear(t + 0.1, 0.4)}</text>'
)
y += LH * 2
t += 0.9

# ---- session 2: neofetch ----------------------------------------------------
t = prompt("neofetch", t, "c2")
y += 6
rows = max(len(robot), len(info))
info_x = PAD_X + LOGO_W * CW
val_x = info_x + KEY_W * CW
for i in range(rows):
    g = []
    if i < len(robot):
        shade = C["cyan"] if i < 6 else C["blue"] if i < 10 else C["magenta"]
        g.append(f'<text x="{PAD_X}" y="{y}" fill="{shade}" xml:space="preserve">{escape(robot[i])}</text>')
    if i < len(info):
        k, v = info[i]
        if k == "title":
            g.append(
                f'<text x="{info_x:.1f}" y="{y}" font-weight="bold"><tspan fill="{C["green"]}">lucas</tspan>'
                f'<tspan fill="{C["fg"]}">@</tspan><tspan fill="{C["green"]}">leite</tspan></text>'
            )
        elif k == "rule":
            g.append(f'<text x="{info_x:.1f}" y="{y}" fill="{C["dim"]}">{v}</text>')
        elif k == "blocks":
            cols = ["red", "orange", "yellow", "green", "cyan", "blue", "magenta", "fg"]
            for j, c in enumerate(cols):
                g.append(f'<rect x="{info_x + j * 3 * CW:.1f}" y="{y - FS + 3}" width="{3 * CW:.1f}" height="{FS}" fill="{C[c]}"/>')
        else:
            g.append(f'<text x="{info_x:.1f}" y="{y}" fill="{C["blue"]}" font-weight="bold">{escape(k)}</text>')
            g.append(f'<text x="{val_x:.1f}" y="{y}" fill="{C["fg"]}">{escape(v)}</text>')
    parts.append(f'<g opacity="0">{appear(t)}{"".join(g)}</g>')
    y += LH
    t += 0.06
y += LH

# ---- final prompt + blinking cursor ------------------------------------------
t += 0.3
x_cur = PAD_X + len("lucas@leite ~ ❯ ") * CW
parts.append(
    f'<g opacity="0">{appear(t, 0.05)}'
    f'<text x="{PAD_X}" y="{y}" font-weight="bold"><tspan fill="{C["green"]}">lucas@leite</tspan>'
    f'<tspan fill="{C["blue"]}"> ~ ❯ </tspan></text>'
    f'<rect x="{x_cur:.1f}" y="{y - FS + 2}" width="{CW:.1f}" height="{FS + 2}" fill="{C["fg"]}">'
    f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" begin="{t:.2f}s" repeatCount="indefinite"/>'
    f"</rect></g>"
)
y += LH

W = int(PAD_X * 2 + max(BW, LOGO_W + KEY_W + 44, len(tag)) * CW)
H = int(y + 10)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal: figlet LUCAS LEITE, then neofetch — principal software engineer, control and automation engineer, Elixir, TypeScript, Python, C++, Swift">
  <defs>
    <linearGradient id="grad" x1="0" y1="0" x2="{W}" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{C['cyan']}"/>
      <stop offset="0.5" stop-color="{C['blue']}"/>
      <stop offset="1" stop-color="{C['magenta']}"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="0 0; {W // 3} 0; 0 0" dur="8s" repeatCount="indefinite"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" rx="12" fill="{C['bg']}"/>
  <rect width="{W}" height="36" rx="12" fill="{C['bar']}"/>
  <rect y="24" width="{W}" height="12" fill="{C['bar']}"/>
  <circle cx="22" cy="18" r="6" fill="#ff5f57"/>
  <circle cx="42" cy="18" r="6" fill="#febc2e"/>
  <circle cx="62" cy="18" r="6" fill="#28c840"/>
  <text x="{W / 2}" y="23" text-anchor="middle" fill="{C['dim']}" font-family="{FONT}" font-size="12">lucas@leite: ~ — zsh — {W // 9}×{(H - 40) // LH}</text>
  <g font-family="{FONT}" font-size="{FS}">
    {chr(10).join("    " + p for p in parts).strip()}
  </g>
</svg>
"""
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg)
print(f"wrote {OUT} ({W}x{H}, {len(svg)} bytes)")
