import os

from _shared.testcase import AppConfigTestCase
from azure.appconfiguration import AppConfigurationClient
from azure.identity import DefaultAzureCredential

class AppConfigurationClientTest(AppConfigTestCase):
    def __init__(self, *args, **kwargs):
        super(AppConfigurationClientTest, self).__init__(*args, **kwargs)
        if self.is_playback():
            self.connection_str = "Endpoint=https://fake_app_config.azconfig-test.io;Id=0-l4-s0:h5htBaY5Z1LwFz50bIQv;Secret=bgyvBgwsQIw0s8myrqJJI3nLrj81M/kzSgSuP4BBoVg="
        else:
            self.connection_str = os.getenv('LEARN_APPCONFIG_CONNECTION')

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