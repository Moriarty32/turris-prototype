(() => {
 'use strict';
 const article = document.querySelector('[data-guide-article]');
 if (!article) return;
 const checklist = article.querySelector('[data-guide-checklist]');
 const inputs = [...checklist.querySelectorAll('[data-guide-check]')];
 const key = 'turris-guide-check-v1:' + checklist.dataset.guideChecklist;
 try {
  const saved = JSON.parse(sessionStorage.getItem(key) || '[]');
  if (Array.isArray(saved)) inputs.forEach(input => input.checked = saved.includes(input.dataset.guideCheck));
 } catch { /* A disabled store does not disable the checklist. */ }
 const update = () => {
  const selected = inputs.filter(input => input.checked).map(input => input.dataset.guideCheck);
  const progress=checklist.querySelector('[data-check-progress]');if(progress)progress.value=selected.length;
  checklist.querySelector('[data-check-count]').textContent = `Готово: ${selected.length} из ${inputs.length}`;
  try { sessionStorage.setItem(key, JSON.stringify(selected)); } catch {}
 };
 inputs.forEach(input => input.addEventListener('change', update));
 checklist.querySelector('[data-check-reset]').addEventListener('click', () => {inputs.forEach(input => input.checked = false); update();});
 update();
 article.querySelector('[data-copy-article]').addEventListener('click', async () => {
  const status = article.querySelector('[data-copy-status]');
  try { await navigator.clipboard.writeText(location.origin + location.pathname); status.textContent = 'Ссылка скопирована'; }
  catch { status.textContent = 'Скопируйте адрес страницы из строки браузера.'; }
 });
 const toc = article.querySelector('.guide-toc');
 const small = matchMedia('(max-width: 900px)');
 const layout = () => { toc.open = !small.matches; };
 layout(); small.addEventListener('change', layout);
 const links = [...article.querySelectorAll('[data-toc-link]')];
 const sections = links.map(link => document.getElementById(link.hash.slice(1)));
 let scheduled = false;
 const markCurrent = () => {
  scheduled = false;
  const threshold = small.matches ? 120 : 165;
  let active = sections[0];
  sections.forEach(section => { if(section.getBoundingClientRect().top <= threshold) active = section; });
  links.forEach(link => {if(link.hash === '#' + active.id) link.setAttribute('aria-current', 'true'); else link.removeAttribute('aria-current');});
 };
 addEventListener('scroll', () => {if (!scheduled) { scheduled = true; requestAnimationFrame(markCurrent); }}, {passive:true});
 links.forEach(link => link.addEventListener('click', () => {
  if(small.matches) toc.open = false;
  // Closing the mobile contents changes layout before the native anchor jump.
 }));
 markCurrent();
})();
