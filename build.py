#!/usr/bin/env python3
"""Generate the static site in public/ from content/*.json.

Usage: python3 build.py
No dependencies. Media files live in public/media/<slug>/ and are referenced
from content/projects.json.
"""
import json
import os
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "public"
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


def media(m, cls="", eager=False):
    """<img> or looping <video> for a media entry."""
    if m.get("poster"):
        return (
            f'<video class="{cls}" src="{m["src"]}" poster="{m["poster"]}" width="{m["w"]}" '
            f'height="{m["h"]}" autoplay muted loop playsinline preload="none"></video>'
        )
    loading = "eager" if eager else "lazy"
    return (
        f'<img class="{cls}" src="{m["src"]}" width="{m["w"]}" height="{m["h"]}" '
        f'alt="" loading="{loading}" decoding="async">'
    )


def page(path, title, body, desc=None, image=None, active=""):
    desc = desc or site["hero"]["lede"]
    full_title = f"{title} — Wei Lee" if title else "Wei Lee — Visual Designer"
    og = site["url"] + (image or "/media/snest/cover.webp")
    nav = "".join(
        f'<a href="{href}"{" aria-current=page" if key == active else ""}>{label}</a>'
        for key, href, label in [("work", "/#work", "Work"), ("about", "/about-me/", "About"), ("contact", "#contact", "Contact")]
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
<meta name="theme-color" content="#f4f3ee">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="/assets/style.css">
<script src="/assets/main.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <a class="brand" href="/" aria-label="Wei Lee, home">{MARK}<span>Wei Lee</span></a>
  <nav class="nav">{nav}</nav>
  <p class="status"><i></i>{escape(site['location'])} · Open to work</p>
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
      <h2 class="display cta-title">let's talk.</h2>
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


def section_head(num, title, extra=""):
    return f'<div class="section-head"><span class="label">({num:02d})</span><h2 class="display section-title">{title}</h2>{extra}</div>'


def build_home():
    hero = site["hero"]
    counts = {c: sum(c in p["categories"] for p in projects) for c in site["categories"]}
    chips = f'<button class="chip" aria-pressed="true" data-filter="all">All <sup>{len(projects)}</sup></button>' + "".join(
        f'<button class="chip" aria-pressed="false" data-filter="{slugify(c)}">{c} <sup>{n}</sup></button>'
        for c, n in counts.items()
    )
    stats = "".join(
        f'<li><b><sup>+</sup>{s["value"]}</b><span>{escape(s["label"])}</span></li>' for s in hero["stats"]
    )
    body = f"""
<section class="hero wrap">
  <div class="hero-copy">
    <h1 class="display hero-title">{"<br>".join(hero["title"])}</h1>
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
  {section_head(1, "selected work", f'<div class="chips" role="group" aria-label="Filter by category">{chips}</div>')}
  <ul class="grid">{"".join(card(p, i) for i, p in enumerate(projects))}</ul>
</section>"""
    page("/", "", body, active="work")


def build_project(i, p):
    nxt = projects[(i + 1) % len(projects)]
    prev = projects[i - 1]
    link = ""
    if p.get("link"):
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
    page(f"/portfolio/{p['slug']}/", p["title"], body, desc=desc, image=p["cover"].get("poster", p["cover"]["src"]))


def build_about():
    exp = "".join(
        f"""<li class="job">
  <div class="job-when">{e['period']}</div>
  <div><h3>{escape(e['role'])}</h3><p class="job-co">{escape(e['company'])}</p>
  <ul>{"".join(f"<li>{escape(x)}</li>" for x in e['points'])}</ul></div>
</li>"""
        for e in site["experience"]
    )
    edu = "".join(
        f'<li><b>{escape(e["degree"])}</b><span>{escape(e["school"])} · {e["period"]}</span></li>' for e in site["education"]
    )
    skills = "".join(f"<li>{escape(s)}</li>" for s in site["skills"])
    cf = "".join(f"<li>{escape(s)}</li>" for s in site["crowdfunding"])
    traits = "".join(f"<li>{escape(s)}</li>" for s in site["traits"])
    nums = "".join(
        f'<li><b>{n["value"]}<sup>{n["suffix"]}</sup></b><span>{escape(n["zh"])}</span><small>{escape(n["en"])}</small></li>'
        for n in site["numbers"]
    )
    statement = "<br>".join(escape(x) for x in site["statement"]["zh"])
    off = "<br>".join(escape(x) for x in site["off_clock"]["zh"])
    body = f"""
<section class="about wrap">
  <div class="about-intro">
    <h1 class="display about-title">about<br>me.</h1>
    <div class="about-card">
      <span class="signature" aria-hidden="true">Wei Lee</span>
      <img src="/assets/img/wei-cutout.webp" width="900" height="900" alt="Portrait of Wei Lee">
    </div>
  </div>
  <div class="about-body">
    <aside class="about-side">
      <p class="label">Contact</p>
      <dl class="contact-list">
        <dt>Email</dt><dd><a href="mailto:{site['email']}">{site['email']}</a></dd>
        <dt>Phone</dt><dd><a href="tel:{site['phone'].replace(' ', '')}">{site['phone']}</a></dd>
        <dt>Based in</dt><dd>{escape(site['location'])}</dd>
      </dl>
    </aside>
    <div class="about-main">
      <h2 class="statement">{statement}</h2>
      <p class="statement-en">{escape(site['statement']['en'])}</p>
      <ul class="nums">{nums}</ul>
      {"".join(f"<p class='lead'>{escape(x)}</p>" for x in site['about'])}
      <ul class="traits">{traits}</ul>
      <h2 class="label section-label">Experience</h2>
      <ol class="jobs">{exp}</ol>
      <div class="about-cols">
        <div>
          <h2 class="label section-label">Skills</h2><ul class="pills">{skills}</ul>
          <p class="ai-note"><b>+ AI Workflow</b>{escape(site['ai_note'])}</p>
        </div>
        <div><h2 class="label section-label">Education</h2><ul class="edu">{edu}</ul></div>
      </div>
      <h2 class="label section-label">Crowdfunding campaigns</h2>
      <ul class="pills pills-outline">{cf}</ul>
      <h2 class="label section-label">Off the clock</h2>
      <p class="off-zh">{off}</p>
      <p class="statement-en">{escape(site['off_clock']['en'])}</p>
    </div>
  </div>
</section>"""
    page("/about-me/", "About", body, active="about")


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
