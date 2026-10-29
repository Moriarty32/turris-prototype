/* One keyboard/touch navigation and one restrained motion system. */
(()=>{'use strict';document.documentElement.classList.add('ux-ready');
const header=document.querySelector('.ux-header'),inner=header.querySelector('.header-inner'),nav=header.querySelector('.nav'),button=header.querySelector('.menu-button'),mobile=matchMedia('(max-width:1100px)'),motion=matchMedia('(prefers-reduced-motion:reduce)'),groups=[...nav.querySelectorAll('details')];
const pageContent=[document.querySelector('main'),document.querySelector('.footer')];
function setMenu(open,restore=false){inner.classList.toggle('menu-open',open);button.setAttribute('aria-expanded',String(open));button.setAttribute('aria-label',open?'Закрыть меню':'Открыть меню');document.body.classList.toggle('ux-menu-open',open&&mobile.matches);pageContent.forEach(e=>{if(e)e.inert=open&&mobile.matches;});if(!open)groups.forEach(g=>g.open=false);if(restore)button.focus();}
button.addEventListener('click',()=>setMenu(!inner.classList.contains('menu-open')));
groups.forEach(group=>group.addEventListener('toggle',()=>{if(group.open)groups.forEach(other=>{if(other!==group)other.open=false;});}));
nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>setMenu(false)));
document.addEventListener('click',e=>{if(!header.contains(e.target))setMenu(false);});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){const open=groups.find(g=>g.open);if(inner.classList.contains('menu-open')){setMenu(false,true);e.preventDefault();}else if(open){open.open=false;open.querySelector('summary').focus();e.preventDefault();}}
if(e.key==='Tab'&&mobile.matches&&inner.classList.contains('menu-open')){const focusable=[...header.querySelectorAll('a,button,summary')].filter(el=>el.getClientRects().length),first=focusable[0],last=focusable.at(-1);if(e.shiftKey&&document.activeElement===first){last.focus();e.preventDefault();}else if(!e.shiftKey&&document.activeElement===last){first.focus();e.preventDefault();}}});
header.addEventListener('focusout',()=>requestAnimationFrame(()=>{if(!mobile.matches&&!header.contains(document.activeElement))setMenu(false);}));
mobile.addEventListener('change',()=>setMenu(false));
function headerSize(){document.documentElement.style.setProperty('--ux-header-height',Math.ceil(header.getBoundingClientRect().height)+'px');}
new ResizeObserver(headerSize).observe(header);headerSize();
const targets='main .section-heading, main .ct-section>h2, main .of-section>h2, main .ar-section>h2, main .hd-section>h2, main .benefit, main .feature, main .guide-tip, main .ct-topics article, main .of-conditions article';
if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){if(!motion.matches)entry.target.classList.add('ux-enter');observer.unobserve(entry.target);}}),{threshold:.12});document.querySelectorAll(targets).forEach(el=>{if(el.getBoundingClientRect().top>innerHeight)observer.observe(el);});}
})();
