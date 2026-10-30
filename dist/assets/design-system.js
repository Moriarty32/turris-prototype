/* One disclosure controller. Mobile navigation isolates the background. */
(()=>{'use strict';document.documentElement.classList.add('ux-ready');
const header=document.querySelector('.ux-header'),nav=header.querySelector('.site-menu'),button=header.querySelector('.menu-button'),mobile=matchMedia('(max-width:767px)'),motion=matchMedia('(prefers-reduced-motion:reduce)');
let opened=false;nav.hidden=true;
function setMenu(value,restore=false){opened=value;nav.classList.toggle('is-open',value);nav.hidden=!value;nav.inert=!value;button.setAttribute('aria-expanded',String(value));button.setAttribute('aria-label',value?'Закрыть меню':'Открыть меню');button.querySelector('span').textContent=value?'Закрыть':'Меню';document.body.classList.toggle('ux-menu-open',value&&mobile.matches);window.turrisModalBackground?.(header,value&&mobile.matches);if(value&&mobile.matches){header.setAttribute('role','dialog');header.setAttribute('aria-modal','true');header.setAttribute('aria-label','Меню сайта');}else{header.removeAttribute('role');header.removeAttribute('aria-modal');header.removeAttribute('aria-label');}if(restore)button.focus({preventScroll:true});}
button.addEventListener('click',()=>setMenu(!opened));
nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>setMenu(false,true)));
document.addEventListener('click',ev=>{if(opened&&!header.contains(ev.target))setMenu(false);});
document.addEventListener('keydown',ev=>{if(!opened)return;if(ev.key==='Escape'){ev.preventDefault();setMenu(false,true);}if(ev.key==='Tab'&&mobile.matches){const items=[...header.querySelectorAll('a,button,summary')].filter(e=>e.getClientRects().length&&!e.closest('[hidden]'));if(ev.shiftKey&&document.activeElement===items[0]){ev.preventDefault();items.at(-1).focus();}else if(!ev.shiftKey&&document.activeElement===items.at(-1)){ev.preventDefault();items[0].focus();}}});
header.addEventListener('focusout',()=>requestAnimationFrame(()=>{if(opened&&!mobile.matches&&!header.contains(document.activeElement))setMenu(false);}));mobile.addEventListener('change',()=>setMenu(false,true));
const measure=()=>document.documentElement.style.setProperty('--ux-header-height',header.querySelector('.header-inner').offsetHeight+'px');if('ResizeObserver'in window)new ResizeObserver(measure).observe(header.querySelector('.header-inner'));measure();
if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){if(!motion.matches)e.target.classList.add('ux-enter');observer.unobserve(e.target);}}),{threshold:.08});document.querySelectorAll('main .section-heading,main .benefit,main .ct-topics article').forEach(e=>{if(e.getBoundingClientRect().top>innerHeight)observer.observe(e);});}
})();

/* Footer groups are compact disclosures on phones; all links remain in HTML. */
(() => {
  const mobile = matchMedia('(max-width:767px)');
  const groups = [...document.querySelectorAll('.footer-top>div')].map((group,index) => {
    const heading=group.querySelector('h2'),links=group.querySelector('.footer-links');
    const label=document.createElement('span');label.className='footer-label';label.textContent=heading.textContent;
    const button=document.createElement('button');button.type='button';button.className='footer-toggle';button.textContent=heading.textContent;
    links.id='footer-links-'+index;button.setAttribute('aria-controls',links.id);button.setAttribute('aria-expanded','false');
    heading.replaceChildren(label,button);
    button.addEventListener('click',()=>{const opened=button.getAttribute('aria-expanded')==='true';button.setAttribute('aria-expanded',String(!opened));links.hidden=opened;});
    return {button,links};
  });
  function layout(){groups.forEach(({button,links})=>{links.hidden=mobile.matches&&button.getAttribute('aria-expanded')!=='true';});}
  mobile.addEventListener('change',layout);layout();
})();
