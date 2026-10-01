"""Generate lightweight SVG panels from public GitHub data."""

from __future__ import annotations

import base64
import html
import json
import os
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
ASSETS = ROOT / "assets"
GENERATED.mkdir(exist_ok=True)
USERNAME = "ANDY0802X"
API = "https://api.github.com"
GREEN = "#35cf7e"
CYAN = "#5edbff"
MUTED = "#81909e"
TEXT = "#e7edf2"
SURFACE = "#111820"
GRID = "#2a3945"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def api(path: str, accept: str = "application/vnd.github+json"):
    request = urllib.request.Request(
        API + path,
        headers={"Accept": accept, "User-Agent": "ANDY0802X-profile-dashboard"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


def graphql(query: str) -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return {}
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "ANDY0802X-profile-dashboard",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8")).get("data", {})
    except Exception:
        return {}


def svg_start(width: int, height: int, title: str, desc: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{esc(title)}</title><desc id="desc">{esc(desc)}</desc>
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#080d13"/><stop offset="1" stop-color="#0d171d"/></linearGradient>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{GRID}" stroke-opacity=".18"/></pattern>
<style>.ui{{font-family:Arial,sans-serif}}.mono{{font-family:'Courier New',monospace}}.h{{font-size:13px;fill:{CYAN}}}.body{{font-size:11px;fill:{MUTED}}}.label{{font-size:9px;fill:#65727f;letter-spacing:1.5px}}.value{{font-size:23px;font-weight:bold;fill:{TEXT}}}.line{{stroke:{GRID}}}.pulse{{animation:pulse 2.8s ease-in-out infinite}}.rise{{animation:rise .7s ease-out both}}@keyframes pulse{{50%{{opacity:.35}}}}@keyframes rise{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:translateY(0)}}}}@media(prefers-reduced-motion:reduce){{.pulse,.rise{{animation:none}}}}</style></defs>
<rect width="{width}" height="{height}" rx="16" fill="url(#bg)"/><rect width="{width}" height="{height}" rx="16" fill="url(#grid)"/>"""


def write(name: str, content: str):
    (GENERATED / name).write_text(content + "</svg>\n", encoding="utf-8")


profile = api(f"/users/{USERNAME}") or {}
repos = api(f"/users/{USERNAME}/repos?per_page=100&sort=updated") or []
events = api(f"/users/{USERNAME}/events/public?per_page=30") or []
repo_names = [repo.get("name", "") for repo in repos]
stars = sum(repo.get("stargazers_count", 0) or 0 for repo in repos)
issues = sum(repo.get("open_issues_count", 0) or 0 for repo in repos)
language_counts = Counter(repo.get("language") for repo in repos if repo.get("language"))
active_repos = sorted(repos, key=lambda repo: (repo.get("stargazers_count", 0), repo.get("updated_at", "")), reverse=True)

user_query = f"""query {{ user(login: "{USERNAME}") {{
  pullRequests {{ totalCount }}
  issues {{ totalCount }}
  contributionsCollection {{ totalCommitContributions totalPullRequestContributions totalIssueContributions
    contributionCalendar {{ totalContributions weeks {{ contributionDays {{ date contributionCount }} }} }}
  }}
}} }}"""
user_data = graphql(user_query).get("user", {})
calendar = user_data.get("contributionsCollection", {}).get("contributionCalendar", {})
days = [day for week in calendar.get("weeks", []) for day in week.get("contributionDays", [])]
contributions = calendar.get("totalContributions", 0)
pull_requests = user_data.get("pullRequests", {}).get("totalCount", 0)
issue_total = user_data.get("issues", {}).get("totalCount", issues)

# Stats panel
stats = svg_start(430, 360, "Live GitHub statistics", "Public GitHub profile metrics, refreshed from the API.")
stats += '<text x="24" y="30" class="mono h">GITHUB OVERVIEW</text><circle cx="390" cy="25" r="4" fill="#35cf7e" class="pulse"/>'
stats += '<text x="24" y="52" class="body">PUBLIC API / NO INVENTED NUMBERS</text>'
stat_items = [
    ("REPOSITORIES", profile.get("public_repos", len(repos))),
    ("PULL REQUESTS", pull_requests),
    ("ISSUES", issue_total),
    ("STARS", stars),
    ("FOLLOWERS", profile.get("followers", 0)),
    ("FOLLOWING", profile.get("following", 0)),
    ("CONTRIBUTIONS", contributions),
    ("OPEN ISSUES", issues),
]
for index, (label, value) in enumerate(stat_items):
    x = 24 + (index % 2) * 200
    y = 86 + (index // 2) * 64
    stats += f'<g class="rise" style="animation-delay:{index * 60}ms"><rect x="{x}" y="{y}" width="178" height="49" rx="12" fill="{SURFACE}"/><text x="{x+14}" y="{y+17}" class="mono label">{esc(label)}</text><text x="{x+14}" y="{y+40}" class="value">{esc(value)}</text></g>'
stats += '<text x="24" y="344" class="mono label">AAYUSH KUMAWAT / ANDY0802X / PROFILE NODE</text>'
write("stats.svg", stats)

# Contribution terrain
contrib = svg_start(560, 360, "Custom contribution terrain", "A generated contribution grid. Hover cells for date and contribution count.")
contrib += '<text x="24" y="30" class="mono h">CONTRIBUTION TERRAIN</text><text x="24" y="49" class="body">LAST 12 MONTHS / EACH CELL HAS A DATE TOOLTIP</text>'
if not days:
    days = [{"date": "", "contributionCount": 0} for _ in range(364)]
max_count = max((day.get("contributionCount", 0) for day in days), default=1) or 1
for index, day in enumerate(days[-364:]):
    col, row = index % 52, index // 52
    count = day.get("contributionCount", 0)
    ratio = count / max_count
    color = "#17212a" if count == 0 else "#214b43" if ratio < .25 else "#2d8460" if ratio < .55 else "#42c978" if ratio < .8 else "#a4e87a"
    title = f'{day.get("date", "unknown")} · {count} contributions'
    contrib += f'<rect class="rise" style="animation-delay:{(index % 30) * 8}ms" x="{24 + col * 9.7:.1f}" y="{70 + row * 15}" width="7" height="11" rx="2" fill="{color}"><title>{esc(title)}</title></rect>'
for month_index, label in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]):
    contrib += f'<text x="{24 + month_index * 44}" y="342" class="mono label">{label}</text>'
contrib += '<text x="24" y="324" class="mono label">LESS</text><text x="486" y="324" class="mono label">MORE</text>'
write("contribution.svg", contrib)

# Activity chart
hour_counts = Counter()
day_counts = Counter()
for event in events:
    timestamp = event.get("created_at")
    if timestamp:
        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            hour_counts[parsed.hour] += 1
            day_counts[parsed.strftime("%a")] += 1
        except ValueError:
            pass
activity = svg_start(430, 360, "Live activity graphs", "Recent public GitHub activity by hour and day.")
activity += '<text x="24" y="30" class="mono h">LIVE ACTIVITY</text><text x="24" y="49" class="body">PUBLIC EVENTS / RECENT SIGNAL</text>'
activity += '<text x="24" y="78" class="mono label">EVENTS BY HOUR</text><line x1="24" y1="174" x2="406" y2="174" class="line"/>'
for hour in range(24):
    count = hour_counts.get(hour, 0)
    height = min(85, count * 17)
    x = 28 + hour * 15.5
    activity += f'<rect class="rise" style="animation-delay:{hour*20}ms" x="{x:.1f}" y="{174-height}" width="8" height="{height}" rx="3" fill="{GREEN}"><title>{hour:02d}:00 · {count} events</title></rect>'
activity += '<text x="24" y="194" class="mono label">00</text><text x="200" y="194" class="mono label">12</text><text x="390" y="194" class="mono label">23</text>'
activity += '<text x="24" y="224" class="mono label">EVENTS BY DAY</text><line x1="24" y1="316" x2="406" y2="316" class="line"/>'
for index, day_name in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
    count = day_counts.get(day_name, 0)
    height = min(76, count * 15)
    x = 38 + index * 54
    activity += f'<rect class="rise" x="{x}" y="{316-height}" width="14" height="{height}" rx="4" fill="{CYAN}"><title>{day_name} · {count} events</title></rect><text x="{x-3}" y="337" class="mono label">{day_name[:2].upper()}</text>'
write("activity.svg", activity)

# Languages
languages = svg_start(760, 155, "Language distribution", "Repository language distribution from public repositories.")
languages += '<text x="24" y="30" class="mono h">LANGUAGE DISTRIBUTION</text><text x="24" y="49" class="body">BASED ON PUBLIC REPOSITORY METADATA</text>'
total_languages = sum(language_counts.values()) or 1
palette = ["#f1d34f", "#5edbff", "#c47cff", "#ef6d9c", "#63d297", "#ff9f68"]
cursor = 24
for index, (language, count) in enumerate(language_counts.most_common(8)):
    width = 690 * count / total_languages
    languages += f'<rect x="{cursor:.1f}" y="70" width="{max(width, 3):.1f}" height="12" fill="{palette[index % len(palette)]}"/><title>{esc(language)} · {count} repositories</title>'
    cursor += width
for index, (language, count) in enumerate(language_counts.most_common(8)):
    languages += f'<text x="{24 + (index % 4) * 175}" y="{113 + (index // 4) * 20}" class="mono label"><tspan fill="{palette[index % len(palette)]}">●</tspan> {esc(language)} {count}</text>'
write("languages.svg", languages)

# Repositories
repository_panel = svg_start(980, 310, "Automatically discovered repositories", "Compact repository cards sorted by stars and recent updates.")
repository_panel += '<text x="24" y="30" class="mono h">REPOSITORY RADAR</text><text x="24" y="49" class="body">SORTED BY STARS + RECENT ACTIVITY / LIVE API</text>'
for index, repo in enumerate(active_repos[:6]):
    x = 24 + (index % 3) * 318
    y = 70 + (index // 3) * 108
    name = repo.get("name", "untitled")
    description = (repo.get("description") or "No public description available.").replace("\n", " ")
    description = description if len(description) < 50 else description[:47] + "..."
    updated = (repo.get("updated_at") or "")[:10] or "unknown"
    repository_panel += f'<a href="{esc(repo.get("html_url", "#"))}"><g class="rise"><rect x="{x}" y="{y}" width="294" height="88" rx="13" fill="{SURFACE}"/><text x="{x+14}" y="{y+22}" class="mono h">{esc(name[:25])}</text><text x="{x+14}" y="{y+43}" class="body">{esc(description)}</text><text x="{x+14}" y="{y+66}" class="mono label">◈ {esc(repo.get("language") or "MULTI")}   ★ {repo.get("stargazers_count", 0)}   ⑂ {repo.get("forks_count", 0)}</text><text x="{x+205}" y="{y+66}" class="mono label">{esc(updated)}</text></g></a>'
write("repositories.svg", repository_panel)

# Spotify fallback panel; the workflow replaces the JSON when configured.
spotify_data = {}
spotify_path = GENERATED / "spotify.json"
if spotify_path.exists():
    try:
        spotify_data = json.loads(spotify_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        pass
track = spotify_data.get("track", "Lofi mode")
artist = spotify_data.get("artist", "Instrumental coding focus")
spotify = svg_start(760, 110, "Recently played music", "Spotify recently played track or graceful local fallback.")
spotify += f'<text x="24" y="30" class="mono h">RECENTLY PLAYED</text><text x="24" y="57" class="ui" font-size="16" fill="{TEXT}">♫ {esc(track)}</text><text x="24" y="79" class="body">{esc(artist)} · instrumental / lo-fi coding mode</text><text x="610" y="57" class="mono label">SPOTIFY OPTIONAL</text>'
write("spotify.svg", spotify)

(GENERATED / "data.json").write_text(json.dumps({
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "profile": profile,
    "repositories": repos,
    "events": events,
    "stats": {"contributions": contributions, "pull_requests": pull_requests, "issues": issue_total, "stars": stars},
}, indent=2), encoding="utf-8")
