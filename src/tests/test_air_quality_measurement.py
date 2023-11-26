import unittest
from src.app.models.air_quality_measurement import AirQualityMeasurement

class TestAirQualityMeasurement(unittest.TestCase):
    def test_get_risk_level_and_statement(self):
        # Test cases for different AQI ranges
        test_data = [
            (50, ('Good', 'None')),
            (75, ('Moderate', 'Active children and adults, and people with respiratory disease, such as asthma, should limit prolonged outdoor exertion.')),
            (125, ('Unhealthy for Sensitive Groups', 'Active children and adults, and people with respiratory disease, such as asthma, should limit prolonged outdoor exertion.')),
            (175, ('Unhealthy', 'Active children and adults, and people with respiratory disease, such as asthma, should avoid prolonged outdoor exertion; everyone else, especially children, should limit prolonged outdoor exertion')),
            (250, ('Very Unhealthy', 'Active children and adults, and people with respiratory disease, such as asthma, should avoid all outdoor exertion; everyone else, especially children, should limit outdoor exertion.')),
            (350, ('Hazardous', 'Everyone should avoid all outdoor exertion')),
            (-5, ('Unknown', 'AQI value out of expected range'))
        ]

        for aqi, expected in test_data:
            measurement = AirQualityMeasurement('Test City', aqi)
            self.assertEqual(measurement.get_risk_level_and_statement(), expected, f"Failed for AQI: {aqi}")

if __name__ == '__main__':
    unittest.main()