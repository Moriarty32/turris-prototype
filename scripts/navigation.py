"""Shared three-zone header, disclosure navigation and three-column footer."""
def logo(g):
 return '<img src="'+g['BASE']+'/assets/turris-logo.png" width="333" height="120" alt="Туррис Онлайн">'

def header(p,g):
 a,icon,url=g['a'],g['icon'],g['url']
 def link(pid,label,cls=''):
  return a(pid,label,cls,'aria-current="page"' if p['id']==pid else '')
 sections=[('hotels','Отели'),('offers','Предложения'),('family','Семейные поездки'),('business','Для компаний'),('blog','Гид по Москве'),('about','О сети'),('contacts','Контакты')]
 primary='<ul class="menu-primary">'+''.join('<li>'+link(pid,label)+'</li>' for pid,label in sections)+'</ul>'
 extra=[('longstay','Проживание от 21 дня'),('groups','Размещение групп'),('loyalty','Туррис-Бонус'),('partner','Сотрудничество'),('payment','Оплата'),('legal','Документы и условия')]
 primary+='<details class="menu-more"><summary>Другие разделы '+icon('chevron')+'</summary><div>'+''.join(link(pid,label) for pid,label in extra)+'</div></details>'
 cards=''
 for hid,h in g['HOTELS'].items():
  cards+='<article class="menu-hotel">'+link(hid,g['image'](hid,'Фасад · '+h['name'],sizes='(max-width:767px) 260px, 320px')+'<span>'+h['name']+'</span>','menu-hotel-cover')+'<p>'+h['address']+'</p><div>'+link(hid+'_rooms','Номера')+link(hid+'_contacts','Как добраться')+'</div></article>'
 utilities=''.join(link(pid,icon(ic)+label) for pid,label,ic in [('search','Поиск','search'),('help','Помощь','headset'),('manage','Моя бронь','calendar')])+'<a href="tel:88005054455">'+icon('phone')+'8 800 505 44 55</a>'
 nav='<nav id="main-nav" class="site-menu" aria-label="Основное меню"><div class="wrap menu-content"><div class="menu-layout"><div>'+primary+'</div><div class="menu-hotels">'+cards+'</div></div><div class="menu-utility">'+utilities+link('booking','Выбрать номер '+icon('arrow'),'btn menu-booking')+'</div></div></nav>'
 bar='<div class="wrap header-inner"><div class="header-start"><button class="menu-button" type="button" aria-expanded="false" aria-controls="main-nav">'+icon('menu')+'<span>Меню</span></button>'+link('hotels','Отели','header-hotels')+'</div>'+link('home',logo(g),'logo')+'<div class="header-end"><a class="header-phone" href="tel:88005054455" aria-label="Позвонить: 8 800 505 44 55">'+icon('phone')+'<span>8 800 505 44 55</span></a>'+link('booking','Выбрать номер '+icon('arrow'),'btn header-booking')+'</div></div>'
 return '<a class="skip" href="#main">Перейти к содержанию</a><header class="header ux-header">'+bar+nav+'</header>'

def footer(g):
 a,icon,ext=g['a'],g['icon'],g['ext']
 def col(title,items):return '<div><h2>'+title+'</h2><div class="footer-links">'+''.join(a(pid,label) for pid,label in items)+'</div></div>'
 brand='<div class="footer-brand">'+a('home',logo(g),'logo')+'<p>Четыре отеля в Москве</p><a class="ux-footer-phone" href="tel:88005054455">'+icon('phone')+'8 800 505 44 55</a><a href="mailto:m-br-1@turris-management.ru">m-br-1@turris-management.ru</a></div>'
 cols=col('Отели',[(hid,h['name']) for hid,h in g['HOTELS'].items()]+[('hotels','Сравнить отели')])+col('Для гостей',[('offers','Предложения'),('family','Семейные поездки'),('longstay','Длительное проживание'),('loyalty','Лояльность'),('blog','Гид по Москве'),('help','Помощь'),('manage','Моя бронь'),('payment','Оплата')])+col('Сеть Туррис',[('about','О сети'),('business','Для компаний'),('groups','Размещение групп'),('partner','Сотрудничество'),('contacts','Контакты')])
 return '<footer class="footer ux-footer"><div class="wrap">'+brand+'<div class="footer-top">'+cols+'</div><div class="ux-footer-external">'+ext('https://rossiya-hotel.ru/','Гостиница «Россия», Санкт-Петербург')+'</div><div class="footer-bottom"><span>© 2026 Туррис · Демонстрационный прототип</span><div>'+a('privacy','Конфиденциальность')+a('legal','Правовая информация')+a('consent','Обработка данных')+a('search','Поиск')+'</div></div><p class="footer-note">Демонстрационный сайт. Цены, наличие, оформление и оплата в модуле TravelLine — действующие. Формы обращений вне модуля демонстрационные: заявки не отправляются. Фотографии отелей и категорий — с turris.online; изображения, созданные с помощью ИИ, подписаны. Бронирование также доступно на официальном сайте turris.online.</p></div></footer>'
