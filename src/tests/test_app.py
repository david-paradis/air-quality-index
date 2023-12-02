import unittest
from unittest import mock
from src.app import app, get_aqi, async_fetch_historical, async_analyze_historical, store_analysis_result

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Air Quality Index Web Application', response.data)
        self.assertIn(b'form action="/search"', response.data)

    @mock.patch('src.app.async_fetch_historical.delay')
    def test_search_with_valid_city(self, mock_delay):
        with mock.patch('src.app.get_aqi') as mocked_get_aqi:
            mocked_get_aqi.return_value = {
                'city': 'Test City',
                'aqi': 42,
                'station': {
                    'name': 'Test Station'
                }
            }
            response = self.app.post('/search', data={'city': 'Test City'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Air Quality Index (AQI) Information', response.data)
            self.assertIn(b'City: Test City', response.data)
            self.assertIn(b'42', response.data)
            self.assertIn(b'Test Station', response.data)
            mock_delay.assert_called_once_with('Test City')

    @mock.patch('src.app.async_fetch_historical.delay')
    def test_search_with_invalid_city(self, mock_delay):
        with mock.patch('src.app.get_aqi') as mocked_get_aqi:
            mocked_get_aqi.return_value = None
            response = self.app.post('/search', data={'city': 'Invalid City'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Air Quality Index (AQI) Information', response.data)
            self.assertIn(b'City: Invalid City', response.data)
            self.assertIn(b'Not Available', response.data)
            mock_delay.assert_not_called()

    def test_check_historical_data_with_existing_data(self):
        with mock.patch('src.app.db') as mocked_db:
            mocked_db['analysis-tasks'].find_one.return_value = {
                '_id': 'Test City',
                'result': {
                    'data': 'Test Data'
                }
            }
            response = self.app.get('/check_historical/Test%20City')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'{"data":{"data":"Test Data"},"status":"READY"}', response.data)

    def test_check_historical_data_with_non_existing_data(self):
        with mock.patch('src.app.db') as mocked_db:
            mocked_db['analysis-tasks'].find_one.return_value = None
            response = self.app.get('/check_historical/Non%20Existing%20City')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'{"status":"PENDING"}', response.data)

    def test_get_aqi_with_valid_city(self):
        with mock.patch('src.app.requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.json.return_value = {
                'data': [
                    {
                        'aqi': 42,
                        'station': {
                            'name': 'Test Station'
                        }
                    }
                ]
            }
            result = get_aqi('Test City')
            self.assertEqual(result, {
                    'aqi': 42,
                    'station': {
                        'name': 'Test Station'
                    }
            })

    def test_get_aqi_with_invalid_city(self):
        with mock.patch('src.app.requests.get') as mocked_get:
            mocked_get.return_value.status_code = 404
            result = get_aqi('Invalid City')
            self.assertIsNone(result)

    def test_store_analysis_result(self):
        with mock.patch('src.app.db') as mocked_db:
            result = {
                'city': 'Test City',
                'data': 'Test Data'
            }
            store_analysis_result(result)
            mocked_db['analysis-tasks'].update_one.assert_called_once_with(
                {"_id": 'Test City', "result": result},
                {"$set": {"_id": 'Test City', "result": result}},
                upsert=True
            )

if __name__ == '__main__':
    unittest.main()