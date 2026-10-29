"""Guide index reference: editorial search, six-card pages, hotel routes and booking."""
import json

def render(p,g):
 a,e,image,icon,url=[g[k] for k in ['a','e','image','icon','url']]
 labels=g['RUBRIC_LABELS'];hotels=g['HOTELS'];rubric=p['id'].replace('blog_','') if p['id']!='blog' else 'all'
 plan=g['B']['blog_plan'];byid={b['id']:b for b in plan}
 order=['article_2','article_3','article_6','article_8','article_12','article_15']
 items=[byid[i] for i in order]+[b for b in plan if b['id'] not in order]
 if rubric!='all':items=[b for b in items if b['rubric']==rubric]
 lead=byid['article_1'] if rubric=='all' else items[0]
 summaries={'article_2':'Начните на площади Тверская Застава и спланируйте остановки по пути.','article_3':'Лубянский проезд и прогулка в сторону Зарядья.','article_6':'Возраст детей, спальные места и вопросы до бронирования.','article_8':'Данные плательщика и требования вашей компании — до оплаты.','article_12':'Разберитесь в типах кроватей и размещении гостей.','article_15':'Проверьте дату начала брони и сообщите время прибытия.'}
 assets={'article_6':'lubyansky_room_1','article_12':'tverskaya_room_4'}
 def media(b,eager=False):
  special={'article_8':'guide-documents','article_15':'guide-arrival'}.get(b['id'])
  if special:return '<img src="'+g['BASE']+'/assets/'+special+'.webp" width="2048" height="768" alt="'+('Чемодан и документы для поездки' if special=='guide-documents' else 'Часы и дверь номера: планирование времени приезда')+'" loading="lazy" decoding="async"><small class="jr-image-label">ИИ-иллюстрация</small>'
  return image(assets.get(b['id'],g['guide_asset'](b)),b['title'],eager=eager,sizes='(max-width:640px) calc(100vw - 32px), (max-width:1280px) 46vw, 600px')
 def related_hotels(b):
  slug,item,d,minutes=g['guide_info'](b)
  if d.get('hotel'):return [d['hotel']]
  if b['commercial_target']=='family':return ['tverskaya','lubyansky']
  if b['commercial_target']=='longstay':return ['petrovsky']
  return list(hotels)
 topics='<nav class="jr-topics" aria-label="Рубрики гида">'+''.join(a('blog_'+key,icon(ic)+'<span>'+label+' · '+str(sum(b['rubric']==key for b in plan))+'</span>'+icon('arrow'),'jr-topic','data-journal-topic="'+key+'"') for key,label,ic in [('districts',labels['districts'],'pin'),('family',labels['family'],'guest'),('business',labels['business'],'calendar'),('stay',labels['stay'],'document')])+'</nav>'
 search='<label class="jr-search">'+icon('search')+'<span>Поиск по гиду<input type="search" data-journal-search placeholder="Район, маршрут или вопрос об отеле" autocomplete="off"></span></label>'
 hero='<header class="jr-hero"><div class="jr-intro"><div class="eyebrow">Гид Туррис · Москва</div><h1>'+('Гид по Москве<br><em>и комфортной поездке</em>' if rubric=='all' else labels[rubric])+'</h1><p>Выберите район, соберите маршрут и подготовьтесь к проживанию.</p>'+search+topics+'<a href="#guide-map" class="text-link">Маршруты на карте ↓</a></div><article class="jr-feature"><a class="jr-feature-photo" href="'+url(lead['id'])+'" tabindex="-1" aria-hidden="true">'+media(lead,True)+'</a><div><div class="eyebrow">С чего начать</div><h2>'+a(lead['id'],lead['title'])+'</h2><p>'+('Сравните четыре адреса и начните с главной цели поездки.' if rubric=='all' else g['guide_info'](lead)[2]['takeaways'][0])+'</p><small>Редакция Туррис · '+str(g['guide_info'](lead)[3])+' мин</small>'+a(lead['id'],'Открыть руководство '+icon('arrow'),'btn jr-blue')+'</div></article></header>'
 cards=''
 for b in items:
  slug,item,d,minutes=g['guide_info'](b);hs=related_hotels(b)
  searchtext=' '.join([b['title'],item['answer'],str(d),labels[b['rubric']]])
  cards+='<article class="jr-card" data-journal-card data-rubric="'+b['rubric']+'" data-hotels="'+' '.join(hs)+'" data-search="'+e(searchtext)+'"><a class="jr-card-photo" href="'+url(b['id'])+'" tabindex="-1" aria-hidden="true">'+media(b)+'</a><div class="jr-card-body"><div class="jr-meta"><span>'+labels[b['rubric']]+'</span>'+('<span>'+hotels[d['hotel']]['name']+'</span>' if d.get('hotel') else '')+'<span>'+str(minutes)+' мин</span></div><h3>'+a(b['id'],b['title'])+'</h3><p>'+e(summaries.get(b['id'],d['takeaways'][0]+' '+d['takeaways'][1]))+'</p>'+a(b['id'],('Маршрут и советы' if 'stops' in d else 'Читать руководство')+' '+icon('arrow'),'text-link')+'</div></article>'
 filters='<div class="jr-filters"><label>'+icon('document')+'<span>Тема<select data-journal-rubric><option value="all">Все материалы</option>'+''.join('<option value="'+key+'"'+(' selected' if key==rubric else '')+'>'+label+'</option>' for key,label in labels.items())+'</select></span></label><label>'+icon('pin')+'<span>Рядом с отелем<select data-journal-hotel><option value="all">Любой отель</option>'+''.join('<option value="'+key+'">'+h['name']+'</option>' for key,h in hotels.items())+'</select></span></label><button class="text-link" type="button" data-journal-reset>↻ Сбросить фильтры</button><span data-journal-count aria-live="polite">'+str(len(items))+' материалов</span></div>'
 library='<section class="jr-library" id="guide-library" tabindex="-1"><h2>Найдите ответ для своей поездки</h2>'+filters+'<div class="jr-grid">'+cards+'</div><div class="empty-state" data-journal-empty hidden><h3>По этому запросу ничего не найдено</h3><p>Попробуйте другую тему или сбросьте фильтры.</p><button type="button" class="btn secondary" data-journal-clear>Показать все материалы</button></div><div class="jr-pagination" data-journal-pagination hidden><button class="btn secondary" type="button" data-journal-more>Показать ещё материалы '+icon('arrow')+'</button><nav aria-label="Страницы материалов" data-journal-pages></nav></div></section>'
 routes={h:next(b for b in plan if g['guide_info'](b)[2].get('hotel')==h) for h in hotels}
 panels=''
 for n,(h,hotel) in enumerate(hotels.items(),1):
  b=routes[h]
  panels+='<div class="jr-map-item"><button type="button" class="jr-map-choice" data-map-select="'+h+'" aria-pressed="false" aria-expanded="false" aria-controls="guide-hotel-'+h+'"><span>'+str(n).zfill(2)+'</span><strong>'+hotel['name']+'</strong>'+icon('chevron')+'</button><article class="jr-map-detail" data-map-detail="'+h+'" id="guide-hotel-'+h+'"><div class="jr-map-photo">'+image(h,'Фасад отеля '+hotel['full'],sizes='(max-width:640px) calc(100vw - 64px), 320px')+'</div><p>'+icon('pin')+hotel['address']+'</p><h3>'+a(b['id'],b['title'])+'</h3>'+a(b['id'],'Открыть маршрут прогулки '+icon('arrow'),'btn jr-blue')+a(h+'_rooms','Номера в этом отеле '+icon('arrow'),'text-link')+'</article></div>'
 config={h:dict(geo,name=hotels[h]['name']) for h,geo in g['MAP']['hotels'].items()}
 maphtml='<section class="jr-map-band" id="guide-map"><div class="eyebrow">Маршрут начинается у отеля</div><h2>Что посмотреть рядом с вашим отелем</h2><p>Выберите отель на карте — откройте маршрут прогулки и сравните расположение.</p><div class="hotel-map jr-map" id="map" data-hotel-map data-selected="tverskaya" data-tile-url="'+g['MAP']['tile_url']+'"><div class="jr-map-layout"><div class="map-stage"><div class="map-canvas" data-map-canvas role="region" aria-label="Карта четырёх отелей Москвы"></div><div class="map-toolbar"><span>Москва · четыре адреса</span><button type="button" data-map-reset>Все отели '+icon('pin')+'</button></div><button class="jr-map-expand" type="button" data-journal-map-expand aria-expanded="false" aria-label="Развернуть карту">⛶</button><p class="map-status" data-map-status role="status">Загружаем карту. Маршруты доступны в карточках отелей.</p></div><div class="jr-map-stack">'+panels+'</div></div><span class="sr-only" data-map-announcement aria-live="polite"></span><script type="application/json" data-map-config>'+json.dumps(config,ensure_ascii=False)+'</script></div>'+a('hotels','Сравнить все четыре отеля '+icon('arrow'),'text-link')+'</section>'
 extra='<section class="jr-extra"><h2>Что ещё уточнить перед поездкой</h2><div>'+''.join(a(i,icon(ic)+'<span>'+byid[i]['title']+'</span>'+icon('arrow'),'jr-extra-link') for i,ic in [('article_13','document'),('article_16','guest'),('article_14','calendar'),('article_7','guest')])+'</div></section>'
 form=g['booking_form']()
 for label,ic in [('Отель','pin'),('Даты поездки','calendar'),('Гости','guest')]:form=form.replace('>'+label+'<','><span class="jr-field-icon">'+icon(ic)+'</span><span class="jr-field-label">'+label+'</span><')
 booking='<section class="jr-booking"><div class="eyebrow">От плана — к поездке</div><h2>Теперь выберите свой отель в Москве</h2><p>Сравните расположение и посмотрите номера на ваши даты.</p>'+form+'<a href="tel:88005054455" class="jr-help">'+icon('phone')+'Помощь с выбором · 8 800 505 44 55</a></section>'
 return '<div class="wrap jr-page" data-journal data-rubric="'+rubric+'">'+hero+library+maphtml+extra+booking+'</div>'
