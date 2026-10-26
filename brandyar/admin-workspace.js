'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const number = value => value == null ? '—' : new Intl.NumberFormat('fa-IR').format(value);
  const date = value => value ? new Intl.DateTimeFormat('fa-IR', {dateStyle:'medium',timeStyle:'short'}).format(new Date(typeof value === 'number' ? value * 1000 : value)) : 'ثبت نشده';
  const json = value => `<pre>${esc(typeof value === 'string' ? value : JSON.stringify(value,null,2))}</pre>`;
  const statusNames = {new:'جدید',contacted:'تماس گرفته‌شده',qualified:'واجد شرایط',converted:'تبدیل‌شده',archived:'آرشیوشده',started:'شروع‌شده',completed:'تکمیل‌شده',preview_shown:'پیش‌نمایش دیده‌شده',report_unlocked:'گزارش ثبت‌شده',draft:'پیش‌نویس',published:'منتشرشده',failed:'ناموفق',success:'موفق',running:'در حال اجرا'};
  const roleNames = {owner:'مالک',admin:'مدیر',crm_manager:'مدیر ارتباط با مشتری',content_manager:'مدیر محتوا',analyst:'تحلیل‌گر',support:'پشتیبان',product:'محصول',finance:'مالی',viewer:'مشاهده‌گر'};
  const labels = {leads:'لیدهای جدید',assessments:'ارزیابی‌های ثبت‌شده',completed:'ارزیابی‌های تکمیل‌شده',overdue:'وظایف عقب‌افتاده',analysis_started:'شروع تحلیل',analysis_ready:'تحلیل موفق',analysis_failed:'تحلیل ناموفق',assessment_stored:'ذخیرهٔ ارزیابی',lead_registered:'ثبت شماره'};
  const icons = ['◫','♙','◎','▤','☷','✧','▱','▧','♧','▥','◷','⚙'];
  let bootstrap, section = location.pathname.split('/')[2] || 'overview', page = 0, viewData, identity = '', sequence = 0;
  const can = permission => bootstrap?.permissions.includes(permission);
  async function api(url, body) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), body?.action === 'lab' || body?.action === 'regenerate' ? 135000 : 65000);
    try {
      const response = await fetch(url, {credentials:'same-origin',cache:'no-store',signal:controller.signal,...(body ? {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)} : {})});
      const data = await response.json();
      if (response.status === 401 && !$('login-form')) { location.assign('/admin/login'); throw new Error('نشست شما پایان یافته است.'); }
      if (!response.ok) throw new Error(data.error || 'درخواست انجام نشد؛ دوباره تلاش کنید.');
      return data;
    } catch (error) {
      if (['AbortError','TypeError','SyntaxError'].includes(error.name)) throw new Error('ارتباط با سرور کامل نشد؛ دوباره تلاش کنید.');
      throw error;
    } finally { clearTimeout(timer); }
  }
  if ($('login-form')) {
    for (const [id,url] of [['login-form','/api/auth/login'],['mfa-form','/api/auth/mfa/verify']]) $(id).addEventListener('submit', async event => {
      event.preventDefault();
      const button = event.target.querySelector('button'); button.disabled = true; $('feedback').textContent = 'در حال بررسی…';
      try {
        const values = Object.fromEntries(new FormData(event.target));
        if (values.code) values.code = values.code.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d)).replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d));
        await api(url, values);
        if (id === 'login-form') {event.target.reset();event.target.hidden = true;$('mfa-form').hidden = false;$('mfa-form').querySelector('input').focus();$('feedback').textContent = 'کد برنامهٔ تأیید هویت را وارد کنید.';}
        else location.assign('/admin');
      } catch { $('feedback').textContent = 'ورود انجام نشد؛ اطلاعات یا کد را بررسی کنید. پس از چند تلاش ناموفق کمی صبر کنید.'; }
      finally {button.disabled = false;}
    });
    return;
  }
  function empty(title, description) {return `<div class="empty"><span class="empty-icon">◌</span><h2>${esc(title)}</h2><p>${esc(description)}</p></div>`;}
  function notice(text) {return text ? `<div class="notice">${esc(text)}</div>` : '';}
  function button(action, title, id='', classes='secondary') {return `<button type="button" class="${classes}" data-action="${esc(action)}" data-id="${esc(id)}">${esc(title)}</button>`;}
  function table(headings, rows) {return rows.length ? `<div class="table-wrap"><table><thead><tr>${headings.map(v=>`<th scope="col">${esc(v)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(v=>`<td>${v}</td>`).join('')}</tr>`).join('')}</tbody></table></div>` : empty('هنوز داده‌ای برای نمایش نیست','با ثبت فعالیت واقعی در این بازه، اطلاعات اینجا نمایش داده می‌شود. می‌توانید بازهٔ زمانی را تغییر دهید.');}
  function badge(value, archived=false) {return `<span class="badge ${archived?'archived':''}">${esc(archived?'آرشیوشده':statusNames[value] || value || 'ثبت نشده')}</span>`;}
  function shortId(id) {return `<bdi class="inline-id" title="${esc(id)}">${esc(id?.slice(0,8) || '—')}</bdi>`;}
  function filtered(rows) {const q = $('search').value.trim();return q ? rows.filter(v => JSON.stringify(v).includes(q)) : rows;}
  function paint() {
    const data = viewData;
    if (!data) return;
    if (data.record) return detail(data.record);
    let html = '';
    if (['overview','reports'].includes(section)) {
      const metrics = Object.entries(data.counts).map(([key,value])=>`<article class="metric"><p>${esc(labels[key])}</p><strong class="number">${number(value)}</strong><small>${key==='overdue'?'وظایف باز تا این لحظه':'دادهٔ واقعی در بازهٔ انتخاب‌شده'}</small></article>`).join('');
      html = `<div class="metrics">${metrics}</div><div class="split"><section class="panel"><div class="panel-heading"><h2>مسیر ارزیابی، به روایت داده</h2><span class="minor">رویدادهای ثبت‌شده</span></div>${Object.keys(data.events).length ? Object.entries(data.events).map(([key,value])=>`<div class="row"><span><i class="dot"></i>${esc(labels[key]||key)}</span><strong>${number(value)}</strong></div>`).join('') : '<p class="muted">هنوز رویدادی در این بازه ثبت نشده است.</p>'}<p class="minor">این مقادیر شمارش رویداد هستند، نه کاربران یکتا یا نرخ تبدیل.</p></section><section class="panel"><div class="panel-heading"><h2>نوبت پیگیری</h2><span class="badge">CRM</span></div>${data.tasks.length?data.tasks.map(v=>`<div class="row"><span>${esc(v.title)}<small class="minor"> · ${date(v.due_at)}</small></span>${button('customer-task','مشاهده',v.lead_id,'table-button')}</div>`).join(''):'<p class="muted">وظیفهٔ بازی برای پیگیری وجود ندارد.</p>'}</section></div>${notice(data.notice)}`;
    } else if (['customers','crm','assessments'].includes(section)) {
      const assessment = section === 'assessments';
      html = table(assessment?['شناسهٔ ارزیابی','وضعیت','مشتری مرتبط','زمان ثبت','اقدام']:['مشتری','شمارهٔ ماسک‌شده','مرحلهٔ پیگیری','برچسب‌ها','زمان ثبت','اقدام'],filtered(data.rows).map(row=>assessment ? [shortId(row.id),badge(row.current_step,row.archived),shortId(row.lead_id),date(row.created_at),button('detail','جزئیات',row.id,'table-button')] : [shortId(row.id),`<bdi>${esc(row.mobile)}</bdi>`,badge(row.crm?.stage || row.status,row.archived),esc(JSON.parse(row.crm?.tags||'[]').join('، ') || '—'),date(row.created_at),button('detail','مشاهدهٔ مشتری',row.id,'table-button')]));
      html += `<div class="pagination">${button('previous','صفحهٔ قبل')}<span class="minor">صفحهٔ ${number(page+1)} · حداکثر ۵۰ رکورد</span>${data.has_more?button('next','صفحهٔ بعد'):''}</div>`;
      if (!assessment && can('export')) html += `<div class="actions">${button('export','خروجی CSV بدون اطلاعات تماس')}</div>`;
      html += notice('این فهرست لیدهاست، نه حساب‌های ثبت‌نام‌شده یا خریداران. جست‌وجو روی صفحهٔ فعلی و بدون افشای شمارهٔ کامل انجام می‌شود.');
    } else if (['tests','prompts','plans','content'].includes(section)) {
      html = notice(data.notice);
      if (section === 'prompts') html += `<section class="panel"><div class="panel-heading"><h2>چرخهٔ امن پرامپت</h2><span class="badge">نسخه‌دار</span></div><p class="muted">پیش‌نویس ← آزمایش غیرشخصی ← تأیید انتشار. نسخه‌های منتشرشده تغییرناپذیرند و بازگردانی تاریخچه را پاک نمی‌کند.</p><details><summary>متغیرهای مجاز و schema ثابت موتور فعلی</summary>${json(data.variables)}${json(data.schema)}</details><details><summary>دستور فعلی پیش‌فرض</summary>${json(data.current_system)}</details></section>`;
      for (const doc of data.documents) html += `<article class="panel"><div class="panel-heading"><div><h2>${esc(doc.title)}</h2><bdi class="minor">${esc(doc.slug)}</bdi></div><span class="badge">${number(doc.versions.length)} نسخه</span></div>${doc.versions.map(v=>`<details><summary>نسخهٔ ${number(v.version)} · ${esc(statusNames[v.status])} ${doc.active_version===v.id?'· فعال':''}<span class="minor"> · ${esc(v.author)} · ${date(v.created_at)}</span></summary><p>${esc(v.change_note)}</p>${json(JSON.parse(v.body))}<div class="actions">${can('write')?button('duplicate','نسخهٔ جدید بر پایهٔ این نسخه',v.id):''}${section==='prompts' && can('publish') ? button('lab','آزمایش با fixture غیرشخصی',v.id) + (v.status==='draft'?button('publish','انتشار',v.id):button('rollback','فعال‌کردن این نسخه',v.id)):''}</div></details>`).join('')}</article>`;
      if (!data.documents.length) html += empty('هنوز نسخه‌ای ثبت نشده است','پیش‌نویس اول را با فیلدهای زیر بسازید؛ هیچ دادهٔ آماده یا اتصال ساختگی ایجاد نشده است.');
      if (can('write')) html += documentForm();
      if (section==='tests') html += `<section class="panel"><h2>سؤال‌های فعلی سایت · نسخهٔ ثابت</h2>${data.current_questions.map((q,index)=>`<details><summary>${number(index+1)}. ${esc(q.title)}</summary>${json(q)}</details>`).join('')}</section>`;
      if (section==='prompts' && data.runs.length) html += `<section class="panel"><h2>تاریخچهٔ آزمایش‌ها</h2>${data.runs.map(v=>`<details><summary>${date(v.created_at)} · ${esc(statusNames[v.status]||v.status)}</summary>${v.output_json?json(JSON.parse(v.output_json)):'خروجی معتبری ثبت نشده است.'}</details>`).join('')}</section>`;
    } else if (section==='audit') {
      html = table(['چه کسی','عملیات','موجودیت','زمان','قبل / بعد'], filtered(data.rows).map(v=>[esc(v.actor),esc(v.action),esc(v.entity_type)+' '+shortId(v.entity_id),date(v.created_at),`<details><summary>جزئیات غیرحساس</summary>${json({before:JSON.parse(v.before_summary),after:JSON.parse(v.after_summary),request_id:v.request_id})}</details>`]));
      html += notice('نمایش حداکثر ۵۰۰ رویداد در بازهٔ انتخابی. متن یادداشت‌ها و شمارهٔ کامل در حسابرسی ذخیره نمی‌شود.');
    } else if (section==='team') {
      html = notice(data.notice) + table(['نام','ایمیل','نقش','تغییر دسترسی'],filtered(data.rows).map(v=>[esc(v.name),`<bdi>${esc(v.email)}</bdi>`,esc(roleNames[v.role]||v.role),can('roles') && v.role!=='owner'?`<form class="role-form" data-staff="${v.id}"><label>نقش جدید<select name="role">${data.roles.filter(r=>r!=='owner').map(r=>`<option value="${r}" ${r===v.role?'selected':''}>${esc(roleNames[r])}</option>`).join('')}</select></label><button type="submit" class="table-button">ثبت نقش</button></form>`:'محافظت‌شده']));
      html += notice('ساخت حساب جدید همچنان از مسیر امن add-staff و راه‌اندازی TOTP انجام می‌شود؛ این پنل رمز یا کلید تأیید هویت را نمایش نمی‌دهد.');
    } else if (section==='settings') {
      html = `<div class="split"><section class="panel"><h2>اتصال‌های واقعی</h2>${Object.entries(data.connections).map(([key,value])=>`<div class="row"><bdi>${esc(key)}</bdi>${badge(value?'متصل':'هنوز متصل نشده')}</div>`).join('')}<p class="minor">«متصل» یعنی تنظیمات موجود است؛ خطای ارتباط جداگانه در عملیات نمایش داده می‌شود.</p></section><section class="panel"><h2>مراحل پیگیری</h2>${data.stages.map(v=>`<div class="row"><span>${esc(v.title)}</span><span>${number(v.position+1)}</span></div>`).join('')}<form id="stage-form" class="actions"><label>مرحلهٔ جدید<input name="title" maxlength="100" required></label><button>افزودن مرحله</button></form></section></div><section class="panel"><h2>ماتریس دسترسی سمت سرور</h2>${json(data.permissions)}</section>`;
    }
    $('content').innerHTML = html;
  }
  function documentForm() {
    const prompt = section === 'prompts';
    return `<section class="panel"><h2>ثبت پیش‌نویس جدید</h2><p class="muted">هر ذخیره یک نسخهٔ مستقل می‌سازد؛ نسخهٔ منتشرشده بازنویسی نمی‌شود.</p><form id="document-form" class="form-grid"><label>نام داخلی<input name="title" maxlength="200" required></label><label>نامک پایدار<input name="slug" dir="ltr" pattern="[a-z][a-z0-9-]*" value="${prompt?'brand-assessment':''}" maxlength="80" required></label><label class="wide">یادداشت تغییر<input name="change_note" maxlength="500"></label>${prompt ? '<label class="wide">دستور سیستم<textarea name="system_prompt" maxlength="16000" required></textarea></label><label class="wide">قالب پیام<textarea name="instruction_prompt" dir="ltr" required>{{assessment.answers}}</textarea></label><label class="wide">نمونه خروجی معتبر JSON<textarea name="sample_output" dir="ltr" required></textarea></label>' : '<label class="wide">ساختار نسخه (JSON)<textarea name="body" dir="ltr" rows="14" required></textarea></label>'}<div class="wide"><button>ذخیرهٔ پیش‌نویس</button></div></form><details><summary>راهنمای ساختار</summary>${json(prompt?{variables:viewData.variables,schema:viewData.schema}:section==='tests'?{description:'',questions:[{id:'question_key',title:'متن سؤال',type:'single',options:['گزینهٔ اول','گزینهٔ دوم']}]}:section==='plans'?{description:'',features:[],cta_path:'#/assessment',active:true}:{text:'',placement:'faq',cta_path:''})}</details></section>`;
  }
  function detail(row) {
    const assessment = section === 'assessments';
    let html = `<div class="actions">${button('back','بازگشت به فهرست')}</div><section class="panel"><div class="panel-heading"><h2>${assessment?'جزئیات ارزیابی':'پروندهٔ مشتری'}</h2>${shortId(row.id)}</div>`;
    if (assessment) {
      const snapshot = row.snapshot || {};
      html += `<dl class="detail-list"><dt>وضعیت پردازش</dt><dd>${badge(row.current_step)}</dd><dt>زمان ایجاد</dt><dd>${date(row.created_at)}</dd><dt>نسخهٔ پرامپت</dt><dd>${snapshot.prompt_version?shortId(snapshot.prompt_version):'تاریخی · نسخه ثبت نشده'}</dd></dl><details open><summary>پاسخ‌های ثبت‌شده</summary>${json(row.answers)}</details><details><summary>خروجی نهایی · بازیابی‌شده از گزارش فشرده</summary>${json(row.full_report)}</details><details><summary>Snapshot سؤال‌های همان زمان</summary>${snapshot.questions_json?json(JSON.parse(snapshot.questions_json)):'برای این رکورد تاریخی snapshot ثبت نشده؛ سؤال فعلی جایگزین تاریخچه نمی‌شود.'}</details>`;
      html += `<details><summary>تاریخچهٔ خروجی‌های نسخه‌دار</summary>${(row.results||[]).map(v=>`<details><summary>${date(v.created_at)} · ${v.prompt_version?shortId(v.prompt_version):'پرامپت پیش‌فرض'}</summary>${json(JSON.parse(v.report_json))}<details><summary>ورودی همان نسخه</summary>${json(JSON.parse(v.context_json||'{}'))}</details></details>`).join('')||'برای نتایج قبل از نصب این پنل، تاریخچهٔ نسخه‌دار موجود نیست.'}</details><p class="minor">فقط پاسخ‌های انتخابیِ ارسال‌شده ذخیره شده‌اند؛ متن‌های آزاد برای حفظ حریم خصوصی ارسال نمی‌شوند.</p>`;
      if(can('publish')) html += `<div class="actions">${button('regenerate','بازتولید و ذخیره به‌عنوان نسخهٔ جدید',row.id)}</div>`;
    } else {
      html += `<dl class="detail-list"><dt>شمارهٔ کامل · مشاهده لاگ شد</dt><dd><bdi>${esc(row.mobile)}</bdi></dd><dt>وضعیت</dt><dd>${badge(row.status)}</dd><dt>رضایت پیگیری</dt><dd>${row.consent_follow_up?'ثبت شده':'ثبت نشده'}</dd><dt>زمان عضویت لید</dt><dd>${date(row.created_at)}</dd></dl><p class="muted">نام، ایمیل، پروفایل حساب و تاریخچهٔ پیامک در دادهٔ فعلی وجود ندارد؛ چیزی جایگزین یا حدس زده نشده است.</p></section><section class="panel"><h2>ارزیابی‌های مشتری</h2>${table(['ارزیابی','وضعیت','تاریخ'],row.assessments.map(v=>[shortId(v.id),badge(v.current_step),date(v.created_at)]))}`;
      if (can('write')) html += `</section><section class="panel"><h2>پیگیری و دسته‌بندی</h2><form id="crm-form" class="form-grid"><label>مرحلهٔ CRM<select name="stage_id">${bootstrap.stages.map(v=>`<option value="${v.id}" ${v.id===row.crm.stage_id?'selected':''}>${esc(v.title)}</option>`).join('')}</select></label><label>برچسب‌ها (با ویرگول جدا کنید)<input name="tags" maxlength="800" value="${esc(JSON.parse(row.crm.tags||'[]').join('، '))}"></label><label>مسئول پیگیری<select name="owner_id"><option value="">تعیین نشده</option>${bootstrap.assignees.map(v=>`<option value="${v.id}" ${v.id===row.crm.owner_id?'selected':''}>${esc(v.name)}</option>`).join('')}</select></label><button>ثبت تغییرات CRM</button></form></section><section class="panel"><h2>یادداشت‌های پیگیری</h2>${row.notes.map(v=>`<div class="row"><div><p>${esc(v.body)}</p><span class="minor">${esc(v.author)} · ${date(v.created_at)}</span></div></div>`).join('') || '<p class="muted">یادداشتی ثبت نشده است.</p>'}<form id="note-form" class="actions"><label class="search-label">یادداشت جدید<textarea name="body" maxlength="3000" required></textarea></label><button>ثبت یادداشت</button></form></section><section class="panel"><h2>وظایف پیگیری</h2>${row.tasks.map(v=>`<div class="row"><span>${esc(v.title)} · ${date(v.due_at)}</span>${v.done?badge('انجام شده'):button('task-done','انجام شد',v.id,'table-button')}</div>`).join('')}<form id="task-form" class="form-grid"><label>عنوان وظیفه<input name="title" maxlength="200" required></label><label>موعد<input name="due" type="datetime-local" required></label><label>مسئول<select name="owner_id"><option value="">تعیین نشده</option>${bootstrap.assignees.map(v=>`<option value="${v.id}">${esc(v.name)}</option>`).join('')}</select></label><button>افزودن وظیفه</button></form>`;
    }
    html += '</section>';
    if (can('archive')) html += `<div class="actions">${button('archive','آرشیو رکورد',row.id,'danger')}</div>`;
    if (!assessment && can('roles')) html += `<div class="actions">${button('privacy','ثبت درخواست ناشناس‌سازی',row.id)}</div>`;
    $('content').innerHTML = html;
  }
  async function confirmAction(copy) {
    $('confirmation-copy').textContent = copy;
    $('confirm-check').checked = false;
    $('confirm-yes').disabled = true;
    $('confirmation').showModal();
    return new Promise(resolve => {
      const dialog = $('confirmation');
      dialog.addEventListener('close', () => resolve(dialog.returnValue === 'yes'), {once:true});
    });
  }
  $('confirm-check').addEventListener('change', () => {$('confirm-yes').disabled = !$('confirm-check').checked;});
  $('confirm-yes').addEventListener('click', () => $('confirmation').close('yes'));
  $('confirm-no').addEventListener('click', () => $('confirmation').close('no'));
  $('confirmation').addEventListener('cancel', () => {$('confirmation').returnValue = 'no';});
  async function load() {
    const request = ++sequence;
    $('content').setAttribute('aria-busy','true');
    $('feedback').textContent = 'در حال دریافت دادهٔ واقعی…';
    $('refresh').disabled = true;
    try {
      const params = new URLSearchParams({section,days:$('period').value,page:String(page),...(identity?{id:identity}:{}),from:$('date-from').value,to:$('date-to').value});
      const data = await api('/api/admin/workspace?' + params);
      if (request !== sequence) return;
      viewData = data;paint();$('feedback').textContent = '';
    } catch (error) {if (request === sequence) {$('content').innerHTML = empty('دریافت اطلاعات انجام نشد',error.message);$('feedback').textContent = error.message;}}
    finally {if (request === sequence) {$('content').setAttribute('aria-busy','false');$('refresh').disabled = false;}}
  }
  function selectSection(next) {
    section = next;identity = '';page = 0;viewData = null;$('search').value = '';
    history.replaceState(null,'','/admin/'+section);
    $('page-title').textContent = bootstrap.modules[section];
    $('breadcrumb').textContent = 'مدیریت / ' + bootstrap.modules[section];
    document.querySelectorAll('#navigation a').forEach(a=>{a.classList.toggle('active',a.dataset.section===section);if(a.dataset.section===section)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
    document.body.classList.remove('menu-open');$('menu-toggle').setAttribute('aria-expanded','false');
    load();
  }
  async function save(body, refresh=true) {
    const result = await api('/api/admin/workspace', {section,csrf:bootstrap.csrf,...body});
    if (refresh) await load();
    $('feedback').textContent = 'عملیات با موفقیت ثبت شد.';
    return result;
  }
  document.addEventListener('click', async event => {
    const nav = event.target.closest('[data-section]');
    if (nav) {event.preventDefault();selectSection(nav.dataset.section);return;}
    const target = event.target.closest('[data-action]');
    if (!target) return;
    const action = target.dataset.action, id = target.dataset.id;
    target.disabled = true;
    try {
      if (action==='detail') {if(!await confirmAction(section==='assessments'?'پاسخ‌ها و گزارش این ارزیابی نمایش داده و مشاهده در حسابرسی ثبت می‌شود.':'شمارهٔ کامل و پروندهٔ مشتری نمایش داده و مشاهده در حسابرسی ثبت می‌شود.'))return;identity=id;await load();return;}
      if (action==='customer-task') {if(!await confirmAction('پروندهٔ کامل مشتری باز می‌شود و مشاهدهٔ آن در حسابرسی ثبت می‌شود.'))return;selectSection('crm');identity=id;await load();return;}
      if (action==='back') {identity='';await load();return;}
      if (action==='next' || action==='previous') {page=Math.max(0,page+(action==='next'?1:-1));await load();return;}
      if (action==='duplicate') {
        const doc = viewData.documents.find(d=>d.versions.some(v=>v.id===id));
        const v = doc.versions.find(v=>v.id===id), body = JSON.parse(v.body), form=$('document-form');
        form.elements.title.value=doc.title;form.elements.slug.value=doc.slug;
        if(section==='prompts') {form.elements.system_prompt.value=body.system_prompt;form.elements.instruction_prompt.value=body.instruction_prompt;form.elements.sample_output.value=JSON.stringify(body.sample_output,null,2);}
        else form.elements.body.value=JSON.stringify(body,null,2);
        form.scrollIntoView({block:'center',behavior:'smooth'});form.elements.title.focus();return;
      }
      if(action==='task-done') {await save({action:'task_done',id:identity,task_id:id});return;}
      const effects={regenerate:'این عملیات از هوش مصنوعی واقعی استفاده می‌کند و ممکن است هزینه داشته باشد. خروجی قبلی حفظ و نتیجهٔ جدید به تاریخچه اضافه می‌شود.',archive:'این رکورد در پنل آرشیو می‌شود؛ دادهٔ اصلی و پاسخ‌ها حذف نمی‌شوند.',publish:'این پرامپت پس از انتشار در ارزیابی‌های جدید استفاده می‌شود. نتایج قبلی تغییر نمی‌کنند.',rollback:'نسخهٔ انتخاب‌شده برای ارزیابی‌های جدید فعال می‌شود؛ تاریخچه حذف نمی‌شود.',lab:'این آزمایش با دادهٔ غیرشخصی از سرویس واقعی هوش مصنوعی استفاده می‌کند و ممکن است هزینه داشته باشد. گزارش کاربران تغییر نمی‌کند.',export:'حداکثر ۵۰۰ رکورد بدون شماره یا اطلاعات تماس صادر و این عملیات ثبت می‌شود.',privacy:'درخواست ناشناس‌سازی برای بررسی مالک ثبت می‌شود؛ هیچ داده‌ای خودکار حذف نمی‌شود.'};
      if (!effects[action] || !await confirmAction(effects[action])) return;
      const result = await save({action,id,confirmed:true,...(action==='privacy'?{kind:'anonymize'}:{})},!['lab','export'].includes(action));
      if(action==='lab') {$('content').insertAdjacentHTML('afterbegin',`<section class="panel"><h2>نتیجهٔ آزمایش · JSON معتبر</h2><details><summary>ورودی نهایی غیرشخصی</summary>${json(result.input)}</details>${json(result.output)}</section>`);}
      if(action==='export') {const blob=new Blob(['\ufeff'+result.csv],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='nesharo-leads.csv';a.click();URL.revokeObjectURL(url);}
    } catch(error) {$('feedback').textContent=error.message;}
    finally {target.disabled=false;}
  });
  document.addEventListener('submit',async event=>{
    if(!event.target.closest('#content'))return;
    event.preventDefault();const form=event.target,button=form.querySelector('button');button.disabled=true;
    try {
      const values=Object.fromEntries(new FormData(form));
      if(form.id==='document-form') {
        const body=section==='prompts'?{system_prompt:values.system_prompt,instruction_prompt:values.instruction_prompt,output_schema:viewData.schema,sample_output:JSON.parse(values.sample_output)}:JSON.parse(values.body);
        await save({action:'draft',...values,body});
      } else if(form.id==='crm-form') await save({action:'crm',id:identity,...values,tags:values.tags.split(/[,،]/).map(v=>v.trim()).filter(Boolean),owner_id:values.owner_id?Number(values.owner_id):null});
      else if(form.id==='note-form') await save({action:'note',id:identity,...values});
      else if(form.id==='task-form') await save({action:'task',id:identity,title:values.title,owner_id:values.owner_id?Number(values.owner_id):null,due_at:Math.floor(new Date(values.due).getTime()/1000)});
      else if(form.id==='stage-form') await save({action:'stage',...values});
      else if(form.classList.contains('role-form') && await confirmAction('نقش این عضو تغییر می‌کند و نشست‌های فعال او پایان می‌یابد.')) await save({action:'role',staff_id:Number(form.dataset.staff),role:values.role,confirmed:true});
    } catch(error) {$('feedback').textContent=error instanceof SyntaxError?'ساختار JSON معتبر نیست؛ متن را بررسی کنید.':error.message;}
    finally {button.disabled=false;}
  });
  $('menu-toggle').addEventListener('click',()=>{const open=document.body.classList.toggle('menu-open');$('menu-toggle').setAttribute('aria-expanded',String(open));});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'){document.body.classList.remove('menu-open');$('menu-toggle').setAttribute('aria-expanded','false');}});
  $('refresh').addEventListener('click',load);
  $('period').addEventListener('change',()=>{const custom=$('period').value==='custom';$('from-label').hidden=!custom;$('to-label').hidden=!custom;page=0;if(!custom)load();});
  for(const id of ['date-from','date-to']) $(id).addEventListener('change',()=>{if($('date-from').value && $('date-to').value){page=0;load();}});
  $('search').addEventListener('input',paint);
  $('logout').addEventListener('click',async()=>{try{await api('/api/admin/logout',{csrf:bootstrap.csrf});location.assign('/admin/login');}catch(error){$('feedback').textContent=error.message;}});
  (async()=>{
    try {
      bootstrap=await api('/api/admin/workspace?section=bootstrap');
      const modules=Object.entries(bootstrap.modules);
      $('principal').textContent=bootstrap.principal.name+' · '+(roleNames[bootstrap.principal.role]||bootstrap.principal.role);
      $('navigation').innerHTML=modules.map(([key,title],index)=>`<a href="/admin/${key}" data-section="${key}"><span class="nav-icon" aria-hidden="true">${icons[index%icons.length]}</span>${esc(title)}</a>`).join('')+(can('assessments')?'<a href="/admin/personal-brand">ارزیابی ساختاریافتهٔ پرسونال برند</a>':'')+(bootstrap.principal.role==='owner'?'<a href="/admin/consultations"><span class="nav-icon" aria-hidden="true">◴</span>مدیریت مشاوره‌ها</a>':'');
      if(!bootstrap.modules[section])section=modules[0]?.[0];
      if(!section){$('content').innerHTML=empty('دسترسی پنل جدید برای این نقش فعال نیست','مالک می‌تواند نقش مناسب پنل جدید را برای شما تعیین کند.');return;}
      selectSection(section);
    } catch(error){$('feedback').textContent=error.message;}
  })();
})();
