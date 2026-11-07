#!/usr/bin/env python3
"""Draw the SVG artwork for the profile README (intro only, no project cards).

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
# "Polar night" identity: ice-blue primary, a warm beak-orange accent.
THEMES = {
    "dark": dict(
        BG="#0A0E1A", PANEL="#0F1526", PANEL2="#131B30", BORDER="#1F2A44",
        TEXT="#E8EEF7", MUTED="#8A97B1", FAINT="#3A4766",
        ICE="#7DD3FC", ICE2="#38BDF8", BEAK="#FB923C", SNOW="#F8FAFC",
        MINT="#5EEAD4", LILAC="#A5B4FC",
        HERO_A="#070B16", HERO_B="#0F1A33", STAR_OP="0.8", AURORA_OP="0.35",
        BODY="#111827", BELLY="#F1F5F9",
    ),
    "light": dict(
        BG="#F6F8FB", PANEL="#FFFFFF", PANEL2="#F1F5FA", BORDER="#D8E0EA",
        TEXT="#0F172A", MUTED="#5B6678", FAINT="#C5CFDC",
        ICE="#0284C7", ICE2="#0369A1", BEAK="#EA580C", SNOW="#FFFFFF",
        MINT="#0F766E", LILAC="#4F46E5",
        HERO_A="#EFF7FF", HERO_B="#E0F2FE", STAR_OP="0.0", AURORA_OP="0.28",
        BODY="#0F172A", BELLY="#FFFFFF",
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


# ── pieces ─────────────────────────────────────────────────────────────────
def penguin(cx: float, cy: float, s: float = 1.0) -> str:
    """A small, friendly penguin mascot, centred at (cx, cy)."""
    return f"""
<g transform="translate({cx} {cy}) scale({s})">
  <ellipse cx="0" cy="92" rx="58" ry="8" fill="{ICE}" fill-opacity="0.18"/>
  <path d="M-46 30 C-52 -40 -30 -78 0 -78 C30 -78 52 -40 46 30 C44 70 24 90 0 90 C-24 90 -44 70 -46 30Z" fill="{BODY}" stroke="{ICE}" stroke-opacity="0.35" stroke-width="2"/>
  <path d="M-30 10 C-34 -30 -18 -50 0 -50 C18 -50 34 -30 30 10 C30 52 16 76 0 76 C-16 76 -30 52 -30 10Z" fill="{BELLY}"/>
  <g class="wave"><path d="M44 0 C66 6 72 30 62 44 C56 34 50 26 42 22Z" fill="{BODY}" stroke="{ICE}" stroke-opacity="0.35" stroke-width="2"/></g>
  <path d="M-44 0 C-64 8 -68 32 -58 44 C-52 34 -46 26 -40 22Z" fill="{BODY}" stroke="{ICE}" stroke-opacity="0.35" stroke-width="2"/>
  <g class="blink"><circle cx="-14" cy="-36" r="5.5" fill="{BODY}"/><circle cx="14" cy="-36" r="5.5" fill="{BODY}"/>
  <circle cx="-12.5" cy="-38" r="1.8" fill="{SNOW}"/><circle cx="15.5" cy="-38" r="1.8" fill="{SNOW}"/></g>
  <path d="M-9 -26 L9 -26 L0 -15Z" fill="{BEAK}"/>
  <circle cx="-24" cy="-22" r="5" fill="{BEAK}" fill-opacity="0.25"/><circle cx="24" cy="-22" r="5" fill="{BEAK}" fill-opacity="0.25"/>
  <ellipse cx="-16" cy="90" rx="13" ry="5" fill="{BEAK}"/><ellipse cx="16" cy="90" rx="13" ry="5" fill="{BEAK}"/>
  <path d="M-30 -66 C-10 -84 10 -84 30 -66 L26 -58 C8 -72 -8 -72 -26 -58Z" fill="{ICE}"/>
  <rect x="-34" y="-66" width="68" height="9" rx="4.5" fill="{ICE2}"/>
</g>"""


def chip(x: float, y: float, label: str, color: str) -> tuple[str, float]:
    w = len(label) * 7.0 + 30
    return (
        f'<rect x="{x}" y="{y}" width="{w:.0f}" height="30" rx="15" fill="{color}" fill-opacity="0.10" stroke="{color}" stroke-opacity="0.45"/>'
        f'<circle cx="{x + 14}" cy="{y + 15}" r="3.5" fill="{color}"/>'
        f'<text x="{x + 24}" y="{y + 19.5}" font-size="13" fill="{TEXT}">{t(label)}</text>'
    ), w


def hero() -> str:
    stars = "".join(
        f'<circle class="tw" cx="{x}" cy="{y}" r="{r}" fill="{SNOW}" style="animation-delay:{d}s"/>'
        for x, y, r, d in [(470, 40, 1.4, 0), (520, 92, 1, 1.2), (612, 28, 1.6, .6), (700, 70, 1.1, 2),
                           (780, 30, 1.3, 1.5), (808, 120, 1, .3), (430, 130, 1, 2.4), (560, 150, 1.2, 1.8)]
    )
    chips, x = [], 48
    for label, color in [("Full-stack", ICE), ("AI-native products", MINT), ("Hà Nội · VN", BEAK)]:
        c, w = chip(x, 228, label, color)
        chips.append(c)
        x += w + 10
    style = (
        ".tw{opacity:" + STAR_OP + ";animation:tw 4s ease-in-out infinite}@keyframes tw{50%{opacity:.15}}"
        ".au{animation:au 9s ease-in-out infinite}@keyframes au{50%{transform:translateX(-30px)}}"
        ".wave{transform-origin:44px 6px;animation:wv 2.6s ease-in-out infinite}@keyframes wv{0%,60%,100%{transform:rotate(0)}70%{transform:rotate(-22deg)}85%{transform:rotate(8deg)}}"
        ".blink{transform-origin:0 -36px;animation:bl 5s infinite}@keyframes bl{0%,94%,100%{transform:scaleY(1)}96%{transform:scaleY(.1)}}"
    )
    body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{HERO_A}"/><stop offset="1" stop-color="{HERO_B}"/></linearGradient>
  <linearGradient id="au" x1="0" x2="1"><stop offset="0" stop-color="{MINT}" stop-opacity="0"/><stop offset=".4" stop-color="{MINT}"/><stop offset=".7" stop-color="{ICE}"/><stop offset="1" stop-color="{LILAC}" stop-opacity="0"/></linearGradient>
  <linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="{TEXT}"/><stop offset="1" stop-color="{ICE}"/></linearGradient>
  <filter id="blur"><feGaussianBlur stdDeviation="22"/></filter>
  <clipPath id="clip"><rect width="840" height="300" rx="20"/></clipPath>
</defs>
<g clip-path="url(#clip)">
  <rect width="840" height="300" fill="url(#bg)"/>
  <g class="au" opacity="{AURORA_OP}" filter="url(#blur)"><path d="M380 70 C500 10 620 120 740 50 S900 40 900 40 L900 110 C780 170 640 80 520 140 S380 130 380 130Z" fill="url(#au)"/></g>
  {stars}
  <path d="M520 300 L600 238 L640 258 L700 214 L780 262 L840 236 L840 300Z" fill="{ICE}" fill-opacity="0.10"/>
  <path d="M440 300 C520 278 640 282 840 290 L840 300Z" fill="{SNOW}" fill-opacity="0.08"/>
</g>
<rect x="0.5" y="0.5" width="839" height="299" rx="20" fill="none" stroke="{BORDER}"/>
<text x="48" y="74" class="mono" font-size="13" fill="{ICE}" letter-spacing="3">XIN CHÀO, MÌNH LÀ</text>
<text x="46" y="138" font-size="60" font-weight="800" fill="url(#name)" letter-spacing="-1.5">penguy<tspan fill="{BEAK}">.</tspan></text>
<text x="48" y="174" font-size="19" font-weight="600" fill="{TEXT}">Full-stack Software Engineer</text>
<text x="48" y="200" font-size="14.5" fill="{MUTED}">Biến những quy trình rối rắm thành phần mềm gọn gàng, đáng tin.</text>
{''.join(chips)}
{penguin(686, 148, 1.0)}
"""
    return svg(840, 300, body, style)


def section(num: str, title: str, sub: str, color: str) -> str:
    body = f"""
<defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{color}"/><stop offset=".5" stop-color="{color}" stop-opacity=".15"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>
<rect x="2" y="12" width="40" height="40" rx="12" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-opacity="0.5"/>
<text x="22" y="38" class="mono" font-size="14" font-weight="700" fill="{color}" text-anchor="middle">{num}</text>
<text x="58" y="31" font-size="20" font-weight="700" fill="{TEXT}">{t(title)}</text>
<text x="58" y="50" font-size="12.5" fill="{MUTED}">{t(sub)}</text>
<rect x="2" y="64" width="836" height="1.5" rx="1" fill="url(#l)"/>
"""
    return svg(840, 70, body)


def card_grid(items: list[tuple[str, str, str, list[str]]], height: int) -> str:
    """Row of 3 cards: (icon, title, accent, lines)."""
    w, gap = 268, 18
    parts = []
    for i, (icon, title, color, lines) in enumerate(items):
        x = i * (w + gap) + 0.5
        parts.append(
            f'<g><rect x="{x}" y="0.5" width="{w - 1}" height="{height - 1}" rx="16" fill="{PANEL}" stroke="{BORDER}"/>'
            f'<rect x="{x + 22}" y="0.5" width="44" height="3" rx="1.5" fill="{color}"/>'
            f'<rect x="{x + 22}" y="26" width="42" height="42" rx="12" fill="{color}" fill-opacity="0.12"/>'
            f'<text x="{x + 43}" y="55" font-size="20" text-anchor="middle">{icon}</text>'
            f'<text x="{x + 22}" y="98" font-size="16.5" font-weight="700" fill="{TEXT}">{t(title)}</text>'
            + "".join(
                f'<text x="{x + 22}" y="{126 + j * 22}" font-size="13" fill="{MUTED}">'
                f'<tspan fill="{color}">›</tspan>  {t(line)}</text>'
                for j, line in enumerate(lines)
            )
            + "</g>"
        )
    return svg(840, height, "\n".join(parts))


def what_i_do() -> str:
    return card_grid([
        ("⚙️", "Backend & nền tảng", ICE, ["API & kiến trúc NestJS", "Auth, phân quyền, audit", "Queue, job nền, cache"]),
        ("🖥️", "Web & giao diện", MINT, ["React · Next.js", "Dashboard, form nghiệp vụ", "UI gọn, dễ dùng, nhanh"]),
        ("📱", "Desktop & mobile", BEAK, ["Rust · Tauri", "Flutter · Dart", "Ưu tiên chạy offline"]),
    ], 206)


def principles() -> str:
    return card_grid([
        ("🔍", "Bằng chứng > phỏng đoán", ICE, ["Mỗi kết luận đi kèm", "lệnh, log hoặc đường link"]),
        ("🪶", "Thay đổi nhỏ, dễ lùi", MINT, ["Một lát cắt, một nhánh,", "một PR dễ review"]),
        ("🔐", "An toàn ngay từ đầu", LILAC, ["Quyền, audit, bí mật", "được tính từ ngày đầu"]),
    ], 184)


def now_panel() -> str:
    rows = [
        ("Đang làm", "Không gian làm việc AI-native cho doanh nghiệp & khối công", ICE),
        ("Đang học", "Rust & Tauri chuyên sâu, thiết kế sản phẩm có LLM", MINT),
        ("Hỏi mình về", "Kiến trúc NestJS, queue, xác thực, CI gate", BEAK),
        ("Ngôn ngữ", "Tiếng Việt · English", LILAC),
    ]
    parts = [f'<rect x="0.5" y="0.5" width="839" height="{44 + len(rows) * 40}" rx="16" fill="{PANEL}" stroke="{BORDER}"/>']
    for i, (k, v, c) in enumerate(rows):
        y = 22 + i * 40
        if i:
            parts.append(f'<rect x="24" y="{y}" width="792" height="1" fill="{BORDER}"/>')
        parts.append(
            f'<circle cx="34" cy="{y + 21}" r="4" fill="{c}"/>'
            f'<text x="50" y="{y + 26}" class="mono" font-size="12.5" fill="{c}" letter-spacing="1">{t(k.upper())}</text>'
            f'<text x="200" y="{y + 26}" font-size="14.5" fill="{TEXT}">{t(v)}</text>'
        )
    return svg(840, 44 + len(rows) * 40 + 1, "\n".join(parts))


def footer() -> str:
    body = f"""
<defs><linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="{ICE}" stop-opacity="0"/><stop offset=".5" stop-color="{ICE}"/><stop offset="1" stop-color="{ICE}" stop-opacity="0"/></linearGradient></defs>
<rect x="120" y="10" width="600" height="1.5" fill="url(#f)"/>
<text x="420" y="46" font-size="15.5" fill="{TEXT}" text-anchor="middle" font-weight="600">Cảm ơn bạn đã ghé thăm 🐧</text>
<text x="420" y="70" class="mono" font-size="11.5" fill="{MUTED}" text-anchor="middle">penguy. · made with care in Hà Nội</text>
"""
    return svg(840, 86, body)


SECTIONS = [
    ("Về mình", "mình là ai và quan tâm điều gì", "ICE"),
    ("Mình làm gì", "những mảng mình làm hằng ngày", "MINT"),
    ("Công cụ", "ngôn ngữ, framework và hạ tầng quen tay", "BEAK"),
    ("Cách mình làm việc", "vài nguyên tắc mình giữ", "LILAC"),
]


def main() -> None:
    for old in OUT.glob("*.svg"):
        old.unlink()
    for theme in THEMES:
        apply_theme(theme)
        w = lambda name, content: write(f"{name}-{theme}.svg", content)  # noqa: E731
        w("hero", hero())
        w("now", now_panel())
        w("what", what_i_do())
        w("principles", principles())
        w("footer", footer())
        for i, (title, sub, color) in enumerate(SECTIONS, start=1):
            w(f"section-{i}", section(f"{i:02d}", title, sub, globals()[color]))
    readme = ROOT / "README.md"
    readme.write_text(bust_cache(readme.read_text(encoding="utf-8")), encoding="utf-8")


def bust_cache(text: str) -> str:
    """Pin each generated image URL to its content hash so GitHub's CDN never serves a stale copy."""
    def stamp(m: re.Match) -> str:
        f = OUT / m.group(1)
        digest = hashlib.sha1(f.read_bytes()).hexdigest()[:10] if f.exists() else "0"
        return f"assets/generated/{m.group(1)}?v={digest}"
    return re.sub(r"assets/generated/([\w.-]+\.svg)(\?v=\w+)?", stamp, text)


if __name__ == "__main__":
    main()
