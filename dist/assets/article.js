/* Map disclosure shares Leaflet selection; the article keeps one live map. */
(()=>{'use strict';const article=document.querySelector('.article-page');if(!article)return;
const root=article.querySelector('[data-hotel-map]'),media=matchMedia('(max-width:640px)'),choices=root.querySelector('.map-choices'),details=root.querySelector('.map-details'),form=article.querySelector('[data-booking]');
const items=[...root.querySelectorAll('[data-map-select]')].map(button=>{const id=button.dataset.mapSelect,panel=root.querySelector('[data-map-detail="'+id+'"]'),wrapper=document.createElement('div');wrapper.className='home-map-item';panel.id='article-hotel-'+id;button.setAttribute('aria-controls',panel.id);return{button,panel,wrapper};});
function sync(){items.forEach(({button,panel})=>button.setAttribute('aria-expanded',String(!panel.hidden)));}
function arrange(){details.classList.toggle('home-map-accordion',!media.matches);items.forEach(({button,panel,wrapper})=>{if(media.matches){choices.append(button);details.append(panel);wrapper.remove();}else{wrapper.append(button,panel);details.append(wrapper);}});choices.hidden=!media.matches;sync();root.dispatchEvent(new Event('hotel-map-layout'));}
new MutationObserver(sync).observe(root,{subtree:true,attributes:true,attributeFilter:['hidden']});media.addEventListener('change',arrange);arrange();

function syncHotel(){if(items.some(({button})=>button.dataset.mapSelect===form.elements.hotel.value))root.dispatchEvent(new CustomEvent('hotel-map-select',{detail:{id:form.elements.hotel.value,pan:false}}));}
form.elements.hotel.addEventListener('change',syncHotel);document.addEventListener('booking-context-change',syncHotel);syncHotel();
function dateLabel(){if(!form.elements.checkin.value)form.querySelector('[data-date-label]').textContent='Выберите даты';}document.addEventListener('booking-context-change',dateLabel);dateLabel();

})();
