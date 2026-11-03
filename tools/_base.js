(() => {
  /* 헤더, 드로어 */
  const hd = document.getElementById('hd'), body = document.body, burger = document.getElementById('burger');
  const onScroll = () => hd.classList.toggle('scrolled', scrollY > 8);
  addEventListener('scroll', onScroll, {passive:true}); onScroll();
  const setMenu = open => { body.classList.toggle('menu-open', open); burger.setAttribute('aria-expanded', open); };
  burger.onclick = () => setMenu(!body.classList.contains('menu-open'));
  document.querySelectorAll('#drawer a[href^="#"]').forEach(a => a.addEventListener('click', () => setMenu(false)));
  addEventListener('resize', () => { if (innerWidth > 1080) setMenu(false); });

  /* 히어로 슬라이드: 진행 바, 이전·다음, 일시정지, 스와이프 */
  const rh = document.getElementById('top'), rs = [...rh.querySelectorAll('.rh-slide')], dots = [...rh.querySelectorAll('.rh-dot')];
  const toggle = rh.querySelector('.rh-toggle'), DUR = 6000;
  const pauseLabel = {ko:['일시정지','재생'], en:['Pause','Play'], ja:['一時停止','再生']}[document.documentElement.lang] || ['Pause','Play'];
  let cur = 0, timer = null, left = DUR, started = 0, paused = matchMedia('(prefers-reduced-motion: reduce)').matches;
  rh.style.setProperty('--rh-dur', DUR + 'ms');
  const schedule = ms => { clearTimeout(timer); started = Date.now(); left = ms; if (!paused) timer = setTimeout(() => rhShow(cur + 1), ms); };
  const rhShow = n => {
    rs[cur].classList.remove('is-active');
    cur = (n + rs.length) % rs.length;
    rs.forEach((s, i) => { s.classList.toggle('is-active', i === cur); s.setAttribute('aria-hidden', i !== cur); });
    rs[cur].querySelectorAll('img').forEach(img => img.loading = 'eager');
    dots.forEach((d, i) => { d.classList.remove('is-active'); d.classList.toggle('is-done', i < cur); d.setAttribute('aria-current', i === cur); });
    void dots[cur].offsetWidth; dots[cur].classList.add('is-active');
    schedule(DUR);
  };
  const setPaused = p => {
    paused = p; rh.classList.toggle('is-paused', p); toggle.setAttribute('aria-label', pauseLabel[p ? 1 : 0]);
    if (p) { clearTimeout(timer); left -= Date.now() - started; } else schedule(Math.max(left, 300));
  };
  dots.forEach((d, i) => d.onclick = () => rhShow(i));
  rh.querySelector('.rh-prev').onclick = () => rhShow(cur - 1);
  rh.querySelector('.rh-next').onclick = () => rhShow(cur + 1);
  toggle.onclick = () => setPaused(!paused);
  let tx = null;
  rh.addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, {passive:true});
  rh.addEventListener('touchend', e => { if (tx === null) return; const dx = e.changedTouches[0].clientX - tx; if (Math.abs(dx) > 50) rhShow(cur + (dx < 0 ? 1 : -1)); tx = null; });
  document.addEventListener('visibilitychange', () => { if (document.hidden && !paused) { setPaused(true); rh.dataset.auto = 1; } else if (!document.hidden && rh.dataset.auto) { delete rh.dataset.auto; setPaused(false); } });
  rh.classList.toggle('is-paused', paused);
  rhShow(0);

  /* 등장 모션 */
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), {rootMargin:'0px 0px -8% 0px'});
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));

  /* 현재 섹션 → 메뉴 밑줄 */
  const secs = [...document.querySelectorAll('[data-sec]')];
  const links = [...document.querySelectorAll('#menu a')];
  const spy = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    const id = '#' + e.target.id;
    links.forEach(l => l.classList.toggle('on', l.getAttribute('href') === id));
  }), {rootMargin:'-45% 0px -50% 0px'});
  secs.forEach(s => spy.observe(s));

  /* GA4: 섹션 도달 · 샵 클릭 (gtag가 있을 때만) */
  const seen = new Set();
  const gaSpy = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting || seen.has(e.target.id) || typeof gtag !== 'function') return;
    seen.add(e.target.id); gtag('event', 'section_view', { section_name: e.target.id });
  }), {threshold: 0.3});
  secs.forEach(s => gaSpy.observe(s));
  document.querySelectorAll('a[href*="rubiworkshop.com"]').forEach(a => a.addEventListener('click', () => {
    if (typeof gtag === 'function') gtag('event', 'shop_click', { link_location: a.closest('[data-sec]')?.id || a.closest('section,header,footer')?.id || 'header' });
  }));

  /* 타임라인 드래그 */
  let moved = false;
  document.querySelectorAll('[data-drag]').forEach(strip => {
    let down = false, sx = 0, sl = 0;
    strip.addEventListener('pointerdown', e => { if (e.pointerType !== 'mouse') return; down = true; moved = false; sx = e.clientX; sl = strip.scrollLeft; strip.classList.add('drag'); });
    addEventListener('pointermove', e => { if (!down) return; const dx = e.clientX - sx; if (Math.abs(dx) > 4) moved = true; strip.scrollLeft = sl - dx; });
    addEventListener('pointerup', () => { down = false; strip.classList.remove('drag'); });
  });

  /* 라이트박스 */
  const lb = document.getElementById('lb'), lbImg = lb.querySelector('img'), lbCt = lb.querySelector('.ct');
  let set = [], li = 0;
  const show = () => { lbImg.src = set[li].src; lbImg.alt = set[li].alt; lbCt.textContent = `${li + 1} / ${set.length}`; };
  const closeLb = () => lb.classList.remove('on');
  document.querySelectorAll('[data-gallery]').forEach(g => g.addEventListener('click', e => {
    const img = e.target.closest('figure')?.querySelector('img'); if (!img || moved) return;
    set = [...g.querySelectorAll('img')]; li = set.indexOf(img); show(); lb.classList.add('on');
  }));
  lb.querySelector('.x').onclick = closeLb;
  lb.querySelector('.pv').onclick = e => { e.stopPropagation(); li = (li - 1 + set.length) % set.length; show(); };
  lb.querySelector('.nx').onclick = e => { e.stopPropagation(); li = (li + 1) % set.length; show(); };
  lb.addEventListener('click', e => { if (e.target === lb) closeLb(); });
  addEventListener('keydown', e => {
    if (e.key === 'Escape') { closeLb(); setMenu(false); }
    if (!lb.classList.contains('on')) return;
    if (e.key === 'ArrowLeft') lb.querySelector('.pv').click();
    if (e.key === 'ArrowRight') lb.querySelector('.nx').click();
  });
})();
