"""Generates the animated green-phosphor terminal SVG for the GitHub profile README.

    python gen.py assets/terminal.svg      (needs: pip install pyfiglet)
"""

import sys
from html import escape
from pathlib import Path

import pyfiglet

OUT = Path(sys.argv[1])

FONT = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"
FS = 14  # font size
CW = 8.43  # nominal char width at FS (layout grid)
LH = 19  # line height
BEZEL = 16
PAD_X = BEZEL + 26
TOP = BEZEL + 40  # first baseline

C = {
    "screen": "#041a0c",
    "bezel": "#151915",
    "hi": "#c8ffd6",  # brightest phosphor
    "fg": "#41ff80",
    "mid": "#22b356",
    "dim": "#11602d",
    "inv": "#041a0c",  # text on inverted (lit) background
}

# ---- art --------------------------------------------------------------------

banner = [
    l.rstrip()
    for l in pyfiglet.figlet_format("LUCAS LEITE", font="ansi_shadow", width=200).splitlines()
    if l.strip()
]
BW = max(len(l) for l in banner)
banner = [l.ljust(BW) for l in banner]

# Retro-futurist tin robot, drawn as pixel art. Only the left half is authored;
# each row is mirrored, then the asymmetric details are stamped on top.
#   @ brightest   # phosphor   o mid   : dim   (space) off
ROBOT_HALF = """\
               @
              @@
               @
               #
               #
          ######
        ##oooooo
       #oo:::::o
       #o::::::o
     ###o:@@@::o
     #:#o:@@@::o
     ###o::::::o
       #o:#:#:#o
       #o:#:#:#o
       #oo:::::o
        ##oooooo
          ######
           #oooo
     ###########
    #oo#ooooooooo
   #oo#:::::::::o
   #o# #:@@:::@@o
   #o# #::::::::o
   #o# #:ooooooo:
   #o# #:o:::::o:
   #o# #:ooooooo:
   #o# #::::::::o
  ##o## #oooooooo
  #: :#  #######
  #: :#   #oo# o
          #oo#
          ####
          #oo#
          #oo#
       #######
      ########"""


def mirror(row, width=16):
    row = row.ljust(width)[:width]
    return row + row[::-1]


robot = [mirror(r) for r in ROBOT_HALF.splitlines()]
# dials on the chest panel and a rivet line: break the symmetry a little
for r, c, ch in [(24, 13, "@"), (24, 18, "#"), (24, 19, "#"), (23, 16, "@"), (25, 16, "@")]:
    robot[r] = robot[r][:c] + ch + robot[r][c + 1 :]
ROBOT_COLS = len(robot[0])
PX = 7  # robot pixel size

info = [
    ("title", "LUCAS@LEITE"),
    ("rule", "=" * 11),
    ("OS", "CONTROL & AUTOMATION ENGINEER -> SOFTWARE"),
    ("HOST", "ORLANDO, FL"),
    ("UPTIME", "13 YEARS SHIPPING (SINCE 2013)"),
    ("ROLE", "PRINCIPAL SOFTWARE ENGINEER"),
    ("SHELL", "ZSH + CLAUDE CODE"),
    ("LANGS", "ELIXIR · TYPESCRIPT · PYTHON · C++ · SWIFT"),
    ("STACK", "PHOENIX LIVEVIEW · DJANGO · REACT · NEXT.JS"),
    ("INFRA", "AWS · GCP · TERRAFORM · KUBERNETES"),
    ("AI", "CLAUDE AGENT SDK · MCP · AGENTS · VECTORS"),
    ("METAL", "ESP32 · C · EMBEDDED · CAD · 3D PRINTING"),
    ("AWARD", "1ST PLACE WORLDWIDE, ROBOTICS ENGINEERING"),
    ("STATUS", "BUILDING ROBOTS, GAMES & AI TOOLING"),
    ("xp", ""),
]
KEY_W = 8

# ---- composition ------------------------------------------------------------

parts = []
y = TOP
t = 0.3  # animation clock (seconds)


def appear(begin, dur=0.12):
    return f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="{dur}s" fill="freeze"/>'


def line(text, x, yy, fill, begin, extra=""):
    return f'<text x="{x:.1f}" y="{yy}" fill="{fill}" xml:space="preserve" opacity="0"{extra}>{escape(text)}{appear(begin)}</text>'


def prompt(cmd, begin, cid):
    """'> CMD' whose command types itself out behind an expanding clip."""
    global y
    x_cmd = PAD_X + 2 * CW
    w = len(cmd) * CW + 2
    dur = max(0.35, len(cmd) * 0.05)
    parts.append(
        f'<clipPath id="{cid}"><rect x="{x_cmd:.1f}" y="{y - FS}" width="0" height="{LH + 4}">'
        f'<animate attributeName="width" from="0" to="{w:.1f}" begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
        f"</rect></clipPath>"
    )
    parts.append(line(">", PAD_X, y, C["fg"], begin - 0.2))
    parts.append(f'<text x="{x_cmd:.1f}" y="{y}" fill="{C["hi"]}" clip-path="url(#{cid})">{escape(cmd)}</text>')
    y += LH
    return begin + dur + 0.3


# header, Fallout-terminal style
parts.append(line("LEITE INDUSTRIES (TM) TERMLINK PROTOCOL", PAD_X, y, C["fg"], t))
y += LH
t += 0.25
t = prompt("LOGON LUCAS", t, "c0")
hdr = " WELCOME, OVERSEER. "
parts.append(
    f'<g opacity="0">{appear(t)}<rect x="{PAD_X:.1f}" y="{y - FS + 1}" width="{len(hdr) * CW:.1f}" height="{LH - 1}" fill="{C["fg"]}"/>'
    f'<text x="{PAD_X:.1f}" y="{y}" fill="{C["inv"]}" font-weight="bold" xml:space="preserve">{hdr}</text></g>'
)
y += LH * 2
t += 0.5

# ---- banner (vectors: font block glyphs leave hairline gaps between rows) ----
t = prompt("FIGLET LUCAS LEITE", t, "c1")
SHADOW = {
    "═": [("w", "e")],
    "║": [("n", "s")],
    "╗": [("w", "c"), ("c", "s")],
    "╝": [("w", "c"), ("c", "n")],
    "╔": [("e", "c"), ("c", "s")],
    "╚": [("e", "c"), ("c", "n")],
}
for row in banner:
    top = y - LH + 5
    rects, strokes = [], []
    for i, ch in enumerate(row):
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
        f'<g opacity="0">{appear(t)}<g fill="{C["fg"]}">{"".join(rects)}</g>'
        f'<path d="{" ".join(strokes)}" stroke="{C["mid"]}" stroke-width="1.1" fill="none"/></g>'
    )
    y += LH
    t += 0.07
tag = "CONTROL & AUTOMATION ENGINEER  //  PRINCIPAL SOFTWARE ENGINEER  //  BUILDER OF WEIRD THINGS"
parts.append(line(tag, PAD_X, y + 4, C["mid"], t + 0.1))
y += LH * 2
t += 0.8

# ---- neofetch: pixel robot + info ------------------------------------------
t = prompt("NEOFETCH", t, "c2")
y += 4
block_top = y - FS
info_h = len(info) * LH
robot_h = len(robot) * PX
robot_top = block_top + max(0, (info_h - robot_h) // 2)
info_x = PAD_X + ROBOT_COLS * PX + 40
val_x = info_x + KEY_W * CW

shade = {"@": C["hi"], "#": C["fg"], "o": C["mid"], ":": C["dim"]}
rt = t
eyes = []
PX_X = lambda c: PAD_X + c * PX
for r, row in enumerate(robot):
    rects = []
    for c, ch in enumerate(row):
        if ch == "@":
            eyes.append(f'<rect x="{PX_X(c)}" y="{robot_top + r * PX}" width="{PX}" height="{PX}"/>')
        if ch in shade:
            rects.append(
                f'<rect x="{PAD_X + c * PX}" y="{robot_top + r * PX}" width="{PX}" height="{PX}" fill="{shade[ch]}"/>'
            )
    parts.append(f'<g opacity="0">{appear(rt, 0.05)}{"".join(rects)}</g>')
    rt += 0.035
# antenna + eyes pulse once the robot is drawn
parts.append(
    f'<g fill="#ffffff" opacity="0">'
    f'<animate attributeName="opacity" values="0;0.55;0" dur="2.4s" begin="{rt:.2f}s" repeatCount="indefinite"/>{"".join(eyes)}</g>'
)
parts.append(
    f'<g opacity="0">{appear(rt)}'
    f'<circle cx="{PAD_X + 16 * PX}" cy="{robot_top + 1.5 * PX}" r="{PX * 2.6}" fill="{C["hi"]}" opacity="0.18">'
    f'<animate attributeName="opacity" values="0.05;0.35;0.05" dur="2.4s" begin="{rt:.2f}s" repeatCount="indefinite"/></circle></g>'
)

for i, (k, v) in enumerate(info):
    yy = y + i * LH
    if k == "title":
        g = f'<text x="{info_x:.1f}" y="{yy}" fill="{C["hi"]}" font-weight="bold">{v}</text>'
    elif k == "rule":
        g = f'<text x="{info_x:.1f}" y="{yy}" fill="{C["dim"]}">{v}</text>'
    elif k == "xp":
        g = (
            f'<text x="{info_x:.1f}" y="{yy}" fill="{C["fg"]}" font-weight="bold">LVL 13</text>'
            f'<rect x="{val_x:.1f}" y="{yy - FS + 3}" width="{22 * CW:.1f}" height="{FS - 2}" fill="none" stroke="{C["mid"]}"/>'
            f'<rect x="{val_x + 2:.1f}" y="{yy - FS + 5}" width="0" height="{FS - 6}" fill="{C["fg"]}">'
            f'<animate attributeName="width" from="0" to="{22 * CW * 0.86:.1f}" begin="{t + i * 0.06:.2f}s" dur="1.6s" fill="freeze"/></rect>'
            f'<text x="{val_x + 23 * CW:.1f}" y="{yy}" fill="{C["mid"]}">XP</text>'
        )
    else:
        g = (
            f'<text x="{info_x:.1f}" y="{yy}" fill="{C["hi"]}" font-weight="bold">{escape(k)}</text>'
            f'<text x="{val_x:.1f}" y="{yy}" fill="{C["fg"]}">{escape(v)}</text>'
        )
    parts.append(f'<g opacity="0">{appear(t + i * 0.06)}{g}</g>')
t = max(rt, t + len(info) * 0.06) + 0.4
y = max(y + info_h, robot_top + robot_h + FS) + LH

# ---- final prompt + blinking block cursor -----------------------------------
parts.append(
    f'<g opacity="0">{appear(t, 0.05)}<text x="{PAD_X}" y="{y}" fill="{C["fg"]}">&gt;</text>'
    f'<rect x="{PAD_X + 2 * CW:.1f}" y="{y - FS + 1}" width="{CW:.1f}" height="{FS + 2}" fill="{C["fg"]}">'
    f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" begin="{t:.2f}s" repeatCount="indefinite"/>'
    f"</rect></g>"
)
y += LH

W = int(PAD_X * 2 + max(BW, len(tag), (info_x - PAD_X) / CW + KEY_W + 42) * CW)
H = int(y + BEZEL + 10)
SW, SH = W - 2 * BEZEL, H - 2 * BEZEL

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Green-phosphor terminal: LEITE INDUSTRIES TERMLINK. figlet LUCAS LEITE, then neofetch next to a pixel-art robot: control and automation engineer turned principal software engineer; Elixir, TypeScript, Python, C++, Swift.">
  <defs>
    <filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
      <feGaussianBlur stdDeviation="2.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse">
      <rect width="4" height="1" fill="#000" opacity="0.45"/>
    </pattern>
    <radialGradient id="vignette" cx="50%" cy="50%" r="75%">
      <stop offset="0.55" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity="0.75"/>
    </radialGradient>
    <radialGradient id="phosphor" cx="50%" cy="45%" r="70%">
      <stop offset="0" stop-color="#0a2e16"/>
      <stop offset="1" stop-color="{C['screen']}"/>
    </radialGradient>
    <linearGradient id="roll" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{C['fg']}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{C['fg']}" stop-opacity="0.07"/>
      <stop offset="1" stop-color="{C['fg']}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="screen"><rect x="{BEZEL}" y="{BEZEL}" width="{SW}" height="{SH}" rx="22"/></clipPath>
  </defs>
  <rect width="{W}" height="{H}" rx="20" fill="{C['bezel']}"/>
  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="19" fill="none" stroke="#2a302a" stroke-width="2"/>
  <g clip-path="url(#screen)">
    <rect x="{BEZEL}" y="{BEZEL}" width="{SW}" height="{SH}" fill="url(#phosphor)"/>
    <g font-family="{FONT}" font-size="{FS}" filter="url(#glow)">
      <animate attributeName="opacity" values="1;0.94;1;0.97;1" dur="0.21s" repeatCount="indefinite"/>
      {chr(10).join("      " + p for p in parts).strip()}
    </g>
    <rect x="{BEZEL}" y="{BEZEL}" width="{SW}" height="{SH}" fill="url(#scan)"/>
    <rect x="{BEZEL}" y="{BEZEL - 120}" width="{SW}" height="120" fill="url(#roll)">
      <animateTransform attributeName="transform" type="translate" from="0 0" to="0 {SH + 120}" dur="7s" repeatCount="indefinite"/>
    </rect>
    <rect x="{BEZEL}" y="{BEZEL}" width="{SW}" height="{SH}" fill="url(#vignette)"/>
  </g>
</svg>
"""
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg)
print(f"wrote {OUT} ({W}x{H}, {len(svg)} bytes)")
