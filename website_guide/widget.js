(() => {
  if(document.getElementById('astreb-guide')) return;
  const i18n={
    en:{open:'Ask ASTREB',close:'Close',intro:'Find the right service. Ask a question or explore a topic.',placeholder:'What would you like to know?',send:'Ask',offline:'AI is not connected. Browse verified website information below.',online:'AI assistant · Answers may contain mistakes.',privacy:'Questions are sent to OpenAI for an answer. Do not enter private or sensitive information.',error:'An AI answer is unavailable right now. You can still browse the topics or contact ASTREB.',busy:'Preparing an answer…',source:'Website source',show:'Show section',contact:'Open email draft',draft:'Your email app will open. Review the text before sending.',missing:'This section is not available on this page.',clear:'Clear conversation',label:'Language'},
    nl:{open:'Vraag ASTREB',close:'Sluiten',intro:'Vind de juiste dienst. Stel een vraag of bekijk een onderwerp.',placeholder:'Wat wil je weten?',send:'Vraag',offline:'AI is niet verbonden. Bekijk hieronder geverifieerde website-informatie.',online:'AI-assistent · Antwoorden kunnen fouten bevatten.',privacy:'Vragen worden naar OpenAI gestuurd voor een antwoord. Voer geen privégegevens of gevoelige informatie in.',error:'Een AI-antwoord is nu niet beschikbaar. Je kunt nog onderwerpen bekijken of contact opnemen.',busy:'Antwoord wordt voorbereid…',source:'Bron op de website',show:'Toon onderdeel',contact:'Open e-mailconcept',draft:'Je e-mailprogramma wordt geopend. Controleer de tekst voordat je deze verstuurt.',missing:'Dit onderdeel is niet beschikbaar op deze pagina.',clear:'Gesprek wissen',label:'Taal'},
    ru:{open:'Спросить ASTREB',close:'Закрыть',intro:'Найдите подходящую услугу. Задайте вопрос или выберите тему.',placeholder:'Что вы хотите узнать?',send:'Спросить',offline:'ИИ не подключён. Ниже доступна проверенная информация с сайта.',online:'ИИ-помощник · В ответах возможны ошибки.',privacy:'Вопросы передаются OpenAI для подготовки ответа. Не вводите личную или конфиденциальную информацию.',error:'Ответ ИИ сейчас недоступен. Можно посмотреть темы или связаться с ASTREB.',busy:'Готовлю ответ…',source:'Источник на сайте',show:'Показать раздел',contact:'Открыть черновик письма',draft:'Откроется почтовая программа. Проверьте текст перед отправкой.',missing:'Этого раздела нет на текущей странице.',clear:'Очистить диалог',label:'Язык'}
  };
  let lang=['nl','ru'].includes(navigator.language.slice(0,2))?navigator.language.slice(0,2):'en';
  let history=[],knowledge=null,mode='offline',pending=false,controller=null;
  const script=document.currentScript;
  const endpoint=new URL(script?.dataset.endpoint || '/guide/api/',location.href);
  if(endpoint.origin!==location.origin) return; // Same-origin reverse proxy only.
  const host=document.createElement('div');host.id='astreb-guide';document.body.append(host);
  const launch=document.createElement('button');launch.className='ag-launch';host.append(launch);
  const panel=document.createElement('aside');panel.className='ag-panel';panel.hidden=true;panel.setAttribute('aria-label','ASTREB Guide');host.append(panel);
  const header=document.createElement('header');header.className='ag-header';panel.append(header);
  const brand=document.createElement('strong');brand.textContent='ASTREB Guide';header.append(brand);
  const language=document.createElement('select');['nl','en','ru'].forEach(l=>{const o=document.createElement('option');o.value=l;o.textContent=l.toUpperCase();language.append(o);});header.append(language);
  const close=document.createElement('button');close.textContent='×';header.append(close);
  const status=document.createElement('p');status.className='ag-status';panel.append(status);
  const log=document.createElement('div');log.className='ag-log';log.setAttribute('role','log');log.setAttribute('aria-live','polite');panel.append(log);
  const topics=document.createElement('div');topics.className='ag-topics';panel.append(topics);
  const privacy=document.createElement('p');privacy.className='ag-note';panel.append(privacy);
  const form=document.createElement('form');form.className='ag-form';panel.append(form);
  const input=document.createElement('textarea');input.rows=2;input.maxLength=1500;input.required=true;form.append(input);
  const send=document.createElement('button');send.type='submit';form.append(send);
  const footer=document.createElement('div');footer.className='ag-footer';panel.append(footer);
  const clear=document.createElement('button');clear.type='button';footer.append(clear);
  const contact=document.createElement('a');contact.href='mailto:info@astreb.nl';footer.append(contact);
  function message(text,who='assistant') {const p=document.createElement('p');p.className='ag-message '+who;p.textContent=text;log.append(p);p.scrollIntoView({block:'nearest'});return p;}
  const allowed=['strategy','integration','workshops','contact'];
  function section(id) {
    if(!allowed.includes(id)) return null;
    const marked=document.querySelector(`[data-guide-section="${id}"]`);
    if(marked) return marked;
    if(id==='contact') return document.querySelector('a[href="mailto:info@astreb.nl"]');
    const title={strategy:'AI Strategy',integration:'Integration',workshops:'Workshops'}[id];
    return [...document.querySelectorAll('h2,h3')].find(e=>e.textContent.trim()===title) || null;
  }
  function navigate(id) {
    const target=section(id);
    if(!target) {message(i18n[lang].missing);return;}
    panel.hidden=true;launch.setAttribute('aria-expanded','false');
    target.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'center'});
    const old=target.getAttribute('tabindex');target.setAttribute('tabindex','-1');target.focus({preventScroll:true});
    target.classList.add('ag-highlight');setTimeout(()=>{target.classList.remove('ag-highlight');if(old===null)target.removeAttribute('tabindex');else target.setAttribute('tabindex',old);},2500);
  }
  function sourceButtons(sourceIds) {
    for(const id of sourceIds) {const e=knowledge?.entries.find(e=>e.id===id);if(!e)continue;
      const b=document.createElement('button');b.type='button';b.className='ag-source';b.textContent=`${i18n[lang].show}: ${e.title}`;b.onclick=()=>navigate(id);log.append(b);
    }
  }
  function render() {
    const t=i18n[lang];host.lang=lang;language.value=lang;language.setAttribute('aria-label',t.label);launch.textContent=t.open;close.setAttribute('aria-label',t.close);
    status.textContent=mode==='ai'?t.online:t.offline;privacy.textContent=mode==='ai'?t.privacy:'';
    input.placeholder=t.placeholder;input.setAttribute('aria-label',t.placeholder);input.disabled=mode!=='ai'||pending;send.disabled=mode!=='ai'||pending;send.textContent=pending?t.busy:t.send;clear.textContent=t.clear;contact.textContent=t.contact;contact.title=t.draft;
    topics.replaceChildren();for(const e of knowledge?.entries??[]) {const b=document.createElement('button');b.type='button';b.textContent=e.title;b.onclick=()=>{message(e[lang]);const a=document.createElement('a');a.textContent=t.source;a.href=knowledge.source;a.target='_blank';a.rel='noopener noreferrer';log.append(a);sourceButtons([e.id]);};topics.append(b);}
  }
  launch.setAttribute('aria-expanded','false');panel.id='astreb-guide-panel';launch.setAttribute('aria-controls',panel.id);
  launch.onclick=()=>{panel.hidden=!panel.hidden;launch.setAttribute('aria-expanded',String(!panel.hidden));if(!panel.hidden)(mode==='ai'?input:language).focus();};
  close.onclick=()=>{panel.hidden=true;launch.setAttribute('aria-expanded','false');launch.focus();};
  panel.addEventListener('keydown',e=>{if(e.key==='Escape')close.click();});
  function reset() {controller?.abort();controller=null;pending=false;history=[];log.replaceChildren();message(i18n[lang].intro);render();}
  language.onchange=()=>{lang=language.value;reset();};clear.onclick=reset;
  contact.onclick=()=>{contact.href='mailto:info@astreb.nl?subject='+encodeURIComponent('ASTREB enquiry')+'&body='+encodeURIComponent(input.value || history.filter(x=>x.role==='user').map(x=>x.content).join('\n\n'));};
  form.onsubmit=async event=>{
    event.preventDefault();const q=input.value.trim();if(!q||pending||mode!=='ai')return;
    message(q,'user');input.value='';pending=true;render();
    const waiting=message(i18n[lang].busy);const requestController=new AbortController();controller=requestController;
    const timer=setTimeout(()=>requestController.abort(),30000);
    try {
      const r=await fetch(new URL('chat',endpoint),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:q,lang,history:history.slice(-6)}),signal:requestController.signal});
      if(!r.ok)throw new Error();const reply=await r.json();if(typeof reply.answer!=='string')throw new Error();
      waiting.remove();message(reply.answer);sourceButtons(Array.isArray(reply.source_ids)?reply.source_ids:[]);
      history.push({role:'user',content:q},{role:'assistant',content:reply.answer});history=history.slice(-6);
      if(allowed.includes(reply.navigate_to))navigate(reply.navigate_to);
    } catch {if(controller===requestController){waiting.remove();message(i18n[lang].error);}}
    finally {clearTimeout(timer);if(controller===requestController){pending=false;controller=null;render();}}
  };
  reset();
  fetch(new URL('status',endpoint)).then(r=>{if(!r.ok)throw new Error();return r.json();}).then(data=>{mode=data.mode==='ai'?'ai':'offline';knowledge=data.knowledge;render();}).catch(()=>{status.textContent=i18n[lang].error;});
})();
