import copy
import math
from urllib.parse import urlsplit

TITLE = 'ارزیابی ساختاریافتهٔ پرسونال برند'
LIKERT = ['کاملاً مخالفم', 'مخالفم', 'نه موافقم نه مخالفم', 'موافقم', 'کاملاً موافقم']
GOALS = ['جذب مشتری یا پروژه', 'فروش محصول یا خدمت', 'افزایش اعتبار تخصصی', 'استخدام یا رشد شغلی', 'ساخت جامعهٔ مخاطبان', 'آموزش و اثرگذاری', 'همکاری تجاری', 'تبدیل‌شدن به مرجع یک موضوع', 'سایر']
DIMENSIONS = [
    ('identity', 'وضوح هویت حرفه‌ای', 'وضوح تخصص، ارزش و مسیر حرفه‌ای', ['برای فعالیت حرفه‌ای خود هدف مشخصی دارم.', 'می‌توانم ارزش خدمتم را در یک جمله توضیح دهم.', 'ارزش‌های اصلی کار حرفه‌ای‌ام را مشخص کرده‌ام.'], 'یک جملهٔ روشن دربارهٔ تخصص، مخاطب و ارزش خود بنویسید.', 'جملهٔ معرفی را با بازخورد پنج مخاطب بازنگری کنید.'),
    ('position', 'جایگاه‌یابی و شناخت مخاطب', 'شناخت مسئله و مخاطب مناسب', ['گروه اصلی مخاطبانم را مشخص کرده‌ام.', 'مسئلهٔ اولویت‌دار مخاطبم را می‌شناسم.', 'از مخاطب دربارهٔ نیازهایش بازخورد می‌گیرم.'], 'یک گروه مخاطب و یک مسئلهٔ اولویت‌دار انتخاب کنید.', 'با پنج مخاطب مصاحبه و مسئلهٔ اصلی را مستند کنید.'),
    ('credibility', 'اعتبار و شواهد تخصص', 'وجود نمونه و نتیجهٔ قابل بررسی', ['نمونه‌هایی برای نمایش نتیجهٔ کارم دارم.', 'در محتوا شواهد مرتبط با تخصصم ارائه می‌کنم.', 'برای توسعهٔ مهارتم برنامهٔ مشخصی دارم.'], 'یک نمونه‌کار همراه با مسئله، اقدام و نتیجه آماده کنید.', 'سه مطالعهٔ موردی با اجازهٔ صاحبان داده منتشر کنید.'),
    ('message', 'پیام، روایت و لحن', 'انسجام پیام و شناخت‌پذیری روایت', ['پیام اصلی معرفی‌ام در کانال‌های مختلف ثابت است.', 'برای محتوایم لحن مشخصی انتخاب کرده‌ام.', 'هر محتوا را حول یک پیام اصلی سازمان می‌دهم.'], 'یک پیام مرکزی و سه ویژگی لحن خود را مشخص کنید.', 'ده محتوای اخیر را از نظر پیام مرکزی بازنگری کنید.'),
    ('digital', 'اجرای دیجیتال و انسجام محتوا', 'انتخاب موضوع، استمرار و کیفیت مسیر اقدام', ['موضوعات محتوا را بر اساس تخصصم انتخاب می‌کنم.', 'برنامهٔ قابل اجرا برای انتشار منظم دارم.', 'می‌دانم کدام قالب محتوا برای پیامم مؤثرتر است.'], 'سه ستون محتوا و برنامهٔ انتشار قابل اجرا بنویسید.', 'دو قالب محتوا را با موضوع مشابه آزمایش و نتیجه را ثبت کنید.'),
    ('growth', 'دیده‌شدن، تمایز و ظرفیت رشد', 'تمایز، فراخوان اقدام و یادگیری از داده', ['تفاوت روش کارم با گزینه‌های دیگر را توضیح می‌دهم.', 'برای مخاطب مسیر روشن اقدام بعدی دارم.', 'ترندها را فقط در صورت ارتباط با تخصصم انتخاب می‌کنم.'], 'در یک محتوا اقدام بعدی مشخص و مرتبط تعریف کنید.', 'نرخ اقدام مخاطب و بازخوردهای مرتبط را چهار هفته دنبال کنید.'),
]
BASE = [
    ('expertise', 'حوزهٔ فعالیت یا تخصص اصلی', True), ('professional_status', 'وضعیت حرفه‌ای فعلی', True),
    ('offering', 'خدمت، محصول یا ارزشی که ارائه می‌دهید', True), ('audience', 'مخاطب اصلی', True),
    ('problem', 'مسئلهٔ اصلی مخاطب', True), ('channels', 'کانال‌های اصلی فعالیت', False),
    ('career_stage', 'مرحلهٔ فعلی فعالیت حرفه‌ای', False), ('barrier', 'مهم‌ترین مانع رشد', False),
]
IDENTITY = [
    ('remember', 'دوست دارید مخاطب با شنیدن نام شما چه جمله‌ای به یاد بیاورد؟', True),
    ('difference', 'چه چیزی در تجربه، نگاه یا روش کارتان متفاوت است؟', True),
    ('one_problem', 'اگر فقط یک مسئله حل کنید، آن مسئله چیست؟', True),
    ('best_audience', 'چه کسانی بیشترین ارزش را از محتوای شما می‌گیرند؟', True),
    ('not_audience', 'چه افرادی مخاطب مناسب شما نیستند؟', False),
    ('values', 'کدام ارزش‌ها نباید در برند شما نادیده گرفته شوند؟', True),
]
EVIDENCE = [
    ('topics', 'سه موضوع اصلی محتوای شما'), ('problems', 'سه مسئله‌ای که برای مخاطب حل می‌کنید'),
    ('proof', 'شواهد اعتبار: تجربه، نمونه‌کار، نتیجه یا سابقه'), ('proud_content', 'یک محتوای موفق یا موردافتخار'),
    ('weak_content', 'یک محتوا که انتظار عملکرد بهتری از آن داشتید'), ('portfolio_url', 'لینک وب‌سایت، رزومه یا نمونه‌کار'),
    ('execution_barriers', 'موانع اجرایی فعلی'),
]


def template():
    items = [{'id': f'{key}_{i+1}', 'dimension': key, 'title': title} for key, _, _, questions, _, _ in DIMENSIONS for i, title in enumerate(questions)]
    return {'title': TITLE, 'base': BASE, 'identity': IDENTITY, 'evidence': EVIDENCE, 'goals': GOALS, 'items': items, 'likert': LIKERT, 'validation': 'not_validated', 'purpose': 'خودبازنگری حرفه‌ای، نه استخدام یا تشخیص شخصیت', 'population': 'بزرگسالان دارای فعالیت حرفه‌ای', 'limitations': 'روایی و پایایی آماری هنوز تأیید نشده‌اند.'}


def model():
    return {'dimensions': {d[0]: 1 / 6 for d in DIMENSIONS}, 'source_weights': {'self_report': 1, 'evidence': 0, 'instagram': 0}, 'thresholds': [20, 40, 60, 80], 'method': 'likert-linear-v1', 'analysis_version': 'structured-rules-v1'}


def clean(value, maximum=1200, required=False):
    if not isinstance(value, str) or len(value) > maximum or any(ord(c) < 32 and c not in '\n\t\r' for c in value):
        raise ValueError('متن واردشده معتبر نیست یا بیش از حد طولانی است.')
    value = value.strip()
    if required and not value:
        raise ValueError('لطفاً فیلدهای الزامی را تکمیل کنید.')
    return value


def validate_step(step, data, body):
    if not isinstance(data, dict):
        raise ValueError('قالب پاسخ معتبر نیست.')
    if step in (1, 2, 4):
        fields = body['base'] if step == 1 else body['identity'] if step == 2 else [(k, t, False) for k, t in body['evidence']]
        allowed = {f[0] for f in fields} | ({'goal'} if step == 1 else set())
        if set(data) - allowed:
            raise ValueError('فیلد ناشناخته در پاسخ وجود دارد.')
        result = {key: clean(data.get(key, ''), 1200, required) for key, _, required in fields}
        if step == 1:
            if data.get('goal') not in body['goals']:
                raise ValueError('هدف برند را انتخاب کنید.')
            result['goal'] = data['goal']
        if step == 4 and result.get('portfolio_url'):
            url = urlsplit(result['portfolio_url'])
            if url.scheme != 'https' or not url.hostname or url.username or url.password:
                raise ValueError('لینک نمونه‌کار باید یک آدرس HTTPS معتبر باشد.')
        return result
    if step == 3:
        ids = {q['id'] for q in body['items']}
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
        raise ValueError('فیلدهای نسخهٔ تست کامل نیستند.')
    for key in ('base', 'identity', 'evidence', 'goals', 'likert'):
        if body[key] != copy.deepcopy(original[key]) and body[key] != [list(v) if isinstance(v, tuple) else v for v in original[key]]:
            raise ValueError('در این نسخه، ساختار مراحل ثابت است؛ متن گویه‌ها قابل ویرایش است.')
    if len(body.get('items', [])) != 18:
        raise ValueError('تست باید ۱۸ گویه داشته باشد.')
    for q, source in zip(body['items'], original['items']):
        if set(q) != {'id', 'dimension', 'title'} or q['id'] != source['id'] or q['dimension'] != source['dimension']:
            raise ValueError('کلید و بُعد گویهٔ نسخه‌دار باید ثابت بماند.')
        clean(q['title'], 400, True)
    clean(body['title'], 150, True)


def validate_model(body):
    if not isinstance(body, dict) or set(body) != set(model()) or not isinstance(body['dimensions'], dict) or set(body['dimensions']) != {d[0] for d in DIMENSIONS}:
        raise ValueError('مدل نمره‌دهی معتبر نیست.')
    weights = list(body['dimensions'].values())
    if any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in weights) or not math.isclose(sum(weights), 1, abs_tol=1e-6):
        raise ValueError('وزن‌های ابعاد باید مثبت و جمع آن‌ها یک باشد.')
    if body['source_weights'] != model()['source_weights'] or body['thresholds'] != model()['thresholds'] or body['method'] != 'likert-linear-v1' or body['analysis_version'] != 'structured-rules-v1':
        raise ValueError('تغییر روش تحلیل نیازمند پیاده‌سازی نسخهٔ موتور است.')


def score(answers, body, scoring, instagram=None):
    validate_model(scoring)
    values = validate_step(3, answers[3], body)
    dimensions = []
    for key, title, description, _, immediate, month in DIMENSIONS:
        ids = [q['id'] for q in body['items'] if q['dimension'] == key]
        value = round(sum((values[q] - 1) * 25 for q in ids) / len(ids), 2)
        dimensions.append({'key': key, 'title': title, 'description': description, 'score': value, 'evidence': ids, 'immediate': immediate, 'month': month, 'interpretation': 'اولویت بهبود' if value < 40 else 'در حال شکل‌گیری' if value < 70 else 'نقطهٔ قوت خوداظهارشده'})
    total = round(sum(d['score'] * scoring['dimensions'][d['key']] for d in dimensions), 2)
    stage = ['کشف', 'تعریف', 'تثبیت', 'تمایز', 'مرجعیت'][sum(total >= threshold for threshold in scoring['thresholds'])]
    ranked = sorted(dimensions, key=lambda d: d['score'])
    has_evidence = bool(answers.get(4, {}).get('proof') or answers.get(4, {}).get('portfolio_url'))
    confidence = 'خوداظهاری به‌همراه شواهد' if has_evidence or instagram else 'خوداظهاری'
    goal = answers[1]['goal']
    pattern = {'آموزش و اثرگذاری': 'مدرس و توانمندساز', 'ساخت جامعهٔ مخاطبان': 'برند مبتنی بر جامعه', 'فروش محصول یا خدمت': 'برند محصول‌محور', 'تبدیل‌شدن به مرجع یک موضوع': 'رهبر فکری', 'جذب مشتری یا پروژه': 'متخصص مسئله‌محور', 'همکاری تجاری': 'مشاور و راهبر', 'استخدام یا رشد شغلی': 'سازنده و مجری'}.get(goal, 'برند ترکیبی')
    return {'title': TITLE, 'dimensions': dimensions, 'total': total, 'stage': stage, 'confidence': confidence, 'pattern': 'الگوی احتمالی: ' + pattern, 'secondary_patterns': [], 'strength': ranked[-1]['title'], 'bottleneck': ranked[0]['title'], 'central_message': f"در حوزهٔ {answers[1]['expertise']} به {answers[1]['audience']} برای {answers[1]['problem']} کمک می‌کنم.", 'identity': answers[2], 'professional': answers[1], 'source_weights': scoring['source_weights'], 'immediate': [{'dimension': d['key'], 'title': d['immediate'], 'evidence': d['evidence']} for d in ranked[:3]], 'thirty_days': [{'dimension': d['key'], 'title': d['month'], 'evidence': d['evidence']} for d in ranked[:3]], 'instagram': instagram, 'limitations': ['این ابزار هنوز اعتبارسنجی روان‌سنجی نشده است.', 'نمره‌ها فقط بر پایهٔ رفتارهای خوداظهارشده‌اند؛ شواهد و پیج به‌صورت زمینهٔ مکمل استفاده می‌شوند.', 'متن شواهد و لینک‌ها اثبات مستقل صحت ادعا نیستند.', 'تحلیل تصویر، ویدیو، شخصیت و ویژگی حساس انجام نشده است.', 'مرحلهٔ بلوغ و الگوی برند فرضیهٔ راهنما هستند، نه حکم قطعی.'], 'analysis_version': scoring['analysis_version']}
