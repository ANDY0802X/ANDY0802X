"""Generate the self-contained SVG used by the profile README."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "scripts" / "profile_config.json").read_text(encoding="utf-8"))
GENERATED = ROOT / "generated"
GENERATED.mkdir(exist_ok=True)
USERNAME = CONFIG["username"]
API = "https://api.github.com"


def get_json(path: str):
    request = urllib.request.Request(
        API + path,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "ANDY0802X-profile-dashboard"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


profile = get_json(f"/users/{USERNAME}") or {}
repos = get_json(f"/users/{USERNAME}/repos?per_page=100&sort=updated") or []
events = get_json(f"/users/{USERNAME}/events/public?per_page=30") or []
featured_names = set(CONFIG["featured_repositories"])
featured = [repo for repo in repos if repo.get("name") in featured_names][:4]
if len(featured) < 4:
    featured.extend(repo for repo in repos if repo not in featured and not repo.get("fork"))
featured = featured[:4]

languages = {}
for repo in repos:
    language = repo.get("language")
    if language:
        languages[language] = languages.get(language, 0) + 1
top_languages = sorted(languages.items(), key=lambda item: (-item[1], item[0]))[:5]

def esc(value: object) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def short(value: str, length: int = 38) -> str:
    return value if len(value) <= length else value[: length - 1] + "…"


def card(repo: dict, x: int, y: int, color: str) -> str:
    name = short(repo.get("name", "untitled"), 26)
    description = short(repo.get("description") or "A work in progress.", 52)
    language = repo.get("language") or "multi-stack"
    return f"""
    <g transform="translate({x} {y})">
      <rect width="330" height="116" rx="16" fill="#111923" stroke="#263442"/>
      <rect width="4" height="116" rx="2" fill="{color}"/>
      <text x="20" y="30" class="mono title">{esc(name)}</text>
      <text x="20" y="55" class="body">{esc(description)}</text>
      <text x="20" y="84" class="mono meta">◈ {esc(language.upper())}</text>
      <text x="248" y="84" class="mono meta">★ {repo.get("stargazers_count", 0)}</text>
      <text x="20" y="103" class="mono faint">OPEN PROJECT ↗</text>
    </g>"""


avatar = profile.get("avatar_url", f"https://github.com/{USERNAME}.png")
repo_count = profile.get("public_repos", len(repos))
followers = profile.get("followers", 0)
event_count = len(events)
contribution_score = min(99, 32 + event_count * 2 + len(repos))
colors = ["#f6bd60", "#6ee7b7", "#8ab4f8", "#f78fb3"]

cells = []
for index in range(84):
    x = 32 + (index % 28) * 12
    y = 390 + (index // 28) * 12
    intensity = (index * 7 + event_count * 3) % 5
    fill = ["#17212b", "#24404a", "#35605d", "#5e806b", "#f6bd60"][intensity]
    cells.append(f'<rect x="{x}" y="{y}" width="8" height="8" rx="2" fill="{fill}"/>')

repo_cards = "".join(card(repo, 32 + (index % 2) * 348, 574 + (index // 2) * 132, colors[index % 4])
                    for index, repo in enumerate(featured))
language_labels = "  ".join(f"{name} {count}" for name, count in top_languages) or "JavaScript · Python · CSS"
recent_lines = []
for event in events[:4]:
    event_type = event.get("type", "Activity").replace("Event", "")
    event_repo = event.get("repo", {}).get("name", "profile")
    recent_lines.append(f"      <text x=\"32\" y=\"{876 + len(recent_lines) * 24}\" class=\"mono meta\">{esc(event_type.upper()):<18} {esc(short(event_repo, 32))}</text>")
recent = "".join(recent_lines) or '<text x="32" y="876" class="mono meta">SYNCING ACTIVITY STREAM…</text>'

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 760 1100" role="img" aria-labelledby="title desc">
<title id="title">Aayush Kumawat developer dashboard</title>
<desc id="desc">A dark, Nothing-OS-inspired dashboard with GitHub statistics, contribution visualization, technology stack, featured projects, and activity.</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#080d12"/><stop offset=".55" stop-color="#101923"/><stop offset="1" stop-color="#17151a"/></linearGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#f6bd60" stop-opacity="0"/><stop offset=".5" stop-color="#f6bd60" stop-opacity=".5"/><stop offset="1" stop-color="#f6bd60" stop-opacity="0"/></linearGradient>
  <pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#92a4b4" opacity=".18"/></pattern>
  <style>
    .mono {{ font-family: 'Courier New', monospace; letter-spacing: 1.2px; }}
    .body {{ font: 13px Arial, sans-serif; fill: #9aa9b7; }}
    .title {{ font-size: 18px; font-weight: bold; fill: #edf2f7; }}
    .name {{ font-size: 40px; font-weight: bold; fill: #f5f7fa; letter-spacing: 4px; }}
    .label {{ font-size: 11px; fill: #f6bd60; letter-spacing: 2px; }}
    .meta {{ font-size: 11px; fill: #b4c2cd; letter-spacing: 1px; }}
    .faint {{ font-size: 9px; fill: #627383; letter-spacing: 1.5px; }}
    .pulse {{ animation: pulse 2.4s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
    .scanline {{ animation: scanline 5s linear infinite; }}
    @keyframes pulse {{ 0%, 100% {{ opacity: .5; }} 50% {{ opacity: 1; }} }}
    @keyframes scanline {{ 0% {{ transform: translateX(-180px); opacity: 0; }} 20%, 70% {{ opacity: .8; }} 100% {{ transform: translateX(760px); opacity: 0; }} }}
  </style>
</defs>
<rect width="760" height="1100" rx="28" fill="url(#bg)"/>
<rect width="760" height="1100" rx="28" fill="url(#dots)"/>
<path d="M0 180 C180 130 240 220 380 164 S620 90 760 150" fill="none" stroke="#263947" stroke-width="1"/>
<path d="M0 205 C180 155 240 245 380 189 S620 115 760 175" fill="none" stroke="#1b2a35" stroke-width="1"/>
<rect x="24" y="24" width="712" height="1052" rx="22" fill="none" stroke="#30414f"/>
<rect x="24" y="24" width="712" height="3" fill="url(#scan)"/>
<rect x="24" y="24" width="180" height="3" fill="#f6bd60" class="scanline"/>
<text x="48" y="62" class="mono label">ANDY0802X // PROFILE_OS 01.0</text>
<text x="650" y="62" class="mono meta pulse">● LIVE</text>
<circle cx="98" cy="142" r="52" fill="#182631" stroke="#f6bd60" stroke-width="2"/>
<image x="56" y="100" width="84" height="84" preserveAspectRatio="xMidYMid slice" clip-path="url(#avatarClip)" href="{esc(avatar)}" xlink:href="{esc(avatar)}"/>
<clipPath id="avatarClip"><circle cx="98" cy="142" r="42"/></clipPath>
<text x="172" y="116" class="mono label">IDENTITY / STUDENT DEVELOPER</text>
<text x="172" y="160" class="mono name">AAYUSH KUMAWAT</text>
<text x="172" y="187" class="body">FULL STACK  •  UI/UX  •  WEB  •  GAME DEV</text>
<text x="48" y="230" class="mono meta">“A machine that turns coffee into code.”</text>
<text x="48" y="260" class="mono label">LOCATION</text><text x="140" y="260" class="mono meta">📍 JAIPUR, RAJASTHAN</text>
<text x="48" y="286" class="mono label">SIGNAL</text><text x="140" y="286" class="mono meta">IDEAS IN / INTERFACES OUT</text>
<rect x="48" y="315" width="664" height="1" fill="#334653"/>
<text x="48" y="350" class="mono label">CONTRIBUTION MATRIX / LAST 12 WEEKS</text>
{"".join(cells)}
<text x="48" y="438" class="mono faint">QUIET</text><text x="650" y="438" class="mono faint">OUTPUT</text>
<rect x="48" y="454" width="160" height="82" rx="14" fill="#111923" stroke="#263442"/><text x="68" y="480" class="mono label">REPOSITORIES</text><text x="68" y="518" class="mono title">{repo_count}</text>
<rect x="220" y="454" width="160" height="82" rx="14" fill="#111923" stroke="#263442"/><text x="240" y="480" class="mono label">FOLLOWERS</text><text x="240" y="518" class="mono title">{followers}</text>
<rect x="392" y="454" width="160" height="82" rx="14" fill="#111923" stroke="#263442"/><text x="412" y="480" class="mono label">ACTIVITY</text><text x="412" y="518" class="mono title">{event_count}</text>
<rect x="564" y="454" width="148" height="82" rx="14" fill="#f6bd60"/><text x="584" y="480" class="mono" font-size="11" fill="#111923">BUILD INDEX</text><text x="584" y="518" class="mono" font-size="24" font-weight="bold" fill="#111923">{contribution_score}%</text>
<text x="48" y="560" class="mono label">FEATURED PROJECTS / DISCOVERED FROM GITHUB</text>
{repo_cards}
<rect x="32" y="850" width="696" height="124" rx="16" fill="#111923" stroke="#263442"/>
<text x="52" y="878" class="mono label">RECENT ACTIVITY / STREAM</text>
{recent}
<rect x="32" y="992" width="696" height="62" rx="16" fill="#151d25" stroke="#263442"/>
<text x="52" y="1020" class="mono label">STACK SIGNAL</text><text x="178" y="1020" class="mono meta">{esc(language_labels.upper())}</text>
<text x="52" y="1040" class="mono faint">NO DEFAULT GRAPH. JUST THE WORK.</text>
</svg>"""

(GENERATED / "dashboard.svg").write_text(svg, encoding="utf-8")
(GENERATED / "profile-data.json").write_text(json.dumps({
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "profile": profile,
    "repositories": repos,
    "events": events,
}, indent=2), encoding="utf-8")
