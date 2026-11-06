import unittest
from pathlib import Path
from html.parser import HTMLParser

import site_chrome
import test_brandyar_architecture as harness


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            self.links.append(attrs.get('href'))
        if 'id' in attrs:
            self.ids.append(attrs['id'])


class SiteChromeTests(unittest.TestCase):
    setUp = harness.ArchitectureTests.setUp
    close = harness.ArchitectureTests.close
    call = harness.ArchitectureTests.call

    def test_same_shell_and_real_assets_on_existing_documents(self):
        for route in ('/', '/personal-brand', '/account', '/brandyar/dashboard', '/brandyar/plans', '/brandyar/activate'):
            with self.subTest(route=route):
                status, body, _ = self.call(path=route)
                self.assertEqual(status, 200)
                text = body.decode()
                self.assertEqual(text.count('class="site-header site-chrome"'), 1)
                self.assertEqual(text.count('class="site-footer site-chrome"'), 1)
                self.assertNotIn('<!-- site-header -->', text)
                self.assertIn('/site-theme.css', text)
                header = text.split('<header class="site-header site-chrome">')[1].split('</header>')[0]
                self.assertNotIn('منابع یادگیری', header)
                parser = Links()
                parser.feed(header)
                self.assertEqual(parser.links, ['/#/', *(item[1] for item in site_chrome.MENU), '/account'])
                self.assertEqual(len(parser.ids), len(set(parser.ids)))
                self.assertIn(site_chrome.footer(), text)
        for route in ('/site-theme.css', '/site-chrome.js', '/landing-logo.png'):
            self.assertEqual(self.call(path=route)[0], 200)

    def test_navigation_is_historical_and_forms_are_preserved(self):
        self.assertEqual([item[2] for item in site_chrome.MENU], [
            'خانه', 'ارزیابی رایگان', 'امکانات', 'چطور کار می‌کند؟', 'تعرفه‌ها', 'سؤالات متداول',
        ])
        text = self.call(path='/personal-brand')[1].decode()
        self.assertIn('data-link="assessment" class="active" aria-current="page"', text)
        for marker in ('id="app"', 'id="confirm-check"', 'id="confirm-yes"', 'id="feedback"'):
            self.assertIn(marker, text)
        root = Path(__file__).parent
        for name in ('index.html', 'personal-brand.html', 'account.html', 'brandyar.html'):
            source = (root / name).read_text()
            self.assertEqual(source.count('<!-- site-header -->'), 1)
            self.assertEqual(source.count('<!-- site-footer -->'), 1)
            self.assertNotIn('<header class="site-header"', source)
        self.assertEqual(site_chrome.render_document(b'{"ok":true}', '/api/account'), b'{"ok":true}')
        self.assertEqual(self.call(path='/forgot-password')[0], 404)
        self.assertEqual(self.call(path='/checkout')[0], 404)
        self.assertEqual(self.call(path='/payment/result')[0], 404)


if __name__ == '__main__':
    unittest.main()
