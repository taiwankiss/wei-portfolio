#!/usr/bin/env python3
"""Generate the static site in public/ from content/*.json.

Usage: python3 build.py
No dependencies. Media files live in public/media/<slug>/ and are referenced
from content/projects/*.json.
"""
import hashlib
import json
import os
import re
import shutil
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "public"
# The About page is the résumé site, copied in at build time when that project is present.
RESUME = ROOT.parent / "Resume"
# the old address (wei-portfolio.pages.dev) moves visitors to weilee01.com/ai-free/;
# the weilee01.com router fetches these same files but never runs scripts
OLD_HOST_REDIRECT = "<script>if (location.hostname === 'wei-portfolio.pages.dev') location.replace('https://weilee01.com/ai-free' + location.pathname + location.search + location.hash);</script>\n"
ACCENT = "#F4A711"
# Theme is set before first paint (saved choice, else the system setting); the button
# and everything else interactive that every page shares lives in /assets/ui.js
THEME_INIT = (
    "<script>(()=>{const t=localStorage.getItem('aifree-theme')||(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark');"
    "document.documentElement.dataset.theme=t;addEventListener('DOMContentLoaded',()=>{const c=document.querySelector('meta[name=theme-color]');"
    "if(c)c.content=t==='light'?'#efebe3':'#0f0e0d'})})();</script>\n"
)
# Sun and moon from PulsoIcon (static SVG; their hover motion is redone in CSS)
SUN = (
    '<svg class="i-sun" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle class="core" cx="12" cy="12" r="4"/>'
    '<g class="rays"><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/>'
    '<path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></g></svg>'
)
MOON = (
    '<svg class="i-moon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401"/></svg>'
)
MAIL = (
    '<svg class="i-mail" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path class="flap" d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7"/>'
    '<rect class="env" x="2" y="4" width="20" height="16" rx="2"/></svg>'
)
THEME_BTN = f'<button class="theme-btn" type="button" aria-label="Switch theme">{SUN}{MOON}</button>'
site = json.loads((ROOT / "content/site.json").read_text())
def load_project(f):
    """Read one project file. Pages CMS leaves out optional fields that were left
    blank (gallery, link, categories) and saves an empty editor as "<p></p>"."""
    p = json.loads(f.read_text())
    p.setdefault("categories", [])
    p.setdefault("gallery", [])
    for lang in ("zh", "en"):
        text = p.get(lang) or ""
        p[lang] = text if re.sub(r"<[^>]+>|&nbsp;|\s", "", text) else ""
    link = p.get("link") or {}
    if link.get("url") and not link.get("label"):
        link["label"] = "Visit"
    p["link"] = link
    return p


# One file per project (Pages CMS collection); newest first.
projects = sorted(
    (load_project(f) for f in (ROOT / "content/projects").glob("*.json")),
    key=lambda p: p["date"], reverse=True,
)

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400..800'
    '&family=Geist+Mono:wght@400;500&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">'
)
MARK = '<img src="/assets/img/mark.svg" width="36" height="36" alt="">'
ARROW = (
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">'
    '<path d="M7 17 17 7M9 7h8v8" fill="none" stroke="currentColor" stroke-width="2.2" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def asset(path):
    """URL with a content hash, so a new deploy never shows a cached old file."""
    digest = hashlib.md5((OUT / path.lstrip("/")).read_bytes()).hexdigest()[:8]
    return f"{path}?v={digest}"


# Grid rhythm on the home page: a wide/narrow pair, then a row of three.
SPANS = [7, 5, 4, 4, 4, 5, 7, 4, 4, 4]


def slugify(cat):
    return cat.lower()


def image_size(path):
    """(width, height) of a PNG, GIF, JPEG or WebP file, or None."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return int.from_bytes(data[6:8], "little"), int.from_bytes(data[8:10], "little")
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        kind = data[12:16]
        if kind == b"VP8X":
            return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
        if kind == b"VP8L":
            bits = int.from_bytes(data[21:25], "little")
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        if kind == b"VP8 ":
            return int.from_bytes(data[26:28], "little") & 0x3FFF, int.from_bytes(data[28:30], "little") & 0x3FFF
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                return int.from_bytes(data[i + 7:i + 9], "big"), int.from_bytes(data[i + 5:i + 7], "big")
            i += 2 + int.from_bytes(data[i + 2:i + 4], "big")
    return None


def media(src, cls="", eager=False):
    """<img>, or a looping <video> when an .mp4 sits next to the image (the image is its poster)."""
    size = image_size(OUT / src.lstrip("/"))
    dims = f' width="{size[0]}" height="{size[1]}"' if size else ""
    video = Path(src).with_suffix(".mp4")
    if (OUT / str(video).lstrip("/")).exists():
        return (
            f'<video class="{cls}" src="{video}" poster="{src}"{dims} '
            'autoplay muted loop playsinline preload="none"></video>'
        )
    loading = "eager" if eager else "lazy"
    return f'<img class="{cls}" src="{src}"{dims} alt="" loading="{loading}" decoding="async">'


def page(path, title, body, desc=None, image=None, active=""):
    desc = desc or site["hero"]["lede"]
    full_title = f"{title} | Wei Lee" if title else f"{site['title']} | Wei Lee"
    og = site["url"] + (image or "/media/snest/cover.webp")
    nav = "".join(
        f'<a href="{href}"{" aria-current=page" if key == active else ""}>{label}</a>'
        for key, href, label in [("work", "/#work", "Work"), ("about", "/about-me/", "About")]
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
{OLD_HOST_REDIRECT}{THEME_INIT}<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(full_title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{site['url']}{path}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(full_title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:image" content="{og}">
<meta property="og:url" content="{site['url']}{path}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0f0e0d">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="{asset("/assets/style.css")}">
<script src="{asset("/assets/main.js")}" defer></script>
<script src="{asset("/assets/ui.js")}" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="site-header__inner">
    <a class="brand" href="/" aria-label="Wei Lee, home">{MARK}<span>Wei Lee</span></a>
    <nav class="nav">{nav}</nav>
    <div class="head-end">{THEME_BTN}<a class="status round-btn" href="mailto:{site['email']}" aria-label="Email Wei" title="Email">{MAIL}</a></div>
  </div>
  <span class="progress" aria-hidden="true"></span>
</header>
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
"""
    dest = OUT / path.strip("/") / "index.html" if path.endswith("/") else OUT / path.lstrip("/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)


def footer():
    return f"""<footer class="site-footer" id="contact">
  <div class="wrap">
    <div class="cta">
      <h2 class="display cta-title reveal">Let's talk.</h2>
      <a class="cta-mail" href="mailto:{site['email']}">{site['email']}</a>
    </div>
    <div class="footer-bottom">
      <span>© 2026 Wei Lee 李建緯</span>
      <span>{escape(site['tagline'])}</span>
      <a href="#main">Back to top ↑</a>
    </div>
  </div>
</footer>"""


def card(p, i):
    cats = " ".join(slugify(c) for c in p["categories"])
    span = SPANS[i % len(SPANS)]
    return f"""<li class="card s{span}" data-cats="{cats}">
  <a href="/portfolio/{p['slug']}/">
    <div class="card-media">
      {media(p['cover'], eager=i < 2)}
      <div class="card-info">
        <h3>{escape(p['title'])}</h3>
        <p>{" / ".join(p['categories'])}</p>
      </div>
    </div>
  </a>
</li>"""


def section_head(title, extra=""):
    return f'<div class="section-head"><h2 class="display section-title reveal">{title}</h2>{extra}</div>'


def build_home():
    hero = site["hero"]
    counts = {c: sum(c in p["categories"] for p in projects) for c in site["categories"]}
    chips = f'<button class="chip" aria-pressed="true" data-filter="all">All <sup>{len(projects)}</sup></button>' + "".join(
        f'<button class="chip" aria-pressed="false" data-filter="{slugify(c)}">{c} <sup>{n}</sup></button>'
        for c, n in counts.items()
    )
    stats = "".join(
        f'<li><b><span data-count="{s["value"]}">{s["value"]}</span><sup>+</sup></b><span>{escape(s["label"])}</span></li>' for s in hero["stats"]
    )
    body = f"""
<section class="hero wrap">
  <div class="hero-copy">
    <h1 class="display hero-title" aria-label="{escape(" ".join(hero["title"]))}">{"".join(
        f'<span class="ln" aria-hidden="true"><span style="--i:{n}">'
        + "".join(f'<span class="ch">{escape(c)}</span>' for c in line)
        + ('<span class="ch stop">.</span>' if n == len(hero["title"]) - 1 else "")
        + "</span></span>"
        for n, line in enumerate(hero["title"])
    )}</h1>
    <div class="hero-row">
      <p class="hero-lede">{escape(hero['lede'])}</p>
    </div>
    <ul class="hero-stats">{stats}</ul>
  </div>
  <div class="hero-card">
    <img class="hero-portrait" src="/assets/img/wei-camera.webp" width="1170" height="1643" alt="Wei Lee holding a camera" fetchpriority="high">
    <span class="hero-noise" aria-hidden="true"></span>
    <svg class="sr-filter" width="0" height="0" aria-hidden="true">
      <filter id="warp" x="-5%" y="-5%" width="110%" height="110%">
        <feTurbulence id="warp-noise" type="fractalNoise" baseFrequency="0.008 0.02" numOctaves="2" seed="3" result="n"/>
        <feDisplacementMap id="warp-map" in="SourceGraphic" in2="n" scale="0" xChannelSelector="R" yChannelSelector="G"/>
      </filter>
    </svg>
    <svg class="hero-badge" viewBox="0 0 120 120" aria-hidden="true">
      <defs><path id="badge-ring" d="M60 60m-44 0a44 44 0 1 1 88 0a44 44 0 1 1-88 0"/></defs>
      <text textLength="274" lengthAdjust="spacing"><textPath href="#badge-ring" textLength="274" lengthAdjust="spacing">VISUAL DESIGNER • DESIGN MANAGER • </textPath></text>
    </svg>
    <a class="hero-badge-mark" href="https://app.pagescms.org/taiwankiss/wei-portfolio/main/collection/projects" target="_blank" rel="noopener" aria-label="後台登入 / Admin"><img src="/assets/img/mark.svg" width="36" height="36" alt=""></a>
  </div>
</section>
<section class="work wrap" id="work">
  {section_head("Selected Work", f'<div class="chips" role="group" aria-label="Filter by category">{chips}</div>')}
  <ul class="grid">{"".join(card(p, i) for i, p in enumerate(projects))}</ul>
</section>"""
    page("/", "", body, active="work")


def build_project(i, p):
    nxt = projects[(i + 1) % len(projects)]
    prev = projects[i - 1]
    link = ""
    if (p.get("link") or {}).get("url"):
        link = f'<a class="project-link" href="{escape(p["link"]["url"])}" target="_blank" rel="noopener">{escape(p["link"]["label"])} <span aria-hidden="true">↗</span></a>'
    tags = "".join(f'<li><a href="/?filter={slugify(c)}#work">{c}</a></li>' for c in p["categories"])
    en = f'<div class="desc-col" lang="en"><h2 class="label">Overview</h2>{p["en"]}</div>' if p["en"] else ""
    gallery = "".join(
        f'<figure class="shot" data-index="{n}">{media(m, eager=n == 0)}</figure>' for n, m in enumerate(p["gallery"])
    )
    body = f"""
<article class="project">
  <header class="project-head wrap">
    <div class="project-top">
      <a class="back" href="/#work">← All work</a>
      <ul class="project-tags" aria-label="Discipline">{tags}</ul>
    </div>
    <h1 class="project-title">{escape(p['title'])}</h1>
    <div class="project-rule">{link}</div>
  </header>
  <section class="desc wrap">
    <div class="desc-col"><h2 class="label">專案介紹</h2>{p['zh']}</div>
    {en}
  </section>
  <section class="gallery wrap">{gallery}</section>
  <nav class="pager wrap" aria-label="More projects">
    <a href="/portfolio/{prev['slug']}/" class="pager-prev"><span class="label">← Previous</span><b>{escape(prev['title'])}</b></a>
    <a href="/portfolio/{nxt['slug']}/" class="pager-next"><span class="label">Next project →</span><b>{escape(nxt['title'])}</b>
      <div class="pager-thumb">{media(nxt['cover'])}</div></a>
  </nav>
</article>
<div class="lightbox" hidden>
  <button class="lb-close" aria-label="Close">×</button>
  <button class="lb-prev" aria-label="Previous image">←</button>
  <div class="lb-stage"></div>
  <button class="lb-next" aria-label="Next image">→</button>
  <p class="lb-count"></p>
</div>"""
    # first paragraph; the CMS saves paragraphs without newlines between them
    desc = unescape(re.sub(r"<[^>]+>", "", re.sub(r"</p>", "\n", p["zh"]))).strip().split("\n")[0][:150]
    page(f"/portfolio/{p['slug']}/", p["title"], body, desc=desc, image=p["cover"])


def build_about():
    """Copy the résumé site into /about-me/, recoloured to the portfolio accent."""
    if not RESUME.exists():
        print(f"{RESUME} not found; keeping the existing about-me/ copy")
        return
    dest = OUT / "about-me"
    shutil.rmtree(dest, ignore_errors=True)
    (dest / "assets/logos").mkdir(parents=True)
    for name in ["avatar3.jpg", "avatar-loop.mp4"]:
        shutil.copy(RESUME / "assets" / name, dest / "assets" / name)
    for logo in (RESUME / "assets/logos").iterdir():
        shutil.copy(logo, dest / "assets/logos" / logo.name)
    css = (RESUME / "assets/style.css").read_text()
    css = css.replace("#FF4D1A", ACCENT).replace("255, 77, 26", "244, 167, 17")
    css += (
        "\n/* portfolio header inside the résumé chrome */\n"
        ".chrome__inner.pf { font: 500 14px/1 'Inter Tight', 'Noto Sans TC', sans-serif; letter-spacing: 0; text-transform: none; padding-top: 14px; padding-bottom: 14px; display: grid; grid-template-columns: 1fr auto 1fr; }\n"
        ".pf-brand { display: flex; align-items: center; gap: 10px; color: inherit; text-decoration: none; font-weight: 700; font-size: 17px; letter-spacing: -.02em; }\n"
        ".pf-brand img { width: 34px; height: 34px; transition: transform .5s; }\n"
        ".pf-brand:hover img { transform: rotate(-12deg) scale(1.06); }\n"
        ".pf-nav { display: flex; gap: 2px; padding: 3px; border-radius: 999px; background: color-mix(in srgb, currentColor 9%, transparent); font-size: 11.2px; }\n"
        ".pf-nav a { color: inherit; text-decoration: none; padding: 8px 13px; border-radius: 999px; transition: background .2s, color .2s; }\n"
        ".pf-nav a:hover { background: var(--acc); }\n"
        ".pf-nav a[aria-current] { background: var(--ink); color: var(--paper); }\n"
        "body.is-dark .pf-nav a[aria-current] { background: var(--paper); color: var(--ink); }\n"
        ".pf-status { justify-self: end; display: flex; align-items: center; font-size: 13px; color: inherit; text-decoration: none; }\n"
        "@media (max-width: 1100px) { .chrome__inner.pf { grid-template-columns: auto 1fr; } .pf-nav { justify-self: end; } }\n"
        "@media (max-width: 720px) { .pf-brand span { display: none; } }\n"
    )
    css += "\n" + (ROOT / "about-taste.css").read_text()
    (dest / "assets/style.css").write_text(css)

    js = (RESUME / "assets/main.js").read_text()
    # background crosshair marks and the scroll listener (header colour, section index) are gone;
    # the progress bar is a CSS scroll timeline now
    js = re.sub(r"  // crosshair marks.*?addEventListener\('resize', buildMarks\);\n", "", js, flags=re.S)
    js = re.sub(r"  // chrome follows the section.*?  onScroll\(\);\n", "", js, flags=re.S)
    (dest / "assets/main.js").write_text(js)

    html = (RESUME / "index.html").read_text()
    html = re.sub(r'<link rel="(?:icon|apple-touch-icon|manifest)"[^>]*>\n', "", html)
    html = html.replace("<head>\n", "<head>\n" + OLD_HOST_REDIRECT, 1)
    html = html.replace(
        "<title>Resume</title>",
        f'<title>About | Wei Lee</title>\n<link rel="canonical" href="{site["url"]}/about-me/">\n'
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
        '<link rel="icon" href="/favicon.png" type="image/png" sizes="32x32">\n'
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
    )
    html = html.replace('<meta name="apple-mobile-web-app-title" content="Resume">\n', "")
    html = re.sub(
        r'<div class="chrome__inner">.*?</div>\n',
        '<div class="chrome__inner pf">'
        '<a class="pf-brand" href="/" aria-label="Wei Lee, home"><img src="/assets/img/mark.svg" alt=""><span>Wei Lee</span></a>'
        '<nav class="pf-nav"><a href="/#work">Work</a><a href="/about-me/" aria-current="page">About</a></nav>'
        f'<a class="pf-status" href="mailto:{site["email"]}">Get in touch</a>'
        "</div>\n",
        html,
        count=1,
        flags=re.S,
    )
    # second profile paragraph as worded on the printed résumé
    html = re.sub(
        r'<p class="reveal">近期也積極投入.*?</p>',
        '<p class="reveal">工作之餘，是一名單車公路騎行與馬拉松愛好者，期許能將這份自律與對生命的細膩體察，'
        '轉化為持續輸出卓越設計的動能。近期也積極投入 AI 輔助設計流程（Vibe Coding），'
        '透過 AI 工具快速將設計概念原型化、迭代網頁與互動介面，加速從構想到落地的產出效率。</p>',
        html,
        count=1,
        flags=re.S,
    )

    # --- taste pass: one theme, sans type, no decorative grid/dots/numbers, no em-dashes ---
    html = html.replace(OLD_HOST_REDIRECT, OLD_HOST_REDIRECT + THEME_INIT, 1)
    html = html.replace("</head>", f'<script src="{asset("/assets/ui.js")}" defer></script>\n</head>', 1)
    html = html.replace('<meta name="theme-color" content="#EFEBE3">', '<meta name="theme-color" content="#0f0e0d">')
    html = re.sub(r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*" rel="stylesheet">',
                  '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400..800&family=Geist+Mono:wght@400;500'
                  '&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">', html, count=1)
    html = re.sub(r'<div class="bg" aria-hidden="true">.*?<div class="bg__marks"></div>\n  </div>\n</div>\n', "", html, count=1, flags=re.S)
    html = html.replace(f'<a class="pf-status" href="mailto:{site["email"]}">Get in touch</a>',
                        f'<div class="pf-end">{THEME_BTN}<a class="pf-status round-btn" href="mailto:{site["email"]}" aria-label="Email Wei" title="Email">{MAIL}</a></div>')
    html = re.sub(r'\s*<span class="avatar__live"[^>]*></span>', "", html)
    html = re.sub(r'\s*<span class="job__ghost"[^>]*>\d+</span>', "", html)
    html = re.sub(r'\s*<p class="hero__meta[^"]*">.*?</p>', "", html)
    html = re.sub(r'\s*<footer class="foot mono">.*?</footer>', "", html, flags=re.S)
    # numbered labels: plain headings where the section has no headline of its own, gone elsewhere
    def kick(m):
        cls, num, zh, en = m.group(1), m.group(2), m.group(3).strip(), m.group(4).strip()
        if num in ("03", "04", "05"):
            extra = " wrap" if "wrap" in cls else ""
            return f'<h2 class="sec-h{extra} reveal">{zh}<span>{en}</span></h2>'
        return ""
    html = re.sub(r'\s*<p class="(kick[^"]*)"><b>(\d+)</b> — ([^/<]+)/([^<]+)</p>',
                  lambda m: ("\n      " + kick(m)) if kick(m) else "", html)
    html = html.replace('<i class="c c--dot"', '<span class="c c--dot"').replace('.</i></span></span>\n      </h1>', '.</span></span></span>\n      </h1>')
    html = html.replace('<span class="ln"><span class="up"><i>clear.</i></span></span>', '<span class="ln"><span class="up"><span class="acc">clear.</span></span></span>')
    html = re.sub(r'<a class="otw mono reveal" href="[^"]*"><span class="dot dot--blink"></span>Open to work</a>',
                  f'<a class="otw reveal" href="mailto:{site["email"]}">Get in touch</a>', html)
    html = html.replace("Crowdfunding · Biotech · Smart parking", "Crowdfunding, biotech, smart parking")
    html = html.replace("李建緯 Wei Lee — 視覺設計師", "李建緯 Wei Lee，視覺設計師")
    html = html.replace("</span>Wei Lee — Visual Designer", "</span>Wei Lee, Visual Designer")
    html = html.replace("—", "-").replace("–", "-")
    stamp = lambda name: hashlib.md5((dest / "assets" / name).read_bytes()).hexdigest()[:8]
    html = re.sub(r'\./assets/style\.css\?v=\w+', f'./assets/style.css?v={stamp("style.css")}', html)
    html = re.sub(r'\./assets/main\.js\?v=\w+', f'./assets/main.js?v={stamp("main.js")}', html)
    (dest / "index.html").write_text(html)


def build_misc():
    page("/404.html", "Not found", """
<section class="hero-404 wrap">
  <h1 class="display hero-title">lost.</h1>
  <p class="hero-lede">This page doesn't exist anymore.</p>
  <p><a class="btn" href="/">Back to work →</a></p>
</section>""")
    urls = ["/", "/about-me/"] + [f"/portfolio/{p['slug']}/" for p in projects]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{site['url']}{u}</loc></url>\n" for u in urls)
        + "</urlset>\n"
    )
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site['url']}/sitemap.xml\n")


if __name__ == "__main__":
    build_home()
    for i, p in enumerate(projects):
        build_project(i, p)
    build_about()
    build_misc()
    print(f"Built {len(projects)} projects into {os.path.relpath(OUT)}")
