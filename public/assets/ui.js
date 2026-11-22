// Shared by every page (home, projects, About): theme button, email links, Work/About switch.
// The theme itself is set before first paint by the small inline script in <head>.
(() => {
  const root = document.documentElement;
  const KEY = "aifree-theme";
  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Light / dark button: icon shows where a click takes you (sun in dark mode, moon in light mode)
  const label = () => {
    const light = root.dataset.theme === "light";
    document.querySelectorAll(".theme-btn").forEach((b) => {
      b.setAttribute("aria-label", light ? "Switch to dark mode" : "Switch to light mode");
      b.setAttribute("aria-pressed", String(light));
    });
  };
  label();
  addEventListener("click", (e) => {
    if (!e.target.closest(".theme-btn")) return;
    const next = root.dataset.theme === "light" ? "dark" : "light";
    localStorage.setItem(KEY, next);
    root.dataset.theme = next;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = next === "light" ? "#efebe3" : "#0f0e0d";
    label();
  });

  // Email links do nothing visible without a mail app, so also copy the address and say so
  const toast = (text) => {
    let n = document.querySelector(".copy-toast");
    if (!n) {
      n = document.createElement("div");
      n.className = "copy-toast";
      n.setAttribute("role", "status");
      document.body.append(n);
    }
    n.textContent = text;
    n.classList.add("on");
    clearTimeout(n.timer);
    n.timer = setTimeout(() => n.classList.remove("on"), 3200);
  };
  addEventListener("click", (e) => {
    const a = e.target.closest('a[href^="mailto:"]');
    if (!a) return;
    const mail = a.getAttribute("href").slice(7).split("?")[0];
    const copy = navigator.clipboard ? navigator.clipboard.writeText(mail) : Promise.reject();
    copy.then(() => toast(`Email copied: ${mail}`), () => toast(mail));
  });

  // Work / About: a pill that slides between the two. It slides before leaving the page,
  // and the next page starts it where it was, so the switch reads as one movement.
  const FROM = "aifree-nav-from";
  document.querySelectorAll(".nav, .pf-nav").forEach((nav) => {
    const links = [...nav.querySelectorAll("a")];
    const current = links.find((a) => a.hasAttribute("aria-current"));
    if (!current) return;
    const pill = document.createElement("span");
    pill.className = "nav-pill";
    pill.setAttribute("aria-hidden", "true");
    nav.prepend(pill);
    const moveTo = (a) => {
      pill.style.width = `${a.offsetWidth}px`;
      pill.style.transform = `translateX(${a.offsetLeft - 3}px)`;
      links.forEach((l) => l.classList.toggle("on", l === a));
    };
    const from = links.find((a) => a.getAttribute("href") === sessionStorage.getItem(FROM));
    sessionStorage.removeItem(FROM);
    nav.classList.add("ready", "still");
    moveTo(from && !calm ? from : current);
    requestAnimationFrame(() => requestAnimationFrame(() => {
      nav.classList.remove("still");
      if (from && from !== current) moveTo(current);
    }));
    addEventListener("resize", () => {
      nav.classList.add("still");
      moveTo(links.find((l) => l.classList.contains("on")) || current);
      requestAnimationFrame(() => nav.classList.remove("still"));
    });
    links.forEach((a) => a.addEventListener("click", (e) => {
      if (a === current || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
      e.preventDefault();
      sessionStorage.setItem(FROM, current.getAttribute("href"));
      moveTo(a);
      setTimeout(() => { location.href = a.href; }, calm ? 0 : 280);
    }));
  });
})();
