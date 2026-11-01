import sqlite3
import unittest
from unittest.mock import patch

import brandyar_profile as product
from test_brandyar_architecture import ArchitectureTests


class AccountTests(unittest.TestCase):
    setUp = ArchitectureTests.setUp
    close = ArchitectureTests.close
    call = ArchitectureTests.call
    session = ArchitectureTests.session

    def post(self, csrf, cookie, **body):
        return self.call('POST', '/api/account', {'csrf': csrf, **body}, cookie)

    def test_assets_and_minimal_snapshot(self):
        for route in ('/account', '/account.js', '/account.css'):
            self.assertEqual(self.call(path=route)[0], 200)
        self.assertFalse(self.call(path='/api/account')[1]['data']['signedIn'])
        _, cookie = self.session()
        data = self.call(path='/api/account', cookie=cookie)[1]['data']
        self.assertEqual(set(data), {'signedIn', 'csrf', 'account', 'testCompleted', 'access'})
        self.assertFalse(data['testCompleted'])
        self.assertEqual(data['access']['status'], 'none')

    def test_persistence_isolation_validation_and_logout(self):
        csrf, cookie = self.session()
        account = {'name': 'نام واقعی', 'email': 'user@example.test', 'phone': '09120000000'}
        self.assertEqual(self.post(csrf, cookie, action='account_save', account=account)[0], 200)
        stored = self.call(path='/api/account', cookie=cookie)[1]['data']['account']
        for key, value in account.items():
            self.assertEqual(stored[key], value)
        self.assertNotIn('verified', stored)
        _, other = self.session()
        self.assertEqual(self.call(path='/api/account', cookie=other)[1]['data']['account']['name'], '')
        for invalid in ({'name': ''}, {**account, 'email': 'a@@b.c'}, {**account, 'phone': 'invalid'}, {**account, 'avatar': 'data:image/svg+xml;base64,AAAA'}):
            self.assertEqual(self.post(csrf, cookie, action='account_save', account=invalid)[0], 422)
        self.assertEqual(self.call(path='/api/account', cookie=cookie)[1]['data']['account'], stored)
        self.assertEqual(self.post('wrong', cookie, action='account_save', account=account)[0], 403)
        self.assertEqual(self.post(csrf, cookie, action='trial_grant', planId='starter')[0], 422)
        self.assertEqual(self.post(csrf, cookie, action='account_logout')[0], 200)
        self.assertFalse(self.call(path='/api/account', cookie=cookie)[1]['data']['signedIn'])
        self.assertEqual(self.post(csrf, cookie, action='account_save', account=account)[0], 401)

    def test_failed_write_preserves_previous_values(self):
        csrf, cookie = self.session()
        self.post(csrf, cookie, action='account_save', account={'name': 'قبلی'})
        with patch.object(product, 'save_account', side_effect=sqlite3.OperationalError('fixture')):
            status, response, _ = self.post(csrf, cookie, action='account_save', account={'name': 'جدید'})
        self.assertEqual(status, 503)
        self.assertNotIn('data', response)
        self.assertEqual(self.call(path='/api/account', cookie=cookie)[1]['data']['account']['name'], 'قبلی')


if __name__ == '__main__':
    unittest.main()
