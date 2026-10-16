# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest.mock import Mock

import pytest
from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.appconfiguration import AzureAppConfigurationClient
from azure.appconfiguration.aio import AzureAppConfigurationClient as AsyncAzureAppConfigurationClient
from azure.appconfiguration._audience import get_audience

_PUBLIC_CLOUD_AUDIENCE = "https://appconfig.azure.com/"

_AUDIENCE_CASES = [
    ("https://example.appconfig.azure.com", _PUBLIC_CLOUD_AUDIENCE),
    ("https://example.azconfig.azure.com", "https://azconfig.azure.com/"),
    ("https://example.azconfig.io", "https://azconfig.io/"),
    ("https://example.appconfig.azure.us", "https://appconfig.azure.us/"),
    ("https://example.azconfig.azure.us", "https://azconfig.azure.us/"),
    ("https://example.appconfig.azure.cn", "https://appconfig.azure.cn/"),
    ("https://example.azconfig.azure.cn", "https://azconfig.azure.cn/"),
    ("https://my-store-123.appconfig.azure.com", _PUBLIC_CLOUD_AUDIENCE),
    ("https://example.appconfig.azure.com/", _PUBLIC_CLOUD_AUDIENCE),
    ("https://example.appconfig.azure.us/", "https://appconfig.azure.us/"),
    ("https://example.appconfig.azure.cn/", "https://appconfig.azure.cn/"),
    ("https://example.azconfig.azure.us/", "https://azconfig.azure.us/"),
    ("https://example.appconfig-staging.azure.com", "https://appconfig-staging.azure.com/"),
    ("https://appconfig.example.appconfig-staging.azure.com", "https://appconfig-staging.azure.com/"),
    ("https://example.appconfig.sovereign.cloud", "https://appconfig.sovereign.cloud/"),
    ("https://example.azconfig.sovereign.cloud", "https://azconfig.sovereign.cloud/"),
    ("https://example.eastus.appconfig.sovereign.cloud", "https://appconfig.sovereign.cloud/"),
    ("https://appconfig-store.azconfig.example.appconfig.sovereign.cloud", "https://appconfig.sovereign.cloud/"),
    ("https://appconfig.example.azconfig.sovereign.cloud", "https://azconfig.sovereign.cloud/"),
    ("https://example.AZconfig.IO/", "https://azconfig.io/"),
    ("https://example.APPCONFIG-STAGING.AZURE.COM/", "https://appconfig-staging.azure.com/"),
    ("https://example.appconfig.azure.us:443/path?key=value#fragment", "https://appconfig.azure.us/"),
    ("https://example.azconfig.azure.cn/path/appconfig.azure.us", "https://azconfig.azure.cn/"),
    ("https://example.appconfig-test.azure.com", _PUBLIC_CLOUD_AUDIENCE),
    ("https://example.fooappconfig.azure.us", _PUBLIC_CLOUD_AUDIENCE),
    ("https://myazconfig.io", _PUBLIC_CLOUD_AUDIENCE),
    ("https://example.fooappconfig-staging.azure.com", _PUBLIC_CLOUD_AUDIENCE),
    ("https://other.custom.audience", _PUBLIC_CLOUD_AUDIENCE),
    ("https://other.custom.audience/appconfig.azure.us", _PUBLIC_CLOUD_AUDIENCE),
    ("https://other.custom.audience/?host=example.appconfig.azure.cn", _PUBLIC_CLOUD_AUDIENCE),
    ("https://example.appconfig.azure.us@other.custom.audience", _PUBLIC_CLOUD_AUDIENCE),
    ("http://localhost:8483", _PUBLIC_CLOUD_AUDIENCE),
    ("https://127.0.0.1:443", _PUBLIC_CLOUD_AUDIENCE),
    ("https://[::1]:443", _PUBLIC_CLOUD_AUDIENCE),
]

_CLIENT_TYPES = [
    (AzureAppConfigurationClient, TokenCredential),
    (AsyncAzureAppConfigurationClient, AsyncTokenCredential),
]


@pytest.mark.parametrize("endpoint, expected_audience", _AUDIENCE_CASES)
def test_get_audience(endpoint, expected_audience):
    assert get_audience(endpoint) == expected_audience


@pytest.mark.parametrize("client_type, credential_type", _CLIENT_TYPES)
@pytest.mark.parametrize("endpoint, expected_audience", _AUDIENCE_CASES)
def test_client_infers_audience(client_type, credential_type, endpoint, expected_audience):
    client = client_type(endpoint, Mock(spec=credential_type))

    assert client._impl._config.credential_scopes == [expected_audience + ".default"]
    assert client._impl._config.authentication_policy._scopes == (expected_audience + ".default",)


@pytest.mark.parametrize("client_type, credential_type", _CLIENT_TYPES)
@pytest.mark.parametrize(
    "audience", [_PUBLIC_CLOUD_AUDIENCE, "https://appconfig.azure.cn/", "https://custom.audience/"]
)
def test_client_explicit_audience_overrides_detection(client_type, credential_type, audience):
    client = client_type("https://example.appconfig.sovereign.cloud", Mock(spec=credential_type), audience=audience)

    assert client._impl._config.credential_scopes == [audience + ".default"]
    assert client._impl._config.authentication_policy._scopes == (audience + ".default",)


@pytest.mark.parametrize("client_type, credential_type", _CLIENT_TYPES)
def test_client_infers_audience_without_endpoint_scheme(client_type, credential_type):
    client = client_type("example.appconfig.sovereign.cloud", Mock(spec=credential_type))

    assert client._impl._config.authentication_policy._scopes == ("https://appconfig.sovereign.cloud/.default",)
