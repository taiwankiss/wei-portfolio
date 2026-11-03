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
    '<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800'
    '&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">'
)


def slugify(cat):
    return cat.lower()


def media(m, cls="", sizes="", eager=False):
    """<img> or looping <video> for a media entry."""
    loading = "eager" if eager else "lazy"
    if m.get("poster"):
        return (
            f'<video class="{cls}" src="{m["src"]}" poster="{m["poster"]}" width="{m["w"]}" '
            f'height="{m["h"]}" autoplay muted loop playsinline preload="none"></video>'
        )
    return (
        f'<img class="{cls}" src="{m["src"]}" width="{m["w"]}" height="{m["h"]}" '
        f'alt="" loading="{loading}" decoding="async">'
    )


def page(path, title, body, desc=None, image=None, active=""):
    desc = desc or site["intro"]
    full_title = f"{title} — {site['name']}" if title else f"{site['name']} | {site['title']}"
    og = site["url"] + (image or "/media/snest/cover.webp")
    nav = "".join(
        f'<a href="{href}"{" aria-current=page" if key == active else ""}>{label}</a>'
        for key, href, label in [("work", "/#work", "Work"), ("about", "/about-me/", "About"), ("contact", "#contact", "Contact")]
    )
    html = f"""<!doctype html>
<html lang="zh-Hant">
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
<meta name="theme-color" content="#f5f4ef">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="/assets/style.css">
<script src="/assets/main.js" defer></script>
</head>
<body>
<a class="skip" href="#main">跳到內容</a>
<header class="site-header">
  <a class="brand" href="/" aria-label="{escape(site['name'])} 首頁">
    <img src="/assets/img/logo.png" width="36" height="36" alt="">
    <span><b>WEI</b> 李建緯</span>
  </a>
  <nav class="nav">{nav}</nav>
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
    <p class="eyebrow">Contact</p>
    <h2 class="footer-cta">有專案想聊聊？<br><span>Let's make something good.</span></h2>
    <a class="footer-mail" href="mailto:{site['email']}">{site['email']} <span aria-hidden="true">→</span></a>
    <div class="footer-bottom">
      <span>© 2026 {escape(site['name'])}</span>
      <span>{escape(site['tagline'])}</span>
    </div>
  </div>
</footer>"""


def card(p, i):
    cats = " ".join(slugify(c) for c in p["categories"])
    return f"""<li class="card" data-cats="{cats}" style="--i:{i}">
  <a href="/portfolio/{p['slug']}/">
    <div class="card-media">{media(p['cover'], eager=i < 3)}</div>
    <div class="card-meta">
      <h3>{escape(p['title'])}</h3>
      <p>{" · ".join(p['categories'])}</p>
    </div>
  </a>
</li>"""


def build_home():
    counts = {c: sum(c in p["categories"] for p in projects) for c in site["categories"]}
    chips = f'<button class="chip" aria-pressed="true" data-filter="all">All <sup>{len(projects)}</sup></button>' + "".join(
        f'<button class="chip" aria-pressed="false" data-filter="{slugify(c)}">{c} <sup>{n}</sup></button>'
        for c, n in counts.items()
    )
    strip = "".join(
        f'<a href="/portfolio/{p["slug"]}/" tabindex="-1">{media(p["cover"])}</a>'
        for p in projects[:14]
    )
    body = f"""
<section class="hero wrap">
  <p class="eyebrow">{escape(site['role'])}</p>
  <h1 class="hero-title">把複雜的策略，<br>轉化為<mark>會說話</mark>的視覺。</h1>
  <div class="hero-foot">
    <p class="hero-intro">{escape(site['intro'])}</p>
    <ul class="stats">
      <li><b>10+</b><span>年經驗</span></li>
      <li><b>{len(projects)}</b><span>精選作品</span></li>
      <li><b>8</b><span>募資專案</span></li>
    </ul>
  </div>
</section>
<div class="strip" aria-hidden="true"><div class="strip-track">{strip}{strip}</div></div>
<section class="work wrap" id="work">
  <div class="work-head">
    <h2>Selected Work</h2>
    <div class="chips" role="group" aria-label="依類別篩選">{chips}</div>
  </div>
  <ul class="grid">{"".join(card(p, i) for i, p in enumerate(projects))}</ul>
</section>"""
    page("/", "", body, active="work")


def build_project(i, p):
    nxt = projects[(i + 1) % len(projects)]
    prev = projects[i - 1]
    link = ""
    if p.get("link"):
        link = f'<a class="btn" href="{escape(p["link"]["url"])}" target="_blank" rel="noopener">{escape(p["link"]["label"])} <span aria-hidden="true">↗</span></a>'
    en = f'<div class="desc-col" lang="en"><h2>Project Overview</h2>{p["en"]}</div>' if p["en"] else ""
    gallery = "".join(
        f'<figure class="shot" data-index="{n}">{media(m, eager=n == 0)}</figure>' for n, m in enumerate(p["gallery"])
    )
    tags = "".join(f'<a class="tag" href="/?filter={slugify(c)}#work">{c}</a>' for c in p["categories"])
    body = f"""
<article class="project">
  <header class="project-head wrap">
    <a class="back" href="/#work">← All work</a>
    <h1>{escape(p['title'])}</h1>
    <div class="project-meta">{tags}{link}</div>
  </header>
  <section class="desc wrap">
    <div class="desc-col"><h2>專案介紹</h2>{p['zh']}</div>
    {en}
  </section>
  <section class="gallery wrap">{gallery}</section>
  <nav class="pager wrap" aria-label="其他作品">
    <a href="/portfolio/{prev['slug']}/" class="pager-prev"><span>Previous</span><b>{escape(prev['title'])}</b></a>
    <a href="/portfolio/{nxt['slug']}/" class="pager-next"><span>Next project</span><b>{escape(nxt['title'])}</b>
      <div class="pager-thumb">{media(nxt['cover'])}</div></a>
  </nav>
</article>
<div class="lightbox" hidden>
  <button class="lb-close" aria-label="關閉">×</button>
  <button class="lb-prev" aria-label="上一張">←</button>
  <div class="lb-stage"></div>
  <button class="lb-next" aria-label="下一張">→</button>
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
    body = f"""
<section class="about wrap">
  <aside class="about-side">
    <img class="portrait" src="/assets/img/wei.webp" width="188" height="188" alt="李建緯">
    <img class="wordmark" src="/assets/img/wordmark.png" width="382" height="92" alt="WEI 李建緯">
    <p class="eyebrow">{escape(site['role'])}</p>
    <dl class="contact-list">
      <dt>Email</dt><dd><a href="mailto:{site['email']}">{site['email']}</a></dd>
      <dt>Phone</dt><dd><a href="tel:{site['phone'].replace(' ', '')}">{site['phone']}</a></dd>
    </dl>
  </aside>
  <div class="about-main">
    <h1 class="about-title">好好感受、<br>用心生活。</h1>
    {"".join(f"<p class='lead'>{escape(x)}</p>" for x in site['about'])}
    <h2 class="section-label">Experience</h2>
    <ol class="jobs">{exp}</ol>
    <div class="about-cols">
      <div><h2 class="section-label">Skills</h2><ul class="pills">{skills}</ul></div>
      <div><h2 class="section-label">Education</h2><ul class="edu">{edu}</ul></div>
    </div>
    <h2 class="section-label">參與募資專案</h2>
    <ul class="pills pills-outline">{cf}</ul>
  </div>
</section>"""
    page("/about-me/", "About", body, active="about")


def build_misc():
    page("/404.html", "找不到頁面", """
<section class="hero wrap notfound">
  <p class="eyebrow">404</p>
  <h1 class="hero-title">這一頁<mark>不見了</mark>。</h1>
  <p><a class="btn" href="/">回到作品集 →</a></p>
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
