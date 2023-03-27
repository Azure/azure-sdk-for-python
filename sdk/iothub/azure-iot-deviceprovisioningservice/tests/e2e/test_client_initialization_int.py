import asyncio
from os import getenv
from typing import Any, Optional

import aiohttp
import pytest
import requests
from azure.core.credentials import AccessToken
from urllib3 import encode_multipart_formdata

from azure.iot.deviceprovisioningservice import ProvisioningServiceClient
from azure.iot.deviceprovisioningservice.aio import (
    ProvisioningServiceClient as AsyncProvisioningServiceClient,
)
from azure.iot.deviceprovisioningservice.util.connection_strings import (
    parse_iot_dps_connection_string,
)

cs = getenv("AZIOTDPSSDK_DPS_CS")
client_id = getenv("AZURE_CLIENT_ID")
tenant_id = getenv("AZURE_TENANT_ID")
client_secret = getenv("AZURE_CLIENT_SECRET")

cs_dict = parse_iot_dps_connection_string(cs)
endpoint = cs_dict["HostName"]


class BearerTokenAuth(object):
    def __init__(self, tenant_id: str, client_id: str, client_secret: str) -> None:
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret

    def get_token(self, *scopes: Optional[Any]) -> AccessToken:
        from json import loads

        url = f"https://login.microsoftonline.com/{self._tenant_id}/oauth2/token"
        fields = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "resource": "https://azure-devices-provisioning.net",
        }
        body, content_type = encode_multipart_formdata(fields)
        headers = {"Content-Type": content_type}
        response: requests.Response = requests.post(url, data=body, headers=headers)
        content = loads(response.content.decode("utf-8"))
        return AccessToken(
            token=content["access_token"], expires_on=content["expires_on"]
        )


class AsyncBearerTokenAuth(object):
    def __init__(self, tenant_id: str, client_id: str, client_secret: str) -> None:
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret

    async def get_token(self, *scopes: Optional[Any]) -> AccessToken:
        url = f"https://login.microsoftonline.com/{self._tenant_id}/oauth2/token"
        fields = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "resource": "https://azure-devices-provisioning.net",
        }
        body, content_type = encode_multipart_formdata(fields)
        headers = {"Content-Type": content_type}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=body, headers=headers) as resp:
                content = await resp.json()
                return AccessToken(
                    token=content["access_token"], expires_on=content["expires_on"]
                )


bearer_token_creds = BearerTokenAuth(
    tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
)
async_bearer_token_creds = AsyncBearerTokenAuth(
    tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
)


# fix for pytest-asyncio closing event loops after first async test
@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestClientInit(object):
    def test_client_connection_string_init(self):
        client = ProvisioningServiceClient.from_connection_string(cs)
        response = client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert client and isinstance(response, list)

    async def test_client_connection_string_init_async(self):
        async_client = AsyncProvisioningServiceClient.from_connection_string(cs)
        response = await async_client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert async_client and isinstance(response, list)

    def test_client_bearer_token_init(self):
        client = ProvisioningServiceClient(
            endpoint=endpoint,
            credential=bearer_token_creds,
        )
        response = client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert client and isinstance(response, list)

    async def test_client_bearer_token_init_async(self):
        async_client = AsyncProvisioningServiceClient(
            endpoint=endpoint,
            credential=async_bearer_token_creds,
        )
        response = await async_client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        assert async_client and isinstance(response, list)
