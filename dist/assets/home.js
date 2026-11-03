/* Rotation previews real rooms. Only an explicit hotel choice updates the trip. */
(() => {
  'use strict';
  const carousel = document.querySelector('[data-hero-carousel]');
  if (!carousel) return;
  const slides = [...carousel.querySelectorAll('[data-hero-slide]')];
  const picks = [...carousel.querySelectorAll('[data-hero-pick]')];
  const play = carousel.querySelector('[data-hero-play]');
  const status = carousel.querySelector('.hero-slider-status');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const mobile = matchMedia('(max-width:767px)');
  const hotel = document.querySelector('.home-booking [name=hotel]');
  let current = 0, timer, userPaused = motion.matches, hovered = false, visible = false;
  let pointer = null;

  function schedule() {
    clearTimeout(timer);
    carousel.classList.remove('is-running');
    carousel.classList.toggle('is-paused', userPaused);
    play.setAttribute('aria-label', userPaused ? 'Включить автоматическую смену отелей' : 'Остановить автоматическую смену отелей');
    if (mobile.matches || userPaused || hovered || !visible || document.hidden || carousel.closest('[inert]') || document.querySelector('dialog[open]')) return;
    void carousel.offsetWidth;
    carousel.classList.add('is-running');
    timer = setTimeout(() => show(current + 1), 5000);
  }

  function show(index, manual = false) {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, n) => {
      const active = n === current;
      slide.classList.toggle('is-active', active);
      slide.inert = !active;
      slide.setAttribute('aria-hidden', String(!active));
      picks[n].classList.toggle('is-preview', active);
      picks[n].setAttribute('aria-pressed', String(hotel.value === slide.dataset.heroSlide));
    });
    if (manual) {
      userPaused = true;
      status.textContent = slides[current].getAttribute('aria-label');
    }
    schedule();
  }

  function choose(index) {
    show(index, true);
    hotel.value = slides[current].dataset.heroSlide;
    hotel.dispatchEvent(new Event('change', {bubbles: true}));
  }
  picks.forEach((button, index) => button.addEventListener('click', () => choose(index)));
  document.addEventListener('booking-context-change', () => {
    const index = slides.findIndex(slide => slide.dataset.heroSlide === hotel.value);
    if (index >= 0) show(index, true);
    else picks.forEach(button => button.setAttribute('aria-pressed', 'false'));
  });
  carousel.querySelector('[data-hero-prev]').addEventListener('click', () => show(current - 1, true));
  carousel.querySelector('[data-hero-next]').addEventListener('click', () => show(current + 1, true));
  // Focus stops rotation until the visitor explicitly starts it again.
  carousel.closest('.home-hero').addEventListener('focusin', event => {
    if (event.target === play) return;
    userPaused = true;
    schedule();
  });
  play.addEventListener('click', () => { userPaused = !userPaused; schedule(); });
  carousel.addEventListener('pointerenter', event => { if (event.pointerType === 'mouse') { hovered = true; schedule(); } });
  carousel.addEventListener('pointerleave', () => { hovered = false; schedule(); });
  carousel.addEventListener('keydown', event => {
    if (!event.target.closest('.hero-carousel-controls,.hero-slide-caption')) return;
    if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    const index = current + (event.key === 'ArrowRight' ? 1 : -1);
    if (event.target.closest('.hero-slide-picker')) choose(index);
    else show(index, true);
    if (event.target.closest('a')) picks[current].focus();
  });
  carousel.addEventListener('pointerdown', event => {
    if (!mobile.matches && event.pointerType !== 'mouse' && !event.target.closest('button,a,form')) pointer = {x: event.clientX, y: event.clientY};
  });
  carousel.addEventListener('pointerup', event => {
    if (!pointer) return;
    const dx = event.clientX - pointer.x, dy = event.clientY - pointer.y;
    pointer = null;
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.5) show(current + (dx < 0 ? 1 : -1), true);
  });
  carousel.addEventListener('pointercancel', () => { pointer = null; });
  document.addEventListener('visibilitychange', schedule);
  motion.addEventListener('change', () => { userPaused = motion.matches; schedule(); });
  new MutationObserver(schedule).observe(document.body, {subtree: true, attributes: true, attributeFilter: ['inert', 'open']});
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => { visible = entries[0].intersectionRatio >= .15; schedule(); }, {threshold: .15}).observe(carousel);
  } else { visible = true; }
  // Load remaining real photos at low priority, before the first automatic change.
  function preload() { if (mobile.matches) return; slides.slice(1).forEach(slide => {
    const photo = slide.querySelector('img');
    photo.fetchPriority = 'low';
    photo.loading = 'eager';
  }); }
  mobile.addEventListener('change', () => { preload(); schedule(); });
  preload();
  const initial = slides.findIndex(slide => slide.dataset.heroSlide === hotel.value);
  show(initial >= 0 ? initial : 0, initial >= 0);
})();

/* One map moves between the mobile hero and its desktop section. Selection
   explicitly updates the existing form, preserving dates and guest ages. */
(() => {
  'use strict';
  const slot = document.querySelector('[data-mobile-map-slot]');
  if (!slot) return;
  const mobile = matchMedia('(max-width:767px)');
  const root = document.querySelector('.home-map-section [data-hotel-map]');
  const section = root.closest('.home-map-section');
  const mapHome = root.parentElement;
  const form = document.querySelector('.home-booking [data-booking]');
  const select = form.querySelector('[name=hotel]');
  const bar = document.querySelector('.home-mobile-actions');
  const book = bar.querySelector('[data-mobile-book]');
  const motion = matchMedia('(prefers-reduced-motion:reduce)');
  root.setAttribute('data-home-map', '');
  const empty = document.createElement('p');
  empty.className = 'mobile-map-empty';
  empty.textContent = 'Можно выбрать отель на карте или сравнить все четыре на ваши даты.';
  root.querySelector('.map-details').append(empty);
  function sync() {
    if (mobile.matches) root.dispatchEvent(new CustomEvent('hotel-map-select', {detail:{id:select.value,pan:false}}));
    else if (select.value || !root.dataset.selected) root.dispatchEvent(new CustomEvent('hotel-map-select', {detail:{id:select.value || 'tverskaya',pan:false}}));
    empty.hidden = !!select.value;
    const hasDates = !!form.elements.checkin.value;
    book.firstChild.textContent = hasDates ? 'Номера и цены ' : 'Выбрать даты ';
    window.turrisSelects?.refresh();
  }
  function layout() {
    if (root.classList.contains('map-expanded')) root.querySelector('.map-expand')?.click();
    (mobile.matches ? slot : mapHome).append(root);
    section.hidden = mobile.matches;
    sync();
    root.dispatchEvent(new Event('hotel-map-show'));
    updateBar();
  }
  root.addEventListener('hotel-map-selection', event => {
    if (!mobile.matches) return;
    select.value = event.detail.id;
    select.dispatchEvent(new Event('change', {bubbles:true}));
  });
  document.addEventListener('booking-context-change', sync);
  function goToMap() {
    root.scrollIntoView({block:'start',behavior:motion.matches?'instant':'smooth'});
    root.querySelector('[data-map-select]')?.focus({preventScroll:true});
  }
  bar.querySelector('[data-mobile-map]').addEventListener('click', goToMap);
  book.addEventListener('click', () => {
    form.scrollIntoView({block:'center',behavior:'instant'});
    if (!form.elements.checkin.value) form.querySelector('[data-dates]').click();
    else form.requestSubmit();
  });
  function updateBar() {
    const blocked = document.querySelector('dialog[open],.ux-menu-open,.ux-map-open');
    const buttons = [...document.querySelectorAll('.home-page [data-booking] button[type=submit]')];
    const buttonVisible = buttons.some(button => {const r=button.getBoundingClientRect();return r.top>=72 && r.bottom<=innerHeight;});
    bar.hidden = !mobile.matches || !!blocked || buttonVisible;
  }
  new IntersectionObserver(updateBar,{threshold:[0,1]}).observe(form.querySelector('[type=submit]'));
  new IntersectionObserver(updateBar,{threshold:[0,1]}).observe(document.querySelector('.booking-bottom [type=submit]'));
  new MutationObserver(updateBar).observe(document.body,{subtree:true,attributes:true,attributeFilter:['open','class','inert']});
  let queued = false;
  addEventListener('scroll',()=>{if(!queued){queued=true;requestAnimationFrame(()=>{queued=false;updateBar();});}},{passive:true});
  addEventListener('resize',updateBar);
  mobile.addEventListener('change',layout);
  layout();
})();
