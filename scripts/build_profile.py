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
# Ice-blue primary with a warm orange accent.
THEMES = {
    "dark": dict(
        BG="#0A0E1A", PANEL="#0F1526", PANEL2="#131B30", BORDER="#1F2A44",
        TEXT="#E8EEF7", MUTED="#8A97B1", FAINT="#3A4766",
        ICE="#7DD3FC", ICE2="#38BDF8", BEAK="#FB923C", SNOW="#F8FAFC",
        MINT="#5EEAD4", LILAC="#A5B4FC",
        HERO_A="#070B16", HERO_B="#0F1A33", STAR_OP="0.8", AURORA_OP="0.35",
        TILE_A="#1E3A5F", TILE_B="#0B1630", TILE_TEXT="#F8FAFC",
    ),
    "light": dict(
        BG="#F6F8FB", PANEL="#FFFFFF", PANEL2="#F1F5FA", BORDER="#D8E0EA",
        TEXT="#0F172A", MUTED="#5B6678", FAINT="#C5CFDC",
        ICE="#0284C7", ICE2="#0369A1", BEAK="#EA580C", SNOW="#FFFFFF",
        MINT="#0F766E", LILAC="#4F46E5",
        HERO_A="#EFF7FF", HERO_B="#E0F2FE", STAR_OP="0.0", AURORA_OP="0.28",
        TILE_A="#0EA5E9", TILE_B="#0369A1", TILE_TEXT="#FFFFFF",
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
def emblem(cx: float, cy: float) -> str:
    """Monogram logo: a glass tile with "p." circled by slow orbits."""
    return f"""
<g transform="translate({cx} {cy})">
  <circle r="104" fill="none" stroke="{ICE}" stroke-opacity="0.18" stroke-dasharray="2 7"/>
  <circle r="80" fill="none" stroke="{ICE}" stroke-opacity="0.28"/>
  <g class="spin"><circle cx="80" cy="0" r="5" fill="{ICE}"/><circle cx="-80" cy="0" r="3" fill="{MINT}"/></g>
  <g class="spin2"><circle cx="0" cy="-104" r="4" fill="{BEAK}"/><circle cx="0" cy="104" r="2.5" fill="{LILAC}"/></g>
  <rect x="-52" y="-52" width="104" height="104" rx="28" fill="url(#tile)" stroke="{ICE}" stroke-opacity="0.55"/>
  <rect x="-52" y="-52" width="104" height="52" rx="28" fill="{SNOW}" fill-opacity="0.07"/>
  <text x="-4" y="22" font-size="66" font-weight="800" fill="{TILE_TEXT}" text-anchor="middle" letter-spacing="-2">p<tspan fill="{BEAK}">.</tspan></text>
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
        ".spin{animation:sp 18s linear infinite}.spin2{animation:sp 28s linear infinite reverse}@keyframes sp{to{transform:rotate(360deg)}}"
        ".tw{opacity:" + STAR_OP + ";animation:tw 4s ease-in-out infinite}@keyframes tw{50%{opacity:.15}}"
        ".au{animation:au 9s ease-in-out infinite}@keyframes au{50%{transform:translateX(-30px)}}"
    )
    body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{HERO_A}"/><stop offset="1" stop-color="{HERO_B}"/></linearGradient>
  <linearGradient id="au" x1="0" x2="1"><stop offset="0" stop-color="{MINT}" stop-opacity="0"/><stop offset=".4" stop-color="{MINT}"/><stop offset=".7" stop-color="{ICE}"/><stop offset="1" stop-color="{LILAC}" stop-opacity="0"/></linearGradient>
  <linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="{TEXT}"/><stop offset="1" stop-color="{ICE}"/></linearGradient>
  <linearGradient id="tile" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{TILE_A}"/><stop offset="1" stop-color="{TILE_B}"/></linearGradient>
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
{emblem(690, 150)}
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


# Line icons drawn on a 24x24 grid (stroke only), so they look the same everywhere.
ICONS = {
    "layers": '<path d="M12 3 2 8l10 5 10-5-10-5Z"/><path d="m2 13 10 5 10-5"/><path d="m2 17.5 10 5 10-5" opacity=".55"/>',
    "shield": '<path d="M12 2.5 4 5.5v6c0 5 3.4 8.6 8 10 4.6-1.4 8-5 8-10v-6l-8-3Z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    "spark": '<path d="M12 2.5c.6 4.6 2.9 6.9 7.5 7.5-4.6.6-6.9 2.9-7.5 7.5-.6-4.6-2.9-6.9-7.5-7.5 4.6-.6 6.9-2.9 7.5-7.5Z"/><path d="M19 16.5c.3 2 1.2 2.9 3 3.2-1.8.3-2.7 1.2-3 3.2-.3-2-1.2-2.9-3-3.2 1.8-.3 2.7-1.2 3-3.2Z"/>',
    "devices": '<rect x="2" y="4" width="15" height="11" rx="2"/><path d="M6 19h7M9.5 15v4"/><rect x="17" y="9" width="5.5" height="11" rx="1.5"/>',
    "pipeline": '<circle cx="5" cy="6" r="2.5"/><circle cx="5" cy="18" r="2.5"/><circle cx="19" cy="12" r="2.5"/><path d="M5 8.5v7M7.3 7l9.4 4M7.3 17l9.4-4"/>',
}


def icon(name: str, x: float, y: float, color: str, size: float = 44) -> str:
    s = (size - 20) / 24
    return (
        f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="12" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-opacity="0.35"/>'
        f'<g transform="translate({x + 10} {y + 10}) scale({s:.3f})" fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>'
    )


def tags(x: float, y: float, labels: list[str], color: str) -> str:
    out = []
    for label in labels:
        w = len(label) * 6.6 + 22
        out.append(
            f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="24" rx="7" fill="{PANEL2}" stroke="{BORDER}"/>'
            f'<text x="{x + 11:.0f}" y="{y + 16}" class="mono" font-size="11" fill="{color}">{t(label)}</text>'
        )
        x += w + 8
    return "".join(out)


EXPERTISE = [
    ("layers", "Kiến trúc hệ thống & Backend", "ICE",
     "Hệ thống chịu tải, dễ mở rộng, dễ bảo trì lâu dài",
     ["Modular monolith, tách service khi thật sự cần",
      "DDD, Clean Architecture, CQRS cho nghiệp vụ khó",
      "Event-driven với Redis/BullMQ, retry & idempotency",
      "Tối ưu PostgreSQL, migration không downtime"],
     ["NestJS", "PostgreSQL", "Redis", "BullMQ"]),
    ("shield", "Bảo mật & nền tảng doanh nghiệp", "LILAC",
     "Nền móng cho khối công và doanh nghiệp lớn",
     ["SSO, OAuth2/JWT, RBAC & ABAC đa tenant",
      "Phân quyền tới từng bản ghi, audit log đầy đủ",
      "Workflow engine phê duyệt nhiều cấp, nhiều nhánh",
      "Secret management, secure-by-default từ thiết kế"],
     ["OAuth2", "RBAC", "Audit", "Workflow"]),
    ("spark", "Sản phẩm AI-native", "MINT",
     "Đưa LLM vào nghiệp vụ thật, không chỉ là demo",
     ["Tích hợp LLM vào luồng làm việc hằng ngày",
      "RAG, tool calling, agent có kiểm soát",
      "Eval & guardrail trước khi lên production",
      "UX cho AI: minh bạch, kiểm chứng, hoàn tác được"],
     ["LLM", "RAG", "Agents", "Evals"]),
    ("devices", "Web, Desktop & Mobile", "BEAK",
     "Giao diện nhanh, gọn, dễ dùng trên mọi màn hình",
     ["React/Next.js cho dashboard & form nghiệp vụ lớn",
      "Rust + Tauri: app desktop nhẹ, local-first",
      "Flutter cho mobile đa nền tảng",
      "Design system, hiệu năng & accessibility"],
     ["Next.js", "Tauri", "Flutter", "Tailwind"]),
]

DELIVERY = [
    ("CI/CD có cổng chặn", "lint · test · build bắt buộc xanh"),
    ("Container hoá", "Docker · Nginx · mọi môi trường"),
    ("Quan sát hệ thống", "metrics · health check · log"),
    ("Kiểm thử thật", "test phải fail được mới đáng tin"),
]


def what_i_do() -> str:
    cw, ch, gap = 411, 262, 18
    parts = []
    for i, (ic, title, col, tagline, bullets, chips) in enumerate(EXPERTISE):
        color = globals()[col]
        x, y = (i % 2) * (cw + gap) + 0.5, (i // 2) * (ch + gap) + 0.5
        parts.append(
            f'<g><rect x="{x}" y="{y}" width="{cw - 1}" height="{ch - 1}" rx="16" fill="{PANEL}" stroke="{BORDER}"/>'
            f'<rect x="{x}" y="{y}" width="{cw - 1}" height="{ch - 1}" rx="16" fill="url(#glow{col})"/>'
            + icon(ic, x + 22, y + 22, color)
            + f'<text x="{x + 80}" y="{y + 41}" font-size="16.5" font-weight="700" fill="{TEXT}">{t(title)}</text>'
            f'<text x="{x + 80}" y="{y + 61}" font-size="12.5" fill="{MUTED}">{t(tagline)}</text>'
            f'<rect x="{x + 22}" y="{y + 84}" width="{cw - 45}" height="1" fill="{BORDER}"/>'
            + "".join(
                f'<circle cx="{x + 27}" cy="{y + 108 + j * 26}" r="2.5" fill="{color}"/>'
                f'<text x="{x + 38}" y="{y + 112.5 + j * 26}" font-size="13" fill="{TEXT}" fill-opacity="0.88">{t(b)}</text>'
                for j, b in enumerate(bullets)
            )
            + tags(x + 22, y + ch - 46, chips, color)
            + "</g>"
        )
    # wide delivery strip
    y0 = 2 * (ch + gap) + 0.5
    parts.append(
        f'<rect x="0.5" y="{y0}" width="839" height="118" rx="16" fill="{PANEL}" stroke="{BORDER}"/>'
        + icon("pipeline", 22.5, y0 + 22, ICE2)
        + f'<text x="80.5" y="{y0 + 41}" font-size="16.5" font-weight="700" fill="{TEXT}">DevOps &amp; chất lượng</text>'
        f'<text x="80.5" y="{y0 + 61}" font-size="12.5" fill="{MUTED}">Đưa code lên production an toàn, đều đặn, không hồi hộp</text>'
    )
    for k, (head, sub) in enumerate(DELIVERY):
        x = 22.5 + k * 202
        parts.append(
            f'<rect x="{x}" y="{y0 + 80}" width="3" height="26" rx="1.5" fill="{ICE2}"/>'
            f'<text x="{x + 12}" y="{y0 + 91}" font-size="12.5" font-weight="700" fill="{TEXT}">{t(head)}</text>'
            f'<text x="{x + 12}" y="{y0 + 106}" font-size="11" fill="{MUTED}">{t(sub)}</text>'
        )
    defs = "<defs>" + "".join(
        f'<radialGradient id="glow{c}" cx="0" cy="0" r="0.9"><stop offset="0" stop-color="{globals()[c]}" stop-opacity="0.13"/>'
        f'<stop offset="1" stop-color="{globals()[c]}" stop-opacity="0"/></radialGradient>'
        for c in ("ICE", "LILAC", "MINT", "BEAK")
    ) + "</defs>"
    return svg(840, int(y0 + 119), defs + "\n".join(parts))


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
<text x="420" y="46" font-size="15.5" fill="{TEXT}" text-anchor="middle" font-weight="600">Cảm ơn bạn đã ghé thăm 👋</text>
<text x="420" y="70" class="mono" font-size="11.5" fill="{MUTED}" text-anchor="middle">penguy. · made with care in Hà Nội</text>
"""
    return svg(840, 86, body)


SECTIONS = [
    ("Về mình", "mình là ai và quan tâm điều gì", "ICE"),
    ("Chuyên môn", "từ kiến trúc hệ thống tới lúc chạy ổn định trên production", "MINT"),
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
