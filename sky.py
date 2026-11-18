"""usage: python sky.py <username> <out.svg>   (or --demo <out.svg>)"""
import json
import os
import random
import sys
import urllib.request

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { weekday contributionLevel } }
      }
    }
  }
}"""

# github only gives quartile buckets per day, not raw counts, which is fine for brightness
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
          "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def fetch(login):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}",
                 "Content-Type": "application/json"},
    )
    cal = json.load(urllib.request.urlopen(req))["data"]["user"][
        "contributionsCollection"]["contributionCalendar"]
    weeks = [[(d["weekday"], LEVELS[d["contributionLevel"]]) for d in w["contributionDays"]]
             for w in cal["weeks"]]
    return weeks, cal["totalContributions"]


def demo():
    rnd = random.Random(4)
    weeks = [[(d, rnd.choice([0] * 9 + [1, 1, 2, 3, 4])) for d in range(7)] for _ in range(53)]
    return weeks, sum(l * 2 for w in weeks for _, l in w)


def draw(weeks, total):
    cell, left, top = 14, 16, 44
    w = left * 2 + len(weeks) * cell
    h = top + 7 * cell + 40
    cycle, sweep = 11.0, 9.0  # seconds per loop / seconds to cross
    x0, x1 = left - 30, w - left + 30

    def arrival(x):
        return (x - x0) / (x1 - x0) * sweep

    radius = {1: 1.3, 2: 1.8, 3: 2.3, 4: 2.9}
    parts, tracked = [], 0
    rnd = random.Random(11)
    for _ in range(60):
        parts.append(f'<circle cx="{rnd.uniform(0, w):.1f}" cy="{rnd.uniform(4, h - 20):.1f}" r="{rnd.choice([.35, .5, .6])}" fill="#e8e4dc" opacity="{rnd.uniform(.12, .35):.2f}"/>')
    for i, week in enumerate(weeks):
        cx = left + i * cell + cell / 2
        delay = f"animation-delay:{arrival(cx):.2f}s"
        for day, level in week:
            cy = top + day * cell + cell / 2
            if level == 0:
                parts.append(f'<circle cx="{cx}" cy="{cy}" r=".6" fill="#3a3c44"/>')
                continue
            tracked += 1
            r = radius[level]
            b = r + 4
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 2.6:.1f}" fill="url(#halo)" class="halo" style="{delay}"/>')
            tw = f"animation-duration:{rnd.uniform(2.2, 5):.1f}s;animation-delay:{rnd.uniform(0, 4):.1f}s"
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#f4f1ea" opacity="{.45 + level * .13:.2f}" class="tw" style="{tw}"/>')
            parts.append(
                f'<path class="lock" style="{delay}" transform="translate({cx} {cy})" '
                f'd="M{-b} {-b + 3}V{-b}H{-b + 3}M{b - 3} {-b}H{b}V{-b + 3}'
                f'M{b} {b - 3}V{b}H{b - 3}M{-b + 3} {b}H{-b}V{b - 3}"/>')

    bottom = top + 7 * cell
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
<defs>
<radialGradient id="halo"><stop offset="0" stop-color="#f4f1ea" stop-opacity=".9"/><stop offset="1" stop-color="#f4f1ea" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2"/></filter>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c9f26b" stop-opacity=".14"/><stop offset="1" stop-color="#c9f26b" stop-opacity="0"/></linearGradient>
<linearGradient id="trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e8e4dc" stop-opacity="0"/><stop offset="1" stop-color="#e8e4dc" stop-opacity=".6"/></linearGradient>
</defs>
<style>
.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;letter-spacing:2px;fill:#8d8a84}}
.halo{{opacity:0;animation:halo {cycle}s linear infinite}}
.lock{{fill:none;stroke:#c9f26b;stroke-width:1.1;opacity:0;animation:lock {cycle}s linear infinite}}
.sat{{animation:sweep {cycle}s linear infinite}}
.tw{{animation-name:tw;animation-iteration-count:infinite;animation-direction:alternate;animation-timing-function:ease-in-out}}
@keyframes tw{{from{{opacity:1}}to{{opacity:.35}}}}
.shoot{{opacity:0;animation:shoot 7s ease-out infinite;animation-delay:3.5s}}
@keyframes shoot{{0%{{opacity:0;transform:translate({w * .62:.0f}px,4px)}}2%{{opacity:1}}9%{{opacity:0;transform:translate({w * .62 - 150:.0f}px,{h * .55:.0f}px)}}100%{{opacity:0;transform:translate({w * .62 - 150:.0f}px,{h * .55:.0f}px)}}}}
@keyframes halo{{0%{{opacity:.75}}8%{{opacity:.15}}100%{{opacity:0}}}}
@keyframes lock{{0%{{opacity:1}}9%{{opacity:1}}17%{{opacity:0}}100%{{opacity:0}}}}
@keyframes sweep{{0%{{transform:translateX({x0}px)}}{sweep / cycle * 100:.1f}%{{transform:translateX({x1}px)}}100%{{transform:translateX({x1}px)}}}}
</style>
<rect width="{w}" height="{h}" rx="8" fill="#0d1117"/>
{"".join(parts)}
<g class="shoot"><g transform="rotate(-121)"><rect x="0" y="-.6" width="70" height="1.2" fill="url(#trail)" transform="scale(-1 1)"/></g><circle r="1.6" fill="#fff"/></g>
<g class="sat">
<rect x="-1.5" y="{top - 6}" width="3" height="{bottom - top + 12}" fill="url(#beam)"/>
<rect x="-46" y="{top - 22.5}" width="46" height="1" fill="url(#trail)"/>
<circle cy="{top - 22}" r="3" fill="#fff" filter="url(#glow)"/>
<circle cy="{top - 22}" r="1.5" fill="#fff"/>
</g>
<text x="{w - left}" y="{h - 12}" class="mono" text-anchor="end"><tspan fill="#c9f26b">{tracked}</tspan> DAYS TRACKED · {total} CONTRIBUTIONS</text>
</svg>'''


if __name__ == "__main__":
    weeks, total = demo() if sys.argv[1] == "--demo" else fetch(sys.argv[1])
    open(sys.argv[2], "w").write(draw(weeks, total))
