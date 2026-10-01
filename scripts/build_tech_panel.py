"""Build a compact claymorphic technology ecosystem SVG."""

from __future__ import annotations

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "assets" / "icons"
OUT = ROOT / "assets" / "tech-ecosystem.svg"

TOOLS = [
    ("Java", "java", "https://www.java.com/"),
    ("Python", "python", "https://www.python.org/"),
    ("C++", "cplusplus", "https://isocpp.org/"),
    ("HTML", "html5", "https://developer.mozilla.org/en-US/docs/Web/HTML"),
    ("CSS", "css3", "https://developer.mozilla.org/en-US/docs/Web/CSS"),
    ("JavaScript", "javascript", "https://developer.mozilla.org/en-US/docs/Web/JavaScript"),
    ("React", "react", "https://react.dev/"),
    ("Node.js", "nodedotjs", "https://nodejs.org/"),
    ("MongoDB", "mongodb", "https://www.mongodb.com/"),
    ("MySQL", "mysql", "https://www.mysql.com/"),
    ("Firebase", "firebase", "https://firebase.google.com/"),
    ("Supabase", "supabase", "https://supabase.com/"),
    ("Git", "git", "https://git-scm.com/"),
    ("Figma", "figma", "https://www.figma.com/"),
    ("Antigravity", None, ""),
    ("Base44", None, ""),
    ("Terminal", "terminal", "https://en.wikipedia.org/wiki/Terminal_(computing)"),
    ("Spyder IDE", None, "https://www.spyder-ide.org/"),
    ("VS Code", "visualstudiocode", "https://code.visualstudio.com/"),
    ("Stitch", None, ""),
    ("Claude", "claude", "https://claude.ai/"),
    ("OpenClaw", None, ""),
    ("Ollama", "ollama", "https://ollama.com/"),
]

CUSTOM = {
    "Antigravity": ("AG", "#8d7aff"),
    "Base44": ("B44", "#ff9d6c"),
    "Spyder IDE": ("SP", "#50d890"),
    "Stitch": ("ST", "#ff75b5"),
    "OpenClaw": ("OC", "#6fbcff"),
}


def icon_markup(name: str, slug: str | None, x: int, y: int) -> str:
    if slug:
        path = ICON_DIR / f"{slug}.svg"
        if path.exists():
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            return f'<image href="data:image/svg+xml;base64,{encoded}" x="{x}" y="{y}" width="27" height="27" preserveAspectRatio="xMidYMid meet"/>'
    label, color = CUSTOM[name]
    return f'<text x="{x + 13}" y="{y + 21}" text-anchor="middle" class="custom" fill="{color}">{label}</text>'


svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 300" role="img" aria-labelledby="title desc">
<title id="title">Aayush Kumawat technology ecosystem</title>
<desc id="desc">Original technology logos presented as soft claymorphic interface tiles.</desc>
<defs>
  <linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#151d26"/><stop offset="1" stop-color="#0d131a"/></linearGradient>
  <filter id="clay" x="-30%" y="-30%" width="160%" height="170%">
    <feDropShadow dx="7" dy="8" stdDeviation="7" flood-color="#03060a" flood-opacity=".8"/>
    <feDropShadow dx="-3" dy="-3" stdDeviation="4" flood-color="#526273" flood-opacity=".16"/>
  </filter>
  <style>
    .mono{font-family:'Courier New',monospace;letter-spacing:1.5px}
    .name{font:11px Arial,sans-serif;fill:#dce5ec}
    .custom{font:700 10px 'Courier New',monospace}
    .tile{transition:transform .2s ease}
    @media(prefers-reduced-motion:reduce){.tile{transition:none}}
  </style>
</defs>
<rect width="980" height="300" rx="22" fill="url(#surface)"/>
<text x="28" y="32" class="mono" font-size="13" fill="#70e3ff">TECHNOLOGY ECOSYSTEM</text>
<text x="28" y="51" font-family="Arial,sans-serif" font-size="11" fill="#81909e">REAL LOGOS / SOFT CLAY SURFACES / COMPACT TOOLCHAIN</text>
"""

for index, (name, slug, url) in enumerate(TOOLS):
    column = index % 6
    row = index // 6
    x = 24 + column * 158
    y = 72 + row * 53
    href_open = f'<a href="{url}">' if url else ""
    href_close = "</a>" if url else ""
    svg += f'{href_open}<g class="tile" transform="translate({x} {y})" filter="url(#clay)"><title>{name}</title><rect width="140" height="40" rx="14" fill="#151e27"/><rect x="1" y="1" width="138" height="38" rx="13" fill="none" stroke="#526170" stroke-opacity=".12"/>{icon_markup(name, slug, 13, 7)}<text x="51" y="25" class="name">{name}</text></g>{href_close}'

svg += '<text x="28" y="286" class="mono" font-size="9" fill="#647482">HOVER A TILE FOR THE TOOL NAME · CLICK A LOGO TO OPEN ITS OFFICIAL SITE</text></svg>\n'
OUT.write_text(svg, encoding="utf-8")
