'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {execFileSync}=require('node:child_process');
const source=fs.readFileSync(`${__dirname}/personal-brand.js`,'utf8'),html=fs.readFileSync(`${__dirname}/personal-brand.html`,'utf8'),css=fs.readFileSync(`${__dirname}/personal-brand.css`,'utf8');
const fixture=JSON.parse(execFileSync('python3',['-c',`import sys,json;sys.path.insert(0,${JSON.stringify(__dirname)});import personal_brand_model as m;from test_personal_brand import responses_v3;r=m.score(responses_v3(),m.template_v3(),m.model_v3());r.update(version=1,created_at=1);print(json.dumps({'template':m.template_v3(),'report':r,'answers':responses_v3()}))`],{encoding:'utf8'}));
function harness({failed=false,admin=false,stage=0,existing=false,theme='dark',storage=new Map()}={}){
  const nodes=new Map(),requests=[],listeners={},documentElement={dataset:{}};
  const node=id=>{if(!nodes.has(id))nodes.set(id,{innerHTML:'',textContent:'',disabled:false,checked:false,returnValue:'yes',dataset:{},listeners:{},addEventListener(name,fn){this.listeners[name]=fn;},insertAdjacentHTML(where,value){this.innerHTML+=value;},replaceWith(){this.replaced=true;},showModal(){this.open=true;},querySelectorAll(){return [];},focus(){}});return nodes.get(id);};
  for(const match of html.matchAll(/id="([^"]+)"/g))node(match[1]);
  const state={completed:false,unlocked:false,stage,revision:stage,answers:{},existing};
  const adminData={csrf:'test',permissions:{private:false,manage:false,export:false},total:0,offset:0,assessments:[],templates:[{id:'v3',version:3,status:'published',body:fixture.template}],models:[],connections:[],sync_jobs:[],retention_days:30,metrics:[],validation:[],question_metrics:[]};
  storage.set('brandyar-theme',theme);
  const context={Intl,Date,URLSearchParams,AbortController,setTimeout,clearTimeout,Blob,URL,console,
    location:{pathname:admin?'/admin/personal-brand':'/personal-brand',search:'',assign(){throw Error('Unexpected navigation');}},
    localStorage:{getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)},
    FormData:class{constructor(form){return Object.entries(form.values||{}).flatMap(([k,v])=>Array.isArray(v)?v.map(x=>[k,x]):[[k,v]]);}},
    document:{documentElement,hidden:false,getElementById:node,addEventListener(name,fn){listeners[name]=fn;},querySelectorAll(){return [];},createElement(){return {};}},
    fetch:async(url,options)=>{
      const body=options.body?JSON.parse(options.body):null;requests.push({url,body});
      if(failed)return {ok:false,json:async()=>({error:'ارتباط برقرار نشد'})};
      let data;
      if(admin)data=adminData;
      else if(url.includes('bootstrap'))data={csrf:'test',instagram_available:false,connection:null,assessments:state.existing?[{id:'test',state:state.completed?'completed':'draft'}]:[]};
      else if(url.includes('?id='))data={assessment:{id:'test',state:state.completed?'completed':'draft',stage:state.stage,revision:state.revision},template:fixture.template,order:fixture.template.behavior.map(q=>q.id),answers:state.answers,reports:state.completed?[{body:fixture.report}]:[],report_unlocked:state.unlocked};
      else if(body.action==='start'){state.existing=true;data={id:'test'};}
      else if(body.action==='save'){state.answers[String(body.step)]=body.answers;state.stage=Math.max(state.stage,body.step);data={revision:++state.revision};}
      else if(body.action==='draft'){state.answers[String(body.step)]=body.answers;data={ok:true};}
      else if(body.action==='report'){state.completed=true;data={report:fixture.report};}
      else if(body.action==='unlock_report'){state.unlocked=true;data={ok:true};}
      else data={ok:true};
      return {ok:true,json:async()=>({ok:true,data})};
    }};
  vm.createContext(context);vm.runInContext(source,context);
  const click=action=>listeners.click({target:{closest(){return {dataset:{action,id:'test'},disabled:false};}}});
  const form=values=>({id:'step-form',values,closest(){return null;},querySelectorAll(){return [];}});
  const submit=(values,name='',id='step-form')=>listeners.submit({target:{...form(values),id},submitter:{name},preventDefault(){}});
  return {node,requests,listeners,click,submit,form,state,documentElement,storage};
}
(async()=>{
  assert(html.includes('lang="fa" dir="rtl"'));assert(html.includes('aria-live="polite"'));assert(html.includes('site-header'));assert(html.includes('site-footer'));assert(!html.includes('/admin'));
  assert(css.includes(':focus-visible'));assert(css.includes('@media(max-width:680px)'));
  assert.equal(fixture.template.behavior.length,15);assert.equal(fixture.template.sections.length,5);
  const h=harness();await new Promise(setImmediate);assert(h.node('app').innerHTML.includes('شروع ارزیابی'));
  assert.equal(h.documentElement.dataset.theme,'dark');h.node('theme-toggle').listeners.click();assert.equal(h.documentElement.dataset.theme,'light');assert.equal(h.storage.get('brandyar-theme'),'light');
  await h.click('start');assert(h.node('app').innerHTML.includes('خودت و مسیر فعلی‌ات'));assert(h.node('app').innerHTML.includes('name="audience"'));
  const form=h.form({field:'آموزش و تدریس',audience:[]});h.listeners.input({target:{name:'field',closest(){return form;}}});await h.click('home');
  await h.click('start');await h.submit(fixture.answers['1']);assert(h.node('app').innerHTML.includes('تصویری که می‌خواهی از خودت بسازی'));
  await h.click('previous');assert(h.node('app').innerHTML.includes('checked'));await h.submit(fixture.answers['1']);
  await h.submit(fixture.answers['2']);for(const q of fixture.template.behavior)assert(h.node('app').innerHTML.includes(q.title));assert.equal((h.node('app').innerHTML.match(/type="radio"/g)||[]).length,75);
  await h.submit(fixture.answers['3']);assert(h.node('app').innerHTML.includes('شواهد و تجربه'));
  await h.submit(fixture.answers['4']);assert(h.node('app').innerHTML.includes('حضور آنلاین'));assert(!h.node('app').innerHTML.includes('نیازمند تکمیل تنظیمات'));assert(h.node('app').innerHTML.includes('ادامه بدون اتصال'));
  await h.submit(fixture.answers['5']);assert(h.node('app').innerHTML.includes('نتیجهٔ اولیهٔ ارزیابی'));assert(h.node('app').innerHTML.includes('گزارش کاملت آماده است'));assert(!h.node('app').innerHTML.includes('چرا این نتیجه را گرفتی'));
  await h.submit({phone:'09121234567',consent:'on'},'','lead-form');assert(h.node('app').innerHTML.includes('الان کجای مسیر هستی؟'));assert(h.node('app').innerHTML.includes('مهم‌ترین نقطهٔ قوت'));assert(h.node('app').innerHTML.includes('چرا این نتیجه را گرفتی'));
  for(const forbidden of ['محدودیت تحلیل','بازخوانی اطلاعات','همگام‌سازی','وضعیت سرور','/admin'])assert(!h.node('app').innerHTML.includes(forbidden));
  const saved=harness({existing:true,stage:2});await new Promise(setImmediate);assert(saved.node('app').innerHTML.includes('ادامهٔ ارزیابی'));assert(!saved.node('app').innerHTML.includes('شروع ارزیابی'));
  const xss=harness({stage:3,storage:new Map([['pb-draft-test-4',JSON.stringify({experience:'<img src=x onerror=alert(1)>'})]])});await new Promise(setImmediate);await xss.click('start');assert(xss.node('app').innerHTML.includes('&lt;img'));assert(!xss.node('app').innerHTML.includes('<img src=x'));
  const broken=harness({failed:true});await new Promise(setImmediate);assert(broken.node('feedback').textContent.includes('ارتباط'));
  const analyst=harness({admin:true});await new Promise(setImmediate);assert(!analyst.node('app').innerHTML.includes('data-action="template_edit"'));assert(analyst.node('privacy-form').replaced);
  await new Promise(resolve=>setTimeout(resolve,650));
  assert(h.requests.some(r=>r.body?.action==='draft'));
  console.log('PASS: v3 five sections, exact 15 texts/75 choices, draft autosave, back/resume, lead gate, full report, themes, XSS and admin controls (Node VM; no browser)');
})().catch(error=>{console.error(error);process.exitCode=1;});
