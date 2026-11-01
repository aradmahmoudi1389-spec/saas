'use strict';
const AccountCenter = (() => {
  const root = document.querySelector('#account-root');
  const pages = {overview:'نمای کلی حساب',information:'اطلاعات حساب',products:'دسترسی‌ها و محصولات',security:'امنیت حساب'};
  const state = {data:null,draft:null,page:'overview',loading:true,error:'',saving:false,avatarReading:false,menu:false};
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const paths = {
    account:'M20 21v-2a7 7 0 0 0-14 0v2 M16 7a4 4 0 1 1-8 0a4 4 0 0 1 8 0',
    overview:'M3 10 12 3l9 7 M5 9v12h14V9 M9 21v-8h6v8',
    information:'M5 4h14v17H5z M9 8h6 M9 12h6 M9 16h4',
    products:'M4 4h6v6H4z M14 4h6v6h-6z M4 14h6v6H4z M14 14h6v6h-6z',
    security:'M12 3 4 6v6c0 5 8 9 8 9s8-4 8-9V6z M8 12l3 3 5-6',
    exit:'M9 4H4v16h5 M10 12h11 M17 8l4 4-4 4',
    back:'M21 12H3 M8 7l-5 5 5 5',
    menu:'M4 6h16 M4 12h16 M4 18h16',
    close:'M6 6l12 12 M18 6 6 18',
    edit:'M14 4l6 6 M4 20l5-1L21 7l-6-6L3 13z',
    sun:'M12 3v2 M12 19v2 M3 12h2 M19 12h2 M5 5l2 2 M17 17l2 2 M19 5l-2 2 M7 17l-2 2 M16 12a4 4 0 1 1-8 0a4 4 0 0 1 8 0'
  };
  const icon = name => `<svg class="icon" aria-hidden="true" viewBox="0 0 24 24"><path d="${paths[name] || paths.account}"></path></svg>`;
  const account = () => state.data?.account || {};
  const displayName = value => value?.name?.trim() || 'نام حساب ثبت نشده';
  const initials = name => (name || '').trim().split(/\s+/u).filter(Boolean).slice(0,2).map(word => Array.from(word)[0]).join(' ') || '—';
  const avatar = (value, large=false) => value?.avatar ? `<img class="avatar ${large?'avatar-large':''}" src="${esc(value.avatar)}" alt="تصویر حساب">` : `<span class="avatar ${large?'avatar-large':''}" role="img" aria-label="${value?.name?'حروف نام '+esc(value.name):'حساب بدون تصویر'}">${esc(initials(value?.name))}</span>`;
  const completion = value => ({percent:value?.name?.trim()?100:0,missing:value?.name?.trim()?[]:['نام نمایشی']});
  const canonical = value => ({name:String(value?.name||'').trim(),email:String(value?.email||'').trim(),phone:String(value?.phone||'').trim(),avatar:value?.avatar||''});
  const dirty = () => Boolean(state.draft && JSON.stringify(canonical(state.draft)) !== JSON.stringify(canonical(account())));
  const routeKey = hash => Object.hasOwn(pages,hash.slice(1)) ? hash.slice(1) : 'overview';
  const empty = (title,text,action='') => `<section class="card empty-account" id="account-main"><div class="card-icon">${icon('account')}</div><h1 tabindex="-1" data-page-heading>${title}</h1><p>${text}</p>${action}</section>`;
  const action = (href,label,secondary=false) => `<a class="button ${secondary?'secondary':''}" href="${href}" data-account-link>${label}</a>`;
  function accessInfo(data) {
    if (!data?.testCompleted) return {testOnly:true,label:'تست هنوز کامل نشده',href:'/personal-brand',action:'ادامهٔ تست'};
    switch (data.access?.status) {
      case 'active': return {label:'دسترسی فعال',href:'/brandyar/dashboard',action:'ورود به برندیـار'};
      case 'trial': return {label:'دسترسی آزمایشی',href:'/brandyar/dashboard',action:'ورود به برندیـار'};
      case 'expired': return {label:'دسترسی پایان‌یافته',href:'/brandyar/plans',action:'بررسی دوبارهٔ دسترسی'};
      case 'suspended': return {label:'دسترسی غیرفعال',href:'/brandyar/activate',action:'بررسی وضعیت دسترسی'};
      default: return {label:'بدون دسترسی فعال',href:'/brandyar/plans',action:'بررسی دسترسی'};
    }
  }
  function productCard() {
    const access = accessInfo(state.data);
    if (access.testOnly) return `<article class="card"><div class="card-icon">${icon('information')}</div><h2>ادامهٔ مسیر شما</h2><p>تست هنوز کامل نشده است. از همان مسیر، پاسخ‌ها را ادامه دهید و نتیجه را ببینید.</p>${action(access.href,access.action)}</article>`;
    return `<article class="card product-card"><div class="product-head"><img src="/logo.jpg" alt="لوگوی برندیـار"><div><h2>برندیـار</h2><small>محصول مستقل</small></div></div><p>فضای کاری ساخت هویت حرفه‌ای و محتوای هماهنگ با برند</p><span class="badge">${esc(access.label)}</span>${state.data.access?.status==='trial'?'<p class="help">این دسترسی آزمایشی است و اشتراک پرداخت‌شده محسوب نمی‌شود.</p>':''}${state.data.access?.status==='suspended'?'<p class="help">فعال‌سازی این دسترسی نیازمند بررسی است.</p>':''}${action(access.href,access.action)}</article>`;
  }
  function securityLines() {
    return `<div class="security-lines"><div class="security-line"><span>وضعیت ورود</span><strong>نشست جاری معتبر است</strong></div><div class="security-line"><span>اطلاعات تماس</span><strong>تأیید مالکیت انجام نشده</strong></div></div>`;
  }
  function overview() {
    const a = account(), progress = completion(a);
    return `<div class="account-grid"><section class="card identity-card"><div class="identity-summary">${avatar(a,true)}<div><h2>${esc(displayName(a))}</h2>${a.email?`<span class="identity-email">${esc(a.email)}</span>`:'<span class="help">ایمیلی ثبت نشده است.</span>'}</div></div><span class="badge"><span class="badge-dot"></span>وارد حساب شده‌اید</span></section>${progress.missing.length?`<section class="card completion-card"><div class="completion-heading"><h2>معرفی حساب را تکمیل کنید</h2><span class="badge">${progress.percent.toLocaleString('fa-IR')}٪</span></div><progress max="100" value="${progress.percent}" aria-label="تکمیل اطلاعات پایهٔ حساب"></progress><div class="completion-bottom"><p>اطلاعات باقی‌مانده: ${progress.missing.join('، ')}. افزودن تصویر و اطلاعات تماس اختیاری است.</p>${action('#information','تکمیل اطلاعات')}</div></section>`:''}${productCard()}<article class="card"><div class="card-icon">${icon('security')}</div><h2>امنیت حساب</h2><p>وضعیت ورود و اطلاعات مربوط به نشست جاری را بررسی کنید.</p>${securityLines()}${action('#security','بررسی امنیت حساب',true)}</article></div>`;
  }
  function information() {
    state.draft ||= {...canonical(account())};
    const d = state.draft;
    return `<form id="account-form" class="card account-form" novalidate><fieldset class="form-fields"><legend class="visually-hidden">اطلاعات حساب</legend><section class="form-section"><h2>تصویر حساب</h2><p class="help">تصویر اختیاری است؛ بدون تصویر، حروف نام شما نمایش داده می‌شود.</p><div class="avatar-editor"><div data-avatar-preview>${avatar(d,true)}</div><div class="field"><label for="avatar-file">انتخاب تصویر <small>اختیاری</small></label><input id="avatar-file" type="file" accept="image/png,image/jpeg" aria-describedby="avatar-help error-avatar"><span class="help" id="avatar-help">PNG یا JPEG، حداکثر ۱۰ کیلوبایت.</span><span class="field-error" id="error-avatar" role="alert"></span><div class="avatar-actions"><button class="button secondary" type="button" data-remove-avatar ${d.avatar?'':'hidden'}>حذف تصویر</button></div></div></div></section><section class="form-section"><h2>اطلاعات پایه</h2><div class="form-grid">${field('name','نام نمایشی',d.name,'text','این نام در مرکز حساب نمایش داده می‌شود.',true)}${field('email','ایمیل',d.email,'email','اختیاری؛ ثبت یا تغییر ایمیل، تأیید مالکیت آن نیست.')}${field('phone','شمارهٔ موبایل',d.phone,'tel','اختیاری؛ شماره فقط به‌عنوان اطلاعات حساب ثبت می‌شود.')}</div></section></fieldset><div class="form-footer"><button class="button" type="submit" data-save ${dirty()?'':'disabled'}>ثبت تغییرات</button><button class="button secondary" type="button" data-discard ${dirty()?'':'hidden'}>لغو تغییرات</button><span class="unsaved-label" data-dirty-label>${dirty()?'تغییرات ثبت‌نشده دارید.':'تغییری برای ثبت وجود ندارد.'}</span></div><p class="save-message" id="save-message" role="status" aria-live="polite"></p></form>`;
  }
  function field(name,label,value,type,help,required=false) {
    return `<div class="field"><label for="account-${name}">${label} <small>${required?'الزامی':'اختیاری'}</small></label><input id="account-${name}" name="${name}" type="${type}" value="${esc(value)}" ${required?'required':''} ${name==='name'?'maxlength="100" autocomplete="name"':name==='email'?'dir="ltr" maxlength="200" autocomplete="email"':'dir="ltr" maxlength="32" autocomplete="tel" inputmode="tel"'} aria-describedby="help-${name} error-${name}"><span class="help" id="help-${name}">${help}</span><span class="field-error" id="error-${name}" role="alert"></span></div>`;
  }
  function security() {
    return `<section class="card security-page"><div class="card-icon">${icon('security')}</div><h2>نشست جاری حساب</h2><p>این حساب از نشست امن مسیر تست استفاده می‌کند. خروج، همین نشست را پایان می‌دهد.</p>${securityLines()}<p class="help">تغییر رمز، تأیید ایمیل و مدیریت چند نشست در این نسخه ارائه نشده‌اند.</p><button class="logout-button" data-logout>${icon('exit')}خروج از حساب</button></section>`;
  }
  function render(focus=false) {
    root.setAttribute('aria-busy',String(state.loading));
    if (state.loading) return;
    if (state.error) {root.innerHTML=empty('بازیابی حساب انجام نشد',esc(state.error),'<button class="button" data-retry>تلاش دوباره</button>');bind();return;}
    if (!state.data?.signedIn) {root.innerHTML=empty('نشست حساب پایان یافته است','برای دسترسی به حساب، از مسیر معتبر ورود یا ادامهٔ تست اقدام کنید.',action('/personal-brand','ورود از مسیر تست'));bind();return;}
    const content = state.page==='overview'?overview():state.page==='information'?information():state.page==='products'?`<div class="account-grid">${productCard()}</div>`:security();
    root.innerHTML=`<div class="account-layout"><button class="menu-backdrop" data-close-menu aria-label="بستن منوی حساب" tabindex="-1"></button><aside class="account-sidebar" id="account-sidebar" aria-label="ناوبری حساب"><div class="account-wordmark">${icon('account')}مرکز حساب<button class="icon-button mobile-close" data-close-menu aria-label="بستن منو">${icon('close')}</button></div><div class="sidebar-person">${avatar(account())}<div class="person-copy"><strong>${esc(displayName(account()))}</strong><small>حساب کاربری</small></div></div><div><p class="nav-heading">مدیریت حساب</p><nav class="account-nav" aria-label="بخش‌های حساب">${Object.entries(pages).slice(0,2).map(([key,label])=>navItem(key,label)).join('')}</nav></div><div><p class="nav-heading">دسترسی و حفاظت</p><nav class="account-nav" aria-label="دسترسی و امنیت">${Object.entries(pages).slice(2).map(([key,label])=>navItem(key,label)).join('')}</nav></div><div class="sidebar-footer"><a href="/" data-account-link>${icon('back')}بازگشت به سایت</a><button class="logout-button" data-logout>${icon('exit')}خروج از حساب</button><p class="field-error" data-logout-message role="alert"></p></div></aside><main class="account-main" id="account-main"><header class="account-topbar"><div><p>فضای شخصی شما</p><strong>مرکز حساب کاربری</strong></div><div class="topbar-tools"><a class="help" href="/" data-account-link>بازگشت به سایت</a><button class="icon-button" data-theme-toggle aria-label="تغییر حالت روشن و تیره">${icon('sun')}</button><button class="icon-button mobile-toggle" data-open-menu aria-controls="account-sidebar" aria-expanded="false" aria-label="باز کردن منوی حساب">${icon('menu')}</button></div></header><div class="page-heading"><div><h1 tabindex="-1" data-page-heading>${pages[state.page]}</h1><p>${{overview:'اطلاعات پایه، وضعیت ورود و دسترسی‌های خود را در یک نگاه مدیریت کنید.',information:'اطلاعات پایهٔ حساب خود را ویرایش کنید؛ اطلاعات حرفه‌ای در محصول برندیـار باقی می‌ماند.',products:'وضعیت دسترسی و مسیر ورود به محصولات را بررسی کنید.',security:'وضعیت واقعی نشست جاری و اقدام‌های موجود حساب.'}[state.page]}</p></div>${state.page==='overview'?action('#information',icon('edit')+'ویرایش اطلاعات',true):''}</div>${content}</main></div>`;
    document.title=pages[state.page]+' | مرکز حساب کاربری';
    document.body.classList.remove('menu-open');state.menu=false;
    bind();if(focus)root.querySelector('[data-page-heading]')?.focus();
  }
  const navItem = (key,label) => `<a href="#${key}" data-account-link ${state.page===key?'aria-current="page"':''}>${icon(key)}${label}</a>`;
  function validation(value) {
    const errors={};
    if(!value.name.trim())errors.name='نام نمایشی را وارد کنید.';
    if(value.name.length>100)errors.name='نام نمایشی باید حداکثر ۱۰۰ نویسه باشد.';
    if(value.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/u.test(value.email))errors.email='ایمیل معتبر وارد کنید.';
    if(value.phone && !/^[+\d۰-۹٠-٩ ()-]{5,32}$/u.test(value.phone))errors.phone='شمارهٔ موبایل معتبر وارد کنید.';
    return errors;
  }
  async function request(body) {
    const response=await fetch('/api/account',{credentials:'same-origin',cache:'no-store',...(body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...body,csrf:state.data?.csrf})}:{})});
    if(response.status===401){state.data=null;state.draft=null;render();throw new Error('نشست پایان یافته است. دوباره وارد شوید.');}
    const payload=await response.json();
    if(!response.ok||payload.ok!==true||!payload.data){const error=new Error(payload.error||'درخواست حساب انجام نشد.');error.status=response.status;throw error;}
    return payload.data;
  }
  async function load() {
    state.loading=true;state.error='';root.setAttribute('aria-busy','true');
    root.innerHTML='<div class="account-loading" id="account-main" role="status">در حال بازیابی حساب…<div class="skeleton skeleton-title" aria-hidden="true"></div><div class="skeleton-grid" aria-hidden="true"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div></div>';
    try{state.data=await request();state.draft=null;state.page=routeKey(location.hash);}
    catch{state.data=null;state.error='ارتباط برقرار نشد؛ دوباره تلاش کنید. در صورت پایان نشست، از مسیر تست وارد شوید.';}
    finally{state.loading=false;render();}
  }
  const mayLeave = () => !state.saving&&!state.avatarReading&&(!dirty()||window.confirm('تغییرات هنوز ثبت نشده‌اند. بدون ثبت از این صفحه خارج می‌شوید؟'));
  function navigate(hash) {
    if(!mayLeave())return false;
    state.draft=null;state.page=routeKey(hash);history.replaceState(null,'',location.pathname+hash);render(true);return true;
  }
  function updateDirty() {
    const save=root.querySelector('[data-save]');if(save)save.disabled=!dirty()||state.saving||state.avatarReading;
    const discard=root.querySelector('[data-discard]');if(discard){discard.hidden=!dirty();discard.disabled=state.saving||state.avatarReading;}
    const remove=root.querySelector('[data-remove-avatar]');if(remove)remove.disabled=state.saving||state.avatarReading;
    const file=root.querySelector('#avatar-file');if(file)file.disabled=state.saving||state.avatarReading;
    const label=root.querySelector('[data-dirty-label]');if(label)label.textContent=state.avatarReading?'در حال خواندن تصویر…':dirty()?'تغییرات ثبت‌نشده دارید.':'تغییری برای ثبت وجود ندارد.';
  }
  function showErrors(errors) {
    for(const name of ['name','email','phone','avatar']){const target=root.querySelector('#error-'+name);if(target)target.textContent=errors[name]||'';root.querySelector('#account-'+name)?.setAttribute('aria-invalid',String(Boolean(errors[name])));}
  }
  async function save(event) {
    event.preventDefault();if(!dirty()||state.saving||state.avatarReading)return;
    const values=canonical(state.draft),errors=validation(values);showErrors(errors);
    if(Object.keys(errors).length){root.querySelector('#account-'+Object.keys(errors)[0])?.focus();return;}
    const message=root.querySelector('#save-message'),form=event.target;
    state.saving=true;form.querySelector('fieldset').disabled=true;updateDirty();
    message.className='save-message';message.textContent='در حال ثبت تغییرات…';root.querySelector('[data-save]').textContent='در حال ثبت…';
    try{
      const result=await request({action:'account_save',account:values});
      if(!result.account||typeof result.account!=='object')throw new Error('پاسخ معتبر ثبت حساب دریافت نشد.');
      state.data.account=result.account;state.draft={...canonical(result.account)};state.saving=false;render();
      const note=root.querySelector('#save-message');if(note){note.className='save-message success';note.textContent='تغییرات حساب ثبت شد.';}
    }catch(error){
      if(!state.data?.signedIn)return;
      message.className='save-message error';message.textContent='تغییرات هنوز ثبت نشده‌اند. '+(error.status?error.message:'ارتباط برقرار نشد؛ دوباره تلاش کنید.');
      if(error.message.includes('ایمیل'))showErrors({email:error.message});
    }finally{state.saving=false;const fields=root.querySelector('fieldset');if(fields)fields.disabled=false;const button=root.querySelector('[data-save]');if(button)button.textContent='ثبت تغییرات';updateDirty();}
  }
  async function logout() {
    if(!mayLeave())return;
    root.querySelectorAll('[data-logout]').forEach(button=>button.disabled=true);
    try{const result=await request({action:'account_logout'});if(result.signedIn!==false)throw new Error('خروج تأیید نشد.');state.data=null;state.draft=null;location.assign('/');}
    catch(error){if(!state.data?.signedIn)return;root.querySelectorAll('[data-logout]').forEach(button=>button.disabled=false);const message=root.querySelector('[data-logout-message]');if(message)message.textContent='خروج انجام نشد؛ دوباره تلاش کنید.';}
  }
  function toggleMenu(open) {
    state.menu=open;document.body.classList.toggle('menu-open',open);
    root.querySelector('[data-open-menu]')?.setAttribute('aria-expanded',String(open));
    const main=root.querySelector('#account-main');if(main)main.inert=open;
    if(open)root.querySelector('.mobile-close')?.focus();else root.querySelector('[data-open-menu]')?.focus();
  }
  function bind() {
    root.querySelectorAll('[data-retry]').forEach(button=>button.addEventListener('click',load));
    root.querySelectorAll('[data-account-link]').forEach(link=>link.addEventListener('click',event=>{const href=link.getAttribute('href');if(href.startsWith('#')){event.preventDefault();navigate(href);}else if(!mayLeave())event.preventDefault();}));
    root.querySelectorAll('[data-logout]').forEach(button=>button.addEventListener('click',logout));
    root.querySelector('[data-theme-toggle]')?.addEventListener('click',()=>{document.documentElement.dataset.theme=document.documentElement.dataset.theme==='dark'?'light':'dark';});
    root.querySelector('[data-open-menu]')?.addEventListener('click',()=>toggleMenu(true));
    root.querySelectorAll('[data-close-menu]').forEach(button=>button.addEventListener('click',()=>toggleMenu(false)));
    root.querySelector('#account-form')?.addEventListener('submit',save);
    for(const name of ['name','email','phone'])root.querySelector('#account-'+name)?.addEventListener('input',event=>{state.draft[name]=event.target.value;const message=root.querySelector('#save-message');if(message)message.textContent='';root.querySelector('#error-'+name).textContent='';event.target.setAttribute('aria-invalid','false');updateDirty();});
    root.querySelector('[data-discard]')?.addEventListener('click',()=>{if(!mayLeave())return;state.draft=null;render();});
    root.querySelector('[data-remove-avatar]')?.addEventListener('click',()=>{state.draft.avatar='';render();});
    root.querySelector('#avatar-file')?.addEventListener('change',event=>{
      const file=event.target.files[0];if(!file)return;
      const error=root.querySelector('#error-avatar');error.textContent='';
      if(!['image/png','image/jpeg'].includes(file.type)||file.size>10240){error.textContent='تصویر PNG یا JPEG تا ۱۰ کیلوبایت انتخاب کنید.';event.target.value='';return;}
      state.avatarReading=true;updateDirty();const reader=new FileReader();
      reader.onload=()=>{state.avatarReading=false;if(state.draft){state.draft.avatar=reader.result;root.querySelector('[data-avatar-preview]').innerHTML=avatar(state.draft,true);root.querySelector('[data-remove-avatar]').hidden=false;}updateDirty();};
      reader.onerror=()=>{state.avatarReading=false;error.textContent='خواندن تصویر انجام نشد؛ دوباره انتخاب کنید.';updateDirty();};reader.readAsDataURL(file);
    });
  }
  window.addEventListener('resize',()=>{if(state.menu&&window.innerWidth>900)toggleMenu(false);});
  window.addEventListener('beforeunload',event=>{if(dirty()||state.saving||state.avatarReading){event.preventDefault();event.returnValue='';}});
  window.addEventListener('hashchange',()=>{const previous='#'+state.page;if(!navigate(location.hash))history.replaceState(null,'',location.pathname+previous);});
  document.addEventListener('keydown',event=>{
    if(!state.menu)return;
    if(event.key==='Escape'){event.preventDefault();toggleMenu(false);}
    if(event.key==='Tab'){
      const items=Array.from(root.querySelectorAll('.account-sidebar a,.account-sidebar button:not(:disabled)')).filter(item=>!item.hidden);
      const first=items[0],last=items[items.length-1];
      if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
    }
  });
  try{document.documentElement.dataset.theme=localStorage.getItem('brandyar-theme')||'light';}catch{}
  load();
  return {state,completion,initials,accessInfo,validation,dirty,navigate,load,save,logout};
})();
