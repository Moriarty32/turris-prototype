/* Four explicit previews. All hotel links/content exist before enhancement. */
(()=>{'use strict';const root=document.querySelector('.home-page');if(!root)return;
const buttons=[...root.querySelectorAll('[data-preview-hotel]')],panels=[...root.querySelectorAll('[data-hotel-preview]')];
function preview(id,animate=false){buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.previewHotel===id)));panels.forEach(p=>{p.hidden=p.dataset.hotelPreview!==id;p.classList.remove('is-entering');if(!p.hidden&&animate){void p.offsetWidth;p.classList.add('is-entering');}});}
buttons.forEach(b=>b.addEventListener('click',()=>preview(b.dataset.previewHotel,true)));preview('tverskaya');
})();
