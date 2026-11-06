import datetime


MENU = (
    ('home', '/#/', 'خانه'),
    ('assessment', '/personal-brand', 'ارزیابی رایگان'),
    ('features', '/#/features', 'امکانات'),
    ('how-it-works', '/#/how-it-works', 'چطور کار می‌کند؟'),
    ('pricing', '/#/pricing', 'تعرفه‌ها'),
    ('faq', '/#/faq', 'سؤالات متداول'),
)


def icon(name):
    paths = {
        'arrow': '<path d="M20 12H4m6-6-6 6 6 6"/>',
        'menu': '<path d="M4 6h16M4 12h16M4 18h16"/>',
        'moon': '<path d="M20 15A8 8 0 0 1 9 4a8 8 0 1 0 11 11Z"/>',
        'telegram': '<path d="m21 3-4 18-6-5-4 3 1-6-5-2Zm-13 10L21 3M11 16l10-13"/>',
        'instagram': '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17" cy="7" r=".6"/>',
        'youtube': '<rect x="2" y="5" width="20" height="14" rx="4"/><path d="m10 9 5 3-5 3Z"/>',
        'linkedin': '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 10v7m4 0v-7m0 3c0-4 6-4 6 0v4M7 7h.01"/>',
    }
    return f'<svg aria-hidden="true" viewBox="0 0 24 24">{paths[name]}</svg>'


def brand():
    return '<a class="logo" href="/#/" aria-label="نشارو، خانه"><img class="ribbon-wordmark" src="/landing-logo.png" alt="" width="1568" height="784"><span class="brand-wordmark">نشارو</span></a>'


def header(active=''):
    links = ''.join(
        f'<a href="{href}" data-link="{key}"'
        + (' class="active" aria-current="page"' if key == active else '')
        + f'>{label}</a>' for key, href, label in MENU
    )
    return (
        '<header class="site-header site-chrome"><div class="container header-inner">'
        + brand() + '<nav class="site-nav" id="site-nav" aria-label="منوی اصلی">' + links + '</nav>'
        + '<div class="header-actions"><button id="theme-toggle" type="button" class="theme-toggle" hidden aria-label="تغییر حالت نمایش" aria-pressed="true">'
        + icon('moon') + '</button><a class="landing-login" href="/account">ورود ' + icon('arrow') + '</a></div>'
        + '<button class="menu-toggle icon-button" id="menu-toggle" type="button" aria-label="باز کردن منو" aria-expanded="false" aria-controls="site-nav">'
        + icon('menu') + '</button></div></header>'
    )


def footer():
    groups = (
        ('محصول', (('/#/features', 'امکانات'), ('/#/pricing', 'قیمت‌گذاری'), ('/#/?section=landing-preview', 'دموی محصول'), (None, 'منابع یادگیری'))),
        ('شرکت', (('/#/about', 'درباره ما'), ('/#/contact', 'تماس با ما'), (None, 'فرصت‌های شغلی'), (None, 'وبلاگ'))),
        ('پشتیبانی', (('/#/faq', 'سوالات متداول'), ('/#/privacy', 'قوانین و حریم خصوصی'), ('/#/terms', 'شرایط استفاده'), ('/#/contact', 'پشتیبانی'))),
    )
    columns = ''.join(
        '<div class="footer-group"><strong>' + title + '</strong><nav aria-label="پیوندهای ' + title + '">'
        + ''.join(
            f'<a href="{href}"' + (' data-home-section="landing-preview"' if label == 'دموی محصول' else '') + f'>{label}</a>'
            if href else f'<span class="footer-unavailable" aria-disabled="true">{label}</span>'
            for href, label in links
        )
        + '</nav></div>' for title, links in groups
    )
    social = '<div class="footer-social" aria-label="شبکه‌های اجتماعی">' + ''.join(
        f'<span role="img" aria-label="{label}؛ نشانی تعریف نشده">{icon(key)}</span>'
        for key, label in (('telegram', 'تلگرام'), ('instagram', 'اینستاگرام'), ('youtube', 'یوتیوب'), ('linkedin', 'لینکدین'))
    ) + '</div>'
    return (
        '<footer class="site-footer site-chrome"><div class="container footer-main"><div class="footer-brand">'
        + brand() + '<p>همراه شما برای شناخت برند شخصی و ساخت محتوای هماهنگ با آن.</p>' + social + '</div>' + columns
        + '</div><div class="container landing-footer-bottom"><span>© <time id="footer-year">'
        + str(datetime.date.today().year) + '</time> نشارو. تمام حقوق محفوظ است.</span>'
        + '<nav aria-label="پیوندهای تکمیلی"><a href="/#/privacy">حریم خصوصی</a><a href="/#/terms">شرایط استفاده</a></nav></div></footer>'
    )


def render_document(body, path):
    if b'<!-- site-header -->' not in body:
        return body
    active = 'assessment' if path in ('/personal-brand', '/admin/personal-brand') else 'home' if path in ('/', '/index.html') else ''
    return body.replace(b'<!-- site-header -->', header(active).encode()).replace(b'<!-- site-footer -->', footer().encode())
