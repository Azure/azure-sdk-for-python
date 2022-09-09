# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from azure.appconfiguration import AzureAppConfigurationClient
from azure.identity import DefaultAzureCredential

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

AppConfigProviderPreparer = functools.partial(
    EnvironmentVariableLoader,
    "appconfiguration",
    appconfiguration_connection_string="Endpoint=https://fake_app_config.azconfig-test.io;Id=0-l4-s0:h5htBaY5Z1LwFz50bIQv;Secret=lamefakesecretlamefakesecretlamefakesecrett=",
    appconfiguration_endpoint_string="https://fake_app_config.azconfig-test.io"
)

class TestAppConfigurationProvider(AzureRecordedTestCase):

    def buildClient(self, endpoint):
        return AzureAppConfigurationClient(base_url=endpoint, credential=DefaultAzureCredential())

    # method: provider_creation
    @AppConfigProviderPreparer()
    @recorded_by_proxy
    def test_provider_creation(self, appconfiguration_endpoint_string):
        client = self.buildClient(appconfiguration_endpoint_string)

        assert client.get_configuration_setting("message","\0") == "hi"