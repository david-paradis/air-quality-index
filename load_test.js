import http from 'k6/http';
import { check, sleep, group } from 'k6';

export let options = {
    stages: [
        { duration: '30s', target: 10 },  // Ramp up to 10 users over 2 minutes
        { duration: '1m', target: 10 },  // Stay at 10 users for 2 minutes
        { duration: '30s', target: 0 },   // Ramp down to 0 users over 2 minutes
    ],
    thresholds: {
        // You can set various thresholds to ensure system reliability
        'http_req_duration': ['p(95)<1000'], // 95% of requests must complete below 1000ms
    }
};

export const HOSTNAME = 'http://127.0.0.1:5001';

function visitHomepage() {
    let res = http.get(HOSTNAME);
    check(res, { 'Homepage status was 200': r => r.status === 200 });
}

function searchAQI(city) {
    // URL encode the city name
    let encodedCity = encodeURIComponent(city);

    // Format the payload as 'city=encodedCityName'
    let payload = `city=${encodedCity}`;   
    let params = {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    };
    let response = http.post(`${HOSTNAME}/search`, payload, params);
    check(response, { 'Search response status was 200': r => r.status === 200 });
}

function checkTaskStatus(city) {
    let response = http.get(`${HOSTNAME}/check_historical/${city}`);
    check(response, { 'Historical data check response was 200': r => r.status === 200 });
}


export default function () {
    let cities = ['Shanghai', 'Los Angeles', 'Montréal'];
    let city = cities[Math.floor(Math.random() * cities.length)];

    // Define the scenarios as functions
    let visitHomepageScenario = function () {
        visitHomepage();
    };

    let searchAndCheckScenario = function () {
        group('Search and Check AQI Task', function () {
            searchAQI(city);
            sleep(1);
            checkTaskStatus(city);
        });
    };

    let scenarios = [visitHomepageScenario, searchAndCheckScenario];
    let selectedScenario = scenarios[Math.floor(Math.random() * scenarios.length)];

    // Execute the selected scenario
    group(selectedScenario.name, function () {
        selectedScenario();
    });

    sleep(1);
}
