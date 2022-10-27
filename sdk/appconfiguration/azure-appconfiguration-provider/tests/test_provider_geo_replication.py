# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfiguration.provider import (
    AzureAppConfigurationProvider,
    SettingSelector
)
from devtools_testutils import (
    AzureRecordedTestCase, 
    recorded_by_proxy
)
from azure.appconfiguration import AzureAppConfigurationClient
from azure.core.exceptions import HttpResponseError
from preparers import app_config_decorator_aad

invalid_endpoint = "https://invl.azconfig.io"

real_method = AzureAppConfigurationClient.list_configuration_settings

def new_method(self, key_filter=None, label_filter=None, **kwargs):
    if self._config.endpoint == invalid_endpoint:
        error = HttpResponseError("Invalid endpoint")
        error.status_code = 500
        raise error
    else:
        return real_method(self, key_filter, label_filter, **kwargs)

AzureAppConfigurationClient.list_configuration_settings = new_method

class TestAppConfigurationProvider(AzureRecordedTestCase):

    def build_provider_aad(self, endpoints, trimmed_key_prefixes=[], selects={SettingSelector("*", "\0")}):
        cred = self.get_credential(AzureAppConfigurationClient)
        return AzureAppConfigurationProvider.load(endpoints=endpoints,credential=cred, trimmed_key_prefixes=trimmed_key_prefixes, selects=selects)

    # method: test_provider_creation_geo
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_provider_creation_geo(self, appconfiguration_endpoint_string, appconfiguration_endpoint_geo_string):
        client = self.build_provider_aad([appconfiguration_endpoint_string, appconfiguration_endpoint_geo_string])
        assert client["message"] == "hi"
        assert client["my_json"]["key"] == "value"

    # method: test_provider_creation_geo_invalid_endpoint
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_provider_creation_geo_invalid_endpoint(self, appconfiguration_endpoint_string):
        # invl is an invalid store name, store names are a minimum of 5 characters
        client = self.build_provider_aad([invalid_endpoint, appconfiguration_endpoint_string])
        assert client["message"] == "hi"
        assert client["my_json"]["key"] == "value"
