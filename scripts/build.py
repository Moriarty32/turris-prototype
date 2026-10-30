from pathlib import Path
import sys,json,html,shutil,re,math
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'data'))
from content import HOTELS,FAQ,ARTICLES,HELP
from guide import DETAILS as GUIDE, SOURCES as GUIDE_SOURCES
from offer_details import TEMPLATES as OFFER_TEMPLATES
B=json.loads((ROOT/'data/routes.json').read_text(encoding='utf-8'))
PAGES={p['id']:p for p in B['pages']}
ASSETS={a['id']:a for a in json.loads((ROOT/'data/asset-sources.json').read_text(encoding='utf-8'))}
DELIVERY=json.loads((ROOT/'data/image-delivery.json').read_text(encoding='utf-8')) if (ROOT/'data/image-delivery.json').exists() else {}
for asset,delivery in DELIVERY.items():ASSETS[asset]={**ASSETS.get(asset,{}),**delivery}
MAP=json.loads((ROOT/'data/map-locations.json').read_text(encoding='utf-8'))
BASE='/turris-prototype'
DIST=ROOT/'dist';DIST.mkdir(exist_ok=True)
def e(s):return html.escape(str(s),quote=True)
def url(id):return BASE+PAGES[id]['url'] if id in PAGES else BASE+id
def a(id,label,cls='',attrs=''):return f'<a href="{url(id)}" class="{cls}" {attrs}>{label}</a>'
def ext(href,label,cls='text-link'):return f'<a href="{e(href)}" class="{cls}" target="_blank" rel="noopener noreferrer">{label} ↗</a>'
ICONS={
 'arrow':'<path d="M4 12h15m-6-6 6 6-6 6"/>',
 'calendar':'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 2v6m10-6v6M3 11h18m-13 4h1m5 0h1m-7 3h1m5 0h1"/>',
 'pin':'<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2"/>',
 'phone':'<path d="m5 3 4 4-2 3c2 3 4 5 7 6l3-2 4 4-2 3C10 21 3 14 2 6Z"/>',
 'document':'<rect x="5" y="2" width="15" height="20" rx="2"/><path d="M9 7h7m-7 5h7m-7 5h4"/>',
 'headset':'<path d="M4 13v-2a8 8 0 0 1 16 0v7c0 3-3 4-6 4"/><rect x="2" y="11" width="4" height="7" rx="1"/><rect x="18" y="11" width="4" height="7" rx="1"/>',
 'chevron':'<path d="m6 9 6 6 6-6"/>',
 'menu':'<path d="M3 6h18M3 12h18M3 18h18"/>',
 'guest':'<circle cx="12" cy="7" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3"/>',
 'check':'<path d="m4 12 5 5L20 5"/>',
 'search':'<circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/>',
}
def icon(id):return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">{ICONS[id]}</svg>'
def image(asset,alt,cls='',eager=False,sizes='(max-width:640px) calc(100vw - 32px), (max-width:900px) 80vw, 754px'):
 if asset in ASSETS:
  aa=ASSETS[asset];file=aa['file'];w=aa['width'];h=aa['height']
 else:file=('hero-room-v2' if asset=='hero-room' else asset)+'.png';w=1536;h=1024
 delivery=DELIVERY.get(asset,{})
 srcset=' srcset="'+', '.join(BASE+'/assets/'+v['file']+' '+str(v['width'])+'w' for v in delivery['variants'])+'" sizes="'+sizes+'"' if delivery and asset not in HOTELS else ''
 cls+=' facade-photo' if asset in HOTELS else ' portrait-photo' if h>w else ''
 label=delivery.get('label','')
 if label:alt=alt.replace('Фотография','Изображение').replace('фотография','изображение')+' — '+label
 return f'<img src="{BASE}/assets/{file}"{srcset} width="{w}" height="{h}" alt="{e(alt)}" class="{cls.strip()}" data-asset="{asset}" loading="{"eager" if eager else "lazy"}" {"fetchpriority=high" if eager else ""} decoding="async">'+('<small class="ai-image-label">'+label+'</small>' if label else '')
def figure(asset,alt,generated=False,eager=False,cls='hero-visual'):
 if asset in HOTELS:cls+=' facade-media'
 return f'<figure class="{cls}">{image(asset,alt,eager=eager)}'+('<figcaption class="image-note">Иллюстрация концепции</figcaption>' if generated else '')+'</figure>'
def section(title,body,sub='',id='',cls=''):
 return f'<section class="section {cls}"'+(f' id="{id}"' if id else '')+f'><div class="section-heading"><div><h2>{title}</h2>'+ (f'<p class="sub">{sub}</p>' if sub else '')+f'</div></div>{body}</section>'
def paras(lines):return ''.join('<p>'+s+'</p>' for s in lines)
def head(title,desc='',eyebrow='Туррис · Москва'):
 return f'<header class="page-head"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1>'+ (f'<p class="sub">{desc}</p>' if desc else '')+'</header>'
def note(text):return f'<div class="notice">{text}</div>'
def infocards(items):return '<div class="cards3">'+''.join(f'<div class="info-card"><h3>{h}</h3><p>{p}</p></div>' for h,p in items)+'</div>'
def chips(items):return '<div class="chips">'+''.join(f'<span class="chip">{x}</span>' for x in items)+'</div>'
def booking_form(hotel='',room='',bottom=False):
 options='<option value="">Любой из четырёх</option>'+''.join(f'<option value="{i}" {"selected" if i==hotel else ""}>{h["name"]} · {h["location"]}</option>' for i,h in HOTELS.items())
 return f'''<form class="booking-form" data-booking data-hotel="{hotel}" data-room="{room}" action="{url('booking')}" method="get">
 <label class="field hotel-select">Отель<select name="hotel" aria-label="Выберите отель">{options}</select></label>
 <label class="field">Даты поездки<button type="button" class="select-button" data-dates>{icon('calendar')}<span data-date-label>Заезд — Выезд</span>{icon('chevron')}</button></label>
 <label class="field">Гости<button type="button" class="select-button" data-guests>{icon('guest')}<span data-guest-label>2 взрослых</span>{icon('chevron')}</button></label>
 <input type="hidden" name="checkin"><input type="hidden" name="checkout"><input type="hidden" name="adults" value="2"><input type="hidden" name="children" value="[]"><input type="hidden" name="room" value="{room}">
 <button class="btn" type="submit">Показать номера и цены {icon('arrow')}</button><p class="form-error" aria-live="polite"></p></form>'''
def bottom_booking(hotel=''):
 return f'<section class="section booking-bottom"><h2>Ваша поездка начинается с дат</h2><p class="sub">Выберите расположение и посмотрите варианты на время поездки.</p>{booking_form(hotel,bottom=True)}<p class="help-line">Нужна помощь с выбором? <a href="tel:88005054455">{icon("phone")} 8 800 505 44 55</a></p></section>'
def hotel_card(id):
 h=HOTELS[id]
 return f'''<article class="hotel-card" data-hotel-card="{id}"><a class="photo" href="{url(id)}">{image(id,'Фасад отеля '+h['full'])}</a><div class="hotel-card-body"><h3>{a(id,h['name'])}</h3><p class="hotel-location">{h['location']}</p><p class="address">{icon('pin')}{h['address']}</p><a href="{url('home')}?map-hotel={id}#map" class="card-map-link" data-show-hotel-map="{id}">Показать на карте</a><div class="card-bottom"><span class="muted">{h['tag']}</span>{a(id+'_rooms','Номера и цены '+icon('arrow'),'text-link')}</div></div></article>'''
def hotel_grid(ids=None):return '<div class="hotels-grid">'+''.join(hotel_card(i) for i in (ids or HOTELS))+'</div>'
def hotel_explorer():
 return '<div class="hotel-explorer" data-hotel-explorer><div class="explorer-toolbar"><div class="view-switch" role="group" aria-label="Способ выбора отеля"><button type="button" data-hotel-view="cards" aria-pressed="true">Карточки отелей</button><button type="button" data-hotel-view="map" aria-pressed="false">'+icon('pin')+' На карте</button></div><a class="hero-map-return text-link" href="#map">К карте отелей ↑</a>'+a('hotels','Сравнить условия '+icon('arrow'),'text-link','data-compare-hotels')+'</div><div data-explorer-panel="cards">'+hotel_grid()+'<p class="selection-note">Питание и парковка зависят от отеля и тарифа. В Таганском нет лифта.</p></div><div data-explorer-panel="map">'+maplinks()+'</div></div>'
def room_hotel(p):return next(i for i in HOTELS if p['id'].startswith(i+'_'))
def room_name(p):
 name=p['h1'].split(' — ')[0]
 if 'Deluxe Suite Twin' in name:return 'Делюкс Suite Twin с диваном'
 if 'Deluxe Suite Double' in name:return 'Делюкс Suite Double с диваном'
 if 'Duplex Suite' in name:return 'Duplex Suite — двухуровневый'
 if 'Deluxe TWIN' in name:return 'Делюкс с двумя кроватями'
 if 'Deluxe DBL' in name:return 'Делюкс с кроватью king-size'
 if name.startswith('Standard ('):return 'Стандарт с кроватью king-size'
 n=name.lower()
 if 'мансарда' in n:return 'Делюкс мансарда' if 'делюкс' in n else 'Симпл мансарда'
 if 'или' in n and 'кроват' in n:return 'Улучшенный номер' if 'улучшенн' in n else 'Стандартный номер' if 'стандарт' in n else 'Делюкс'
 if 'стандарт' in n:return 'Стандарт с двумя кроватями' if 'двумя' in n else 'Стандарт с двуспальной кроватью'
 if 'улучшенн' in n:return 'Улучшенный с двумя кроватями' if 'двумя' in n else 'Улучшенный с двуспальной кроватью'
 if 'симпл' in n:return 'Симпл с двуспальной кроватью'
 return name.replace('С двуспальной','с двуспальной').replace('Двухспальной','двуспальной')
def room_facts(p):
 n=p['h1'].lower()
 beds='Одна двуспальная кровать'
 if 'одноместн' in n:beds='Одно основное спальное место'
 elif 'или' in n and ('кроват' in n):beds='Двуспальная или две раздельные кровати — уточните конфигурацию'
 elif 'twin' in n or 'двумя кроватями' in n:beds='Две раздельные кровати'
 if 'диван' in n or 'семейный' in n:beds+=' и диван'
 if 'мансард' in n:detail='Мансардный потолок со скосами. Посмотрите фотографии и уточните высоту в важных для вас зонах.'
 elif 'duplex' in n or 'двухъярус' in n:detail='Два уровня и внутренняя лестница. Учитывайте планировку при поездке с ребёнком.'
 elif 'семейный' in n:detail='Спальня с большой кроватью и гостиная с диваном. По описанию отеля — до четырёх мест.'
 else:detail='Выберите даты и состав гостей, чтобы проверить условия конкретной категории.'
 return beds,detail
def room_card(p):
 beds,detail=room_facts(p);hid=room_hotel(p)
 return f'<article class="room-card" data-room-card="{p["id"]}"><a href="{url(p["id"])}">{image(p["id"],room_name(p)+', '+HOTELS[hid]["full"])}</a><div class="room-body"><div class="eyebrow">{HOTELS[hid]["name"]}</div><h3>{a(p["id"],e(room_name(p)))}</h3><p>{beds}. {detail}</p>{a(p["id"],"Подробнее о номере "+icon('arrow'),'text-link')}</div></article>'
def rooms(hotel=None,ids=None,limit=None):
 arr=[p for p in PAGES.values() if p['template']=='room' and (not hotel or p['id'].startswith(hotel+'_')) and (not ids or p['id'] in ids)]
 return '<div class="rooms-grid">'+''.join(room_card(p) for p in arr[:limit])+'</div>'
def faqs(items=FAQ,opened=True):
 return '<div class="faq">'+''.join(f'<details {"open" if k==0 and opened else ""}><summary>{q}</summary><div class="faq-answer">{ans}'+(a(dest,'Подробнее '+icon('arrow')) if dest else '')+'</div></details>' for k,(q,ans,dest) in enumerate(items))+'</div>'
def contact_cards():return '<div class="hotels-grid">'+''.join(f'<div class="info-card"><h3>{a(i,h["full"])}</h3><p class="address">{icon("pin")}{h["address"]}</p><p style="margin-top:15px"><a href="tel:88005054455">8 800 505 44 55</a><br><a href="mailto:{h["email"]}">{h["email"]}</a></p>{a(i+"_contacts","Как добраться "+icon("arrow"),"text-link")}</div>' for i,h in HOTELS.items())+'</div>'
def maplinks(selected='tverskaya'):
 buttons='';panels=''
 for n,(i,h) in enumerate(HOTELS.items(),1):
  geo=MAP['hotels'][i]
  buttons+=f'<button type="button" class="map-choice" data-map-select="{i}" aria-pressed="false"><span class="map-number">0{n}</span><span>{h["name"]}<small>{h["location"]}</small></span></button>'
  panels+=f'<article class="map-detail" data-map-detail="{i}">{image(i,"Фасад отеля "+h["full"])}<div class="map-detail-copy"><div class="eyebrow">Ваш адрес в Москве · 0{n}</div><h3>{h["full"]}</h3><p class="address">{icon("pin")}{h["address"]}</p><p class="map-condition">{h["notice"]}</p>{a(i+"_booking","Номера на мои даты "+icon("arrow"),"btn full",'data-trip-hotel="'+i+'"')}<div class="map-actions">{ext(geo["source"]+"?rtext=~"+str(geo["lat"])+","+str(geo["lng"]),"Маршрут")}{a(i,"Об отеле","text-link")}</div></div></article>'
 config={i:dict(g,name=HOTELS[i]['name']) for i,g in MAP['hotels'].items()}
 return f'<div class="hotel-map" id="map" data-hotel-map data-selected="{selected}" data-tile-url="{MAP["tile_url"]}"><div class="map-choices" aria-label="Выберите отель на карте">{buttons}</div><div class="map-layout"><div class="map-stage"><div class="map-canvas" data-map-canvas role="region" aria-label="Интерактивная карта четырёх отелей в Москве"></div><div class="map-toolbar"><span>Москва · четыре адреса</span><button type="button" data-map-reset>Все отели {icon("pin")}</button></div><p class="map-status" data-map-status role="status">Загружаем карту… Адреса и маршруты доступны в карточках.</p></div><div class="map-details">{panels}</div></div><p class="hero-map-hint">Выберите отель выше или нажмите на отметку — он появится в форме поиска.</p><p class="map-footnote">Выберите отметку или название отеля. Для масштаба используйте + и −. Вход и парковку уточняйте перед поездкой.</p><span class="sr-only" data-map-announcement aria-live="polite"></span><script type="application/json" data-map-config>{json.dumps(config,ensure_ascii=False)}</script></div>'
def tabs(hotel,active):
 return '<nav class="hotel-tabs" aria-label="Разделы отеля">'+''.join(a(id,label,'active' if id==active else '') for id,label in [(hotel,'Обзор'),(hotel+'_rooms','Номера'),(hotel+'_services','Услуги'),(hotel+'_contacts','Как добраться'),(hotel+'_reviews','Отзывы'),(hotel+'_rules','Правила')])+'</nav>'
def benefits():return '<div class="benefits">'+''.join(f'<div class="benefit">{icon(ic)}<div><h3>{h}</h3><p>{p}</p></div></div>' for ic,h,p in [('calendar','Номера на ваши даты','Категории и стоимость проживания — под вашу поездку.'),('document','Условия в выбранном тарифе','Питание, предоплата и условия отмены до оформления.'),('headset','Связь с отелем','Помощь с выбором и деталями поездки.')])+'</div>'
def band():return f'<section class="team-band"><div class="wrap"><div><h2>Разместим вашу команду</h2><p>Расскажите о датах и количестве гостей.<br>Подберём варианты и подготовим предложение.</p></div><div class="team-action">{a("groups","Запросить расчёт "+icon("arrow"),"btn white")}<span class="small">Для компаний и организаторов групп</span></div></div></section>'
def feature(asset,title,text,dest,label,eye='',pale=False,generated=False):
 media=figure(asset,'Иллюстрация: '+title if generated else title,generated,cls='feature-media')
 copy=f'<div class="feature-copy"><div class="eyebrow">{eye}</div><h2>{title}</h2><p>{text}</p>{a(dest,label+" "+icon("arrow"),'text-link' if pale else 'btn')}</div>'
 return '<div class="feature'+(' pale' if pale else '')+'">'+(copy+media if pale else media+copy)+'</div>'
def home(p):
 from home_page import render
 return render(p,globals())

def catalog(p):
 comparison='<div class="table-scroll"><table><thead><tr><th>Отель</th><th>Расположение</th><th>На что обратить внимание</th><th>Выбор</th></tr></thead><tbody>'+''.join(f'<tr><td>{h["full"]}</td><td>{h["address"]}</td><td>{h["notice"]}</td><td>{a(i+"_rooms","Выбрать номер")}</td></tr>' for i,h in HOTELS.items())+'</tbody></table></div>'
 return '<div class="wrap">'+head('Четыре отеля.<br>Ваша Москва.','Сравните расположение, категории и важные условия перед выбором.')+'<div class="catalog-tools"><label class="field">Цель поездки<select data-hotel-filter><option value="all">Все отели</option><option value="family">Семейные категории</option><option value="longstay">Длительное проживание</option><option value="beds">Раздельные кровати</option></select></label><button type="button" class="btn secondary" data-reset-hotels hidden>Сбросить фильтр</button><span class="small" data-filter-count>4 отеля</span></div>'+section('Выберите расположение',hotel_explorer(),id='hotels')+section('Сравните важные детали',comparison,id='comparison')+bottom_booking()+'</div>'
def hotel_page(p):
 from hotel_detail import render
 return render(p,globals())

def room_page(p):
 i=room_hotel(p);h=HOTELS[i];beds,detail=room_facts(p)
 others=[r['id'] for r in PAGES.values() if r['template']=='room' and r['id'].startswith(i) and r['id']!=p['id']][:3]
 return f'<div class="wrap"><section class="hotel-hero"><div class="hero-copy"><div class="eyebrow">{h["full"]}</div><h1>{e(room_name(p))}</h1><p class="sub">{beds}.</p><p class="muted">{detail}</p><div style="margin-top:22px">{booking_form(i,p["id"])}</div></div>{figure(p["id"],room_name(p),False,True)}</section>{tabs(i,i+"_rooms")}{note(h["notice"])}{section("Посмотрите категорию подробнее",'<div class="image-gallery"><button data-lightbox aria-label="Увеличить фотографию номера">'+image(p['id'],room_name(p))+'</button><div><h3>Ваш состав гостей — ваш тариф</h3><p>'+beds+'. Укажите всех гостей при поиске. Дополнительные места и детские условия нужно подтвердить до оплаты.</p><p style="margin-top:15px">'+detail+'</p></div></div>')}{section('Перед выбором тарифа',infocards([('Полная стоимость','Итог зависит от дат, числа гостей, питания и условий оплаты. В демонстрации цены не подменяются вымышленными цифрами.'),('Питание и отмена','Проверьте включение завтрака, предоплату и срок отмены. Условия разных тарифов могут отличаться.'),('Ваши пожелания','Нужны отдельные кровати, кроватка или определённый этаж? Уточните возможность подтверждения у отеля.')]))}{section('Вопросы о размещении',faqs(FAQ[:4]))}{section('Сравните другие категории',rooms(ids=others))}</div>'
def rooms_page(p):
 i=room_hotel(p);h=HOTELS[i]
 return '<div class="wrap">'+head('Номера в отеле '+h['full'],'Выберите категорию по кроватям и особенностям. Стоимость проверяется на ваши даты.')+tabs(i,p['id'])+note(h['notice'])+section('Категории номеров',rooms(i))+bottom_booking(i)+'</div>'
def services_page(p):
 i=room_hotel(p);h=HOTELS[i]
 items=[('Питание','Завтрак проверяйте в составе тарифа. Уточните формат и время питания, особенно при раннем выезде.'),('Парковка','До приезда уточните возможность размещения автомобиля, стоимость, въезд и необходимость предварительного согласования.'),('Лифт и багаж','В Таганском нет лифта. Уточните этаж категории и возможную помощь с багажом.' if i=='tagansky' else 'Если важны отсутствие лестниц и доступный вход, сообщите об этом до бронирования и уточните условия выбранной категории.'),('Ранний заезд','Раннее заселение и поздний выезд подтверждаются отдельно и зависят от наличия.'),('Дополнительные места','Возраст детей, диван, дополнительная кровать и кроватка учитываются при подборе. Не все варианты взаимозаменяемы.'),('Связь с отелем','По деталям поездки звоните 8 800 505 44 55. Сообщите название объекта и выбранную категорию.')]
 return '<div class="wrap">'+head('Услуги и условия · '+h['name'],'Практические детали, которые стоит проверить до поездки.')+tabs(i,p['id'])+note(h['notice'])+section('Чтобы всё было понятно заранее',infocards(items))+section('Частые вопросы',faqs())+bottom_booking(i)+'</div>'
def contacts_page(p):
 if p['id']=='contacts':
  from contacts_page import render
  return render(p,globals())
 i=room_hotel(p);h=HOTELS[i]
 from hotel_details import DETAILS
 admin=DETAILS[i]['admin'];admin_tel=''.join(c for c in admin if c.isdigit() or c=='+')
 return '<div class="wrap">'+head('Как добраться · '+h['name'],h['address'])+tabs(i,p['id'])+section('Ваш адрес в Москве','<div class="two-col">'+figure(i,'Фасад '+h['full'],cls='feature-media')+'<div class="prose"><h3>'+h['full']+'</h3><p>'+h['address']+'</p><p>Администратор отеля<br><a href="tel:'+admin_tel+'">'+admin+'</a></p><p>Отдел бронирования<br><a href="tel:88005054455">8 800 505 44 55</a><br><a href="mailto:m-br-1@turris-management.ru">m-br-1@turris-management.ru</a></p>'+ext('https://yandex.ru/maps/?text='+quote('Москва '+h['address']),'Построить маршрут','btn secondary')+'</div></div>')+section('Расположение на карте',maplinks(i))+section('Перед дорогой',infocards([('На общественном транспорте','Постройте маршрут от вашей точки отправления до точного адреса отеля. Выход из метро и переходы проверьте по актуальной карте.'),('На автомобиле','Уточните возможность парковки и место для высадки. Адрес здания не всегда совпадает с въездом на парковку.'),('Позднее прибытие',h['notice']+' Если приезжаете ночью, согласуйте время и порядок входа с отелем.')]))+bottom_booking(i)+'</div>'
def reviews_page(p):
 i=room_hotel(p);h=HOTELS[i]
 links=ext('https://yandex.ru/maps/?text='+quote(h['full']+' '+h['address']),'Найти отель и отзывы на карте','btn secondary')
 if i=='tverskaya':links+=' '+ext('https://www.putevka.com/moskva/moskva/turris-tverskaya','Отзывы на Путёвка','btn secondary')
 return '<div class="wrap">'+head('Отзывы · '+h['name'],'Читайте опыт гостей с учётом даты поездки и выбранной категории.')+tabs(i,p['id'])+section('Смотрите первоисточник','<div class="prose"><p>Расположение, тип кроватей и особенности здания могут быть важнее общей оценки. Смотрите свежие отзывы о конкретном объекте и сравнивайте фотографии той категории, которую выбираете.</p><p>Мы не подменяем отзывы гостей сгенерированными историями или выдуманным рейтингом.</p><p>'+links+'</p></div>')+section('Что проверить перед бронированием',infocards([('Совпадает ли категория','Уточните, о каком номере пишет гость: особенности мансарды или Duplex не относятся ко всему номерному фонду.'),('Когда был отзыв','Условия и услуги могут меняться. Важные для поездки детали подтвердите непосредственно у отеля.'),('Подходит ли вам адрес',h['address']+'. Сравните маршрут с вашими планами, а не только с чужими впечатлениями.')]))+bottom_booking(i)+'</div>'
def lead_form(kind='groups'):
 return f'''<form class="lead-form" data-lead="{kind}"><div class="steps"><span class="current" data-step-label="1">1. Ваша поездка</span><span data-step-label="2">2. Контакт</span></div><h3>Расскажите о поездке</h3><div data-step="1"><div class="form-grid"><label class="field">Заезд<input type="date" name="arrival" required></label><label class="field">Выезд<input type="date" name="departure" required></label><label class="field">Количество гостей<input type="number" name="guests" value="{10 if kind=='groups' else 2}" min="1" max="500" required></label><label class="field">Количество комнат<input type="number" name="rooms" value="{5 if kind=='groups' else 1}" min="1" max="250" required></label><label class="field wide">Предпочтения<textarea name="wishes" placeholder="Например: отдельные кровати, завтрак, гибкие даты"></textarea></label></div><button type="button" class="btn" data-next-step>Далее {icon('arrow')}</button></div><div data-step="2" hidden><div class="form-grid"><label class="field wide">Как к вам обращаться<input name="name" autocomplete="name" placeholder="Имя"></label><label class="field wide">Email для ответа<input type="email" name="email" autocomplete="email" placeholder="name@example.com"></label><label class="field wide">Компания, если есть<input name="company" autocomplete="organization" placeholder="Необязательно"></label></div><label class="consent"><input type="checkbox" name="consent"><span>Я понимаю, что это демонстрация: заявка не отправляется и номера не бронируются. Не вводите реальные персональные данные.</span></label><button type="button" class="btn secondary" data-prev-step>Назад</button> <button class="btn" type="submit">Показать результат {icon('arrow')}</button></div><p class="form-error" aria-live="polite"></p><p class="small" style="margin-top:15px">Демонстрационный расчёт. Для реального запроса: 8 800 505 44 55.</p></form>'''
def commercial(p):
 from offers_page import render
 return render(p,globals())

def offer_page(p):
 from offers_page import render
 return render(p,globals())

def offers_page(p):
 from offers_page import render
 return render(p,globals())

def loyalty_page(p):
 from offers_page import render
 return render(p,globals())

def help_page(p):
 if p['id']=='help':
  return '<div class="wrap">'+head('Чем можем помочь?','Ответы о бронировании, оплате и подготовке к поездке.')+'<form class="search-form search-input" action="'+url('search')+'"><label class="field" style="flex:1">Поиск по сайту<input name="q" type="search" placeholder="Например: отмена бронирования" required></label><button class="btn" type="submit">Найти</button></form>'+section('Выберите тему','<div class="cards3">'+''.join('<div class="info-card"><h3>'+v[0]+'</h3><p>'+v[1]+'</p>'+a(k,'Читать ответ '+icon('arrow'),'text-link')+'</div>' for k,v in HELP.items())+'</div>')+section('Популярные вопросы',faqs())+'</div>'
 if p['id'].endswith('_rules'):
  i=room_hotel(p);h=HOTELS[i]
  return '<div class="wrap">'+head('Правила проживания · '+h['name'],'Проверьте условия объекта и выбранного тарифа до оплаты.')+tabs(i,p['id'])+note(h['notice'])+section('Вопросы перед поездкой',faqs())+'<p>'+ext('https://turris.online/hotels/'+h['slug']+'/','Проверить на официальной странице','btn secondary')+'</p>'+bottom_booking(i)+'</div>'
 title,intro,sections=HELP[p['id']]
 return '<div class="wrap">'+head(title,intro,'Помощь гостю')+'<article class="prose">'+''.join('<section><h2>'+h+'</h2><p>'+t+'</p></section>' for h,t in sections)+'</article>'+section('Если ситуация нестандартная',contact_cards())+'</div>'
def guide_info(b):
 slug=b['url'].strip('/').split('/')[-1];item=ARTICLES[slug];detail=GUIDE[slug]
 words=len((item['answer']+' '+str(item['sections'])+' '+str(detail)).split())
 return slug,item,detail,max(2,math.ceil(words/180))
def guide_asset(b):
 slug,_,detail,_=guide_info(b)
 specific={'family-room-checklist':'tverskaya_room_1','moscow-with-child':'tverskaya_room_4','trip-documents':'petrovsky_room_3','business-location':'petrovsky','group-organizer':'tverskaya_room_3','attic-room':'petrovsky_room_1','twin-double':'tverskaya_room_5','breakfast-rates':'lubyansky_room_5','long-stay-checklist':'petrovsky_room_4','arrival-checklist':'tverskaya','hotel-pets-checklist':'lubyansky'}
 asset=detail.get('hotel') or specific.get(slug,'petrovsky')
 return asset
def blog_card(b):
 slug,item,detail,minutes=guide_info(b)
 search=' '.join([b['title'],item['answer'],RUBRIC_LABELS[b['rubric']],str(detail)]).lower()
 return '<article class="article-card guide-card" data-article data-rubric="'+b['rubric']+'" data-title="'+e(search)+'"><a class="guide-card-image" href="'+url(b['id'])+'" tabindex="-1" aria-hidden="true">'+image(guide_asset(b),'',sizes='(max-width:640px) 400px, 380px')+'</a><div class="article-card-body"><div class="guide-card-meta"><span>'+RUBRIC_LABELS[b['rubric']]+'</span><span>'+str(minutes)+' мин</span></div><h3>'+a(b['id'],b['title'])+'</h3><p>'+e(detail['takeaways'][0])+' '+e(detail['takeaways'][1])+'</p>'+a(b['id'],('Маршрут и советы' if 'stops' in detail else 'Читать руководство')+' '+icon('arrow'),'text-link')+'</div></article>'
RUBRIC_LABELS={'districts':'Районы и маршруты','family':'Москва с детьми','business':'Командировки','stay':'Как подготовиться'}
def blog_page(p):
 from blog_page import render
 return render(p,globals())

def article_page(p):
 from article_page import render
 return render(p,globals())

def booking_page(p):
 from booking_page import render
 return render(p,globals())

def about_page(p):
 if p['id']=='partner':return '<div class="wrap">'+head('Сотрудничество с Туррис','Найдём правильный контакт для вашего запроса.')+section('Выберите направление','<div class="cards3">'+''.join('<div class="info-card"><h3>'+title+'</h3><p>'+text+'</p>'+a(dest,'Перейти '+icon('arrow'),'text-link')+'</div>' for title,text,dest in [('Размещение сотрудников','Договор, документы и поездки от компании.','business'),('Организаторам групп','Даты, состав и предварительный расчёт.','groups'),('Другие вопросы сотрудничества','Свяжитесь с сетью и уточните ответственного по вашему направлению.','contacts')])+'</div>')+'</div>'
 return '<div class="wrap">'+head('Четыре адреса.<br>Одна понятная поездка.','Туррис — отели для работы, отдыха и знакомства с Москвой.')+section('Выбирайте по своим планам','<div class="prose"><p>Тверская, Лубянский, Петровский и Таганский — четыре московских объекта с разным расположением и категориями. Мы предлагаем начать с маршрута поездки, затем выбрать кровати, планировку и подходящий тариф.</p><p>Условия питания, парковки, дополнительных мест и отмены нужно проверять для конкретного объекта и бронирования.</p></div>')+hotel_grid()+section('Если вы едете в Санкт-Петербург','<div class="prose"><p>Гостиница «Россия» представлена на отдельном официальном сайте. Она не относится к четырём московским адресам этого каталога.</p><p>'+ext('https://rossiya-hotel.ru/','Гостиница «Россия», Санкт-Петербург','btn secondary')+'</p></div>')+section('Открытая информация','<p>'+a('legal','Правовая информация')+' · '+a('contacts','Контакты')+' · '+a('help','Помощь гостю')+'</p>')+'</div>'
def legal_page(p):
 title=p['h1']
 return '<div class="wrap">'+head(title,'Информация о демонстрационном сайте.')+'<article class="prose"><h2>Назначение прототипа</h2><p>Этот сайт демонстрирует структуру и интерфейс будущего сайта отелей Туррис. Интерфейс сайта является прототипом. Встроенный модуль TravelLine подключён к действующим отелям: цены, наличие, оформление и оплата в нём настоящие.</p><h2>Формы и локальные настройки</h2><p>Даты, количество гостей и выбранная категория сохраняются в пределах вкладки браузера для работы демонстрации. Формы запроса показывают результат на экране и не отправляют введённые данные отелю или в CRM. Не вводите реальные персональные данные в демонстрационные формы обращений. Данные для настоящего бронирования вводятся только в модуле TravelLine и обрабатываются его сервисом и выбранным отелем по условиям, указанным в модуле.</p><h2>Изображения и источники</h2><p>Фотографии фасадов и категорий взяты с официального сайта turris.online. Иллюстрации концепции интерьера и гида созданы с помощью ИИ и обозначены в интерфейсе. Они не подтверждают оснащение, планировку или вид из окна конкретного номера.</p><h2>Реальное бронирование</h2><p>Для действующих правил, реквизитов и условий используйте официальный сайт. Юридические документы будущего сайта должны соответствовать его фактическим процессам и быть утверждены ответственным лицом.</p><p>'+ext('https://turris.online/pravovaya-informatsiya/','Официальная правовая информация','btn secondary')+'</p><h2>Внешние сервисы</h2><p>Прототип размещён на GitHub Pages. При открытии результатов бронирования загружается внешний модуль TravelLine, который может использовать свои cookies и технические идентификаторы. Платёжные и контактные данные модуль обрабатывает самостоятельно; код прототипа их не сохраняет. Карты и официальный сайт также работают по собственным условиям.</p></article>'+section('Нужен ответ по поездке?',contact_cards())+'</div>'
def utility_page(p):
 if p['id']=='search':return '<div class="wrap">'+head('Найдите нужную страницу','Поиск по отелям, номерам, справке и гиду.')+'<form class="search-form" data-site-search><label class="field" style="flex:1">Ваш запрос<input name="q" type="search" placeholder="Например: семейный номер" required></label><button class="btn">Найти '+icon('search')+'</button></form><div class="search-results section" data-search-results aria-live="polite"></div></div>'
 if p['id']=='manage':return '<div class="wrap">'+head('Управление бронированием','Начните с письма, которое получили после оформления.')+section('Ваша бронь — в подтверждении',infocards([('Найдите письмо','Проверьте почту и папку нежелательных писем. В подтверждении указаны отель, даты, тариф и условия.'),('Откройте управление','Используйте ссылку из подтверждения или свяжитесь с отелем. Не вводите номер брони и личные данные на демонстрационном сайте.'),('Проверьте изменение','Отмена и перенос зависят от тарифа. Перед повторной оплатой уточните статус первой операции.')]))+section('Связаться с отелем',contact_cards())+'</div>'
 if p['id']=='thanks':return '<div class="wrap">'+head('Так выглядит результат заявки','Демонстрационное состояние: данные не отправлены.')+note('Для реального запроса свяжитесь с выбранным отелем. Демонстрационная заявка не резервирует номера. Для бронирования используйте TravelLine в разделе бронирования.')+'<p>'+a('hotels','Вернуться к отелям','btn')+'</p></div>'
 return '<div class="wrap">'+head('Эта страница не найдена','Продолжите выбор отеля или найдите ответ в справке.')+'<div class="scenario-links">'+a('hotels','Выбрать отель')+a('help','Помощь')+a('search','Поиск по сайту')+'</div>'+section('Четыре адреса в Москве',hotel_grid())+'</div>'

RENDER={'home':home,'catalog':catalog,'hotel':hotel_page,'room':room_page,'rooms':rooms_page,'services':services_page,'contacts':contacts_page,'reviews':reviews_page,'family':commercial,'business':commercial,'groups':commercial,'longstay':commercial,'offer':offer_page,'offers':offers_page,'loyalty':loyalty_page,'help':help_page,'blog':blog_page,'article':article_page,'booking':booking_page,'about':about_page,'legal':legal_page,'utility':utility_page}
def header(p):
 from navigation import header as render_header
 return render_header(p,globals())

def footer(p=None):
 from navigation import footer as render_footer
 return render_footer(globals())

def dialogs():
 return '''<dialog aria-label="Когда вы приедете?" id="dates-dialog"><button class="dialog-close" data-close aria-label="Закрыть">×</button><h2>Когда вы приедете?</h2><form id="dates-form"><div class="form-grid date-grid"><label class="field">Заезд<input type="date" name="checkin" aria-describedby="dates-error" required></label><label class="field">Выезд<input type="date" name="checkout" aria-describedby="dates-error" required></label></div><p class="form-error" id="dates-error" aria-live="polite"></p><div class="dialog-actions"><button class="btn secondary" type="button" data-close>Отмена</button><button class="btn" type="submit">Применить</button></div></form></dialog>
 <dialog aria-label="Кто едет с вами?" id="guests-dialog"><button class="dialog-close" data-close aria-label="Закрыть">×</button><h2>Кто едет с вами?</h2><div class="guest-row"><div>Взрослые<div class="small">От 18 лет</div></div><div class="stepper"><button data-count="adults" data-change="-1" aria-label="Убрать взрослого">−</button><span data-count-value="adults">2</span><button data-count="adults" data-change="1" aria-label="Добавить взрослого">+</button></div></div><div class="guest-row"><div>Дети<div class="small">Укажите возраст каждого</div></div><div class="stepper"><button data-count="children" data-change="-1" aria-label="Убрать ребёнка">−</button><span data-count-value="children">0</span><button data-count="children" data-change="1" aria-label="Добавить ребёнка">+</button></div></div><div class="ages"></div><p class="form-error" id="guests-error" role="alert"></p><p class="modal-note">Условия размещения и дополнительные места зависят от возраста и категории номера.</p><div class="dialog-actions"><button class="btn secondary" type="button" data-close>Отмена</button><button class="btn" data-save-guests>Готово</button></div></dialog>
 <dialog aria-label="Демонстрационный сайт" id="demo-dialog"><button class="dialog-close" data-close aria-label="Закрыть">×</button><h2>Прототип для знакомства</h2><p>Можно выбрать даты и гостей, сравнить отели, посмотреть номера и пройти демонстрацию заявки.</p><p class="modal-note">В разделе бронирования подключён действующий TravelLine: цены, наличие и оформление настоящие. Формы обращений вне TravelLine демонстрационные и не отправляют заявки. Сгенерированные изображения отмечены как иллюстрации концепции.</p><div class="dialog-actions"><button class="btn" data-close>Посмотреть сайт</button></div></dialog>
 <dialog aria-label="Фотография номера" id="lightbox-dialog" class="lightbox"><button class="dialog-close" data-close aria-label="Закрыть фотографию">×</button><img alt="Фотография номера крупно"></dialog>'''
def breadcrumbs(p):
 if p['id']=='home':return ''
 parents=[];pid=p['parent']
 while pid:
  pp=PAGES[pid];parents.insert(0,a(pid,'Главная' if pid=='home' else 'Отели' if pid=='hotels' else 'Гид по Москве' if pid=='blog' else pp['h1'].split(' — ')[0]));pid=pp['parent']
 return '<div class="wrap"><nav class="breadcrumbs" aria-label="Хлебные крошки">'+'<span>/</span>'.join(parents)+('<span>/</span>' if parents else '')+'<span>'+e(room_name(p) if p['template']=='room' else 'Гид по Москве' if p['id']=='blog' else p['h1'])+'</span></nav></div>'
def build():
 shutil.copytree(ROOT/'assets',DIST/'assets',dirs_exist_ok=True)
 reportdir=DIST/'research';reportdir.mkdir(exist_ok=True)
 for name in ['premium-design-research.html','global-ux-audit.html']:
  if (ROOT/'docs'/name).exists():shutil.copy2(ROOT/'docs'/name,reportdir/name)
 public=[]
 for p in PAGES.values():
  body=RENDER[p['template']](p)
  body=body.replace('<br>', '<br> ').replace('6 категории','6 категорий').replace('7 категории','7 категорий')
  if p['id']=='groups':body=body.replace('two-col section-sm','two-col section-sm group-layout')
  title='Отели Туррис в центре Москвы — демонстрационный сайт' if p['id']=='home' else (room_name(p) if p['template']=='room' else p['h1'])+' | Туррис · прототип'
  schema={'@context':'https://schema.org','@type':'WebPage','name':title,'description':'Демонстрационный прототип сайта отелей Туррис.'}
  if p['id']=='contacts':schema['@type']='ContactPage'
  if p['template']=='article':
   schema.update({'@type':'BlogPosting','headline':p['h1'],'dateModified':'2026-10-29','author':{'@type':'Organization','name':'Редакция прототипа Туррис'},'inLanguage':'ru','description':ARTICLES[p['url'].strip('/').split('/')[-1]]['answer']})
  doc='<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><script>document.documentElement.classList.add("js")</script><link rel="preload" href="'+BASE+'/assets/fonts/Manrope.woff2" as="font" type="font/woff2" crossorigin><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#0758b9"><title>'+e(title)+'</title><meta name="description" content="'+e(p['description'])+'"><meta property="og:title" content="'+e(title)+'"><meta property="og:description" content="Демонстрационный сайт: четыре отеля в Москве, номера, предложения и гид."><meta property="og:type" content="website"><meta property="og:image" content="https://moriarty32.github.io/turris-prototype/assets/hero-room-v2.png"><link rel="icon" href="'+BASE+'/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="'+BASE+'/assets/site.css?v=images-1"><link rel="stylesheet" href="'+BASE+'/assets/premium.css?v=images-1"><link rel="stylesheet" href="'+BASE+'/assets/layout.css?v=images-1"><script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script><script>window.SITE_BASE='+json.dumps(BASE)+';</script><script src="'+BASE+'/assets/site.js?v=live-booking-1" defer></script><script src="'+BASE+'/assets/calendar.js?v=redesign-1" defer></script><script src="'+BASE+'/assets/experience.js?v=map-attribution-2" defer></script></head><body class="ux-site" data-page="'+p['id']+'" data-template="'+p['template']+'">'+header(p)+breadcrumbs(p)+'<main id="main">'+body+'</main>'+footer(p)+dialogs()+'</body></html>'
  if p['template'] in ['blog','article']:
   doc=doc.replace('</head>','<link rel="stylesheet" href="'+BASE+'/assets/guide.css?v=images-1"><script src="'+BASE+'/assets/guide.js?v=article-1" defer></script></head>')
  doc=doc.replace('</head>','<link rel="stylesheet" href="'+BASE+'/assets/media.css?v=images-1"></head>')
  if p['template']=='hotel':
   doc=doc.replace('</head>','<link rel="stylesheet" href="'+BASE+'/assets/hotel-detail.css?v=hotel-1"><script src="'+BASE+'/assets/hotel-detail.js?v=hotel-1" defer></script></head>')
  if p['template']=='booking':
   doc=doc.replace('</head>','<link rel="stylesheet" href="'+BASE+'/assets/booking.css?v=live-booking-1"><script src="'+BASE+'/assets/booking.js?v=live-booking-1" defer></script></head>')
  if p['template'] in OFFER_TEMPLATES:
   doc=doc.replace('</head>','<link rel="stylesheet" href="'+BASE+'/assets/offers.css?v=offers-1"><script src="'+BASE+'/assets/offers.js?v=offers-1" defer></script></head>')
  if p['template']=='article':
   doc=doc.replace('</head>','<link rel="stylesheet" href="'+BASE+'/assets/article.css?v=article-1"><script src="'+BASE+'/assets/article.js?v=system-1" defer></script></head>')
  if p['id']=='contacts':
   doc=doc.replace('</head>','<link rel="stylesheet" href="'+BASE+'/assets/contacts.css?v=contacts-1"><script src="'+BASE+'/assets/contacts.js?v=contacts-1" defer></script></head>')
  if p['id']=='home':
   doc=doc.replace('</head>','<link rel="stylesheet" href="'+BASE+'/assets/home.css?v=adaptive-hero-4"><script src="'+BASE+'/assets/home.js?v=home-slider-2" defer></script></head>')
  doc=doc.replace('</head>','<link rel="stylesheet" href="'+BASE+'/assets/design-system.css?v=forms-3"><script src="'+BASE+'/assets/design-system.js?v=system-1" defer></script></head>')
  if p['template']=='blog':
   doc=doc.replace('</head>','<link rel="stylesheet" href="'+BASE+'/assets/journal.css?v=journal-1"><script src="'+BASE+'/assets/journal.js?v=journal-1" defer></script></head>')
  doc=doc.replace('</head>','<script src="'+BASE+'/assets/selects.js?v=selects-1" defer></script></head>')
  path=DIST/p['url'].strip('/')/'index.html';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(doc,encoding='utf-8')
  public.append({'id':p['id'],'url':p['url'],'title':room_name(p) if p['template']=='room' else p['h1'],'type':p['template'],'hotel':next((i for i in HOTELS if p['id'].startswith(i)),None),'image':ASSETS.get(p['id'],{}).get('file'),'summary':p['intent']})
 (DIST/'site-data.json').write_text(json.dumps({'pages':public,'hotels':HOTELS},ensure_ascii=False),encoding='utf-8')
 (DIST/'404.html').write_text((DIST/'404/index.html').read_text(encoding='utf-8'),encoding='utf-8')
 (DIST/'.nojekyll').write_text('',encoding='utf-8')
 # PDFs cannot carry HTML noindex on GitHub Pages; retain the source in docs only.
 (reportdir/'Turris-premium-design-research.pdf').unlink(missing_ok=True)
 # Apply to every published HTML artifact, including reports, widgets and 404 pages.
 robots='<meta name="robots" content="noindex,nofollow,noimageindex,nosnippet">'
 for page in DIST.rglob('*.html'):
  markup=page.read_text(encoding='utf-8')
  if re.search(r'<meta\b[^>]*name=[\"\']robots[\"\'][^>]*>',markup,re.I):
   markup=re.sub(r'<meta\b[^>]*name=[\"\']robots[\"\'][^>]*>',robots,markup,flags=re.I)
  else:
   markup=markup.replace('<head>','<head>'+robots,1)
  if robots not in markup:raise RuntimeError('Missing indexing protection: '+str(page))
  page.write_text(markup,encoding='utf-8')
 (DIST/'robots.txt').write_text('User-agent: *\nDisallow:\n# Indexing is disabled through robots meta on every HTML page.\n# Crawling must remain allowed so robots can read noindex.\n# This project-path robots.txt is informational; host-root rules take precedence.\n',encoding='utf-8')
 (ROOT/'docs/build-report.json').write_text(json.dumps({'pages':len(public),'templates':len(RENDER),'base':BASE,'generated_assets':4,'documentary_assets':len(ASSETS),'mode':'prototype-with-live-travelline-booking-demo-contact-forms','indexing':'noindex'},ensure_ascii=False,indent=2),encoding='utf-8')
 print('Built',len(public),'pages,',len(RENDER),'templates')
if __name__=='__main__':build()
