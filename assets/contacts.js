/* Selection and demo submission stay in this page; no messages or PII are sent. */
(()=>{'use strict';const page=document.querySelector('.contacts-page');if(!page)return;
const root=page.querySelector('[data-hotel-map]'),choices=root.querySelector('.map-choices'),panels=root.querySelector('.map-details'),mobile=matchMedia('(max-width:640px)'),form=page.querySelector('[data-contact-form]');
const items=[...root.querySelectorAll('[data-map-select]')].map(button=>{const id=button.dataset.mapSelect,panel=root.querySelector('[data-map-detail="'+id+'"]'),photo=panel.querySelector('.ct-hotel-photo'),wrapper=document.createElement('div');wrapper.className='ct-map-item';panel.id='contact-map-'+id;button.setAttribute('aria-controls',panel.id);return{button,panel,photo,wrapper};});
function sync(){items.forEach(({button,panel,photo})=>{button.setAttribute('aria-expanded',String(!panel.hidden));if(photo.hidden!==panel.hidden)photo.hidden=panel.hidden;});}
function arrange(){panels.classList.toggle('ct-map-accordion',!mobile.matches);items.forEach(({button,panel,photo,wrapper})=>{if(mobile.matches){choices.append(button);panel.prepend(photo);panels.append(panel);wrapper.remove();}else{wrapper.append(photo,button,panel);panels.append(wrapper);}});choices.hidden=!mobile.matches;sync();root.dispatchEvent(new Event('hotel-map-layout'));}
new MutationObserver(sync).observe(root,{subtree:true,attributes:true,attributeFilter:['hidden']});mobile.addEventListener('change',arrange);arrange();
root.addEventListener('hotel-map-selection',ev=>{form.elements.hotel.value=ev.detail.id;});
form.elements.hotel.addEventListener('change',()=>{if(form.elements.hotel.value)root.dispatchEvent(new CustomEvent('hotel-map-select',{detail:{id:form.elements.hotel.value,pan:false}}));});
const requested=new URLSearchParams(location.search).get('map-hotel');if(items.some(x=>x.button.dataset.mapSelect===requested))form.elements.hotel.value=requested;
const status=page.querySelector('[data-contact-copy-status]');let timer;
page.querySelectorAll('[data-contact-copy]').forEach(button=>button.addEventListener('click',async()=>{clearTimeout(timer);try{await navigator.clipboard.writeText(button.dataset.contactCopy);status.textContent='Скопировано: '+button.dataset.contactCopy;}catch{status.textContent='Скопируйте вручную: '+button.dataset.contactCopy;}timer=setTimeout(()=>status.textContent='',10000);}));
form.querySelector('fieldset').disabled=false;
const contact=form.elements.contact,message=form.elements.message,error=page.querySelector('#contact-error'),result=page.querySelector('[data-contact-result]');
[contact,message].forEach(input=>input.addEventListener('input',()=>{input.setCustomValidity('');error.textContent='';}));
form.addEventListener('submit',ev=>{ev.preventDefault();error.textContent='';contact.setCustomValidity('');message.setCustomValidity('');
const value=contact.value.trim(),digits=value.replace(/\D/g,'');
if(!(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)||(/^[+\d\s().-]+$/.test(value)&&digits.length>=10&&digits.length<=15)))contact.setCustomValidity('Укажите корректный email или телефон с кодом города.');
if(message.value.trim().length<10)message.setCustomValidity('Опишите вопрос: не менее 10 символов.');
if(!form.checkValidity()){error.textContent='Проверьте контакт, сообщение и согласие.';form.reportValidity();return;}
result.querySelector('[data-contact-result-text]').textContent='Тема: '+form.elements.topic.value+'. Отель: '+form.elements.hotel.selectedOptions[0].textContent+'.';form.hidden=true;result.hidden=false;result.focus();
});
page.querySelector('[data-contact-again]').addEventListener('click',()=>{result.hidden=true;form.hidden=false;form.elements.topic.focus();});
})();
