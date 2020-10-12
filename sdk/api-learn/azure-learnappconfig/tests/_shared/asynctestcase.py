import asyncio
import functools
import os

from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from devtools_testutils.azure_testcase import _is_autorest_v3

from .testcase import AppConfigTestCase

class AsyncAppConfigTestCase(AppConfigTestCase):
    def __init__(self, *args, **kwargs):
        super(AppConfigTestCase, self).__init__(*args, **kwargs)

    class AsyncFakeCredential(object):
        # fake async credential
        async def get_token(self, *scopes, **kwargs):
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
