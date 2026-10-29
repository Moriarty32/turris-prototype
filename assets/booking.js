/* Booking screen: one selected hotel across form, cards and map. */
(() => {
 'use strict';
 const root = document.querySelector('.booking-page');
 if (!root) return;
 const form = root.querySelector('[data-booking]'), hotel = form.elements.hotel;
 const map = root.querySelector('[data-hotel-map]'), results = root.querySelector('#booking-results');
 const status = root.querySelector('[data-booking-choice-status]');
 const roomContext = root.querySelector('.bk-room-context');
 let lastTrip = '';
 const trip = () => [hotel.value,form.elements.checkin.value,form.elements.checkout.value,form.elements.adults.value,form.elements.children.value,form.elements.room.value].join('|');
 function paint(initial = false) {
  root.querySelectorAll('[data-booking-card]').forEach(card => {
   const selected = card.dataset.bookingCard === hotel.value;
   card.classList.toggle('is-selected', selected);
   card.querySelector('.bk-select-circle').setAttribute('aria-pressed', String(selected));
   const label = card.querySelector('[data-pick-label]');
   label.firstChild.textContent = selected ? 'Отель выбран ' : 'Выбрать отель ';
   if (selected) label.setAttribute('aria-current', 'true'); else label.removeAttribute('aria-current');
  });
  if (hotel.value) map.dispatchEvent(new CustomEvent('hotel-map-select', {detail:{id:hotel.value,pan:!initial}}));
  else if (!initial) map.querySelector('[data-map-reset]').click();
  const changed = !initial && trip() !== lastTrip;
  if (changed && results.querySelector('.room-card,.empty-state')) results.hidden = true;
  root.querySelector('[data-search-hint]').textContent = form.elements.checkin.value ? 'Параметры готовы. Нажмите «Показать номера и цены» для продолжения.' : 'Укажите даты, чтобы перейти к выбору категории номера.';
  if (!initial) status.textContent = hotel.value ? 'Выбран отель «'+hotel.selectedOptions[0].textContent+'». Даты и гости — в форме выше.' : 'Можно сравнить категории всех четырёх отелей.';
  const room = form.elements.room.value;
  roomContext.hidden = !room;
  root.querySelector('[data-room-context]').textContent = room ? 'Категория из предыдущего шага сохранена.' : '';
  lastTrip = trip();
 }
 function pick(id, returnToForm = false) {
  if (hotel.value !== id) {hotel.value = id; hotel.dispatchEvent(new Event('change', {bubbles:true}));}
  if (returnToForm) {
   root.querySelector('#booking-search').scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});
   form.querySelector('[data-dates]').focus({preventScroll:true});
  }
 }
 root.querySelectorAll('[data-booking-pick]').forEach(button => button.addEventListener('click', ev => {ev.preventDefault();pick(button.dataset.bookingPick,true);}));
 document.addEventListener('booking-context-change', () => paint());
 document.addEventListener('booking-results-updated', () => {results.hidden=false;lastTrip=trip();});
 map.addEventListener('hotel-map-selection', ev => {pick(ev.detail.id);syncAccordion();});
 function syncAccordion() {
  map.querySelectorAll('[data-map-select]').forEach(button => button.setAttribute('aria-expanded', String(button.dataset.mapSelect === map.dataset.selected)));
 }
 new MutationObserver(syncAccordion).observe(map,{attributes:true,attributeFilter:['data-selected']});
 paint(true);syncAccordion();
 root.querySelector('[data-booking-clear-room]').addEventListener('click', () => document.dispatchEvent(new Event('booking-clear-room')));
 root.querySelector('[data-booking-open-dates]').addEventListener('click', ev => {
  ev.preventDefault();root.querySelector('#booking-search').scrollIntoView({block:'start',behavior:'instant'});form.querySelector('[data-dates]').click();
 });
 const promo=root.querySelector('#booking-promo'), promoStatus=root.querySelector('[data-promo-status]');
 try {promo.value=sessionStorage.getItem('turris-promo')||'';} catch {}
 function promoMessage(saved) {promoStatus.textContent=saved?'Код сохранён для этой вкладки. Введите его и проверьте скидку на официальном сайте отеля.':'Действие кода и скидку проверяйте на официальном сайте отеля.';}
 if(promo.value) promoMessage(true);
 root.querySelector('[data-save-promo]').addEventListener('click',()=>{
  promo.value=promo.value.trim();
  try {if(promo.value)sessionStorage.setItem('turris-promo',promo.value);else sessionStorage.removeItem('turris-promo');promoMessage(Boolean(promo.value));}
  catch {promoStatus.textContent='Не удалось сохранить код в браузере. Скопируйте его для ввода на сайте отеля.';}
 });
 promo.addEventListener('keydown',ev=>{if(ev.key==='Enter'){ev.preventDefault();root.querySelector('[data-save-promo]').click();}});
 const expand = root.querySelector('[data-booking-expand]'), stage=map.querySelector('.map-stage');
 function expanded(value) {
  map.classList.toggle('bk-map-expanded',value);document.body.classList.toggle('bk-map-open',value);
  expand.setAttribute('aria-expanded',String(value));expand.querySelector('span').textContent=value?'Свернуть карту':'На весь экран';
  stage.setAttribute('role',value?'dialog':'region');stage.setAttribute('aria-label','Карта отелей');
  if(value)stage.setAttribute('aria-modal','true');else stage.removeAttribute('aria-modal');
  map.dispatchEvent(new Event('hotel-map-show'));expand.focus();
 }
 expand.addEventListener('click',()=>expanded(!map.classList.contains('bk-map-expanded')));
 document.addEventListener('keydown',ev=>{if(ev.key==='Escape'&&map.classList.contains('bk-map-expanded'))expanded(false);});
 stage.addEventListener('keydown',ev=>{
  if(ev.key!=='Tab'||!map.classList.contains('bk-map-expanded'))return;
  const focus=[...stage.querySelectorAll('button,a,[tabindex="0"]')].filter(el=>el.getClientRects().length);
  if(ev.shiftKey&&document.activeElement===focus[0]){ev.preventDefault();focus.at(-1).focus();}
  else if(!ev.shiftKey&&document.activeElement===focus.at(-1)){ev.preventDefault();focus[0].focus();}
 });
})();
