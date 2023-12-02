import unittest

from flask_testing import TestCase
from src.app import app

class FlaskTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_index_get(self):
        # Test the index route with a GET request
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Enter a city name', response.data)

    def test_search_post(self):
        # Test the search functionality with a POST request
        response = self.client.post('/', data=dict(city="Test City"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test City', response.data)

if __name__ == '__main__':
    unittest.main()
