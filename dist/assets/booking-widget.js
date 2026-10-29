/* Public hotel-owned TravelLine contexts. No API credentials or payment handling here. */
(() => {
 'use strict';
 const contexts={tverskaya:'turris-hotel-tverskaya',lubyansky:'turris-hotel-lubyansky-',petrovsky:'turris-hotel-petrovsky',tagansky:'turris-hotel-tagansky'};
 const query=new URLSearchParams(location.search), hotel=query.get('hotel');
 const send=(type,extra={})=>parent.postMessage({source:'turris-booking',type,...extra},location.origin);
 if(!Object.hasOwn(contexts,hotel)){document.querySelector('#tl-booking-form').textContent='Выберите отель.';send('error');return;}
 let lastHeight=0,ready=false;
 function resize(){
  // TravelLine uses an absolutely positioned container on mobile. Body height can be zero.
  // Measure the actual provider frame, not a viewport-sized wrapper (which prevents shrinking).
  const main=[...document.querySelectorAll('#tl-booking-form iframe')].find(f=>/\/booking2\//.test(f.src)&&!f.src.includes('/s/cart'));
  const rect=main?.getBoundingClientRect();
  const height=Math.ceil(rect?rect.bottom+scrollY:document.body.getBoundingClientRect().height);
  if(height>0&&height!==lastHeight){lastHeight=height;send('height',{height});}
 }
 const observer=new ResizeObserver(resize);observer.observe(document.body);
 const container=document.querySelector('#tl-booking-form');
 new MutationObserver(()=>{
  container.querySelectorAll('iframe').forEach(frame=>{
   if(frame.dataset.observed)return;frame.dataset.observed='true';observer.observe(frame);
   frame.addEventListener('load',()=>{if(!ready&&/\/booking2\//.test(frame.src)){ready=true;send('ready');}resize();});
  });resize();
 }).observe(container,{childList:true,subtree:true});
 window.travelline={integration:{__cq:[
  ['setContext','TL-INT-hotels-turris.'+contexts[hotel],'ru'],
  ['embed','booking-form',{container:'tl-booking-form',onBookingStepChanged:data=>{
   if(['search','preview','payment','complete'].includes(data?.step))send('step',{step:data.step});
  },onNoAvailableRooms:()=>send('empty')}]
 ]}};
 const hosts=['ru-ibe.tlintegration.ru','ibe.tlintegration.ru','ibe.tlintegration.com'];
 function load(index){if(index>=hosts.length){send('error');return;}const script=document.createElement('script');script.src='https://'+hosts[index]+'/integration/loader.js';script.async=true;script.onerror=()=>load(index+1);document.head.append(script);}
 load(0);resize();
})();
