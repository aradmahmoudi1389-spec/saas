import personal_brand_model as model

VERSION = 'pb-test-15-v3'
RELEASED_ON = '2026-10-27'

CONTEXT = {
    'field': ('زمینهٔ کاری', 'clarity', 'شناخت زمینهٔ فعلی بدون فرض انتخاب نهایی مسیر.'),
    'goal': ('هدف ارزیابی', 'clarity', 'تفسیر گزارش در زمینهٔ هدف اعلام‌شده.'),
    'audience': ('مخاطب موردنظر', 'clarity', 'شناخت مخاطب بدون الزام به تعریف تخصصی آن.'),
    'showcase': ('توانایی مورد تأکید', 'introduction', 'شناخت چیزی که فرد مایل است نشان دهد.'),
    'situation': ('وضعیت فعلی', 'clarity', 'شناخت نقطهٔ شروع از تجربهٔ خود فرد.'),
    'trait': ('تصویر مطلوب', 'introduction', 'شناخت ویژگی موردنظر برای معرفی خود.'),
    'help': ('کمک قابل ارائه', 'introduction', 'شناخت نوع کمکی که مخاطب می‌تواند دریافت کند.'),
    'state': ('آگاهی از توانایی', 'clarity', 'شناخت مرحلهٔ فعلی توضیح و معرفی توانایی.'),
    'feeling': ('تجربهٔ مطلوب مخاطب', 'content', 'شناخت قصد ارتباطی محتوا و کار.'),
    'image.need': ('نیاز معرفی', 'introduction', 'شناخت اولویت فرد برای بهتر شناخته‌شدن.'),
    'proof': ('شواهد در دسترس', 'evidence', 'شناخت انواع شواهد بدون ترجیح سابقهٔ بزرگ.'),
    'experience': ('تجربهٔ قابل ارائه', 'evidence', 'ثبت اختیاری نمونهٔ تجربه بدون اثر مستقیم بر نمره.'),
    'need': ('نیاز شواهد', 'evidence', 'شناخت کمک موردنیاز برای ارائهٔ توانایی.'),
    'platform': ('محل حضور', 'visibility', 'شناخت فضای واقعی حضور بدون امتیازدهی به پلتفرم.'),
    'published': ('نوع محتوای فعلی', 'content', 'شناخت شکل محتوای منتشرشده.'),
    'clarity': ('وضوح ادراک‌شدهٔ صفحه', 'introduction', 'ثبت برداشت فرد از معرفی آنلاین بدون تأیید بیرونی.'),
}

BEHAVIOR_REASONS = [
    'سنجش توان توضیح سادهٔ کمک قابل ارائه.',
    'سنجش روشن‌بودن موضوع موردنظر برای شناخته‌شدن.',
    'سنجش شناخت افراد نیازمند تجربه یا توانایی.',
    'سنجش در دسترس بودن نمونهٔ دارای نتیجه.',
    'سنجش همراه‌کردن ادعا با مثال واقعی.',
    'سنجش ارتباط محتوای منتشرشده با کار.',
    'سنجش وضوح موضوع کار در محتوای قابل مشاهده.',
    'سنجش قابل‌توضیح‌بودن ادعاهای معرفی برای خود فرد.',
    'سنجش پیوستگی موضوع میان محتواهای اخیر.',
    'سنجش توجه به مخاطب مشخص هنگام انتشار.',
    'سنجش ادامه‌دادن معرفی و انتشار بدون انتظار بی‌نقص‌بودن.',
    'سنجش یادگیری از بازخوردهای واقعی.',
    'سنجش روشن‌بودن وجه قابل‌تشخیص در تجربه یا روش.',
    'سنجش روشن‌بودن راه ارتباط یا همکاری برای مخاطب.',
    'سنجش هماهنگی حضور آنلاین با تصویر مطلوب کاری.',
]


def catalog():
    template = model.template_v3()
    entries = []
    for section in ('base', 'image', 'evidence', 'online'):
        for key, title, *_ in template[section]:
            construct, dimension, rationale = CONTEXT['image.need' if section == 'image' and key == 'need' else key]
            entries.append({'id': section + '.' + key, 'title': title, 'construct': construct,
                            'dimension': dimension, 'rationale': rationale, 'scored': False})
    for question, rationale in zip(template['behavior'], BEHAVIOR_REASONS):
        entries.append({'id': question['id'], 'title': question['title'],
                        'construct': dict((key, title) for key, title, _ in model.V3_DIMENSIONS)[question['dimension']],
                        'dimension': question['dimension'], 'rationale': rationale, 'scored': True})
    return {'version': VERSION, 'released_on': RELEASED_ON,
            'validation_status': 'pending_empirical_study', 'questions': entries}
