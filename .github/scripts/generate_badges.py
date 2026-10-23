#!/usr/bin/env python3
"""Generate LiveEdit contributor badge SVGs into .github/badges/.

Edit BADGES below (file name, title, subtitle, colour, icon) and re-run:
    python .github/scripts/generate_badges.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "badges"

# Icons are drawn white on a 24x24 grid.
ICONS = {
    "merge": '<circle cx="6" cy="5" r="2.4"/><circle cx="6" cy="19" r="2.4"/><circle cx="18" cy="12" r="2.4"/>'
             '<path d="M6 7.4v9.2M6 12h5.5a4 4 0 0 0 4-.2" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>',
    "bug": '<ellipse cx="12" cy="13.5" rx="4.6" ry="6"/><circle cx="12" cy="6.2" r="2.4"/>'
           '<path d="M7 11H3.5M17 11h3.5M7.4 16H4M16.6 16H20M8.5 8L6 5.5M15.5 8L18 5.5" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round"/>',
    "doc": '<path d="M6 2.5h8l4.5 4.5v14a1 1 0 0 1-1 1h-11.5a1 1 0 0 1-1-1v-17.5a1 1 0 0 1 1-1z"/>'
           '<path d="M8.5 12h7M8.5 15.5h7M8.5 8.5h3" fill="none" stroke="#0f172a" stroke-width="1.6" stroke-linecap="round"/>',
    "pixel": '<rect x="3" y="3" width="5" height="5"/><rect x="10" y="3" width="5" height="5" opacity=".55"/>'
             '<rect x="17" y="3" width="4" height="5"/><rect x="3" y="10" width="5" height="5" opacity=".55"/>'
             '<rect x="10" y="10" width="5" height="5"/><rect x="17" y="10" width="4" height="5" opacity=".55"/>'
             '<rect x="3" y="17" width="5" height="4"/><rect x="10" y="17" width="5" height="4" opacity=".55"/>'
             '<rect x="17" y="17" width="4" height="4"/>',
    "wave": '<g stroke="#fff" stroke-width="2.6" stroke-linecap="round"><path d="M4 10v4"/><path d="M8 6v12"/>'
            '<path d="M12 3v18"/><path d="M16 7v10"/><path d="M20 10v4"/></g>',
    "star": '<path d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3 6.1 20.6l1.3-6.6L2.5 9.4l6.6-.8z"/>',
}

BADGES = [
    # file,             title,              subtitle,                     colour,    icon
    ("first-pr",        "First PR Merged",  "Welcome to the crew",        "#6366f1", "merge"),
    ("test-hero",       "Test Hero",        "Made the suite stronger",    "#10b981", "check"),
    ("bug-squasher",    "Bug Squasher",     "One fewer bug in the wild",  "#ef4444", "bug"),
    ("docs-champion",   "Docs Champion",    "Made it easier to start",    "#3b82f6", "doc"),
    ("pixel-perfect",   "Pixel Perfect",    "Sweated the small stuff",    "#ec4899", "pixel"),
    ("audio-alchemist", "Audio Alchemist",  "Turned sound into magic",    "#f59e0b", "wave"),
    ("contributor",     "Hacktoberfest",    "LiveEdit contributor 2026",  "#8b5cf6", "star"),
]

FONT = "Segoe UI, Helvetica, Arial, sans-serif"

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="300" height="96" viewBox="0 0 300 96" role="img" aria-label="{title} - LiveEdit Hacktoberfest 2026">
  <title>{title} - LiveEdit Hacktoberfest 2026</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1e293b"/><stop offset="1" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{c}"/><stop offset="1" stop-color="{c}" stop-opacity=".55"/>
    </linearGradient>
  </defs>
  <rect x="1.5" y="1.5" width="297" height="93" rx="16" fill="url(#bg)" stroke="{c}" stroke-width="3"/>
  <circle cx="52" cy="48" r="32" fill="url(#ring)"/>
  <circle cx="52" cy="48" r="32" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="2"/>
  <g transform="translate(34 30) scale(1.5)" fill="#fff">{icon}</g>
  <text x="102" y="30" font-family="{font}" font-size="10" font-weight="700" letter-spacing="2" fill="{c}">LIVEEDIT 2026</text>
  <text x="102" y="56" font-family="{font}" font-size="{fs}" font-weight="800" fill="#f8fafc">{title}</text>
  <text x="102" y="76" font-family="{font}" font-size="12" fill="#94a3b8">{sub}</text>
</svg>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for file, title, sub, colour, icon in BADGES:
        fs = 22 if len(title) <= 12 else 20
        svg = TEMPLATE.format(title=title, sub=sub, c=colour, icon=ICONS[icon], fs=fs, font=FONT)
        (OUT / f"{file}.svg").write_text(svg, encoding="utf-8")
        print("wrote", OUT / f"{file}.svg")


if __name__ == "__main__":
    main()
