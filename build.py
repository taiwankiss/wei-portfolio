#!/usr/bin/env python3
"""Generate the static site in public/ from content/*.json.

Usage: python3 build.py
No dependencies. Media files live in public/media/<slug>/ and are referenced
from content/projects.json.
"""
import json
import os
import re
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "public"
# The About page is the résumé site, copied in at build time when that project is present.
RESUME = ROOT.parent / "Resume"
ACCENT = "#F4A711"
site = json.loads((ROOT / "content/site.json").read_text())
projects = json.loads((ROOT / "content/projects.json").read_text())

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400..900'
    '&family=Mrs+Saint+Delafield&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">'
)
MARK = '<img src="/assets/img/mark.svg" width="36" height="36" alt="">'
ARROW = (
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">'
    '<path d="M7 17 17 7M9 7h8v8" fill="none" stroke="currentColor" stroke-width="2.2" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)
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
    full_title = f"{title} — Wei Lee" if title else "Wei Lee — Visual Designer"
    og = site["url"] + (image or "/media/snest/cover.webp")
    nav = "".join(
        f'<a href="{href}"{" aria-current=page" if key == active else ""}>{label}</a>'
        for key, href, label in [("work", "/#work", "Work"), ("about", "/about-me/", "About")]
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
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
<meta name="theme-color" content="#efebe3">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="/assets/style.css">
<script src="/assets/main.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="glow" aria-hidden="true"></div>
<div class="cursor" aria-hidden="true">View</div>
<header class="site-header">
  <a class="brand" href="/" aria-label="Wei Lee, home">{MARK}<span>Wei Lee</span></a>
  <nav class="nav">{nav}</nav>
  <p class="status"><i></i>{escape(site['location'])} · Open to work</p>
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
      <p class="label">Have a project in mind?</p>
      <h2 class="display cta-title reveal">let's talk.</h2>
      <a class="cta-mail" href="mailto:{site['email']}">{site['email']}</a>
      <a class="notch-btn cta-btn" href="mailto:{site['email']}" aria-label="Send an email">{ARROW}</a>
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
    <div class="card-media">{media(p['cover'], eager=i < 2)}</div>
    <div class="card-meta">
      <div><h3>{escape(p['title'])}</h3><p>{" · ".join(p['categories'])}</p></div>
      <span class="card-arrow">{ARROW}</span>
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
        f'<li><b><sup>+</sup><span data-count="{s["value"]}">{s["value"]}</span></b><span>{escape(s["label"])}</span></li>' for s in hero["stats"]
    )
    body = f"""
<section class="hero wrap">
  <div class="hero-copy">
    <h1 class="display hero-title">{"".join(f'<span class="ln"><span style="--i:{n}">{escape(x)}</span></span>' for n, x in enumerate(hero["title"]))}</h1>
    <div class="hero-row">
      <div class="circles">
        <a href="mailto:{site['email']}">mail</a>
        <a href="/about-me/">cv</a>
        <a href="#work">work</a>
      </div>
      <p class="hero-lede">{escape(hero['lede'])}</p>
    </div>
    <ul class="hero-stats">{stats}</ul>
  </div>
  <div class="hero-card">
    <img class="hero-portrait" src="/assets/img/wei-camera.webp" width="1200" height="1149" alt="Wei Lee holding a camera" fetchpriority="high">
  </div>
</section>
<section class="work wrap" id="work">
  {section_head("selected work", f'<div class="chips" role="group" aria-label="Filter by category">{chips}</div>')}
  <ul class="grid">{"".join(card(p, i) for i, p in enumerate(projects))}</ul>
</section>"""
    page("/", "", body, active="work")


def build_project(i, p):
    nxt = projects[(i + 1) % len(projects)]
    prev = projects[i - 1]
    link = ""
    if (p.get("link") or {}).get("url"):
        link = f'<div><dt>Live</dt><dd><a href="{escape(p["link"]["url"])}" target="_blank" rel="noopener">{escape(p["link"]["label"])} ↗</a></dd></div>'
    tags = ", ".join(f'<a href="/?filter={slugify(c)}#work">{c}</a>' for c in p["categories"])
    en = f'<div class="desc-col" lang="en"><h2 class="label">Overview</h2>{p["en"]}</div>' if p["en"] else ""
    gallery = "".join(
        f'<figure class="shot" data-index="{n}">{media(m, eager=n == 0)}</figure>' for n, m in enumerate(p["gallery"])
    )
    body = f"""
<article class="project">
  <header class="project-head wrap">
    <a class="back" href="/#work">← All work</a>
    <h1 class="project-title">{escape(p['title'])}</h1>
    <dl class="project-meta">
      <div><dt>Discipline</dt><dd>{tags}</dd></div>
      <div><dt>Project</dt><dd>{i + 1:02d} / {len(projects):02d}</dd></div>
      {link}
    </dl>
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
    desc = re.sub(r"<[^>]+>", "", p["zh"]).strip().split("\n")[0][:150]
    page(f"/portfolio/{p['slug']}/", p["title"], body, desc=desc, image=p["cover"])


def build_about():
    """Copy the résumé site into /about-me/, recoloured to the portfolio accent."""
    if not RESUME.exists():
        print(f"{RESUME} not found; keeping the existing about-me/ copy")
        return
    dest = OUT / "about-me"
    shutil.rmtree(dest, ignore_errors=True)
    (dest / "assets/logos").mkdir(parents=True)
    for name in ["main.js", "avatar3.jpg", "avatar-loop.mp4"]:
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
        ".pf-nav { display: flex; gap: 2px; padding: 4px; border-radius: 999px; background: color-mix(in srgb, currentColor 9%, transparent); }\n"
        ".pf-nav a { color: inherit; text-decoration: none; padding: 10px 16px; border-radius: 999px; }\n"
        ".pf-nav a:hover { background: color-mix(in srgb, currentColor 10%, transparent); }\n"
        ".pf-nav a[aria-current] { background: var(--ink); color: var(--paper); }\n"
        "body.is-dark .pf-nav a[aria-current] { background: var(--paper); color: var(--ink); }\n"
        ".pf-status { justify-self: end; display: flex; align-items: center; gap: 8px; font-size: 13px; color: inherit; text-decoration: none; }\n"
        "@media (max-width: 1100px) { .chrome__inner.pf { grid-template-columns: auto 1fr; } .pf-nav { justify-self: end; } .pf-status { display: none; } }\n"
        "@media (max-width: 720px) { .pf-brand span { display: none; } .pf-nav a { padding: 10px 12px; } }\n"
    )
    (dest / "assets/style.css").write_text(css)

    html = (RESUME / "index.html").read_text()
    html = re.sub(r'<link rel="(?:icon|apple-touch-icon|manifest)"[^>]*>\n', "", html)
    html = html.replace(
        "<title>Resume</title>",
        f'<title>About — Wei Lee</title>\n<link rel="canonical" href="{site["url"]}/about-me/">\n'
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
        f'<a class="pf-status" href="mailto:{site["email"]}"><span class="dot"></span>Open to work</a>'
        "</div>\n",
        html,
        count=1,
        flags=re.S,
    )
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
