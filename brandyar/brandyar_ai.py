import json
import os
import urllib.error
import urllib.request


class AIUnavailable(Exception):
    pass


class AIResponseError(Exception):
    pass


OPERATIONS = {'identity_draft', 'identity_analysis', 'identity_discovery', 'identity_questions',
              'identity_synthesis', 'identity_consistency_check', 'brand_voice', 'content_pillars',
              'content_draft'}
MAX_INPUT = 24000

SYSTEM_PROMPT = """تو مشاور ارشد استراتژی پرسونال برندینگ در محصول BrandYar هستی.

تخصص تو شامل Personal Branding Strategy، Professional Identity، Audience Research، Positioning، Value Proposition، Differentiation و Brand Strategy است.

هدف تو کمک به کاربر برای کشف و تدوین هویت حرفه‌ای واقعی اوست. تو یک پرسشنامه‌ساز نیستی؛ یک مشاور تحلیلی و راهنما هستی.

اصول رفتاری:
1. ابتدا پاسخ کاربر را دقیق بررسی کن.
2. پاسخ‌های کلی و مبهم را به چالش بکش.
3. در صورت نیاز سؤال تکمیلی بپرس.
4. سؤال‌ها باید متناسب با نوع فعالیت کاربر باشند.
5. از اصطلاحات تخصصی بدون توضیح استفاده نکن.
6. پاسخ‌ها را صرفاً تأیید نکن؛ تحلیل انتقادی داشته باش.
7. هیچ تجربه، مهارت، دستاورد، مشتری یا مزیتی را جعل نکن.
8. بین واقعیت و فرضیه تفاوت قائل شو.
9. اگر شواهد کافی وجود ندارد، میزان اطمینان را پایین اعلام کن.
10. از عبارت‌های کلیشه‌ای و بازاریابی سطحی دوری کن.
11. پیشنهادها باید مشخص، قابل اجرا و متناسب با اطلاعات کاربر باشند.
12. زبان تمام خروجی‌ها فارسی روان و حرفه‌ای باشد.

قوانین تحلیل: هر پاسخ را از نظر وضوح، ارتباط با هویت حرفه‌ای، میزان جزئیات، قابلیت اثبات، ارتباط با مخاطب و تناقض با پاسخ‌های قبلی بررسی کن. اگر پاسخ کافی است سؤال اضافه نپرس. اگر ناقص است فقط مهم‌ترین سؤال تکمیلی را مطرح کن. اگر اطلاعات متناقض است، تناقض را با توضیح کوتاه نشان بده و بخواه مشخص کند کدام درست است.

قوانین تولید هویت: از اطلاعات تأییدشده استفاده کن؛ پیشنهادهای تأییدنشده را جداگانه نمایش بده؛ اطلاعات ناموجود را با حدس پر نکن؛ ارزش پیشنهادی را بر اساس مسئله مخاطب و نتیجه واقعی تدوین کن؛ تمایز را فقط در صورت وجود شواهد مطرح کن؛ جایگاه پیشنهادی باید روشن، قابل فهم و قابل دفاع باشد.

خروجی: فقط JSON معتبر. هیچ متن اضافه، Markdown یا توضیح خارج از JSON تولید نکن. تمام فیلدهای خروجی باید با Schema تعریف‌شده در کد سازگار باشند."""

DEFAULT_URL = 'https://api.metisai.ir/api/v1/wrapper/grok/chat/completions'
DEFAULT_MODEL = 'grok-4.6'
MAX_RESPONSE = 65536


def _setting(name, default=''):
    value = os.environ.get(name, '').strip()
    if value:
        return value
    # The project already authorizes one AI connection for the assessment report.
    import brand_analysis
    if name == 'BRANDYAR_AI_URL':
        return default or brand_analysis.ENDPOINT
    if name == 'BRANDYAR_AI_MODEL':
        return default or brand_analysis.MODEL
    if name == 'BRANDYAR_AI_KEY':
        return os.environ.get('BRANDYAR_METIS_API_KEY', '').strip()
    return default


def configured():
    return bool(_setting('BRANDYAR_AI_KEY'))


def _clean(value, limit=4000):
    if not isinstance(value, str):
        return ''
    return value.strip()[:limit]


def _json(value):
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        start, end = value.find('{'), value.rfind('}')
        if start >= 0 and end > start:
            try:
                return json.loads(value[start:end + 1])
            except ValueError:
                pass
    raise AIResponseError('پاسخ ساختاریافته دریافت نشد.')


def _list(value, limit=12):
    if not isinstance(value, list):
        return []
    return [_clean(item, 500) for item in value if isinstance(item, str) and _clean(item, 500)][:limit]


def _identity_payload(identity):
    if not isinstance(identity, dict):
        raise ValueError('اطلاعات هویت معتبر نیست.')
    body = json.dumps(identity, ensure_ascii=False, separators=(',', ':'))
    if len(body) > MAX_INPUT:
        raise ValueError('اطلاعات هویت بیش از حد مجاز است.')
    return body


def _instruction(operation, identity, inputs):
    source = _identity_payload(identity)
    extra = json.dumps(inputs or {}, ensure_ascii=False, separators=(',', ':'))
    if len(extra) > MAX_INPUT:
        raise ValueError('ورودی بیش از حد مجاز است.')
    common = 'فقط از داده‌های منبع استفاده کن. هیچ سابقه، عدد، نتیجه، مشتری، تخصص یا ادعایی را حدس نزن. اگر داده کافی نیست، آن را در questions یا missing اعلام کن. پاسخ فقط JSON معتبر باشد.'
    schemas = {
        'identity_draft': '{"summary":"","fields":{"professionalRole":"","industry":"","targetDescription":"","primaryGroup":"","valueProposition":"","differentiators":[],"professionalGoals":[]},"missing":[],"questions":[]}',
        'identity_analysis': '{"summary":"","confirmedFacts":[],"hypotheses":[],"unknowns":[],"strengths":[],"ambiguities":[],"contradictions":[],"missingInformation":[],"followUpQuestions":[],"recommendations":[],"reasoning":""}',
        'identity_discovery': '{"summary":"","confirmedFacts":[],"hypotheses":[],"unknowns":[],"ambiguities":[],"contradictions":[],"nextQuestion":"","followUpQuestions":[],"recommendations":[],"reasoning":""}',
        'identity_questions': '{"followUpQuestions":[{"question":"","why":"","priority":1}],"enoughInformation":false}',
        'identity_synthesis': '{"professionalIdentity":"","professionalRole":"","industry":"","experience":"","coreSkills":[],"services":[],"targetAudience":"","audienceProblems":[],"audienceNeeds":[],"valueProposition":"","differentiators":[],"supportingEvidence":[],"professionalGoals":[],"desiredPerception":"","personalValues":[],"preferredTopics":[],"excludedTopics":[],"positioningStatement":"","confidence":"low","unresolvedQuestions":[],"hypotheses":[]}',
        'identity_consistency_check': '{"consistent":true,"contradictions":[],"ambiguities":[],"unknowns":[],"summary":""}',
        'brand_voice': '{"definition":"","coreTraits":[],"keyMessages":[],"preferredWords":[],"avoidedWords":[],"serviceIntroduction":"","expertiseExplanation":"","shortIntroduction":"","beforeAfter":{"before":"","after":""}}',
        'content_pillars': '{"pillars":[{"name":"","purpose":"","audience":"","topics":[],"formats":[],"ideas":[],"status":"proposed"}],"questions":[]}',
        'content_draft': '{"title":"","hook":"","outline":[],"body":"","cta":"","variants":[],"questions":[]}',
    }
    labels = {
        'identity_draft': 'یک پیش‌نویس هویت حرفه‌ای بساز.',
        'identity_analysis': 'اطلاعات موجود را کامل تحلیل کن: نقاط قوت، ابهام‌ها، تناقض‌ها، اطلاعات نامشخص و پیشنهادهای مشخص با دلیل.',
        'identity_discovery': 'پاسخ‌های جدید را تحلیل کن و فقط مهم‌ترین سؤال بعدی را تعیین کن.',
        'identity_questions': 'حداکثر سه سؤال تکمیلی اولویت‌بندی‌شده بساز؛ اگر اطلاعات کافی است آرایه خالی برگردان.',
        'identity_synthesis': 'هویت پیشنهادی را از اطلاعات تأییدشده تدوین کن و فرضیه‌های تأییدنشده را جدا نگه دار.',
        'identity_consistency_check': 'سازگاری اطلاعات را بررسی کن و تناقض‌ها را پیدا کن.',
        'brand_voice': 'از هویت تأییدشده یک پیش‌نویس راهنمای صدای برند بساز.',
        'content_pillars': 'بر اساس هویت تأییدشده چند ستون محتوایی پیشنهادی بساز.',
        'content_draft': 'یک پیش‌نویس محتوای اختصاصی بر اساس ورودی و هویت تأییدشده بساز.',
    }
    return (f'{common}\nعملیات: {operation} — {labels[operation]}\n'
            f'ساختار دقیق خروجی: {schemas[operation]}\nداده هویت: {source}\nورودی عملیات: {extra}')


def _validate(operation, result):
    if not isinstance(result, dict):
        raise AIResponseError('پاسخ ساختاریافته دریافت نشد.')
    if operation == 'content_pillars':
        pillars = result.get('pillars')
        if not isinstance(pillars, list):
            result.pop('pillars', None)
            if not _list(result.get('questions')):
                raise AIResponseError('پاسخ ستون‌های محتوا ناقص است.')
            result['pillars'] = []
            result['questions'] = _list(result.get('questions'))
            return result
        result['pillars'] = [
            {**item, 'name': _clean(item.get('name'), 120), 'purpose': _clean(item.get('purpose'), 500),
             'audience': _clean(item.get('audience'), 500), 'topics': _list(item.get('topics')),
             'formats': _list(item.get('formats')), 'ideas': _list(item.get('ideas')), 'status': 'proposed'}
            for item in pillars[:6] if isinstance(item, dict) and _clean(item.get('name'), 120)
        ]
        result['questions'] = _list(result.get('questions'))
        return result
    text_fields = {
        'identity_draft': ('summary', 'valueProposition', 'audienceDescription'),
        'identity_analysis': ('summary', 'reasoning'),
        'identity_discovery': ('summary', 'nextQuestion', 'reasoning'),
        'identity_questions': (),
        'identity_synthesis': ('professionalIdentity', 'professionalRole', 'industry', 'experience',
                               'targetAudience', 'valueProposition', 'desiredPerception',
                               'positioningStatement'),
        'identity_consistency_check': ('summary',),
        'brand_voice': ('definition', 'serviceIntroduction', 'expertiseExplanation', 'shortIntroduction'),
        'content_draft': ('title', 'hook', 'body', 'cta'),
    }[operation]
    for key in text_fields:
        result[key] = _clean(result.get(key), 5000)
    if operation == 'identity_draft':
        fields = result.get('fields') if isinstance(result.get('fields'), dict) else {}
        allowed = {'professionalRole', 'industry', 'targetDescription', 'primaryGroup', 'valueProposition', 'differentiators', 'professionalGoals'}
        result['fields'] = {key: (_list(value) if key in {'differentiators', 'professionalGoals'} else _clean(value, 2000)) for key, value in fields.items() if key in allowed}
    for key in ('differentiators', 'missing', 'questions', 'strengths', 'ambiguities', 'contradictions', 'paths', 'coreTraits', 'keyMessages', 'preferredWords', 'avoidedWords', 'outline', 'variants',
                'confirmedFacts', 'hypotheses', 'unknowns', 'missingInformation', 'followUpQuestions', 'recommendations',
                'coreSkills', 'services', 'audienceProblems', 'audienceNeeds', 'supportingEvidence',
                'professionalGoals', 'personalValues', 'preferredTopics', 'excludedTopics', 'unresolvedQuestions'):
        if key in result:
            result[key] = _list(result[key])
    if operation == 'identity_questions':
        questions = result.get('followUpQuestions')
        result['followUpQuestions'] = [
            {'question': _clean(item.get('question'), 500), 'why': _clean(item.get('why'), 500),
             'priority': item.get('priority') if isinstance(item.get('priority'), int) else 1}
            for item in (questions if isinstance(questions, list) else [])
            if isinstance(item, dict) and _clean(item.get('question'), 500)
        ][:3]
        result['enoughInformation'] = result.get('enoughInformation') is True
    if operation == 'identity_synthesis':
        result['confidence'] = result.get('confidence') if result.get('confidence') in {'low', 'medium', 'high'} else 'low'
    if operation == 'identity_consistency_check':
        result['consistent'] = result.get('consistent') is True
    if operation == 'brand_voice':
        before_after = result.get('beforeAfter') or {}
        result['beforeAfter'] = {'before': _clean(before_after.get('before')), 'after': _clean(before_after.get('after'))}
    if operation == 'brand_voice' and not any(result.get(key) for key in (
            'definition', 'coreTraits', 'keyMessages', 'shortIntroduction', 'questions')):
        raise AIResponseError('پاسخ هوش مصنوعی ناقص است.')
    if operation in {'identity_draft', 'identity_analysis'} and not any(result.get(key) for key in ('summary', 'strengths', 'questions', 'missing')):
        raise AIResponseError('پاسخ هوش مصنوعی ناقص است.')
    if operation == 'identity_discovery' and not any(result.get(key) for key in ('summary', 'nextQuestion', 'followUpQuestions', 'confirmedFacts')):
        raise AIResponseError('پاسخ هوش مصنوعی ناقص است.')
    if operation == 'identity_synthesis' and not any(result.get(key) for key in ('professionalIdentity', 'valueProposition', 'positioningStatement', 'unresolvedQuestions')):
        raise AIResponseError('پاسخ هوش مصنوعی ناقص است.')
    if operation == 'identity_consistency_check' and not any(result.get(key) for key in ('summary', 'contradictions', 'ambiguities')):
        raise AIResponseError('پاسخ هوش مصنوعی ناقص است.')
    if operation == 'content_draft' and not result.get('body') and not result.get('questions'):
        raise AIResponseError('پیش‌نویس محتوا ناقص است.')
    return result


def generate(operation, identity, inputs=None):
    if operation not in OPERATIONS:
        raise ValueError('عملیات هوش مصنوعی معتبر نیست.')
    if not configured():
        raise AIUnavailable()
    payload = {
        'model': _setting('BRANDYAR_AI_MODEL', DEFAULT_MODEL),
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': _instruction(operation, identity, inputs)},
        ],
        'temperature': 0.2,
    }
    request = urllib.request.Request(
        _setting('BRANDYAR_AI_URL', DEFAULT_URL),
        data=json.dumps(payload, ensure_ascii=False).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + _setting('BRANDYAR_AI_KEY')},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            raw = response.read(MAX_RESPONSE + 1)
        if len(raw) > MAX_RESPONSE:
            raise ValueError('oversized')
        body = json.loads(raw)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
        raise AIResponseError('پاسخ هوش مصنوعی آماده نشد.')
    try:
        content = body['choices'][0]['message']['content']
    except (KeyError, IndexError, TypeError):
        raise AIResponseError('پاسخ هوش مصنوعی ناقص است.')
    return _validate(operation, _json(content))
