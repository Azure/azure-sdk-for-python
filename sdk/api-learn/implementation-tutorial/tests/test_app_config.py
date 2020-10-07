import os
import pytest

from _shared.testcase import AppConfigTestCase
from devtools_testutils import CachedResourceGroupPreparer
from appconfig_preparer import CachedAppConfigPreparer

from azure.appconfiguration import AppConfigurationClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError

class AppConfigurationClientTest(AppConfigTestCase):
    def __init__(self, *args, **kwargs):
        super(AppConfigurationClientTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(AppConfigurationClientTest, self).setUp()

    def test_create_client(self):
        url = os.environ.get('APP_CONFIG_URL')
        credential = DefaultAzureCredential()
        client = AppConfigurationClient(account_url=url, credential=credential)

    def test_create_client_invalid_url(self):
        url = os.environ.get('APP_CONFIG_URL_DOES_NOT_EXIST')
        credential = DefaultAzureCredential()
        with self.assertRaises(ValueError):
            client = AppConfigurationClient(account_url=url, credential=credential)

    @CachedResourceGroupPreparer(name_prefix="appconfigtest")
    @CachedAppConfigPreparer(name_prefix="appconfigtest")
    def test_get_key_value(self, resource_group, appconfig_url, appconfig_conn_str):
        client = AppConfigurationClient.from_connection_string(appconfig_conn_str)

        self.assertIsNotNone(client)
        # Confirm by doing a single get, which should throw an error
        with self.assertRaises(ResourceNotFoundError):
            color_setting = client.get_configuration_setting('FontColor')