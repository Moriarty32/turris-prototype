/* Turris site UI. Live reservations are handled exclusively by the external TravelLine module. */
(()=>{'use strict';

const modalBackgrounds=new WeakMap();
window.turrisModalBackground=(element,active)=>{if(active){if(modalBackgrounds.has(element))return;const previous=[];for(let node=element;node&&node!==document.body;node=node.parentElement){for(const sibling of node.parentElement.children){if(sibling!==node&&!['SCRIPT','STYLE','LINK'].includes(sibling.tagName)){previous.push([sibling,sibling.inert]);sibling.inert=true;}}}modalBackgrounds.set(element,previous);}else{for(const [node,inert]of modalBackgrounds.get(element)||[])node.inert=inert;modalBackgrounds.delete(element);}};

const base=window.SITE_BASE||'', $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const today=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Moscow',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const addDay=s=>{const d=new Date(s+'T12:00:00');d.setDate(d.getDate()+1);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`};
const validDate=s=>{if(!/^\d{4}-\d{2}-\d{2}$/.test(s||''))return false;const d=new Date(s+'T12:00:00Z');return !Number.isNaN(d.getTime())&&d.toISOString().slice(0,10)===s;};
const fmt=s=>validDate(s)?new Date(s+'T12:00:00').toLocaleDateString('ru-RU',{day:'numeric',month:'short'}):'';
const clamp=(v,min,max,def)=>{v=Number(v);return Number.isFinite(v)?Math.min(max,Math.max(min,Math.floor(v))):def};
let context={hotel:'',room:'',scenario:'',checkin:'',checkout:'',adults:2,children:[]};
try{const saved=JSON.parse(sessionStorage.getItem('turris-context')||'null');if(saved&&typeof saved==='object')context={...context,...saved};}catch{}
function normalize(){context.adults=clamp(context.adults,1,6,2);context.children=Array.isArray(context.children)?context.children.slice(0,4).map(n=>n===null||n===''||!Number.isInteger(Number(n))||Number(n)<0||Number(n)>17?null:Number(n)):[];if(!validDate(context.checkin)||context.checkin<today()||!validDate(context.checkout)||context.checkout<=context.checkin){context.checkin='';context.checkout='';}}
if(!context.guestAgesConfirmed)context.children=(context.children||[]).map(n=>Number(n)===0?null:n);
normalize();
function save(){try{sessionStorage.setItem('turris-context',JSON.stringify(context));}catch{}}
function guestLabel(adults,children){return `${adults} ${adults===1?'взрослый':'взрослых'}`+(children.length?`, ${children.length} ${children.length===1?'ребёнок':children.length<5?'ребёнка':'детей'}`:'');}
function setForm(form){
 const hotel=form.dataset.hotel||context.hotel||'',select=$('[name=hotel]',form);if(select)select.value=[...select.options].some(o=>o.value===hotel)?hotel:select.options[0].value;
 $('[name=checkin]',form).value=context.checkin;$('[name=checkout]',form).value=context.checkout;
 if(document.body.dataset.template==='booking')$('[name=room]',form).value=context.room||'';
 $('[name=adults]',form).value=context.adults;$('[name=children]',form).value=JSON.stringify(context.children);
 $('[data-date-label]',form).textContent=context.checkin?`${fmt(context.checkin)} — ${fmt(context.checkout)}`:'Выберите даты';
 $('[data-guest-label]',form).textContent=guestLabel(context.adults,context.children);
}
function syncForms(){$$('[data-booking]').forEach(setForm);document.dispatchEvent(new CustomEvent('booking-context-change',{detail:{...context}}));}
const params=new URLSearchParams(location.search);
if(document.body.dataset.page==='booking'||document.body.dataset.page.endsWith('_booking')){
 if(params.has('hotel')&&!params.has('room'))context.room='';
 if(params.has('hotel')&&!params.has('scenario'))context.scenario='';
 for(const k of ['hotel','room','scenario','checkin','checkout'])if(params.has(k))context[k]=params.get(k);
 if(params.has('adults'))context.adults=params.get('adults');
 if(params.has('children'))try{context.children=JSON.parse(params.get('children'));}catch{context.children=[];}
 const preset=$('[data-booking]')?.dataset.hotel;
 if(preset&&!params.has('hotel')){if(context.hotel!==preset)context.room='';context.hotel=preset;}
 if(params.has('hotel')&&$('[data-booking]'))$('[data-booking]').dataset.hotel=context.hotel;
 normalize();save();
}
if($('[data-scenario=family]')&&!['tverskaya','lubyansky'].includes(context.hotel)){context.hotel='';context.room='';save();}
syncForms();
document.addEventListener('booking-guests-change',ev=>{context.adults=ev.detail.adults;context.children=[...ev.detail.children];context.guestAgesConfirmed=true;normalize();save();syncForms();});
let activeForm=null,returnFocus=null,guestDraft={adults:2,children:[]};
function open(dialog,trigger){returnFocus=trigger;dialog.showModal();}
$$('[data-close]').forEach(b=>b.addEventListener('click',()=>b.closest('dialog').close()));
$$('dialog').forEach(d=>{d.addEventListener('click',ev=>{if(ev.target===d){const r=d.getBoundingClientRect();if(ev.clientX<r.left||ev.clientX>r.right||ev.clientY<r.top||ev.clientY>r.bottom)d.close();}});d.addEventListener('close',()=>{if(returnFocus&&document.contains(returnFocus))returnFocus.focus();});});
$$('[data-dates]').forEach(b=>b.addEventListener('click',()=>{
 activeForm=b.closest('form');const d=$('#dates-dialog'),f=$('#dates-form');$('[name=checkin]',f).min=today();$('[name=checkin]',f).value=context.checkin;$('[name=checkout]',f).value=context.checkout;$('[name=checkout]',f).min=context.checkin?addDay(context.checkin):addDay(today());$('.form-error',f).textContent='';open(d,b);
}));
$('[name=checkin]',$('#dates-form')).addEventListener('change',ev=>{$('[name=checkout]',$('#dates-form')).min=addDay(ev.target.value||today());});
$('#dates-form').noValidate=true;
$('#dates-form').addEventListener('submit',ev=>{ev.preventDefault();const f=ev.currentTarget,start=f.elements.checkin.value,end=f.elements.checkout.value;if(!validDate(start)||!validDate(end)||start<today()||end<=start){f.elements.checkin.setAttribute('aria-invalid',String(!validDate(start)||start<today()));f.elements.checkout.setAttribute('aria-invalid',String(!validDate(end)||end<=start));$('.form-error',f).textContent='Выезд должен быть позже заезда. Выберите даты не раньше сегодняшнего дня.';return;}f.elements.checkin.removeAttribute('aria-invalid');f.elements.checkout.removeAttribute('aria-invalid');context.checkin=start;context.checkout=end;save();syncForms();if(activeForm)$('.form-error',activeForm).textContent='';$('#dates-dialog').close();});
function renderGuests(){
 $('[data-count-value=adults]').textContent=guestDraft.adults;$('[data-count-value=children]').textContent=guestDraft.children.length;
 $('.ages').innerHTML=guestDraft.children.map((age,i)=>`<label class="field">Возраст ребёнка ${i+1}<select data-age="${i}" aria-label="Возраст ребёнка ${i+1}"><option value="" ${age===null?'selected':''}>Укажите возраст</option>${Array.from({length:18},(_,n)=>`<option value="${n}" ${n===age?'selected':''}>${n===0?'До года':n+' '+(n===1?'год':n<5?'года':'лет')}</option>`).join('')}</select></label>`).join('');
 $$('[data-age]').forEach(s=>s.addEventListener('change',()=>{guestDraft.children[+s.dataset.age]=s.value===''?null:+s.value;s.removeAttribute('aria-invalid');}));
 $$('[data-count]').forEach(b=>{const isAdult=b.dataset.count==='adults',n=isAdult?guestDraft.adults:guestDraft.children.length;b.disabled=+b.dataset.change<0?n<=(isAdult?1:0):n>=(isAdult?6:4);});
}
$$('[data-guests]').forEach(b=>b.addEventListener('click',()=>{activeForm=b.closest('form');guestDraft={adults:context.adults,children:[...context.children]};renderGuests();$('#guests-error').textContent=context.children.some(n=>n===null)?'Подтвердите возраст каждого ребёнка, включая вариант «До года».':'';open($('#guests-dialog'),b);}));
$$('[data-count]').forEach(b=>b.addEventListener('click',()=>{const change=+b.dataset.change;if(b.dataset.count==='adults')guestDraft.adults=clamp(guestDraft.adults+change,1,6,2);else if(change>0&&guestDraft.children.length<4)guestDraft.children.push(null);else if(change<0)guestDraft.children.pop();renderGuests();}));
$('[data-save-guests]').addEventListener('click',()=>{const missing=guestDraft.children.findIndex(n=>n===null);if(missing!==-1){$('#guests-error').textContent='Укажите возраст ребёнка '+(missing+1)+' на дату заезда.';const field=$('[data-age="'+missing+'"]');field.setAttribute('aria-invalid','true');field.setAttribute('aria-describedby','guests-error');field.focus();return;}context.guestAgesConfirmed=true;context.adults=guestDraft.adults;context.children=[...guestDraft.children];save();syncForms();$('#guests-dialog').close();});
$$('[data-booking]').forEach(f=>{
 $('[name=hotel]',f).addEventListener('change',ev=>{const preset=f.dataset.hotel||'',room=$('[name=room]',f);if(ev.target.value!==preset&&room.value){room.value='';f.dataset.room='';$('.form-error',f).textContent='Выбран другой отель. Категория сброшена — выберите подходящий номер в результатах.';}context.hotel=ev.target.value;context.room=room.value;if(context.scenario==='family'&&!['','tverskaya','lubyansky'].includes(context.hotel))context.scenario='';if(context.scenario==='offer_four'&&!['','lubyansky','tagansky'].includes(context.hotel))context.scenario='';$$('[data-booking]').forEach(other=>{other.dataset.hotel=context.hotel;if(other!==f){other.dataset.room='';$('[name=room]',other).value='';}});save();syncForms();});
 f.addEventListener('submit',async ev=>{ev.preventDefault();if(context.children.some(n=>n===null)){$('.form-error',f).textContent='Укажите возраст каждого ребёнка.';$('[data-guests]',f).click();return;}if(document.body.dataset.template==='booking'&&!f.elements.hotel.value){$('.form-error',f).textContent='Выберите отель, чтобы посмотреть его категории номеров.';f.elements.hotel.focus();return;}if(!context.checkin||!context.checkout){$('.form-error',f).textContent='Выберите даты поездки.';$('[data-dates]',f).click();return;}
 $('.form-error',f).textContent='';const data=new FormData(f);context={...context,hotel:String(data.get('hotel')||''),room:String(data.get('room')||''),scenario:document.body.dataset.template==='booking'?context.scenario:(f.dataset.scenario||'')};save();const q=new URLSearchParams({hotel:context.hotel,room:context.room,checkin:context.checkin,checkout:context.checkout,adults:String(context.adults),children:JSON.stringify(context.children)});if(context.scenario)q.set('scenario',context.scenario);if(document.body.dataset.template==='booking'){history.replaceState(null,'',location.pathname+'?'+q.toString());await bookingResults();const result=$('#booking-results');result.scrollIntoView({block:'start',behavior:'instant'});result.focus({preventScroll:true});}else location.href=base+'/bronirovanie/?'+q.toString();});
});
$$('[data-demo-info]').forEach(b=>b.addEventListener('click',()=>open($('#demo-dialog'),b)));
$$('[data-lightbox]').forEach(b=>b.addEventListener('click',()=>{const im=$('img',b),target=$('#lightbox-dialog img');target.src=im.src;target.alt=im.alt;open($('#lightbox-dialog'),b);}));
const filter=$('[data-hotel-filter]');$('[data-reset-hotels]')?.addEventListener('click',()=>{filter.value='all';filter.dispatchEvent(new Event('change'));filter.focus();});if(filter)filter.addEventListener('change',()=>{const ids=filter.value==='family'?['tverskaya','lubyansky']:filter.value==='longstay'?['petrovsky']:filter.value==='beds'?['tverskaya','lubyansky','tagansky']:['tverskaya','lubyansky','petrovsky','tagansky'];$$('[data-hotel-card]').forEach(card=>card.hidden=!ids.includes(card.dataset.hotelCard));if($('[data-reset-hotels]'))$('[data-reset-hotels]').hidden=filter.value==='all';document.dispatchEvent(new CustomEvent('hotel-filter-change',{detail:ids}));$('[data-filter-count]').textContent=`${ids.length} ${ids.length===1?'отель':'отеля'} · наличие проверяется отдельно`;});
let blogRubric='all';
function filterBlog(){const norm=s=>s.toLocaleLowerCase('ru').replaceAll('ё','е');const term=norm(($('[data-blog-search]')?.value||'').trim());const terms=term.split(/\s+/).filter(Boolean);let count=0;$$('[data-article]').forEach(card=>{const visible=(blogRubric==='all'||card.dataset.rubric===blogRubric)&&terms.every(t=>norm(card.dataset.title).includes(t));card.hidden=!visible;if(visible)count++;});if($('[data-blog-empty]'))$('[data-blog-empty]').hidden=count>0;if($('[data-blog-count]'))$('[data-blog-count]').textContent='Материалов: '+count;if($('[data-blog-reset]'))$('[data-blog-reset]').hidden=!term&&blogRubric==='all';}
$$('[data-rubric-filter]').forEach(b=>b.addEventListener('click',()=>{blogRubric=b.dataset.rubricFilter;$$('[data-rubric-filter]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));filterBlog();}));
$('[data-blog-search]')?.addEventListener('input',filterBlog);
$('[data-blog-reset]')?.addEventListener('click',()=>{blogRubric='all';$('[data-blog-search]').value='';$$('[data-rubric-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.rubricFilter==='all')));filterBlog();$('[data-blog-search]').focus();});
$$('[data-lead]').forEach(f=>{
 f.noValidate=true;const start=f.elements.arrival,end=f.elements.departure;start.min=today();end.min=addDay(today());start.addEventListener('change',()=>end.min=addDay(start.value||today()));
 function error(text){$('.form-error',f).textContent=text;}
 function step(n){$$('[data-step]',f).forEach(el=>el.hidden=+el.dataset.step!==n);$$('[data-step-label]',f).forEach(el=>el.classList.toggle('current',+el.dataset.stepLabel===n));error('');if(n===2)f.elements.name.focus();}
 $('[data-next-step]',f).addEventListener('click',()=>{for(const input of $$('[data-step="1"] input',f)){if(!input.reportValidity())return;}if(!validDate(start.value)||!validDate(end.value)||end.value<=start.value||start.value<today()){error('Проверьте даты: выезд должен быть позже заезда.');return;}step(2);});
 $('[data-prev-step]',f).addEventListener('click',()=>step(1));
 f.addEventListener('submit',ev=>{ev.preventDefault();if(!$('[data-step="1"]',f).hidden){$('[data-next-step]',f).click();return;}if(!f.elements.name.value.trim()){error('Введите демонстрационное имя.');f.elements.name.focus();return;}if(!f.elements.email.value||!f.elements.email.reportValidity()){error('Укажите email в правильном формате. Для демонстрации можно использовать name@example.com.');return;}if(!f.elements.consent.checked){error('Подтвердите, что понимаете демонстрационный режим.');return;}
 const result=document.createElement('div');result.className='form-success';result.setAttribute('role','status');result.innerHTML=`<h3>Всё готово для расчёта</h3><p>${esc(fmt(start.value))} — ${esc(fmt(end.value))}<br>Гостей: ${esc(f.elements.guests.value)} · Комнат: ${esc(f.elements.rooms.value)}</p><p><strong>Это демонстрация. Заявка не отправлена, номера не забронированы.</strong></p><p>Для настоящего запроса позвоните <a href="tel:88005054455">8 800 505 44 55</a>.</p><button type="button" class="btn secondary" data-reset-lead>Попробовать ещё раз</button>`;f.hidden=true;f.after(result);$('[data-reset-lead]',result).addEventListener('click',()=>{result.remove();f.hidden=false;f.reset();step(1);});});
});

document.addEventListener('click',ev=>{const link=ev.target.closest('[data-trip-hotel]');if(!link||ev.ctrlKey||ev.metaKey||ev.shiftKey)return;ev.preventDefault();context.hotel=link.dataset.tripHotel;context.room='';save();syncForms();const q=new URLSearchParams({hotel:context.hotel,checkin:context.checkin,checkout:context.checkout,adults:String(context.adults),children:JSON.stringify(context.children)});location.href=base+'/bronirovanie/?'+q;});

let dataPromise;const getData=()=>dataPromise||(dataPromise=fetch(base+'/site-data.json').then(r=>{if(!r.ok)throw new Error('data unavailable');return r.json();}));
let bookingRequest=0,disposeBooking=()=>{};
const chooseHotelMessage='<section class="empty-state"><h2>Сначала выберите отель</h2><p>Покажем номера и цены только выбранного отеля. Даты и гости сохранены.</p><button class="btn secondary" type="button" data-booking-choose-hotel>Выбрать отель</button></section>';
function resetBooking(){bookingRequest++;disposeBooking();disposeBooking=()=>{};$$('.bk-steps li').forEach((li,i)=>{if(!i)li.setAttribute('aria-current','step');else li.removeAttribute('aria-current');});}
async function bookingResults(){const root=$('#booking-results');if(!root)return;resetBooking();const request=bookingRequest;
 if(!context.checkin){root.innerHTML='';return;}if(context.children.some(n=>n===null)){root.hidden=false;root.innerHTML='<p class="notice">Подтвердите возраст детей в поле «Гости», затем покажем номера и цены.</p>';return;}root.hidden=false;
 if(!context.hotel){root.innerHTML=chooseHotelMessage;document.dispatchEvent(new Event('booking-results-updated'));return;}
 root.innerHTML='<p class="small" style="padding:25px 0">Подключаем бронирование отеля…</p>';
 try{
  const data=await getData();if(request!==bookingRequest)return;
  if(!Object.hasOwn(data.hotels,context.hotel)){root.innerHTML=chooseHotelMessage;document.dispatchEvent(new Event('booking-results-updated'));return;}
  const hotel=data.hotels[context.hotel],selected=data.pages.find(p=>p.type==='room'&&p.hotel===context.hotel&&p.id===context.room);
  const nights=Math.round((Date.parse(context.checkout+'T00:00:00Z')-Date.parse(context.checkin+'T00:00:00Z'))/86400000);
  const q=new URLSearchParams({date:context.checkin,nights:String(nights),adults:String(context.adults),children:String(context.children.length)});
  if(context.children.length)q.set('children-age',context.children.join(','));
  const promo=$('#booking-promo')?.value.trim()||(()=>{try{return sessionStorage.getItem('turris-promo')||'';}catch{return '';}})();
  if(promo)q.set('promo-code-plain',promo.slice(0,40));
  const official='https://turris.online/hotels/'+hotel.slug+'/booking/?'+q.toString();
  const widgetQuery=new URLSearchParams(q);widgetQuery.set('hotel',context.hotel);
  root.innerHTML=`<section class="bk-live" data-live-hotel="${esc(context.hotel)}"><div class="bk-live-heading"><div><span class="bk-live-label">БРОНИРОВАНИЕ · TRAVELLINE</span><h2>Номера и цены · ${esc(hotel.name)}</h2><p>Выберите номер, затем тариф. Полная стоимость и условия — до оформления.</p></div><a href="#booking-search" class="text-link">Изменить поиск ↑</a></div>${selected?'<p class="bk-live-room">Вы смотрели: <strong>'+esc(selected.title)+'</strong>. Выберите эту категорию в модуле, если она доступна на ваши даты.</p>':''}<p class="bk-live-info">Это действующий модуль отеля. Оформление и оплата реальны. Даты и гостей можно изменить внутри модуля; итоговые параметры проверяйте в нём.</p><div class="bk-live-status" role="status" data-live-status><span class="bk-loader" aria-hidden="true"></span><span>Загружаем номера и тарифы отеля…</span></div><div class="bk-live-stage"><iframe class="bk-live-frame" title="Номера, тарифы и бронирование — ${esc(hotel.full)}" src="${base}/assets/booking-widget.html?${esc(widgetQuery.toString())}" allow="payment" referrerpolicy="strict-origin-when-cross-origin"></iframe></div><div class="bk-live-recovery"><p>Модуль не открылся или неудобно продолжать?</p><div><button type="button" class="btn secondary" data-retry-results>Загрузить снова</button><a class="btn secondary" data-official-booking href="${esc(official)}" target="_blank" rel="noopener noreferrer">Открыть на сайте отеля ↗</a></div><small>Передадим отель, даты, состав гостей и промокод. Доступность и скидка проверяются отелем.</small></div></section>`;
  const frame=$('.bk-live-frame',root),status=$('[data-live-status]',root);let loaded=false;
  function message(event){if(event.origin!==location.origin||event.source!==frame.contentWindow||event.data?.source!=='turris-booking'||request!==bookingRequest)return;
   const msg=event.data;
   if(msg.type==='height'&&Number.isFinite(msg.height)&&msg.height>0)frame.style.height=Math.min(30000,Math.max(500,msg.height))+'px';
   if(msg.type==='ready'){loaded=true;clearTimeout(timer);status.hidden=true;frame.classList.add('is-ready');}
   if(msg.type==='error'){clearTimeout(timer);status.textContent='Не удалось подключить модуль. Попробуйте ещё раз или откройте бронирование на сайте отеля.';}
   if(msg.type==='empty'){status.hidden=false;status.textContent='На эти параметры нет предложений. Измените даты или состав гостей в модуле либо выберите другой отель.';}
   if(msg.type==='step'){const step={search:0,preview:1,payment:1,complete:2}[msg.step];if(step!==undefined){$$('.bk-steps li').forEach((li,i)=>{if(i===step)li.setAttribute('aria-current','step');else li.removeAttribute('aria-current');});if(loaded&&step>0)frame.scrollIntoView({block:'start',behavior:'instant'});}}
  }
  const timer=setTimeout(()=>{status.hidden=false;status.textContent='Загрузка занимает больше обычного. Можно подождать или продолжить на сайте отеля по ссылке ниже.';},25000);
  window.addEventListener('message',message);disposeBooking=()=>{clearTimeout(timer);window.removeEventListener('message',message);};
  $('[data-retry-results]',root).addEventListener('click',bookingResults);
 }catch{if(request!==bookingRequest)return;root.innerHTML='<div class="empty-state"><h3>Не удалось подключить бронирование</h3><p>Ваши даты сохранены. Повторите попытку или позвоните <a href="tel:88005054455">8 800 505 44 55</a>.</p><button class="btn secondary" data-retry-results>Попробовать снова</button></div>';$('[data-retry-results]',root).addEventListener('click',()=>{dataPromise=null;bookingResults();});}
 document.dispatchEvent(new Event('booking-results-updated'));
}
document.addEventListener('booking-context-change',()=>{resetBooking();const root=$('#booking-results');if(root){root.replaceChildren();root.hidden=true;}});
document.addEventListener('booking-query-invalidated',()=>{resetBooking();const root=$('#booking-results');if(root){root.replaceChildren();root.hidden=true;}});
document.addEventListener('booking-clear-room',async()=>{context.room='';$$('[data-booking]').forEach(f=>{f.dataset.room='';$('[name=room]',f).value='';});save();syncForms();const q=new URLSearchParams(location.search);q.delete('room');history.replaceState(null,'',location.pathname+(q.size?'?'+q.toString():''));await bookingResults();});
bookingResults();
const search=$('[data-site-search]');if(search){const input=$('[name=q]',search),root=$('[data-search-results]');input.value=params.get('q')||'';
 async function run(){const query=input.value.trim();if(!query){root.innerHTML='<p class="muted">Введите название отеля, тип номера или ваш вопрос.</p>';return;}root.innerHTML='<p class="muted">Ищем страницы…</p>';try{const data=await getData(),terms=query.toLocaleLowerCase('ru').split(/\s+/);const rows=data.pages.filter(p=>!['utility','booking','legal'].includes(p.type)&&terms.every(t=>(p.title+' '+p.summary).toLocaleLowerCase('ru').includes(t)));root.innerHTML=rows.length?`<p class="small">Найдено страниц: ${rows.length}</p>`+rows.map(p=>`<a class="search-result" href="${base+esc(p.url)}"><h3>${esc(p.title)}</h3><p>${esc(p.summary)}</p></a>`).join(''):'<div class="empty-state"><h3>Ничего не найдено</h3><p>Попробуйте более короткий запрос: «дети», «мансарда» или название отеля.</p><a class="btn secondary" href="'+base+'/help/">Открыть помощь</a></div>';}catch{root.innerHTML='<p class="muted">Поиск временно недоступен. Перейдите к разделам через меню.</p>';}}
 search.addEventListener('submit',ev=>{ev.preventDefault();history.replaceState(null,'',location.pathname+'?q='+encodeURIComponent(input.value));run();});run();}
})();
