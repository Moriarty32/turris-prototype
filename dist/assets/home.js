/* A single live map: desktop accordion, mobile hotel tabs, shared selection. */
(()=>{'use strict';const root=document.querySelector('.home-page [data-hotel-map]');if(!root)return;
function dateLabels(){document.querySelectorAll('.home-page [data-booking]').forEach(form=>{if(!form.elements.checkin.value)form.querySelector('[data-date-label]').textContent='Выберите даты';});}document.addEventListener('booking-context-change',dateLabels);dateLabels();
const media=matchMedia('(max-width:640px)'),choices=root.querySelector('.map-choices'),details=root.querySelector('.map-details');
const items=[...root.querySelectorAll('[data-map-select]')].map(button=>{const id=button.dataset.mapSelect,panel=root.querySelector('[data-map-detail="'+id+'"]'),wrapper=document.createElement('div');wrapper.className='home-map-item';panel.id='home-map-'+id;button.setAttribute('aria-controls',panel.id);return{button,panel,wrapper};});
function arrange(){details.classList.toggle('home-map-accordion',!media.matches);items.forEach(({button,panel,wrapper})=>{if(media.matches){choices.append(button);details.append(panel);wrapper.remove();}else{wrapper.append(button,panel);details.append(wrapper);}});choices.hidden=!media.matches;sync();root.dispatchEvent(new Event('hotel-map-layout'));}
function sync(){items.forEach(({button,panel})=>button.setAttribute('aria-expanded',String(!panel.hidden)));}
new MutationObserver(sync).observe(root,{subtree:true,attributes:true,attributeFilter:['hidden']});media.addEventListener('change',arrange);arrange();
})();
