import unittest
from src.app.app import get_aqi

class GetAQITestCase(unittest.TestCase):
    def test_get_aqi(self):
        # Mock the requests.get call to return a known response
        with mock.patch('requests.get') as mocked_get:
            mocked_get.return_value.json.return_value = {
                'status': 'ok',
                'data': {
                    'aqi': 42,
                    'city': 'Test City'
                }
            }
            response = get_aqi('Test City')
            self.assertEqual(response['data']['aqi'], 42)
            self.assertEqual(response['status'], 'ok')

if __name__ == '__main__':
    unittest.main()
