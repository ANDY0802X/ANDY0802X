"""Refresh the lightweight activity panel with public GitHub API data."""

from pathlib import Path
import json
import urllib.request

root = Path(__file__).resolve().parents[1]
user = "ANDY0802X"
request = urllib.request.Request(
    f"https://api.github.com/users/{user}/events/public?per_page=6",
    headers={"User-Agent": "ANDY0802X-profile-dashboard"},
)
try:
    with urllib.request.urlopen(request, timeout=15) as response:
        events = json.loads(response.read().decode("utf-8"))
    names = [event.get("repo", {}).get("name", "").split("/", 1)[-1] for event in events]
    names = [name for name in names if name]
    text = " · ".join(names[:3]) or "WAITING FOR NEXT BUILD SIGNAL"
except Exception:
    text = "LOCAL FALLBACK // API SIGNAL TEMPORARILY QUIET"

svg = (root / "assets" / "activity-panel.svg").read_text(encoding="utf-8")
start = '<text x="30" y="103" class="m" font-size="11" fill="#9cecff">'
end = "</text>"
left = svg.index(start) + len(start)
right = svg.index(end, left)
svg = svg[:left] + text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + svg[right:]
(root / "assets" / "activity-panel.svg").write_text(svg, encoding="utf-8")
