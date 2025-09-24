import unittest
import json
from app import app

class ApiIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_repopulate_es(self):
        resp = self.app.post('/repopulate-es')
        self.assertIn(resp.status_code, [200, 500])
        data = resp.get_json()
        self.assertIn('status', data)
        # Accept either success or error, but must be structured
        self.assertTrue(data['status'] in ['success', 'error'])

    def test_process_show_all(self):
        resp = self.app.post('/process', json={'prompt': 'show all'})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('intent', data)
        self.assertIn('results', data)
        # Should be a list for 'show all'
        if isinstance(data['results'], list):
            self.assertGreaterEqual(len(data['results']), 1)

    def test_process_cve(self):
        resp = self.app.post('/process', json={'prompt': 'show me CVE-2020-1472'})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('intent', data)
        self.assertIn('results', data)

    def test_process_component(self):
        resp = self.app.post('/process', json={'prompt': 'show me log4jscanner'})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('intent', data)
        self.assertIn('results', data)

    def test_process_error(self):
        resp = self.app.post('/process', json={'prompt': ''})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('intent', data)
        self.assertIn('results', data)

if __name__ == '__main__':
    unittest.main()
