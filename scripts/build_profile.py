#!/usr/bin/env python3
"""Build the custom SVG artwork and the live sections of the profile README.

Runs daily in GitHub Actions (see .github/workflows/build-profile.yml).
Only the standard library is used. Needs GITHUB_TOKEN in the environment.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import urllib.request
from html import escape
from pathlib import Path

USER = "kdy74"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "generated"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

# ── palette ────────────────────────────────────────────────────────────────
BG = "#0B1020"
PANEL = "#111833"
BORDER = "#22305A"
TEXT = "#E6EDF3"
MUTED = "#8B98B8"
ORANGE = "#22C55E"  # primary accent (green)
RED = "#A3E635"  # lime
CYAN = "#22D3EE"
VIOLET = "#2DD4BF"  # teal
GREEN = "#34D399"
SANS = "'Segoe UI', Ubuntu, -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"

LANG_COLORS = {
    "TypeScript": "#3178C6", "JavaScript": "#F1E05A", "Rust": "#DEA584",
    "Python": "#3572A5", "Dart": "#00B4AB", "Java": "#B07219", "CSS": "#663399",
    "HTML": "#E34C26", "SCSS": "#C6538C", "Less": "#4F7CC4", "Shell": "#89E051",
    "Dockerfile": "#5B8BA0", "PowerShell": "#2E6DB4", "TSQL": "#E38C00",
}

# Curated copy for the featured cards; numbers are always fetched live.
FEATURED = [
    ("Otter", "🦦", ORANGE, "Rust · Tauri · Windows",
     "A local-first workspace time machine. Saves apps, tabs, terminals, Docker and files as a context, then restores them with verified results."),
    ("nest_codebase", "🧱", RED, "NestJS 11 · Fastify · Prisma",
     "Enterprise NestJS boilerplate: Prisma & TypeORM repositories, Redis + BullMQ jobs, JWT auth, Prometheus metrics and health checks."),
    ("Vinsaky", "🛒", CYAN, "NestJS · MongoDB · React",
     "Full-stack commerce platform with queue workers, SePay payments, live chat, dashboards and interactive maps."),
    ("Pettopia", "🐾", GREEN, "Next.js · Tailwind · Docker",
     "Pet-care platform: TypeScript backend, a customer app with QR scanning and a clinic portal with analytics."),
    ("Vietnamosaic", "🇻🇳", VIOLET, "Product spec · 12 screens",
     "A social network for discovering Việt Nam through everyday stories, experience mosaic pieces and mini postage stamps."),
    ("EXE", "🧩", "#5EEAD4", "Express · MongoDB · JWT",
     "Express MVC API with routers, controllers, Joi validators and middleware, JWT auth and Cloudinary uploads."),
]


# ── GitHub API ─────────────────────────────────────────────────────────────
def _request(url: str, body: dict | None = None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", f"{USER}-profile-builder")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def rest(path: str):
    return _request(f"https://api.github.com/{path}")


def graphql(query: str, variables: dict):
    data = _request("https://api.github.com/graphql", {"query": query, "variables": variables})
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


# ── helpers ────────────────────────────────────────────────────────────────
def t(s) -> str:
    return escape(str(s), quote=True)


def wrap(text: str, width: int, max_lines: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,") + "…"
    return lines


def fmt_num(n: int) -> str:
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)


def svg(w: int, h: int, body: str, style: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img">\n<style>text{{font-family:{SANS}}} .mono{{font-family:{MONO}}}{style}</style>\n{body}\n</svg>\n'
    )


def write(name: str, content: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")


# ── static artwork ─────────────────────────────────────────────────────────
def hero() -> str:
    lines = [
        ("$", "whoami", TEXT),
        ("›", "mundo · full-stack engineer · Hà Nội", GREEN),
        ("$", "cat focus.txt", TEXT),
        ("›", "AI-native workspaces", CYAN),
        ("›", "secure backend platforms", CYAN),
        ("›", "local-first desktop tools", CYAN),
        ("$", "otter restore --verify", TEXT),
        ("✓", "context restored · all checks green", GREEN),
    ]
    term = []
    for i, (p, s, color) in enumerate(lines):
        y = 110 + i * 20
        pc = RED if p == "$" else color
        term.append(
            "<g>"
            f'<text x="502" y="{y}" class="mono" font-size="12.5" fill="{pc}">{t(p)}</text>'
            f'<text x="520" y="{y}" class="mono" font-size="12.5" fill="{color}">{t(s)}</text></g>'
        )
    cursor_y = 110 + len(lines) * 20
    chips = [("AI-native workspace", ORANGE), ("Local-first tools", CYAN), ("Hà Nội", RED)]
    chip_svg, x = [], 40
    for label, color in chips:
        w = len(label) * 6.5 + 28
        chip_svg.append(
            f'<rect x="{x}" y="218" width="{w:.0f}" height="28" rx="14" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-opacity="0.55"/>'
            f'<circle cx="{x + 13}" cy="232" r="3.5" fill="{color}"/>'
            f'<text x="{x + 22}" y="236.5" font-size="12.5" fill="{TEXT}">{t(label)}</text>'
        )
        x += w + 10
    style = (
        ""
        ".cur{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
        ".orb{animation:pulse 6s ease-in-out infinite}@keyframes pulse{50%{opacity:.55}}"
    )
    body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0B1020"/><stop offset="1" stop-color="#131B3A"/></linearGradient>
  <radialGradient id="orb" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{ORANGE}" stop-opacity="0.45"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>
  <radialGradient id="orb2" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0.30"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
  <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="#1B2547" stroke-width="1"/></pattern>
  <linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#86EFAC"/></linearGradient>
  <clipPath id="clip"><rect width="840" height="300" rx="18"/></clipPath>
</defs>
<g clip-path="url(#clip)">
  <rect width="840" height="300" fill="url(#bg)"/>
  <rect width="840" height="300" fill="url(#grid)" opacity="0.55"/>
  <circle class="orb" cx="760" cy="40" r="190" fill="url(#orb)"/>
  <circle class="orb" cx="80" cy="300" r="170" fill="url(#orb2)" style="animation-delay:3s"/>
</g>
<rect x="0.5" y="0.5" width="839" height="299" rx="18" fill="none" stroke="{BORDER}"/>
<g>
  <text x="40" y="70" class="mono" font-size="13" fill="{ORANGE}" letter-spacing="3">XIN CHÀO · HELLO</text>
  <text x="40" y="122" font-size="44" font-weight="800" fill="url(#name)">Mundo</text>
  <text x="40" y="158" font-size="19" font-weight="600" fill="{TEXT}">Full-stack Software Engineer</text>
  <text x="40" y="186" font-size="14" fill="{MUTED}">Turning messy workflows into calm, reliable software.</text>
</g>
{''.join(chip_svg)}
<!-- terminal -->
<rect x="482" y="62" width="326" height="222" rx="12" fill="#0A0F1E" fill-opacity="0.92" stroke="{BORDER}"/>
<rect x="482" y="62" width="326" height="28" rx="12" fill="#151E3F"/><rect x="482" y="80" width="326" height="10" fill="#151E3F"/>
<circle cx="500" cy="76" r="5" fill="#FF5F57"/><circle cx="516" cy="76" r="5" fill="#FEBC2E"/><circle cx="532" cy="76" r="5" fill="#28C840"/>
<text x="645" y="80" class="mono" font-size="11" fill="{MUTED}" text-anchor="middle">mundo@hanoi: ~</text>
{''.join(term)}
<rect class="cur" x="502" y="{cursor_y - 11}" width="8" height="14" fill="{ORANGE}"/>
"""
    return svg(840, 300, body, style)


def section(num: str, title: str, sub: str, color: str = ORANGE) -> str:
    body = f"""
<defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{color}"/><stop offset="0.45" stop-color="{color}" stop-opacity="0.25"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>
<text x="2" y="40" class="mono" font-size="30" font-weight="700" fill="{color}">{num}</text>
<text x="58" y="30" font-size="21" font-weight="700" fill="{TEXT}" stroke="#0B1020" stroke-width="0.4" paint-order="stroke">{t(title)}</text>
<text x="58" y="50" font-size="12.5" fill="{MUTED}">{t(sub)}</text>
<rect x="2" y="62" width="836" height="2" rx="1" fill="url(#l)"/>
"""
    return svg(840, 68, body)


def journey() -> str:
    steps = [
        ("2024", "Hello, GitHub", ["Java web shop", "React + Vite basics"], CYAN),
        ("2025", "Shipping full-stack", ["Express MVC APIs", "Pettopia: Next.js apps"], GREEN),
        ("2026 · H1", "Going deeper", ["nest_codebase ⭐", "Vinsaky commerce"], VIOLET),
        ("2026 · now", "Building tools", ["Otter (Rust/Tauri)", "AI-native workspace"], ORANGE),
    ]
    parts = [
        f'<defs><linearGradient id="tl" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="0.35" stop-color="{GREEN}"/>'
        f'<stop offset="0.68" stop-color="{VIOLET}"/><stop offset="1" stop-color="{ORANGE}"/></linearGradient></defs>',
        f'<rect x="0.5" y="0.5" width="839" height="179" rx="16" fill="{PANEL}" stroke="{BORDER}"/>',
        f'<rect x="100" y="62" width="639" height="3" rx="1.5" fill="{BORDER}"/>',
        f'<rect x="100" y="62" width="639" height="3" rx="1.5" fill="url(#tl)"/>',
    ]
    for i, (year, head, items, color) in enumerate(steps):
        cx = 100 + i * 213
        parts.append(
            "<g>"
            + (f'<circle class="glow" cx="{cx}" cy="63.5" r="18" fill="{color}" fill-opacity="0.25"/>' if i == len(steps) - 1 else "")
            + f'<circle cx="{cx}" cy="63.5" r="11" fill="{BG}" stroke="{color}" stroke-width="3"/>'
            f'<circle cx="{cx}" cy="63.5" r="4" fill="{color}"/>'
            f'<text x="{cx}" y="36" class="mono" font-size="13" font-weight="700" fill="{color}" text-anchor="middle">{t(year)}</text>'
            f'<text x="{cx}" y="100" font-size="14.5" font-weight="700" fill="{TEXT}" text-anchor="middle">{t(head)}</text>'
            + "".join(
                f'<text x="{cx}" y="{124 + j * 19}" font-size="12.5" fill="{MUTED}" text-anchor="middle">{t(it)}</text>'
                for j, it in enumerate(items)
            )
            + "</g>"
        )
    style = (
        ".glow{animation:pulse 3s ease-in-out infinite}@keyframes pulse{50%{opacity:.35}}"
    )
    return svg(840, 180, "\n".join(parts), style)


def footer() -> str:
    body = f"""
<defs><linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}" stop-opacity="0"/><stop offset="0.5" stop-color="{ORANGE}"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></linearGradient></defs>
<rect x="120" y="10" width="600" height="2" fill="url(#f)"/>
<text x="420" y="44" font-size="15" fill="{TEXT}" text-anchor="middle" font-weight="600">Cảm ơn bạn đã ghé thăm · Thanks for stopping by</text>
<text x="420" y="68" class="mono" font-size="11.5" fill="{MUTED}" text-anchor="middle">made with care in Hà Nội · artwork generated by scripts/build_profile.py</text>
"""
    return svg(840, 84, body)


# ── live artwork ───────────────────────────────────────────────────────────
def lang_bar(langs: dict[str, int], x: float, y: float, w: float, h: float, rid: str) -> str:
    total = sum(langs.values()) or 1
    out, cx = [f'<clipPath id="{rid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}"/></clipPath><g clip-path="url(#{rid})">'], x
    for name, size in langs.items():
        seg = w * size / total
        out.append(f'<rect x="{cx:.2f}" y="{y}" width="{seg + 0.5:.2f}" height="{h}" fill="{LANG_COLORS.get(name, MUTED)}"/>')
        cx += seg
    out.append("</g>")
    return "".join(out)


def repo_card(repo: dict, langs: dict[str, int], emoji: str, accent: str, tagline: str, desc: str) -> str:
    top = dict(sorted(langs.items(), key=lambda kv: -kv[1])[:4])
    total = sum(langs.values()) or 1
    pushed = dt.datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00")).strftime("%b %Y")
    desc_lines = wrap(desc, 52, 3)
    legend, lx = [], 24
    for name, size in list(top.items())[:3]:
        label = f"{name} {size * 100 / total:.0f}%"
        legend.append(
            f'<circle cx="{lx + 4}" cy="168" r="4" fill="{LANG_COLORS.get(name, MUTED)}"/>'
            f'<text x="{lx + 13}" y="172" font-size="11.5" fill="{MUTED}">{t(label)}</text>'
        )
        lx += len(label) * 6.4 + 26
    no_code = not langs
    body = f"""
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{accent}" stop-opacity="0.16"/><stop offset="0.55" stop-color="{PANEL}" stop-opacity="0"/></linearGradient></defs>
<rect x="0.5" y="0.5" width="409" height="219" rx="14" fill="{PANEL}" stroke="{BORDER}"/>
<rect x="0.5" y="0.5" width="409" height="219" rx="14" fill="url(#g)"/>
<rect x="24" y="0.5" width="64" height="3" rx="1.5" fill="{accent}"/>
<text x="24" y="44" font-size="22">{emoji}</text>
<text x="58" y="43" font-size="19" font-weight="700" fill="{TEXT}">{t(repo["name"])}</text>
<text x="386" y="42" font-size="12" fill="{MUTED}" text-anchor="end" class="mono">★ {fmt_num(repo["stargazers_count"])}  ⑂ {fmt_num(repo["forks_count"])}</text>
<text x="24" y="66" class="mono" font-size="11.5" fill="{accent}">{t(tagline)}</text>
{''.join(f'<text x="24" y="{94 + i * 19}" font-size="13" fill="{TEXT}" fill-opacity="0.86">{t(line)}</text>' for i, line in enumerate(desc_lines))}
{'<rect x="24" y="148" width="362" height="6" rx="3" fill="' + BORDER + '"/>' if no_code else lang_bar(top, 24, 148, 362, 6, "c")}
{''.join(legend) if legend else f'<text x="24" y="172" font-size="11.5" fill="{MUTED}">Spec &amp; design documents</text>'}
<text x="24" y="202" class="mono" font-size="11" fill="{MUTED}">updated {pushed}</text>
<text x="386" y="202" class="mono" font-size="11" fill="{accent}" text-anchor="end">view repo →</text>
"""
    return svg(410, 220, body)


def contributions() -> dict:
    q = """query($login:String!){user(login:$login){followers{totalCount}
      contributionsCollection{contributionCalendar{totalContributions
        weeks{contributionDays{date contributionCount}}}}}}"""
    return graphql(q, {"login": USER})["user"]


def streaks(days: list[tuple[str, int]]) -> tuple[int, int]:
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current, seq = 0, list(days)
    if seq and seq[-1][1] == 0:
        seq = seq[:-1]  # today may not have contributions yet
    for _, c in reversed(seq):
        if not c:
            break
        current += 1
    return current, longest


def dashboard(user: dict, repos: list[dict], lang_totals: dict[str, int]) -> str:
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]
    current, longest = streaks(days)
    stars = sum(r["stargazers_count"] for r in repos)
    kpis = [
        (fmt_num(cal["totalContributions"]), "contributions · last year", ORANGE),
        (f"{current}d", "current streak", RED),
        (f"{longest}d", "longest streak", VIOLET),
        (fmt_num(stars), "stars earned", "#FBBF24"),
        (str(len(repos)), "public repositories", CYAN),
    ]
    parts = [f'<rect x="0.5" y="0.5" width="839" height="411" rx="16" fill="{PANEL}" stroke="{BORDER}"/>']
    for i, (val, label, color) in enumerate(kpis):
        x = 20 + i * 162
        parts.append(
            f'<rect x="{x}" y="20" width="150" height="74" rx="10" fill="{BG}" stroke="{BORDER}"/>'
            f'<rect x="{x}" y="20" width="3" height="74" rx="1.5" fill="{color}"/>'
            f'<text x="{x + 18}" y="58" font-size="27" font-weight="800" fill="{color}">{t(val)}</text>'
            f'<text x="{x + 18}" y="80" font-size="11.5" fill="{MUTED}">{t(label)}</text>'
        )
    # heatmap
    peak = max((c for _, c in days), default=0) or 1
    scale = ["#1A2342", "#14532D", "#15803D", "#22C55E", "#86EFAC"]
    cell, gap, hx, hy = 11, 3, 52, 152
    parts.append(f'<text x="20" y="124" font-size="13" font-weight="700" fill="{TEXT}">Contribution heatmap</text>')
    parts.append(f'<text x="820" y="124" font-size="11.5" fill="{MUTED}" text-anchor="end">{t(cal["totalContributions"])} contributions in the last year</text>')
    last_month = None
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            date = dt.date.fromisoformat(d["date"])
            wd = (date.weekday() + 1) % 7  # Sunday first
            c = d["contributionCount"]
            lvl = 0 if c == 0 else min(4, 1 + int(3 * c / peak))
            parts.append(
                f'<rect x="{hx + wi * (cell + gap)}" y="{hy + wd * (cell + gap)}" width="{cell}" height="{cell}" rx="2.5" fill="{scale[lvl]}"><title>{d["date"]}: {c}</title></rect>'
            )
            if date.day <= 7 and wd == 0 and date.month != last_month:
                last_month = date.month
                parts.append(f'<text x="{hx + wi * (cell + gap)}" y="{hy - 6}" font-size="10" fill="{MUTED}">{date.strftime("%b")}</text>')
    for wd, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="20" y="{hy + wd * (cell + gap) + 9}" font-size="10" fill="{MUTED}">{name}</text>')
    lx = 820 - 5 * 14 - 30
    parts.append(f'<text x="{lx - 6}" y="{hy + 7 * (cell + gap) + 14}" font-size="10" fill="{MUTED}" text-anchor="end">less</text>')
    for i, col in enumerate(scale):
        parts.append(f'<rect x="{lx + i * 14}" y="{hy + 7 * (cell + gap) + 5}" width="11" height="11" rx="2.5" fill="{col}"/>')
    parts.append(f'<text x="{lx + 5 * 14 + 4}" y="{hy + 7 * (cell + gap) + 14}" font-size="10" fill="{MUTED}">more</text>')
    # languages
    ly = 302
    top = sorted(lang_totals.items(), key=lambda kv: -kv[1])
    total = sum(lang_totals.values()) or 1
    shown = dict(top[:7])
    other = sum(v for _, v in top[7:])
    if other:
        shown["Other"] = other
    parts.append(f'<text x="20" y="{ly}" font-size="13" font-weight="700" fill="{TEXT}">Languages across public repositories</text>')
    parts.append(lang_bar(shown, 20, ly + 14, 800, 10, "lb"))
    for i, (name, size) in enumerate(shown.items()):
        col, row = i % 4, i // 4
        x, y = 20 + col * 205, ly + 52 + row * 24
        parts.append(
            f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{LANG_COLORS.get(name, MUTED)}"/>'
            f'<text x="{x + 16}" y="{y}" font-size="12.5" fill="{TEXT}">{t(name)}</text>'
            f'<text x="{x + 180}" y="{y}" class="mono" font-size="11.5" fill="{MUTED}" text-anchor="end">{size * 100 / total:.1f}%</text>'
        )
    return svg(840, 412, "\n".join(parts))


COMMIT_ICONS = {"feat": "✨", "fix": "🐛", "docs": "📝", "chore": "🧹", "refactor": "♻️",
                "test": "🧪", "perf": "⚡", "ci": "🤖", "build": "📦", "style": "🎨"}


def recent_activity(repos: list[dict], limit: int = 6) -> str:
    """Latest commit of the most recently pushed public repositories."""
    rows = []
    for r in sorted(repos, key=lambda r: r["pushed_at"], reverse=True):
        if r["name"] == USER:
            continue
        try:
            commits = rest(f"repos/{USER}/{r['name']}/commits?per_page=1")
        except Exception:  # empty repository
            continue
        if not commits:
            continue
        c = commits[0]["commit"]
        msg = c["message"].splitlines()[0].strip()
        kind = re.match(r"^(\w+)(\(.*?\))?!?:", msg)
        icon = COMMIT_ICONS.get(kind.group(1).lower(), "🔨") if kind else "🔨"
        if len(msg) > 64:
            msg = msg[:63].rstrip() + "…"
        msg = msg.replace("|", "\\|").replace("`", "'")
        date = dt.datetime.fromisoformat(c["committer"]["date"].replace("Z", "+00:00")).strftime("%b&nbsp;%d,&nbsp;%Y")
        rows.append(f"| {icon} | **[{r['name']}]({r['html_url']})**<br/><sub>{escape(msg)}</sub> | {date} |")
        if len(rows) >= limit:
            break
    if not rows:
        return "_No public activity yet._"
    return "| | Latest commit | When |\n|:-:|---|--:|\n" + "\n".join(rows)


def replace_block(text: str, tag: str, content: str) -> str:
    pattern = re.compile(rf"(<!--{tag}:START-->)(.*?)(<!--{tag}:END-->)", re.S)
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", text)


def main() -> None:
    write("hero.svg", hero())
    write("journey.svg", journey())
    write("footer.svg", footer())
    for i, (title, sub, color) in enumerate([
        ("About me", "who I am, what I care about", ORANGE),
        ("Toolbox", "languages, frameworks and the tools around them", CYAN),
        ("Featured work", "live cards — stars, languages and dates refresh daily", RED),
        ("Activity", "a heatmap, the numbers and what I touched recently", VIOLET),
        ("Journey & principles", "how I got here and how I work", GREEN),
    ], start=1):
        write(f"section-{i}.svg", section(f"{i:02d}", title, sub, color))

    repos = [r for r in rest(f"users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
    by_name = {r["name"]: r for r in repos}
    lang_totals: dict[str, int] = {}
    for r in repos:
        for k, v in rest(f"repos/{USER}/{r['name']}/languages").items():
            lang_totals[k] = lang_totals.get(k, 0) + v
    for name, emoji, accent, tagline, desc in FEATURED:
        if name in by_name:
            langs = rest(f"repos/{USER}/{name}/languages")
            write(f"card-{name.lower()}.svg", repo_card(by_name[name], langs, emoji, accent, tagline, desc))
    write("dashboard.svg", dashboard(contributions(), repos, lang_totals))

    readme = ROOT / "README.md"
    text = replace_block(readme.read_text(encoding="utf-8"), "ACTIVITY", recent_activity(repos))
    readme.write_text(bust_cache(text), encoding="utf-8")


def bust_cache(text: str) -> str:
    """Pin each generated image URL to its content hash so GitHub's CDN never serves a stale copy."""
    def stamp(m: re.Match) -> str:
        f = OUT / m.group(1)
        digest = hashlib.sha1(f.read_bytes()).hexdigest()[:10] if f.exists() else "0"
        return f"assets/generated/{m.group(1)}?v={digest}"
    return re.sub(r"assets/generated/([\w.-]+\.svg)(\?v=\w+)?", stamp, text)


if __name__ == "__main__":
    main()
