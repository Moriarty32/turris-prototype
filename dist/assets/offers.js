/* Scenario-specific controls reuse the shared trip context and booking dialogs. */
(() => {
 'use strict';
 const root=document.querySelector('[data-offer-page]');if(!root)return;
 const motion=matchMedia('(prefers-reduced-motion: reduce)');
 if('IntersectionObserver' in window){const reveal=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){if(!motion.matches)entry.target.classList.add('revealed');reveal.unobserve(entry.target);}}),{threshold:.08});root.querySelectorAll('.of-room,.of-option,.of-conditions,.of-band,.of-programs article').forEach(el=>{if(el.getBoundingClientRect().top>innerHeight)reveal.observe(el);});}
 const form=root.querySelector('[data-offer-form]'), family=root.dataset.offerPage==='family';
 const map=root.querySelector('[data-hotel-map]'), selected=root.querySelector('[data-offer-selection]');
 let guestDraft={adults:2,children:[]}, guestKey='';
 const guestName=()=>`${guestDraft.adults} ${guestDraft.adults===1?'взрослый':'взрослых'}`+(guestDraft.children.length?` · ${guestDraft.children.length} ${guestDraft.children.length===1?'ребёнок':'ребёнка'}`:'');
 function commitGuests(){if(guestDraft.children.every(n=>n!==null))document.dispatchEvent(new CustomEvent('booking-guests-change',{detail:guestDraft}));}
 function renderFamily(){
  root.querySelector('[data-family-value=adults]').textContent=guestDraft.adults;
  root.querySelector('[data-family-value=children]').textContent=guestDraft.children.length;
  root.querySelectorAll('[data-family-count]').forEach(b=>{const n=b.dataset.familyCount==='adults'?guestDraft.adults:guestDraft.children.length;b.disabled=+b.dataset.delta<0?n<=(b.dataset.familyCount==='adults'?1:0):n>=(b.dataset.familyCount==='adults'?6:4);});
  const ages=root.querySelector('[data-family-ages]');ages.replaceChildren();ages.hidden=!guestDraft.children.length;
  guestDraft.children.forEach((age,n)=>{
   const label=document.createElement('label');label.className='field';label.textContent='Возраст ребёнка '+(n+1);
   const select=document.createElement('select');select.required=true;select.setAttribute('aria-label','Возраст ребёнка '+(n+1));
   select.append(new Option('Выберите возраст','',age===null,age===null));
   for(let v=0;v<18;v++)select.append(new Option(v===0?'До 1 года':v+' '+(v===1?'год':v<5?'года':'лет'),String(v),age===v,age===v));
   select.addEventListener('change',()=>{guestDraft.children[n]=select.value===''?null:+select.value;commitGuests();updateSummary();});label.append(select);ages.append(label);
  });
  updateSummary();
 }
 function updateSummary(){
  if(!form)return;
  root.querySelector('[data-offer-date-summary]').textContent=form.querySelector('[data-date-label]').textContent;
  root.querySelector('[data-offer-guest-summary]').textContent=family?guestName():form.querySelector('[data-guest-label]').textContent;
 }
 function sync(){
  if(!form)return;
  const key=form.elements.adults.value+'|'+form.elements.children.value;
  if(family&&key!==guestKey){guestKey=key;guestDraft={adults:+form.elements.adults.value,children:JSON.parse(form.elements.children.value)};renderFamily();}
  updateSummary();
 }
 if(form){
  document.addEventListener('booking-context-change',sync);sync();
  root.querySelectorAll('[data-family-count]').forEach(b=>b.addEventListener('click',()=>{
   if(b.dataset.familyCount==='adults')guestDraft.adults=Math.max(1,Math.min(6,guestDraft.adults+(+b.dataset.delta)));
   else if(+b.dataset.delta>0&&guestDraft.children.length<4)guestDraft.children.push(null);else if(+b.dataset.delta<0)guestDraft.children.pop();
   renderFamily();commitGuests();
  }));
  form.addEventListener('submit',ev=>{
   if(family&&guestDraft.children.some(n=>n===null)){ev.preventDefault();ev.stopImmediatePropagation();form.querySelector('.form-error').textContent='Укажите возраст каждого ребёнка на дату заезда.';root.querySelector('[data-family-ages] select:invalid')?.focus();return;}
   const start=form.elements.checkin.value,end=form.elements.checkout.value,min=Number(form.dataset.minNights||0);
   if(start&&end&&min&&(new Date(end+'T12:00:00')-new Date(start+'T12:00:00'))/86400000<min){ev.preventDefault();ev.stopImmediatePropagation();form.querySelector('.form-error').textContent=`Для этого предложения выберите проживание от ${min} ночей. Для короткой поездки доступны обычные тарифы отеля.`;form.querySelector('[data-dates]').focus();}
  },true);
 }
 function choose(hotel,room='',name=''){
  if(!form)return;
  if(form.elements.hotel.value!==hotel){form.elements.hotel.value=hotel;form.elements.hotel.dispatchEvent(new Event('change',{bubbles:true}));}
  form.elements.room.value=room;form.dataset.room=room;
  selected.textContent=room?'Выбран номер: '+name+'. Проверьте даты и состав гостей.':hotel?'Выбран отель «'+form.elements.hotel.selectedOptions[0].textContent+'».':'';
  root.querySelector('[data-offer-clear]').hidden=false;
  map.dispatchEvent(new CustomEvent('hotel-map-select',{detail:{id:hotel,pan:false}}));
 }
 function searchFocus(){root.querySelector('#offer-search').scrollIntoView({block:'start',behavior:'instant'});}
 root.querySelector('[data-offer-clear]')?.addEventListener('click',()=>{form.elements.room.value='';form.dataset.room='';form.elements.hotel.value=form.elements.hotel.options[0].value;form.elements.hotel.dispatchEvent(new Event('change',{bubbles:true}));selected.textContent='';root.querySelector('[data-offer-clear]').hidden=true;root.querySelector('#options').scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});});
 root.querySelectorAll('[data-offer-room]').forEach(link=>link.addEventListener('click',ev=>{
  ev.preventDefault();choose(link.dataset.offerHotel,link.dataset.offerRoom,link.dataset.offerRoomName);searchFocus();
  if(family&&guestDraft.children.some(n=>n===null)){root.querySelector('[data-family-ages] select:invalid')?.reportValidity();return;}
  if(!form.elements.checkin.value)form.querySelector('[data-dates]').click();else form.requestSubmit();
 }));
 root.querySelectorAll('[data-offer-map-hotel]').forEach(link=>link.addEventListener('click',ev=>{
  ev.preventDefault();const id=link.dataset.offerMapHotel;
  if(form){choose(id);root.querySelectorAll('.of-room').forEach(card=>card.hidden=card.querySelector('[data-offer-hotel]').dataset.offerHotel!==id);root.querySelector('#options').scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});}
  else{const lead=root.querySelector('[data-lead]');lead.elements.wishes.value='Предпочтительный отель: '+link.closest('article').querySelector('[data-map-select]>span').firstChild.textContent+'.';searchFocus();lead.elements.arrival.focus();}
 }));
 // Choosing all hotels in the search restores all suggested categories.
 if(form)form.elements.hotel.addEventListener('change',()=>{root.querySelectorAll('.of-room').forEach(card=>card.hidden=form.elements.hotel.value&&card.querySelector('[data-offer-hotel]').dataset.offerHotel!==form.elements.hotel.value);});
 root.querySelector('[data-offer-dates]').addEventListener('click',ev=>{ev.preventDefault();searchFocus();if(form)form.querySelector('[data-dates]').click();else root.querySelector('[name=arrival]').focus();});
 root.querySelector('[data-offer-guests]').addEventListener('click',ev=>{ev.preventDefault();searchFocus();if(family)root.querySelector('[data-family-count=adults][data-delta="1"]').focus();else if(form)form.querySelector('[data-guests]').click();else root.querySelector('[name=guests]').focus();});
 root.querySelector('[data-offer-submit]').addEventListener('click',ev=>{ev.preventDefault();searchFocus();if(form)form.requestSubmit();else root.querySelector('[data-next-step]').click();});
 const expand=root.querySelector('[data-offer-map-expand]'),stage=map.querySelector('.map-stage');
 function full(value){window.turrisModalBackground(stage,value);map.classList.toggle('of-map-expanded',value);document.body.classList.toggle('of-map-open',value);if(value){stage.setAttribute('role','dialog');stage.setAttribute('aria-modal','true');stage.setAttribute('aria-label','Карта отелей');}else{stage.removeAttribute('role');stage.removeAttribute('aria-modal');stage.removeAttribute('aria-label');}expand.setAttribute('aria-expanded',String(value));expand.setAttribute('aria-label',value?'Свернуть карту':'Развернуть карту');map.dispatchEvent(new Event('hotel-map-show'));expand.focus();}
 expand.addEventListener('click',()=>full(!map.classList.contains('of-map-expanded')));
 document.addEventListener('keydown',ev=>{if(ev.key==='Escape'&&map.classList.contains('of-map-expanded'))full(false);});
 stage.addEventListener('keydown',ev=>{if(ev.key!=='Tab'||!map.classList.contains('of-map-expanded'))return;const items=[...stage.querySelectorAll('a,button,[tabindex="0"]')].filter(el=>el.getClientRects().length);if(ev.shiftKey&&document.activeElement===items[0]){ev.preventDefault();items.at(-1).focus();}else if(!ev.shiftKey&&document.activeElement===items.at(-1)){ev.preventDefault();items[0].focus();}});
 const filter=root.querySelector('[data-offer-filter]');if(filter)filter.addEventListener('change',()=>{let count=0;root.querySelectorAll('[data-promo-hotel]').forEach(card=>{card.hidden=!['all',...card.dataset.promoHotel.split(' ')].includes(filter.value)&&card.dataset.promoHotel!=='all';if(!card.hidden)count++;});root.querySelector('[data-offer-count]').textContent='Найдено: '+count;});
})();

