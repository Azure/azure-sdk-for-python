# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import AzureMgmtPreparer, ResourceGroupPreparer
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM
from azure_devtools.scenario_tests.exceptions import AzureTestError
from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.credentials import AccessToken
import asyncio
from async_proxy import AzureAppConfigurationClientProxy
try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock

class AppConfigurationClientPreparer(AzureMgmtPreparer):
    def __init__(self,
                 name_prefix="appconfig",
                 aad_mode=False,
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 disable_recording=True,
                 playback_fake_resource=None,
                 client_kwargs=None):
        super(AppConfigurationClientPreparer, self).__init__(
            name_prefix,
            24,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
        )
        self.resource_group_parameter_name = resource_group_parameter_name
        self.aad_mode = aad_mode

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs[self.resource_group_parameter_name]
        except KeyError:
            template = (
                "To create a key vault a resource group is required. Please add "
                "decorator @{} in front of this storage account preparer."
            )
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

    def create_resource(self, name, **kwargs):
        if self.is_live:
            if self.aad_mode:
                base_url = kwargs.get("base_url", None)
                credential = DefaultAzureCredential()
                app_config_client = AzureAppConfigurationClient(base_url=base_url, credential=credential)
            else:
                connection_str = kwargs.get("connection_str", None)
                app_config_client = AzureAppConfigurationClient.from_connection_string(connection_str)
        else:
            if self.aad_mode:
                base_url = "https://fake_app_config.azconfig-test.io"
                credential = Mock(get_token=asyncio.coroutine(lambda _: AccessToken("fake-token", 0)))
                app_config_client = AzureAppConfigurationClient(base_url=base_url, credential=credential)
            else:
                connection_str = "Endpoint=https://fake_app_config.azconfig-test.io;Id=0-l4-s0:h5htBaY5Z1LwFz50bIQv;Secret=bgyvBgwsQIw0s8myrqJJI3nLrj81M/kzSgSuP4BBoVg="
                app_config_client = AzureAppConfigurationClient.from_connection_string(connection_str)

        app_config_client = AzureAppConfigurationClientProxy(app_config_client)
        return {"app_config_client": app_config_client}
