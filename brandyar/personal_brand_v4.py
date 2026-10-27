import copy
import math
import secrets

from personal_brand_model import clean

TEMPLATE_ID = 'pb-test-month-v4'
MODEL_ID = 'pb-score-month-v4'
SCALE = ['هنوز برای من اتفاق نیفتاده', 'به‌ندرت اتفاق افتاده', 'گاهی اتفاق افتاده', 'در بیشتر مواقع اتفاق افتاده', 'تقریباً به یک روال تبدیل شده']
STAGES = ['شروع مسیر', 'در حال شکل‌گرفتن', 'قابل‌تشخیص', 'روبه‌رشد', 'جاافتاده و قابل‌اعتماد']
DISCLAIMER = 'این نتیجه، تصویری از وضعیت فعلی توست و فقط کمک می‌کند نقطهٔ شروع مناسب‌تری پیدا کنی.'
SECTIONS = [
    {'id': 'path', 'title': 'مسیر فعلی تو', 'description': 'اول می‌خواهیم بدانیم این روزها در چه مسیری هستی و از دیده‌شدن بیشتر چه نتیجه‌ای می‌خواهی. لازم نیست جواب‌ها رسمی یا کامل باشند؛ نزدیک‌ترین گزینه را انتخاب کن.'},
    {'id': 'image', 'title': 'تصویری که دوست داری ساخته شود', 'description': 'اینجا قرار نیست پاسخ حرفه‌ای یا نهایی بدهی. فقط می‌خواهیم ببینیم دوست داری دیگران بعد از آشنایی با تو، بیشتر چه چیزی را به یاد داشته باشند.'},
    {'id': 'behavior', 'title': 'رفتارهای واقعی در یک ماه اخیر', 'description': 'این بخش دربارهٔ رفتار این روزهای توست، نه تصویری که دوست داری از خودت بسازی. جواب نزدیک‌تر به واقعیت را انتخاب کن؛ حتی اگر هنوز در ابتدای مسیر هستی. اینجا پاسخ خوب یا بد وجود ندارد.'},
    {'id': 'evidence', 'title': 'چیزهایی که برای نشان‌دادن داری', 'description': 'اینجا فقط می‌خواهیم بدانیم چه چیزهایی برای معرفی توانایی‌هایت در اختیار داری. تجربه‌های کوچک هم ارزش نشان‌دادن دارند.'},
    {'id': 'online', 'title': 'حضور آنلاین فعلی', 'description': 'اگر هنوز فعالیت زیادی در فضای آنلاین نداری، کاملاً طبیعی است. فقط گزینه‌ای را انتخاب کن که به وضعیت امروزت نزدیک‌تر است.'},
]
BASE = [
    ('field', 'این روزها بیشتر در چه زمینه‌ای کار می‌کنی یا دوست داری با آن شناخته شوی؟', ['آموزش و تدریس', 'مشاوره و کوچینگ', 'فروش و کسب‌وکار', 'بازاریابی و تولید محتوا', 'طراحی و کارهای خلاقانه', 'فناوری و برنامه‌نویسی', 'پزشکی، سلامت یا ورزش', 'امور مالی یا حقوقی', 'منابع انسانی یا مدیریت', 'هنر و رسانه', 'دانشجویی یا شروع مسیر کاری', 'هنوز مطمئن نیستم', 'موضوع دیگری دارم']),
    ('primary_goal', 'اگر قرار باشد در چند ماه آینده یک نتیجه از دیده‌شدن بیشتر بگیری، کدام برایت مهم‌تر است؟', ['پیدا کردن مشتری یا پروژهٔ بیشتر', 'بهتر دیده‌شدن در حوزهٔ کاری', 'پیدا کردن شغل یا فرصت کاری بهتر', 'فروش محصول یا خدمات', 'معرفی بهتر توانایی‌هایم', 'شناخته‌شدن در یک موضوع مشخص', 'پیدا کردن همکار یا فرصت همکاری', 'فقط می‌خواهم بفهمم از کجا باید شروع کنم', 'هدف دیگری دارم']),
    ('audience', 'دوست داری بیشتر چه کسانی از کار و توانایی تو باخبر شوند؟', ['مشتریان یا خریداران احتمالی', 'مدیران و کارفرماها', 'همکاران حوزهٔ کاری', 'دانشجویان و علاقه‌مندان به یادگیری', 'صاحبان کسب‌وکار', 'مخاطبان عمومی', 'شریک یا همکار تجاری', 'هنوز دقیق نمی‌دانم', 'گروه دیگری مدنظرم است']),
    ('showcase_priority', 'اگر بخواهی یک چیز را بیشتر دربارهٔ خودت نشان بدهی، کدام برایت مهم‌تر است؟', ['دانشی که دارم', 'تجربه‌ای که به دست آورده‌ام', 'نتیجه‌ای که برای دیگران ایجاد کرده‌ام', 'سبک و نگاه متفاوت من', 'طرز فکر و نگاه من به کار', 'نمونه‌کارها و پروژه‌هایم', 'هنوز نمی‌دانم']),
    ('current_situation', 'کدام جمله بیشتر به وضعیت این روزهای تو نزدیک است؟', ['هنوز نمی‌دانم بهتر است خودم را با چه موضوعی معرفی کنم.', 'چند علاقه یا توانایی دارم و انتخاب یک مسیر برایم سخت است.', 'می‌دانم چه کاری انجام می‌دهم، اما دیگران آن را خوب نمی‌شناسند.', 'محتوا تولید می‌کنم، اما نمی‌دانم چه چیزی را بیشتر ادامه بدهم.', 'شروع می‌کنم، اما ادامه‌دادن برایم سخت می‌شود.', 'مخاطب یا ارتباط دارم، اما به فرصت کاری یا مشتری تبدیل نمی‌شود.', 'هنوز نمونه‌کار یا نتیجهٔ کافی برای نشان‌دادن ندارم.', 'فعلاً موضوع مشخصی ذهنم را درگیر نکرده است.', 'وضعیت دیگری دارم.']),
]
IMAGE = [
    ('desired_impression', 'دوست داری مردم بیشتر با کدام ویژگی تو را به یاد بیاورند؟', ['قابل‌اعتماد بودن', 'متخصص بودن', 'خلاق بودن', 'ساده و قابل‌فهم توضیح‌دادن', 'نتیجه‌گرا بودن', 'همراه و حمایتگر بودن', 'متفاوت فکرکردن', 'منظم و دقیق بودن', 'هنوز نمی‌دانم', 'ویژگی دیگری']),
    ('help_area', 'اگر کسی بخواهد از تو کمک بگیرد، احتمالاً برای چه موضوعی سراغت می‌آید؟', ['یادگیری یک مهارت یا موضوع', 'حل یک مسئلهٔ کاری', 'تصمیم‌گیری و انتخاب بهتر', 'انجام یک کار تخصصی', 'پیدا کردن ایده یا مسیر', 'رشد فروش یا کسب‌وکار', 'بهترشدن شرایط شخصی یا حرفه‌ای', 'هنوز کسی برای این موضوع سراغم نمی‌آید', 'مورد دیگری']),
    ('position_status', 'کدام جمله به وضعیت فعلی تو نزدیک‌تر است؟', ['هنوز دارم می‌فهمم در چه کاری قوی‌تر هستم.', 'چند توانایی دارم، اما نمی‌دانم کدام را بیشتر نشان بدهم.', 'می‌دانم در چه کاری خوبم، اما آن را روشن معرفی نکرده‌ام.', 'بعضی‌ها توانایی من را می‌شناسند، اما حضورم منظم نیست.', 'تا حدی شناخته شده‌ام و می‌خواهم حرفه‌ای‌تر دیده شوم.', 'نمی‌دانم کدام گزینه به من نزدیک‌تر است.']),
    ('desired_audience_feeling', 'دوست داری مخاطب بعد از دیدن کار یا محتوای تو چه حسی داشته باشد؟', ['احساس کند چیز تازه‌ای یاد گرفته است.', 'احساس کند می‌تواند به من اعتماد کند.', 'برای حل مسئله‌اش انگیزه بگیرد.', 'ایدهٔ تازه‌ای پیدا کند.', 'احساس کند مسئله‌اش را می‌فهمم.', 'برای همکاری یا خرید کنجکاو شود.', 'هنوز نمی‌دانم.']),
    ('needed_next_step', 'برای اینکه دیگران بهتر تو را بشناسند، بیشتر به کدام مورد نیاز داری؟', ['انتخاب یک موضوع روشن', 'توضیح بهتر دربارهٔ کاری که انجام می‌دهم', 'نشان‌دادن نمونه‌کار و نتیجه', 'تولید محتوای منظم‌تر', 'حضور بیشتر در فضای آنلاین', 'راحت‌تر معرفی‌کردن خودم', 'داشتن یک مسیر روشن برای ادامه', 'هنوز مطمئن نیستم']),
]
BEHAVIOR = [
    ('clarity_1', 'clarity', 'در یک ماه اخیر، وقتی کسی دربارهٔ کارم پرسیده، توانسته‌ام با یک توضیح کوتاه بگویم چه کمکی می‌کنم.'),
    ('clarity_2', 'clarity', 'در یک ماه اخیر، برای خودم تا حدی روشن بوده که دوست دارم با چه موضوعی شناخته شوم.'),
    ('clarity_3', 'clarity', 'در یک ماه اخیر، حدس نسبتاً روشنی داشته‌ام که چه کسانی بیشتر به تجربه یا توانایی من نیاز دارند.'),
    ('evidence_1', 'evidence', 'در یک ماه اخیر، دست‌کم یک نمونه، تجربه، پروژه یا نتیجه داشته‌ام که بتوانم برای معرفی کارم نشان بدهم.'),
    ('evidence_2', 'evidence', 'در یک ماه اخیر، وقتی دربارهٔ توانایی‌هایم حرف زده‌ام، توانسته‌ام یک مثال واقعی هم بگویم.'),
    ('evidence_3', 'evidence', 'در یک ماه اخیر، یک تجربه یا نتیجهٔ واقعی از کارم را با دیگران به اشتراک گذاشته‌ام.'),
    ('consistency_1', 'consistency', 'در یک ماه اخیر، بیشتر چیزهایی که منتشر کرده‌ام یا درباره‌شان صحبت کرده‌ام، با کار اصلی من ارتباط داشته‌اند.'),
    ('consistency_2', 'consistency', 'در یک ماه اخیر، اگر چند محتوای اخیرم را کنار هم بگذارم، بین آن‌ها یک موضوع مشترک دیده می‌شود.'),
    ('consistency_3', 'consistency', 'در یک ماه اخیر، معرفی من در صفحه‌ها یا شبکه‌های اجتماعی‌ام با کاری که واقعاً انجام می‌دهم هم‌خوان بوده است.'),
    ('execution_1', 'execution', 'در یک ماه اخیر، پیش از انتشار محتوا یا معرفی کارم، تا حدی می‌دانسته‌ام برای چه کسی آن را آماده می‌کنم.'),
    ('execution_2', 'execution', 'در یک ماه اخیر، حتی وقتی همه‌چیز کامل نبوده، توانسته‌ام معرفی کارم یا تولید محتوا را ادامه بدهم.'),
    ('execution_3', 'execution', 'در یک ماه اخیر، از سؤال‌ها، بازخوردها یا واکنش دیگران برای بهترکردن کارم استفاده کرده‌ام.'),
    ('differentiation_1', 'differentiation', 'در یک ماه اخیر، توانسته‌ام دست‌کم یک دلیل مشخص برای انتخاب خودم نسبت به افراد مشابه بیان کنم.'),
    ('conversion_1', 'differentiation', 'در یک ماه اخیر، کسی که صفحه یا محتوای من را دیده، توانسته بفهمد برای پرسیدن سؤال یا همکاری با من چه کاری باید انجام دهد.'),
    ('alignment_1', 'differentiation', 'در یک ماه اخیر، حضور آنلاین من تا حدی با تصویری که دوست دارم از کارم منتقل شود هماهنگ بوده است.'),
]
EVIDENCE = [
    ('available_proof', 'برای نشان‌دادن توانایی‌هایت، کدام موارد را در اختیار داری؟', ['نمونه‌کار', 'تجربهٔ کاری', 'نتیجه‌ای که برای خودم یا دیگری ایجاد کرده‌ام', 'نظر یا رضایت دیگران', 'مدرک یا گواهی', 'صفحه، محصول یا پروژه', 'هنوز چیز مشخصی ندارم', 'مورد دیگری']),
    ('proud_work', 'اگر دوست داری، یک کار، تجربه یا نتیجه را بنویس که مایل هستی دیگران بیشتر ببینند.', None),
    ('evidence_need', 'برای معرفی بهتر توانایی‌هایت، الان بیشتر به چه چیزی نیاز داری؟', ['ساخت نمونه‌کار', 'نشان‌دادن نتیجهٔ کار', 'توضیح روشن‌تر توانایی‌ها', 'مرتب‌کردن محتوای قبلی', 'پیدا کردن موضوع مناسب', 'گرفتن بازخورد', 'هنوز نمی‌دانم']),
]
ONLINE = [
    ('primary_channel', 'الان بیشتر در کدام فضا فعالیت می‌کنی؟', ['اینستاگرام', 'لینکدین', 'تلگرام', 'وب‌سایت شخصی', 'یوتیوب', 'چند فضای آنلاین', 'فعلاً حضور فعالی ندارم', 'جای دیگری']),
    ('content_type', 'اگر چیزی منتشر می‌کنی، بیشتر از چه نوعی است؟', ['آموزش', 'تجربه‌های شخصی یا کاری', 'معرفی خدمات یا محصول', 'نمونه‌کار', 'نظر و دیدگاه', 'محتوای سرگرم‌کننده', 'موضوع‌های متنوع و پراکنده', 'فعلاً چیزی منتشر نمی‌کنم']),
    ('profile_clarity', 'اگر فردی برای اولین‌بار صفحهٔ تو را ببیند، به‌نظر خودت چقدر می‌فهمد چه کاری انجام می‌دهی؟', ['هنوز قابل‌فهم نیست', 'کمی قابل‌فهم است', 'تا حدی قابل‌فهم است', 'بیشتر قابل‌فهم است', 'به‌خوبی قابل‌فهم است', 'مطمئن نیستم']),
]
DIMENSIONS = [
    ('clarity', 'روشن‌بودن مسیر'), ('evidence', 'شواهد و تجربه'),
    ('consistency', 'انسجام محتوا و معرفی'), ('execution', 'استمرار و ارتباط با مخاطب'),
    ('differentiation', 'تمایز و امکان اقدام'),
]
OTHER = {
    'field': 'موضوع دیگری دارم', 'primary_goal': 'هدف دیگری دارم',
    'audience': 'گروه دیگری مدنظرم است', 'current_situation': 'وضعیت دیگری دارم.',
    'desired_impression': 'ویژگی دیگری', 'help_area': 'مورد دیگری',
    'available_proof': 'مورد دیگری', 'primary_channel': 'جای دیگری',
}


def template():
    return copy.deepcopy({'schema': 4, 'title': 'ارزیابی پرسونال برند', 'version': 'v4',
                          'released_on': '2026-10-27', 'sections': SECTIONS,
                          'base': BASE, 'image': IMAGE, 'evidence': EVIDENCE, 'online': ONLINE,
                          'behavior': [{'id': key, 'dimension': dimension, 'title': title,
                                        'order': index, 'active': True, 'weight': 1}
                                       for index, (key, dimension, title) in enumerate(BEHAVIOR)],
                          'dimensions': [{'key': key, 'title': title} for key, title in DIMENSIONS],
                          'likert': SCALE, 'other': OTHER})


def model():
    return {'schema': 4, 'dimensions': {key: 0.2 for key, _ in DIMENSIONS},
            'thresholds': [20, 40, 60, 80], 'method': 'monthly-behavior-mean',
            'analysis_version': 'monthly-behavior-v4'}


def validate_template(body):
    import json
    if json.dumps(body, ensure_ascii=False, sort_keys=True) != json.dumps(template(), ensure_ascii=False, sort_keys=True):
        raise ValueError('سؤال‌ها و گزینه‌های این نسخه ثابت‌اند.')


def validate_model(body):
    if body != model():
        raise ValueError('در این نسخه میانگین پنج بخش با وزن یکسان محاسبه می‌شود.')


def validate(step, data, body, partial=False):
    if type(step) is not int or step not in range(1, 6) or not isinstance(data, dict):
        raise ValueError('پاسخ این بخش را بررسی کن.')
    if step == 3:
        ids = {question['id'] for question in body['behavior']}
        if (set(data) - ids or (not partial and set(data) != ids)
                or any(type(value) is not int or not 1 <= value <= 5 for value in data.values())):
            raise ValueError('برای هر سؤال یک گزینه انتخاب کن.')
        return dict(data)
    fields = body[{1: 'base', 2: 'image', 4: 'evidence', 5: 'online'}[step]]
    options = {key: choices for key, _, choices in fields}
    text_keys = {key + '_other' for key in options if key in OTHER}
    if step == 4:
        text_keys.add('proud_work')
    if set(data) - set(options) - text_keys - ({'choice'} if step == 5 else set()):
        raise ValueError('پاسخ این بخش را بررسی کن.')
    if step == 5 and data.get('choice', 'skip') != 'skip':
        raise ValueError('پاسخ این بخش را بررسی کن.')
    result = {}
    for key, choices in options.items():
        if choices is None:
            result[key] = clean(data.get(key, ''), 300)
            continue
        if partial and key not in data:
            continue
        value = data.get(key)
        if key in {'audience', 'available_proof'}:
            maximum = 2 if key == 'audience' else len(choices)
            if (not isinstance(value, list) or len(value) > maximum or (not partial and not value)
                    or any(not isinstance(item, str) or item not in choices for item in value)
                    or len(set(value)) != len(value)):
                raise ValueError('گزینه‌های انتخاب‌شده را بررسی کن.')
            if key == 'available_proof' and 'هنوز چیز مشخصی ندارم' in value and len(value) > 1:
                raise ValueError('اگر هنوز چیز مشخصی نداری، فقط همان گزینه را انتخاب کن.')
        elif not isinstance(value, str) or value not in choices:
            raise ValueError('برای هر سؤال یک گزینه انتخاب کن.')
        result[key] = value
    for key in text_keys - {'proud_work'}:
        source = key.removesuffix('_other')
        chosen = result.get(source)
        visible = OTHER[source] in chosen if isinstance(chosen, list) else chosen == OTHER[source]
        if visible and key in data:
            result[key] = clean(data[key], 200)
    return result


def question_order(body):
    rng = secrets.SystemRandom()
    groups = {key: [question['id'] for question in body['behavior'] if question['dimension'] == key] for key, _ in DIMENSIONS}
    for questions in groups.values():
        rng.shuffle(questions)
    order, previous = [], None
    for round_index in range(3):
        keys = list(groups)
        rng.shuffle(keys)
        if keys[0] == previous:
            keys[0], keys[1] = keys[1], keys[0]
        order.extend(groups[key][round_index] for key in keys)
        previous = keys[-1]
    return order


def score(answers, body, scoring):
    validate_model(scoring)
    values = {step: validate(step, answers[step], body) for step in range(1, 6)}
    dimensions, precise = [], []
    for key, title in DIMENSIONS:
        ids = [question['id'] for question in body['behavior'] if question['dimension'] == key]
        value = (sum(values[3][identity] for identity in ids) / len(ids) - 1) * 25
        precise.append(value)
        dimensions.append({'key': key, 'title': title, 'score': round(value, 2), 'evidence': ids})
    total = math.floor(sum(precise) / 5 + 0.5)
    stage = STAGES[sum(total > threshold for threshold in scoring['thresholds'])]
    low = min(range(5), key=lambda index: precise[index])
    high = max(range(5), key=lambda index: precise[index])
    if low == high:
        high = 4
    lowest, highest = dimensions[low], dimensions[high]
    strengths = {
        'clarity': 'در پاسخ‌هایت، روشن‌بودن موضوع کار و کسانی که می‌توانی به آن‌ها کمک کنی بیشتر دیده می‌شود.',
        'evidence': 'در پاسخ‌هایت، داشتن تجربه و مثال‌های واقعی برای نشان‌دادن توانایی‌ها بیشتر دیده می‌شود.',
        'consistency': 'در پاسخ‌هایت، ارتباط میان معرفی، موضوع محتوا و کاری که انجام می‌دهی بیشتر دیده می‌شود.',
        'execution': 'در پاسخ‌هایت، ادامه‌دادن حضور و استفاده از واکنش مخاطب بیشتر دیده می‌شود.',
        'differentiation': 'در پاسخ‌هایت، توضیح دلیل انتخاب تو و روشن‌بودن راه ارتباط بیشتر دیده می‌شود.',
    }
    growth = {
        'clarity': 'می‌توانی موضوعی را که می‌خواهی با آن شناخته شوی، برای خودت و دیگران روشن‌تر کنی.',
        'evidence': 'می‌توانی یک تجربه یا نتیجهٔ کوچک را برای نشان‌دادن توانایی‌هایت آماده کنی.',
        'consistency': 'می‌توانی ارتباط میان معرفی خودت و موضوع چیزهایی را که منتشر می‌کنی روشن‌تر کنی.',
        'execution': 'می‌توانی یک کار کوچک و قابل‌ادامه برای ارتباط با مخاطب انتخاب کنی.',
        'differentiation': 'می‌توانی یک دلیل مشخص برای انتخاب خودت و راه ساده‌ای برای ارتباط نشان بدهی.',
    }
    first, image, proof, online = values[1], values[2], values[4], values[5]
    field = first.get('field_other', '').strip() if first['field'] == OTHER['field'] else first['field']
    topic = field if field and field != 'هنوز مطمئن نیستم' else 'یکی از کارها یا علاقه‌هایت'
    audience = '، '.join(first['audience'])
    if 'هنوز دقیق نمی‌دانم' in first['audience']:
        audience = 'یک نفر که ممکن است به این کار نیاز داشته باشد'
    if OTHER['audience'] in first['audience']:
        audience = first.get('audience_other') or 'یک نفر از گروهی که مدنظر داری'
    actions = {
        'clarity': f'برای {topic}، یک جمله بنویس که بگوید چه کمکی به {audience} می‌کنی.',
        'evidence': f'از {topic} یک تجربهٔ کوچک را انتخاب کن و کار انجام‌شده و نتیجه‌اش را در دو جمله بنویس.',
        'consistency': f'معرفی خودت و سه محتوای اخیر دربارهٔ {topic} را کنار هم بگذار و یک موضوع مشترک انتخاب کن.',
        'execution': f'یک نکتهٔ کوتاه دربارهٔ {topic} برای {audience} آماده کن و از او یک سؤال بپرس.',
        'differentiation': f'یک دلیل مشخص برای انتخاب کارت در زمینهٔ {topic} بنویس و کنار آن راه پرسیدن سؤال را بگذار.',
    }
    action = actions[lowest['key']]
    no_proof = 'هنوز چیز مشخصی ندارم' in proof['available_proof']
    if no_proof:
        action += ' از یک تمرین کوچک شروع کن؛ لازم نیست تجربهٔ بزرگی باشد.'
    elif proof.get('proud_work'):
        action += f' می‌توانی از تجربهٔ «{proof["proud_work"]}» شروع کنی.'
    elif proof['evidence_need'] == 'ساخت نمونه‌کار':
        action += ' یک نمونهٔ کوچک و قابل‌انجام را نقطهٔ شروع بگذار.'
    else:
        action += f' یکی از چیزهایی که داری، مثل {proof["available_proof"][0]}، می‌تواند کمک کند.'
    channel = online['primary_channel']
    if channel == 'فعلاً حضور فعالی ندارم' or online['content_type'] == 'فعلاً چیزی منتشر نمی‌کنم':
        action += ' فعلاً آن را برای یک نفر بفرست؛ نیازی به انتشار عمومی نیست.'
    else:
        place = online.get('primary_channel_other') if channel == OTHER['primary_channel'] else channel
        action += f' آن را برای حضور فعلی‌ات در {place or "فضای آنلاین موردنظرت"} آماده کن.'
    goals = {'پیدا کردن مشتری یا پروژهٔ بیشتر': 'اولین گفت‌وگوی کاری از چه سؤال ساده‌ای می‌تواند شروع شود؟',
             'پیدا کردن شغل یا فرصت کاری بهتر': 'کدام نمونه می‌تواند توانایی تو را برای یک کارفرما روشن‌تر کند؟',
             'فروش محصول یا خدمات': 'مخاطب پیش از خرید بیشتر به پاسخ کدام سؤال نیاز دارد؟'}
    reflection = goals.get(first['primary_goal'], 'اگر مخاطب فقط یک چیز را از کارت به خاطر بسپارد، دوست داری چه باشد؟')
    if image['needed_next_step'] == 'نشان‌دادن نمونه‌کار و نتیجه':
        reflection = 'کدام تجربهٔ کوچک می‌تواند چیزی را که می‌خواهی نشان بدهی قابل‌دیدن کند؟'
    tied = max(precise) == min(precise)
    summary = (f'پاسخ‌های یک ماه اخیرت در هر پنج بخش نزدیک به هم‌اند؛ برای شروع می‌توانی روی «{lowest["title"]}» تمرکز کنی.'
               if tied else f'در یک ماه اخیر، نشانه‌های «{highest["title"]}» در پاسخ‌هایت بیشتر دیده می‌شود؛ «{lowest["title"]}» می‌تواند نقطهٔ شروع بعدی تو باشد.')
    return {'title': 'ارزیابی پرسونال برند', 'analysis_version': scoring['analysis_version'],
            'total': total, 'stage': stage, 'dimensions': dimensions, 'summary': summary,
            'strength': (f'امتیاز هر پنج بخش برابر است؛ «{highest["title"]}» هم یکی از زمینه‌هایی است که می‌توانی تجربه‌هایش را مرور کنی.' if tied else strengths[highest['key']]), 'strength_dimension': highest['key'],
            'top_opportunity': growth[lowest['key']], 'bottleneck': lowest['title'],
            'growth_dimension': lowest['key'], 'starter_action': action,
            'challenge_question': reflection, 'goal': first['primary_goal'],
            'needs_profile_review': online['profile_clarity'] == 'مطمئن نیستم',
            'disclaimer': DISCLAIMER, 'instagram': None,
            'immediate': [{'dimension': lowest['key'], 'title': action, 'evidence': lowest['evidence']}],
            'thirty_days': []}
