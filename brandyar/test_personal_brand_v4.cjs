'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {execFileSync}=require('node:child_process');
const source=fs.readFileSync(`${__dirname}/personal-brand.js`,'utf8');
const fixture=JSON.parse(execFileSync('python3',['-c',`import sys,json;sys.path.insert(0,${JSON.stringify(__dirname)});import personal_brand_v4 as m;import personal_brand_report as full;from test_personal_brand import responses_v4;a=responses_v4();r=m.score(a,m.template(),m.model());print(json.dumps({'template':m.template(),'report':r,'answers':a,'full':full.build(r,{'answers':{str(k):v for k,v in a.items()},'template':m.template()})}))`],{encoding:'utf8'}));
function harness(stage=0,storage=new Map(),options={}){
  const nodes=new Map(),listeners={},requests=[];
  const node=id=>{if(!nodes.has(id))nodes.set(id,{innerHTML:'',textContent:'',disabled:false,dataset:{},setAttribute(){},addEventListener(){},querySelectorAll(){return [];},insertAdjacentHTML(_,text){this.innerHTML+=text;},focus(){}});return nodes.get(id);};
  const state={stage,revision:stage,answers:{},completed:false,phoneRegistered:false,fullCalls:0,failPhone:false,failReport:false,hasAccess:false,savedPhoneMasked:null,...options};
  const context={Intl,Date,URLSearchParams,AbortController,setTimeout,clearTimeout,Blob,URL,console,
    location:{pathname:'/personal-brand',search:'',hash:options.hash||'',assign:href=>state.destination=href},
    history:{replaceState:(_,__,hash)=>{context.location.hash=hash;}},
    localStorage:{getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)},
    FormData:class{constructor(form){if(form.inputs)return form.inputs.filter(x=>!x.disabled&&(x.type!=='checkbox'||x.checked)).map(x=>[x.name,x.value]);return Object.entries(form.values||{}).flatMap(([key,value])=>Array.isArray(value)?value.map(x=>[key,x]):[[key,value]]);}},
    document:{documentElement:{dataset:{}},getElementById:node,querySelectorAll(){return [];},addEventListener:(name,fn)=>listeners[name]=fn},
    fetch:async(url,options)=>{
      const body=options.body?JSON.parse(options.body):null;requests.push({url,body});let data;
      if(url.includes('bootstrap'))data={csrf:'test',assessments:state.completed?[{id:'test',state:'completed'}]:[],instagram_available:true,connection:{status:'connected',username:'existing'}};
      else if(url.includes('?id='))data={assessment:{id:'test',state:state.completed?'completed':'draft',stage:state.stage,revision:state.revision},template:fixture.template,order:fixture.template.behavior.map(q=>q.id),answers:state.answers,reports:state.completed?[{body:fixture.report}]:[],report_unlocked:state.completed,report_flow:{phoneRegistered:state.phoneRegistered,savedPhoneMasked:state.savedPhoneMasked}};
      else if(body.action==='start')data={id:'test'};
      else if(body.action==='save'){state.answers[body.step]=body.answers;state.stage=Math.max(state.stage,body.step);data={revision:++state.revision};}
      else if(body.action==='draft'){state.answers[body.step]=body.answers;data={ok:true};}
      else if(body.action==='report'){state.completed=true;data={report:fixture.report};}
      else if(body.action==='unlock_report'){if(state.phoneWait)await state.phoneWait;if(state.failPhone||body.phone==='wrong')return {ok:false,json:async()=>({error:'شماره ثبت نشد'})};state.phoneRegistered=true;data={ok:true};}
      else if(body.action==='full_report'){state.fullCalls++;if(!state.phoneRegistered||state.failReport)return {ok:false,json:async()=>({error:'گزارش آماده نشد'})};data={report:fixture.full,offer:{hasAccess:state.hasAccess}};}
      else data={ok:true};
      return {ok:true,json:async()=>({ok:true,data})};
    }};
  vm.createContext(context);vm.runInContext(source,context);
  const click=action=>listeners.click({target:{closest:()=>({dataset:{action,id:'test'}})}});
  const form=values=>({id:'step-form',values,querySelectorAll(){return [];},closest(){return null;}});
  const submit=values=>listeners.submit({target:form(values),submitter:{name:''},preventDefault(){}});
  const phoneSubmit=values=>listeners.submit({target:{id:'full-phone-form',values,querySelectorAll:()=>[node('phone-submit')],querySelector:selector=>node(selector==='[type=submit]'?'phone-submit':'phone'),closest:()=>null},preventDefault(){}});
  return {node,state,listeners,requests,click,submit,storage,phoneSubmit};
}
(async()=>{
  const h=harness();await new Promise(setImmediate);await h.click('start');
  let html=h.node('app').innerHTML;
  assert(html.includes('مسیر فعلی تو'));assert(html.includes('data-action="home"'));assert(!/name="[^"]*_other"[^>]*required/.test(html));
  for(const key of ['field','primary_goal','audience','current_situation'])assert(html.includes(`name="${key}_other"`));
  const other={name:'field_other',value:'متن اختیاری',disabled:false};
  const radio={name:'field',value:'آموزش و تدریس',type:'radio'};
  const label={dataset:{otherFor:'field_other'},querySelector:()=>other};
  const otherForm={id:'step-form',inputs:[radio,other],querySelectorAll:selector=>selector==='[data-other-for]'?[label]:[]};
  const input=()=>h.listeners.input({target:{...radio,closest:()=>otherForm}});
  input();assert(label.hidden);assert(other.disabled);
  radio.value='موضوع دیگری دارم';input();assert(!label.hidden);assert(!other.disabled);
  assert(h.node('app').innerHTML===html,'input must not navigate');
  await h.click('home');await h.click('start');await h.submit(fixture.answers['1']);
  html=h.node('app').innerHTML;assert(html.includes('تصویری که دوست داری ساخته شود'));
  for(const key of ['desired_impression','help_area'])assert(html.includes(`name="${key}_other"`));
  await h.click('previous');assert(h.node('app').innerHTML.includes('checked'));await h.submit(fixture.answers['1']);await h.submit(fixture.answers['2']);
  html=h.node('app').innerHTML;assert.equal((html.match(/type="radio"/g)||[]).length,75);
  for(const question of fixture.template.behavior){assert(html.includes(question.title));assert(question.title.includes('در یک ماه اخیر'));}
  for(const text of fixture.template.likert)assert.equal(html.split(`<span>${text}</span>`).length-1,15);
  await h.submit(fixture.answers['3']);assert(h.node('app').innerHTML.includes('name="available_proof_other"'));
  const proofs=['نمونه‌کار','هنوز چیز مشخصی ندارم','تجربهٔ کاری'].map(value=>({name:'available_proof',type:'checkbox',value,checked:true}));
  const proofForm={id:'step-form',inputs:proofs,querySelectorAll:selector=>selector.includes('available_proof')?proofs:[]};
  function proofInput(index){h.listeners.input({target:Object.assign(proofs[index],{closest:()=>proofForm})});}
  proofInput(1);assert.deepEqual(proofs.map(x=>x.checked),[false,true,false]);
  proofs[2].checked=true;proofInput(2);assert.deepEqual(proofs.map(x=>x.checked),[false,false,true]);
  await h.submit(fixture.answers['4']);html=h.node('app').innerHTML;
  assert(html.includes('name="primary_channel_other"'));assert(!html.includes('اتصال اینستاگرام'));assert(!html.includes('name="phone"'));
  await h.submit(fixture.answers['5']);html=h.node('app').innerHTML;
  for(const text of ['امتیاز کلی','مرحلهٔ فعلی','نقطهٔ قوت','فرصت رشد','اقدام ابتدایی','سؤال برای ادامه',fixture.report.disclaimer])assert(html.includes(text));
  assert(!html.includes('lead-form'));assert(!html.includes('صفحهٔ اینستاگرام تو'));assert(html.indexOf(fixture.report.disclaimer)>html.indexOf('سؤال برای ادامه'));
  assert(!('choice' in h.requests.find(x=>x.body?.action==='save'&&x.body.step===5).body.answers));
  const saved=harness(3,new Map([['pb-draft-test-4',JSON.stringify({proud_work:'<img src=x onerror=alert(1)>'})]]));await new Promise(setImmediate);await saved.click('start');
  assert(saved.node('app').innerHTML.includes('&lt;img'));assert(!saved.node('app').innerHTML.includes('<img src=x'));
  assert(h.requests.some(x=>x.body?.action==='draft'));
  const flow=harness(5,new Map(),{completed:true});await new Promise(setImmediate);await flow.click('open');
  assert(flow.node('app').innerHTML.includes('تصویر کامل‌تری از برندت ببین'));
  assert(!flow.node('app').innerHTML.includes('/brandyar/plans'));
  await flow.click('open_full_report');assert(flow.node('app').innerHTML.includes('id="full-phone-form"'));assert.equal(flow.state.fullCalls,0);
  await flow.phoneSubmit({phone:'wrong',use_saved_phone:'no'});assert.equal(flow.state.fullCalls,0);assert(flow.node('full-phone-error').textContent.includes('شماره ثبت نشد'));
  flow.state.failReport=true;await flow.phoneSubmit({phone:'۰۹۱۲۱۲۳۴۵۶۷',use_saved_phone:'no'});assert.equal(flow.state.fullCalls,1);assert(flow.node('app').innerHTML.includes('تلاش دوباره'));assert(!flow.state.destination);
  flow.state.failReport=false;await flow.click('retry_full_report');
  let fullHTML=flow.node('app').innerHTML;assert(fullHTML.includes('گزارش کامل برند شخصی'));assert(fullHTML.includes('مشاهدهٔ پیشنهاد خرید'));
  assert(fullHTML.indexOf('حالا تحلیل را به اقدام تبدیل کن')>fullHTML.indexOf('محدودیت تحلیل'));
  await flow.click('initial_report');assert(flow.node('app').innerHTML.includes('امتیاز کلی'));
  await flow.click('open_full_report');await flow.click('report_purchase_offer');assert.equal(flow.state.destination,'/brandyar/plans');
  const savedPhone=harness(5,new Map(),{completed:true,savedPhoneMasked:'0912•••••67'});await new Promise(setImmediate);await savedPhone.click('open');await savedPhone.click('open_full_report');
  assert(savedPhone.node('app').innerHTML.includes('0912•••••67'));assert(!savedPhone.node('app').innerHTML.includes('name="phone"'));
  await savedPhone.click('edit_report_phone');assert(savedPhone.node('app').innerHTML.includes('name="phone"'));
  let releasePhone;const phoneWait=new Promise(resolve=>releasePhone=resolve);
  const duplicate=harness(5,new Map(),{completed:true,phoneWait});await new Promise(setImmediate);await duplicate.click('open');await duplicate.click('open_full_report');
  const pendingPhone=duplicate.phoneSubmit({phone:'09121234567',use_saved_phone:'no'});
  assert.equal(duplicate.node('phone-submit').disabled,true);
  await duplicate.phoneSubmit({phone:'09121234567',use_saved_phone:'no'});
  assert.equal(duplicate.requests.filter(item=>item.body?.action==='unlock_report').length,1);
  releasePhone();await pendingPhone;
  assert.equal(duplicate.node('phone-submit').disabled,false);
  const active=harness(5,new Map(),{completed:true,phoneRegistered:true,hasAccess:true,hash:'#assessment=test&view=full'});await new Promise(setImmediate);await new Promise(setImmediate);
  assert(active.node('app').innerHTML.includes('ورود به محصول'));assert(!active.node('app').innerHTML.includes('مشاهدهٔ پیشنهاد خرید'));
  assert.equal(active.state.fullCalls,1);
  console.log('PASS: v4 initial result, phone form, saved phone, retry, full report ordering, refresh, product access and assessment regressions (Node VM; no browser)');
})().catch(error=>{console.error(error);process.exitCode=1;});
