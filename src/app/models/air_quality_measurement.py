class AirQualityMeasurement:
    def __init__(self, city, aqi, station_name=None):
        self.city = city
        self.aqi = float(aqi)
        self.station_name = station_name

    def get_risk_level_and_statement(self):
        if 0 <= self.aqi <= 50:
            return ('Good', 'None')
        elif 51 <= self.aqi <= 100:
            return ('Moderate', 'Active children and adults, and people with respiratory disease, '
                                'such as asthma, should limit prolonged outdoor exertion.')
        elif 101 <= self.aqi <= 150:
            return ('Unhealthy for Sensitive Groups', 'Active children and adults, and people with respiratory '
                                                      'disease, such as asthma, should limit prolonged outdoor exertion.')
        elif 151 <= self.aqi <= 200:
            return ('Unhealthy', 'Active children and adults, and people with respiratory disease, such as asthma, '
                                 'should avoid prolonged outdoor exertion; everyone else, especially children, '
                                 'should limit prolonged outdoor exertion')
        elif 201 <= self.aqi <= 300:
            return ('Very Unhealthy', 'Active children and adults, and people with respiratory disease, such as asthma, '
                                      'should avoid all outdoor exertion; everyone else, especially children, should limit '
                                      'outdoor exertion.')
        elif self.aqi > 300:
            return ('Hazardous', 'Everyone should avoid all outdoor exertion')
        else:
            return ('Unknown', 'AQI value out of expected range')