/* Progressive enhancement: native selects remain the form/state source of truth.
   Popovers stay in the top layer, including when opened inside the guest dialog. */
(() => {
  'use strict';
  if (!('showPopover' in HTMLElement.prototype)) return;
  const widgets = new Map();
  let opened = null, serial = 0, refreshQueued = false;
  const chevron = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';
  const pin = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2"/></svg>';
  const check = '<svg class="icon ui-select-check" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4 4 10-10"/></svg>';

  function close(restore = false) {
    if (!opened) return;
    const widget = opened;
    opened = null;
    if (widget.panel.matches(':popover-open')) widget.panel.hidePopover();
    widget.button.setAttribute('aria-expanded', 'false');
    widget.button.removeAttribute('aria-activedescendant');
    if (restore && widget.button.isConnected) widget.button.focus({preventScroll: true});
  }

  function position(widget) {
    const viewport = window.visualViewport;
    const width = viewport?.width || innerWidth, height = viewport?.height || innerHeight;
    const ox = viewport?.offsetLeft || 0, oy = viewport?.offsetTop || 0;
    const rect = widget.button.getBoundingClientRect(), margin = 12;
    const panelWidth = Math.min(width - margin * 2, width < 640 ? width - 32 : Math.max(rect.width, widget.hotel ? 340 : 240));
    widget.panel.style.width = panelWidth + 'px';
    const below = oy + height - rect.bottom - margin - 8, above = rect.top - oy - margin - 8;
    const upward = below < 280 && above > below;
    widget.list.style.maxHeight = Math.max(64, Math.min(360, (upward ? above : below) - 58)) + 'px';
    const panelHeight = widget.panel.getBoundingClientRect().height;
    const left = width < 640 ? ox + (width - panelWidth) / 2 : Math.max(ox + margin, Math.min(rect.left, ox + width - panelWidth - margin));
    const top = Math.max(oy + margin, Math.min(upward ? rect.top - panelHeight - 8 : rect.bottom + 8, oy + height - panelHeight - margin));
    widget.panel.style.left = left + 'px';
    widget.panel.style.top = top + 'px';
  }

  function activate(widget, index, scroll = true) {
    widget.active = index;
    widget.items.forEach((item, n) => item.classList.toggle('is-active', n === index));
    const item = widget.items[index];
    if (!item) return;
    widget.button.setAttribute('aria-activedescendant', item.id);
    if (scroll) item.scrollIntoView({block: 'nearest', behavior: 'instant'});
  }

  function enabled(widget) {
    return [...widget.select.options].map((option, index) => ({option, index})).filter(({option}) => !option.disabled && !option.hidden && !option.closest('optgroup[disabled]')).map(({index}) => index);
  }

  function commit(widget, index, restore = true) {
    if (!enabled(widget).includes(index)) return;
    const changed = widget.select.selectedIndex !== index;
    close(restore);
    widget.select.selectedIndex = index;
    widget.select.removeAttribute('aria-invalid');
    if (changed) {
      widget.select.dispatchEvent(new Event('input', {bubbles: true}));
      widget.select.dispatchEvent(new Event('change', {bubbles: true}));
    }
    refreshAll();
  }

  function render(widget) {
    widget.list.replaceChildren();
    widget.items = [...widget.select.options].map((option, index) => {
      const item = document.createElement('div');
      item.id = widget.id + '-option-' + index;
      item.className = 'ui-select-option' + (widget.hotel ? ' is-hotel' : '');
      item.setAttribute('role', 'option');
      item.setAttribute('aria-selected', String(index === widget.select.selectedIndex));
      item.setAttribute('aria-disabled', String(option.disabled || !!option.closest('optgroup[disabled]')));
      item.hidden = option.hidden;
      if (widget.hotel) item.insertAdjacentHTML('beforeend', pin);
      const copy = document.createElement('span');
      copy.className = 'ui-select-option-copy';
      const parts = widget.hotel ? option.textContent.split(' · ') : [option.textContent];
      const title = document.createElement('span'); title.textContent = parts[0]; copy.append(title);
      if (parts.length > 1) { const detail = document.createElement('small'); detail.textContent = parts.slice(1).join(' · '); copy.append(detail); }
      item.append(copy); item.insertAdjacentHTML('beforeend', check);
      item.addEventListener('pointerdown', event => event.preventDefault());
      item.addEventListener('pointermove', event => { if (event.pointerType === 'mouse' && enabled(widget).includes(index)) activate(widget, index, false); });
      item.addEventListener('click', event => { event.preventDefault(); event.stopPropagation(); commit(widget, index); });
      widget.list.append(item);
      return item;
    });
  }

  function show(widget) {
    if (widget.select.matches(':disabled')) return;
    close(); refresh(widget); render(widget);
    opened = widget;
    widget.panel.showPopover();
    widget.button.setAttribute('aria-expanded', 'true');
    position(widget);
    const selected = enabled(widget).includes(widget.select.selectedIndex) ? widget.select.selectedIndex : enabled(widget)[0];
    activate(widget, selected);
  }

  function refresh(widget) {
    const full = widget.select.selectedOptions[0]?.textContent.trim() || 'Выберите вариант';
    const text = widget.hotel ? full.split(' · ')[0] : full;
    if (widget.value.textContent !== text) widget.value.textContent = text;
    widget.button.setAttribute('aria-label', widget.label + ': ' + full);
    widget.button.disabled = widget.select.matches(':disabled');
    widget.button.setAttribute('aria-required', String(widget.select.required));
    for (const attr of ['aria-invalid', 'aria-describedby']) {
      const value = widget.select.getAttribute(attr);
      if (value) widget.button.setAttribute(attr, value); else widget.button.removeAttribute(attr);
    }
    if (opened === widget) widget.items.forEach((item, n) => item.setAttribute('aria-selected', String(n === widget.select.selectedIndex)));
  }

  function refreshAll() {
    for (const [select, widget] of widgets) {
      if (!select.isConnected) { if (opened === widget) close(); widgets.delete(select); }
      else { refresh(widget); if (opened === widget && select.matches(':disabled')) close(); }
    }
  }

  function queueRefresh() {
    if (refreshQueued) return;
    refreshQueued = true;
    requestAnimationFrame(() => { refreshQueued = false; refreshAll(); });
  }

  function enhance(select) {
    if (widgets.has(select) || select.multiple || select.size > 1 || select.dataset.nativeSelect !== undefined) return;
    const labelNode = select.labels?.[0] || select.closest('label');
    const clone = labelNode?.cloneNode(true);
    clone?.querySelectorAll('select,input,button,svg').forEach(node => node.remove());
    const label = select.getAttribute('aria-label') || clone?.textContent.trim().replace(/\s+/g, ' ') || 'Выберите вариант';
    const wrapper = document.createElement('span'); wrapper.className = 'ui-select';
    const id = 'ui-select-' + (++serial);
    const button = document.createElement('button');
    button.type = 'button'; button.id = id + '-button'; button.className = 'select-button ui-select-trigger';
    button.setAttribute('role', 'combobox'); button.setAttribute('aria-haspopup', 'listbox'); button.setAttribute('aria-expanded', 'false'); button.setAttribute('aria-controls', id + '-list');
    const hotel = select.name === 'hotel';
    if (hotel) button.insertAdjacentHTML('beforeend', pin);
    const value = document.createElement('span'); value.className = 'ui-select-value'; button.append(value); button.insertAdjacentHTML('beforeend', chevron);
    const panel = document.createElement('div'); panel.className = 'ui-select-popover'; panel.setAttribute('popover', 'manual');
    const caption = document.createElement('div'); caption.className = 'ui-select-caption'; caption.textContent = label;
    const list = document.createElement('div'); list.className = 'ui-select-list'; list.id = id + '-list'; list.setAttribute('role', 'listbox'); list.setAttribute('aria-label', label);
    panel.append(caption, list);
    select.before(wrapper); wrapper.append(select, button, panel);
    select.classList.add('ui-select-native'); select.tabIndex = -1; select.setAttribute('aria-hidden', 'true');
    if (labelNode) labelNode.htmlFor = button.id;
    const widget = {select, wrapper, button, panel, list, value, label, id, hotel, items: [], active: 0, search: '', typedAt: 0};
    widgets.set(select, widget); refresh(widget);
    button.addEventListener('click', event => { event.preventDefault(); opened === widget ? close() : show(widget); });
    button.addEventListener('focus', () => refresh(widget));
    select.addEventListener('focus', () => button.focus({preventScroll: true}));
    select.addEventListener('change', () => refresh(widget));
    select.addEventListener('invalid', event => { event.preventDefault(); select.setAttribute('aria-invalid', 'true'); refresh(widget); button.focus(); });
    button.addEventListener('keydown', event => {
      if (event.key === 'Escape' && opened === widget) { event.preventDefault(); event.stopPropagation(); close(true); return; }
      if (event.key === 'Tab') { if (opened === widget) commit(widget, widget.active, false); return; }
      if (event.ctrlKey || event.metaKey || event.altKey) return;
      if (['Enter', ' '].includes(event.key)) {
        event.preventDefault(); opened === widget ? commit(widget, widget.active) : show(widget); return;
      }
      if (['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) {
        event.preventDefault();
        if (opened !== widget) { show(widget); if (event.key.startsWith('Arrow')) return; }
        const indices = enabled(widget), current = indices.indexOf(widget.active);
        const next = event.key === 'Home' ? 0 : event.key === 'End' ? indices.length - 1 : Math.max(0, Math.min(indices.length - 1, current + (event.key === 'ArrowDown' ? 1 : -1)));
        activate(widget, indices[next]); return;
      }
      if (event.key.length === 1) {
        event.preventDefault(); if (opened !== widget) show(widget);
        const now = performance.now(); widget.search = (now - widget.typedAt > 700 ? '' : widget.search) + event.key.toLocaleLowerCase('ru'); widget.typedAt = now;
        const prefix = [...widget.search].every(char => char === widget.search[0]) ? widget.search[0] : widget.search;
        const indices = enabled(widget), start = indices.indexOf(widget.active);
        const order = [...indices.slice(start + 1), ...indices.slice(0, start + 1)];
        const found = order.find(index => widget.select.options[index].textContent.trim().toLocaleLowerCase('ru').startsWith(prefix));
        if (found !== undefined) activate(widget, found);
      }
    });
    panel.addEventListener('toggle', () => { if (opened === widget && !panel.matches(':popover-open')) close(); });
  }

  function scan(root) { if (root.matches?.('select')) enhance(root); root.querySelectorAll?.('select').forEach(enhance); }
  scan(document);
  new MutationObserver(records => {
    for (const record of records) {
      if (record.type === 'childList') record.addedNodes.forEach(node => { if (node.nodeType === 1) scan(node); });
      if (record.target.matches?.('select,option,optgroup,fieldset')) queueRefresh();
    }
    if (opened && (!opened.select.isConnected || opened.select.closest('dialog:not([open]),[hidden],[inert]'))) close();
  }).observe(document.body, {subtree: true, childList: true, attributes: true, attributeFilter: ['disabled', 'required', 'aria-invalid', 'aria-describedby', 'selected', 'open', 'hidden', 'inert']});
  document.addEventListener('pointerdown', event => { if (opened && !opened.wrapper.contains(event.target)) close(); }, true);
  document.addEventListener('focusin', event => { if (opened && !opened.wrapper.contains(event.target)) close(); }, true);
  document.addEventListener('scroll', event => {
    if (!opened || opened.panel.contains(event.target)) return;
    const rect = opened.button.getBoundingClientRect();
    if (rect.bottom < 0 || rect.top > innerHeight) close(); else position(opened);
  }, true);
  for (const event of ['click', 'change', 'booking-context-change', 'hotel-map-selection', 'reset']) document.addEventListener(event, queueRefresh, true);
  addEventListener('popstate', queueRefresh);
  addEventListener('resize', () => { if (opened) position(opened); });
  window.visualViewport?.addEventListener('resize', () => { if (opened) position(opened); });
  window.turrisSelects = {refresh: refreshAll};
})();
