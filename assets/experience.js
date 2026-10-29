/* Shared navigation, restrained motion and progressively enhanced hotel map. */
(() => {
  'use strict';
  const base = window.SITE_BASE || '';
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const header = document.querySelector('.header');
  const inner = document.querySelector('.header-inner');
  const menu = document.querySelector('.menu-button');
  const closeMenu = () => {
    inner.classList.remove('menu-open');
    menu.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-label', 'Открыть меню');
    document.querySelectorAll('.nav details[open]').forEach(el => el.open = false);
  };
  document.querySelectorAll('.nav a').forEach(el => el.addEventListener('click', closeMenu));
  document.addEventListener('keydown', ev => {
    if (ev.key === 'Escape' && header.contains(document.activeElement)) {
      closeMenu();
      if (matchMedia('(max-width: 900px)').matches) menu.focus();
    }
  });
  header.addEventListener('focusout', () => {
    requestAnimationFrame(() => {
      if (!header.contains(document.activeElement)) closeMenu();
    });
  });
  const top = document.createElement('button');
  top.className = 'back-to-top'; top.type = 'button'; top.textContent = '↑';
  top.setAttribute('aria-label', 'Вернуться к началу страницы'); top.hidden = true;
  top.addEventListener('click', () => {
    window.scrollTo({top: 0, behavior: motion.matches ? 'instant' : 'smooth'});
    const main = document.querySelector('main');
    main.tabIndex = -1; main.focus({preventScroll: true});
  });
  document.body.append(top);
  let scrollQueued = false;
  const scrollState = () => {
    header.classList.toggle('is-scrolled', scrollY > 8);
    top.hidden = scrollY < 800; scrollQueued = false;
  };
  window.addEventListener('scroll', () => {
    if (!scrollQueued) {scrollQueued = true; requestAnimationFrame(scrollState);}
  }, {passive: true});
  scrollState();
  // Two views of one selection task; HTML retains both when JavaScript is unavailable.
  document.querySelectorAll('[data-hotel-explorer]').forEach(explorer => {
    const show = (view, updateAddress = false) => {
      explorer.querySelectorAll('[data-explorer-panel]').forEach(panel => panel.hidden = panel.dataset.explorerPanel !== view);
      explorer.querySelectorAll('[data-hotel-view]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.hotelView === view)));
      explorer.dataset.view = view;
      if (view === 'map') explorer.querySelector('[data-hotel-map]').dispatchEvent(new Event('hotel-map-show'));
      if (updateAddress) history.replaceState(null, '', location.pathname + location.search + (view === 'map' ? '#map' : '#hotels'));
      window.dispatchEvent(new Event('resize'));
    };
    explorer.showHotelView = show;
    explorer.querySelectorAll('[data-hotel-view]').forEach(button => button.addEventListener('click', () => show(button.dataset.hotelView, true)));
    const compare = explorer.querySelector('[data-compare-hotels]');
    compare.href = base + '/hotels/#comparison';
    show(location.hash === '#map' ? 'map' : 'cards');
    window.addEventListener('hashchange', () => {
      if (location.hash === '#map') {show('map'); explorer.querySelector('#map').scrollIntoView({block: 'start'});}
      if (location.hash === '#hotels') show('cards');
    });
    document.querySelectorAll('a[href$="#map"]').forEach(link => link.addEventListener('click', ev => {
      const target = new URL(link.href, location.href);
      if (target.pathname === location.pathname) {
        ev.preventDefault(); show('map', true); explorer.querySelector('#map').scrollIntoView({behavior: motion.matches ? 'instant' : 'smooth', block: 'start'});
      }
    }));
  });
  // Content is always visible. A reveal animates once on entry, never gates reading.
  if ('IntersectionObserver' in window) {
    const reveal = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) {
        if (!motion.matches) entry.target.classList.add('revealed');
        reveal.unobserve(entry.target);
      }
    }), {threshold: .08});
    document.querySelectorAll('.section-heading,.feature,.benefits,.quote,.team-band,.hotel-card,.room-card,.article-card').forEach(el => {
      if (el.getBoundingClientRect().top > innerHeight) reveal.observe(el);
    });
  }

  let leafletPromise;
  const loadLeaflet = () => {
    if (window.L) return Promise.resolve(window.L);
    if (!leafletPromise) leafletPromise = new Promise((resolve, reject) => {
      const css = document.createElement('link'); css.rel = 'stylesheet';
      css.href = base + '/assets/vendor/leaflet/leaflet.css'; document.head.append(css);
      const js = document.createElement('script'); js.src = base + '/assets/vendor/leaflet/leaflet.js';
      js.onload = () => window.L ? resolve(window.L) : reject(new Error('Map unavailable'));
      js.onerror = () => reject(new Error('Map unavailable')); document.head.append(js);
    });
    return leafletPromise;
  };
  document.querySelectorAll('[data-hotel-map]').forEach(root => {
    const hotels = JSON.parse(root.querySelector('[data-map-config]').textContent);
    const choices = [...root.querySelectorAll('[data-map-select]')];
    const panels = [...root.querySelectorAll('[data-map-detail]')];
    const status = root.querySelector('[data-map-status]');
    const announce = root.querySelector('[data-map-announcement]');
    const requested = new URLSearchParams(location.search).get('map-hotel');
    let selected = hotels[requested] ? requested : root.dataset.selected, map, L, started = false;
    let visible = Object.keys(hotels);
    const markers = {};
    root.classList.add('map-ready');
    const select = (id, pan = true, speak = true) => {
      if (!hotels[id]) return;
      selected = id; root.dataset.selected = id;
      choices.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.mapSelect === id)));
      panels.forEach(panel => panel.hidden = panel.dataset.mapDetail !== id);
      Object.entries(markers).forEach(([key, marker]) => {
        marker.getElement()?.classList.toggle('selected', key === id);
        marker.getElement()?.setAttribute('aria-pressed', String(key === id));
        marker.setZIndexOffset(key === id ? 1000 : 0);
      });
      if (map && pan) map.panTo([hotels[id].lat, hotels[id].lng], {animate: !motion.matches, duration: .35});
      if (speak) announce.textContent = 'Выбран отель «' + hotels[id].name + '». Адрес, условия и номера — в карточке рядом с картой.';
    };
    const fit = () => {
      if (!map || !visible.length) return;
      map.fitBounds(visible.map(id => [hotels[id].lat, hotels[id].lng]), {
        paddingTopLeft: [48, 90], paddingBottomRight: [48, 60],
        maxZoom: visible.length === 1 ? 15 : 13, animate: !motion.matches
      });
    };
    choices.forEach(button => button.addEventListener('click', () => select(button.dataset.mapSelect)));
    select(selected, false, false);
    root.querySelector('[data-map-reset]').addEventListener('click', fit);
    const start = async () => {
      if (started) return; started = true;
      try {
        L = await loadLeaflet();
        map = L.map(root.querySelector('[data-map-canvas]'), {
          scrollWheelZoom: false, zoomControl: false, keyboard: true,
          dragging: !matchMedia('(pointer: coarse)').matches,
          tap: false, zoomAnimation: !motion.matches, fadeAnimation: !motion.matches,
          markerZoomAnimation: !motion.matches, inertia: !motion.matches
        });
        L.control.zoom({position: 'bottomleft', zoomInTitle: 'Приблизить', zoomOutTitle: 'Отдалить'}).addTo(map);
        if (matchMedia('(pointer: coarse)').matches) {
          const move = document.createElement('button');
          move.type = 'button'; move.className = 'map-move';
          move.textContent = 'Двигать карту'; move.setAttribute('aria-pressed', 'false');
          move.addEventListener('click', () => {
            const enable = !map.dragging.enabled();
            if (enable) map.dragging.enable(); else map.dragging.disable();
            move.setAttribute('aria-pressed', String(enable));
            move.textContent = enable ? 'Завершить просмотр' : 'Двигать карту';
            announce.textContent = enable ? 'Карту можно перемещать пальцем. Нажмите «Завершить просмотр», чтобы снова прокручивать страницу над картой.' : 'Перемещение карты выключено. Можно прокручивать страницу.';
          });
          root.querySelector('.map-stage').append(move);
        }
        const layer = L.tileLayer(root.dataset.tileUrl, {
          maxZoom: 19, minZoom: 10, updateWhenIdle: true,
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>'
        });
        let loaded = 0, failed = 0;
        layer.on('loading', () => {loaded = 0; failed = 0;});
        layer.on('tileload', () => loaded++);
        layer.on('tileerror', () => failed++);
        layer.on('load', () => {
          status.hidden = failed === 0 && loaded > 0;
          if (!status.hidden) status.textContent = 'Карта загружена не полностью. Выберите отель по названию или откройте маршрут.';
        });
        Object.entries(hotels).forEach(([id, hotel], index) => {
          const pin = L.divIcon({className: 'map-pin', html: '<span><b>0' + (index + 1) + '</b></span>', iconSize: [44, 44], iconAnchor: [22, 44]});
          const marker = L.marker([hotel.lat, hotel.lng], {icon: pin, keyboard: true, title: 'Туррис ' + hotel.name, alt: 'Выбрать отель ' + hotel.name});
          marker.bindTooltip(hotel.name, {className: 'map-label', direction: 'top', offset: [0, -42]});
          marker.on('add', () => {
            const element = marker.getElement();
            element.setAttribute('aria-label', 'Выбрать отель «' + hotel.name + '»');
            element.setAttribute('aria-pressed', String(selected === id));
            element.addEventListener('keydown', ev => {
              if (ev.key === 'Enter' || ev.key === ' ') {
                ev.preventDefault(); ev.stopPropagation(); select(id);
              }
            });
          });
          marker.on('click', () => select(id)); markers[id] = marker;
          if (visible.includes(id)) marker.addTo(map);
        });
        fit(); layer.addTo(map); select(selected, false, false);
        root.dataset.mapLoaded = 'true';
        root.addEventListener('hotel-map-show', () => {
          requestAnimationFrame(() => {map.invalidateSize({pan: false}); fit();});
        });
        new ResizeObserver(() => {map.invalidateSize({pan: false});}).observe(root.querySelector('.map-stage'));
        motion.addEventListener('change', () => {
          map.options.zoomAnimation = !motion.matches;
          map.options.fadeAnimation = !motion.matches;
          map.options.markerZoomAnimation = !motion.matches;
          map.options.inertia = !motion.matches;
        });
        // Touch screens retain natural page scrolling; +/− and hotel selection operate the map.
      } catch (_) {
        status.hidden = false;
        status.textContent = 'Не удалось загрузить карту. Все адреса и ссылки на маршруты доступны в карточках отелей.';
        root.dataset.mapLoaded = 'error';
      }
    };
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        if (entries.some(entry => entry.isIntersecting)) {observer.disconnect(); start();}
      }); observer.observe(root);
    } else start();
    document.addEventListener('hotel-filter-change', ev => {
      visible = ev.detail;
      choices.forEach(button => button.hidden = !visible.includes(button.dataset.mapSelect));
      Object.entries(markers).forEach(([id, marker]) => {
        if (visible.includes(id)) marker.addTo(map); else marker.remove();
      });
      if (!visible.includes(selected)) select(visible[0], false);
      const reset = root.querySelector('[data-map-reset]');
      reset.firstChild.textContent = visible.length === 4 ? 'Все отели ' : 'Показать выбранные ';
      root.querySelector('.map-toolbar>span').textContent = 'Москва · ' + visible.length + (visible.length === 1 ? ' отель' : ' отеля');
      fit();
    });
    document.querySelectorAll('[data-show-hotel-map]').forEach(button => button.addEventListener('click', ev => {
      ev.preventDefault();
      root.closest('[data-hotel-explorer]')?.showHotelView('map', true);
      select(button.dataset.showHotelMap);
      root.scrollIntoView({behavior: motion.matches ? 'instant' : 'smooth', block: 'start'});
      choices.find(choice => choice.dataset.mapSelect === selected)?.focus({preventScroll: true});
    }));
  });
})();
