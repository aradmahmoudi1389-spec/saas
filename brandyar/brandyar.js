const plans=window.BRANDYAR_PLANS;
const titles={dashboard:'داشبورد',plans:'تعرفه‌های برندیـار',activate:'فعال‌سازی آزمایشی',profile:'پروفایل من',identity:'هویت من',guide:'راهنمای برند من',create:'ساخت محتوا',library:'خروجی‌های ذخیره‌شده',calendar:'تقویم محتوا',settings:'تنظیمات'};
const PRIVATE=new Set(['dashboard','identity','guide','create','library','calendar','settings']);
const app=document.querySelector('#app'),title=document.querySelector('#page-title');
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ID=()=>window.BRANDYAR_IDENTITY;
const access=()=>ID().state.access||{status:'none',planId:'',planName:'',simulation:true};
const me=()=>ID().current();
const hasAccess=()=>['trial','active'].includes(access().status);
const signedIn=()=>ID().state.signedIn;
const testCompleted=()=>Boolean(me().testInsight?.exists);
const faDate=v=>v?new Date(v*1000).toLocaleString('fa-IR',{dateStyle:'medium',timeStyle:'short'}):'';
let step=0;

function empty(icon,heading,text,action=''){return `<div class="empty"><div class="empty-icon">${icon}</div><h3>${esc(heading)}</h3><p>${esc(text)}</p>${action?`<a class="button" href="${action[0]}">${esc(action[1])}</a>`:''}</div>`}
function shell(heading,description,body){return `<section class="page"><div class="page-heading"><span class="eyebrow">برندیـار · فضای خصوصی</span><h2>${heading}</h2><p>${esc(description)}</p></div>${body}</section>`}
function flowNotice(){const a=access();return `<div class="flow-status" role="status"><span class="tag">${esc(ID().accessLabel(a))}</span><span>${a.planName?`پلن ${esc(a.planName)}`:'پلنی فعال نیست'} · محیط آزمایشی بدون پرداخت واقعی</span></div>`}
function loadingView(){return shell('در حال بارگذاری','وضعیت حساب و هویت خوانده می‌شود…','<article class="card"><p>کمی صبر کن.</p></article>')}
function errorView(){return shell('وضعیت خوانده نشد','ارتباط با سرور برقرار نشد یا نشست معتبر نیست.',`<article class="card">${empty('◇','بازیابی اطلاعات انجام نشد','ممکن است نشست منقضی شده باشد. دوباره تلاش کن یا از مسیر تست وارد شو.',['/personal-brand','رفتن به تست'])}<button class="button secondary" type="button" data-retry>تلاش دوباره</button></article>`)}
function signedOutView(){return shell('ورود لازم است','این فضای خصوصی فقط برای کاربر واردشده در دسترس است.',`<article class="card">${empty('◌','نشست کاربری پیدا نشد','برندیـار بعد از تست پرسونال برند و با همان نشست باز می‌شود.',['/personal-brand','رفتن به تست پرسونال برند'])}</article>`)}
function gateView(){const copy=ID().accessCopy();return shell(copy.title,copy.text,`${flowNotice()}<article class="card activation-card"><span class="tag">${esc(copy.label)}</span><h3>${esc(copy.title)}</h3><p>${esc(copy.text)}</p><div class="page-actions"><a class="button" href="/brandyar/plans">مشاهدهٔ تعرفه‌ها</a><a class="button secondary" href="/brandyar/profile">پروفایل من</a></div></article>`)}
function noTestView(){return shell('دسترسی هنوز آماده نیست','برای ورود به فضای خصوصی، ابتدا تست را کامل کن.',`<article class="card">${empty('◌','تست هنوز کامل نشده است','برندیـار فقط بعد از پایان موفق تست پیشنهاد می‌شود. ابتدا تست را کامل کن و نتیجه‌ات را ببین.',['/personal-brand','رفتن به تست'])}</article>`)}

function dashboard(){
  if(!testCompleted())return noTestView();
  if(!hasAccess())return gateView();
  const v=me(),status=v.status;
  const next=status==='approved'?{text:'هویتت تأیید شده است. در مرحله‌های بعدی راهنمای برند روی همین پایه ساخته می‌شود.',label:'مرور هویت'}:status==='ready_for_review'?{text:'اطلاعاتت آمادهٔ مرور نهایی است؛ تأیید فقط با خودت انجام می‌شود.',label:'مرور نهایی'}:status==='needs_revision'?{text:'بعد از ویرایش، فقط بخش تغییریافته از حالت تأیید خارج شده است. آن را بازبینی کن.',label:'بازبینی هویت'}:{text:'بخش‌های ناقص هویت حرفه‌ای‌ات را تکمیل کن.',label:'رفتن به هویت من'};
  return `<section class="page"><div class="hero"><div><span class="eyebrow">فضای آزمایشی برندیـار</span><h2>هویت حرفه‌ای تو از همین‌جا شکل می‌گیرد.</h2><p>این داشبورد مستقل از نتیجهٔ تست است. هر چیزی که در هویت برند ثبت می‌کنی باید با تأیید خودت تکمیل شود.</p></div><a class="button" href="#identity">${status==='not_started'?'شروع ساخت هویت':'ادامهٔ ساخت هویت'}</a></div>${flowNotice()}<div class="section-title"><div><h2>نمای کلی مسیر</h2><p>وضعیت از دادهٔ ذخیره‌شدهٔ هویت محاسبه می‌شود.</p></div></div><div class="grid"><article class="card metric"><span class="eyebrow">تکمیل هویت</span><strong>${v.completionPercentage}٪</strong><small>${esc(ID().statusLabel(status))}</small><div class="progress"><i style="width:${v.completionPercentage}%"></i></div></article><article class="card metric"><span class="eyebrow">وضعیت هویت</span><strong>${esc(ID().statusLabel(status))}</strong><small>آخرین ویرایش: ${v.updatedAt?faDate(v.updatedAt):'ثبت نشده'}</small></article><article class="card metric"><span class="eyebrow">تأیید</span><strong>${v.approvedAt?'تأییدشده':'تأییدنشده'}</strong><small>${v.approvedAt?`زمان تأیید: ${faDate(v.approvedAt)}`:'تا تأیید نهایی، اطلاعات پیش‌نویس است.'}</small></article></div><div class="split"><article class="card panel"><h3>اقدام پیشنهادی بعدی</h3><p>${next.text}</p><a class="button" href="#identity" style="margin-top:18px">${next.label}</a></article><article class="card panel"><h3>آخرین خروجی‌ها</h3>${empty('✦','هنوز خروجی‌ای ساخته نشده','تولید واقعی محتوا در این مرحله ساخته نشده است.')}</article></div></section>`;
}

function plansView(){
  if(!testCompleted())return shell('تعرفه‌های برندیـار','این صفحه فقط بعد از پایان تست در دسترس است.',`<article class="card">${empty('◌','تست هنوز کامل نشده است','برای دیدن پیشنهاد برندیـار، ابتدا تست را کامل کن.',['/personal-brand','رفتن به تست'])}</article>`);
  const selected=access().planId;
  return shell('ادامهٔ مسیر در برندیـار','برندیـار محصولی خصوصی و جدا از تست است؛ این تعرفه‌ها فقط مربوط به همین محصول‌اند.',`${flowNotice()}<div class="notice">قیمت واقعی هنوز در پروژه تعریف نشده است. موارد زیر دادهٔ نمونه‌اند و قیمت نهایی یا تعهد پرداخت محسوب نمی‌شوند.</div><div class="plans-grid">${plans.filter(p=>p.isAvailable).map(p=>`<article class="card plan-card ${selected===p.id?'selected':''}"><div class="plan-head"><div><h3>${esc(p.name)}</h3></div>${selected===p.id?'<span class="tag selected-mark">پلن فعلی</span>':''}</div><p>${esc(p.description)}</p><ul>${p.features.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><div class="limits"><strong>محدودیت‌ها</strong>${p.limits.map(x=>`<span>${esc(x)}</span>`).join('')}</div><div class="plan-price">قیمت در این نسخه مشخص نشده</div><button class="button ${selected===p.id?'secondary':''}" data-plan="${esc(p.id)}" ${hasAccess()&&selected===p.id?'disabled':''}>${hasAccess()&&selected===p.id?'دسترسی این پلن فعال است':'ادامه با این پلن'}</button></article>`).join('')}</div><div class="page-actions"><a class="button secondary" href="/brandyar/profile">پروفایل من</a><a class="text-link" href="/personal-brand">بازگشت به نتیجهٔ تست</a></div>`);
}

function activateView(){
  if(!testCompleted())return shell('فعال‌سازی در دسترس نیست','ابتدا تست را کامل کن.',`<article class="card">${empty('◌','تست هنوز کامل نشده است','برای این مرحله نتیجهٔ کامل تست لازم است.',['/personal-brand','رفتن به تست'])}</article>`);
  if(hasAccess())return activationMessage('done','دسترسی از قبل فعال است',`پلن ${access().planName||'فعال'} برای حساب تو فعال است.`);
  const plan=plans.find(p=>p.id===access().planId);
  if(!plan)return shell('انتخاب پلن لازم است','قبل از فعال‌سازی، یک پلن برندیـار را انتخاب کن.',`<article class="card">${empty('◇','هنوز پلنی انتخاب نشده است','انتخاب پلن فقط مرحلهٔ بعدی جریان آزمایشی است.',['/brandyar/plans','رفتن به تعرفه‌ها'])}</article>`);
  return shell('فعال‌سازی آزمایشی','پلن انتخاب‌شده را برای بررسی جریان محصول فعال کن.',`${flowNotice()}<article class="card activation-card"><span class="eyebrow">پلن انتخاب‌شده</span><h3>${esc(plan.name)}</h3><p>این محیط آزمایشی است و پرداخت واقعی انجام نمی‌شود. فعال‌سازی فقط برای بررسی مسیر ورود به محصول است.</p><div class="activation-actions"><button class="button" data-activate="grant">فعال‌سازی و ورود آزمایشی</button><button class="button secondary" data-activate="cancel">انصراف و بازگشت</button></div><p class="activation-error muted" data-activation-error role="alert" aria-live="polite"></p></article><a class="text-link" href="/brandyar/plans">بازگشت به تعرفه‌ها</a>`);
}

function activationMessage(status,heading,text){return shell('فعال‌سازی آزمایشی',heading,`<article class="card status-card"><span class="tag">${status==='done'?'دسترسی فعال':'تغییری ثبت نشد'}</span><h3>${esc(heading)}</h3><p>${esc(text)}</p><div class="page-actions"><a class="button" href="/brandyar/dashboard">ورود به داشبورد</a><a class="button secondary" href="/brandyar/plans">تعرفه‌ها</a></div></article>`)}

function profileView(){
  if(!signedIn())return signedOutView();
  const copy=ID().accessCopy(),a=access(),state=ID().accessState();
  const inPanel=state==='active'&&hasAccess();
  const actions=inPanel?`<a class="button" href="/brandyar/dashboard">ورود به پنل برندیـار</a><a class="button secondary" href="#settings">مدیریت اشتراک</a>`:`<a class="button" href="/brandyar/plans">${esc(copy.action)}</a>${state==='completed_no_access'?'<a class="button secondary" href="/brandyar/activate">فعال‌سازی آزمایشی</a>':''}`;
  const plan=a.planName?`<div class="profile-plan"><span>پلن</span><strong>${esc(a.planName)}</strong><small>${a.status==='trial'?'فعال‌سازی آزمایشی · بدون پرداخت واقعی':'دسترسی فعال'}</small></div>`:'<p class="muted">اطلاعات پلن برای این حساب ثبت نشده است.</p>';
  return shell('پروفایل من','وضعیت دسترسی‌ات به برندیـار از همین‌جا مشخص است.',`<article class="card profile-access" data-access="${esc(state)}"><div class="profile-access-head"><div><span class="eyebrow">برندیـار · قابلیت حساب تو</span><h3>${esc(copy.title)}</h3><p>${esc(copy.text)}</p></div><span class="tag${state==='active'?' ok':''}">${esc(copy.label)}</span></div>${state==='ended'?'':plan}<div class="page-actions">${actions}</div>${ID().state.demoAuth?'<p class="muted demo-note">این دسترسی به نشست فعلی همین مرورگر وابسته است و جای حساب کاربری کامل را نمی‌گیرد.</p>':''}</article>`);
}

const labels={not_started:'شروع نشده',in_progress:'در حال تکمیل',ready_for_review:'آمادهٔ مرور',approved:'تأییدشده',needs_revision:'نیازمند بازبینی'};
const sectionStatus=(v,s)=>{const approved=v.approvedSections.includes(s.id);if(approved)return {key:'approved',label:'تأییدشده'};if(v.draftSections.includes(s.id))return {key:'complete',label:'تکمیل‌شده'};return {key:'incomplete',label:'ناقص'}};
const sectionMissing=(v,s)=>s.fields.map(([key])=>key).filter(key=>ID().required.includes(key)&&!ID().has(v,key));

function identity(){
  if(!hasAccess())return gateView();
  const v=me(),total=ID().sections.length;
  step=Math.max(0,Math.min(total-1,step));
  const section=ID().sections[step],status=sectionStatus(v,section);
  return shell('هویت من','هویت حرفه‌ای‌ات را در چند قدم کوتاه بساز؛ اطلاعات در حساب تو ذخیره می‌شود.',`${identityStatus(v)}<div class="identity-progress"><span>مرحلهٔ ${step+1} از ${total}</span><strong>${v.completionPercentage}٪ تکمیل شده</strong><div class="progress"><i style="width:${v.completionPercentage}%"></i></div></div><form class="card form-card identity-form" data-form="identity" data-section="${esc(section.id)}"><div class="section-kicker">بخش ${step+1} · <span class="section-status ${status.key}">${status.label}</span></div><h3>${esc(section.title)}</h3><p class="form-help">اطلاعاتی را بنویس که واقعاً دربارهٔ مسیر حرفه‌ای تو درست است؛ چیزی را حدس نمی‌زنیم.</p><div class="form-grid">${section.fields.map(([key,label,type,placeholder])=>identityField(key,label,type,placeholder)).join('')}</div><p class="identity-error" data-identity-error role="alert"></p><div class="identity-actions">${step>0?'<button class="button secondary" type="button" data-step="previous">بازگشت</button>':''}<button class="button secondary" type="button" data-identity-action="draft">ذخیرهٔ پیش‌نویس</button><button class="button" type="submit">${step===total-1?'رفتن به مرور نهایی':'ادامه'}</button></div></form><div class="section-status-list"><span class="eyebrow">وضعیت بخش‌ها</span>${ID().sections.map((s,i)=>{const st=sectionStatus(v,s);return `<button type="button" class="${st.key}" data-step="${i}" ${i===step?'aria-current="step"':''}>${st.key==='approved'?'✓':st.key==='complete'?'●':'○'} ${esc(s.title)}</button>`}).join('')}</div>${step===total-1?`<div class="page-actions"><a class="button" href="#identity/review">مشاهدهٔ مرور و تأیید</a></div>`:''}`);
}

function identityValue(v,key){if(key==='targetDescription')return v.targetAudience.description;if(key==='primaryGroup')return v.targetAudience.primaryGroup;if(key==='needs'||key==='problems')return v.targetAudience[key];return v[key]}
function identityText(v,key){const x=identityValue(v,key);return Array.isArray(x)?x.join('، '):String(x||'')}
function identityField(key,label,type,placeholder){const required=ID().required.includes(key),value=identityText(me(),key);const input=type==='textarea'?`<textarea id="${key}" name="${key}" placeholder="${esc(placeholder)}">${esc(value)}</textarea>`:`<input id="${key}" name="${key}" value="${esc(value)}" placeholder="${esc(placeholder)}" ${required?'required':''}>`;return `<div class="field ${type==='textarea'?'full':''}"><label for="${key}">${esc(label)}${required?' <b aria-label="ضروری">*</b>':''}</label>${input}<small class="field-help">${required?'برای ساخت پایهٔ هویت لازم است.':'اختیاری است؛ اگر هنوز پاسخ روشنی نداری، خالی بگذار.'}</small></div>`}
function identityStatus(v){const insight=v.testInsight;const proposal=insight.exists&&!insight.isResolved?'<span class="tag warn">بینش تست در انتظار تصمیم</span>':'';return `<div class="identity-overview card"><div><span class="eyebrow">وضعیت هویت</span><strong>${labels[v.status]||labels.not_started}</strong><small>${v.updatedAt?`آخرین ویرایش: ${faDate(v.updatedAt)}`:'هنوز ذخیره‌ای انجام نشده است.'}${v.status==='needs_revision'?' · فقط بخش تغییریافته از تأیید خارج شده است.':''}</small></div><div class="tag-row"><span class="tag">${v.completionPercentage}٪</span>${proposal}</div></div>`}

function insightCard(v){
  const t=v.testInsight;
  if(!t.exists)return `<article class="card insight empty-insight"><span class="eyebrow">بینش حاصل از تست</span><p>نتیجهٔ تستی برای استفاده در این بخش پیدا نشد. می‌توانی هویت را بدون آن کامل کنی.</p><a class="text-link" href="/personal-brand">رفتن به تست</a></article>`;
  const source=t.source==='user_approved'?'تأییدشدهٔ خودت':'متن نتیجهٔ تست · تأییدنشده';
  return `<article class="card insight"><span class="eyebrow">بینش حاصل از تست</span><span class="tag ${t.isApprovedForBrandUse?'ok':''}">${esc(source)}</span><p>${esc(t.summary)}</p><p class="muted">این بینش به‌صورت خودکار وارد هویت نمی‌شود و با نوشته‌های خودت یکی نیست.</p><div class="identity-actions">${t.isApprovedForBrandUse?'<button type="button" class="button secondary" data-insight="ignore">نادیده‌گرفتن این بینش</button>':'<button type="button" class="button" data-insight="use">استفاده در هویت</button><button type="button" class="button secondary" data-insight="ignore">نادیده‌گرفتن</button>'}</div><p class="insight-error muted" data-insight-error role="alert"></p></article>`;
}

function identityReview(){
  if(!hasAccess())return gateView();
  const v=me(),missing=ID().missing(v),isApproved=v.status==='approved',needsRevision=v.status==='needs_revision';
  const missingText=missing.length?`<article class="card review-missing"><span class="tag warn">اطلاعات ضروری ناقص</span><h3>چند مورد ضروری هنوز خالی است</h3><ul>${missing.map(key=>{const s=ID().sections.find(x=>x.fields.some(([k])=>k===key)),label=s.fields.find(([k])=>k===key)[1];return `<li>${esc(label)} — در بخش «${esc(s.title)}» <button type="button" class="text-link" data-edit-section="${ID().sections.indexOf(s)}">تکمیل</button></li>`}).join('')}</ul><p>این موارد برای ساخت پایهٔ هویت لازم‌اند؛ ما آن‌ها را به‌جای تو پر نمی‌کنیم.</p></article>`:'';
  const insightPending=v.testInsight.exists&&!v.testInsight.isResolved;
  const canApprove=!isApproved&&!missing.length&&!insightPending;
  const stateTag=isApproved?'<span class="tag ok">تأییدشده توسط شما</span>':needsRevision?'<span class="tag warn">نیازمند بازبینی</span>':missing.length?'<span class="tag warn">اطلاعات ناقص</span>':'<span class="tag">آمادهٔ تأیید</span>';
  return shell('مرور نهایی هویت','اطلاعات را پیش از ثبت نهایی بررسی کن. هیچ نتیجه‌ای از تست بدون تأیید تو وارد هویت نشده است.',`${identityStatus(v)}${missingText}<div class="review-grid">${ID().sections.map((s,i)=>{const st=sectionStatus(v,s);return `<article class="card review-card" data-section="${esc(s.id)}"><div class="review-head"><h3>${esc(s.title)}</h3><div class="review-tools"><span class="tag ${st.key}">${st.label}</span><button type="button" class="text-link" data-edit-section="${i}">ویرایش</button></div></div>${s.fields.map(([key,label])=>{const empty=!ID().has(v,key),required=ID().required.includes(key);return `<div class="review-row ${empty?'missing':''}"><span>${esc(label)}${required?' *':''}</span><strong>${esc(identityText(v,key)||(required?'وارد نشده — ضروری':'وارد نشده'))}</strong></div>`}).join('')}</article>`}).join('')}</div>${insightCard(v)}<article class="card review-note">${stateTag}<h3>${isApproved?'هویت تأییدشده':'تأیید نهایی'}</h3><p class="muted">«ذخیرهٔ پیش‌نویس» اطلاعات را نگه می‌دارد ولی هویت را تأیید نمی‌کند. «تأیید هویت» نسخهٔ تأییدشده را با زمان ثبت می‌کند. بعد از تأیید، ویرایش هر بخش فقط همان بخش را از حالت تأیید خارج می‌کند.</p>${isApproved?`<p>زمان تأیید: ${faDate(v.approvedAt)} · آخرین ویرایش: ${faDate(v.updatedAt)}</p><div class="page-actions"><a class="button secondary" href="/brandyar/dashboard">بازگشت به داشبورد</a></div>`:`<div class="identity-actions"><button class="button secondary" type="button" data-identity-action="draft">ذخیرهٔ پیش‌نویس</button><button class="button" type="button" data-identity-action="approve" ${canApprove?'':'disabled aria-describedby="approve-block"'}>${needsRevision?'تأیید دوبارهٔ هویت':'تأیید هویت'}</button></div><p id="approve-block" class="identity-error" data-identity-error role="alert">${missing.length?'برای تأیید، اطلاعات ضروری را کامل کن.':insightPending?'بینش تست را تأیید کن یا نادیده بگیر، بعد هویت را تأیید کن.':''}</p>`}</article>`);
}

function attribution(v){const approved=v.approvedSections,badges=[];if(approved.length)badges.push(`<span class="tag ok">${approved.length} بخش تأییدشده</span>`);if(v.draftSections.length>approved.length)badges.push(`<span class="tag">${v.draftSections.length-approved.length} بخش تکمیل‌شدهٔ تأییدنشده</span>`);return badges.join('')}

function guide(){return shell('راهنمای برند من','یک محل آماده برای پیام، لحن و واژه‌هایی که بعداً تأیید می‌کنی.',`<article class="card">${empty('✦','راهنمای برند هنوز ساخته نشده','اول هویت حرفه‌ای‌ات را تکمیل و تأیید کن. بعد می‌توانیم پیام اصلی، لحن و واژه‌های مناسب تو را بررسی و تأیید کنیم.',['#identity','رفتن به هویت من'])}</article><div class="grid"><article class="card"><span class="tag">پیشنهادی</span><h3>پیام اصلی</h3><p>پس از تکمیل هویت حرفه‌ای نمایش داده می‌شود.</p></article><article class="card"><span class="tag">در انتظار اطلاعات</span><h3>لحن برند</h3><p>هنوز لحن تأییدشده‌ای ثبت نشده است.</p></article><article class="card"><span class="tag">در انتظار اطلاعات</span><h3>واژه‌های راهنما</h3><p>واژه‌های پیشنهادی و نامناسب اینجا نگهداری می‌شوند.</p></article></div>`)}
function create(){return shell('ساخت محتوا','ایدهٔ خامت را وارد کن؛ در این نسخه هنوز تولید واقعی متن انجام نمی‌شود.',`<form class="card form-card" data-form="create"><div class="notice">این فرم فقط برای آماده‌سازی مسیر است. هیچ متن نهایی یا تولیدشده‌ای بدون تأیید تو ذخیره نمی‌شود.</div><div class="form-grid">${select('goal','هدف محتوا',['آموزش','اعتمادسازی','معرفی خدمت','ارتباط با مخاطب'])}${select('format','قالب محتوا',['پست متنی','اسکریپت ویدیو','استوری','خبرنامه'])}<div class="field full"><label for="idea">موضوع یا ایدهٔ خام</label><textarea id="idea" name="idea" placeholder="ایده‌ات را کوتاه بنویس."></textarea></div>${select('pillar','ستون محتوایی',['هنوز ستونی ساخته نشده'])}</div><button class="button" type="submit">آماده‌سازی پیش‌نویس</button><span class="save-state" aria-live="polite"></span></form><article class="card" style="margin-top:16px">${empty('✦','خروجی اینجا نمایش داده می‌شود','بعد از آماده‌شدن مسیر تولید، پیش‌نویس پیشنهادی در این بخش قابل بررسی خواهد بود.')}</article>`)}
function select(name,label,options){return `<div class="field"><label for="${name}">${esc(label)}</label><select id="${name}" name="${name}"><option value="">انتخاب کن</option>${options.map(v=>`<option>${esc(v)}</option>`).join('')}</select></div>`}
function library(){return shell('خروجی‌های ذخیره‌شده','اینجا محل نگهداری متن‌ها و ایده‌هایی است که خودت تأیید کرده‌ای.',`<div class="status-list"><span class="tag">همه</span><span class="tag">پیشنهادی</span><span class="tag">تأییدشده</span></div><article class="card" style="margin-top:16px">${empty('▤','کتابخانه هنوز خالی است','اول هویت حرفه‌ای‌ات را بساز، سپس از بخش ساخت محتوا اولین خروجی را برای بررسی ایجاد کن.',['#create','ساخت اولین محتوا'])}</article>`)}
function calendar(){return shell('تقویم محتوا','یک نمای ساده برای ایده‌ها و برنامه‌های آینده؛ بدون زمان‌بندی یا انتشار خودکار.',`<div class="status-list"><span class="tag">ایده</span><span class="tag">پیش‌نویس</span><span class="tag">آماده</span><span class="tag">انجام‌شده</span></div><div class="calendar" style="margin-top:18px">${['شنبه','یکشنبه','دوشنبه','سه‌شنبه','چهارشنبه','پنجشنبه','جمعه'].map(day=>`<article class="day"><h3>${day}</h3><small>بدون برنامه</small><div class="placeholder">+ جای ایدهٔ آینده</div></article>`).join('')}</div>`)}

function settings(){
  if(!hasAccess())return gateView();
  const v=me(),a=access(),ended=!hasAccess();
  return shell('تنظیمات','مدیریت وضعیت فضای خصوصی برندیـار و داده‌های هویت.',`<article class="card"><div class="setting-row"><div><strong>وضعیت دسترسی</strong><small>${esc(ID().accessLabel(a))}${a.simulation?' · بدون پرداخت واقعی':''}</small></div><span class="tag${hasAccess()?' ok':''}">${esc(a.planName||'بدون پلن')}</span></div><div class="setting-row"><div><strong>اطلاعات هویت</strong><small>${esc(ID().statusLabel(v.status))} · ${v.completionPercentage}٪</small></div><a class="button secondary" href="#identity/review">مشاهده</a></div><div class="setting-row"><div><strong>پروفایل و مسیر ورود</strong><small>وضعیت دسترسی از پروفایل هم قابل مشاهده است.</small></div><a class="button secondary" href="/brandyar/profile">پروفایل من</a></div>${ended?'':`<div class="setting-row"><div><strong>مدیریت اشتراک</strong><small>پرداخت واقعی و تمدید خودکار در این نسخه وجود ندارد.</small></div><span class="tag">آزمایشی</span></div><div class="setting-row"><div><strong>پایان‌دادن به دسترسی آزمایشی</strong><small>می‌توانی دسترسی را متوقف کنی؛ اطلاعات هویت پاک نمی‌شود.</small></div><button class="button secondary" type="button" data-revoke>پایان دسترسی</button></div>`}<div class="setting-row"><div><strong>حریم خصوصی</strong><small>داده‌های هویت در حساب همین نشست ذخیره می‌شوند، نه فقط در مرورگر.</small></div><span class="tag">توضیح داده شد</span></div></article><p class="identity-error" data-settings-error role="alert"></p>`);
}

const views={dashboard,plans:plansView,activate:activateView,profile:profileView,identity,guide,create,library,calendar,settings};

async function load(){
  app.innerHTML=loadingView();
  try{await ID().refresh()}
  catch{title.textContent='وضعیت خوانده نشد';app.innerHTML=errorView();bind();return}
  route();
}

function route(){
  let key=location.hash.slice(1).split('/')[0]||'dashboard';
  if(location.pathname==='/brandyar/plans')key='plans';
  else if(location.pathname==='/brandyar/activate')key='activate';
  else if(location.pathname==='/brandyar/dashboard')key='dashboard';
  else if(location.pathname==='/brandyar/profile')key='profile';
  const sub=location.hash.slice(1).split('/')[1];
  if(!titles[key])key='dashboard';
  if(PRIVATE.has(key)){
    if(!signedIn()){title.textContent='ورود لازم است';app.innerHTML=signedOutView();bind();return}
    if(!testCompleted()){title.textContent=titles.plans;app.innerHTML=noTestView();bind();return}
    if(!hasAccess()){title.textContent=titles.plans;app.innerHTML=gateView();bind();return}
  }
  let html;
  if(key==='identity'&&sub==='review'){title.textContent='مرور و تأیید هویت';html=identityReview()}
  else{title.textContent=titles[key];html=views[key]()}
  app.innerHTML=html;
  document.querySelectorAll('[data-page]').forEach(a=>a.classList.toggle('active',a.dataset.page===key));
  bind();
}

function sectionOf(key){return ID().sections.find(s=>s.fields.some(([k])=>k===key))?.id}
function collectForm(form){
  const section=ID().sections.find(s=>s.id===form.dataset.section),values={};
  for(const [key] of section.fields){
    const raw=Object.is(form.get(key),undefined)?'':form.get(key);
    if(ID().lists.includes(key))values[key]=ID().normalizeList(raw);
    else values[key]=String(raw).trim();
  }
  return {values,section:section.id};
}

function bind(){
  document.querySelector('[data-retry]')?.addEventListener('click',load);
  document.querySelector('[data-form=create]')?.addEventListener('submit',e=>{e.preventDefault();e.target.querySelector('.save-state').textContent='در این نسخه هنوز تولید واقعی فعال نشده است.'});
  document.querySelectorAll('[data-plan]').forEach(b=>b.addEventListener('click',()=>{location.href='/brandyar/activate'}));
  document.querySelectorAll('[data-activate]').forEach(b=>b.addEventListener('click',async()=>{
    if(b.dataset.activate==='cancel'){location.href='/brandyar/plans';return}
    const planId=access().planId;if(!planId){location.href='/brandyar/plans';return}
    b.disabled=true;
    try{await ID().grant(planId);location.href='/brandyar/dashboard'}
    catch(error){b.disabled=false;const area=document.querySelector('[data-activation-error]');if(area)area.textContent=error.message}
  }));
  document.querySelector('[data-revoke]')?.addEventListener('click',async e=>{
    e.target.disabled=true;
    try{await ID().revoke();await load()}
    catch(error){e.target.disabled=false;const area=document.querySelector('[data-settings-error]');if(area)area.textContent=error.message}
  });
  document.querySelectorAll('[data-step]').forEach(b=>b.addEventListener('click',()=>{step=Number(b.dataset.step);if(location.hash!=='#identity')location.hash='#identity';else route()}));
  document.querySelectorAll('[data-edit-section]').forEach(b=>b.addEventListener('click',()=>{step=Number(b.dataset.editSection);location.hash='#identity';route()}));
  document.querySelectorAll('[data-insight]').forEach(b=>b.addEventListener('click',async()=>{
    b.disabled=true;
    try{await ID().save({},b.dataset.insight==='use');route()}
    catch(error){b.disabled=false;const area=document.querySelector('[data-insight-error]');if(area)area.textContent=error.message}
  }));
  document.querySelectorAll('[data-identity-action]').forEach(b=>b.addEventListener('click',async()=>{
    const action=b.dataset.identityAction,form=document.querySelector('[data-form=identity]'),errorArea=document.querySelector('[data-identity-error]');
    if(errorArea)errorArea.textContent='';
    b.disabled=true;
    try{
      if(action==='draft'){
        if(form){const {values,section}=collectForm(new FormData(form));await ID().save(values,undefined,[section])}
        if(location.pathname.startsWith('/brandyar/')&&!location.hash){location.href='/brandyar/dashboard';return}
        route();return;
      }
      if(action==='approve'){
        await ID().approve(Math.floor(Date.now()/1000));
        step=0;route();return;
      }
    }catch(error){
      if(errorArea)errorArea.textContent=error.message;
    }
    b.disabled=false;
  }));
  document.querySelector('[data-form=identity]')?.addEventListener('submit',async e=>{
    e.preventDefault();
    const form=e.target,submit=e.submitter,errorArea=form.querySelector('[data-identity-error]');
    const {values,section}=collectForm(new FormData(form));
    const total=ID().sections.length;
    submit.disabled=true;
    try{
      await ID().save(values,undefined,[section]);
      errorArea.textContent='';
      if(step<total-1){step+=1;route()}
      else location.hash='#identity/review';
    }catch(error){
      errorArea.textContent=error.message;
      submit.disabled=false;
    }
  });
}

document.querySelector('#theme-toggle').addEventListener('click',()=>{const root=document.documentElement,dark=root.dataset.theme==='dark';root.dataset.theme=dark?'light':'dark';try{localStorage.setItem('brandyar-theme',dark?'light':'dark')}catch{}});
try{document.documentElement.dataset.theme=localStorage.getItem('brandyar-theme')||'light'}catch{}
window.addEventListener('hashchange',route);
load();
