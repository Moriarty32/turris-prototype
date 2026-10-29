/* Progressive enhancement: all photos and category links work without JS. */
(() => {
 'use strict';
 const root = document.querySelector('.hotel-detail');
 if (!root) return;
 const gallery = JSON.parse(root.querySelector('[data-hotel-gallery]').textContent);
 const dialog = document.querySelector('#hotel-gallery-dialog');
 const picture = dialog.querySelector('img'), caption = dialog.querySelector('[data-gallery-caption]');
 let index = 0, trigger;
 const dots = dialog.querySelector('.hd-gallery-dots');
 gallery.forEach((item, n) => {
  const button = document.createElement('button');
  button.type = 'button'; button.textContent = String(n + 1); button.setAttribute('aria-label', item.caption);
  button.addEventListener('click', () => show(n)); dots.append(button);
 });
 function show(n) {
  index = (n + gallery.length) % gallery.length;
  picture.src = gallery[index].src; picture.alt = gallery[index].caption;
  caption.textContent = `${index + 1} / ${gallery.length} · ${gallery[index].caption}`;
  [...dots.children].forEach((b, j) => b.setAttribute('aria-pressed', String(j === index)));
 }
 root.querySelectorAll('[data-hotel-photo]').forEach(link => link.addEventListener('click', ev => {
  ev.preventDefault(); trigger = link; show(Number(link.dataset.hotelPhoto)); dialog.showModal();
 }));
 dialog.querySelector('[data-gallery-prev]').addEventListener('click', () => show(index - 1));
 dialog.querySelector('[data-gallery-next]').addEventListener('click', () => show(index + 1));
 dialog.addEventListener('keydown', ev => {
  if (ev.key === 'ArrowLeft' || ev.key === 'ArrowRight') {ev.preventDefault(); show(index + (ev.key === 'ArrowRight' ? 1 : -1));}
 });
 dialog.addEventListener('close', () => trigger?.focus());
 const form = root.querySelector('#hotel-booking form');
 const selection = root.querySelector('.hd-selected-room');
 function choose(room, name = '') {
  root.querySelectorAll('[data-booking]').forEach(f => {f.dataset.room = room; f.elements.room.value = room;});
  selection.hidden = !room; selection.querySelector('span').textContent = name;
 }
 root.querySelectorAll('[data-select-room]').forEach(link => link.addEventListener('click', ev => {
  ev.preventDefault(); choose(link.dataset.selectRoom, link.dataset.roomName);
  if (form.elements.checkin.value && form.elements.checkout.value) form.requestSubmit();
  else {document.querySelector('#hotel-booking').scrollIntoView({block: 'start', behavior: 'instant'}); form.querySelector('[data-dates]').click();}
 }));
 root.querySelector('[data-clear-room]').addEventListener('click', () => choose(''));
 const map = root.querySelector('.hd-map'), expand = root.querySelector('[data-map-expand]');
 function expandMap(value) {
  map.classList.toggle('hd-map-expanded', value); expand.setAttribute('aria-expanded', String(value));
  expand.setAttribute('aria-label', value ? 'Свернуть карту' : 'Развернуть карту');
  document.body.classList.toggle('hd-map-open', value);
  map.dispatchEvent(new Event('hotel-map-show'));
  if (!value) expand.focus();
 }
 expand.addEventListener('click', () => expandMap(!map.classList.contains('hd-map-expanded')));
 document.addEventListener('keydown', ev => {if (ev.key === 'Escape' && map.classList.contains('hd-map-expanded')) expandMap(false);});
 // Keep keyboard focus inside the expanded map; return to its control on Escape.
 map.addEventListener('keydown', ev => {
  if (ev.key !== 'Tab' || !map.classList.contains('hd-map-expanded')) return;
  const controls = [...map.querySelectorAll('button,a,[tabindex="0"]')].filter(el => el.getClientRects().length);
  if (ev.shiftKey && document.activeElement === controls[0]) {ev.preventDefault(); controls.at(-1).focus();}
  if (!ev.shiftKey && document.activeElement === controls.at(-1)) {ev.preventDefault(); controls[0].focus();}
 });
 const tabs = [...root.querySelectorAll('.hd-tabs a')];
 if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
   if (entry.isIntersecting) tabs.forEach(link => {if (link.hash === '#' + entry.target.id) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current');});
  }), {rootMargin: '-130px 0px -55% 0px'});
  tabs.forEach(link => observer.observe(root.querySelector(link.hash)));
 }
 document.querySelectorAll('.hd-header .nav a').forEach(link => link.addEventListener('click', () => {
  document.querySelector('.header-inner').classList.remove('menu-open'); document.querySelector('.menu-button').setAttribute('aria-expanded', 'false');
 }));
})();
