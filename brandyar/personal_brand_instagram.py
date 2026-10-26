import json
import os
import re
from collections import Counter
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

import personal_brand as pb


class Unavailable(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def configured():
    try:
        from cryptography.fernet import Fernet
        Fernet(os.environ.get('PB_TOKEN_ENCRYPTION_KEY', '').encode())
        callback = urlsplit(os.environ.get('META_INSTAGRAM_REDIRECT_URI', ''))
        return bool(os.environ.get('META_INSTAGRAM_APP_ID') and os.environ.get('META_INSTAGRAM_APP_SECRET') and re.fullmatch(r'v\d+\.\d+', os.environ.get('META_GRAPH_VERSION', '')) and callback.scheme == 'https' and callback.path == '/api/personal-brand/instagram/callback' and callback.hostname and not callback.username and not callback.password and not callback.query and not callback.fragment)
    except (ImportError, ValueError):
        return False


def cipher():
    from cryptography.fernet import Fernet
    return Fernet(os.environ['PB_TOKEN_ENCRYPTION_KEY'].encode())


def request(url, data=None, token=None):
    headers = {'Accept': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    if data is not None:
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    try:
        with build_opener(NoRedirect()).open(Request(url, data=urlencode(data).encode() if data is not None else None, headers=headers), timeout=15) as response:
            raw = response.read(1048577)
            if len(raw) > 1048576:
                raise Unavailable()
            result = json.loads(raw)
            if not isinstance(result, dict) or 'error' in result:
                raise Unavailable()
            return result
    except (HTTPError, URLError, OSError, ValueError):
        raise Unavailable() from None


def graph(path, fields, token, limit=None):
    query = {'fields': fields}
    if limit:
        query['limit'] = limit
    return request('https://graph.instagram.com/' + os.environ['META_GRAPH_VERSION'] + '/' + path + '?' + urlencode(query), token=token)


def begin(db, owner, data):
    if not configured():
        raise Unavailable()
    if data.get('consent') is not True:
        raise ValueError('رضایت اتصال لازم است.')
    state = pb.secrets.token_urlsafe(32)
    consent = pb.uid()
    db.execute('DELETE FROM pb_oauth_states WHERE owner_hash=? OR expires<?', (owner, pb.now()))
    db.execute('INSERT INTO pb_consents VALUES(?,?,?,?,?,?,?,?,NULL)', (consent, owner, 'instagram_text', '1', '1', 'instagram_business_basic', 'تحلیل محتوای متنی حساب حرفه‌ای متصل‌شده', pb.now()))
    db.execute('INSERT INTO pb_oauth_states VALUES(?,?,?,?,?)', (pb.digest(state), owner, consent, pb.now() + 600, pb.now()))
    pb.event(db, owner, None, 'oauth_started', 'oauth:' + pb.digest(state))
    db.commit()
    return {'authorization_url': 'https://www.instagram.com/oauth/authorize?' + urlencode({'client_id': os.environ['META_INSTAGRAM_APP_ID'], 'redirect_uri': os.environ['META_INSTAGRAM_REDIRECT_URI'], 'scope': 'instagram_business_basic', 'response_type': 'code', 'state': state, 'enable_fb_login': '0', 'force_authentication': '1'})}


def callback(handler, connect):
    from urllib.parse import parse_qs
    query = parse_qs(urlsplit(handler.path).query)
    outcome = 'failed'
    principal = None
    try:
        with connect() as db:
            principal = pb.session(handler, db)
            state = query.get('state', [''])[0]
            if not principal or len(state) > 256:
                raise Unavailable()
            db.execute('BEGIN IMMEDIATE')
            pending = db.execute('SELECT * FROM pb_oauth_states WHERE state_hash=? AND owner_hash=? AND expires>?', (pb.digest(state), principal['owner_hash'], pb.now())).fetchone()
            if not pending:
                raise Unavailable()
            consent = db.execute('SELECT 1 FROM pb_consents WHERE id=? AND revoked_at IS NULL', (pending['consent_id'],)).fetchone()
            db.execute('DELETE FROM pb_oauth_states WHERE state_hash=?', (pending['state_hash'],))
            db.commit()
            if not consent or not configured():
                raise Unavailable()
            if 'error' in query:
                outcome = 'cancelled'
                db.execute('UPDATE pb_consents SET revoked_at=? WHERE id=?', (pb.now(), pending['consent_id']))
                pb.event(db, principal['owner_hash'], None, 'oauth_cancelled', 'oauth-cancel:' + state, status='cancelled')
            else:
                code = query.get('code', [''])[0]
                if not code or len(code) > 4096:
                    raise Unavailable()
                result = request('https://api.instagram.com/oauth/access_token', {'client_id': os.environ['META_INSTAGRAM_APP_ID'], 'client_secret': os.environ['META_INSTAGRAM_APP_SECRET'], 'grant_type': 'authorization_code', 'redirect_uri': os.environ['META_INSTAGRAM_REDIRECT_URI'], 'code': code})
                token = result.get('access_token')
                if not isinstance(token, str) or not token or len(token) > 8192:
                    raise Unavailable()
                profile = graph('me', 'user_id,username,account_type', token)
                account = str(profile.get('user_id', profile.get('id', '')))
                if not account.isdigit() or profile.get('account_type') not in {'BUSINESS', 'MEDIA_CREATOR', 'CREATOR'} or not isinstance(profile.get('username'), str):
                    raise Unavailable()
                if result.get('user_id') is not None and str(result['user_id']) != account:
                    raise Unavailable()
                # A disconnect while Meta was responding must invalidate the in-flight grant.
                db.execute('BEGIN IMMEDIATE')
                if not db.execute('SELECT 1 FROM pb_consents WHERE id=? AND revoked_at IS NULL', (pending['consent_id'],)).fetchone():
                    raise Unavailable()
                db.execute("UPDATE pb_instagram_connections SET status='disconnected',token_cipher=NULL,updated_at=? WHERE owner_hash=? AND status='connected'", (pb.now(), principal['owner_hash']))
                expires = result.get('expires_in', 3600)
                if type(expires) is not int or not 0 < expires <= 5184000:
                    expires = 3600
                connection = pb.uid()
                db.execute('INSERT INTO pb_instagram_connections VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', (connection, principal['owner_hash'], account, profile['username'][:100], cipher().encrypt(token.encode()), 'instagram_business_basic', pb.now(), pb.now() + expires, 'connected', None, None, pb.now()))
                pb.audit(db, principal['owner_hash'], 'instagram_connected', connection)
                pb.event(db, principal['owner_hash'], None, 'oauth_success', 'oauth-success:' + connection)
                outcome = 'connected'
            db.commit()
    except (Unavailable, ValueError, KeyError, pb.sqlite3.Error):
        outcome = 'failed'
        if principal:
            try:
                with connect() as db:
                    pb.event(db, principal['owner_hash'], None, 'oauth_failed', 'oauth-failed:' + pb.uid(), status='failed')
                    pb.audit(db, principal['owner_hash'], 'instagram_connection_failed')
                    db.commit()
            except pb.sqlite3.Error:
                pass
    handler.respond(303, content_type='text/html; charset=utf-8', headers={'Location': '/personal-brand?instagram=' + outcome, 'Referrer-Policy': 'no-referrer'})


def sync(db, owner):
    if not configured():
        raise Unavailable()
    connection = pb.active_connection(db, owner)
    if not connection:
        raise ValueError('ابتدا اتصال را برقرار کنید.')
    if connection['expires_at'] <= pb.now():
        db.execute("UPDATE pb_instagram_connections SET status='expired',token_cipher=NULL,updated_at=? WHERE id=?", (pb.now(), connection['id']))
        db.commit()
        raise Unavailable()
    if db.execute('SELECT 1 FROM pb_instagram_sync_jobs WHERE connection_id=? AND created_at>?', (connection['id'], pb.now() - 60)).fetchone():
        raise ValueError('بین همگام‌سازی‌ها یک دقیقه فاصله بگذارید.')
    job = pb.uid()
    db.execute('INSERT INTO pb_instagram_sync_jobs VALUES(?,?,?,?,?,NULL)', (job, connection['id'], 'running', None, pb.now()))
    pb.event(db, owner, None, 'sync_started', 'sync-start:' + job)
    db.commit()
    try:
        from cryptography.fernet import InvalidToken
        try:
            token = cipher().decrypt(connection['token_cipher']).decode()
        except InvalidToken:
            raise Unavailable() from None
        fetched_profile = graph('me', 'user_id,username,account_type', token)
        if str(fetched_profile.get('user_id', fetched_profile.get('id', ''))) != connection['account_id'] or fetched_profile.get('account_type') not in {'BUSINESS', 'MEDIA_CREATOR', 'CREATOR'} or not isinstance(fetched_profile.get('username'), str):
            raise Unavailable()
        profile = {'username': fetched_profile['username'][:100], 'account_type': fetched_profile['account_type']}
        unavailable = []
        for field in ('biography', 'name', 'website'):
            try:
                extra = graph('me', field, token)
                if field in extra and isinstance(extra[field], str):
                    profile[field] = extra[field][:2000]
                else:
                    unavailable.append(field)
            except Unavailable:
                unavailable.append(field)
        media = graph('me/media', 'id,caption,media_type,timestamp,permalink', token, 25).get('data')
        if not isinstance(media, list):
            raise Unavailable()
        cleaned = []
        for item in media[:25]:
            if not isinstance(item, dict) or not isinstance(item.get('id'), str):
                raise Unavailable()
            cleaned.append({k: v[:10000] for k, v in item.items() if k in {'id', 'caption', 'media_type', 'timestamp', 'permalink'} and isinstance(v, str)})
        captions = [item.get('caption', '') for item in cleaned]
        tags = Counter(tag for caption in captions for tag in re.findall(r'#[\w\u200c]+', caption))
        formats = Counter(item.get('media_type', 'UNKNOWN') for item in cleaned)
        cta = sum(any(word in caption for word in ('ثبت', 'تماس', 'بنویس', 'لینک', 'ذخیره', 'ارسال')) for caption in captions)
        observation = {'sample_size': len(cleaned), 'caption_count': sum(bool(c) for c in captions), 'formats': dict(formats), 'hashtags': tags.most_common(10), 'possible_cta_count': cta, 'method': 'text-metadata-v1', 'limitations': ['فقط حداکثر ۲۵ محتوای اخیر؛ نه کل تاریخچهٔ پیج.', 'وجود کلمات فراخوان اقدام فقط یک شاخص لغوی احتمالی است.', 'لحن، شخصیت و کیفیت تصویر یا ویدیو از این شاخص‌ها استنتاج نمی‌شود.'], 'unavailable_fields': unavailable}
        db.execute('BEGIN IMMEDIATE')
        active = pb.active_connection(db, owner)
        if not active or active['id'] != connection['id']:
            raise Unavailable()
        db.execute('DELETE FROM pb_instagram_profiles WHERE connection_id=?', (connection['id'],))
        db.execute('DELETE FROM pb_instagram_media WHERE connection_id=?', (connection['id'],))
        db.execute('DELETE FROM pb_instagram_analysis WHERE connection_id=?', (connection['id'],))
        db.execute('INSERT INTO pb_instagram_profiles VALUES(?,?,?,?)', (pb.uid(), connection['id'], pb.dumps(profile), pb.now()))
        for item in cleaned:
            db.execute('INSERT INTO pb_instagram_media VALUES(?,?,?,?,?)', (pb.uid(), connection['id'], item['id'], pb.dumps(item), pb.now()))
        db.execute('INSERT INTO pb_instagram_analysis VALUES(?,?,?,?,?)', (pb.uid(), connection['id'], pb.dumps(observation), 'text-metadata-v1', pb.now()))
        db.execute('UPDATE pb_instagram_connections SET synced_at=?,error_code=NULL,updated_at=? WHERE id=?', (pb.now(), pb.now(), connection['id']))
        db.execute("UPDATE pb_instagram_sync_jobs SET status='success',completed_at=? WHERE id=?", (pb.now(), job))
        pb.event(db, owner, None, 'sync_success', 'sync-success:' + job)
        db.commit()
        return {'connection': pb.public_connection(pb.active_connection(db, owner)), 'observations': observation}
    except (Unavailable, ValueError, KeyError):
        db.rollback()
        db.execute("UPDATE pb_instagram_sync_jobs SET status='failed',error_code='provider_unavailable',completed_at=? WHERE id=?", (pb.now(), job))
        db.execute("UPDATE pb_instagram_connections SET error_code='provider_unavailable',updated_at=? WHERE id=?", (pb.now(), connection['id']))
        pb.event(db, owner, None, 'sync_failed', 'sync-failed:' + job, status='failed')
        db.commit()
        raise Unavailable() from None
