document.documentElement.classList.add("js");

// Header border once the page scrolls
const header = document.querySelector(".site-header");
const onScroll = () => header.classList.toggle("scrolled", scrollY > 8);
addEventListener("scroll", onScroll, { passive: true });
onScroll();

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
const chips = [...document.querySelectorAll(".chip")];
function applyFilter(name, push) {
  if (!chips.some((c) => c.dataset.filter === name)) name = "all";
  chips.forEach((c) => c.setAttribute("aria-pressed", c.dataset.filter === name));
  for (const card of cards) {
    const show = name === "all" || card.dataset.cats.split(" ").includes(name);
    card.hidden = !show;
    if (show) card.classList.add("in");
  }
  if (push) {
    const url = new URL(location);
    name === "all" ? url.searchParams.delete("filter") : url.searchParams.set("filter", name);
    history.replaceState(null, "", url);
  }
}
if (chips.length) {
  chips.forEach((c) => c.addEventListener("click", () => applyFilter(c.dataset.filter, true)));
  const initial = new URLSearchParams(location.search).get("filter");
  if (initial) applyFilter(initial, false);
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
