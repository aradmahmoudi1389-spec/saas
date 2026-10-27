import copy
import json
import math
from urllib.parse import urlsplit

TITLE = 'ارزیابی ساختاریافتهٔ پرسونال برند'
LIKERT = ['کاملاً مخالفم', 'مخالفم', 'نه موافقم نه مخالفم', 'موافقم', 'کاملاً موافقم']
GOALS = ['جذب مشتری یا پروژه', 'فروش محصول یا خدمت', 'افزایش اعتبار تخصصی', 'استخدام یا رشد شغلی', 'جذب همکاری تجاری', 'ساخت جامعهٔ مخاطبان', 'آموزش و اثرگذاری', 'تبدیل‌شدن به مرجع در یک موضوع', 'سایر']
STATUSES = ['فریلنسر یا متخصص مستقل', 'صاحب کسب‌وکار', 'مدرس یا تولیدکنندهٔ محتوا', 'مشاور یا کوچ', 'کارمند یا مدیر سازمانی', 'دانشجو یا ابتدای مسیر حرفه‌ای', 'در حال تغییر مسیر شغلی', 'سایر']
BARRIERS = ['مشخص‌نبودن مسیر و جایگاه', 'تولید محتوای مستمر', 'دیده‌نشدن', 'اعتمادسازی', 'فروش و تبدیل مخاطب', 'نداشتن نمونه‌کار یا شواهد کافی', 'نداشتن زمان یا برنامه', 'کیفیت اجرا جلوی دوربین', 'نداشتن ایدهٔ محتوا', 'سایر']
DIMENSIONS = [
    ('identity', 'وضوح هویت حرفه‌ای', 'وضوح تخصص، ارزش و مسیر حرفه‌ای', [
        'می‌توانم تخصص و نقش حرفه‌ای خود را در یک توضیح کوتاه و روشن بیان کنم.',
        'می‌دانم می‌خواهم در ذهن مخاطب با چه موضوع یا ارزشی شناخته شوم.',
        'انتخاب موضوعات کاری و محتوایی من با هدف حرفه‌ای بلندمدتم هماهنگ است.',
        'ارزش‌ها و اصولی که در کارم مهم هستند، در شیوهٔ معرفی و محتوای من دیده می‌شوند.',
    ], 'یک جملهٔ روشن دربارهٔ تخصص، مخاطب و ارزش خود بنویسید.', 'جملهٔ معرفی را با بازخورد پنج مخاطب بازنگری کنید.'),
    ('position', 'جایگاه‌یابی و شناخت مخاطب', 'شناخت مسئله و مخاطب مناسب', [
        'مخاطب اصلی خود را از نظر مسئله، نیاز و سطح آگاهی به‌خوبی می‌شناسم.',
        'می‌دانم مخاطب چرا باید من را به گزینه‌های مشابه ترجیح دهد.',
        'مسئله‌ای که برای مخاطب حل می‌کنم در معرفی و محتواهایم روشن است.',
        'می‌دانم کدام گروه‌ها مخاطب مناسب من نیستند.',
    ], 'یک گروه مخاطب و یک مسئلهٔ اولویت‌دار انتخاب کنید.', 'با پنج مخاطب مصاحبه و مسئلهٔ اصلی را مستند کنید.'),
    ('credibility', 'اعتبار و شواهد تخصص', 'وجود نمونه و نتیجهٔ قابل بررسی', [
        'برای ادعاهای حرفه‌ای خود نمونه‌کار، تجربه، نتیجه یا شواهد قابل‌ارائه دارم.',
        'در محتوایم به‌جای ادعاهای کلی، از مثال، تجربه یا نتیجه استفاده می‌کنم.',
        'مخاطبان یا مشتریان قبلی می‌توانند ارزش کاری من را تأیید کنند.',
        'می‌دانم برای افزایش اعتماد مخاطب، چه شواهدی باید بیشتر نمایش دهم.',
    ], 'یک نمونه‌کار همراه با مسئله، اقدام و نتیجه آماده کنید.', 'سه مطالعهٔ موردی با اجازهٔ صاحبان داده منتشر کنید.'),
    ('message', 'پیام، روایت و لحن', 'انسجام پیام و شناخت‌پذیری روایت', [
        'پیام اصلی من در محتواهای مختلف تکرار و تقویت می‌شود.',
        'لحن من در نوشته‌ها، ویدیوها و تعامل با مخاطب تا حد زیادی یکپارچه است.',
        'محتوای من فقط اطلاع‌رسانی نیست و دیدگاه یا روایت حرفه‌ای من را نیز نشان می‌دهد.',
        'در بیشتر محتواهایم مخاطب می‌داند قدم بعدی یا اقدام موردانتظار چیست.',
    ], 'یک پیام مرکزی و سه ویژگی لحن خود را مشخص کنید.', 'ده محتوای اخیر را از نظر پیام مرکزی بازنگری کنید.'),
    ('digital', 'اجرای دیجیتال و انسجام محتوا', 'انتخاب موضوع، استمرار و یادگیری از بازخورد', [
        'موضوعات محتوا را بر اساس هدف حرفه‌ای و نیاز مخاطب انتخاب می‌کنم، نه فقط ترندها.',
        'برای انتشار محتوا یا ارتباط با مخاطب، الگوی نسبتاً مشخصی دارم.',
        'می‌دانم کدام فرمت محتوا برای انتقال پیام من مؤثرتر است.',
        'عملکرد محتوا و بازخورد مخاطبان را بررسی می‌کنم و از آن یاد می‌گیرم.',
    ], 'سه ستون محتوا و برنامهٔ انتشار قابل اجرا بنویسید.', 'دو قالب محتوا را با موضوع مشابه آزمایش و نتیجه را ثبت کنید.'),
    ('growth', 'دیده‌شدن، تمایز و ظرفیت رشد', 'ارجاع حرفه‌ای، تمایز و برنامهٔ رشد', [
        'افراد خارج از شبکهٔ نزدیکم نیز برای موضوع تخصصی من به سراغم می‌آیند یا من را معرفی می‌کنند.',
        'محتوای من ویژگی یا زاویه‌ای دارد که آن را از محتوای مشابه قابل‌تشخیص می‌کند.',
        'حضور آنلاین من به شکل مشخصی با حوزهٔ حرفه‌ای‌ام پیوند خورده است.',
        'برای رشد دیده‌شدن، اعتبار و ارتباطات حرفه‌ای خود برنامه دارم.',
    ], 'یک زاویهٔ تخصصی مشخص برای معرفی خود انتخاب کنید.', 'با سه همکار مکمل یک محتوای مشترک مسئله‌محور منتشر کنید.'),
]
BASE = [
    ('expertise', 'حوزهٔ اصلی فعالیت شما چیست؟', True),
    ('professional_status', 'در حال حاضر کدام وضعیت حرفه‌ای را دارید؟', True),
    ('audience', 'مخاطب اصلی شما بیشتر چه کسانی هستند؟', True),
    ('problem', 'مهم‌ترین مسئله‌ای که برای مخاطب حل می‌کنید چیست؟', True),
    ('barrier', 'مهم‌ترین مانع فعلی شما در رشد برند شخصی چیست؟', True),
]
IDENTITY = [
    ('remember', 'اگر مخاطب فقط یک جمله از شما به خاطر بسپارد، دوست دارید آن جمله چه باشد؟', True),
    ('difference', 'چه تجربه، نگاه یا روش کاری شما را از افراد مشابه متمایز می‌کند؟', True),
    ('one_problem', 'اگر فقط بتوانید روی حل یک مسئله برای مخاطب تمرکز کنید، آن مسئله چیست؟', True),
    ('best_audience', 'چه کسانی بیشترین ارزش را از محتوا یا خدمات شما می‌گیرند؟', True),
    ('not_audience', 'چه افرادی مخاطب مناسب شما نیستند؟', False),
    ('values', 'چه ارزش یا اصلی نباید در برند شما نادیده گرفته شود؟', True),
]
EVIDENCE = [
    ('topics', 'سه موضوعی که بیشتر دربارهٔ آن‌ها محتوا تولید می‌کنید.'),
    ('problems', 'سه مسئله‌ای که برای مخاطب حل می‌کنید.'),
    ('proof', 'شواهد اعتبار شما چیست؟ مانند تجربه، نمونه‌کار، نتیجه، رضایت مشتری، گواهی یا سابقه.'),
    ('proud_content', 'یک محتوایی که از آن رضایت دارید یا به آن افتخار می‌کنید.'),
    ('weak_content', 'یک محتوایی که انتظار داشتید بهتر عمل کند.'),
    ('portfolio_url', 'لینک وب‌سایت، رزومه یا نمونه‌کار، در صورت تمایل.'),
    ('notes', 'توضیح تکمیلی برای تحلیل‌گر، در صورت نیاز.'),
]


def template():
    items = [{'id': f'{key}_{i+1}', 'dimension': key, 'title': title, 'weight': 1, 'order': j * 4 + i, 'active': True} for j, (key, _, _, questions, _, _) in enumerate(DIMENSIONS) for i, title in enumerate(questions)]
    return {'title': TITLE, 'base': BASE, 'identity': IDENTITY, 'evidence': EVIDENCE, 'goals': GOALS, 'statuses': STATUSES, 'barriers': BARRIERS, 'items': items, 'likert': LIKERT, 'validation': 'not_validated', 'purpose': 'خودبازنگری حرفه‌ای، نه استخدام یا تشخیص شخصیت', 'population': 'بزرگسالان دارای فعالیت حرفه‌ای', 'limitations': 'روایی و پایایی آماری هنوز تأیید نشده‌اند.'}


def model():
    return {'dimensions': {d[0]: 1 / 6 for d in DIMENSIONS}, 'source_weights': {'self_report': 1, 'evidence': 0, 'instagram': 0}, 'thresholds': [20, 40, 60, 80], 'method': 'likert-linear-v1', 'analysis_version': 'structured-rules-v2'}


def clean(value, maximum=1200, required=False):
    if not isinstance(value, str) or len(value) > maximum or any(ord(c) < 32 and c not in '\n\t\r' for c in value):
        raise ValueError('متن واردشده معتبر نیست یا بیش از حد طولانی است.')
    value = value.strip()
    if required and not value:
        raise ValueError('لطفاً فیلدهای الزامی را تکمیل کنید.')
    return value


def active_items(body):
    return [q for q in body['items'] if q.get('active', True)]


def validate_step(step, data, body):
    if not isinstance(data, dict):
        raise ValueError('قالب پاسخ معتبر نیست.')
    if step in (1, 2, 4):
        fields = body['base'] if step == 1 else body['identity'] if step == 2 else [(k, t, False) for k, t in body['evidence']]
        allowed = {f[0] for f in fields} | ({'goal'} if step == 1 else set())
        if set(data) - allowed:
            raise ValueError('فیلد ناشناخته در پاسخ وجود دارد.')
        result = {}
        for key, _, required in fields:
            if step == 1 and key == 'barrier' and 'barriers' in body:
                barriers = data.get(key)
                if not isinstance(barriers, list) or not 1 <= len(barriers) <= 2 or any(v not in body['barriers'] for v in barriers) or len(set(barriers)) != len(barriers):
                    raise ValueError('یک یا حداکثر دو مانع رشد را انتخاب کنید.')
                result[key] = barriers
            else:
                result[key] = clean(data.get(key, ''), 200 if key == 'expertise' and 'statuses' in body else 1200, required)
        if step == 1:
            if data.get('goal') not in body['goals']:
                raise ValueError('هدف برند را انتخاب کنید.')
            if 'statuses' in body and result['professional_status'] not in body['statuses']:
                raise ValueError('وضعیت حرفه‌ای را از گزینه‌ها انتخاب کنید.')
            result['goal'] = data['goal']
        if step == 4 and result.get('portfolio_url'):
            url = urlsplit(result['portfolio_url'])
            if url.scheme != 'https' or not url.hostname or url.username or url.password:
                raise ValueError('لینک نمونه‌کار باید یک آدرس HTTPS معتبر باشد.')
        return result
    if step == 3:
        ids = {q['id'] for q in active_items(body)}
        if set(data) != ids or any(type(v) is not int or not 1 <= v <= 5 for v in data.values()):
            raise ValueError('به همهٔ گویه‌ها از یک تا پنج پاسخ دهید.')
        return dict(data)
    if step == 5:
        if set(data) - {'choice', 'introduction'} or data.get('choice') not in {'skip', 'connected'}:
            raise ValueError('روش ادامه را انتخاب کنید.')
        return {'choice': data['choice'], 'introduction': clean(data.get('introduction', ''), 1200) if data['choice'] == 'skip' else ''}
    raise ValueError('مرحله معتبر نیست.')


def validate_template(body):
    original = template()
    if not isinstance(body, dict) or set(body) != set(original):
        raise ValueError('برای ویرایش از قالب جدید ۲۴گویه‌ای استفاده کنید؛ داده‌های قبلی حفظ می‌شوند.')
    for key in ('base', 'identity', 'evidence', 'goals', 'statuses', 'barriers', 'likert'):
        if body[key] != copy.deepcopy(original[key]) and body[key] != [list(v) if isinstance(v, tuple) else v for v in original[key]]:
            raise ValueError('ساختار مراحل ثابت است؛ متن، ترتیب و فعال‌بودن گویه‌ها قابل ویرایش است.')
    if not isinstance(body.get('items'), list) or len(body['items']) != 24:
        raise ValueError('قالب باید ۲۴ گویه داشته باشد.')
    sources = {q['id']: q for q in original['items']}
    if {q.get('id') for q in body['items']} != set(sources):
        raise ValueError('کلید پایدار گویه‌ها نباید تغییر کند.')
    for q in body['items']:
        if set(q) != set(sources[q['id']]) or q['dimension'] != sources[q['id']]['dimension'] or q['weight'] != 1 or type(q['active']) is not bool or type(q['order']) is not int or not 0 <= q['order'] < 24:
            raise ValueError('بُعد و وزن گویه باید ثابت و ترتیب معتبر باشد.')
        clean(q['title'], 400, True)
    if len({q['order'] for q in body['items']}) != 24 or any(not any(q['dimension'] == d[0] for q in active_items(body)) for d in DIMENSIONS):
        raise ValueError('ترتیب گویه‌ها باید یکتا و هر بُعد دارای حداقل یک گویهٔ فعال باشد.')
    clean(body['title'], 150, True)


def validate_model(body):
    if not isinstance(body, dict) or set(body) != set(model()) or not isinstance(body['dimensions'], dict) or set(body['dimensions']) != {d[0] for d in DIMENSIONS}:
        raise ValueError('مدل نمره‌دهی معتبر نیست.')
    weights = list(body['dimensions'].values())
    if any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in weights) or not math.isclose(sum(weights), 1, abs_tol=1e-6):
        raise ValueError('وزن‌های ابعاد باید مثبت و جمع آن‌ها یک باشد.')
    if body['source_weights'] != model()['source_weights'] or body['thresholds'] != model()['thresholds'] or body['method'] != 'likert-linear-v1' or body['analysis_version'] not in {'structured-rules-v1', 'structured-rules-v2'}:
        raise ValueError('تغییر روش تحلیل نیازمند پیاده‌سازی نسخهٔ موتور است.')


def score(answers, body, scoring, instagram=None):
    validate_model(scoring)
    values = validate_step(3, answers[3], body)
    dimensions = []
    for key, title, description, _, immediate, month in DIMENSIONS:
        items = [q for q in active_items(body) if q['dimension'] == key]
        ids = [q['id'] for q in items]
        value = round(sum((values[q['id']] - 1) * 25 * q.get('weight', 1) for q in items) / sum(q.get('weight', 1) for q in items), 2)
        strongest = max(items, key=lambda q: values[q['id']])
        weakest = min(items, key=lambda q: values[q['id']])
        dimensions.append({'key': key, 'title': title, 'description': description, 'score': value, 'evidence': ids, 'immediate': immediate, 'month': month, 'strength_detail': strongest['title'], 'gap_detail': weakest['title'], 'interpretation': 'اولویت بهبود' if value < 40 else 'در حال شکل‌گیری' if value < 70 else 'نقطهٔ قوت خوداظهارشده'})
    total = round(sum(d['score'] * scoring['dimensions'][d['key']] for d in dimensions), 2)
    by_key = {d['key']: d['score'] for d in dimensions}
    stage_index = sum(total >= threshold for threshold in scoring['thresholds'])
    core = min(by_key[key] for key in ('identity', 'position', 'message'))
    stage_index = min(stage_index, 0 if core < 20 else 1 if core < 40 else 2 if min(by_key.values()) < 60 else 4)
    stage = ['کشف', 'تعریف', 'تثبیت', 'تمایز', 'مرجعیت'][stage_index]
    ranked = sorted(dimensions, key=lambda d: d['score'])
    has_evidence = any(answers.get(4, {}).get(k) for k in ('proof', 'portfolio_url', 'proud_content'))
    confidence = 'تحلیل تکمیل‌شده با شواهدی که وارد کرده‌اید' if has_evidence or instagram else 'تحلیل پایه بر اساس پاسخ‌های شما'
    goal = answers[1]['goal']
    status = answers[1].get('professional_status', '')
    candidates = {'متخصص مسئله‌محور': by_key['position'] + 20, 'مدرس و توانمندساز': by_key['message'], 'سازنده و مجری': by_key['digital'], 'مشاور و راهبر': by_key['position'], 'روایت‌گر تجربه': by_key['message'], 'رهبر فکری': (by_key['credibility'] + by_key['growth']) / 2, 'برند جامعه‌محور': by_key['growth'], 'برند محصول‌محور': by_key['digital'], 'برند ترکیبی': total}
    goal_pattern = {'آموزش و اثرگذاری': 'مدرس و توانمندساز', 'ساخت جامعهٔ مخاطبان': 'برند جامعه‌محور', 'فروش محصول یا خدمت': 'برند محصول‌محور', 'تبدیل‌شدن به مرجع در یک موضوع': 'رهبر فکری', 'تبدیل‌شدن به مرجع یک موضوع': 'رهبر فکری', 'جذب مشتری یا پروژه': 'متخصص مسئله‌محور', 'جذب همکاری تجاری': 'مشاور و راهبر', 'همکاری تجاری': 'مشاور و راهبر', 'استخدام یا رشد شغلی': 'سازنده و مجری'}.get(goal, 'برند ترکیبی')
    candidates[goal_pattern] += 25
    if status == 'مشاور یا کوچ':
        candidates['مشاور و راهبر'] += 25
    if status == 'مدرس یا تولیدکنندهٔ محتوا':
        candidates['مدرس و توانمندساز'] += 25
    if answers.get(4, {}).get('proud_content') and has_evidence:
        candidates['روایت‌گر تجربه'] += 15
    patterns = sorted(candidates, key=candidates.get, reverse=True)
    context = {'identity': answers[2].get('remember', ''), 'position': answers[1]['audience'], 'credibility': answers.get(4, {}).get('proof') or answers[1]['expertise'], 'message': answers[2].get('remember', ''), 'digital': answers.get(4, {}).get('topics') or answers[1]['problem'], 'growth': answers[2].get('difference', '')}
    def action(d, monthly=False):
        return {'dimension': d['key'], 'title': (d['month'] if monthly else d['immediate']) + ' موضوع تمرین شما: «' + context[d['key']][:200] + '».', 'evidence': d['evidence']}
    return {'title': TITLE, 'dimensions': dimensions, 'total': total, 'stage': stage, 'confidence': confidence, 'pattern': 'الگوی احتمالی: ' + patterns[0], 'secondary_patterns': patterns[1:3], 'pattern_reason': f'این پیشنهاد از هدف «{goal}»، وضعیت حرفه‌ای «{status}» و ترکیب نمره‌های شش بُعد استخراج شده است؛ تشخیص شخصیت نیست.', 'strength': ranked[-1]['title'], 'bottleneck': ranked[0]['title'], 'summary': f"در حوزهٔ {answers[1]['expertise']} و برای مخاطب «{answers[1]['audience']}»، قوی‌ترین بُعد خوداظهاری شما {ranked[-1]['title']} است. برای هدف «{goal}»، نخست روی {ranked[0]['title']} کار کنید؛ این گلوگاه فعلی مسیر رشد شماست.", 'central_message': f"در حوزهٔ {answers[1]['expertise']} به {answers[1]['audience']} برای {answers[1]['problem']} کمک می‌کنم.", 'identity': answers[2], 'professional': answers[1], 'content_evidence': answers.get(4, {}) if has_evidence or answers.get(4, {}).get('topics') else None, 'source_weights': scoring['source_weights'], 'score_adjustments': [], 'immediate': [action(d) for d in ranked[:3]], 'thirty_days': [action(d, True) for d in ranked[3:]], 'instagram': instagram, 'limitations': ['این ابزار هنوز اعتبارسنجی روان‌سنجی نشده است.', 'نمره‌ها فقط بر پایهٔ رفتارهای خوداظهارشده‌اند؛ شواهد و پیج به‌صورت زمینهٔ مکمل استفاده می‌شوند و تعدیل امتیاز انجام نشده است.', 'متن شواهد و لینک‌ها اثبات مستقل صحت ادعا نیستند.', 'تحلیل تصویر، ویدیو، شخصیت و ویژگی حساس انجام نشده است.', 'مرحلهٔ بلوغ و الگوی برند فرضیهٔ راهنما هستند، نه حکم قطعی.'], 'analysis_version': scoring['analysis_version']}


V3_LIKERT = ['اصلاً دربارهٔ من درست نیست', 'معمولاً دربارهٔ من درست نیست', 'گاهی دربارهٔ من درست است', 'بیشتر وقت‌ها دربارهٔ من درست است', 'کاملاً دربارهٔ من درست است']
V3_STAGES = ['شروع مسیر', 'در حال شکل‌گرفتن', 'قابل‌تشخیص', 'روبه‌رشد', 'جاافتاده و قابل‌اعتماد']
V3_DIMENSIONS = [
    ('clarity', 'روشن‌بودن مسیر', 'اینکه بدانی در چه زمینه‌ای می‌خواهی شناخته شوی.'),
    ('introduction', 'قابل‌فهم‌بودن معرفی', 'اینکه دیگران سریع بفهمند چه کمکی می‌کنی.'),
    ('evidence', 'اعتماد و شواهد', 'تجربه‌ها و نتیجه‌هایی که توانایی‌ات را نشان می‌دهند.'),
    ('content', 'هماهنگی محتوا', 'ارتباط موضوع‌های محتوایت با مسیر و هدفت.'),
    ('visibility', 'استمرار و دیده‌شدن', 'ادامه‌دادن حضور و کمک‌کردن به مخاطب برای قدم بعدی.'),
]
V3_SECTIONS = [
    {'id':'path','title':'خودت و مسیر فعلی‌ات','description':'قبل از اینکه ببینیم پرسونال برندت چطور است، بهتر است بدانیم الان در چه مسیر کاری هستی و از این ارزیابی چه می‌خواهی. لازم نیست جواب‌هایت رسمی یا کامل باشند؛ همان چیزی را بنویس که همین حالا واقعاً به ذهنت می‌رسد.','purpose':'شناخت نقطهٔ شروع و چیزی که برایت مهم‌تر است.'},
    {'id':'image','title':'تصویری که می‌خواهی از خودت بسازی','description':'در این قسمت قرار نیست جواب حرفه‌ای یا نهایی بدهی. فقط می‌خواهیم ببینیم دوست داری دیگران چه چیزی را در تو ببینند و چه حسی از آشنایی با تو بگیرند. اگر هنوز جواب روشنی نداری، گزینهٔ نزدیک‌تر را انتخاب کن.','purpose':'روشن‌کردن تصویری که دوست داری در ذهن مخاطب بماند.'},
    {'id':'behavior','title':'رفتارهای واقعی تو','description':'در این قسمت دربارهٔ رفتارهای واقعی روزمره‌ات سؤال می‌پرسیم. قرار نیست بهترین گزینه را انتخاب کنی. گزینه‌ای را بزن که بیشتر شبیه رفتار این روزهای توست، حتی اگر همیشه این‌طور نیست.','purpose':'دیدن رفتارهای فعلی، بدون قضاوت خوب یا بد.'},
    {'id':'evidence','title':'شواهد و تجربه','description':'اینجا فقط می‌خواهیم بدانیم چه چیزهایی برای نشان‌دادن توانایی‌هایت در اختیار داری. لازم نیست سابقهٔ خیلی بزرگ یا نمونهٔ رسمی داشته باشی؛ تجربه‌های کوچک هم می‌توانند کمک‌کننده باشند.','purpose':'شناخت چیزهایی که می‌توانند توانایی‌ات را نشان دهند.'},
    {'id':'online','title':'حضور آنلاین','description':'در این قسمت دربارهٔ حضور آنلاین و شیوه‌ای که دیگران تو را در اینترنت می‌بینند صحبت می‌کنیم. اگر هنوز فعالیت زیادی نداری، همان گزینه‌ای را انتخاب کن که به وضعیت فعلی‌ات نزدیک‌تر است.','purpose':'دیدن تصویری که امروز از تو در فضای آنلاین دیده می‌شود.'},
]
V3_BASE = [
    ('field','این روزها بیشتر در چه زمینه‌ای کار می‌کنی یا دوست داری در چه زمینه‌ای شناخته شوی؟', ['آموزش و تدریس','مشاوره و کوچینگ','فروش و کسب‌وکار','بازاریابی و تولید محتوا','طراحی و کارهای خلاقانه','فناوری و برنامه‌نویسی','پزشکی، سلامت و ورزش','امور مالی و حقوقی','منابع انسانی و مدیریت','هنر و رسانه','دانشجویی و شروع مسیر کاری','هنوز مطمئن نیستم','موضوع دیگری دارم']),
    ('goal','در حال حاضر بیشتر دنبال کدام نتیجه هستی؟',['پیدا کردن مشتری یا پروژهٔ بیشتر','بهتر دیده‌شدن در حوزهٔ کاری','پیدا کردن شغل یا فرصت کاری بهتر','فروش محصول یا خدمات','معرفی بهتر توانایی‌هایم','ساختن اعتبار در یک موضوع','پیدا کردن همکار یا فرصت همکاری','هنوز دقیق نمی‌دانم؛ فقط می‌خواهم وضعیتم را بهتر بفهمم','هدف دیگری دارم']),
    ('audience','دوست داری چه کسانی بیشتر تو را بشناسند؟',['مشتریان و خریداران احتمالی','مدیران و کارفرماها','همکاران حوزهٔ کاری','دانشجویان و علاقه‌مندان به یادگیری','صاحبان کسب‌وکار','مخاطبان عمومی','سرمایه‌گذاران یا شرکای تجاری','هنوز دقیق نمی‌دانم','گروه دیگری مدنظرم است']),
    ('showcase','اگر بخواهی فقط یک چیز را دربارهٔ خودت بیشتر نشان بدهی، کدام مورد برایت مهم‌تر است؟',['دانشی که دارم','تجربه‌ای که به دست آورده‌ام','نتیجه‌ای که برای دیگران ایجاد می‌کنم','سبک و نگاه متفاوت من','شخصیت و طرز فکر من','نمونه‌کارها و کارهایی که انجام داده‌ام','هنوز نمی‌دانم']),
    ('situation','الان بیشتر کدام حالت را تجربه می‌کنی?',['نمی‌دانم دقیقاً باید خودم را با چه موضوعی معرفی کنم.','چند علاقه و توانایی دارم و انتخاب یک مسیر برایم سخت است.','می‌دانم چه کاری می‌کنم، اما دیگران آن را خوب نمی‌شناسند.','محتوا تولید می‌کنم، اما نمی‌دانم چه چیزی بهتر است منتشر کنم.','شروع می‌کنم، اما استمرار برایم سخت می‌شود.','مخاطب دارم، اما به مشتری یا فرصت کاری تبدیل نمی‌شود.','هنوز نمونه‌کار یا نتیجهٔ کافی برای نشان‌دادن ندارم.','فعلاً مشکل مشخصی احساس نمی‌کنم.','مورد دیگری دارم.']),
]
V3_IMAGE = [
 ('trait','وقتی کسی با تو آشنا می‌شود، دوست داری بیشتر با کدام ویژگی تو را به یاد بیاورد؟',['قابل‌اعتمادبودن','متخصص‌بودن','خلاق‌بودن','ساده و قابل‌فهم توضیح‌دادن','نتیجه‌گرا بودن','همراه و حمایتگر بودن','متفاوت فکرکردن','منظم و حرفه‌ای بودن','هنوز نمی‌دانم','ویژگی دیگری']),
 ('help','مردم معمولاً برای چه چیزی می‌توانند از تو کمک بگیرند؟',['یادگیری یک مهارت یا موضوع','حل یک مشکل کاری','تصمیم‌گیری و انتخاب بهتر','انجام یک کار تخصصی','پیدا کردن ایده و مسیر','افزایش فروش یا رشد کسب‌وکار','بهترشدن شرایط شخصی یا حرفه‌ای','هنوز کسی برای کمک به سراغم نمی‌آید','مورد دیگری']),
 ('state','کدام جمله بیشتر به وضعیت فعلی تو نزدیک است?',['هنوز دارم می‌فهمم در چه کاری قوی‌تر هستم.','چند توانایی دارم، اما نمی‌دانم کدام را پررنگ‌تر کنم.','می‌دانم در چه کاری خوبم، اما آن را خوب معرفی نکرده‌ام.','دیگران از توانایی من خبر دارند، اما حضورم منظم نیست.','تا حدی شناخته شده‌ام و می‌خواهم حرفه‌ای‌تر دیده شوم.','نمی‌دانم کدام گزینه به من نزدیک‌تر است.']),
 ('feeling','دوست داری مخاطب بعد از دیدن محتوا یا کار تو چه احساسی داشته باشد?',['احساس کند چیزی یاد گرفته است.','احساس کند می‌تواند به من اعتماد کند.','برای حل مسئله‌اش انگیزه بگیرد.','ایدهٔ جدید پیدا کند.','احساس کند من او را می‌فهمم.','برای همکاری یا خرید کنجکاو شود.','هنوز نمی‌دانم.']),
 ('need','برای اینکه دیگران بهتر تو را بشناسند، کدام مورد را بیشتر لازم داری?',['انتخاب یک موضوع روشن','توضیح بهتر دربارهٔ کاری که انجام می‌دهم','نشان‌دادن نمونه‌کار و نتیجه','تولید محتوای منظم‌تر','حضور بیشتر در شبکه‌های اجتماعی','اعتمادبه‌نفس برای معرفی خودم','داشتن یک مسیر مشخص','هنوز مطمئن نیستم']),
]
V3_BEHAVIOR = [
 'وقتی دربارهٔ کارم صحبت می‌کنم، معمولاً می‌توانم ساده بگویم چه کمکی می‌کنم.','موضوعی که دوست دارم با آن شناخته شوم، برای خودم تا حدی روشن است.','معمولاً می‌دانم چه کسانی بیشتر به تجربه یا توانایی من نیاز دارند.','می‌توانم یک نمونه از کاری را نشان بدهم که برای خودم یا فرد دیگری نتیجه داشته است.','وقتی دربارهٔ توانایی‌هایم حرف می‌زنم، معمولاً مثال یا تجربه‌ای هم برای نشان‌دادن دارم.','محتوایی که منتشر می‌کنم معمولاً به کاری که انجام می‌دهم ارتباط دارد.','کسی که محتوای من را می‌بیند، معمولاً می‌فهمد موضوع اصلی کار من چیست.','در معرفی خودم از جمله‌ها یا ادعاهایی استفاده نمی‌کنم که خودم هم دقیقاً نمی‌دانم منظورشان چیست.','اگر چند محتوای اخیرم را کنار هم بگذارم، موضوع مشترکی بین آن‌ها دیده می‌شود.','وقتی محتوایی منتشر می‌کنم، معمولاً می‌دانم برای چه کسی ساخته شده است.','بیشتر اوقات می‌توانم انتشار محتوا یا معرفی کارم را ادامه بدهم، حتی اگر کامل و بی‌نقص نباشد.','از واکنش‌ها، سؤال‌ها یا نتیجهٔ محتواهایم چیزی یاد می‌گیرم.','چیزی در نگاه، تجربه یا روش کار من وجود دارد که باعث می‌شود با افراد مشابه اشتباه گرفته نشوم.','مخاطب می‌تواند بفهمد برای آشنایی بیشتر، پرسیدن سؤال یا همکاری با من چه کاری انجام دهد.','حضور آنلاین من کم‌وبیش همان تصویری را نشان می‌دهد که دوست دارم دیگران از کارم داشته باشند.'
]
V3_EVIDENCE = [('proof','کدام مورد را برای نشان‌دادن توانایی‌هایت داری؟',['نمونه‌کار','تجربهٔ کاری','نتیجه‌ای که برای خودم یا دیگری ایجاد کرده‌ام','رضایت یا نظر دیگران','مدرک یا گواهی','صفحه، محصول یا پروژه','هنوز چیز مشخصی ندارم','مورد دیگری']),('experience','کدام کار یا تجربه‌ات را بیشتر دوست داری دیگران ببینند؟',None),('need','در حال حاضر بیشتر به چه چیزی نیاز داری?',['ساخت نمونه‌کار','نشان‌دادن نتیجهٔ کار','توضیح بهتر توانایی‌ها','منظم‌کردن محتوای قبلی','پیدا کردن موضوع مناسب','گرفتن بازخورد','هنوز نمی‌دانم'])]
V3_ONLINE = [('platform','در حال حاضر بیشتر در کدام فضا فعالیت می‌کنی?',['اینستاگرام','لینکدین','تلگرام','وب‌سایت شخصی','یوتیوب','چند شبکهٔ اجتماعی','فعلاً حضور فعالی ندارم','جای دیگری']),('published','معمولاً چه چیزی منتشر می‌کنی?',['آموزش','تجربه‌های شخصی و کاری','معرفی خدمات یا محصول','نمونه‌کار','نظر و دیدگاه','محتوای سرگرم‌کننده','محتوای متنوع و بدون موضوع مشخص','فعلاً محتوایی منتشر نمی‌کنم']),('clarity','وقتی کسی صفحهٔ تو را می‌بیند، به‌نظر خودت چقدر می‌فهمد چه کاری انجام می‌دهی?',['اصلاً مشخص نیست','کمی مشخص است','تا حدی مشخص است','بیشتر مشخص است','کاملاً مشخص است','مطمئن نیستم'])]

def template_v3():
    dims=['clarity','introduction','evidence','content','visibility']
    mapping=[('introduction',0),('clarity',1),('clarity',2),('evidence',3),('evidence',4),('content',5),('introduction',6),('introduction',7),('content',8),('content',9),('visibility',10),('visibility',11),('clarity',12),('visibility',13),('visibility',14)]
    return {'schema':3,'title':'ارزیابی پرسونال برند','version':'v3','released_on':'2026-10-27','sections':V3_SECTIONS,'base':V3_BASE,'image':V3_IMAGE,'behavior':[{'id':f'behavior_{i+1}','title':V3_BEHAVIOR[index],'dimension':dim,'order':i,'active':True,'weight':1} for i,(dim,index) in enumerate(mapping)],'evidence':V3_EVIDENCE,'online':V3_ONLINE,'likert':V3_LIKERT,'dimensions':[{'key':k,'title':t,'description':d} for k,t,d in V3_DIMENSIONS],'validation':'not_validated','purpose':'تصویر کلی از وضعیت فعلی، نه قضاوت ارزش یا توانایی.'}

def model_v3():
    return {'schema':3,'dimensions':{k:1/5 for k,_,_ in V3_DIMENSIONS},'thresholds':[20,40,60,80],'method':'likert-linear-v2','analysis_version':'structured-rules-v3'}

def _v3_clean_choice(data,key,options,required=True,multiple=False):
    value=data.get(key)
    if multiple:
        if not isinstance(value,list) or not 1<=len(value)<= (2 if key == 'audience' else len(options)) or any(not isinstance(v, str) or v not in options for v in value) or len(set(value))!=len(value): raise ValueError('گزینه‌های انتخاب‌شده معتبر نیستند.')
        if key == 'proof' and 'هنوز چیز مشخصی ندارم' in value and len(value) > 1:
            raise ValueError('اگر هنوز چیز مشخصی نداری، فقط همان گزینه را انتخاب کن.')
        return value
    if value not in options and (required or value): raise ValueError('یکی از گزینه‌ها را انتخاب کنید.')
    return value or ''

def validate_partial_v3(step, data, body):
    if body.get('schema') != 3 or not isinstance(data, dict):
        raise ValueError('قالب پاسخ معتبر نیست.')
    if step == 3:
        allowed = {q['id'] for q in body['behavior']}
        if set(data) - allowed or any(type(v) is not int or not 1 <= v <= 5 for v in data.values()):
            raise ValueError('پاسخ معتبر نیست.')
        return dict(data)
    fields = body[{1: 'base', 2: 'image', 4: 'evidence', 5: 'online'}[step]]
    options = {key: values for key, _, values in fields}
    texts = {'field_other', 'goal_other', 'audience_other', 'situation_other'} if step == 1 else {'experience'} if step == 4 else set()
    if set(data) - set(options) - texts:
        raise ValueError('فیلد ناشناخته در پاسخ وجود دارد.')
    result = {}
    for key, value in data.items():
        if key in texts:
            result[key] = clean(value, 1200 if key == 'experience' else 200)
        elif key in {'audience', 'proof'}:
            maximum = 2 if key == 'audience' else len(options[key])
            if not isinstance(value, list) or len(value) > maximum or any(not isinstance(v, str) or v not in options[key] for v in value) or len(set(value)) != len(value):
                raise ValueError('گزینه‌های انتخاب‌شده معتبر نیستند.')
            result[key] = value
        elif value not in options[key]:
            raise ValueError('یکی از گزینه‌ها را انتخاب کن.')
        else:
            result[key] = value
    return result


def validate_step_v3(step,data,body):
    if not isinstance(data,dict): raise ValueError('قالب پاسخ معتبر نیست.')
    if step==1:
        allowed={k for k,_,_ in body['base']}|{'field_other','goal_other','audience_other','situation_other'}
        if set(data)-allowed: raise ValueError('فیلد ناشناخته در پاسخ وجود دارد.')
        result={}
        for key,_,options in body['base']:
            result[key]=_v3_clean_choice(data,key,options,multiple=key=='audience')
        for key in ('field_other','goal_other','audience_other','situation_other'):
            result[key]=clean(data.get(key,''),200)
        if result['field']=='موضوع دیگری دارم' and not result['field_other']: raise ValueError('موضوع دیگری را کوتاه بنویسید.')
        return result
    if step==2:
        if set(data) - {key for key, _, _ in body['image']}:
            raise ValueError('فیلد ناشناخته در پاسخ وجود دارد.')
        result={}
        for key,_,options in body['image']: result[key]=_v3_clean_choice(data,key,options)
        return result
    if step==3:
        ids={q['id'] for q in body['behavior']}
        if set(data)!=ids or any(type(v) is not int or not 1<=v<=5 for v in data.values()): raise ValueError('به همهٔ سؤال‌ها پاسخ بده.')
        return dict(data)
    if step==4:
        result={'proof':_v3_clean_choice(data,'proof',body['evidence'][0][2],multiple=True),'experience':clean(data.get('experience',''),1200),'need':_v3_clean_choice(data,'need',body['evidence'][2][2])}
        if set(data)-{'proof','experience','need'}: raise ValueError('فیلد ناشناخته در پاسخ وجود دارد.')
        return result
    if step==5:
        result={k:_v3_clean_choice(data,k,options) for k,_,options in body['online']}
        if set(data)-set(result)-{'choice','introduction'}: raise ValueError('فیلد ناشناخته در پاسخ وجود دارد.')
        result.update(choice=data.get('choice','skip'),introduction=clean(data.get('introduction',''),1200))
        if result['choice'] not in {'skip','connected'}: raise ValueError('روش ادامه را انتخاب کنید.')
        return result
    raise ValueError('مرحله معتبر نیست.')

def score_v3(answers,body,scoring,instagram=None):
    validate_model(scoring)
    for step in range(1, 6):
        validate_step_v3(step, answers[step], body)
    values=validate_step_v3(3,answers[3],body)
    dims=[]
    for key,title,description in V3_DIMENSIONS:
        items=[q for q in body['behavior'] if q['dimension']==key]
        score=round(sum((values[q['id']]-1)*25 for q in items)/len(items),2)
        dims.append({'key':key,'title':title,'description':description,'score':score,'evidence':[q['id'] for q in items],'interpretation':'جای خوبی برای شروع' if score<40 else 'در حال شکل‌گرفتن' if score<70 else 'نقطهٔ قوت فعلی'})
    total=round(sum(d['score']*scoring['dimensions'][d['key']] for d in dims),2)
    stage=V3_STAGES[min(sum(total>=t for t in scoring['thresholds']),4)]
    ranked=sorted(dims,key=lambda d:d['score'])
    answers1=answers[1]; field=answers1['field_other'] if answers1['field']=='موضوع دیگری دارم' else answers1['field']
    summaries = ['اینجا جای خوبی برای شروع وجود دارد؛ هنوز می‌توانی موضوع و شیوهٔ معرفی خودت را روشن‌تر کنی.', 'بخش‌هایی از مسیرت روشن شده، اما هنوز مخاطب ممکن است نداند دقیقاً برای چه کاری به سراغت بیاید.', 'تصویر کلی کارت قابل‌تشخیص است و حالا می‌توانی بخش‌های کم‌رنگ‌تر را روشن‌تر کنی.', 'چند رفتار کمک‌کننده در حضورت دیده می‌شود؛ تقویت بخش‌های کم‌رنگ‌تر می‌تواند به ادامهٔ رشد کمک کند.', 'پاسخ‌هایت نشان می‌دهد موضوع کارت، شواهد و حضورت تا حد زیادی در کنار هم قرار گرفته‌اند.']
    summary = summaries[min(sum(total>=t for t in scoring['thresholds']),4)]
    actions = {
        'clarity': 'فعلاً یک موضوع اصلی انتخاب کن و معرفی‌ات را حول همان موضوع بنویس.',
        'introduction': 'در یک جملهٔ ساده بگو چه کمکی به چه کسی می‌کنی و آن را به یک نفر نشان بده.',
        'evidence': 'یک تجربهٔ کوچک را انتخاب کن و نتیجهٔ قابل‌نشان‌دادن آن را کوتاه توضیح بده.',
        'content': 'چند محتوای اخیرت را کنار هم بگذار و موضوع مشترک آن‌ها را پیدا کن.',
        'visibility': 'یک شکل ساده و قابل‌ادامه برای معرفی کارت انتخاب کن، حتی اگر بی‌نقص نیست.'
    }
    opportunity=ranked[0]['title']
    starter = actions[ranked[0]['key']]
    reason = f'در پاسخ‌های رفتاری تو، میانگین بخش «{opportunity}» {ranked[0]["score"]} از ۱۰۰ و بخش «{ranked[-1]["title"]}» {ranked[-1]["score"]} از ۱۰۰ بود. انتخاب‌های دیگر برای شناخت هدفت استفاده شده‌اند، نه کم‌کردن یا زیادکردن نمره.'
    return {'title':'ارزیابی پرسونال برند','dimensions':dims,'total':total,'stage':stage,'confidence':'تصویر کلی بر اساس پاسخ‌های تو','summary':summary,'points':[f'قوی‌ترین بخش فعلی: {ranked[-1]["title"]}.',f'بیشترین فرصت رشد: {opportunity}.','این نتیجه فقط وضعیت فعلی را نشان می‌دهد و قابل تغییر است.'],'strength':ranked[-1]['title'],'bottleneck':opportunity,'top_opportunity':opportunity,'starter_action':starter,'reason':reason,'preview_opportunities':[d['title'] for d in ranked[:2]],'goal':answers1['goal'],'challenge_question':'اگر مخاطب فقط یک چیز را از تو به خاطر بسپارد، دوست داری چه باشد؟','instagram':instagram,'limitations':['این نتیجه یک تصویر کلی از وضعیت فعلی توست و قرار نیست ارزش یا توانایی‌ات را قضاوت کند.'],'immediate':[{'dimension':ranked[0]['key'],'title':starter,'evidence':ranked[0]['evidence']}],'thirty_days':[],'analysis_version':scoring['analysis_version']}

_legacy_validate_step=validate_step
_legacy_validate_template=validate_template
_legacy_validate_model=validate_model
_legacy_score=score

def validate_step(step, data, body):
    if body.get('schema') == 4:
        from personal_brand_v4 import validate
        return validate(step, data, body)
    return validate_step_v3(step, data, body) if body.get('schema') == 3 else _legacy_validate_step(step, data, body)


def validate_partial(step, data, body):
    if body.get('schema') == 4:
        from personal_brand_v4 import validate
        return validate(step, data, body, partial=True)
    return validate_partial_v3(step, data, body)

def validate_template(body):
    if body.get('schema') == 4:
        from personal_brand_v4 import validate_template as validate
        return validate(body)
    if body.get('schema')==3:
        original=template_v3()
        if set(body)!=set(original) or len(body.get('behavior',[]))!=15 or len(body.get('sections',[]))!=5:
            raise ValueError('قالب نسخهٔ جدید باید پنج بخش و ۱۵ سؤال داشته باشد.')
        for key in set(original) - {'title', 'behavior'}:
            if json.dumps(body[key], ensure_ascii=False, sort_keys=True) != json.dumps(original[key], ensure_ascii=False, sort_keys=True):
                raise ValueError('ساختار بخش‌ها و گزینه‌ها در این نسخه ثابت است.')
        clean(body['title'], 150, True)
        sources={q['id']:q for q in original['behavior']}
        ids=set(sources)
        for q in body['behavior']:
            if set(q)!=set(original['behavior'][0]) or q['id'] not in ids or q['dimension'] != sources[q['id']]['dimension'] or q['active'] is not True or q['weight'] != 1 or type(q['order']) is not int or not 0<=q['order']<15:
                raise ValueError('ساختار سؤال‌های نسخهٔ جدید معتبر نیست.')
            clean(q['title'],400,True)
        if len({q['id'] for q in body['behavior']})!=15 or len({q['order'] for q in body['behavior']})!=15: raise ValueError('ترتیب سؤال‌ها باید یکتا باشد.')
        return
    return _legacy_validate_template(body)
def validate_model(body):
    if body.get('schema') == 4:
        from personal_brand_v4 import validate_model as validate
        return validate(body)
    if body.get('schema')==3:
        expected = model_v3()
        if set(body) != set(expected) or not isinstance(body['dimensions'], dict) or set(body['dimensions']) != set(expected['dimensions']) or any(body[key] != expected[key] for key in ('schema', 'thresholds', 'method', 'analysis_version')):
            raise ValueError('مدل نمره‌دهی نسخهٔ جدید معتبر نیست.')
        weights = list(body['dimensions'].values())
        if any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in weights) or not math.isclose(sum(weights), 1, abs_tol=1e-6):
            raise ValueError('وزن‌های ابعاد باید مثبت و جمع آن‌ها یک باشد.')
        return
    return _legacy_validate_model(body)
def score(answers, body, scoring, instagram=None):
    if body.get('schema') == 4 or scoring.get('schema') == 4:
        if body.get('schema') != scoring.get('schema'):
            raise ValueError('نسخهٔ پاسخ‌ها با این نتیجه هماهنگ نیست.')
        from personal_brand_v4 import score as monthly_score
        return monthly_score(answers, body, scoring)
    if (body.get('schema') == 3) != (scoring.get('schema') == 3):
        raise ValueError('نسخهٔ مدل باید با نسخهٔ ارزیابی هماهنگ باشد.')
    return score_v3(answers, body, scoring, instagram) if body.get('schema') == 3 else _legacy_score(answers, body, scoring, instagram)
