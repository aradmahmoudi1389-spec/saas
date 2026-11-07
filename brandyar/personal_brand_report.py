import json
from pathlib import Path
import time


ACTIONS = {
    'clarity': 'یک جمله بنویس که بگوید در چه زمینه‌ای به چه کسی کمک می‌کنی؛ آن را برای یک نفر از مخاطبان مدنظرت بخوان و بپرس چه برداشتی داشته است.',
    'evidence': 'یک تجربه یا نمونه‌کار واقعی را با سه بخش مسئله، کار انجام‌شده و نتیجه مستند کن؛ اگر نمونه‌ای نداری، از یک تمرین کوچک شروع کن.',
    'consistency': 'معرفی خودت و سه محتوای اخیرت را کنار هم بگذار؛ یک موضوع مشترک پیدا کن و بخش‌های نامرتبط را برای بازنگری علامت بزن.',
    'execution': 'یک فعالیت کوچک و قابل‌تکرار انتخاب کن؛ پس از انجام آن یک پرسش از مخاطب بپرس و بازخورد واقعی را یادداشت کن.',
    'differentiation': 'یک دلیل قابل‌اثبات برای انتخاب کارت بنویس و راه سادهٔ ارتباط یا پرسیدن سؤال را کنار آن قرار بده.',
}


def saved_phone(db, owner, normalize):
    row = db.execute('SELECT body FROM pb_account_details WHERE owner_hash=?', (owner,)).fetchone()
    if not row:
        return None
    try:
        return normalize(json.loads(row['body']).get('phone'))
    except ValueError:
        return None


def flow_state(db, owner, assessment_id, normalize):
    phone = saved_phone(db, owner, normalize)
    registered = db.execute('SELECT 1 FROM pb_leads WHERE owner_hash=? AND assessment_id=?', (owner, assessment_id)).fetchone() is not None
    return {'phoneRegistered': registered, 'savedPhoneMasked': phone[:4] + '•••••' + phone[-2:] if phone else None}


def offer(db, owner):
    import brandyar_profile
    access = brandyar_profile.access(db, owner)
    settings = json.loads(Path(__file__).with_name('report-offer.json').read_text())
    return {'hasAccess': access['status'] in ('active', 'trial'), 'href': '/brandyar/dashboard' if access['status'] in ('active', 'trial') else '/brandyar/plans',
            'checkoutAvailable': False, 'discount': None,
            'configurationPending': not settings['enabled'] or not settings['checkout_enabled']}


def source(db, owner, assessment_id):
    row = db.execute('SELECT v.id,v.body,v.input_json FROM pb_report_versions v JOIN pb_reports r ON r.id=v.report_id JOIN pb_assessments a ON a.id=r.assessment_id WHERE a.id=? AND a.owner_hash=? AND a.state=\'completed\' AND a.archived_at IS NULL ORDER BY v.version DESC LIMIT 1', (assessment_id, owner)).fetchone()
    if not row:
        raise LookupError('گزارش اولیه موجود نیست؛ ابتدا ارزیابی را کامل کنید.')
    return row


def build(report, snapshot):
    if report.get('analysis_version') != 'monthly-behavior-v4':
        raise ValueError('گزارش تکمیلی برای این نسخهٔ قدیمی تست در دسترس نیست؛ نتیجهٔ قبلی حفظ شده است.')
    answers = snapshot['answers']
    behavior = answers.get('3', {})
    template = snapshot['template']
    bank = {question['id']: question for question in template['behavior']}
    dimensions = []
    for dimension in report['dimensions']:
        evidence = [{'question': bank[key]['title'], 'answer': template['likert'][behavior[key] - 1]} for key in dimension['evidence']]
        ordered = sorted(dimension['evidence'], key=lambda key: behavior[key])
        dimensions.append({'key': dimension['key'], 'title': dimension['title'], 'score': dimension['score'], 'evidence': evidence,
                           'observation': 'در این بُعد، انتخاب‌های ثبت‌شدهٔ یک ماه اخیر شما مبنای امتیاز موجود هستند؛ این امتیاز سنجش ارزش یا شخصیت شما نیست.',
                           'evidenceVaries': behavior[ordered[-1]] != behavior[ordered[0]],
                           'strongerBehavior': bank[ordered[-1]]['title'], 'strongerAnswer': template['likert'][behavior[ordered[-1]] - 1],
                           'reviewBehavior': bank[ordered[0]]['title'], 'reviewAnswer': template['likert'][behavior[ordered[0]] - 1],
                           'suggestion': ACTIONS[dimension['key']]})
    base, proof, online = answers['1'], answers['4'], answers['5']
    priorities = [{'dimension': d['title'], 'observation': 'این بُعد در میان امتیازهای همین ارزیابی، در اولویت مرور قرار گرفته است؛ ترتیب در امتیازهای برابر به معنی تفاوت قطعی نیست.', 'action': d['suggestion']} for d in sorted(dimensions, key=lambda d: d['score'])[:3]]
    facts = [{'label': 'حوزهٔ فعالیت انتخاب‌شده', 'value': base.get('field_other') or base['field']},
             {'label': 'مخاطبان انتخاب‌شده', 'value': base.get('audience_other') or '، '.join(base['audience'])},
             {'label': 'هدف انتخاب‌شده', 'value': base.get('primary_goal_other') or base['primary_goal']},
             {'label': 'شواهدی که گفته‌اید در اختیار دارید', 'value': '، '.join(proof['available_proof'])},
             {'label': 'کانال اصلی انتخاب‌شده', 'value': online.get('primary_channel_other') or online['primary_channel']}]
    if proof.get('proud_work'):
        facts.append({'label': 'نمونه‌ای که خودتان معرفی کرده‌اید', 'value': proof['proud_work']})
    result = {'schema': 1, 'summary': report['summary'], 'strength': report['strength'], 'improvement': report['top_opportunity'],
              'dimensions': dimensions, 'facts': facts, 'priorities': priorities, 'nextStep': report['starter_action'],
              'reflection': report['challenge_question'], 'limitations': [report['disclaimer'], 'این گزارش بر پاسخ‌های خوداظهاری همین تست متکی است؛ محتوای واقعی و نتیجهٔ اجرای پیشنهادها بررسی نشده است.', 'بخش «مشاهده» پاسخ ثبت‌شده را بیان می‌کند؛ بخش «پیشنهاد» یک تفسیر عملی و قابل‌آزمایش است، نه پیش‌بینی یا تضمین رشد.', 'برابری امتیازها و تفاوت‌های کوچک، برای نتیجه‌گیری قطعی کافی نیستند.']}
    if len(dimensions) != 5 or any(not d['evidence'] or not 0 <= d['score'] <= 100 for d in dimensions):
        raise ValueError('دادهٔ کافی برای گزارش معتبر وجود ندارد.')
    return result


def get_report(db, owner, assessment_id, generate=False):
    if not db.execute('SELECT 1 FROM pb_leads WHERE owner_hash=? AND assessment_id=?', (owner, assessment_id)).fetchone():
        raise PermissionError('برای دریافت گزارش کامل، ابتدا شمارهٔ موبایل را ثبت کنید.')
    original = source(db, owner, assessment_id)
    stored = db.execute('SELECT body FROM pb_full_reports WHERE source_version=? AND owner_hash=?', (original['id'], owner)).fetchone()
    if stored:
        return json.loads(stored['body'])
    if not generate:
        raise LookupError('گزارش تکمیلی هنوز آماده نشده است؛ از دکمهٔ آماده‌سازی گزارش استفاده کنید.')
    result = build(json.loads(original['body']), json.loads(original['input_json']))
    result['sourceVersion'] = original['id']
    result['createdAt'] = int(time.time())
    db.execute('INSERT INTO pb_full_reports VALUES(?,?,?,?)', (original['id'], owner, json.dumps(result, ensure_ascii=False), result['createdAt']))
    return result
