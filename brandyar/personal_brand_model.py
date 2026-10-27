import copy
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
