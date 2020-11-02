import pytest
import asyncio
import functools
import os

from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from devtools_testutils.azure_testcase import _is_autorest_v3
from devtools_testutils import AzureTestCase

APP_CONFIG_URL = "https://fake-app-config-url.azconfig.io"

class AsyncAppConfigTestCase(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(AsyncAppConfigTestCase, self).__init__(*args, **kwargs)
        self.env_color = os.environ.get('API-LEARN_SETTING_COLOR_VALUE', "Green")
        self.env_color_key = os.environ.get('API-LEARN_SETTING_COLOR_KEY', "FontColor")
        self.env_greeting = os.environ.get('API-LEARN_SETTING_TEXT_VALUE', "Hello World!")
        self.env_greeting_key = os.environ.get('API-LEARN_SETTING_TEXT_KEY', "Greeting")

    def setUp(self):
        super(AppConfigurationClientTest, self).setUp()
        # Set the env variable AZURE_APP_CONFIG_URL or put APP_CONFIG_URL in your "mgmt_settings_real.py" file
        self.app_config_url = self.set_value_to_scrub('APP_CONFIG_URL', APP_CONFIG_URL)

    class AsyncFakeCredential(object):
        # fake async credential
        async def get_token(self, *scopes, **kwargs):
            from azure.core.credentials import AccessToken
            return AccessToken('fake_token', 2527537086)

        async def close(self):
            pass

    def create_basic_client(self, client_class, **kwargs):
        # This is the patch for creating client using aio identity

        tenant_id = os.environ.get("AZURE_TENANT_ID", None)
        client_id = os.environ.get("AZURE_CLIENT_ID", None)
        secret = os.environ.get("AZURE_CLIENT_SECRET", None)

        if tenant_id and client_id and secret and self.is_live:
            if _is_autorest_v3(client_class):
                # Create azure-identity class using aio credential
                from azure.identity.aio import ClientSecretCredential
                credentials = ClientSecretCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=secret
                )
            else:
                # Create msrestazure class
                from msrestazure.azure_active_directory import ServicePrincipalCredentials
                credentials = ServicePrincipalCredentials(
                    tenant=tenant_id,
                    client_id=client_id,
                    secret=secret
                )
        else:
            if _is_autorest_v3(client_class):
                credentials = self.AsyncFakeCredential()
                #credentials = self.settings.get_azure_core_credentials()
            else:
                credentials = self.settings.get_credentials()

        # Real client creation
        # FIXME decide what is the final argument for that
        # if self.is_playback():
        #     kwargs.setdefault("polling_interval", 0)
        if _is_autorest_v3(client_class):
            kwargs.setdefault("logging_enable", True)
            client = client_class(
                credential=credentials,
                **kwargs
            )
        else:
            client = client_class(
                credentials=credentials,
                **kwargs
            )

        if self.is_playback():
            try:
                client._config.polling_interval = 0  # FIXME in azure-mgmt-core, make this a kwargs
            except AttributeError:
                pass

        if hasattr(client, "config"):  # Autorest v2
            if self.is_playback():
                client.config.long_running_operation_timeout = 0
            client.config.enable_http_logger = True
        return client