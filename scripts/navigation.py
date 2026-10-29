"""One navigation contract for every page, including booking and service pages."""
def header(p,g):
 a,icon,url=g['a'],g['icon'],g['url'];hotels=g['HOTELS']
 def link(pid,label,cls=''):
  return a(pid,label,cls,'aria-current="page"' if p['id']==pid else '')
 def column(title,items):return '<section class="ux-menu-column"><h2>'+title+'</h2>'+''.join(link(pid,label) for pid,label in items)+'</section>'
 def group(key,label,content,active):
  return '<details class="nav-group'+(' current' if active else '')+'" data-nav-section="'+key+'"><summary>'+label+icon('chevron')+'</summary><div class="drop ux-mega"><div class="ux-menu-heading"><span>'+label+'</span><span>Четыре адреса. Ваша Москва.</span></div>'+content+'</div></details>'
 hotel_cols=''
 for hid,h in hotels.items():
  hotel_cols+=column(h['name'],[(hid,'Об отеле'),(hid+'_rooms','Номера и цены'),(hid+'_services','Услуги'),(hid+'_contacts','Как добраться'),(hid+'_reviews','Отзывы'),(hid+'_rules','Правила проживания'),(hid+'_booking','Бронирование')])
 hotel_intro='<div class="ux-menu-shortcuts">'+link('hotels','Сравнить четыре отеля')+'<a href="'+url('home')+'#map">Отели на карте</a>'+link('booking','Выбрать даты и номер')+'</div>'
 hotel_active=p['template'] in ['hotel','rooms','room','services','reviews'] or p['id']=='hotels' or any(p['id']==hid+suffix for hid in hotels for suffix in ['_contacts','_rules','_booking'])
 nav=group('hotels','Отели',hotel_intro+'<div class="ux-menu-grid">'+hotel_cols+'</div>',hotel_active)
 offer_cols=column('Для вашей поездки',[('offers','Все предложения'),('family','Семейное размещение'),('longstay','Проживание от 21 дня'),('offer_9','Раннее бронирование'),('offer_7','Предложение ко дню рождения')])
 offer_cols+=column('Условия акций',[('offer_2','Предложение Лубянского'),('offer_3','Размещение четырёх гостей'),('offer_5','Оплата онлайн · Петровский'),('offer_8','Осеннее предложение')])
 offer_cols+=column('С питомцем',[('offer_10','Тверская'),('offer_1','Лубянский'),('offer_4','Петровский'),('offer_6','Таганский'),('help_pets','Правила размещения')])
 offer_cols+=column('Лояльность',[('loyalty','Туррис-Бонус'),('loyalty_standard','Standard'),('loyalty_platinum','Platinum'),('loyalty_aeroflot','Аэрофлот Бонус')])
 nav+=group('offers','Предложения','<div class="ux-menu-grid">'+offer_cols+'</div>',p['template'] in ['offers','offer','family','longstay','loyalty'])
 business=column('Для организаций',[('business','Командировки и компании'),('groups','Размещение групп'),('partner','Сотрудничество')])+column('Подготовка поездки',[('blog_business','Гид для деловой поездки'),('payment','Оплата проживания'),('contacts','Связаться с отелем')])
 nav+=group('business','Для компаний','<div class="ux-menu-grid ux-menu-two">'+business+'</div>',p['template'] in ['business','groups'])
 guide=column('Планируйте поездку',[('blog','Все статьи гида'),('blog_districts','Районы и маршруты'),('blog_family','Поездка с детьми'),('blog_business','Деловая поездка'),('blog_stay','Номера и проживание')])+column('С чего начать',[('blog_choose-area','Как выбрать район Москвы') if 'blog_choose-area' in g['PAGES'] else (next(x['id'] for x in g['PAGES'].values() if x['url']=='/blog/choose-area/'),'Как выбрать район Москвы'),('hotels','Сравнить отели'),('family','Подобрать семейный номер')])
 nav+=group('guide','Гид по Москве','<div class="ux-menu-grid ux-menu-two">'+guide+'</div>',p['template'] in ['blog','article'])
 about=column('Сеть Туррис',[('about','О сети'),('partner','Сотрудничество'),('contacts','Контакты')])+column('Помощь гостям',[('help','Все вопросы и ответы'),('help_booking','Как забронировать'),('help_cancel','Изменение и отмена'),('help_checkin','Заезд и документы'),('help_children','Размещение детей'),('help_pets','Размещение с питомцем'),('payment','Оплата')])+column('Документы',[('legal','Правовая информация'),('privacy','Конфиденциальность'),('consent','Обработка данных')])
 nav+=group('about','О сети','<div class="ux-menu-grid ux-menu-three">'+about+'</div>',p['id'] in ['about','partner','legal','privacy','consent'] or (p['template']=='help' and not hotel_active))
 nav+=link('contacts','Контакты','nav-direct'+(' current' if p['id']=='contacts' else ''))
 mobile='<div class="mobile-utility">'+link('search',icon('search')+'Поиск')+link('help',icon('headset')+'Помощь')+link('manage',icon('calendar')+'Моя бронь')+'<a href="tel:88005054455">'+icon('phone')+'8 800 505 44 55</a></div>'
 utility='<div class="ux-utility wrap"><span>Четыре адреса. Ваша Москва.</span><div>'+link('search',icon('search')+'Поиск')+link('help',icon('headset')+'Помощь')+link('manage',icon('calendar')+'Моя бронь')+'<a class="header-phone" href="tel:88005054455">'+icon('phone')+'8 800 505 44 55</a><button class="demo-badge" data-demo-info>ДЕМО</button></div></div>'
 return '<a class="skip" href="#main">Перейти к содержанию</a><header class="header ux-header">'+utility+'<div class="wrap header-inner"><div class="brand-block">'+link('home','TURRIS<span>ONLINE</span><i></i>','logo')+'</div><nav class="nav" id="main-nav" aria-label="Основное меню">'+nav+mobile+'</nav>'+link('booking','Выбрать номер '+icon('arrow'),'btn header-booking')+'<button class="menu-button" type="button" aria-label="Открыть меню" aria-expanded="false" aria-controls="main-nav">'+icon('menu')+'<span>Меню</span></button></div></header>'

def footer(g):
 a,icon,ext=g['a'],g['icon'],g['ext']
 def col(title,items):return '<div><h2>'+title+'</h2><div class="footer-links">'+''.join(a(pid,label) for pid,label in items)+'</div></div>'
 brand='<div>'+a('home','TURRIS<span>ONLINE</span><i></i>','logo')+'<p>Четыре отеля в Москве</p><a class="ux-footer-phone" href="tel:88005054455">'+icon('phone')+'8 800 505 44 55</a>'+a('contacts','Адреса и контакты','text-link')+'</div>'
 cols=col('Отели',[(hid,h['name']) for hid,h in g['HOTELS'].items()]+[('hotels','Сравнить отели')])+col('Для гостей',[('offers','Предложения'),('family','Семейное размещение'),('loyalty','Лояльность'),('blog','Гид по Москве'),('help','Помощь'),('manage','Моя бронь')])+col('Сеть Туррис',[('about','О сети'),('business','Для компаний'),('groups','Размещение групп'),('partner','Сотрудничество'),('contacts','Контакты')])
 return '<footer class="footer ux-footer"><div class="wrap"><div class="footer-top">'+brand+cols+'</div><div class="ux-footer-external">'+ext('https://rossiya-hotel.ru/','Гостиница «Россия», Санкт-Петербург')+'</div><div class="footer-bottom"><span>© 2026 Туррис · Демонстрационный прототип</span><div>'+a('privacy','Конфиденциальность')+a('legal','Правовая информация')+a('consent','Обработка данных')+a('search','Поиск')+'</div></div><p class="footer-note">Демонстрация дизайна и сценариев. Цены и наличие не подключены, заявки не отправляются. Фотографии отелей и категорий — с turris.online; изображения, созданные с помощью ИИ, подписаны. Реальное бронирование — на официальном сайте.</p></div></footer>'
