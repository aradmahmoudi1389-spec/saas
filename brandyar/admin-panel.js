let csrf = '';
let timeZone = 'Asia/Tehran';
let pending = false;
const feedback = document.getElementById('feedback');
const say = (text, error = false) => { feedback.textContent = text; feedback.className = error ? 'error' : ''; };
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const number = value => new Intl.NumberFormat('fa-IR').format(value);
const labels = {open:'باز', blocked:'مسدود', requested:'درخواست‌شده', confirmed:'تأییدشده', pending:'در انتظار تأیید', cancelled:'لغوشده', completed:'انجام‌شده'};
const fmt = stamp => new Intl.DateTimeFormat('fa-IR-u-ca-persian', {dateStyle:'medium', timeStyle:'short', timeZone}).format(new Date(stamp * 1000));
async function api(path, body) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(path, {credentials:'same-origin', cache:'no-store', signal:controller.signal, ...(body ? {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({...body, csrf})} : {})});
    const data = await response.json();
    if (response.status === 401) throw Error('نشست مدیریت پایان یافته است. دوباره از صفحهٔ ورود وارد شوید.');
    if (response.status === 403) throw Error('دسترسی به این بخش مجاز نیست یا نشست معتبر نیست.');
    if (!response.ok) throw Error(data.error || 'عملیات انجام نشد.');
    return data;
  } catch (error) {
    if (['TypeError','SyntaxError','AbortError'].includes(error.name)) throw Error('پاسخ سرور دریافت نشد. پیش از تکرار عملیات، فهرست‌ها را به‌روزرسانی کنید.');
    throw error;
  } finally {
    clearTimeout(timer);
  }
}
function fillDates() {
  const dateFormat = new Intl.DateTimeFormat('en-CA', {year:'numeric', month:'2-digit', day:'2-digit', timeZone});
  const faFormat = new Intl.DateTimeFormat('fa-IR-u-ca-persian', {dateStyle:'full', timeZone});
  const options = Array.from({length:366}, (_, day) => {
    const date = new Date(Date.now() + day * 86400000);
    const parts = Object.fromEntries(dateFormat.formatToParts(date).map(part => [part.type, part.value]));
    return `<option value="${parts.year}-${parts.month}-${parts.day}">${faFormat.format(date)}</option>`;
  });
  document.getElementById('slot-date').innerHTML = '<option value="">تاریخ را انتخاب کنید</option>' + options.join('');
}
async function load() {
  const slotHost = document.getElementById('slots');
  const requestHost = document.getElementById('requests');
  slotHost.setAttribute('aria-busy','true');
  requestHost.setAttribute('aria-busy','true');
  try {
    const [slots, requests] = await Promise.all([api('/api/admin/consultation-slots'), api('/api/admin/consultations')]);
    timeZone = slots.timeZone;
    document.getElementById('timezone').textContent = `تاریخ‌ها شمسی هستند؛ همهٔ ساعت‌ها به وقت ${timeZone === 'Asia/Tehran' ? 'تهران' : timeZone} نمایش و ثبت می‌شوند.`;
    slotHost.innerHTML = slots.slots.length ? `<table class="table"><caption>آخرین ۲۰۰ زمان مشاوره</caption><thead><tr><th scope="col">زمان</th><th scope="col">مدت</th><th scope="col">وضعیت</th><th scope="col">عملیات</th></tr></thead><tbody>${slots.slots.map(slot => `<tr><td>${fmt(slot.starts_at)}</td><td>${number(slot.duration_minutes)} دقیقه</td><td>${esc(labels[slot.status])}</td><td><div class="actions">${['open','blocked','cancelled'].includes(slot.status) && slot.starts_at * 1000 > Date.now() ? `${slot.status !== 'open' ? `<button class="secondary" data-slot="${slot.id}" data-status="open">آزادکردن</button>` : `<button class="secondary" data-slot="${slot.id}" data-status="blocked">مسدودکردن</button>`}${slot.status !== 'cancelled' ? `<button class="danger" data-slot="${slot.id}" data-status="cancelled">لغو زمان</button>` : ''}` : ''}</div></td></tr>`).join('')}</tbody></table>` : '<p class="muted">هنوز زمانی تعریف نشده است.</p>';
    requestHost.innerHTML = requests.requests.length ? `<table class="table"><caption>آخرین ۲۰۰ درخواست مشاوره</caption><thead><tr><th scope="col">نام</th><th scope="col">شمارهٔ تماس</th><th scope="col">زمان</th><th scope="col">توضیح</th><th scope="col">وضعیت</th><th scope="col">تاریخ ثبت</th><th scope="col">عملیات</th></tr></thead><tbody>${requests.requests.map(item => `<tr><td>${esc(item.name) || '—'}</td><td><bdi dir="ltr">${esc(item.phone)}</bdi></td><td>${fmt(item.starts_at)}</td><td class="notes">${esc(item.notes) || '—'}</td><td>${esc(labels[item.status])}</td><td>${fmt(item.created_at)}</td><td><div class="actions">${item.status === 'pending' ? `<button class="success" data-request="${item.id}" data-status="confirmed" ${item.starts_at * 1000 <= Date.now() ? 'disabled' : ''}>تأیید</button><button class="danger" data-request="${item.id}" data-status="cancelled">رد</button>` : ''}${item.status === 'confirmed' ? `<button class="danger" data-request="${item.id}" data-status="cancelled">لغو</button><button class="secondary" data-request="${item.id}" data-status="completed" ${(item.starts_at + item.duration_minutes * 60) * 1000 > Date.now() ? 'disabled' : ''}>انجام شد</button>` : ''}</div></td></tr>`).join('')}</tbody></table>` : '<p class="muted">درخواستی ثبت نشده است.</p>';
  } catch (error) {
    slotHost.textContent = 'دریافت زمان‌ها انجام نشد؛ با دکمهٔ به‌روزرسانی دوباره تلاش کنید.';
    requestHost.textContent = 'دریافت درخواست‌ها انجام نشد؛ دسترسی یا اتصال را بررسی کنید.';
    throw error;
  } finally {
    slotHost.setAttribute('aria-busy','false');
    requestHost.setAttribute('aria-busy','false');
  }
}
async function init() {
  try {
    const data = await api('/api/admin/me');
    if (!['owner','support'].includes(data.principal.role)) throw Error('نقش شما مجوز مدیریت مشاوره‌ها را ندارد.');
    csrf = data.csrf;
    await load();
    fillDates();
    document.getElementById('slot-form').hidden = false;
  } catch (error) {
    say(error.message, true);
    document.getElementById('slots').textContent = 'اطلاعات در دسترس نیست.';
    document.getElementById('requests').textContent = 'اطلاعات در دسترس نیست.';
  }
}
document.getElementById('slot-form').addEventListener('submit', async event => {
  event.preventDefault();
  if (pending) return;
  pending = true;
  const button = event.target.querySelector('[type="submit"]');
  button.disabled = true;
  try {
    const values = new FormData(event.target);
    await api('/api/admin/consultation-slots', {date:values.get('date'), time:values.get('time'), durationMinutes:Number(values.get('durationMinutes'))});
    say('زمان مشاوره اضافه شد.');
    event.target.reset();
    await load();
  } catch (error) {
    say(error.message, true);
  } finally {
    pending = false;
    button.disabled = false;
  }
});
document.addEventListener('click', async event => {
  const slot = event.target.closest('[data-slot]');
  const request = event.target.closest('[data-request]');
  const button = slot || request;
  if (!button || pending || button.disabled) return;
  const warning = button.dataset.status === 'cancelled' ? 'این ثبت حذف نمی‌شود، اما وضعیت آن لغو می‌شود. ادامه می‌دهید؟' : `وضعیت به «${labels[button.dataset.status]}» تغییر کند؟`;
  if (!window.confirm(warning)) return;
  pending = true;
  button.disabled = true;
  try {
    if (slot) await api('/api/admin/consultation-slot-status', {slotId:Number(slot.dataset.slot), status:slot.dataset.status});
    else await api('/api/admin/consultation-status', {requestId:Number(request.dataset.request), status:request.dataset.status});
    say('تغییر با موفقیت ثبت شد.');
    await load();
  } catch (error) {
    say(error.message, true);
  } finally {
    pending = false;
    button.disabled = false;
  }
});
document.getElementById('reload').addEventListener('click', async () => {
  if (pending) return;
  try { await load(); say('فهرست‌ها به‌روز شدند.'); } catch (error) { say(error.message, true); }
});
document.getElementById('logout').addEventListener('click', async () => {
  try { await api('/api/admin/logout', {}); location.assign('/'); } catch (error) { say(error.message, true); }
});
init();
