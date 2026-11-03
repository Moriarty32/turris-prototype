"""Home reference composition; reuse existing trip, navigation and map contracts."""

def render(p,g):
 a,image,icon,url,ext=[g[k] for k in ['a','image','icon','url','ext']]
 hotels=g['HOTELS']
 def form(bottom=False):
  s=g['booking_form'](bottom=bottom)
  for label,ic in [('Отель','pin'),('Даты поездки','calendar'),('Гости','guest')]:
   s=s.replace('>'+label+'<', '><span class="home-field-icon">'+icon(ic)+'</span><span class="home-field-label">'+('Заезд — Выезд' if label=='Даты поездки' else label)+'</span><')
  return s
 slides='';slide_buttons=''
 photos={i:'hero_'+i+'_v2' for i in hotels}
 photo_sizes='(max-width:767px) 1px, max(calc(100vw - 8px), min(calc(177.78svh - 142.23px), 1920px))'
 for n,(i,h) in enumerate(hotels.items(),1):
  active=n==1
  label=g['DELIVERY'][photos[i]].get('label','')
  photo=image(photos[i],'Номер в отеле '+h['full'],eager=active,sizes=photo_sizes)
  if label:photo=photo.replace('<small class="ai-image-label">'+label+'</small>','')
  photo='<picture><source media="(max-width:767px)" srcset="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7">'+photo+'</picture>'
  slides+='<div class="hero-slide'+(' is-active' if active else '')+'" id="hero-slide-'+i+'" data-hero-slide="'+i+'" role="group" aria-roledescription="слайд" aria-label="'+str(n)+' из 4: '+h['full']+'"'+('' if active else ' aria-hidden="true" inert')+'>'+photo+'<div class="hero-slide-caption">'+('<span class="hero-image-note">'+label+'</span>' if label else '')+a(i,h['full']+' '+icon('arrow'),'hero-hotel-link')+'</div></div>'
  slide_buttons+='<button type="button" data-hero-pick="'+str(n-1)+'" aria-controls="hero-slide-'+i+'" aria-label="Выбрать отель '+h['name']+'" aria-pressed="'+str(active).lower()+'">'+icon('pin')+'<span class="hero-slide-name">'+h['name']+'</span><span class="hero-slide-progress" aria-hidden="true"></span></button>'
 controls='<div class="hero-carousel-controls"><div class="hero-slide-picker" aria-label="Выбрать отель для бронирования">'+slide_buttons+'</div><div class="hero-carousel-actions"><button type="button" data-hero-prev aria-label="Предыдущая фотография">'+icon('arrow')+'</button><button type="button" data-hero-play aria-label="Остановить автоматическую смену отелей"><svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path class="slider-pause-icon" d="M8 5v14M16 5v14"/><path class="slider-play-icon" d="m9 5 10 7-10 7Z"/></svg></button><button type="button" data-hero-next aria-label="Следующая фотография">'+icon('arrow')+'</button></div></div>'
 intro='<div class="hero-intro"><div class="hero-copy"><div class="hero-eyebrow">Сеть отелей Туррис</div><h1>Отели Туррис<br>в центре Москвы</h1><svg class="hero-flourish" viewBox="0 0 180 16" aria-hidden="true"><path d="M2 13C54-12 112 30 178 3"/></svg><p class="sub">Четыре адреса для отдыха и деловых поездок.<br>Выберите расположение и номер на ваши даты.</p></div>'+controls+'</div>'
 mobile_map='<div class="home-mobile-map" data-mobile-map-slot><h2>Выберите свой адрес</h2><p class="mobile-map-intro">Нажмите на отметку или название отеля.</p></div>'
 caption='<div class="home-search-caption"><p>'+icon('document')+'<span>Стоимость, питание и отмена — в выбранном тарифе.</span></p><a href="tel:88005054455">'+icon('phone')+'<span>Поможем выбрать: <u>8 800 505 44 55</u></span></a></div>'
 dock='<div class="home-booking" id="home-search" aria-label="Поиск номера"><div class="home-booking-heading"><h2>Забронировать проживание</h2>'+caption+'</div>'+form()+'</div>'
 hero='<section class="hero home-hero"><div class="home-hero-scene hero-carousel" data-hero-carousel role="region" aria-label="Выбор отеля и бронирование">'+slides+intro+mobile_map+dock+'<span class="hero-slider-status" role="status" aria-live="polite" aria-atomic="true"></span></div></section>'
 map_markup=g['maplinks']().replace('class="hotel-map"','class="hotel-map home-location-map" data-map-keep-overview').replace('<p class="map-footnote">','<div class="home-map-compare">'+a('hotels','Сравнить условия отелей '+icon('arrow'),'text-link')+'</div><p class="map-footnote">')
 hotel_map='<section class="section home-map-section" id="hotels" aria-labelledby="home-map-title"><div class="wrap home-map-inner"><div class="section-heading"><div><h2 id="home-map-title">Найдите свой адрес в Москве</h2><p class="sub">Выберите отель на карте: адрес, условия и номера — в карточке.</p></div></div>'+map_markup+'</div></section>'
 flourish='<svg class="home-title-flourish" viewBox="0 0 180 18" aria-hidden="true"><path d="M2 12C52-2 94 2 124 10l-12 4 29-4-27-7"/></svg>'
 direct='<section class="home-direct" aria-labelledby="home-direct-title"><h2 id="home-direct-title">Понятное бронирование</h2>'+flourish+g['benefits']()+'<div class="center-link">'+a('loyalty','Программа «Туррис-Бонус» '+icon('arrow'),'text-link')+'</div></section>'
 family_photo=image('tverskaya_room_1','Спальня семейного люкса Тверской',sizes='(max-width:767px) calc(100vw - 40px), (max-width:1099px) 42vw, 440px')
 family_body='<div class="home-offer-media">'+family_photo+'</div><div class="home-offer-copy"><div class="eyebrow">Тверская · семейный люкс</div><h3 id="home-family-title">Вместе — и с местом для каждого</h3><p>Спальня с большой кроватью и гостиная с диваном. Вместимость до 4 мест.</p><span class="home-offer-arrow" aria-hidden="true">'+icon('arrow')+'</span><span class="home-offer-cta">Подобрать семейный номер</span></div>'
 long_body='<div class="home-offer-media">'+image('petrovsky','Фасад отеля Туррис Петровский',sizes='(max-width:767px) calc(100vw - 40px), (max-width:1099px) 40vw, 560px')+'</div><div class="home-offer-copy"><div class="eyebrow">Петровский · от 21 дня</div><h3 id="home-longstay-title">Останьтесь в Москве подольше</h3><p>Для проектной работы или переезда.</p><span class="home-offer-arrow" aria-hidden="true">'+icon('arrow')+'</span><span class="home-offer-cta">Узнать условия</span></div>'
 offers='<div class="home-offers">'+a('family',family_body,'home-offer home-offer-family','aria-labelledby="home-family-title"')+a('longstay',long_body,'home-offer home-offer-longstay','aria-labelledby="home-longstay-title"')+'</div>'
 story='<section class="home-booking-story" aria-label="Бронирование и предложения"><div class="wrap home-story-inner">'+direct+offers+'</div></section>'
 review='<section class="home-review"><h2>Гости о своём проживании</h2><div class="quote"><div class="quote-mark" aria-hidden="true">“</div><div><blockquote><p>В номере чисто, всё необходимое есть. Персонал внимательный и вежливый.</p></blockquote><span class="small">Татьяна Н. · Тверская · фрагмент отзыва на Путёвка.ком</span></div>'+ext('https://www.putevka.com/moskva/moskva/turris-tverskaya','Читать полный отзыв')+'</div></section>'
 team='<section class="team-band home-team">'+icon('guest')+'<div><h2>Разместим вашу команду</h2><p>Для компаний и организаторов групп. Для расчёта свяжитесь с отделом бронирования. Форма запроса пока работает в демонстрационном режиме.</p></div><div class="team-action">'+a('groups','Запросить расчёт '+icon('arrow'),'btn white')+a('business','Условия для компаний ↗','text-link')+'</div></section>'
 faq='<section class="section home-faq"><div><h2>Перед бронированием</h2><p>Ответим на вопросы о вашей поездке.</p><a href="tel:88005054455">'+icon('phone')+'8 800 505 44 55</a></div>'+g['faqs'](opened=False)+'</section>'
 bottom='<section class="booking-bottom"><h2>Ваша поездка начинается с дат</h2><p class="sub">Выберите расположение и посмотрите номера на время поездки.</p>'+form(True)+'<p class="help-line">Поможем с выбором. <a href="tel:88005054455">8 800 505 44 55</a></p></section>'
 mobile_actions='<nav class="home-mobile-actions" aria-label="Быстрый выбор номера" hidden><button type="button" data-mobile-map>'+icon('pin')+'<span>Карта отелей</span></button><button type="button" class="btn" data-mobile-book>Выбрать даты '+icon('arrow')+'</button></nav>'
 return '<div class="wrap home-page">'+hero+hotel_map+story+review+team+faq+bottom+'</div>'+mobile_actions
