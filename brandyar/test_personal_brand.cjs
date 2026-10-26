'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {execFileSync} = require('node:child_process');
const source = fs.readFileSync(`${__dirname}/personal-brand.js`, 'utf8');
const html = fs.readFileSync(`${__dirname}/personal-brand.html`, 'utf8');
const css = fs.readFileSync(`${__dirname}/personal-brand.css`, 'utf8');
const fixture = JSON.parse(execFileSync('python3', ['-c', `import sys,json;sys.path.insert(0,${JSON.stringify(__dirname)});import personal_brand_model as m;from test_personal_brand import responses;r=m.score(responses(),m.template(),m.model());r.update(version=1,created_at=1);print(json.dumps({'template':m.template(),'report':r}))`], {encoding:'utf8'}));
function harness({failed=false, admin=false}={}) {
  const nodes = new Map(), requests = [], listeners = {};
  const node = id => {
    if(!nodes.has(id))nodes.set(id,{innerHTML:'',textContent:'',disabled:false,checked:false,returnValue:'yes',dataset:{},listeners:{},addEventListener(name,fn){this.listeners[name]=fn;},insertAdjacentHTML(where,value){this.innerHTML+=value;},replaceWith(){this.replaced=true;},showModal(){this.open=true;},querySelectorAll(){return [];}});
    return nodes.get(id);
  };
  for(const match of html.matchAll(/id="([^"]+)"/g))node(match[1]);
  const state={completed:false};
  const adminData={csrf:'test-csrf',permissions:{private:false,manage:false,export:false},total:0,offset:0,assessments:[],templates:[{id:'v1',version:1,status:'published',body:fixture.template}],models:[],connections:[],sync_jobs:[],retention_days:30,metrics:[],validation:[],question_metrics:[]};
  const context={
    Intl,Date,URLSearchParams,AbortController,setTimeout,clearTimeout,Blob,URL,console,
    location:{pathname:admin?'/admin/personal-brand':'/personal-brand',search:'',assign(){throw new Error('Unexpected navigation');}},
    sessionStorage:{getItem(){return null;},setItem(){},removeItem(){}},
    FormData:class {constructor(form){return Object.entries(form.values||{});}},
    document:{hidden:false,getElementById:node,addEventListener(name,fn){listeners[name]=fn;},querySelectorAll(){return [];},createElement(){return {}; }},
    fetch:async(url,options)=>{
      const body=options.body?JSON.parse(options.body):null;requests.push({url,body});
      if(failed)return {ok:false,json:async()=>({error:'دریافت داده ناموفق بود'})};
      let data;
      if(admin)data=adminData;
      else if(url.includes('bootstrap'))data={csrf:'test-csrf',instagram_available:false,connection:null,assessments:[]};
      else if(url.includes('?id='))data={assessment:{id:'test',state:state.completed?'completed':'draft',stage:4,revision:0},template:fixture.template,order:fixture.template.items.map(q=>q.id),answers:{5:{introduction:'<img src=x onerror=alert(1)>'}},reports:state.completed?[{body:fixture.report}]:[]};
      else if(body.action==='start')data={id:'test'};
      else if(body.action==='save')data={revision:1};
      else if(body.action==='report'){state.completed=true;data={report:fixture.report};}
      else data={ok:true};
      return {ok:true,json:async()=>({ok:true,data})};
    }
  };
  vm.createContext(context);vm.runInContext(source,context);
  const click=action=>listeners.click({target:{closest(){return {dataset:{action,id:'test'},disabled:false};}}});
  return {nodes,requests,listeners,click,node};
}
(async()=>{
  assert(html.includes('lang="fa" dir="rtl"'));
  assert(html.includes('aria-live="polite"'));
  assert(css.includes(':focus-visible'));
  assert(css.includes('@media(max-width:680px)'));
  const h=harness();await new Promise(resolve=>setImmediate(resolve));
  assert(h.node('app').innerHTML.includes('هنوز ارزیابی ثبت نکرده‌اید'));
  await h.click('start');
  assert(!h.node('app').innerHTML.includes('name="introduction"'));
  assert(h.node('app').innerHTML.includes('data-action="oauth" disabled'));
  await h.click('skip');
  assert(h.node('app').innerHTML.includes('name="introduction"'));
  assert(h.node('app').innerHTML.includes('&lt;img'));
  assert(!h.node('app').innerHTML.includes('<img src=x'));
  const form={id:'step-form',values:{introduction:'معرفی تست'},closest(){return null;},querySelectorAll(){return [];}};
  await h.listeners.submit({target:form,submitter:{name:'skip'},preventDefault(){}});
  assert(h.requests.some(r=>r.body?.action==='save'&&r.body.answers.choice==='skip'));
  assert(h.node('app').innerHTML.includes('مرحلهٔ احتمالی'));
  assert(h.node('app').innerHTML.includes('دریافت گزارش برای اشتراک‌گذاری'));
  const cancellation=h.click('delete_assessment');
  assert.equal(h.node('confirm').returnValue,'cancel');
  h.node('confirm').listeners.close();await cancellation;
  assert(!h.requests.some(r=>r.body?.action==='delete_assessment'));
  const broken=harness({failed:true});await new Promise(resolve=>setImmediate(resolve));
  assert(broken.node('feedback').textContent.includes('ناموفق'));
  const analyst=harness({admin:true});await new Promise(resolve=>setImmediate(resolve));
  assert(!analyst.node('app').innerHTML.includes('data-action="template_edit"'));
  assert(!analyst.node('app').innerHTML.includes('data-action="template_publish"'));
  assert(analyst.node('privacy-form').replaced);
  console.log('PASS: personal-brand empty/error states, optional introduction, skip-to-report flow, escaping, cancellation and role-gated controls (Node VM; no browser)');
})().catch(error=>{console.error(error);process.exitCode=1;});
