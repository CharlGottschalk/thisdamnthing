'use strict';
// Credentials never enter the custom iframe or the URL sent to the server.
const token = location.hash.slice(1) || sessionStorage.getItem('tdt-token');
if (token) sessionStorage.setItem('tdt-token', token);
history.replaceState(null, '', '/');
const $ = id => document.getElementById(id);
let round = null, page = null, answers = Object.create(null), step = 0, currentStatus = '', busy = false, frame = null, bridgeKey = null, pending = null, pageKey = null;
const el = (tag, text, attrs={}) => { const e=document.createElement(tag); if(text!==null)e.textContent=text; for(const [k,v] of Object.entries(attrs)) e.setAttribute(k,v); return e; };
// A deliberately small text format: fenced blocks and inline code, never HTML.
function renderText(target,text){
  target.replaceChildren();
  const lines=String(text).replace(/\r\n?/g,'\n').split('\n');
  let prose=[],code=null,language='';
  function flush(){
    if(!prose.length)return;
    const p=el('p',null);
    const parts=prose.join('\n').split(/(`[^`\n]+`)/g);
    for(const part of parts){
      if(/^`[^`\n]+`$/.test(part))p.append(el('code',part.slice(1,-1)));
      else p.append(document.createTextNode(part));
    }
    target.append(p);prose=[];
  }
  function block(){
    const pre=el('pre',null,{class:'tdt-code',tabindex:'0','aria-label':language?language+' code':'Code block'});
    if(language)pre.append(el('span',language,{class:'code-language'}));
    pre.append(el('code',code.join('\n')));target.append(pre);code=null;
  }
  for(const line of lines){
    const fence=line.match(/^\s*```([a-zA-Z0-9_+.-]*)\s*$/);
    if(code!==null){if(fence&&!fence[1])block();else code.push(line);}
    else if(fence){flush();code=[];language=fence[1];}
    else if(!line.trim())flush();
    else prose.push(line);
  }
  if(code!==null)block();flush();
}
function message(text, waitingForAgent=false){
  const status=$('status');
  if(status.dataset.message===text&&status.classList.contains('agent-waiting')===waitingForAgent)return;
  status.dataset.message=text;
  status.classList.toggle('agent-waiting',waitingForAgent);
  if(!waitingForAgent){status.textContent=text;return;}
  const indicator=el('span',null,{class:'agent-activity','aria-hidden':'true'});
  for(let i=0;i<3;i++)indicator.append(el('span',null));
  const copy=el('div',null);
  copy.append(el('strong',text),el('p','Keep this tab open. The next question or completion message will appear here.',{class:'agent-waiting-hint'}));
  status.replaceChildren(indicator,copy);
}
let statusVisible=true;
function syncActivity(){ $('status').classList.toggle('activity-paused',document.hidden||!statusVisible); }
document.addEventListener('visibilitychange',syncActivity);
new IntersectionObserver(([entry])=>{statusVisible=entry.isIntersecting;syncActivity();}).observe($('status'));
syncActivity();
async function api(route, payload) {
  const response=await fetch('/api/'+route,{method:payload===undefined?'GET':'POST',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:payload===undefined?undefined:JSON.stringify(payload)});
  const data=await response.json(); if(!response.ok){const err=new Error(data.error);err.fields=data.fields;throw err;} return data;
}
function retain(){sessionStorage.setItem('tdt-draft',JSON.stringify({round,answers,step}));}
function button(text, fn, primary=false){const b=el('button',text,{type:'button'});if(primary)b.className='primary';b.onclick=fn;$('actions').append(b);return b;}
function showErrors(errors){for(const old of document.querySelectorAll('.error'))old.remove();for(const [id,text] of Object.entries(errors||{})){const f=document.getElementById('field-'+id);if(f){const p=el('p',text,{id:'error-'+id,class:'error'});f.append(p);f.querySelectorAll('input,textarea,select').forEach(e=>{e.setAttribute('aria-invalid','true');e.setAttribute('aria-describedby','help-'+id+' error-'+id);});}}const first=document.querySelector('[aria-invalid=true]');if(first)first.focus();}
function draw(){
  $('content').replaceChildren();$('actions').replaceChildren();frame=null;bridgeKey=null;
  if(currentStatus!=='waiting'){message(currentStatus==='received'?'Received — waiting for your agent.':currentStatus==='finished'?'Finished. You can close this page.':'Cancelled. No further answer is expected.',currentStatus==='received');return;}
  message('Waiting for your answer');
  const steps=page.steps||[];
  if(page.custom_html!==undefined){
    frame=el('iframe',null,{sandbox:'allow-scripts',title:page.title+' — custom interaction',referrerpolicy:'no-referrer'});
    bridgeKey=pageKey;
    frame.src='/custom/'+pageKey;
    $('content').append(frame);
    button('Cancel',()=>send('cancel'));
    return;
  }
  const panel=el('section',null);$('content').append(panel);
  if(step<steps.length){
    panel.append(el('p',`Step ${step+1} of ${steps.length}`,{class:'progress'}),el('h2',steps[step].title,{tabindex:'-1'}));
    for(const f of steps[step].fields){
      const group=el('fieldset',null,{class:'field',id:'field-'+f.id});panel.append(group);
      group.append(el('legend',f.label+(f.required?' *':'')));
      const help=el('div',null,{class:'help',id:'help-'+f.id});
      renderText(help,f.help|| (f.required?'Required':'Optional'));group.append(help);
      const attrs={id:'input-'+f.id,'aria-label':f.label,'aria-describedby':'help-'+f.id};
      function change(v){answers[f.id]=v;pending=null;sessionStorage.removeItem('tdt-pending');retain();}
      if(['single','multiple','boolean'].includes(f.type)){
        const options=f.type==='boolean'?[true,false]:f.options;
        for(const [i,opt] of options.entries()){
          const label=el('label',null,{class:'choice'});const input=el('input',null,{type:f.type==='multiple'?'checkbox':'radio',name:f.id,value:String(opt),'aria-describedby':'help-'+f.id});
          input.checked=f.type==='multiple'?(answers[f.id]||[]).includes(opt):answers[f.id]===opt;
          input.onchange=()=>{change(f.type==='multiple'?(input.checked?[...(answers[f.id]||[]),opt]:(answers[f.id]||[]).filter(x=>x!==opt)):opt);if(f.type==='single'){const other=group.querySelector('input[type=text]');if(other)other.value='';}};
          label.append(input,document.createTextNode(f.type==='boolean'?(opt?'Yes':'No'):opt));group.append(label);
        }
        if(f.alternative&&f.type!=='boolean'){
          const input=el('input',null,{...attrs,placeholder:'Another answer',type:'text',maxlength:200});
          input.value=f.type==='multiple'?(answers[f.id]||[]).find(x=>!f.options.includes(x))||'':(!f.options.includes(answers[f.id])?answers[f.id]||'':'');
          input.oninput=()=>{const v=input.value;change(f.type==='multiple'?[...(answers[f.id]||[]).filter(x=>f.options.includes(x)),...(v?[v]:[])]:v);if(f.type==='single')group.querySelectorAll('[type=radio]').forEach(e=>e.checked=false);};
          group.append(el('label','Another answer',{for:attrs.id}),input);
        }
      }else{
        const input=el(f.type==='multiline'?'textarea':'input',null,attrs);
        if(f.type!=='multiline')input.type=f.type==='scale'?'range':f.type==='number'?'number':'text';
        if(['text','multiline'].includes(f.type))input.maxLength=4000;
        for(const k of ['min','max','step'])if(f[k]!==undefined)input[k]=f[k];
        input.value=answers[f.id]??'';
        const output=el('output',f.type==='scale'?(answers[f.id]===undefined?'No value selected':String(answers[f.id])):'');
        input.oninput=()=>{change(['number','scale'].includes(f.type)?(input.value===''?null:Number(input.value)):input.value);output.textContent=f.type==='scale'?String(answers[f.id]):'';};
        if(f.type==='scale'){input.onpointerup=()=>input.oninput();input.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();input.oninput();}};}
        group.append(input,output);
      }
    }
    if(step>0)button('Back',()=>{step--;retain();draw();focusHeading();});
    button('Cancel',()=>send('cancel'));
    button(step===steps.length-1?'Review answers':'Next',()=>{step++;retain();draw();focusHeading();},true);
  }else{
    panel.append(el('h2','Review your answers',{tabindex:'-1'}));const dl=el('dl',null);panel.append(dl);
    for(const s of steps)for(const f of s.fields){
      const dd=el('dd',null);
      renderText(dd,answers[f.id]===undefined||answers[f.id]===null?'Not answered':Array.isArray(answers[f.id])?answers[f.id].join(', '):String(answers[f.id]));
      dl.append(el('dt',f.label),dd);
    }
    button('Back',()=>{step=Math.max(0,steps.length-1);retain();draw();focusHeading();});button('Cancel',()=>send('cancel'));button('Submit answers',()=>send('submit'),true);
  }
  for(const action of page.actions||[])button(action,()=>send(action));
}
function focusHeading(){document.querySelector('h2')?.focus();}
async function send(action,data,customAnswers){
  if(busy||currentStatus!=='waiting')return;busy=true;
  const body={round_id:round,submission_id:crypto.randomUUID(),action,answers:action==='cancel'?{}:(customAnswers||answers)};if(data!==undefined&&action!=='cancel')body.data=data;
  // Retain the precise request after a network error, so retry is idempotent.
  if(!pending||pending.round_id!==body.round_id||pending.action!==body.action||JSON.stringify(pending.answers)!==JSON.stringify(body.answers)||JSON.stringify(pending.data)!==JSON.stringify(body.data))pending=body;
  sessionStorage.setItem('tdt-pending',JSON.stringify(pending));
  try{await api('submit',pending);pending=null;sessionStorage.removeItem('tdt-pending');currentStatus=action==='cancel'?'cancelled':'received';draw();}
  catch(e){message(e.message);if(e.fields){pending=null;sessionStorage.removeItem('tdt-pending');const ids=Object.keys(e.fields);step=(page.steps||[]).findIndex(s=>s.fields.some(f=>ids.includes(f.id)));step=Math.max(0,step);draw();message(e.message);showErrors(e.fields);}else{button('Retry submission',()=>send(action,data,customAnswers));}}
  finally{busy=false;}
}
window.addEventListener('message',event=>{
  const d=event.data;
  if(!frame||event.source!==frame.contentWindow||event.origin!=='null'||!d||d.tdt!==1||d.key!==bridgeKey||d.round!==round)return;
  if(!['submit','cancel',...(page.actions||[])].includes(d.action))return;
  if(JSON.stringify(d).length>200000){message('Custom response is too large');return;}
  send(d.action,d.data,d.answers);
});
async function poll(){
  try{
    const result=await api('page');
    if(result.page&&(result.round_id!==round||result.status!==currentStatus)){
      const changed=result.round_id!==round;round=result.round_id;page=result.page;pageKey=result.custom_key;currentStatus=result.status;
      $('title').textContent=page.title;renderText($('description'),page.description||'');
      if(changed){answers=Object.create(null);step=0;pending=null;for(const s of page.steps||[])for(const f of s.fields)if(f.default!==undefined)answers[f.id]=f.default;
        try{const saved=JSON.parse(sessionStorage.getItem('tdt-draft'));if(saved?.round===round){answers=saved.answers;step=saved.step;}const req=JSON.parse(sessionStorage.getItem('tdt-pending'));if(req?.round_id===round)pending=req;}catch{}
      }
      draw();
    }else if(!result.page)message('Waiting for your agent to present a question',true);
    else if($('status').textContent.startsWith('Disconnected')){
      if(currentStatus==='waiting')message('Reconnected — your edits are preserved');
      else draw();
    }
  }catch{message(['finished','cancelled'].includes(currentStatus)?(currentStatus==='finished'?'Finished.':'Cancelled.')+' You can close this page.':'Disconnected — answers and drafts are retained. Ask your agent to resume this session.');}
  setTimeout(poll,1500);
}
poll();
