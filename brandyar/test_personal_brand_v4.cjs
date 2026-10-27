'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {execFileSync}=require('node:child_process');
const source=fs.readFileSync(`${__dirname}/personal-brand.js`,'utf8');
const fixture=JSON.parse(execFileSync('python3',['-c',`import sys,json;sys.path.insert(0,${JSON.stringify(__dirname)});import personal_brand_v4 as m;from test_personal_brand import responses_v4;a=responses_v4();r=m.score(a,m.template(),m.model());print(json.dumps({'template':m.template(),'report':r,'answers':a}))`],{encoding:'utf8'}));
function harness(stage=0,storage=new Map()){
  const nodes=new Map(),listeners={},requests=[];
  const node=id=>{if(!nodes.has(id))nodes.set(id,{innerHTML:'',textContent:'',disabled:false,dataset:{},addEventListener(){},querySelectorAll(){return [];},insertAdjacentHTML(_,text){this.innerHTML+=text;},focus(){}});return nodes.get(id);};
  const state={stage,revision:stage,answers:{},completed:false};
  const context={Intl,Date,URLSearchParams,AbortController,setTimeout,clearTimeout,Blob,URL,console,
    location:{pathname:'/personal-brand',search:''},
    localStorage:{getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)},
    FormData:class{constructor(form){if(form.inputs)return form.inputs.filter(x=>!x.disabled&&(x.type!=='checkbox'||x.checked)).map(x=>[x.name,x.value]);return Object.entries(form.values||{}).flatMap(([key,value])=>Array.isArray(value)?value.map(x=>[key,x]):[[key,value]]);}},
    document:{documentElement:{dataset:{}},getElementById:node,querySelectorAll(){return [];},addEventListener:(name,fn)=>listeners[name]=fn},
    fetch:async(url,options)=>{
      const body=options.body?JSON.parse(options.body):null;requests.push({url,body});let data;
      if(url.includes('bootstrap'))data={csrf:'test',assessments:[],instagram_available:true,connection:{status:'connected',username:'existing'}};
      else if(url.includes('?id='))data={assessment:{id:'test',state:state.completed?'completed':'draft',stage:state.stage,revision:state.revision},template:fixture.template,order:fixture.template.behavior.map(q=>q.id),answers:state.answers,reports:state.completed?[{body:fixture.report}]:[],report_unlocked:state.completed};
      else if(body.action==='start')data={id:'test'};
      else if(body.action==='save'){state.answers[body.step]=body.answers;state.stage=Math.max(state.stage,body.step);data={revision:++state.revision};}
      else if(body.action==='draft'){state.answers[body.step]=body.answers;data={ok:true};}
      else if(body.action==='report'){state.completed=true;data={report:fixture.report};}
      else data={ok:true};
      return {ok:true,json:async()=>({ok:true,data})};
    }};
  vm.createContext(context);vm.runInContext(source,context);
  const click=action=>listeners.click({target:{closest:()=>({dataset:{action,id:'test'}})}});
  const form=values=>({id:'step-form',values,querySelectorAll(){return [];},closest(){return null;}});
  const submit=values=>listeners.submit({target:form(values),submitter:{name:''},preventDefault(){}});
  return {node,state,listeners,requests,click,submit,storage};
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
  console.log('PASS: v4 exact bank/scale, optional other inputs, exclusive proof, no automatic advance, autosave/back/resume, complete result without phone/Instagram, escaping (Node VM; no browser)');
})().catch(error=>{console.error(error);process.exitCode=1;});
