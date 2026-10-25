const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(`${__dirname}/admin-workspace.js`, 'utf8');
const html = fs.readFileSync(`${__dirname}/admin-workspace.html`, 'utf8');
const css = fs.readFileSync(`${__dirname}/admin-workspace.css`, 'utf8');
const modules = {overview:'نمای کلی',customers:'مشتری‌ها',crm:'CRM',assessments:'ارزیابی‌ها',tests:'تست‌ها',prompts:'پرامپت‌ها',plans:'پلن‌ها',content:'محتوا',team:'تیم',reports:'گزارش‌ها',audit:'حسابرسی',settings:'تنظیمات'};
function harness(fail = false) {
  const nodes = new Map();
  for (const match of html.matchAll(/id="([^"]+)"/g)) nodes.set(match[1], {innerHTML:'',textContent:'',value:'',disabled:false,hidden:false,dataset:{},listeners:{},setAttribute(){},addEventListener(name,fn){this.listeners[name]=fn;},querySelector(){return null;}});
  nodes.get('period').value = '30';
  const requests = [], docEvents = {};
  const context = {
    console,URLSearchParams,AbortController,setTimeout,clearTimeout,Intl,Date,Blob,URL,
    location:{pathname:'/admin',assign(){}},history:{replaceState(){}},
    document:{getElementById:id=>nodes.get(id)||null,querySelectorAll:()=>[],body:{classList:{remove(){},toggle(){return false;}}},addEventListener(name,fn){docEvents[name]=fn;}},
    fetch:async url=>{
      requests.push(url);
      if(url.includes('bootstrap'))return {ok:true,status:200,json:async()=>({principal:{name:'تیم آزمایش',role:'owner'},csrf:'test-csrf',modules,permissions:['write','publish','archive'],stages:[],assignees:[]})};
      if(fail) return {ok:false,status:503,json:async()=>({error:'اتصال برقرار نیست'})};
      return {ok:true,status:200,json:async()=>({counts:{leads:0,assessments:0,completed:0,overdue:0},events:{},tasks:[],notice:'رویداد گذشته موجود نیست'})};
    }
  };
  vm.createContext(context);vm.runInContext(source,context);
  return {nodes,requests,context,docEvents};
}
(async()=>{
  assert(html.includes('lang="fa" dir="rtl"'));
  assert(html.includes('aria-live="polite"'));
  assert(html.includes('<dialog'));
  assert(css.includes('@media(max-width:760px)'));
  assert(css.includes(':focus-visible'));
  const h=harness();
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(h.requests.length,2);
  assert.equal((h.nodes.get('navigation').innerHTML.match(/data-section=/g)||[]).length,12);
  assert(h.nodes.get('content').innerHTML.includes('۰'));
  assert(h.nodes.get('content').innerHTML.includes('هنوز رویدادی'));
  assert(!h.nodes.get('content').innerHTML.includes('۱۲۳۴'));
  const broken=harness(true);
  await new Promise(resolve=>setImmediate(resolve));
  assert(broken.nodes.get('content').innerHTML.includes('دریافت اطلاعات انجام نشد'));
  assert(broken.nodes.get('feedback').textContent.includes('اتصال برقرار نیست'));
  console.log('PASS: admin navigation, actual empty metrics, API failure, RTL, accessibility and responsive layout contracts');
})().catch(error=>{console.error(error);process.exitCode=1;});
