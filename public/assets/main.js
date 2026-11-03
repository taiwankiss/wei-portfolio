document.documentElement.classList.add("js");

const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;

// Header border, reading progress and a slow drift on the hero photo
const header = document.querySelector(".site-header");
const portrait = document.querySelector(".hero-portrait");
let ticking = false;
const onScroll = () => {
  const max = document.documentElement.scrollHeight - innerHeight;
  header.style.setProperty("--p", max > 0 ? Math.min(scrollY / max, 1) : 0);
  if (portrait && !calm && scrollY < innerHeight * 1.2) portrait.style.setProperty("--py", `${scrollY * 0.08}px`);
  ticking = false;
};
addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
onScroll();

// Hero numbers count up once
document.querySelectorAll("[data-count]").forEach((el) => {
  const end = Number(el.dataset.count);
  if (calm || !end) return;
  const start = performance.now() + 600;
  const step = (now) => {
    const t = Math.min(Math.max((now - start) / 1400, 0), 1);
    el.textContent = Math.round(end * (1 - (1 - t) ** 3));
    if (t < 1) requestAnimationFrame(step);
  };
  el.textContent = "0";
  requestAnimationFrame(step);
});

// Headings slide up as they enter the viewport
const headingObserver = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) { e.target.classList.add("in"); headingObserver.unobserve(e.target); }
}, { rootMargin: "0px 0px -10% 0px" });
document.querySelectorAll(".reveal").forEach((el) => headingObserver.observe(el));

// "View" bubble that follows the pointer over project cards
const cursor = document.querySelector(".cursor");
if (cursor && !calm && matchMedia("(hover: hover) and (pointer: fine)").matches) {
  addEventListener("pointermove", (e) => {
    cursor.style.setProperty("--cx", `${e.clientX}px`);
    cursor.style.setProperty("--cy", `${e.clientY}px`);
    cursor.classList.toggle("on", !!e.target.closest?.(".card-media, .pager-next"));
  }, { passive: true });
  document.addEventListener("pointerleave", () => cursor.classList.remove("on"));
}

// Looping videos only play while on screen
const videoObserver = new IntersectionObserver((entries) => {
  for (const e of entries) {
    if (e.isIntersecting) e.target.play().catch(() => {});
    else e.target.pause();
  }
}, { rootMargin: "200px" });
document.querySelectorAll("video[loop]").forEach((v) => videoObserver.observe(v));

// Cards fade in as they enter the viewport
const cards = [...document.querySelectorAll(".card")];
const revealObserver = new IntersectionObserver((entries) => {
  let n = 0;
  for (const e of entries) {
    if (!e.isIntersecting) continue;
    e.target.style.setProperty("--d", n++);
    e.target.classList.add("in");
    revealObserver.unobserve(e.target);
  }
}, { rootMargin: "0px 0px -8% 0px" });
cards.forEach((c) => revealObserver.observe(c));

// Category filter, kept in ?filter= so links and back button work
// Cards that stay slide to their new spot (FLIP), leaving ones fade out, new ones fade up.
const chips = [...document.querySelectorAll(".chip")];
const grid = document.querySelector(".grid");
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)");
const EASE = "cubic-bezier(.2, .7, .2, 1)";
let filterRun = 0;

const pageRect = (el) => {
  const r = el.getBoundingClientRect();
  return { left: r.left + scrollX, top: r.top + scrollY, width: r.width };
};

function setFilterState(name, matches) {
  grid.classList.toggle("filtered", name !== "all");
  for (const card of cards) {
    card.hidden = !matches(card);
    if (!card.hidden) card.classList.add("in");
  }
}

async function applyFilter(name, push, animate) {
  if (!chips.some((c) => c.dataset.filter === name)) name = "all";
  chips.forEach((c) => c.setAttribute("aria-pressed", c.dataset.filter === name));
  const matches = (card) => name === "all" || card.dataset.cats.split(" ").includes(name);
  const run = ++filterRun;

  if (push) {
    const url = new URL(location);
    name === "all" ? url.searchParams.delete("filter") : url.searchParams.set("filter", name);
    history.replaceState(null, "", url);
  }
  if (!animate || reduceMotion.matches) return setFilterState(name, matches);

  cards.forEach((c) => c.getAnimations().forEach((a) => a.cancel()));
  const visible = cards.filter((c) => !c.hidden);
  const leaving = visible.filter((c) => !matches(c));
  if (leaving.length) {
    await Promise.all(leaving.map((c) =>
      c.animate(
        [{ opacity: 1, transform: "none" }, { opacity: 0, transform: "scale(.94)" }],
        { duration: 220, easing: "ease-in", fill: "forwards" },
      ).finished.catch(() => {}),
    ));
    if (run !== filterRun) return;
  }

  const first = new Map(visible.filter(matches).map((c) => [c, pageRect(c)]));
  setFilterState(name, matches);
  leaving.forEach((c) => c.getAnimations().forEach((a) => a.cancel()));

  let entering = 0;
  for (const card of cards) {
    if (card.hidden) continue;
    const from = first.get(card);
    if (from) {
      const to = pageRect(card);
      const dx = from.left - to.left;
      const dy = from.top - to.top;
      const s = from.width / to.width;
      if (Math.abs(dx) < 1 && Math.abs(dy) < 1 && Math.abs(s - 1) < 0.01) continue;
      card.animate(
        [
          { transformOrigin: "0 0", transform: `translate(${dx}px, ${dy}px) scale(${s})` },
          { transformOrigin: "0 0", transform: "none" },
        ],
        { duration: 650, easing: EASE },
      );
    } else {
      card.animate(
        [{ opacity: 0, transform: "translateY(28px) scale(.97)" }, { opacity: 1, transform: "none" }],
        { duration: 560, delay: Math.min(entering++, 12) * 45, easing: EASE, fill: "backwards" },
      );
    }
  }
}
if (chips.length) {
  chips.forEach((c) => c.addEventListener("click", () => applyFilter(c.dataset.filter, true, true)));
  const initial = new URLSearchParams(location.search).get("filter");
  if (initial) applyFilter(initial, false, false);
}
// Lightbox for project galleries
const lightbox = document.querySelector(".lightbox");
if (lightbox) {
  const shots = [...document.querySelectorAll(".shot")];
  const stage = lightbox.querySelector(".lb-stage");
  const count = lightbox.querySelector(".lb-count");
  let index = 0;
  let lastFocus = null;

  const show = (i) => {
    index = (i + shots.length) % shots.length;
    const src = shots[index].querySelector("img, video");
    const clone = src.cloneNode();
    clone.removeAttribute("loading");
    if (clone.tagName === "VIDEO") { clone.autoplay = true; clone.preload = "auto"; }
    stage.replaceChildren(clone);
    stage.scrollTop = 0;
    count.textContent = `${index + 1} / ${shots.length}`;
  };
  const open = (i) => {
    lastFocus = document.activeElement;
    show(i);
    lightbox.hidden = false;
    document.body.style.overflow = "hidden";
    lightbox.querySelector(".lb-close").focus();
  };
  const close = () => {
    lightbox.hidden = true;
    stage.replaceChildren();
    document.body.style.overflow = "";
    lastFocus?.focus();
  };

  shots.forEach((s, i) => {
    s.tabIndex = 0;
    s.setAttribute("role", "button");
    s.setAttribute("aria-label", `放大第 ${i + 1} 張`);
    s.addEventListener("click", () => open(i));
    s.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(i); } });
  });
  lightbox.querySelector(".lb-close").addEventListener("click", close);
  lightbox.querySelector(".lb-prev").addEventListener("click", () => show(index - 1));
  lightbox.querySelector(".lb-next").addEventListener("click", () => show(index + 1));
  lightbox.addEventListener("click", (e) => { if (e.target === lightbox || e.target === stage) close(); });
  addEventListener("keydown", (e) => {
    if (lightbox.hidden) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") show(index - 1);
    if (e.key === "ArrowRight") show(index + 1);
  });

  let startX = null;
  stage.addEventListener("touchstart", (e) => { startX = e.touches[0].clientX; }, { passive: true });
  stage.addEventListener("touchend", (e) => {
    if (startX === null) return;
    const dx = e.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
    startX = null;
  });
}
