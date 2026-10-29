/* Turris demonstration. No payment, CRM submission, tracking or personal-data storage. */
(()=>{'use strict';
const base=window.SITE_BASE||'', $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const today=()=>{const d=new Date();return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`};
const addDay=s=>{const d=new Date(s+'T12:00:00');d.setDate(d.getDate()+1);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`};
const validDate=s=>/^\d{4}-\d{2}-\d{2}$/.test(s||'')&&!Number.isNaN(new Date(s+'T12:00:00').getTime());
const fmt=s=>validDate(s)?new Date(s+'T12:00:00').toLocaleDateString('ru-RU',{day:'numeric',month:'short'}):'';
const clamp=(v,min,max,def)=>{v=Number(v);return Number.isFinite(v)?Math.min(max,Math.max(min,Math.floor(v))):def};
let context={hotel:'',room:'',checkin:'',checkout:'',adults:2,children:[]};
try{const saved=JSON.parse(sessionStorage.getItem('turris-context')||'null');if(saved&&typeof saved==='object')context={...context,...saved};}catch{}
function normalize(){context.adults=clamp(context.adults,1,6,2);context.children=Array.isArray(context.children)?context.children.slice(0,4).map(n=>clamp(n,0,17,0)):[];if(!validDate(context.checkin)||context.checkin<today()||!validDate(context.checkout)||context.checkout<=context.checkin){context.checkin='';context.checkout='';}}
normalize();
function save(){try{sessionStorage.setItem('turris-context',JSON.stringify(context));}catch{}}
function guestLabel(adults,children){return `${adults} ${adults===1?'взрослый':'взрослых'}`+(children.length?`, ${children.length} ${children.length===1?'ребёнок':children.length<5?'ребёнка':'детей'}`:'');}
function setForm(form){
 const hotel=form.dataset.hotel||context.hotel||'';if($('[name=hotel]',form))$('[name=hotel]',form).value=hotel;
 $('[name=checkin]',form).value=context.checkin;$('[name=checkout]',form).value=context.checkout;
 if(document.body.dataset.template==='booking')$('[name=room]',form).value=context.room||'';
 $('[name=adults]',form).value=context.adults;$('[name=children]',form).value=JSON.stringify(context.children);
 $('[data-date-label]',form).textContent=context.checkin?`${fmt(context.checkin)} — ${fmt(context.checkout)}`:(document.body.dataset.template==='booking'?'Выберите даты':'Заезд — Выезд');
 $('[data-guest-label]',form).textContent=guestLabel(context.adults,context.children);
}
function syncForms(){$$('[data-booking]').forEach(setForm);document.dispatchEvent(new CustomEvent('booking-context-change',{detail:{...context}}));}
const params=new URLSearchParams(location.search);
if(document.body.dataset.page==='booking'||document.body.dataset.page.endsWith('_booking')){
 if(params.has('hotel')&&!params.has('room'))context.room='';
 for(const k of ['hotel','room','checkin','checkout'])if(params.has(k))context[k]=params.get(k);
 if(params.has('adults'))context.adults=params.get('adults');
 if(params.has('children'))try{context.children=JSON.parse(params.get('children'));}catch{context.children=[];}
 const preset=$('[data-booking]')?.dataset.hotel;
 if(preset&&!params.has('hotel')){if(context.hotel!==preset)context.room='';context.hotel=preset;}
 if(params.has('hotel')&&$('[data-booking]'))$('[data-booking]').dataset.hotel=context.hotel;
 normalize();save();
}
syncForms();
let activeForm=null,returnFocus=null,guestDraft={adults:2,children:[]};
function open(dialog,trigger){returnFocus=trigger;dialog.showModal();}
$$('[data-close]').forEach(b=>b.addEventListener('click',()=>b.closest('dialog').close()));
$$('dialog').forEach(d=>{d.addEventListener('click',ev=>{if(ev.target===d){const r=d.getBoundingClientRect();if(ev.clientX<r.left||ev.clientX>r.right||ev.clientY<r.top||ev.clientY>r.bottom)d.close();}});d.addEventListener('close',()=>{if(returnFocus&&document.contains(returnFocus))returnFocus.focus();});});
$$('[data-dates]').forEach(b=>b.addEventListener('click',()=>{
 activeForm=b.closest('form');const d=$('#dates-dialog'),f=$('#dates-form');$('[name=checkin]',f).min=today();$('[name=checkin]',f).value=context.checkin;$('[name=checkout]',f).value=context.checkout;$('[name=checkout]',f).min=context.checkin?addDay(context.checkin):addDay(today());$('.form-error',f).textContent='';open(d,b);
}));
$('[name=checkin]',$('#dates-form')).addEventListener('change',ev=>{$('[name=checkout]',$('#dates-form')).min=addDay(ev.target.value||today());});
$('#dates-form').addEventListener('submit',ev=>{ev.preventDefault();const f=ev.currentTarget,start=f.elements.checkin.value,end=f.elements.checkout.value;if(!validDate(start)||!validDate(end)||start<today()||end<=start){$('.form-error',f).textContent='Выезд должен быть позже заезда. Выберите даты не раньше сегодняшнего дня.';return;}context.checkin=start;context.checkout=end;save();syncForms();if(activeForm)$('.form-error',activeForm).textContent='';$('#dates-dialog').close();});
function renderGuests(){
 $('[data-count-value=adults]').textContent=guestDraft.adults;$('[data-count-value=children]').textContent=guestDraft.children.length;
 $('.ages').innerHTML=guestDraft.children.map((age,i)=>`<label class="field">Возраст ребёнка ${i+1}<select data-age="${i}" aria-label="Возраст ребёнка ${i+1}">${Array.from({length:18},(_,n)=>`<option value="${n}" ${n===age?'selected':''}>${n===0?'До года':n+' лет'}</option>`).join('')}</select></label>`).join('');
 $$('[data-age]').forEach(s=>s.addEventListener('change',()=>guestDraft.children[+s.dataset.age]=+s.value));
 $$('[data-count]').forEach(b=>{const isAdult=b.dataset.count==='adults',n=isAdult?guestDraft.adults:guestDraft.children.length;b.disabled=+b.dataset.change<0?n<=(isAdult?1:0):n>=(isAdult?6:4);});
}
$$('[data-guests]').forEach(b=>b.addEventListener('click',()=>{activeForm=b.closest('form');guestDraft={adults:context.adults,children:[...context.children]};renderGuests();open($('#guests-dialog'),b);}));
$$('[data-count]').forEach(b=>b.addEventListener('click',()=>{const change=+b.dataset.change;if(b.dataset.count==='adults')guestDraft.adults=clamp(guestDraft.adults+change,1,6,2);else if(change>0&&guestDraft.children.length<4)guestDraft.children.push(0);else if(change<0)guestDraft.children.pop();renderGuests();}));
$('[data-save-guests]').addEventListener('click',()=>{context.adults=guestDraft.adults;context.children=[...guestDraft.children];save();syncForms();$('#guests-dialog').close();});
$$('[data-booking]').forEach(f=>{
 $('[name=hotel]',f).addEventListener('change',ev=>{const preset=f.dataset.hotel||'',room=$('[name=room]',f);if(ev.target.value!==preset&&room.value){room.value='';f.dataset.room='';$('.form-error',f).textContent='Выбран другой отель. Категория сброшена — выберите подходящий номер в результатах.';}context.hotel=ev.target.value;context.room=room.value;$$('[data-booking]').forEach(other=>{other.dataset.hotel=context.hotel;if(other!==f){other.dataset.room='';$('[name=room]',other).value='';}});save();syncForms();});
 f.addEventListener('submit',async ev=>{ev.preventDefault();if(!context.checkin||!context.checkout){$('.form-error',f).textContent='Выберите даты поездки.';$('[data-dates]',f).click();return;}
 $('.form-error',f).textContent='';const data=new FormData(f);context={...context,hotel:String(data.get('hotel')||''),room:String(data.get('room')||'')};save();const q=new URLSearchParams({hotel:context.hotel,room:context.room,checkin:context.checkin,checkout:context.checkout,adults:String(context.adults),children:JSON.stringify(context.children)});if(document.body.dataset.template==='booking'){history.replaceState(null,'',location.pathname+'?'+q.toString());await bookingResults();const result=$('#booking-results');result.scrollIntoView({block:'start',behavior:'instant'});result.focus({preventScroll:true});}else location.href=base+'/bronirovanie/?'+q.toString();});
});
$$('[data-demo-info]').forEach(b=>b.addEventListener('click',()=>open($('#demo-dialog'),b)));
const menu=$('.menu-button'),header=$('.header-inner');
menu.addEventListener('click',()=>{const isOpen=header.classList.toggle('menu-open');menu.setAttribute('aria-expanded',String(isOpen));menu.setAttribute('aria-label',isOpen?'Закрыть меню':'Открыть меню');});
$$('.nav details').forEach(d=>d.addEventListener('toggle',()=>{if(d.open)$$('.nav details').forEach(x=>{if(x!==d)x.open=false;});}));
document.addEventListener('keydown',ev=>{if(ev.key==='Escape'){header.classList.remove('menu-open');menu.setAttribute('aria-expanded','false');$$('.nav details').forEach(d=>d.open=false);}});
document.addEventListener('click',ev=>{if(!ev.target.closest('.header')){$$('.nav details').forEach(d=>d.open=false);header.classList.remove('menu-open');menu.setAttribute('aria-expanded','false');}});
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
let dataPromise;const getData=()=>dataPromise||(dataPromise=fetch(base+'/site-data.json').then(r=>{if(!r.ok)throw new Error('data unavailable');return r.json();}));
async function bookingResults(){const root=$('#booking-results');if(!root)return;
 if(!context.checkin){root.innerHTML='';return;}
 root.hidden=false;
 root.innerHTML='<p class="small" style="padding:25px 0">Подбираем страницы категорий…</p>';
 try{const data=await getData();let list=data.pages.filter(p=>p.type==='room'&&(!context.hotel||p.hotel===context.hotel));const selected=list.find(p=>p.id===context.room);if(context.room&&!selected){context.room='';save();syncForms();}if(selected)list=[selected];
 const hotel=data.hotels[context.hotel],title=selected?'Ваш выбранный номер':hotel?'Категории отеля '+hotel.full:'Категории четырёх отелей';
 const selectedNote=selected?'<p class="small">Выбранная категория сохранена. Перед реальным оформлением повторно проверьте её в официальном модуле.</p>':'';
 root.innerHTML=`<section class="section"><h2>${esc(title)}</h2><div class="results-summary"><span>${esc(fmt(context.checkin))} — ${esc(fmt(context.checkout))}</span><span>${esc(guestLabel(context.adults,context.children))}</span>${context.children.length?'<span>Возраст детей: '+context.children.map(n=>esc(n)).join(', ')+'</span>':''}</div>${selectedNote}<div class="notice">Это категории для ознакомления, а не подтверждённое наличие. Итоговая цена, допустимый состав гостей и условия тарифа проверяются на официальном сайте.</div><div class="rooms-grid">${list.map(p=>{
 const h=data.hotels[p.hotel],nights=Math.round((new Date(context.checkout+'T12:00:00')-new Date(context.checkin+'T12:00:00'))/86400000);const q=new URLSearchParams({date:context.checkin,nights:String(nights),adults:String(context.adults)});const official='https://turris.online'+p.url+'?'+q.toString();
 return `<article class="room-card"><a href="${base+esc(p.url)}"><img src="${base}/assets/${esc(p.image)}" alt="${esc(p.title)}" loading="lazy"></a><div class="room-body"><div class="eyebrow">${esc(h.name)}</div><h3><a href="${base+esc(p.url)}">${esc(p.title)}</a></h3><p>Цена и наличие уточняются на официальном сайте. Состав гостей, возраст детей и категория требуют проверки при оформлении.</p><a class="btn secondary" href="${esc(official)}" target="_blank" rel="noopener noreferrer">Проверить на сайте отеля ↗</a></div></article>`;}).join('')}</div>${!list.length?'<div class="empty-state"><h3>Выберите другой отель</h3><p>Не удалось сопоставить выбранную категорию. Измените фильтр в форме выше.</p></div>':''}</section>`;
 }catch{root.innerHTML='<div class="empty-state"><h3>Не удалось загрузить категории</h3><p>Обновите страницу или выберите отель ниже. Ваши даты сохранены.</p><button class="btn secondary" data-retry-results>Попробовать снова</button></div>';$('[data-retry-results]').addEventListener('click',()=>{dataPromise=null;bookingResults();});}
 document.dispatchEvent(new Event('booking-results-updated'));
}
document.addEventListener('booking-clear-room',async()=>{context.room='';$$('[data-booking]').forEach(f=>{f.dataset.room='';$('[name=room]',f).value='';});save();syncForms();const q=new URLSearchParams(location.search);q.delete('room');history.replaceState(null,'',location.pathname+(q.size?'?'+q.toString():''));await bookingResults();});
bookingResults();
const search=$('[data-site-search]');if(search){const input=$('[name=q]',search),root=$('[data-search-results]');input.value=params.get('q')||'';
 async function run(){const query=input.value.trim();if(!query){root.innerHTML='<p class="muted">Введите название отеля, тип номера или ваш вопрос.</p>';return;}root.innerHTML='<p class="muted">Ищем страницы…</p>';try{const data=await getData(),terms=query.toLocaleLowerCase('ru').split(/\s+/);const rows=data.pages.filter(p=>!['utility','booking','legal'].includes(p.type)&&terms.every(t=>(p.title+' '+p.summary).toLocaleLowerCase('ru').includes(t)));root.innerHTML=rows.length?`<p class="small">Найдено страниц: ${rows.length}</p>`+rows.map(p=>`<a class="search-result" href="${base+esc(p.url)}"><h3>${esc(p.title)}</h3><p>${esc(p.summary)}</p></a>`).join(''):'<div class="empty-state"><h3>Ничего не найдено</h3><p>Попробуйте более короткий запрос: «дети», «мансарда» или название отеля.</p><a class="btn secondary" href="'+base+'/help/">Открыть помощь</a></div>';}catch{root.innerHTML='<p class="muted">Поиск временно недоступен. Перейдите к разделам через меню.</p>';}}
 search.addEventListener('submit',ev=>{ev.preventDefault();history.replaceState(null,'',location.pathname+'?q='+encodeURIComponent(input.value));run();});run();}
})();
