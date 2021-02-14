import httpx
import pytest
from asynctest import Mock

from api.exponea import ApiError, call_exponea


@pytest.mark.asyncio
class TestCallExponea:
    def setup(self):
        self.client = Mock(httpx.AsyncClient())

    async def test_returns_response_body(self):
        self.client.get.return_value = Mock(text="{'time': 123}", status_code=200)

        data = await call_exponea(500, api_client=self.client)

        assert data == "{'time': 123}"

    async def test_raise_error_if_status_not_200(self):
        self.client.get.return_value = Mock(text="{'time': 123}", status_code=400)

        with pytest.raises(ApiError):
            await call_exponea(500, api_client=self.client)

    async def test_transform_exceptions_to_custom_one(self):
        self.client.side_effect = httpx.HTTPError

        with pytest.raises(ApiError):
            await call_exponea(500, api_client=self.client)
