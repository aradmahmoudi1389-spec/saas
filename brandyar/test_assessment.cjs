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
    requestAnimationFrame:callback=>callback(),
    FormData:class {constructor(form){this.values=form.values}get(key){return this.values[key]??null}},
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
  h.run("reportLeadStatus='idle'");
  const markup=h.run('reportPage()');
  assert.equal((markup.match(/<h1>/g)||[]).length,1);
  assert(markup.includes(report.summary));
  assert(markup.includes(report.strengths[0]));
  assert(markup.indexOf('class="report-preview"') < markup.indexOf('<form id="report-lead-form"'));
  assert.equal((markup.match(/name="phone"/g)||[]).length,1);
  assert(!markup.includes('id="report-full"'));
  assert(!markup.includes(report.this_week_action.description));
  assert(!markup.includes('assessment-download'));
  assert(!markup.includes('consultation-phone'));
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
  const html = fs.readFileSync(`${__dirname}/index.html`, 'utf8');
  const inlineStart = html.indexOf('let assessmentResult = null;');
  assert.equal(html.slice(inlineStart, html.indexOf('function closeSiteMenu(', inlineStart)), source.slice(source.indexOf('let assessmentResult = null;'), end));
  const booking = harness();
  assert(!booking.run('reportPage()').includes('consultation-open'));
  booking.context.reportFixture = report;
  booking.run("assessmentResult = reportFixture; reportLeadStatus='idle'");
  assert(!booking.run('reportPage()').includes('id="report-consultation"'));
  assert(!booking.run('reportPage()').includes('id="consultation-phone"'));
  assert(booking.run('consultationMarkup()').includes('ثبت شماره برای هماهنگی مشاوره'));
  assert.equal(booking.requests.length,0);
  const host = {innerHTML:'',querySelector:()=>null};
  const feedback = {textContent:''};
  booking.context.document.getElementById = id => id === 'report-consultation' ? host : id === 'consultation-feedback' ? feedback : null;
  let releaseSlots;
  booking.context.fetch = async (url,options) => {
    booking.requests.push({url,options});
    await new Promise(resolve=>releaseSlots=resolve);
    return {ok:true,json:async()=>({slots:[],request:null,timeZoneLabel:'تهران'})};
  };
  const loadingSlots = booking.run('loadConsultation()');
  assert(host.innerHTML.includes('aria-busy="true"'));
  await booking.run('loadConsultation()');
  assert.equal(booking.requests.length,1);
  releaseSlots(); await loadingSlots;
  assert(host.innerHTML.includes('id="consultation-form"'));
  assert(!host.innerHTML.includes('name="slotId"'));
  assert(host.innerHTML.includes('href="#/privacy"'));
  assert(host.innerHTML.includes('زمان جلسه پس از تماس و هماهنگی مشخص می‌شود'));
  const slot = {id:1,startsAt:Math.floor(Date.now()/1000)+86400,durationMinutes:60,timeZone:'Asia/Tehran'};
  booking.context.slotFixture = slot;
  const formattedDate = booking.run('consultationDate(slotFixture)');
  assert(!formattedDate.includes(new Date(slot.startsAt*1000).toISOString().slice(0,10)));
  assert.equal(booking.run('consultationDate({startsAt:null})'),'زمان جلسه با تماس هماهنگ می‌شود');
  const submit = {disabled:false};
  const form = {values:{name:'',phone:'۰۹۱۲۱۲۳۴۵۶۷',notes:'موضوع شخصی'},attrs:{},querySelector:selector=>selector==='[type="submit"]'?submit:feedback,setAttribute(key,value){this.attrs[key]=value}};
  booking.context.formFixture = form;
  const storageBefore = JSON.stringify([...booking.storage]);
  let releaseBooking;
  booking.context.fetch = async (url,options) => {
    booking.requests.push({url,options});
    await new Promise(resolve=>releaseBooking=resolve);
    return {ok:false,json:async()=>({error:'این زمان دیگر در دسترس نیست.'})};
  };
  const failedBooking = booking.run('submitConsultation(formFixture)');
  assert.equal(submit.disabled,true);
  assert.equal(form.attrs['aria-busy'],'true');
  const count = booking.requests.length;
  await booking.run('submitConsultation(formFixture)');
  assert.equal(booking.requests.length,count);
  releaseBooking(); await failedBooking;
  assert.equal(submit.disabled,false);
  assert.equal(form.values.phone,'۰۹۱۲۱۲۳۴۵۶۷');
  assert.equal(form.values.notes,'موضوع شخصی');
  assert.equal(feedback.textContent,'این زمان دیگر در دسترس نیست.');
  assert.equal(JSON.stringify([...booking.storage]),storageBefore);
  booking.context.fetch = async ()=>{throw new TypeError('private network detail')};
  await booking.run('submitConsultation(formFixture)');
  assert(feedback.textContent.includes('پاسخ ثبت دریافت نشد'));
  assert.equal(form.values.phone,'۰۹۱۲۱۲۳۴۵۶۷');
  booking.context.fetch = async (url,options)=>{
    booking.requests.push({url,options});
    return {ok:true,json:async()=>({request:{startsAt:null,status:'در انتظار تماس برای هماهنگی زمان',state:'pending'}})};
  };
  await booking.run('submitConsultation(formFixture)');
  assert(host.innerHTML.includes('شماره‌ات ثبت شد'));
  assert(host.innerHTML.includes('برای هماهنگی زمان جلسهٔ مشاوره با تو تماس می‌گیریم'));
  assert(!host.innerHTML.includes('۱۹۷۰'));
  assert.equal(JSON.parse(booking.requests.at(-1).options.body).slotId,null);
  assert(!host.innerHTML.includes('id="consultation-form"'));
  assert(!host.innerHTML.includes(form.values.phone));
  assert.equal(JSON.stringify([...booking.storage]),storageBefore);
  booking.run("assessmentConsultation.request={...slotFixture,state:'confirmed',status:'زمان تأیید شد'};updateConsultation()");
  assert(host.innerHTML.includes('زمان تأیید شد'));
  assert(!host.innerHTML.includes('این زمان هنوز قطعی نیست'));
  for(const state of ['cancelled','completed']){
    booking.context.stateFixture=state;
    booking.run('assessmentConsultation.request.state=stateFixture;updateConsultation()');
    assert(host.innerHTML.includes('id="consultation-new"'));
  }
  assert(booking.requests.every(item=>item.url==='/api/assessment/consultation'));
  assert(booking.requests.every(item=>!item.url.includes(form.values.phone)));
  const lead = harness();
  lead.context.reportFixture=report;
  lead.run("assessmentResult=reportFixture; reportLeadStatus='idle'");
  const leadFeedback={textContent:''},leadButton={disabled:false,textContent:''};
  const leadInput={setAttribute(){},focus(){}};
  const leadForm={values:{phone:'۱۲۳'},setAttribute(){},querySelector:selector=>selector==='#report-lead-feedback'?leadFeedback:selector==='[name="phone"]'?leadInput:leadButton};
  lead.context.leadForm=leadForm;
  await lead.run('requestReportLead(leadForm)');
  assert.equal(lead.requests.length,0);
  assert.equal(leadFeedback.textContent,'شماره موبایل را به‌درستی وارد کن.');
  leadForm.values.phone='۰۹۱۲۱۲۳۴۵۶۷';
  lead.context.fetch=async()=>{throw new TypeError('private error')};
  await lead.run('requestReportLead(leadForm)');
  assert(!lead.run('reportPage()').includes('id="report-full"'));
  assert.equal(leadForm.values.phone,'۰۹۱۲۱۲۳۴۵۶۷');
  assert(!leadFeedback.textContent.includes('private error'));
  let releaseLead;
  lead.context.fetch=async(url,options)=>{lead.requests.push({url,options});await new Promise(resolve=>releaseLead=resolve);return {ok:true,json:async()=>({registered:true})}};
  const leadPending=lead.run('requestReportLead(leadForm)');
  assert.equal(leadButton.disabled,true);
  assert.equal(lead.run('reportLeadStatus'),'submitting');
  await lead.run('requestReportLead(leadForm)');
  assert.equal(lead.requests.length,1);
  releaseLead();await leadPending;
  assert.deepEqual(JSON.parse(lead.requests[0].options.body),{phone:'09121234567',consent:true});
  const fullReport=lead.run('reportPage()');
  for(const heading of ['تصویر کلی برند شخصی تو','جایگاه تخصصی','محتوای متمایز','اعتماد مخاطب','مهم‌ترین فرصت رشد تو','مسیر پیشنهادی برای ساخت محتوا','مأموریت تو در این هفته','از تحلیل تا اقدام'])assert(fullReport.includes(heading));
  assert(!fullReport.includes('name="phone"'));
  assert(fullReport.includes('href="#/app/plan"'));
  assert(fullReport.includes('assessment-download'));
  lead.run('saveAssessmentSession()');
  assert(!JSON.stringify([...lead.storage]).includes('09121234567'));
  assert(!JSON.stringify([...lead.storage]).includes('۰۹۱۲۱۲۳۴۵۶۷'));
  lead.run("assessmentAnswers={q11:['انجام یک خدمت']}");
  assert.equal(lead.run('reportViewData().has_product_or_service'),true);
  lead.run("assessmentAnswers={q11:['هیچ‌کدام']}");
  assert.equal(lead.run('reportViewData().has_product_or_service'),false);
  const restoredLead=harness(JSON.parse(lead.storage.get('brandyar-assessment-session-v1')));
  assert.equal(restoredLead.run('reportLeadStatus'),'unchecked');
  restoredLead.context.fetch=async()=>({ok:true,json:async()=>({registered:true})});
  await restoredLead.run('requestReportLead()');
  assert(restoredLead.run('reportPage()').includes('id="report-full"'));
  restoredLead.run("reportLeadStatus='idle'");
  restoredLead.context.fetch=async()=>({ok:false,json:async()=>({error:'نشست منقضی شده است.'})});
  await restoredLead.run('requestReportLead()');
  assert(!restoredLead.run('reportPage()').includes('id="report-full"'));
  const adminElements = new Map();
  const adminListeners = {};
  const adminRequests = [];
  const adminContext = {
    console, AbortController, setTimeout, clearTimeout,
    window:{confirm:()=>true},
    document:{
      getElementById(id){
        if(!adminElements.has(id)) adminElements.set(id,{innerHTML:'',textContent:'',value:'',hidden:true,setAttribute(){},addEventListener(){},focus(){}});
        return adminElements.get(id);
      },
      addEventListener:(name,fn)=>adminListeners[name]=fn
    },
    fetch:async (url,options)=>{
      adminRequests.push({url,options});
      const result = options.method === 'POST' ? {status:'updated'} : url === '/api/admin/me' ? {principal:{role:'owner'},csrf:'test-csrf'} : url === '/api/admin/consultation-slots' ? {slots:[{id:7,starts_at:slot.startsAt,duration_minutes:60,status:'open'}],timeZone:'Asia/Tehran'} : {requests:[{id:3,name:'<img src=x>',phone:'09121234567',starts_at:null,notes:'موضوع تست',status:'pending',created_at:Math.floor(Date.now()/1000)}]};
      return {ok:true,status:200,json:async()=>result};
    }
  };
  vm.createContext(adminContext);
  vm.runInContext(fs.readFileSync(`${__dirname}/admin-panel.js`,'utf8'),adminContext);
  await new Promise(resolve=>setImmediate(resolve));
  const adminMarkup=adminElements.get('requests').innerHTML;
  assert(adminMarkup.includes('نیازمند تماس برای هماهنگی'));
  assert(adminMarkup.includes('id="request-slot-3"'));
  assert(adminMarkup.includes('value="7"'));
  assert(!adminMarkup.includes('۱۹۷۰'));
  assert(!adminMarkup.includes('<img'));
  const confirmButton={disabled:false,dataset:{request:'3',status:'confirmed'}};
  const clickEvent={target:{closest:selector=>selector==='[data-request]'?confirmButton:null}};
  const beforeConfirm=adminRequests.length;
  await adminListeners.click(clickEvent);
  assert.equal(adminRequests.length,beforeConfirm);
  assert(adminElements.get('feedback').textContent.includes('زمان توافق‌شده'));
  adminElements.get('request-slot-3').value='7';
  await adminListeners.click(clickEvent);
  const confirmation=adminRequests.find(item=>item.url==='/api/admin/consultation-status');
  assert.deepEqual(JSON.parse(confirmation.options.body),{requestId:3,status:'confirmed',slotId:7,csrf:'test-csrf'});
  console.log('PASS: assessment regression, preview-before-phone, report unlock, lead validation/loading/failure/refresh/privacy, inline parity, consultation and admin regression');
})().catch(error=>{console.error(error);process.exitCode=1;});
