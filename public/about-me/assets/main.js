(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reduced) $$('video[autoplay]').forEach(v => { v.removeAttribute('autoplay'); v.pause(); });

  // crosshair marks on the background grid
  const marks = $('.bg__marks');
  const colW = () => parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--col')) || 160;
  function buildMarks() {
    const step = innerWidth <= 700 ? innerWidth / 4 : colW();
    let html = '';
    for (let x = step; x < innerWidth + step * 2; x += step * 2) {
      for (let y = 180; y < innerHeight; y += 180) {
        html += `<b style="left:${x}px;top:${y}px;animation-delay:${-((x * 13 + y * 7) % 97) / 97 * 3.4}s"></b>`;
      }
    }
    marks.innerHTML = html;
  }
  buildMarks();
  addEventListener('resize', buildMarks);

  // marquee rows (content duplicated so a -50% loop is seamless)
  const sep = '<span class="sep"></span>';
  const rows = [
    'Branding' + sep + '<em>Web</em>&nbsp;Design' + sep + 'Graphic' + sep,
    'Photography' + sep + '<em>Motion</em>' + sep + '3D&nbsp;Graphic' + sep,
    'Vibe Code<span class="tag">AI</span>'
  ];
  $$('.marquee__track').forEach((el, i) => { el.innerHTML = rows[i].repeat(i === 2 ? 4 : 3).repeat(2); });

  // running route (deterministic elevation profile)
  const pts = [];
  for (let i = 0; i <= 160; i++) {
    const x = i * 10;
    const y = 130 - 45 * Math.sin(i / 13) - 26 * Math.sin(i / 5.3 + 1) - 13 * Math.sin(i / 2.1) + (i > 100 ? -30 * Math.sin((i - 100) / 19) : 0);
    pts.push([x, y]);
  }
  const line = $('.route__line'), area = $('.route__area'), dot = $('.route__dot');
  line.setAttribute('d', 'M' + pts.map(p => p.map(v => v.toFixed(1)).join(' ')).join(' L'));
  area.setAttribute('d', `M0 240 L${pts.map(p => p.join(' ')).join(' L')} L1600 240 Z`);
  const RL = line.getTotalLength();
  line.style.strokeDasharray = RL;
  line.style.strokeDashoffset = reduced ? 0 : RL;
  const last = pts[pts.length - 1];
  dot.setAttribute('cx', last[0]); dot.setAttribute('cy', last[1]);

  // counters
  function count(el) {
    const to = parseFloat(el.dataset.count), dec = +(el.dataset.dec || 0);
    if (reduced) return;
    const t0 = performance.now(), dur = dec ? 1600 : 1100;
    (function tick(now) {
      const p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      el.textContent = (e * to).toFixed(dec);
      if (p < 1) requestAnimationFrame(tick);
    })(t0);
  }

  // scroll reveals
  const io = new IntersectionObserver(entries => {
    for (const en of entries) {
      if (!en.isIntersecting) continue;
      const el = en.target;
      el.classList.add('in');
      $$('[data-count]', el).forEach(count);
      if (el.matches('.route')) line.style.strokeDashoffset = 0;
      io.unobserve(el);
    }
  }, { threshold: 0.18, rootMargin: '0px 0px -8% 0px' });
  $$('.reveal, .reveal-x, .route, h2, .job__yr, .num').forEach(el => io.observe(el));
  requestAnimationFrame(() => $('.hero').classList.add('in'));
  $$('.hero .ln').forEach(el => el.parentElement.classList.add('in'));

  // chrome follows the section under it; progress + index
  const secs = $$('.sec');
  const prog = $('.chrome__prog'), idx = $('#idx'), lbl = $('#lbl');
  let ticking = false;
  function onScroll() {
    ticking = false;
    const h = document.documentElement;
    prog.style.transform = `scaleX(${h.scrollTop / Math.max(1, h.scrollHeight - innerHeight)})`;
    const probe = $('.chrome').offsetHeight + 1;
    let cur = secs[0], ci = 0;
    secs.forEach((s, i) => { if (s.getBoundingClientRect().top <= probe) { cur = s; ci = i; } });
    document.body.classList.toggle('is-dark', cur.classList.contains('sec--dark'));
    document.body.classList.toggle('is-hot', cur.classList.contains('sec--hot'));
    idx.textContent = String(ci + 1).padStart(2, '0');
    lbl.textContent = cur.dataset.label;
  }
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();
})();
