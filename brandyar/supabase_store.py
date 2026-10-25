import base64
import json
import logging
import os
import re
import time
import uuid
import zlib
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


def filter_value(value):
    return quote(str(value), safe='')


def is_id(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', value) is not None


def compact_insight(report):
    return {
        'summary': report['summary'][:180],
        **{key: {'status': report[key]['status']} for key in ('positioning', 'content', 'trust')},
    }


def pack_report(report):
    raw = json.dumps(report, ensure_ascii=False, separators=(',', ':')).encode()
    return {
        'encoding': 'zlib-base64-v1',
        'data': base64.b64encode(zlib.compress(raw, 9)).decode('ascii'),
    }


def unpack_report(value):
    if not isinstance(value, dict) or value.get('encoding') != 'zlib-base64-v1':
        return value
    data = value.get('data')
    if not isinstance(data, str) or len(data) > 131072:
        raise ValueError()
    compressed = base64.b64decode(data, validate=True)
    decompressor = zlib.decompressobj()
    raw = decompressor.decompress(compressed, 262145)
    if len(raw) > 262144 or decompressor.unconsumed_tail or decompressor.unused_data or not decompressor.eof:
        raise ValueError()
    return json.loads(raw)


class SupabaseUnavailable(Exception):
    def __init__(self, status=None):
        self.status = status
        super().__init__()


class SupabaseStore:
    def __init__(self):
        url = os.environ.get('SUPABASE_URL', '').strip().rstrip('/')
        key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '').strip()
        if not url or not key:
            self.base = None
            return
        if not url.startswith('https://'):
            raise ValueError('SUPABASE_URL must use HTTPS')
        self.base = url + '/rest/v1'
        self.key = key

    @property
    def enabled(self):
        return self.base is not None

    @staticmethod
    def session_id(session):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, 'nesharo-assessment:' + session))

    def request(self, table, method='GET', query='', body=None, prefer='return=representation'):
        if not self.enabled:
            raise SupabaseUnavailable()
        url = f'{self.base}/{table}' + (f'?{query}' if query else '')
        headers = {
            'apikey': self.key,
            'Authorization': 'Bearer ' + self.key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Prefer': prefer,
        }
        request = Request(url, data=json.dumps(body, ensure_ascii=False).encode() if body is not None else None, headers=headers, method=method)
        for attempt in range(3):
            try:
                with urlopen(request, timeout=10) as response:
                    raw = response.read(262145)
                    if len(raw) > 262144:
                        raise SupabaseUnavailable()
                    return json.loads(raw) if raw else []
            except SupabaseUnavailable:
                raise
            except HTTPError as error:
                raise SupabaseUnavailable(error.code) from error
            except (URLError, OSError) as error:
                if attempt == 2:
                    reason = error.reason if isinstance(error, URLError) else error
                    logging.getLogger(__name__).warning('supabase_failure method=%s reason=%s', method, type(reason).__name__)
                    raise SupabaseUnavailable('transport_' + type(reason).__name__) from None
                time.sleep(0.25)
            except UnicodeError:
                logging.getLogger(__name__).warning('supabase_failure method=%s reason=invalid_header_encoding', method)
                raise SupabaseUnavailable('invalid_header_encoding') from None
            except ValueError:
                logging.getLogger(__name__).warning('supabase_failure method=%s reason=invalid_header_or_response', method)
                raise SupabaseUnavailable('invalid_header_or_response') from None

    def save_assessment(self, session, answers, report):
        assessment_id = self.session_id(session)
        insight = compact_insight(report)
        packed_report = pack_report(report)
        # Status only moves forward: a preview can be re-shown without losing an unlocked report.
        current = self.request('assessments', 'GET', 'session_id=eq.' + filter_value(assessment_id) + '&select=id,current_step', prefer='return=minimal')
        if current:
            step = current[0].get('current_step') or 'started'
            rows = self.request('assessments', 'PATCH', 'id=eq.' + filter_value(assessment_id), {
                'answers': answers,
                'insight': insight,
                'full_report': packed_report,
                'current_step': 'completed' if step == 'started' else step,
            })
            if not rows or rows[0].get('id') != assessment_id:
                raise SupabaseUnavailable()
            return assessment_id
        rows = self.request('assessments', 'POST', body={
            'id': assessment_id,
            'session_id': assessment_id,
            'answers': answers,
            'insight': insight,
            'full_report': packed_report,
            'current_step': 'completed',
            'completed_at': datetime.now(timezone.utc).isoformat(),
        })
        if not rows or not rows[0].get('id'):
            raise SupabaseUnavailable()
        return rows[0]['id']

    def save_lead(self, assessment_id, mobile, consent_follow_up, source_page=None, source_campaign=None):
        existing = self.request('leads', 'GET', 'mobile=eq.' + filter_value(mobile) + '&select=id', prefer='return=minimal')
        if existing:
            return self.link_lead(assessment_id, existing[0]['id'])
        try:
            rows = self.request('leads', 'POST', body={
                'mobile': mobile,
                'consent_follow_up': consent_follow_up,
                'source_page': source_page,
                'source_campaign': source_campaign,
            })
            lead_id = rows[0]['id']
        except SupabaseUnavailable:
            # A concurrent request may have inserted the same number first.
            existing = self.request('leads', 'GET', 'mobile=eq.' + filter_value(mobile) + '&select=id', prefer='return=minimal')
            if not existing:
                raise
            lead_id = existing[0]['id']
        if not lead_id:
            raise SupabaseUnavailable()
        return self.link_lead(assessment_id, lead_id)

    def link_lead(self, assessment_id, lead_id):
        rows = self.request('assessments', 'PATCH', 'id=eq.' + filter_value(assessment_id), {'lead_id': lead_id, 'current_step': 'report_unlocked'})
        if not rows or rows[0].get('lead_id') != lead_id:
            raise SupabaseUnavailable()
        return lead_id

    def assessment_has_lead(self, assessment_id):
        rows = self.request('assessments', 'GET', 'id=eq.' + filter_value(assessment_id) + '&select=lead_id', prefer='return=minimal')
        return bool(rows and rows[0].get('lead_id'))
