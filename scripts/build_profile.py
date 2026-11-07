#!/usr/bin/env python3
"""Draw the SVG artwork for the profile README (introduction only, no project cards).

Runs in GitHub Actions on every push to scripts/ (see .github/workflows/build-profile.yml).
Standard library only; no network access needed.
"""
from __future__ import annotations

import hashlib
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "generated"

# ── palettes ───────────────────────────────────────────────────────────────
# Restrained on purpose: neutrals plus one accent (sky) and a single warm dot.
THEMES = {
    "dark": dict(
        BG="#0B0F17", PANEL="#0F141E", PANEL2="#151B27", BORDER="#232B3A",
        TEXT="#E6EAF0", SOFT="#B4BCC9", MUTED="#7D8798",
        ACCENT="#7DD3FC", DOT="#FB923C", OK="#4ADE80", GRID="#1A2130",
    ),
    "light": dict(
        BG="#FFFFFF", PANEL="#FFFFFF", PANEL2="#F5F7FA", BORDER="#DDE2E9",
        TEXT="#0F172A", SOFT="#334155", MUTED="#64748B",
        ACCENT="#0369A1", DOT="#EA580C", OK="#16A34A", GRID="#EEF2F6",
    ),
}


def apply_theme(name: str) -> None:
    globals().update(THEMES[name])


apply_theme("dark")
SANS = "'Segoe UI', Ubuntu, -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"


def t(s) -> str:
    return escape(str(s), quote=True)


def svg(w: int, h: int, body: str, style: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">\n'
        f"<style>text{{font-family:{SANS}}} .mono{{font-family:{MONO}}}{style}</style>\n{body}\n</svg>\n"
    )


def write(name: str, content: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")


def panel(w: float, h: float, x: float = 0.5, y: float = 0.5) -> str:
    return f'<rect x="{x}" y="{y}" width="{w - 1}" height="{h - 1}" rx="14" fill="{PANEL}" stroke="{BORDER}"/>'


# ── hero ───────────────────────────────────────────────────────────────────
SPEC = [
    ("role", "Full-stack Engineer"),
    ("focus", "Platforms · Security · AI"),
    ("core", "NestJS · Postgres · Redis"),
    ("also", "React · Rust · Flutter"),
    ("based", "Hanoi, Vietnam (UTC+7)"),
]


def hero() -> str:
    rows = []
    for i, (k, v) in enumerate(SPEC):
        y = 132 + i * 24
        rows.append(
            f'<text x="532" y="{y}" class="mono" font-size="12" fill="{MUTED}">{t(k)}</text>'
            f'<text x="588" y="{y}" class="mono" font-size="12" fill="{TEXT}">{t(v)}</text>'
        )
    y = 132 + len(SPEC) * 24
    rows.append(
        f'<text x="532" y="{y}" class="mono" font-size="12" fill="{MUTED}">status</text>'
        f'<circle class="pulse" cx="593" cy="{y - 4}" r="3.5" fill="{OK}"/>'
        f'<text x="602" y="{y}" class="mono" font-size="12" fill="{OK}">open to conversations</text>'
    )
    style = ".pulse{animation:p 2.4s ease-in-out infinite}@keyframes p{50%{opacity:.25}}"
    body = f"""
<defs>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{GRID}"/></pattern>
  <linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{PANEL}"/><stop offset=".55" stop-color="{PANEL}" stop-opacity=".6"/><stop offset="1" stop-color="{PANEL}" stop-opacity="0"/></linearGradient>
  <clipPath id="c"><rect width="840" height="300" rx="16"/></clipPath>
</defs>
<g clip-path="url(#c)">
  <rect width="840" height="300" fill="{PANEL}"/>
  <rect width="840" height="300" fill="url(#grid)"/>
  <rect width="840" height="300" fill="url(#fade)"/>
</g>
<rect x="0.5" y="0.5" width="839" height="299" rx="16" fill="none" stroke="{BORDER}"/>
<rect x="48" y="58" width="22" height="2" fill="{ACCENT}"/>
<text x="80" y="63" class="mono" font-size="11.5" fill="{ACCENT}" letter-spacing="2.4">SOFTWARE ENGINEER</text>
<text x="45" y="138" font-size="66" font-weight="800" fill="{TEXT}" letter-spacing="-2.5">penguy<tspan fill="{DOT}">.</tspan></text>
<text x="48" y="182" font-size="17" fill="{SOFT}">I design and build secure, scalable platforms,</text>
<text x="48" y="206" font-size="17" fill="{SOFT}">from the domain model all the way to production.</text>
<text x="48" y="252" class="mono" font-size="11.5" fill="{MUTED}">Architecture  /  Enterprise platforms  /  AI products</text>
<rect x="508.5" y="56.5" width="292" height="210" rx="12" fill="{PANEL2}" stroke="{BORDER}"/>
<path d="M508.5 92.5h292" stroke="{BORDER}"/>
<circle cx="530" cy="75" r="4.5" fill="{BORDER}"/><circle cx="546" cy="75" r="4.5" fill="{BORDER}"/><circle cx="562" cy="75" r="4.5" fill="{BORDER}"/>
<text x="782" y="79" class="mono" font-size="11" fill="{MUTED}" text-anchor="end">profile.yaml</text>
{''.join(rows)}
"""
    return svg(840, 300, body, style)


# ── section header ─────────────────────────────────────────────────────────
def section(num: str, title: str, sub: str) -> str:
    body = f"""
<text x="0" y="33" class="mono" font-size="13" font-weight="700" fill="{ACCENT}">{num}</text>
<text x="34" y="34" font-size="22" font-weight="700" fill="{TEXT}" letter-spacing="-.3">{t(title)}</text>
<text x="840" y="33" font-size="12.5" fill="{MUTED}" text-anchor="end">{t(sub)}</text>
<rect x="0" y="50" width="840" height="1" fill="{BORDER}"/>
<rect x="0" y="49.5" width="26" height="2" fill="{ACCENT}"/>
"""
    return svg(840, 56, body)


# ── at a glance ────────────────────────────────────────────────────────────
GLANCE = [
    ("Currently", "Building an AI-native workspace for enterprise and public-sector teams"),
    ("Focus", "Platform architecture, access control, approval workflows, audit"),
    ("Exploring", "Rust & Tauri internals, product design for LLM features"),
    ("Ask me about", "NestJS architecture, job queues, authentication, CI quality gates"),
    ("Languages", "Vietnamese (native)  ·  English (professional working)"),
]


def glance() -> str:
    h = 24 + len(GLANCE) * 42
    parts = [panel(840, h)]
    for i, (k, v) in enumerate(GLANCE):
        y = 12 + i * 42
        if i:
            parts.append(f'<rect x="24" y="{y}" width="792" height="1" fill="{BORDER}"/>')
        parts.append(
            f'<text x="28" y="{y + 27}" class="mono" font-size="11.5" fill="{MUTED}" letter-spacing="1.2">{t(k.upper())}</text>'
            f'<text x="196" y="{y + 27}" font-size="14.5" fill="{TEXT}">{t(v)}</text>'
        )
    return svg(840, h, "\n".join(parts))


# ── expertise ──────────────────────────────────────────────────────────────
ICONS = {
    "layers": '<path d="M12 3 2 8l10 5 10-5-10-5Z"/><path d="m2 13 10 5 10-5"/><path d="m2 17.5 10 5 10-5" opacity=".55"/>',
    "shield": '<path d="M12 2.5 4 5.5v6c0 5 3.4 8.6 8 10 4.6-1.4 8-5 8-10v-6l-8-3Z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    "spark": '<path d="M12 2.5c.6 4.6 2.9 6.9 7.5 7.5-4.6.6-6.9 2.9-7.5 7.5-.6-4.6-2.9-6.9-7.5-7.5 4.6-.6 6.9-2.9 7.5-7.5Z"/><path d="M19 16.5c.3 2 1.2 2.9 3 3.2-1.8.3-2.7 1.2-3 3.2-.3-2-1.2-2.9-3-3.2 1.8-.3 2.7-1.2 3-3.2Z"/>',
    "devices": '<rect x="2" y="4" width="15" height="11" rx="2"/><path d="M6 19h7M9.5 15v4"/><rect x="17" y="9" width="5.5" height="11" rx="1.5"/>',
    "pipeline": '<circle cx="5" cy="6" r="2.5"/><circle cx="5" cy="18" r="2.5"/><circle cx="19" cy="12" r="2.5"/><path d="M5 8.5v7M7.3 7l9.4 4M7.3 17l9.4-4"/>',
}


def icon(name: str, x: float, y: float) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="40" height="40" rx="10" fill="{PANEL2}" stroke="{BORDER}"/>'
        f'<g transform="translate({x + 10} {y + 10}) scale(.84)" fill="none" stroke="{ACCENT}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>'
    )


def tags(x: float, y: float, labels: list[str]) -> str:
    out = []
    for label in labels:
        w = len(label) * 6.9 + 20
        out.append(
            f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="24" rx="6" fill="{PANEL2}" stroke="{BORDER}"/>'
            f'<text x="{x + 10:.0f}" y="{y + 16}" class="mono" font-size="11" fill="{SOFT}">{t(label)}</text>'
        )
        x += w + 8
    return "".join(out)


EXPERTISE = [
    ("layers", "Systems Architecture & Backend",
     "Services that scale and stay maintainable for years",
     ["Modular monoliths; split services only when it pays",
      "DDD, Clean Architecture and CQRS for complex domains",
      "Event-driven jobs on BullMQ with idempotent retries",
      "PostgreSQL tuning and zero-downtime migrations"],
     ["NestJS", "PostgreSQL", "Redis", "BullMQ"]),
    ("shield", "Security & Enterprise Platforms",
     "Foundations for enterprise and public-sector teams",
     ["SSO with OAuth2 / OIDC, multi-tenant RBAC & ABAC",
      "Record-level permissions with complete audit trails",
      "Multi-step, multi-branch approval workflow engines",
      "Secret management and secure-by-default design"],
     ["OIDC", "RBAC", "Audit", "Workflows"]),
    ("spark", "AI-native Products",
     "LLMs inside real workflows, not just demos",
     ["LLM features embedded in everyday business flows",
      "Retrieval (RAG), tool calling and guarded agents",
      "Evals and guardrails before anything ships",
      "AI UX that is transparent, verifiable, reversible"],
     ["LLM", "RAG", "Agents", "Evals"]),
    ("devices", "Web, Desktop & Mobile",
     "Fast, focused interfaces on every screen",
     ["React / Next.js for data-heavy dashboards and forms",
      "Rust + Tauri for lightweight, local-first desktop apps",
      "Flutter for cross-platform mobile",
      "Design systems, performance and accessibility"],
     ["Next.js", "Tauri", "Flutter", "Tailwind"]),
]

DELIVERY = [
    ("Gated CI/CD", "lint · test · build must pass"),
    ("Containerised", "Docker · Nginx · env parity"),
    ("Observability", "metrics · health checks · logs"),
    ("Real tests", "tests that can actually fail"),
]


def expertise() -> str:
    cw, ch, gap = 411, 258, 18
    parts = []
    for i, (ic, title, tagline, bullets, chips) in enumerate(EXPERTISE):
        x, y = (i % 2) * (cw + gap) + 0.5, (i // 2) * (ch + gap) + 0.5
        parts.append(
            f'<g><rect x="{x}" y="{y}" width="{cw - 1}" height="{ch - 1}" rx="14" fill="{PANEL}" stroke="{BORDER}"/>'
            + icon(ic, x + 24, y + 24)
            + f'<text x="{x + 78}" y="{y + 41}" font-size="16" font-weight="700" fill="{TEXT}">{t(title)}</text>'
            f'<text x="{x + 78}" y="{y + 60}" font-size="12.5" fill="{MUTED}">{t(tagline)}</text>'
            + "".join(
                f'<rect x="{x + 25}" y="{y + 98 + j * 26}" width="8" height="1.6" fill="{ACCENT}"/>'
                f'<text x="{x + 42}" y="{y + 103.5 + j * 26}" font-size="13" fill="{SOFT}">{t(b)}</text>'
                for j, b in enumerate(bullets)
            )
            + tags(x + 24, y + ch - 46, chips)
            + "</g>"
        )
    y0 = 2 * (ch + gap) + 0.5
    parts.append(
        f'<rect x="0.5" y="{y0}" width="839" height="122" rx="14" fill="{PANEL}" stroke="{BORDER}"/>'
        + icon("pipeline", 24.5, y0 + 24)
        + f'<text x="78.5" y="{y0 + 41}" font-size="16" font-weight="700" fill="{TEXT}">Engineering &amp; Delivery</text>'
        f'<text x="78.5" y="{y0 + 60}" font-size="12.5" fill="{MUTED}">Shipping to production safely, steadily and without drama</text>'
    )
    for k, (head, sub) in enumerate(DELIVERY):
        x = 24.5 + k * 200
        parts.append(
            f'<rect x="{x}" y="{y0 + 82}" width="2" height="28" fill="{ACCENT}"/>'
            f'<text x="{x + 12}" y="{y0 + 93}" font-size="12.5" font-weight="700" fill="{TEXT}">{t(head)}</text>'
            f'<text x="{x + 12}" y="{y0 + 109}" font-size="11" fill="{MUTED}">{t(sub)}</text>'
        )
    return svg(840, int(y0 + 123), "\n".join(parts))


# ── technology ─────────────────────────────────────────────────────────────
STACK = [
    ("Languages", ["TypeScript", "JavaScript", "Rust", "Python", "Java", "Dart"]),
    ("Backend", ["NestJS", "Node.js", "Express", "FastAPI", "Prisma", "TypeORM"]),
    ("Frontend", ["React", "Next.js", "Vite", "Redux", "Tailwind CSS"]),
    ("Desktop & Mobile", ["Tauri", "Flutter"]),
    ("Data & Messaging", ["PostgreSQL", "MongoDB", "Redis", "MySQL", "BullMQ"]),
    ("Infra & Tooling", ["Docker", "Nginx", "GitHub Actions", "Linux", "Jest", "Figma"]),
]


def stack() -> str:
    h = 20 + len(STACK) * 46
    parts = [panel(840, h)]
    for i, (k, items) in enumerate(STACK):
        y = 10 + i * 46
        if i:
            parts.append(f'<rect x="24" y="{y}" width="792" height="1" fill="{BORDER}"/>')
        parts.append(f'<text x="28" y="{y + 28}" font-size="13.5" font-weight="600" fill="{TEXT}">{t(k)}</text>')
        parts.append(tags(196, y + 11, items))
    return svg(840, h, "\n".join(parts))


# ── principles ─────────────────────────────────────────────────────────────
PRINCIPLES = [
    ("Evidence over assumptions", "Every claim ships with a command, a log or a link."),
    ("Small, reversible changes", "One slice, one branch, one reviewable pull request."),
    ("Secure by default", "Permissions, audit and secrets are designed in on day one."),
    ("Tests that can fail", "If breaking the code doesn't break the test, it isn't a test."),
]


def principles() -> str:
    cw, ch, gap = 411, 104, 18
    parts = []
    for i, (head, sub) in enumerate(PRINCIPLES):
        x, y = (i % 2) * (cw + gap) + 0.5, (i // 2) * (ch + gap) + 0.5
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cw - 1}" height="{ch - 1}" rx="14" fill="{PANEL}" stroke="{BORDER}"/>'
            f'<text x="{x + 24}" y="{y + 40}" class="mono" font-size="12" font-weight="700" fill="{ACCENT}">{i + 1:02d}</text>'
            f'<text x="{x + 54}" y="{y + 41}" font-size="16" font-weight="700" fill="{TEXT}">{t(head)}</text>'
            f'<text x="{x + 54}" y="{y + 68}" font-size="13" fill="{MUTED}">{t(sub)}</text>'
        )
    return svg(840, 2 * ch + gap, "\n".join(parts))


# ── footer ─────────────────────────────────────────────────────────────────
def footer() -> str:
    body = f"""
<rect x="0" y="8" width="840" height="1" fill="{BORDER}"/>
<text x="420" y="48" font-size="15" fill="{TEXT}" text-anchor="middle" font-weight="600">Always happy to talk platform engineering, enterprise systems and AI products.</text>
<text x="420" y="74" class="mono" font-size="11.5" fill="{MUTED}" text-anchor="middle">penguy<tspan fill="{DOT}">.</tspan>  ·  Hanoi, Vietnam</text>
"""
    return svg(840, 90, body)


SECTIONS = [
    ("About", "who I am and how I think"),
    ("Core expertise", "from system design to stable production"),
    ("Technology", "tools I reach for every day"),
    ("How I work", "principles I hold myself to"),
]


def main() -> None:
    for old in OUT.glob("*.svg"):
        old.unlink()
    for theme in THEMES:
        apply_theme(theme)
        w = lambda name, content: write(f"{name}-{theme}.svg", content)  # noqa: E731
        w("hero", hero())
        w("glance", glance())
        w("expertise", expertise())
        w("stack", stack())
        w("principles", principles())
        w("footer", footer())
        for i, (title, sub) in enumerate(SECTIONS, start=1):
            w(f"section-{i}", section(f"{i:02d}", title, sub))
    readme = ROOT / "README.md"
    readme.write_text(bust_cache(readme.read_text(encoding="utf-8")), encoding="utf-8")


def bust_cache(text: str) -> str:
    """Rename each SVG to name.<hash>.svg and point the README at it.

    A brand-new path per content change means neither raw.githubusercontent.com
    nor GitHub's image proxy can ever serve a stale copy.
    """
    names = {}
    for f in sorted(OUT.glob("*.svg")):
        digest = hashlib.sha1(f.read_bytes()).hexdigest()[:10]
        target = OUT / f"{f.stem}.{digest}.svg"
        f.rename(target)
        names[f.stem] = target.name
    return re.sub(
        r"assets/generated/([\w-]+?)(?:\.[0-9a-f]{10})?\.svg(?:\?v=\w+)?",
        lambda m: f"assets/generated/{names.get(m.group(1), m.group(1) + '.svg')}",
        text,
    )


if __name__ == "__main__":
    main()
