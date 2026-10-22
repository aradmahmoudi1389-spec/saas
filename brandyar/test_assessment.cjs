const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(`${__dirname}/app.js`, 'utf8');
const schema = JSON.parse(fs.readFileSync(`${__dirname}/assessment_questions.json`, 'utf8'));
const start = source.indexOf('const assessmentQuestions = [');
const end = source.indexOf('function closeSiteMenu(', start);
const block = source.slice(start, end);
const report = {
  summary: 'خلاصهٔ برند بر اساس پاسخ‌ها',
  positioning: {status:'نیازمند بررسی',insight:'تخصص دقیق مشخص نیست.'},
  content: {status:'نیازمند بررسی',insight:'کیفیت واقعی محتوا دیده نشده است.'},
  trust: {status:'نیازمند بررسی',insight:'اعتماد از روی پاسخ‌ها مرور می‌شود.'},
  strengths:['آمادگی برای مرور مسیر'],growth_opportunities:['روشن‌ترکردن معرفی'],
  priority_actions:Array.from({length:3},()=>({title:'یک قدم کوچک',description:'یک تجربه بنویس.',why_it_matters:'به وضوح کمک می‌کند.'})),
  this_week_action:{title:'تمرین هفته',description:'یک جمله بنویس.'},
  questions_to_refine:['تخصص دقیق شما چیست؟'],disclaimer:'این تحلیل فقط بر اساس پاسخ‌های شماست.'
};

function harness(saved=null) {
  const storage = new Map(saved ? [['brandyar-assessment-session-v1',JSON.stringify(saved)]] : []);
  const listeners = {};
  let requests = [];
  const context = {
    console,AbortController,setTimeout,clearTimeout,URL,Blob,
    location:{hash:'#/report',protocol:'https:'},
    sessionStorage:{getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)},
    pages:{},appPages:{},appTitle:()=>'',icon:()=>'<svg aria-hidden="true"></svg>',
    pageHero:(_,title,sub)=>`<h1>${title}</h1><p>${sub}</p>`,
    esc:value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),
    document:{addEventListener:(name,fn)=>(listeners[name]??=[]).push(fn),querySelector:()=>null,getElementById:()=>null},
    route:()=>{},
    fetch:async (url,options)=>{requests.push({url,options});return {ok:true,json:async()=>url.endsWith('/status')?{ready:true}:{report}};}
  };
  vm.createContext(context);vm.runInContext(block,context);
  return {context,storage,listeners,requests,run:code=>vm.runInContext(code,context)};
}

(async()=>{
  const h=harness();
  assert.deepEqual(JSON.parse(h.run('JSON.stringify(assessmentQuestions)')),schema);
  assert.equal(h.requests.length,0);
  h.run("assessmentAnswers={q1:'آموزش'}; assessmentStep=assessmentFlow().length-1");
  assert(h.run('assessmentStepMarkup()').includes('name="analysis-consent" required'));
  assert(h.run('assessmentStepMarkup()').includes('href="#/privacy"'));
  let release;
  h.context.fetch=async (url,options)=>{
    h.requests.push({url,options});
    if(url.endsWith('/status'))return {ok:true,json:async()=>({ready:true})};
    await new Promise(resolve=>release=resolve);
    return {ok:true,json:async()=>({report})};
  };
  const pending=h.run('submitBrandAnalysis()');
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(h.run('assessmentPending'),true);
  const loading=h.run('reportPage()');
  assert(loading.includes('aria-busy="true"'));assert(loading.includes('disabled'));
  await h.run('submitBrandAnalysis()');assert.equal(h.requests.length,2);
  release();await pending;
  assert.equal(h.run('assessmentPending'),false);
  const markup=h.run('reportPage()');
  assert.equal((markup.match(/<h1>/g)||[]).length,1);
  for(const heading of ['تصویر کلی','جایگاه تخصصی','کیفیت محتوا','اعتمادسازی','نقاط قوت','فرصت‌های رشد','سه اقدام اولویت‌دار','قدم این هفته','پرسش‌های تکمیلی'])assert(markup.includes(heading));
  assert.equal(JSON.parse(h.requests[1].options.body).consent,true);
  const saved=JSON.parse(h.storage.get('brandyar-assessment-session-v1'));
  const refreshed=harness(saved);
  assert(refreshed.run('assessmentResult!==null'));
  assert.equal(refreshed.requests.length,0);
  refreshed.run("assessmentResult.summary='<img src=x onerror=alert(1)>'");
  assert(!refreshed.run('reportPage()').includes('<img'));
  const failure=harness();
  failure.run("assessmentAnswers={q1:'آموزش'}");
  failure.context.fetch=async()=>{throw new TypeError('network detail')};
  await failure.run('submitBrandAnalysis()');
  assert(failure.run('reportPage()').includes('assessment-retry'));
  assert.equal(failure.run('assessmentAnswers.q1'),'آموزش');
  assert(!failure.run('reportPage()').includes('network detail'));
  failure.context.fetch=async url=>({ok:true,json:async()=>url.endsWith('/status')?{ready:true}:{report:{summary:'گزارش ناقص'}}});
  await failure.run('submitBrandAnalysis()');
  assert.equal(failure.run('assessmentResult'),null);
  assert(failure.run('assessmentError').includes('معتبر'));
  failure.context.fetch=async()=>({ok:true,json:async()=>({ready:false,error:'سرویس هنوز فعال نیست.'})});
  await failure.run('submitBrandAnalysis()');
  assert.equal(failure.run('assessmentError'),'سرویس هنوز فعال نیست.');
  const insecure=harness();
  insecure.context.location.protocol='http:';
  insecure.run("assessmentAnswers={q1:'آموزش'}");
  await insecure.run('submitBrandAnalysis()');
  assert.equal(insecure.requests.length,0);
  assert(insecure.run('assessmentError').includes('اتصال امن'));
  const clear=failure.listeners.click.find(fn=>fn.toString().includes('assessment-retry'));
  clear({target:{id:'assessment-clear'}});
  assert.equal(failure.storage.size,0);
  assert.equal(failure.run('Object.keys(assessmentAnswers).length'),0);
  console.log('PASS: schema parity, explicit consent, loading, duplicate-click guard, success sections, refresh without requests, escaping, network/invalid/config errors, retained answers, clear');
})().catch(error=>{console.error(error);process.exitCode=1;});
