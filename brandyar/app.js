const icon = (name) => `<svg aria-hidden="true"><use href="#${name}"/></svg>`;
const cta = `<section class="section"><div class="container"><div class="cta-block"><h2>آماده‌ای برند شخصی‌ات را جدی‌تر بسازی؟</h2><p>از شناخت جایگاه امروزت شروع کن و برای قدم بعدی‌ات برنامه داشته باش.</p><a class="btn btn-accent" href="/personal-brand">ارزیابی رایگان را شروع کن ${icon('arrow')}</a></div></div></section>`;
const featureCards = `<div class="feature-grid"><article class="feature-card"><span class="feature-icon">${icon('target')}</span><h3>تحلیل دقیق برند</h3><p>از جایگاه تخصصی و کیفیت محتوا تا اعتمادسازی؛ بدان کجای مسیر ایستاده‌ای و دقیقاً چه چیزی را بهتر کنی.</p><a href="#/features/brand-analysis" class="more">بیشتر بدانید ${icon('arrow')}</a></article><article class="feature-card"><span class="feature-icon">${icon('idea')}</span><h3>ایده‌هایی که به تو می‌آیند</h3><p>به‌جای ایده‌های تکراری، ایده‌هایی که به تخصص، مخاطب و هدف صفحه‌ی خودت می‌خورند.</p><a href="#/features/content-ideas" class="more">بیشتر بدانید ${icon('arrow')}</a></article><article class="feature-card"><span class="feature-icon">${icon('chart')}</span><h3>نقشه راه قابل اجرا</h3><p>از پیدا کردن مشکل تا انجامش؛ قدم‌های کوچک و به‌ترتیب برای رشدی ماندگار بردار.</p><a href="#/features/growth-roadmap" class="more">بیشتر بدانید ${icon('arrow')}</a></article></div>`;
const steps = `<div class="steps"><div class="step-card"><div class="step-num">01</div><h3>چند سؤال ساده</h3><p>از کارهایی که در پیجت انجام می‌دهی و چیزی که می‌خواهی بسازی می‌پرسیم.</p></div><div class="step-card"><div class="step-num">02</div><h3>گزارش اولیه</h3><p>می‌بینی چه اطلاعاتی از پیجت داریم، چه چیزی نیاز به بررسی دارد و از کجا بهتر است شروع کنی.</p></div><div class="step-card"><div class="step-num">03</div><h3>بررسی دقیق‌تر، در صورت نیاز</h3><p>جلسهٔ تصویری برای مرور پیج و نمونهٔ محتوا در حال آماده‌سازی است؛ فعلاً امکان رزرو ندارد.</p></div></div>`;
const productFeatures = [
  {path:'brand',symbol:'user',title:'برند من',problem:'وقتی پیام، لحن و جایگاهت روشن نباشد، مخاطب به‌سختی تو را به خاطر می‌سپارد.',result:'هویت، مخاطب، پیام اصلی و لحن برند شخصی‌ات را یک‌جا شفاف کن.',status:'ثبت و ویرایش دستی'},
  {path:'plan',symbol:'calendar',title:'برنامه',problem:'دانستن اینکه باید محتوا تولید کنی کافی نیست؛ باید بدانی از کجا و با چه اولویتی شروع کنی.',result:'قدم‌های کوتاه، مشخص و قابل‌اجرا برای رشد پیجت داشته باش.',status:'برنامه‌ریزی دستی'},
  {path:'studio',symbol:'idea',title:'استودیو',problem:'ایده‌ها اگر ساختار پیدا نکنند، معمولاً به محتوای منتشرشده تبدیل نمی‌شوند.',result:'ایده، ساختار و نسخهٔ اولیهٔ محتوایت را در یک محیط واحد آماده کن.',status:'استودیوی دستی؛ بدون تولید هوشمند'},
  {path:'learning',symbol:'book',title:'یادگیری',problem:'توصیه‌های پراکنده معمولاً به اقدام واقعی تبدیل نمی‌شوند.',result:'بازخورد محتوای منتشرشده را ثبت کن و از تجربهٔ خودت برای قدم بعدی یاد بگیر.',status:'ثبت تجربه فعال؛ آموزش کوتاه به‌زودی'}
];
const productFeaturesMarkup = () => `<div class="feature-grid product-feature-grid">${productFeatures.map(feature=>`<a class="feature-card product-feature-card" href="#/app/${feature.path}"><span class="feature-icon">${icon(feature.symbol)}</span><h3>${feature.title}</h3><p>${feature.problem}</p><p class="product-feature-result">${feature.result}</p><small>${feature.status}</small><span class="more">دیدن ${feature.title} ${icon('arrow')}</span></a>`).join('')}</div>`;
const assessmentJourney = `<div class="steps">${[
  ['۰۱','وضعیت امروزت را بگو','به چند سؤال کوتاه دربارهٔ تخصص، مخاطب، هدف و محتوای فعلی‌ات پاسخ بده.'],
  ['۰۲','تصویر برندت را ببین','جایگاه، محتوا و اعتمادسازی برند شخصی‌ات را بر اساس پاسخ‌های خودت در یک نمای ساده و قابل‌فهم مرور کن.'],
  ['۰۳','قدم بعدی را اجرا کن','سه قدم پیشنهادی و اولویت‌بندی‌شده برای شروع دریافت کن و آن‌ها را ذخیره کن.']
].map(([number,title,body])=>`<article class="step-card"><div class="step-num">${number}</div><h3>${title}</h3><p>${body}</p></article>`).join('')}</div>`;
const assessmentLandingSections = (session = '') => `<section class="section" id="features"><div class="container feature-editorial"><div class="section-heading"><span class="eyebrow">بعد از شناخت، نوبت ساختن است</span><h2 class="section-title">یک مسیر پیوسته برای برند شخصی تو</h2><p class="section-subtitle">فضای کاری دستی نشارو را بشناس؛ تصمیم، تجربه و تأیید نهایی محتوا با خود توست.</p></div>${productFeaturesMarkup()}</div></section><section class="section soft" id="how-it-works"><div class="container method-editorial"><div class="section-heading center"><span class="eyebrow">نشارو چطور کار می‌کند؟</span><h2 class="section-title">از ارزیابی تا اقدام، کنار تو</h2><p class="section-subtitle">نشارو کمک می‌کند وضعیت امروزت را شفاف ببینی و قدم بعدی را با اطمینان بیشتری برداری.</p></div>${assessmentJourney}<div class="assessment-output-note"><strong>چه چیزی دریافت می‌کنی؟</strong><p>خلاصهٔ پاسخ‌هایت، مواردی که هنوز نیاز به بررسی دارند و سه قدم پیشنهادی قابل ذخیره؛ بدون نمره‌سازی یا تحلیل خودکار پیج.</p><a class="btn btn-dark" href="/personal-brand">ارزیابی رایگان را شروع کن ${icon('arrow')}</a><small>حدود ۵ تا ۷ دقیقه · بدون ثبت‌نام</small></div></div></section>${session}<section class="section light"><div class="container assessment-transparency"><div class="section-heading"><span class="eyebrow">پرسونال برندت را آگاهانه بساز.</span><h2 class="section-title">ارزیابی شفاف، مسیر قابل‌اجرا</h2></div><div><ul class="check-list"><li>${icon('check')} برای شروع لازم نیست حساب اینستاگرامت را وصل کنی.</li><li>${icon('check')} نتیجهٔ اولیه بر پایهٔ پاسخ‌های خودت ساخته می‌شود.</li><li>${icon('check')} هدف نشارو، کمک به تصمیم‌گیری و اقدام مرحله‌به‌مرحله است؛ نه ارائهٔ توصیه‌های کلی و تکراری.</li></ul><p class="section-subtitle">تحلیل گزینه‌های انتخابی پس از تأیید شما از طریق متیس انجام می‌شود؛ متن‌های آزاد به متیس ارسال نمی‌شوند. پاسخ‌ها و گزارش پس از تأیید از حساب شما قابل‌بازیابی‌اند. جزئیات پردازش و نگهداری را در حریم خصوصی بخوان.</p><a class="inline-link" href="#/privacy">حریم خصوصی</a> · <a class="inline-link" href="#/terms">قوانین استفاده</a></div></div></section><section class="section"><div class="container"><div class="cta-block"><h2>مسیر برندت از یک ارزیابی کوتاه شروع می‌شود.</h2><p>وضعیت امروزت را ببین و برای قدم بعدی، یک مسیر روشن‌تر داشته باش.</p><a class="btn btn-accent" href="/personal-brand">ارزیابی رایگان را شروع کن ${icon('arrow')}</a></div></div></section>`;
const problemCards = `<div class="feature-grid"><article class="feature-card"><span class="feature-icon">${icon('target')}</span><h3>موضوع پیج نامشخص است</h3><p>مخاطب تازه‌وارد نمی‌داند دقیقاً چه آموزشی در این صفحه پیدا می‌کند.</p></article><article class="feature-card"><span class="feature-icon">${icon('idea')}</span><h3>تولید محتوا سخت و پراکنده می‌شود</h3><p>هر بار پیدا کردن موضوع جدید، انرژی زیادی می‌گیرد و استمرار را سخت می‌کند.</p></article><article class="feature-card"><span class="feature-icon">${icon('chart')}</span><h3>علاقه به درخواست تبدیل نمی‌شود</h3><p>مخاطب محتوا را دوست دارد، اما نمی‌داند برای قدم بعدی از کجا شروع کند.</p></article></div>`;
const faq = `<div class="faq-list"><details><summary>نشارو برای چه کسانی مناسب است؟</summary><p>برای مدرس‌ها، مربی‌ها و تولیدکنندگان محتوای آموزشی که می‌خواهند در اینستاگرام برند شخصی مشخص‌تری بسازند و محتوایی هدفمندتر منتشر کنند.</p></details><details><summary>برای شروع باید چند دنبال‌کننده داشته باشم؟</summary><p>برای شروع به عدد مشخصی نیاز نیست. مسیر پیشنهادی محصول برای صفحه‌های آموزشی در حال رشد طراحی شده است.</p></details><details><summary>آیا استفاده از محصول رایگان است؟</summary><p>ارزیابی اولیه و گزارش پیشنهادی آن رایگان و بدون ثبت‌نام در دسترس‌اند. طرح‌های نرم‌افزاری دیگر هنوز در مرحلهٔ پیش‌نمایش هستند.</p></details><details><summary>آیا نشارو به جای من محتوا منتشر می‌کند؟</summary><p>هدف، کمک به تحلیل، ایده‌پردازی و برنامه‌ریزی است. در این پیش‌نمایش، انتشار خودکار محتوا و اتصال واقعی به اینستاگرام فعال نیست.</p></details><details><summary>آیا برای دیدن داشبورد باید حساب بسازم؟</summary><p>در این نسخه می‌توانی پیش‌نمایش داشبورد را بدون ثبت‌نام ببینی. اطلاعات نمایشی نمونه هستند و به صفحه واقعی متصل نیستند.</p></details></div>`;
const pageHero = (label, title, sub) => `<section class="page-hero"><div class="container page-intro"><div><a class="page-back" href="#/">نشارو /</a><span class="eyebrow">${label}</span><h1>${title}</h1></div><p>${sub}</p></div></section>`;
const home = () => `<section class="landing-hero" aria-labelledby="landing-title"><div class="landing-container landing-hero-grid"><div class="landing-copy"><span class="landing-kicker">نشارو</span><h1 id="landing-title">برند شخصی تو<br><strong>به سطح بعدی برسون!</strong></h1><p>تحلیل، برنامه‌ریزی و رشد هدفمند برند شخصی<br>با کمک هوش مصنوعی</p><div class="landing-actions"><a class="landing-btn landing-btn-primary" href="/personal-brand">شروع رایگان <svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-arrow"/></svg></a><a class="landing-btn landing-btn-ghost" href="#/" data-home-section="landing-preview"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-play"/></svg> مشاهده دموی محصول</a></div></div><div class="landing-ribbon-visual"><div class="landing-orbit orbit-one" aria-hidden="true"></div><div class="landing-orbit orbit-two" aria-hidden="true"></div><img class="landing-ribbon" src="/landing-logo.png" alt="" width="1568" height="784" decoding="async"><i class="landing-light-dot" aria-hidden="true"></i></div></div></section>
<section class="landing-preview" id="landing-preview" tabindex="-1" aria-label="پیش‌نمایش محصول"><div class="landing-container landing-preview-stage"><article class="landing-dashboard-card" aria-label="پیش‌نمایش داشبورد برند"><aside class="dashboard-rail" aria-label="نمونهٔ نوار کناری داشبورد"><img class="rail-logo" src="/landing-logo.png" alt="" width="1568" height="784" decoding="async"><span class="rail-icon is-active"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-home"/></svg></span><span class="rail-icon"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-bars"/></svg></span><span class="rail-icon"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-document"/></svg></span><span class="rail-icon"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-pie"/></svg></span><span class="dashboard-avatar" role="img" aria-label="نشان کاربر"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-user"/></svg></span></aside><div class="dashboard-main"><div class="dashboard-top"><span class="dashboard-period">۳۰ روز گذشته <svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-chevron"/></svg></span></div><div class="dashboard-score"><div class="landing-score" role="img" aria-label="اعتبار برند ۸۷ درصد"><svg viewBox="0 0 200 200" aria-hidden="true"><defs><linearGradient id="lp-ring-gradient" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#1243ab"/><stop offset=".55" stop-color="#10cfe2"/><stop offset="1" stop-color="#31f3c3"/></linearGradient></defs><circle class="ring-track" cx="100" cy="100" r="82"/><circle class="ring-progress" cx="100" cy="100" r="82" pathLength="100"/></svg><div><strong>۸۷٪</strong><small>اعتبار برند</small></div></div><div class="dashboard-chart"><svg viewBox="0 0 400 216" role="img" aria-label="نمودار خطی صعودی برند"><defs><linearGradient id="lp-chart-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#08e5c3" stop-opacity=".48"/><stop offset="1" stop-color="#08bada" stop-opacity=".04"/></linearGradient><pattern id="lp-chart-grid" width="48" height="43" patternUnits="userSpaceOnUse"><path d="M48 0H0V43" fill="none" stroke="#3bc2d4" stroke-opacity=".12" stroke-width="1"/></pattern></defs><rect width="400" height="216" fill="url(#lp-chart-grid)"/><path class="chart-fill" d="M8 185 C38 160 50 141 75 147 S100 169 127 140 S161 163 197 101 S238 130 267 113 S307 35 335 39 S366 80 391 42 V216 H8Z"/><path class="chart-line" d="M8 185 C38 160 50 141 75 147 S100 169 127 140 S161 163 197 101 S238 130 267 113 S307 35 335 39 S366 80 391 42"/><g class="chart-points"><circle cx="75" cy="147" r="3.8"/><circle cx="127" cy="140" r="3.8"/><circle cx="197" cy="101" r="3.8"/><circle cx="267" cy="113" r="3.8"/><circle cx="335" cy="39" r="3.8"/><circle cx="391" cy="42" r="3.8"/></g></svg></div></div><div class="dashboard-stats"><div class="dashboard-stat"><span class="stat-value"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-people"/></svg><strong dir="ltr">↑٪۷۴</strong></span><small>رشد تعامل</small></div><div class="dashboard-stat"><span class="stat-value"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-people"/></svg><strong dir="ltr">۱۲.۵K</strong></span><small>مخاطبان هدف</small></div><div class="dashboard-stat"><span class="stat-value"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-play"/></svg><strong dir="ltr">۹.۸٪</strong></span><small>نرخ تعامل</small></div></div></div></article><article class="landing-insight-card"><span class="landing-pill">داشبورد</span><h2>تحلیل عمیق برند<br>با داده‌های واقعی</h2><p>وضعیت برند خود را به‌صورت دقیق تحلیل کنید<br>و مسیر رشد خود را ببینید</p><a href="/brandyar/dashboard" class="landing-outline-btn">مشاهده جزئیات <svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-arrow"/></svg></a></article></div></section>
<section class="landing-features" id="landing-features" aria-labelledby="features-heading"><div class="landing-container"><div class="landing-section-heading"><span>امکانات کلیدی</span><h2 id="features-heading">همه چیز برای ساخت یک برند قدرتمند</h2></div><div class="landing-feature-grid"><article><span class="landing-feature-icon"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-shield"/></svg></span><h3>تحلیل هوشمند برند</h3><p>شناخت جایگاه و نقاط قوت</p></article><article><span class="landing-feature-icon"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-bars"/></svg></span><h3>مسیر رشد اختصاصی</h3><p>برنامه‌ریزی قدم به قدم</p></article><article><span class="landing-feature-icon"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-diamond"/></svg></span><h3>پیشنهاد محتوای هدفمند</h3><p>ایده‌های خلاقانه و کاربردی</p></article><article><span class="landing-feature-icon"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-target"/></svg></span><h3>گزارش‌های پیشرفته</h3><p>مشاهده نتایج و پیشرفت</p></article></div></div></section>
<section class="landing-proof" aria-label="نظرات و شروع کار"><div class="landing-container landing-proof-grid"><article class="landing-testimonial"><span class="testimonial-quote" aria-hidden="true"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-quote"/></svg></span><span class="testimonial-avatar" role="img" aria-label="جای تصویر کاربر؛ تصویر شخص در فایل‌های پیوست موجود نیست"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-user"/></svg></span><blockquote><p>نشارو دقیقا همون ابزاریه که بهش نیاز داشتم.<br>خیلی حرفه‌ای، کاربردی و متفاوت!</p><footer>علیرضا رضایی — مدرس تولید محتوا</footer></blockquote><div class="testimonial-dots" role="img" aria-label="نظر اول از سه جایگاه نمایشی"><i class="active"></i><i></i><i></i></div></article><article class="landing-cta-card"><div class="cta-art" aria-hidden="true"><img class="cta-ribbon" src="/landing-logo.png" alt="" width="1568" height="784" decoding="async"></div><div class="cta-copy"><h2>آماده‌اید برند شخصی‌تون رو بسازید؟</h2><p>همین حالا شروع کنید با نشارو. یک قدم جلوتر باشید</p><a href="/personal-brand" class="landing-btn landing-btn-primary">شروع رایگان <svg aria-hidden="true" viewBox="0 0 24 24"><use href="#lp-arrow"/></svg></a></div></article></div></section>`;
function pricingCards(){return `<div class="pricing-grid"><article class="price-card"><span class="pill">برای شروع</span><h3>رایگان</h3><p>برای شناخت مسیر و دیدن امکانات پایه محصول.</p><div class="price">0 <small>تومان</small></div><a href="/personal-brand" class="btn btn-outline">رایگان شروع کن</a><ul><li>${icon('check')} آشنایی با مسیر ساخت برند</li><li>${icon('check')} دسترسی به امکانات پایه پس از راه‌اندازی</li><li>${icon('check')} بدون نیاز به پرداخت برای شروع</li></ul></article><article class="price-card featured"><span class="pill">برای رشد جدی‌تر</span><h3>حرفه‌ای</h3><p>برای مدرس‌هایی که می‌خواهند مسیر رشدشان را منظم پیش ببرند.</p><div class="price">7,990,000 <small>تومان / ماه</small></div><a href="/personal-brand" class="btn btn-accent">دیدن ارزیابی رایگان ${icon('arrow')}</a><ul><li>${icon('check')} تحلیل جامع پرسونال برند</li><li>${icon('check')} نقشه راه رشد اختصاصی</li><li>${icon('check')} ایده‌های محتوایی متناسب با تخصص</li><li>${icon('check')} اولویت‌بندی فرصت‌های بهبود</li></ul></article><article class="price-card custom"><span class="pill">متناسب با نیاز شما</span><h3>سفارشی</h3><p>برای تیم‌ها و مجموعه‌های آموزشی با نیازهای متفاوت.</p><div class="price price-custom">توافقی <small>پس از بررسی نیازها</small></div><a href="/personal-brand" class="btn btn-outline">ارزیابی رایگان ${icon('arrow')}</a><ul><li>${icon('check')} بررسی نیازهای کسب‌وکار شما</li><li>${icon('check')} طراحی مسیر متناسب با اهداف تیم</li><li>${icon('check')} تعیین امکانات و قیمت پس از گفتگو</li></ul></article></div><p class="pricing-note">این تعرفه‌ها مربوط به نرم‌افزارِ در حال توسعه‌اند، نه ارزیابی رایگان یا جلسهٔ تصویری. ثبت‌نام، پرداخت و رزرو جلسه هنوز فعال نیستند.</p>`}
const pages = {
  '': home,
  'features': () => `${pageHero('امکانات نشارو','هر چیزی که برای ساخت برندت لازم داری','از تحلیل جایگاه امروزت تا پیدا کردن ایده و برداشتن قدم بعدی، همه چیز در یک مسیر منسجم.') }<section class="section"><div class="container">${featureCards}</div></section><section class="section soft"><div class="container split"><div><span class="eyebrow">تصمیم‌های بهتر</span><h2 class="section-title">داده‌ها را به <em>اقدام تبدیل کن.</em></h2><p class="section-subtitle">فقط یک عدد و نمودار نمی‌بینی؛ برای هر بخش از برندت می‌فهمی کدام فرصت رشد، توجه بیشتری می‌خواهد.</p><ul class="check-list"><li>${icon('check')} ارزیابی جایگاه تخصصی و کیفیت محتوا</li><li>${icon('check')} ایده‌های متناسب با هدف مخاطب</li><li>${icon('check')} مسیر رشد مرحله‌بندی‌شده</li></ul></div><div class="insight-art"><div class="insight-sheet"><strong>گزارش نمونه</strong><div class="insight-row"><span>تخصص و جایگاه‌سازی</span><strong>88%</strong></div><div class="insight-row"><span>کیفیت محتوا</span><strong>76%</strong></div><div class="insight-row"><span>اعتمادسازی و فروش</span><strong>59%</strong></div></div></div></div></section>${cta}`,
  'how-it-works': () => `${pageHero('چطور کار می‌کند؟','از تخصص تو تا برندی ماندگار','یک مسیر ساده و مرحله‌به‌مرحله برای تبدیل دانش به محتوایی که دیده و به خاطر سپرده شود.') }<section class="section light"><div class="container">${steps}</div></section><section class="section soft"><div class="container split"><div class="insight-art"><div class="insight-sheet"><strong>قدم‌های رشد برند</strong><div class="insight-row"><span>1. شناخت جایگاه</span><strong>شروع</strong></div><div class="insight-row"><span>2. ساخت اعتماد</span><strong>اولویت فعلی</strong></div><div class="insight-row"><span>3. تبدیل مخاطب</span><strong>قدم بعد</strong></div></div></div><div><span class="eyebrow">از برنامه تا عمل</span><h2 class="section-title">هر مرحله، <em>یک قدم روشن.</em></h2><p class="section-subtitle">وقتی بدانید مخاطبتان چه چیزی از شما می‌خواهد، تصمیم‌گیری درباره محتوا راحت‌تر می‌شود. نشارو کمک می‌کند اولویت‌ها را واضح ببینید.</p><a href="#/app" class="btn btn-dark">دیدن پیش‌نمایش داشبورد ${icon('arrow')}</a></div></div></section>${cta}`,
  'pricing': () => `${pageHero('تعرفه‌ها','تعرفه‌های پیش‌نمایش نرم‌افزار در حال توسعه','این قیمت‌ها مربوط به طرح‌های احتمالی نرم‌افزار آینده‌اند؛ ارزیابی فعلی رایگان است و رزرو جلسه هنوز فعال نیست.') }<section class="section"><div class="container">${pricingCards()}</div></section><section class="section soft"><div class="container"><div class="section-heading center"><h2 class="section-title">سؤالی درباره طرح‌ها داری؟</h2></div>${faq}</div></section>${cta}`,
  'faq': () => `${pageHero('سؤالات متداول','جواب سؤال‌هایت اینجاست','پیش از شروع، با خیال راحت درباره مسیر و امکانات نشارو بیشتر بدان.') }<section class="section"><div class="container">${faq}</div></section>${cta}`,
  'about': () => `${pageHero('درباره نشارو','برند شخصی، از خودت شروع می‌شود','قرار نیست برای دیده شدن شبیه دیگران شوی؛ کافی است ارزش واقعی‌ات را واضح‌تر نشان دهی.') }<section class="section"><div class="container about-grid"><article class="white-card"><span class="eyebrow">مسئله‌ای که می‌شناسیم</span><h2>از کجا شروع کنم؟</h2><p class="section-subtitle">خیلی از مدرس‌ها تخصص دارند اما برای نمایش آن، ساخت اعتماد و تبدیل مخاطب به مشتری مسیر مشخصی ندارند. تولید محتوای بیشتر، بدون جهت‌گیری درست، همیشه جواب نیست.</p></article><article class="white-card"><span class="eyebrow">چیزی که می‌خواهیم بسازیم</span><h2>یک همراه در تمام مسیر</h2><p class="section-subtitle">نشارو برای کمک به شناخت برند فعلی، شناسایی فرصت‌ها و تبدیل پیشنهادها به یک نقشه راه قابل اجرا طراحی شده است؛ از عیب‌یابی تا ایده‌پردازی.</p></article></div></section>${cta}`,
  'login': () => authPage(false),
  'signup': () => authPage(true)
};
const featureDetail = ({ label, title, sub, lead, points, asideTitle, asideRows, faqs, ctaTitle, ctaText, ctaHref, ctaLabel }) => `${pageHero(label, title, sub)}<section class="section"><div class="container split"><div><span class="eyebrow">چرا مهم است؟</span><h2 class="section-title">${lead.heading}</h2><p class="section-subtitle">${lead.body}</p><ul class="check-list">${points.map((point) => `<li>${icon('check')} ${point}</li>`).join('')}</ul></div><div class="insight-art"><div class="insight-sheet"><strong>${asideTitle}</strong>${asideRows.map(([key, value]) => `<div class="insight-row"><span>${key}</span><strong>${value}</strong></div>`).join('')}</div></div></div></section><section class="section soft"><div class="container legal-copy"><div class="section-heading center"><h2 class="section-title">پرسش‌های پرتکرار</h2></div><div class="faq-list">${faqs.map(([q, a]) => `<details><summary>${q}</summary><p>${a}</p></details>`).join('')}</div></div></section><section class="section"><div class="container"><div class="cta-block"><h2>${ctaTitle}</h2><p>${ctaText}</p><a class="btn btn-accent" href="${ctaHref}">${ctaLabel} ${icon('arrow')}</a></div></div></section>`;
const featurePages = {
  'brand-analysis': {
    label: 'امکانات نشارو — تحلیل برند',
    title: 'تحلیل دقیق برند',
    sub: 'بدان کجای مسیر ایستاده‌ای و کدام بخش برندت بیشتر به توجه نیاز دارد.',
    lead: {
      heading: 'قبل از محتوا ساختن، <em>یک نگاه به وضعیتت بینداز.</em>',
      body: 'خیلی از ما محتوای زیاد منتشر می‌کنیم، فقط چون دقیقاً نمی‌دانیم الان کجای مسیر ایستاده‌ایم. تحلیل برند اول فاصله‌ی بین آنچه هستی و آنچه مخاطب می‌بیند را روشن می‌کند، بعد نشان می‌دهد کدام بخش را باید درست کنی.',
    },
    points: [
      'سنجش جایگاه تخصصی و تمایز در حوزه کاری‌ات',
      'بررسی کیفیت و ارزش محتوای منتشرشده',
      'ارزیابی میزان اعتمادسازی و مسیر تبدیل مخاطب',
      'مشخص‌کردن نقاط قوت برای تقویت و ضعف‌ها برای اصلاح',
    ],
    asideTitle: 'نمونه گزارش تحلیل',
    asideRows: [['جایگاه تخصصی', '88%'], ['کیفیت و ارزش محتوا', '76%'], ['ارتباط با مخاطب', '72%'], ['اعتمادسازی و فروش', '59%']],
    faqs: [
      ['برای تحلیل به چند دنبال‌کننده نیاز دارم؟', 'برای شروع به عدد مشخصی نیاز نیست. تحلیل بر جایگاه تخصصی، کیفیت محتوا و اعتمادسازی تمرکز دارد و برای صفحه‌های آموزشی در حال رشد طراحی شده است.'],
      ['تحلیل بر چه چیزی تکیه می‌کند؟', 'بر اطلاعاتی که خودت از حرفه، مخاطب هدف و محتوایت وارد می‌کنی. اتصال اینستاگرام در نسخه فعلی فعال نیست و هیچ داده‌ای بدون اجازه تو خوانده نمی‌شود.'],
      ['خروجی تحلیل چه شکلی است؟', 'یک تصویر کلی از سلامت برند همراه با تفکیک بخش‌ها و توضیح اینکه کدام فرصت رشد اولویت بیشتری دارد.'],
    ],
    ctaTitle: 'هنوز مطمئن نیستی از کجا شروع کنی؟',
    ctaText: 'اول جایگاه امروزت را روشن کن تا محتوایت به‌جای بیشتر شدن، دقیق‌تر شود.',
    ctaLabel: 'از جای درستم شروع کنم',
  },
  'content-ideas': {
    label: 'امکانات نشارو — ایده محتوا',
    title: 'ایده‌هایی که به تو می‌آیند',
    sub: 'به‌جای ایده‌های تکراری، ایده‌هایی که به تخصص و مخاطب خودت می‌خورند.',
    lead: {
      heading: 'ایده‌ها باید <em>از خودت</em> بیایند.',
      body: 'هرچه ایده عمومی‌تر باشد، شبیه بقیه‌ی صفحه‌ها می‌شود. ایده‌پردازی در نشارو از حرفه‌ات، مخاطبت و هدفی که از محتوا داری شروع می‌شود تا محتوایت صدای خودت را داشته باشد.',
    },
    points: [
      'ایده‌های محتوایی متناسب با حوزه تخصص و مخاطب هدف',
      'پیشنهاد زاویه و روایت برای هر ایده، نه فقط یک تیتر',
      'تحلیل اینکه هر ایده کدام نیاز مخاطب را پاسخ می‌دهد',
      'امکان ذخیره ایده‌های مناسب در کتابخانه محتوا',
    ],
    asideTitle: 'نمونه ایده‌های پیشنهادی',
    asideRows: [['برای اعتمادسازی', 'روایت یک اشتباه واقعی'], ['برای نشان‌دادن تخصص', 'شکستن یک باور رایج'], ['برای ارتباط با مخاطب', 'پاسخ به سؤال پرتکرار']],
    faqs: [
      ['ایده‌ها از کجا می‌آیند؟', 'از اطلاعات پروفایل برند تو: حرفه، حوزه تخصص، مخاطب هدف و محصولات و خدمات. هرچه این اطلاعات کامل‌تر باشد، ایده‌ها دقیق‌تر می‌شوند.'],
      ['ایده‌ها متن آماده هستند یا پیشنهاد موضوع؟', 'هر ایده با زاویه، هدف و مخاطب پیشنهادی می‌آید تا خودت روایت را با تجربه و لحن خودت بنویسی.'],
      ['می‌توانم ایده‌ها را نگه دارم؟', 'بله. ایده‌های مناسب در کتابخانه محتوا ذخیره می‌شوند تا بعداً سراغ نوشتن سناریو و برنامه انتشار بروی.'],
    ],
    ctaTitle: 'هر بار می‌نشینی و می‌گویی «خب، چی بسازم؟»',
    ctaText: 'ایده‌های مناسب تخصصت را یک‌جا ببین و از همان‌جا دست‌به‌کار شو.',
    ctaLabel: 'ایده‌های من را نشانم بده',
  },
  'growth-roadmap': {
    label: 'امکانات نشارو — نقشه راه',
    title: 'نقشه راه قابل اجرا',
    sub: 'از پیدا کردن مشکل تا انجامش؛ قدم‌های کوچک و به‌ترتیب برای رشدی ماندگار.',
    lead: {
      heading: 'توصیه‌های پراکنده <em>رشد نمی‌سازند.</em>',
      body: 'وقتی فهرست کارها بی‌نهایت است، معمولاً هیچ‌کدام انجام نمی‌شود. نقشه راه کارها را به ترتیب اثر می‌چیند تا هر بار بدانی قدم بعدی چیست و چرا این یکی مهم‌تر است.',
    },
    points: [
      'تبدیل تحلیل برند به قدم‌های اجرایی مشخص',
      'اولویت‌بندی کارها متناسب با مرحله فعلی رشد',
      'تعریف وضعیت هر قدم: انجام‌شده، در حال انجام، انجام‌نشده',
      'نمایش پیشرفت در طول زمان به‌جای فهرست بی‌پایان کارها',
    ],
    asideTitle: 'نمونه نقشه راه',
    asideRows: [['۱. بازنویسی بیو', 'اولویت فعلی'], ['۲. روایت تجربه‌های واقعی', 'قدم بعد'], ['۳. تبدیل مخاطب به مشتری', 'مرحله بعدی']],
    faqs: [
      ['نقشه راه چطور ساخته می‌شود؟', 'نتیجه تحلیل برند مشخص می‌کند کدام بخش بیشترین اثر را دارد. نقشه راه همان فرصت‌ها را به قدم‌های کوچک و قابل انجام تبدیل می‌کند.'],
      ['اگر فقط وقت انجام یک کار را داشته باشم؟', 'کارها اولویت‌بندی‌شده‌اند. همیشه بالاترین اولویت در دسترس است تا با کمترین زمان، بیشترین اثر را بگیری.'],
      ['پیشرفتم را چطور ببینم؟', 'وضعیت هر قدم را به‌روز می‌کنی و پیشرفت کلی در داشبورد نمایش داده می‌شود.'],
    ],
    ctaTitle: 'در ذهنت کلی کار ریخته‌ای؟',
    ctaText: 'به‌جای فهرست بی‌پایان، فقط قدم بعدی‌ات را ببین و همان یکی را انجام بده.',
    ctaLabel: 'نقشه راهم را بساز',
  },
};
for (const key of Object.keys(featurePages)) {
  pages[`features/${key}`] = () => featureDetail({ ...featurePages[key], ctaHref: '#/signup' });
}
function authPage(signup){return `<section class="form-page"><div class="auth-card"><h1>${signup?'برندت را از امروز جدی بگیر':'خوش آمدی به نشارو'}</h1><p>${signup?'همین حالا شروع کن؛ لازم نیست همه چیز را از قبل بدانی.':'برای ورود به فضای کاری، اطلاعات حسابت را وارد کن.'}</p><div class="notice">${signup?'ثبت‌نام هنوز فعال نیست.':'ورود کارکنان مجاز با رمز عبور و تأیید دومرحله‌ای انجام می‌شود؛ حساب کاربران عادی هنوز راه‌اندازی نشده است.'} <a href="#/app" class="dashboard-link">پروفایل حساب ${icon('arrow')}</a></div><form id="auth-form">${signup?'<div class="field"><label for="name">نام و نام خانوادگی</label><input id="name" name="name" type="text" autocomplete="name" required placeholder="نام شما"></div>':''}<div class="field"><label for="email">ایمیل</label><input id="email" name="email" type="email" autocomplete="email" required placeholder="name@example.com"></div><div class="field"><label for="password">رمز عبور</label><input id="password" name="password" type="password" autocomplete="${signup?'new-password':'current-password'}" minlength="8" required placeholder="حداقل 8 کاراکتر">${signup?'<small>برای نسخه نهایی، رمز عبور حداقل 8 کاراکتر خواهد بود.</small>':''}</div><button class="btn btn-dark" type="submit">${signup?'ساختن حساب':'ورود به حساب'} ${icon('arrow')}</button><div class="form-feedback" id="form-feedback" role="status" aria-live="polite"></div></form><div class="auth-bottom">${signup?'قبلاً حساب ساخته‌ای؟ <a href="#/login">وارد شو</a>':'حساب نداری؟ <a href="/personal-brand">ارزیابی رایگان را شروع کن</a>'}</div></div></section>`}
function esc(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function notify(message){let area=document.getElementById('toast');if(!area)return;area.textContent=message;area.hidden=false;clearTimeout(notify.timer);notify.timer=setTimeout(()=>area.hidden=true,4000)}
const appPages={};
pages.contact=()=>`${pageHero('تماس با ما','گفتگو، بهترین نقطه شروع است','برای پرسش درباره محصول یا همکاری، موضوع خود را ثبت کنید.') }<section class="section"><div class="container"><div class="panel contact-panel"><h2>پیام شما</h2><div class="notice">در این پیش‌نمایش ارسال پیام به پشتیبانی فعال نیست. اطلاعاتی که وارد کنید ارسال یا ذخیره نمی‌شود.</div><form id="contact-form"><div class="field"><label for="contact-name">نام</label><input id="contact-name" required></div><div class="field"><label for="contact-email">ایمیل</label><input id="contact-email" type="email" required></div><div class="field"><label for="contact-message">پیام</label><textarea id="contact-message" required rows="5"></textarea></div><button class="btn btn-dark" type="submit">ثبت پیام نمایشی</button></form></div></div></section>`;
pages.terms=()=>`${pageHero('قوانین استفاده','شرایط استفاده از نسخه نمایشی','این صفحه وضعیت فعلی محصول را به‌روشنی توضیح می‌دهد.') }<section class="section"><div class="container legal-copy panel"><h2>دامنه پیش‌نمایش</h2><p>این سایت ارزیابی اولیهٔ خوداظهاری و گزارش پیشنهادی قابل دانلود ارائه می‌کند؛ ثبت‌نام، پرداخت، رزرو جلسه، تحلیل خودکار پیج و اتصال اینستاگرام فعال نیستند. بخش داشبورد صرفاً پیش‌نمایش رابط با داده‌های نمونه است.</p><h2>مسئولیت محتوا</h2><p>پیشنهادهای محتوایی و سناریوهای قالبی باید پیش از انتشار توسط شما بازبینی شوند. محصول وعده قطعی افزایش بازدید، دنبال‌کننده یا فروش نمی‌دهد.</p><h2>تغییرات آینده</h2><p>شرایط نهایی سرویس هنگام راه‌اندازی واقعی همراه با جزئیات خدمات و پشتیبانی منتشر خواهد شد.</p></div></section>`;
pages.privacy=()=>`${pageHero('حریم خصوصی','کنترل اطلاعات حساب','اطلاعات حساب از هویت حرفه‌ای و نتیجهٔ تست مستقل است.')}<section class="section"><div class="container panel"><p>اطلاعات ثبت‌شده برای بازیابی مسیر، راهنمای برند و خروجی‌های شما استفاده می‌شود. پیشنهادهای هوش مصنوعی فقط با اقدام شما ساخته و پس از بررسی شما قابل استفاده می‌شوند. از واردکردن اطلاعات خصوصی دیگران خودداری کنید.</p><p>اطلاعات تماس حساب به معنی تأیید مالکیت شماره یا ایمیل نیست. هیچ رمز عبور اینستاگرامی درخواست نمی‌کنیم.</p></div></section>`;
pages['instagram-guide']=()=>`${pageHero('راهنمای اتصال اینستاگرام','اتصال امن، با اختیار شما','اتصال حساب حرفه‌ای در مرحلهٔ پنجم ارزیابی پرسونال برند در دسترس است.')}<section class="section"><div class="container legal-copy panel"><h2>اتصال رسمی و اختیاری</h2><p>رمز عبور شما دریافت نمی‌شود؛ مجوز فقط از صفحهٔ رسمی Meta داده می‌شود و هر زمان امکان قطع اتصال یا درخواست حذف داده دارید.</p><p>بدون اتصال هم می‌توانید ارزیابی را کامل کنید. اگر تنظیمات اپ Meta آماده نباشد، وضعیت «نیازمند تکمیل تنظیمات» نمایش داده می‌شود و هیچ اتصال موفقی شبیه‌سازی نمی‌شود.</p><a class="btn btn-dark" href="/personal-brand">شروع یا ادامهٔ ارزیابی و مدیریت اتصال</a></div></section>`;
pages.loading=()=>`${pageHero('وضعیت بارگذاری','در حال آماده‌سازی اطلاعات','این صفحه نمونه‌ای از وضعیت بارگذاری است؛ درخواست زنده‌ای در این نسخه انجام نمی‌شود.') }<section class="section"><div class="container legal-copy panel"><div class="skeleton" aria-label="نمونه وضعیت بارگذاری"></div><div class="skeleton short"></div><a class="btn btn-outline" href="#/">بازگشت به خانه</a></div></section>`;
let motionObserver;
function setupHeroMotion(){const visual=document.querySelector('.hero-visual');if(!visual)return;const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;requestAnimationFrame(()=>visual.classList.add('hero-ready'));if(reduced||!window.matchMedia('(min-width: 801px) and (hover: hover) and (pointer: fine)').matches)return;visual.addEventListener('pointermove',event=>{const rect=visual.getBoundingClientRect();visual.style.setProperty('--glow-x',`${(event.clientX-rect.left)/rect.width*100}%`);visual.style.setProperty('--glow-y',`${(event.clientY-rect.top)/rect.height*100}%`);const x=Math.max(-.5,Math.min(.5,(event.clientX-rect.left)/rect.width-.5)),y=Math.max(-.5,Math.min(.5,(event.clientY-rect.top)/rect.height-.5));visual.style.setProperty('--card-rotate-x',`${-y*8}deg`);visual.style.setProperty('--card-rotate-y',`${x*8}deg`);visual.style.setProperty('--card-shift-x',`${x*14}px`);visual.style.setProperty('--card-shift-y',`${y*10}px`);visual.style.setProperty('--card-shadow-x',`${-x*24}px`);visual.style.setProperty('--card-shadow-y',`${28+y*12}px`)});visual.addEventListener('pointerleave',()=>{for(const name of ['--glow-x','--glow-y','--card-rotate-x','--card-rotate-y','--card-shift-x','--card-shift-y','--card-shadow-x','--card-shadow-y'])visual.style.removeProperty(name)})}
function setupMotion(){if(motionObserver)motionObserver.disconnect();const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;const selectors=['.hero-copy','.trust-inner','.page-hero .container','.section-heading','.feature-card','.split > *','.step-card','.price-card','.faq-list details','.cta-block','.app-heading','.app-banner','.metric-card','.app-grid > .panel','.roadmap-stage','.analysis-card','.calendar-day','.settings-grid > *'];const items=[...new Set(selectors.flatMap(selector=>[...document.querySelectorAll(selector)]))];items.forEach((item,index)=>{item.classList.add('motion-item');if(item.closest('.hero'))item.classList.add('motion-hero');item.style.setProperty('--motion-delay',`${Math.min(index%4,3)*70}ms`)});if(reduced||!('IntersectionObserver' in window)){items.forEach(item=>item.classList.add('is-visible'));return}motionObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-visible');motionObserver.unobserve(entry.target)}}),{threshold:.12,rootMargin:'0px 0px -7%'});items.forEach(item=>motionObserver.observe(item))}
const assessmentQuestions = [
  {id:'q1',section:'موضوع پیج و هدف',title:'بیشتر دربارهٔ چه چیزی آموزش می‌دهی؟',type:'text',hint:'مثلاً آموزش زبان، طراحی، آشپزی، ورزش، فروش یا مهارت‌های نرم'},
  {id:'q2',section:'موضوع پیج و هدف',title:'این روزها بیشتر چه کسانی به آموزش‌هایت علاقه نشان می‌دهند؟',options:['کسانی که تازه می‌خواهند این موضوع را یاد بگیرند','کسانی که کمی تجربه دارند و می‌خواهند بهتر شوند','افراد حرفه‌ای‌تر','گروه‌های مختلف','هنوز دقیق نمی‌دانم'],extra:'اگر دوست داری، بیشتر توضیح بده (اختیاری)'},
  {id:'q3',section:'موضوع پیج و هدف',title:'معمولاً مردم چه سؤال یا مشکلی را در دایرکت یا زیر پست‌ها با تو مطرح می‌کنند؟',type:'text',skip:'هنوز پیام یا سؤال زیادی دریافت نمی‌کنم'},
  {id:'q4',section:'موضوع پیج و هدف',title:'دوست داری در سه ماه آینده، بیشتر کدام اتفاق برای پیجت بیفتد؟',options:['افراد بیشتری آموزش‌هایم را ببینند','افراد بیشتری به من اعتماد کنند','برای کلاس، دوره یا خدمتم درخواست بیشتری بگیرم','منظم‌تر محتوا منتشر کنم','موضوع پیجم برای مخاطب روشن‌تر شود','هنوز مطمئن نیستم']},
  {id:'q5',section:'آنچه امروز در پیج دیده می‌شود',title:'اگر کسی امروز وارد پیجت شود، کدام مورد را در پیجت می‌بیند؟',type:'multi',options:['در بیو نوشته‌ام چه آموزشی می‌دهم','یک پست یا ریلز معرفی را سنجاق کرده‌ام','هایلایت معرفی یا شروع از اینجا دارم','نمونه‌ای از آموزش‌هایم در پیج هست','راه ارتباط یا پرسیدن سؤال را مشخص کرده‌ام','هیچ‌کدام یا مطمئن نیستم'],none:'هیچ‌کدام یا مطمئن نیستم'},
  {id:'q6',section:'آنچه امروز در پیج دیده می‌شود',title:'اگر راحتی، متن فعلی بیوی پیجت را اینجا کپی کن.',type:'textarea',optional:true,hint:'لازم نیست آن را بهتر یا رسمی‌تر بنویسی؛ همان متنی که الان در پیجت هست کافی است.'},
  {id:'q7',section:'آنچه امروز در پیج دیده می‌شود',title:'در دو هفتهٔ گذشته برای پیجت چه کاری انجام داده‌ای؟',type:'multi',options:['پست یا ریلز آموزشی منتشر کرده‌ام','به سؤال یا پیام مخاطبان جواب داده‌ام','کلاس، دوره یا خدمتم را معرفی کرده‌ام','تجربه، نمونه‌کار یا نتیجهٔ واقعی منتشر کرده‌ام','پیج یا محتوای قبلی‌ام را مرتب کرده‌ام','این مدت چیزی منتشر نکرده‌ام'],none:'این مدت چیزی منتشر نکرده‌ام'},
  {id:'q8',section:'محتوا و اعتماد',title:'معمولاً موضوع محتوای بعدی‌ات را چطور انتخاب می‌کنی؟',options:['از سؤال‌ها و پیام‌های مخاطبان','از تجربهٔ خودم در کار یا تدریس','از برنامه‌ای که از قبل نوشته‌ام','از موضوعات پرطرفدار و ترند','هر بار همان موقع تصمیم می‌گیرم','روش دیگری دارم']},
  {id:'q9',section:'محتوا و اعتماد',title:'در پیجت چه چیزی از تجربه یا روش واقعی کارت دیده می‌شود؟',type:'multi',options:['بخشی از آموزش یا تدریسم را نشان داده‌ام','دربارهٔ روش کارم توضیح داده‌ام','نمونه‌کار یا نتیجه‌ای را با اجازهٔ صاحب آن منتشر کرده‌ام','به سؤال‌های پرتکرار جواب کامل داده‌ام','پشت‌صحنهٔ کار یا تجربهٔ شخصی‌ام را گفته‌ام','فعلاً مورد مشخصی ندارم'],none:'فعلاً مورد مشخصی ندارم'},
  {id:'q10',section:'محتوا و اعتماد',title:'الان بیشتر کدام بخش تولید محتوا برایت سخت است؟',type:'multi',max:2,options:['پیدا کردن ایدهٔ محتوا','منظم منتشر کردن','نوشتن یا ساختن خود محتوا','دیده شدن محتوا','اینکه مخاطب به من اعتماد کند','اینکه محتوا به درخواست یا فروش برسد','نمی‌دانم از کجا شروع کنم']},
  {id:'q11',section:'راه ارتباط و خدمات',title:'الان از چه راهی می‌توانی به مخاطبت کمک کنی؟',type:'multi',options:['آموزش رایگان در پیج','کلاس یا دورهٔ آموزشی','جلسه یا مشاورهٔ خصوصی','انجام یک خدمت','محصول دیجیتال یا فیزیکی','فعلاً چیزی برای فروش ندارم'],none:'فعلاً چیزی برای فروش ندارم'},
  {id:'q12',section:'راه ارتباط و خدمات',title:'اگر کسی همین حالا بخواهد دربارهٔ کلاس یا خدمتت بیشتر بداند، از کجا شروع می‌کند؟',options:['لینک بیو','هایلایت','پست یا ریلز معرفی','دایرکت','راه مشخصی نگذاشته‌ام']},
  {id:'q13',section:'راه ارتباط و خدمات',title:'وقتی کسی دربارهٔ کار با تو سؤال می‌کند، معمولاً چه می‌کنی؟',options:['لینک یا توضیح آماده می‌فرستم','در دایرکت توضیح می‌دهم','بسته به شرایط فرق می‌کند','هنوز چنین درخواستی نداشته‌ام']},
  {id:'q14',section:'راه ارتباط و خدمات',title:'در ماه گذشته، چند نفر دربارهٔ کلاس، دوره، خدمت یا همکاری از تو سؤال کرده‌اند؟',options:['هیچ‌کس','۱ تا ۵ نفر','بیشتر از ۵ نفر','یادم نیست']},
  {id:'q12a',section:'راه ارتباط و خدمات',title:'اگر قرار باشد در آینده از پیجت درآمد داشته باشی، بیشتر به کدام گزینه فکر می‌کنی؟',options:['دوره یا کلاس','جلسهٔ خصوصی','ارائهٔ خدمت','فروش محصول','هنوز نمی‌دانم']},
  {id:'q15',section:'نتیجهٔ تو',title:'دوست داری در نتیجهٔ این ارزیابی، اول دربارهٔ کدام بخش به تو کمک کنیم؟',optional:true,options:['بهتر معرفی کردن موضوع پیجم','پیدا کردن ایده و برنامهٔ محتوا','جلب اعتماد بیشتر','گرفتن درخواست و فروش بیشتر','ساختن مسیر کلی پیجم','هنوز مطمئن نیستم']}
];
let assessmentResult = null;
let assessmentSessionToken = '';
let reportLeadStatus = 'unchecked';
let reportLeadError = '';
let reportLeadRequest = 0;
let analysisSucceededAt = 0;
let assessmentAnswers = {};
let assessmentStep = 0;
let assessmentPending = false;
let assessmentError = '';
let assessmentRequestId = 0;
let assessmentConsultation = null;
let assessmentConsultationLoading = false;
let assessmentConsultationError = '';
let consultationSubmitting = false;
let consultationBookingOpen = false;
const assessmentStorageKey = 'brandyar-assessment-session-v1';
function validBrandReport(value) {
  const text = value => typeof value === 'string' && value.length > 0 && value.length <= 600;
  const list = (value, min, max) => Array.isArray(value) && value.length >= min && value.length <= max && value.every(text);
  return value && text(value.summary) && ['positioning','content','trust'].every(key => value[key] && text(value[key].status) && text(value[key].insight)) && list(value.strengths,1,5) && list(value.growth_opportunities,1,5) && list(value.questions_to_refine,0,5) && Array.isArray(value.priority_actions) && value.priority_actions.length === 3 && value.priority_actions.every(item => item && ['title','description','why_it_matters'].every(key => text(item[key]))) && value.this_week_action && text(value.this_week_action.title) && text(value.this_week_action.description) && text(value.disclaimer);
}
try {
  const saved = JSON.parse(sessionStorage.getItem(assessmentStorageKey));
  if (saved && saved.answers && typeof saved.answers === 'object' && !Array.isArray(saved.answers) && Date.now() - saved.at >= 0 && Date.now() - saved.at < 3600000) {
    assessmentAnswers = saved.answers;
    assessmentResult = validBrandReport(saved.report) ? saved.report : null;
    assessmentSessionToken = typeof saved.sessionToken === 'string' && /^[0-9a-f]{64}$/.test(saved.sessionToken) ? saved.sessionToken : '';
  }
} catch {}
function saveAssessmentSession() {
  try { sessionStorage.setItem(assessmentStorageKey, JSON.stringify({answers:assessmentAnswers,report:assessmentResult,sessionToken:assessmentSessionToken,at:Date.now()})); } catch {}
}
async function submitBrandAnalysis() {
  if (assessmentPending) return;
  const requestId = ++assessmentRequestId;
  assessmentPending = true;
  assessmentError = '';
  assessmentResult = null;
  assessmentSessionToken = '';
  analysisSucceededAt = 0;
  reportLeadStatus = 'unchecked';
  reportLeadRequest++;
  reportLeadError = '';
  reportRequestedAxis = '';
  reportWeekSteps = [false, false, false];
  saveAssessmentSession();
  if (location.hash === '#/report') route(); else location.hash = '#/report';
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 135000);
  try {
    if (location.protocol !== 'https:') throw new Error('برای ارسال پاسخ‌ها، اتصال امن سایت باید فعال باشد. پاسخ‌های شما حفظ شده‌اند.');
    const statusResponse = await fetch('/api/assessment/status', {credentials:'same-origin',signal:controller.signal,cache:'no-store'});
    const status = await statusResponse.json();
    if (!statusResponse.ok || !status.ready) throw new Error(status.error || 'تحلیل هوشمند هنوز فعال نشده است. پاسخ‌های شما حفظ شده‌اند.');
    if (requestId !== assessmentRequestId) return;
    const response = await fetch('/api/assessment/analyze', {method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({answers:assessmentAnswers,consent:true}),signal:controller.signal});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'تحلیل الان کامل نشد. لطفاً دوباره تلاش کن.');
    if (!validBrandReport(data.report)) throw new Error('گزارش معتبر دریافت نشد. لطفاً دوباره تلاش کن.');
    if (typeof data.session_id !== 'string' || !/^[0-9a-f]{64}$/.test(data.session_id)) throw new Error('نشست ارزیابی معتبر نیست. دوباره تلاش کن.');
    if (requestId !== assessmentRequestId) return;
    assessmentResult = data.report;
    assessmentSessionToken = data.session_id;
    analysisSucceededAt = Date.now();
    const storageController = new AbortController();
    const storageTimer = setTimeout(() => storageController.abort(), 15000);
    fetch('/api/assessments', {method:'POST',credentials:'same-origin',cache:'no-store',signal:storageController.signal,headers:{'Content-Type':'application/json','X-Nesharo-Assessment-Session':assessmentSessionToken},body:JSON.stringify({session_id:'current',answers:assessmentAnswers,insight:data.report})}).catch(() => {}).finally(() => clearTimeout(storageTimer));
  } catch (error) {
    if (requestId === assessmentRequestId) assessmentError = ['SyntaxError','TypeError','AbortError'].includes(error.name) ? 'تحلیل الان کامل نشد. لطفاً دوباره تلاش کن.' : error.message;
  } finally {
    clearTimeout(timer);
    if (requestId === assessmentRequestId) {
      assessmentPending = false;
      saveAssessmentSession();
      if (location.hash === '#/report') {
        route();
        const heading = document.querySelector('#main h1');
        heading?.setAttribute('tabindex','-1');
        heading?.focus({preventScroll:true});
      }
    }
  }
}
function offersService(answers){return Array.isArray(answers.q11)&&answers.q11.some(v=>['کلاس یا دورهٔ آموزشی','جلسه یا مشاورهٔ خصوصی','انجام یک خدمت','محصول دیجیتال یا فیزیکی'].includes(v))}
function assessmentFlow(){const noSale=Array.isArray(assessmentAnswers.q11)&&!offersService(assessmentAnswers);return assessmentQuestions.filter(q=>noSale?!['q12','q13','q14'].includes(q.id):q.id!=='q12a')}
function assessmentStepMarkup(){const flow=assessmentFlow(),question=flow[assessmentStep]||flow[flow.length-1],saved=assessmentAnswers[question.id],count=flow.length;return `<div class="assessment-progress"><span>${question.section} · سؤال ${assessmentStep+1} از ${count}</span><progress max="${count}" value="${assessmentStep+1}">${assessmentStep+1} از ${count}</progress></div><form id="assessment-step-form" class="panel assessment-question"><h2 id="assessment-label">${question.title}</h2>${question.hint?`<p>${question.hint}</p>`:''}${question.type==='text'||question.type==='textarea'?`<label class="sr-only" for="assessment-answer">${question.title}</label>${question.type==='textarea'?`<textarea id="assessment-answer" name="answer" rows="4" maxlength="500" ${question.optional?'':'required'}>${esc(typeof saved==='string'?saved:'')}</textarea>`:`<input id="assessment-answer" name="answer" type="text" maxlength="160" value="${esc(typeof saved==='string'&&saved!==question.skip?saved:'')}" ${question.optional||saved===question.skip?'':'required'}>`}${question.skip?`<label class="check-control"><input type="checkbox" name="skip" ${saved===question.skip?'checked':''}> ${question.skip}</label>`:''}`:`<div class="assessment-choices" role="group" aria-labelledby="assessment-label">${question.options.map((option,index)=>`<label><input type="${question.type==='multi'?'checkbox':'radio'}" name="answer" value="${index}" ${question.type==='multi'?(Array.isArray(saved)&&saved.includes(option)?'checked':''):(saved===option?'checked':'')}> ${option}</label>`).join('')}</div>${question.extra?`<label class="field" for="assessment-extra">${question.extra}<input id="assessment-extra" name="extra" maxlength="120" value="${esc(assessmentAnswers.q2extra||'')}"></label>`:''}`}${question.optional?'<p>این سؤال اختیاری است؛ می‌توانی بدون انتخاب ادامه بدهی.</p>':''}${assessmentStep===count-1?'<p class="assessment-processing-note">پاسخ‌های شما برای آماده‌سازی گزارش برند پردازش می‌شوند. این تحلیل بر اساس اطلاعاتی است که خودتان وارد کرده‌اید.</p><p class="hint">برای حفظ حریم خصوصی، فقط گزینه‌های انتخابی به متیس فرستاده می‌شوند؛ متن آزاد، بیو و اطلاعات تماس به این سرویس ارسال نمی‌شوند. پاسخ‌ها و گزارش پس از ثبت قابل بازیابی‌اند. <a href="#/privacy">حریم خصوصی</a></p><label class="check-control"><input type="checkbox" name="analysis-consent" required> با پردازش گزینه‌های انتخابی برای تولید گزارش موافقم.</label>':''}<div class="form-feedback" id="assessment-feedback" role="status" aria-live="polite"></div><div class="card-actions">${assessmentStep?'<button class="btn btn-outline" type="button" id="assessment-prev">سؤال قبل</button>':''}<button class="btn btn-accent" type="submit">${assessmentStep===count-1?'دیدن گزارش':'سؤال بعد'} ${icon('arrow')}</button></div></form>`}
function updateAssessment(){const stage=document.getElementById('assessment-stage');if(stage){stage.innerHTML=assessmentStepMarkup();stage.querySelector('input:not([type=checkbox]):not([type=radio]),textarea,input[type=radio]:checked,input[type=checkbox]:checked')?.focus()}}
function assessmentPage(){return `${pageHero('ارزیابی رایگان پیج','چند سؤال ساده، یک قدم روشن‌تر','چند سؤال ساده دربارهٔ پیج و کارهایی که این روزها انجام می‌دهی می‌پرسیم. جواب درست و غلط وجود ندارد؛ اگر کاری را هنوز انجام نداده‌ای، همان جواب به ما کمک می‌کند قدم بعدی مناسب‌تری پیشنهاد بدهیم. این نتیجهٔ اولیه فقط بر اساس پاسخ‌های تو ساخته می‌شود و پیجت به‌صورت خودکار بررسی نمی‌شود.')}<section class="section"><div class="container assessment-layout"><div class="notice">حدود ۵ تا ۷ دقیقه · بدون ثبت‌نام یا اتصال به اینستاگرام · تحلیل با رضایت شما و پس از فعال‌سازی سرویس انجام می‌شود؛ پیش از ارسال، شیوهٔ پردازش را می‌بینی.</div><div id="assessment-stage">${assessmentStepMarkup()}</div></div></section>`}
function consultationDate(value) {
  if (value.startsAt == null) return 'زمان جلسه با تماس هماهنگ می‌شود';
  return new Intl.DateTimeFormat('fa-IR-u-ca-persian', {dateStyle:'full', timeStyle:'short', timeZone:value.timeZone}).format(new Date(value.startsAt * 1000));
}
function updateConsultation() {
  const host = document.getElementById('report-consultation');
  if (!host || !validBrandReport(assessmentResult)) return;
  host.innerHTML = consultationMarkup();
  const card = host.querySelector('.panel');
  card?.classList.add('motion-item');
  requestAnimationFrame(() => card?.classList.add('is-visible'));
  host.querySelector('h2')?.focus({preventScroll:true});
}
async function loadConsultation() {
  if (assessmentConsultationLoading || consultationSubmitting || !validBrandReport(assessmentResult)) return;
  assessmentConsultationLoading = true;
  assessmentConsultationError = '';
  updateConsultation();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch('/api/assessment/consultation', {credentials:'same-origin', cache:'no-store', signal:controller.signal});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'اطلاعات مشاوره در دسترس نیست.');
    assessmentConsultation = data;
    consultationBookingOpen = false;
  } catch (error) {
    assessmentConsultationError = ['TypeError','SyntaxError','AbortError'].includes(error.name) ? 'دریافت وضعیت انجام نشد. لطفاً دوباره تلاش کن.' : error.message;
  } finally {
    clearTimeout(timer);
    assessmentConsultationLoading = false;
    updateConsultation();
  }
}
function consultationMarkup() {
  const heading = '<h2 tabindex="-1">دربارهٔ گزارش برندت با هم صحبت کنیم</h2>';
  if (assessmentConsultationLoading) return `<article class="panel consultation-invite" aria-busy="true">${heading}<p role="status">در حال دریافت وضعیت درخواست…</p></article>`;
  if (assessmentConsultationError) return `<article class="panel consultation-invite">${heading}<p class="error" role="alert">${esc(assessmentConsultationError)}</p><button class="btn btn-outline" type="button" id="consultation-open">تلاش دوباره</button></article>`;
  if (assessmentConsultation?.request && !consultationBookingOpen) {
    const request = assessmentConsultation.request;
    return `<article class="panel consultation-invite"><h2 tabindex="-1">وضعیت درخواست مشاوره</h2><p role="status">${esc(request.status)} · ${esc(consultationDate(request))}</p>${request.state==='pending'?`<p>${request.startsAt == null?'شماره‌ات ثبت شد. برای هماهنگی زمان جلسهٔ مشاوره با تو تماس می‌گیریم.':'درخواستت ثبت شد. بعد از تأیید زمان، برای هماهنگی با تو تماس می‌گیریم. این زمان هنوز قطعی نیست.'}</p>`:''}<p class="hint">شمارهٔ تماس فقط برای هماهنگی مشاوره استفاده می‌شود.</p><div class="card-actions"><button class="btn btn-outline" type="button" id="consultation-open">به‌روزرسانی وضعیت</button>${['cancelled','completed'].includes(request.state)?'<button class="btn btn-outline" type="button" id="consultation-new">درخواست جدید</button>':''}</div></article>`;
  }
  return `<article class="panel consultation-invite">${heading}<p>نتیجهٔ تست، شروع مسیر رشد برند توست. در یک جلسهٔ مشاوره می‌توانیم گزارش و قدم‌های بعدی را با هم بررسی کنیم. شماره‌ات را ثبت کن تا برای هماهنگی زمان جلسه با تو تماس بگیریم.</p><form id="consultation-form"><div class="field"><label for="consultation-name">نام (اختیاری)</label><input id="consultation-name" name="name" maxlength="120" autocomplete="name"></div><div class="field"><label for="consultation-phone">شمارهٔ موبایل برای هماهنگی جلسه</label><input id="consultation-phone" name="phone" type="tel" inputmode="tel" maxlength="32" autocomplete="tel" dir="ltr" required aria-describedby="consultation-privacy"></div><div class="field"><label for="consultation-notes">توضیح کوتاه (اختیاری؛ حداکثر ۲۰۰ نویسه)</label><textarea id="consultation-notes" name="notes" maxlength="200" rows="3"></textarea></div><p class="hint" id="consultation-privacy">شمارهٔ تماس فقط برای هماهنگی مشاوره در سرور ذخیره می‌شود و به هوش مصنوعی یا سرویس تحلیلی ارسال نمی‌شود. زمان جلسه پس از تماس و هماهنگی مشخص می‌شود. <a href="#/privacy">حریم خصوصی</a></p><div class="form-feedback" id="consultation-feedback" role="status" aria-live="polite"></div><div class="card-actions"><button class="btn btn-outline" type="submit" ${consultationSubmitting?'disabled':''}>ثبت شماره برای هماهنگی مشاوره</button><button class="btn btn-outline" type="button" id="consultation-open">پیگیری درخواست قبلی</button></div></form></article>`;
}
async function submitConsultation(form) {
  if (consultationSubmitting) return;
  consultationSubmitting = true;
  const button = form.querySelector('[type="submit"]');
  const feedback = form.querySelector('#consultation-feedback');
  button.disabled = true;
  form.setAttribute('aria-busy','true');
  feedback.textContent = 'در حال ثبت درخواست…';
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const values = new FormData(form);
    const response = await fetch('/api/assessment/consultation', {method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'}, signal:controller.signal, body:JSON.stringify({name:String(values.get('name')||''), phone:String(values.get('phone')||''), slotId:null, notes:String(values.get('notes')||'')})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'ثبت درخواست انجام نشد.');
    assessmentConsultation = {request:data.request, slots:[]};
    assessmentConsultationError = '';
    consultationBookingOpen = false;
    updateConsultation();
  } catch (error) {
    feedback.textContent = ['TypeError','SyntaxError','AbortError'].includes(error.name) ? 'پاسخ ثبت دریافت نشد. برای بررسی وضعیت، زمان‌ها را به‌روزرسانی کن یا دوباره تلاش کن.' : error.message;
  } finally {
    clearTimeout(timer);
    consultationSubmitting = false;
    button.disabled = false;
    form.setAttribute('aria-busy','false');
  }
}
function reportViewData() {
  const report = assessmentResult;
  const hasProduct = offersService(assessmentAnswers);
  return {
    brand_positioning_summary: report.summary,
    primary_strength: report.strengths[0],
    primary_growth_opportunity: report.growth_opportunities[0],
    weekly_action: report.this_week_action,
    recommended_pillars: report.priority_actions,
    content_direction: report.content.insight,
    current_stage: assessmentAnswers.q11 ? (hasProduct ? 'دارای محصول یا خدمت' : 'در مسیر ساخت پیشنهاد') : 'وضعیت عرضه مشخص نشده است',
    has_product_or_service: hasProduct,
    recommended_next_step: hasProduct ? 'در فضای کاری، پیام محتوایت را به مسئله‌ای وصل کن که محصول یا خدمتت حل می‌کند.' : 'در فضای کاری، ابتدا مسئلهٔ مخاطب و موضوعی را روشن کن که می‌خواهی با آن شناخته شوی.',
    lead_submission_status: reportLeadStatus
  };
}
async function requestReportLead(form = null) {
  if (['checking','submitting'].includes(reportLeadStatus)) return;
  const feedback = form?.querySelector('#report-lead-feedback');
  const input = form?.querySelector('[name="phone"]');
  const button = form?.querySelector('[type="submit"]');
  let phone = '';
  if (form) {
    phone = String(new FormData(form).get('phone') || '').trim().replace(/[۰-۹]/g, d => String('۰۱۲۳۴۵۶۷۸۹'.indexOf(d))).replace(/[٠-٩]/g, d => String('٠١٢٣٤٥٦٧٨٩'.indexOf(d))).replace(/[ -]/g, '').replace(/^(?:\+98|98)/, '0');
    if (!/^09[0-9]{9}$/.test(phone)) {
      feedback.textContent = 'شماره موبایل را به‌درستی وارد کن.';
      input?.setAttribute('aria-invalid','true');
      input?.focus();
      return;
    }
    input?.setAttribute('aria-invalid','false');
    button.disabled = true;
    button.textContent = 'در حال ثبت اطلاعات…';
    form.setAttribute('aria-busy','true');
    feedback.textContent = '';
  }
  const requestId = ++reportLeadRequest;
  reportLeadStatus = form ? 'submitting' : 'checking';
  reportLeadError = '';
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const headers = {'Content-Type':'application/json'};
    if (assessmentSessionToken) headers['X-Nesharo-Assessment-Session'] = assessmentSessionToken;
    if (Date.now() - analysisSucceededAt < 180000) headers['X-Nesharo-Supabase-Grace'] = String(Math.ceil((Date.now() - analysisSucceededAt) / 1000));
    const response = await fetch('/api/assessment/lead', {method:form?'POST':'GET',credentials:'same-origin',cache:'no-store',signal:controller.signal,...(form?{headers,body:JSON.stringify({phone,consent:true})}:{headers})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'تأیید ثبت دریافت نشد. دوباره تلاش کن.');
    if (typeof data.registered !== 'boolean' || (form && !data.registered)) throw new Error('تأیید ثبت دریافت نشد. دوباره تلاش کن.');
    if (requestId !== reportLeadRequest) return;
    reportLeadStatus = data.registered ? 'registered' : 'idle';
    if (!form || data.registered) {
      if (location.hash === '#/report') route();
      if (form && location.hash === '#/report') {
        focusReportSection(reportRequestedAxis ? `report-axis-${reportRequestedAxis}` : 'report-full');
        reportRequestedAxis = '';
      }
    }
  } catch (error) {
    if (requestId !== reportLeadRequest) return;
    reportLeadStatus = 'error';
    reportLeadError = ['TypeError','SyntaxError','AbortError'].includes(error.name) ? (form ? 'تأیید ثبت دریافت نشد. شماره‌ات حفظ شده؛ دوباره تلاش کن.' : 'بررسی دسترسی گزارش انجام نشد. می‌توانی دوباره با ثبت شماره تلاش کنی.') : error.message;
    if (feedback) feedback.textContent = reportLeadError;
    else if (location.hash === '#/report') route();
  } finally {
    clearTimeout(timer);
    if (button) {button.disabled=false;button.textContent='ثبت شماره برای پیگیری';form.setAttribute('aria-busy','false');}
  }
}
let reportRequestedAxis = '';
let reportWeekSteps = [false, false, false];
function reportExcerpt(text, maximum = 140) {
  if (text.length <= maximum) return text;
  const sentence = text.match(/^.*?[.!؟](?:\s|$)/u)?.[0]?.trim();
  if (sentence && sentence.length <= maximum) return sentence;
  const words = text.slice(0, maximum).replace(/\s+\S*$/, '').trim();
  return `${words}…`;
}
function reportAxisStatus(status) {
  return /[0-9۰-۹٠-٩%٪]|نمره|درصد|امتیاز|رتبه/.test(status) ? 'نیازمند بررسی بیشتر' : status;
}
function reportAxisArt(key) {
  return `<span class="report-art report-art--${key}" aria-hidden="true"><i></i><i></i><i></i><b></b></span>`;
}
function reportDisclosure(id, label, content) {
  return `<details class="report-disclosure" id="${id}"><summary><span class="report-disclosure-closed">${label}</span><span class="report-disclosure-open">بستن تحلیل</span>${icon('chevron')}</summary><div class="report-disclosure-body">${content}</div></details>`;
}
function reportAxes() {
  return [
    {key:'positioning', title:'جایگاه تخصصی', icon:'target', question:'برای چه چیزی می‌خواهی در ذهن مخاطب بمانی؟', label:'یک مشاهدهٔ عملی', observation:assessmentResult.positioning.insight, suggestion:'یک جمله بنویس: به چه کسی، برای حل کدام مسئله و با چه تخصصی کمک می‌کنی؟', example:'الگوی معرفی: «به [مخاطب مشخص] کمک می‌کنم [مسئلهٔ مشخص] را با [تخصص و تجربهٔ من] حل کند.»'},
    {key:'content', title:'محتوای متمایز', icon:'book', question:'چه نگاهی را فقط تو می‌توانی به این موضوع اضافه کنی؟', label:'یک الگوی پیشنهادی محتوا', observation:'تخصص + تجربهٔ واقعی + برداشت شخصی؛ یک موضوع را با این سه لایه روایت کن.', suggestion:'یک تجربه را انتخاب کن و بگو چه اتفاقی افتاد، چه آموختی و مخاطب چه استفاده‌ای می‌تواند بکند.', example:'مثال اجرایی: «در یک پروژه با این مسئله روبه‌رو شدم؛ این تصمیم را گرفتم و این نکته را یاد گرفتم.»'},
    {key:'trust', title:'اعتماد مخاطب', icon:'shield', question:'چگونه می‌توانی با تداوم و شفافیت، قابل‌اعتمادتر شوی؟', label:'یک رفتار برای اعتمادسازی', observation:'در محتوای بعدی، یک تجربهٔ مشخص را با آموخته و محدودیت‌هایش به اشتراک بگذار.', suggestion:'پرسش‌های مخاطبت را پیگیری کن و نشان بده کجا تجربهٔ مستقیم داری و کجا هنوز در حال یادگیری هستی.', example:'معیار کیفی پیگیری: آیا پرسش‌های مخاطب مشخص‌تر می‌شوند و برای ادامهٔ همان موضوع به تو برمی‌گردد؟'}
  ];
}
function focusReportSection(id) {
  const target = document.getElementById(id);
  target?.scrollIntoView({behavior:'auto', block:'start'});
  target?.focus({preventScroll:true});
}
function reportPage() {
  const actions = `<div class="card-actions report-tools"><a href="/personal-brand" class="btn btn-outline" id="assessment-edit">اصلاح پاسخ‌ها</a><button class="btn btn-outline" type="button" id="assessment-clear">پاک‌کردن پاسخ‌ها</button></div>`;
  if (assessmentPending) return `<section class="section"><div class="container assessment-layout"><article class="panel" aria-busy="true"><h1>در حال آماده‌سازی تصویر برند تو</h1><p role="status">پاسخ‌هایت برای آماده‌سازی گزارش بررسی می‌شوند.</p><div class="skeleton" aria-hidden="true"></div><button class="btn btn-dark" disabled>در حال آماده‌سازی…</button></article></div></section>`;
  if (!validBrandReport(assessmentResult)) return `<section class="section"><div class="container assessment-layout"><h1>مسیر برند شخصی تو از اینجا شروع می‌شود</h1><p role="status">${esc(assessmentError || (Object.keys(assessmentAnswers).length ? 'برای ساخت گزارش، پاسخ‌های ارزیابی را کامل و مرور کن. هنوز نتیجهٔ کافی در دسترس نیست.' : 'برای دیدن تصویر اولیهٔ برندت، ابتدا ارزیابی را انجام بده.'))}</p>${Object.keys(assessmentAnswers).length?`<button class="btn btn-outline" id="assessment-retry">تلاش دوباره</button>${actions}`:'<a class="btn btn-accent" href="/personal-brand">شروع ارزیابی رایگان</a>'}</div></section>`;
  const data = reportViewData(), report = assessmentResult, axes = reportAxes();
  const list = items => `<ul class="report-text-list">${items.map(item => `<li>${esc(item)}</li>`).join('')}</ul>`;
  const map = `<section class="report-brand-map" aria-labelledby="report-map-title"><header class="report-section-heading"><span class="report-eyebrow">شناخت مسیر</span><h2 id="report-map-title">نقشهٔ فعلی برند شخصی تو</h2><p>سه بخش به‌هم‌پیوسته که مسیر دیده‌شدن تخصصت را شکل می‌دهند.</p></header><div class="report-map-nodes">${axes.map(axis => `<button class="report-map-node" type="button" data-report-axis="${axis.key}" aria-controls="report-axis-${axis.key}"><span class="report-node-icon">${icon(axis.icon)}</span><strong>${axis.title}</strong><span class="report-status">${esc(reportAxisStatus(report[axis.key].status))}</span><span class="report-node-copy">${esc(reportExcerpt(report[axis.key].insight, 94))}</span><span class="report-node-link">دیدن جزئیات این محور ${icon('arrow')}</span></button>`).join('')}</div></section>`;
  const preview = `<section class="report-preview" aria-labelledby="report-first-insight"><div class="report-first"><span class="report-eyebrow">اولین نگاه، بر پایهٔ پاسخ‌های تو</span><h2 id="report-first-insight">برداشت اولیه از مسیر تو</h2><p>${esc(reportExcerpt(data.brand_positioning_summary, 230))}</p>${data.brand_positioning_summary.length>230?reportDisclosure('report-summary-detail','بیشتر بخوان',`<p>${esc(data.brand_positioning_summary)}</p>`):''}</div><div class="report-preview-notes"><article class="report-bright-spot"><span class="report-insight-marker" aria-hidden="true">${icon('spark')}</span><div><h3>نقطهٔ روشن</h3><p>${esc(reportExcerpt(data.primary_strength))}</p></div></article><article class="report-growth-spot"><span class="report-insight-marker" aria-hidden="true">${icon('idea')}</span><div><h3>فرصت رشد</h3><p>${esc(reportExcerpt(data.primary_growth_opportunity))}</p></div></article></div></section>`;
  const lead = reportLeadStatus === 'registered' ? `<div class="report-unlocked-note" role="status">${icon('check')}<span>شماره‌ات برای پیگیری ثبت شد.</span></div>` : `<section class="report-unlock" id="report-unlock" aria-labelledby="report-unlock-title" tabindex="-1"><header><span class="report-eyebrow">ادامهٔ مسیر تو · اختیاری</span><h2 id="report-unlock-title">برای پیگیری مسیر برندت در ارتباط باشیم</h2><p>گزارش کامل در ادامه در دسترس است؛ ثبت شماره برای دیدن یا دانلود آن لازم نیست.</p><div class="report-form-context" aria-hidden="true">${icon('target')}<span></span>${icon('book')}<span></span>${icon('shield')}</div></header><form id="report-lead-form" novalidate aria-busy="${['checking','submitting'].includes(reportLeadStatus)}"><label for="report-lead-phone">شماره موبایل</label><input id="report-lead-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" maxlength="32" dir="ltr" placeholder="۰۹۱۲۱۲۳۴۵۶۷" aria-describedby="report-lead-help report-lead-feedback" required><p id="report-lead-help" class="hint">در صورت تمایل، شماره‌ات را برای پیگیری مسیر برندت در نشارو ثبت کن.</p><p id="report-lead-feedback" class="form-feedback" role="status" aria-live="polite">${esc(reportLeadError)}</p><button class="btn btn-accent" type="submit" ${['checking','submitting'].includes(reportLeadStatus)?'disabled':''}>${reportLeadStatus==='submitting'?'در حال ثبت اطلاعات…':'ثبت شماره برای پیگیری'}</button><p class="hint">با ثبت شماره، با نگهداری آن در سرور نشارو و پیگیری مسیر برندت موافقی؛ ثبت شماره، درخواست مشاوره نیست. <a href="#/privacy">حریم خصوصی</a></p></form></section>`;
  const full = `<section id="report-full" class="report-full" tabindex="-1" aria-labelledby="report-overview">
    <header class="report-section-heading"><span class="report-eyebrow">از تصویر کلی تا قدم بعدی</span><h2 id="report-overview">تصویر کلی برند شخصی تو</h2><p>گزارش تفصیلی سه‌محوره؛ هر محور را در یک نگاه ببین و برای بررسی بیشتر، تحلیل کامل همان بخش را باز کن.</p></header>
    <section class="report-reflection" aria-label="برداشت‌های کلیدی"><article><h2>نقطه‌ای که می‌توانی روی آن تکیه کنی</h2><p>${esc(data.primary_strength)}</p></article><article><h2>مهم‌ترین فرصت رشد تو</h2><p>${esc(data.primary_growth_opportunity)}</p></article></section>
    <div class="report-axis-modules">${axes.map(axis => `<article id="report-axis-${axis.key}" class="report-axis-module report-axis-module--${axis.key}" tabindex="-1" aria-labelledby="report-axis-title-${axis.key}"><div class="report-axis-visual">${reportAxisArt(axis.key)}<span class="report-status">${esc(reportAxisStatus(report[axis.key].status))}</span></div><div class="report-axis-copy"><header><h3 id="report-axis-title-${axis.key}">${axis.title}</h3><p class="report-axis-question">${axis.question}</p></header><p class="report-axis-glance">${esc(reportExcerpt(report[axis.key].insight))}</p><div class="report-practice"><strong>${axis.label}</strong><p>${esc(reportExcerpt(axis.observation, 180))}</p></div><div class="report-suggestion"><strong>پیشنهاد قابل اجرا</strong><p>${axis.suggestion}</p></div>${reportDisclosure(`report-analysis-${axis.key}`,'دیدن تحلیل کامل',`<h4>تحلیل بر پایهٔ پاسخ‌های تو</h4><p>${esc(report[axis.key].insight)}</p><h4>${axis.key==='trust'?'معیار کیفی پیگیری':'یک مثال برای اجرا'}</h4><p>${axis.example}</p>`)}</div></article>`).join('')}</div>
    <section class="report-complete-notes" aria-labelledby="report-notes-title"><h3 id="report-notes-title">نقاط اتکا و فرصت‌های مسیر تو</h3><p>همهٔ نکته‌های گزارش برای مرور دقیق‌تر در دسترس‌اند.</p>${reportDisclosure('report-supporting-analysis','دیدن تحلیل کامل',`<h4>نقاط قوت</h4>${list(report.strengths)}<h4>فرصت‌های رشد</h4>${list(report.growth_opportunities)}${report.questions_to_refine.length?`<h4>پرسش‌های تکمیلی</h4>${list(report.questions_to_refine)}`:''}<h4>مبنای تحلیل</h4><p>${esc(report.disclaimer)}</p>`)}</section>
    <section class="report-content-path" aria-labelledby="report-content-title"><header class="report-section-heading"><span class="report-eyebrow">تبدیل تجربه به محتوا</span><h2 id="report-content-title">مسیر پیشنهادی برای ساخت محتوا</h2></header><ol class="report-content-nodes">${[['تخصص','target','یک مسئله‌ای که بهتر از دیگران می‌فهمی'],['تجربه','book','یک اتفاق واقعی، اشتباه یا نتیجه از مسیر حرفه‌ای تو'],['اعتماد','shield','یک نکتهٔ عملی که مخاطب بتواند همین امروز استفاده کند']].map(([title,mark,example])=>`<li><span class="report-path-icon">${icon(mark)}</span><h3>${title}</h3><p>${example}</p></li>`).join('')}</ol>${reportDisclosure('report-priority-actions','دیدن پیشنهادهای اختصاصی گزارش',`<h3>سه اقدام اولویت‌دار تو</h3><ol class="report-action-list">${report.priority_actions.map(item=>`<li><h4>${esc(item.title)}</h4><p>${esc(item.description)}</p><p class="hint"><strong>چرا مهم است؟</strong> ${esc(item.why_it_matters)}</p></li>`).join('')}</ol>`)}</section>
    <section class="report-week" aria-labelledby="report-week-title"><div class="report-week-heading"><span class="report-step-label">گام ۱</span>${icon('calendar')}</div><h2 id="report-week-title">مأموریت تو در این هفته</h2><p class="report-week-mission">یک تجربهٔ واقعی از مسیر حرفه‌ای‌ات را به یک محتوای آموزشی کوتاه تبدیل کن.</p><div class="report-week-checklist" role="group" aria-label="مرحله‌های مأموریت این هفته">${['یک تجربهٔ واقعی انتخاب کن.','مسئله و آموختهٔ اصلی‌اش را بنویس.','آن را به یک محتوای کوتاه و کاربردی تبدیل کن.'].map((text,index)=>`<label><input type="checkbox" data-report-week-step="${index}" ${reportWeekSteps[index]?'checked':''}><span>${text}</span></label>`).join('')}</div>${reportDisclosure('report-week-personal','دیدن قدم اختصاصی گزارش تو',`<h3>${esc(report.this_week_action.title)}</h3><p>${esc(report.this_week_action.description)}</p>`)}<a href="#/app/studio" class="btn btn-accent">شروع ساخت محتوا ${icon('arrow')}</a></section>
    <section class="report-next" aria-labelledby="report-next-title"><h2 id="report-next-title">از تحلیل تا اقدام</h2><p>گزارش، فقط نقطهٔ شروع است. در نشارو می‌توانی پیام برندت را روشن‌تر کنی، مسیر محتوا بسازی و هر هفته یک گام مشخص برداری.</p><ol class="report-continuation" aria-label="مسیر ادامه در نشارو"><li>${icon('target')}<span>شناخت</span></li><li>${icon('calendar')}<span>برنامه‌ریزی</span></li><li>${icon('check')}<span>اجرا</span></li></ol><p>${esc(data.recommended_next_step)}</p><div class="card-actions"><a class="btn btn-accent" href="#/app/plan">ساخت مسیر محتوایی من</a><a class="btn btn-outline" href="#/app">بازگشت به فضای کاری</a></div></section><div class="report-download"><button class="btn btn-outline" type="button" id="assessment-download">ذخیرهٔ گزارش کامل</button></div>
  </section>`;
  return `<div class="report-experience" dir="rtl"><div class="container report-shell"><header class="report-hero"><div><span class="report-eyebrow">ارزیابی برند شخصی · بر پایهٔ پاسخ‌های تو</span><h1>تصویر اولیهٔ برند شخصی تو آماده است</h1><p>پاسخ‌هایت نشان می‌دهد کدام بخش از برندت روشن‌تر است و برای دیده‌شدن تخصصت، روی چه نقطه‌ای می‌توانی تمرکز کنی.</p></div><div class="report-hero-art" aria-hidden="true"><span class="report-orbit report-orbit--outer"></span><span class="report-orbit report-orbit--inner"></span><span class="report-orbit-core"></span><i></i><i></i><i></i><small>از شناخت تا اقدام</small></div></header>${map}${preview}${lead}${full}<p class="report-basis">این گزارش بر پایهٔ پاسخ‌های تو در ارزیابی ساخته شده است و نقطهٔ شروعی برای روشن‌ترکردن مسیر برند شخصی توست.</p>${actions}</div></div>`;
}
pages.assessment=assessmentPage;
pages.report=reportPage;
document.addEventListener('submit',event=>{if(event.target.id==='report-lead-form'){event.preventDefault();requestReportLead(event.target);return}if(event.target.id==='consultation-form'){event.preventDefault();submitConsultation(event.target);return}if(event.target.id!=='assessment-step-form')return;event.preventDefault();if(assessmentPending)return;const question=assessmentFlow()[assessmentStep],form=event.target,values=new FormData(form);let answer;if(question.type==='multi'){answer=values.getAll('answer').map(v=>question.options[Number(v)]);if(!answer.length||question.max&&answer.length>question.max){form.querySelector('#assessment-feedback').textContent=question.max?`حداکثر ${question.max} گزینه انتخاب کن.`:'یک گزینه انتخاب کن یا «هیچ‌کدام» را بزن.';return}}else if(question.type==='text'||question.type==='textarea'){answer=question.skip&&values.has('skip')?question.skip:String(values.get('answer')||'').trim();if(!answer&&!question.optional){form.querySelector('#assessment-feedback').textContent='می‌توانی یک پاسخ کوتاه بنویسی یا گزینهٔ کمکی را انتخاب کنی.';return}}else{answer=values.has('answer')?question.options[Number(values.get('answer'))]:'';if(!answer&&!question.optional){form.querySelector('#assessment-feedback').textContent='یک گزینه انتخاب کن تا ادامه بدهیم.';return}}assessmentAnswers[question.id]=answer||'';if(question.extra)assessmentAnswers.q2extra=String(values.get('extra')||'').trim();if(question.id==='q11'){if(!offersService(assessmentAnswers))for(const id of ['q12','q13','q14'])delete assessmentAnswers[id];else delete assessmentAnswers.q12a}if(assessmentStep===assessmentFlow().length-1){if(!values.has('analysis-consent')){form.querySelector('#assessment-feedback').textContent='برای آماده‌سازی گزارش، رضایت به پردازش گزینه‌ها لازم است.';return}submitBrandAnalysis();return}assessmentStep++;updateAssessment()});
document.addEventListener('change',event=>{const input=event.target;if(input.dataset.reportWeekStep){reportWeekSteps[Number(input.dataset.reportWeekStep)]=input.checked;return}const form=input.closest('#assessment-step-form');if(!form)return;const question=assessmentFlow()[assessmentStep];if(input.name==='skip'){const text=form.querySelector('#assessment-answer');text.disabled=input.checked;text.required=!input.checked;if(input.checked)text.value=''}if(question.type==='multi'&&input.name==='answer'&&question.none&&input.checked){const inputs=[...form.querySelectorAll('[name=answer]')];if(question.options[Number(input.value)]===question.none)inputs.forEach(other=>{if(other!==input)other.checked=false});else inputs[question.options.indexOf(question.none)].checked=false}if(question.max&&form.querySelectorAll('[name=answer]:checked').length>question.max){input.checked=false;form.querySelector('#assessment-feedback').textContent=`حداکثر ${question.max} گزینه انتخاب کن.`}else form.querySelector('#assessment-feedback').textContent=''});
document.addEventListener('click',event=>{
  if(event.target.id==='consultation-open') loadConsultation();
  else if(event.target.closest?.('[data-report-axis]')) {
    const node=event.target.closest('[data-report-axis]');
    reportRequestedAxis=node.dataset.reportAxis;
    focusReportSection(`report-axis-${reportRequestedAxis}`);
  }
  else if(event.target.closest?.('.report-disclosure summary')) { event.preventDefault(); const disclosure=event.target.closest('.report-disclosure'); disclosure.open=!disclosure.open; }
  else if(event.target.id==='consultation-new') {consultationBookingOpen=true;updateConsultation()}
  else if(event.target.id==='assessment-retry') submitBrandAnalysis();
  else if(event.target.id==='assessment-edit') {
    assessmentRequestId++;
    assessmentPending=false;
    assessmentError='';
    assessmentResult=null;
    reportLeadRequest++;
    reportLeadStatus='unchecked';
    reportLeadError='';
    assessmentStep=0;
    saveAssessmentSession();
  } else if(event.target.id==='assessment-prev') {
    assessmentStep=Math.max(0,assessmentStep-1);
    updateAssessment();
  } else if(event.target.id==='assessment-clear') {
    assessmentRequestId++;
    assessmentPending=false;
    assessmentError='';
    assessmentResult=null;
    reportLeadRequest++;
    reportLeadStatus='unchecked';
    reportLeadError='';
    assessmentAnswers={};
    assessmentStep=0;
    try { sessionStorage.removeItem(assessmentStorageKey); } catch {}
    location.hash='#/assessment';
    route();
  } else if(event.target.id==='assessment-download'&&validBrandReport(assessmentResult)) {
    const report=assessmentResult;
    const text=['گزارش نشارو',report.summary,...['positioning','content','trust'].map(key=>`${report[key].status}\n${report[key].insight}`),'نقاط قوت',...report.strengths,'فرصت‌های رشد',...report.growth_opportunities,'سه اقدام اولویت‌دار',...report.priority_actions.map(item=>`${item.title}\n${item.description}\n${item.why_it_matters}`),'قدم این هفته',report.this_week_action.title,report.this_week_action.description,...report.questions_to_refine,report.disclaimer].join('\n\n');
    const url=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'})),anchor=document.createElement('a');
    anchor.href=url;
    anchor.download='nesharo-report.txt';
    anchor.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
});
function closeSiteMenu(restoreFocus=false){const menu=document.getElementById('site-nav'),toggle=document.getElementById('menu-toggle');menu.classList.remove('open');toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-label','باز کردن منو');if(restoreFocus)toggle.focus()}
function route(){const path=location.hash.replace(/^#\/?/,'').split('?')[0].replace(/^\/+|\/+$/g,'');if(path==='assessment'){location.replace('/personal-brand');return;}const isApp=path==='app'||path.startsWith('app/');if(isApp){const destination={brand:'/brandyar/identity',studio:'/brandyar/create',plan:'/brandyar/calendar',roadmap:'/brandyar/roadmap',library:'/brandyar/library',settings:'/account',profile:'/account'}[path.split('/')[1]]||'/account';location.replace(destination);return;}document.body.classList.toggle('landing-mode',path==='');document.getElementById('site-shell').hidden=isApp;document.getElementById('app-shell').hidden=!isApp;closeSiteMenu();document.getElementById('main').innerHTML=pages[path]?pages[path]():(path.startsWith('features/')?pages['features']():`<div class="not-found"><h1>این صفحه پیدا نشد</h1><a href="#/" class="btn btn-dark">بازگشت به خانه</a></div>`);document.querySelectorAll('[data-link]').forEach(a=>{let active=a.dataset.link===(path||'home');a.classList.toggle('active',active);active?a.setAttribute('aria-current','page'):a.removeAttribute('aria-current')});document.title=`${({app:'نمای کلی',analysis:'تحلیل برند',ideas:'ایده‌های محتوا',roadmap:'نقشه راه',library:'کتابخانه محتوا',studio:'استودیوی سناریو',calendar:'تقویم محتوا',onboarding:'شروع کار','onboarding-review':'بازبینی برند',connection:'اتصال اینستاگرام',subscription:'اشتراک',contact:'تماس با ما','instagram-guide':'راهنمای اتصال اینستاگرام',loading:'در حال بارگذاری',terms:'قوانین استفاده',privacy:'حریم خصوصی',settings:'پروفایل و تنظیمات',features:'امکانات','features/brand-analysis':'تحلیل دقیق برند','features/content-ideas':'ایده‌هایی که به تو می‌آیند','features/growth-roadmap':'نقشه راه قابل اجرا','how-it-works':'نحوه کار',pricing:'تعرفه‌ها',faq:'سؤالات متداول',about:'درباره ما',login:'ورود',signup:'ثبت‌نام'})[path]||({features:'امکانات','features/brand-analysis':'تحلیل دقیق برند','features/content-ideas':'ایده‌هایی که به تو می‌آیند','features/growth-roadmap':'نقشه راه قابل اجرا'})[path]||'پرسونال برندت را آگاهانه بساز'} | نشارو`;window.scrollTo(0,0);setupMotion();setupHeroMotion()}
const themeToggle=document.getElementById('theme-toggle');
document.getElementById('footer-year').textContent=String(new Date().getFullYear());
function updateThemeButton(){const dark=document.documentElement.dataset.theme==='dark';themeToggle.setAttribute('aria-pressed',String(dark));themeToggle.setAttribute('aria-label',dark?'فعال‌کردن حالت روشن':'فعال‌کردن حالت تیره');themeToggle.querySelector('use').setAttribute('href',dark?'#sun':'#moon')}
updateThemeButton();
themeToggle.addEventListener('click',()=>{const next=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=next;try{localStorage.setItem('brandyar-theme',next)}catch{}updateThemeButton()});
document.getElementById('skip-link').addEventListener('click',e=>{e.preventDefault();document.getElementById(document.getElementById('app-shell').hidden?'main':'app-main').focus()});
document.getElementById('menu-toggle').addEventListener('click',()=>{const menu=document.getElementById('site-nav'),toggle=document.getElementById('menu-toggle');if(menu.classList.contains('open')){closeSiteMenu(true);return}menu.classList.add('open');toggle.setAttribute('aria-expanded','true');toggle.setAttribute('aria-label','بستن منو');menu.querySelector('a')?.focus()});document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.getElementById('site-nav').classList.contains('open'))closeSiteMenu(true)});document.addEventListener('click',e=>{const menu=document.getElementById('site-nav');if(!menu.classList.contains('open'))return;if(menu.contains(e.target)){if(e.target.closest('a')){closeSiteMenu();setTimeout(()=>document.getElementById(document.getElementById('app-shell').hidden?'main':'app-main').focus(),0)}return}if(!e.target.closest('#menu-toggle'))closeSiteMenu(true)});document.addEventListener('submit',async e=>{if(e.target.id!=='auth-form')return;e.preventDefault();const form=e.target,feedback=document.getElementById('form-feedback');if(location.hash.includes('signup')){feedback.textContent='ثبت‌نام هنوز فعال نیست؛ می‌توانی پیش‌نمایش داشبورد را ببینی.';return}const submit=form.querySelector('[type="submit"]');submit.disabled=true;feedback.textContent='در حال بررسی ورود...';try{const response=await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify({email:form.elements.namedItem('email').value,password:form.elements.namedItem('password').value})});form.elements.namedItem('password').value='';if(!response.ok){feedback.textContent='اطلاعات ورود معتبر نیست یا تلاش‌های زیادی انجام شده است.';return}const code=window.prompt('کد یک‌بارمصرف برنامه احراز هویت را وارد کنید:');if(!code){feedback.textContent='تأیید دومرحله‌ای تکمیل نشد.';return}const verified=await fetch('/api/auth/mfa/verify',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify({code})});if(!verified.ok){feedback.textContent='کد تأیید معتبر نیست یا مهلت آن گذشته است.';return}location.assign('/admin')}catch{feedback.textContent='سرویس ورود در دسترس نیست؛ پیش‌نمایش داشبورد همچنان قابل مشاهده است.'}finally{submit.disabled=false}});let headerScrollFrame=0;function updateHeaderScroll(){headerScrollFrame=0;document.body.classList.toggle('has-scrolled',window.scrollY>32)}window.addEventListener('scroll',()=>{if(!headerScrollFrame)headerScrollFrame=requestAnimationFrame(updateHeaderScroll)},{passive:true});updateHeaderScroll();window.addEventListener('hashchange',route);route();
function syncLandingSections() {
  const onHome = ['', '#', '#/'].includes(location.hash);
  document.querySelectorAll('#site-nav [data-home-section]').forEach(link => {
    if (!onHome) return;
    const rect = document.getElementById(link.dataset.homeSection)?.getBoundingClientRect();
    const active = Boolean(rect && rect.top <= 180 && rect.bottom > 180);
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current','location'); else link.removeAttribute('aria-current');
  });
  if (onHome) {
    const homeLink = document.querySelector('#site-nav [data-link="home"]');
    const active = !document.querySelector('#site-nav [aria-current="location"]');
    homeLink?.classList.toggle('active', active);
    if (active) homeLink?.setAttribute('aria-current','page'); else homeLink?.removeAttribute('aria-current');
  }
}
let landingScrollFrame = 0;
window.addEventListener('scroll', () => {
  if (landingScrollFrame) return;
  landingScrollFrame = requestAnimationFrame(() => {landingScrollFrame=0;syncLandingSections();});
}, {passive:true});
window.addEventListener('hashchange', syncLandingSections);
document.addEventListener('click', event => {
  const link = event.target.closest('[data-home-section]');
  if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  if (!['', '#', '#/'].includes(location.hash)) return;
  const section = document.getElementById(link.dataset.homeSection);
  if (!section) return;
  event.preventDefault();
  closeSiteMenu();
  section.setAttribute('tabindex','-1');
  section.focus({preventScroll:true});
  section.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
});
