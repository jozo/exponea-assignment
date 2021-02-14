import asyncio

from asynctest import patch
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


async def wait_too_long(*args, **kwargs):
    await asyncio.sleep(0.1)
    return '{"time": 100}'


class TestApiAll:
    @patch("api.main.call_exponea")
    def test_returns_data_from_exponea_api(self, m_call):
        m_call.return_value = '{"time": 123}'

        response = client.get("/api/all/")

        assert response.status_code == 200, f"Response: {response.text}"
        assert response.json() == [{'time': 123}, {'time': 123}, {'time': 123}]

    @patch("api.main.call_exponea", wait_too_long)
    def test_raise_error_after_timeout_reached(self):
        response = client.get("/api/all/?timeout=10")

        assert response.status_code == 500, f"Response: {response.text}"
        assert response.json() == {"detail": "Internal error"}

    @patch("api.main.call_exponea")
    def test_raise_error_when_no_valid_response(self, m_call):
        m_call.return_value = 'wrong json'

        response = client.get("/api/all/")

        assert response.status_code == 500, f"Response: {response.text}"
        assert response.json() == {"detail": "Internal error"}


class TestApiFirst:
    @patch("api.main.call_exponea")
    def test_returns_data_from_first_exponea_api_response(self, m_call):
        m_call.side_effect = ['{"time": 1}', wait_too_long, wait_too_long]

        response = client.get("/api/first/")

        assert response.status_code == 200, f"Response: {response.text}"
        assert response.json() == {'time': 1}

    @patch("api.main.call_exponea", wait_too_long)
    def test_raise_error_after_timeout_reached_and_no_response(self):
        response = client.get("/api/first/?timeout=10")

        assert response.status_code == 500, f"Response: {response.text}"
        assert response.json() == {"detail": "Internal error"}


class TestApiWithinTimeout:
    @patch("api.main.call_exponea")
    def test_returns_data_from_responses_received(self, m_call):
        m_call.side_effect = [wait_too_long, '{"time": 42}', wait_too_long]

        response = client.get("/api/within-timeout/")

        assert response.status_code == 200, f"Response: {response.text}"
        assert response.json() == [{'time': 42}]

    @patch("api.main.call_exponea", wait_too_long)
    def test_returns_empty_array_after_timeout_reached_and_no_response(self):
        response = client.get("/api/within-timeout/?timeout=10")

        assert response.status_code == 200, f"Response: {response.text}"
        assert response.json() == []
