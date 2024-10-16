# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import logging
import os
import os.path
import re
import six
import sys
import time
from typing import Dict

from dotenv import load_dotenv, find_dotenv

from . import mgmt_settings_fake as fake_settings
from .azure_testcase import (
    _is_autorest_v3,
    get_resource_name,
    get_qualified_method_name,
)
from .fake_credentials import SANITIZED
from .fake_credentials_async import AsyncFakeCredential
from .helpers import is_live, trim_kwargs_from_test_function
from .sanitizers import add_general_string_sanitizer


_LOGGER = logging.getLogger()

load_dotenv(find_dotenv())


class AzureRecordedTestCase(object):
    """Test class for use by data-plane tests that use the azure-sdk-tools test proxy.

    For more details and usage examples, refer to
    https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md
    """

    @property
    def settings(self):
        if self.is_live:
            return os.environ
        else:
            return fake_settings

    def _load_settings(self):
        return fake_settings, os.environ

    @property
    def is_live(self):
        return is_live()

    @property
    def qualified_test_name(self):
        return get_qualified_method_name(self, "method_name")

    @property
    def in_recording(self):
        return self.is_live

    # TODO: This needs to be removed, recording processors are handled on the proxy side, but
    # this is needed for the preparers
    @property
    def recording_processors(self):
        return []

    def is_playback(self):
        return not self.is_live

    def get_settings_value(self, key):
        key_value = os.environ.get("AZURE_" + key, None)

        if not key_value or self.is_playback():
            try:
                key_value = getattr(self.settings, key)
            except Exception as ex:
                six.raise_from(ValueError("Could not get {}".format(key)), ex)
        return key_value

    def get_credential(self, client_class, **kwargs):
        if _is_autorest_v3(client_class):
            return get_credential(**kwargs)
        tenant_id = os.environ.get("AZURE_TENANT_ID", getattr(os.environ, "TENANT_ID", None))
        client_id = os.environ.get("AZURE_CLIENT_ID", getattr(os.environ, "CLIENT_ID", None))
        secret = os.environ.get("AZURE_CLIENT_SECRET", getattr(os.environ, "CLIENT_SECRET", None))

        # Return live credentials only in live mode
        if self.is_live:
            # Service principal authentication
            if tenant_id and client_id and secret:
                # Create msrestazure class
                from msrestazure.azure_active_directory import (
                    ServicePrincipalCredentials,
                )

                return ServicePrincipalCredentials(tenant=tenant_id, client_id=client_id, secret=secret)

        # For playback tests, return credentials that will accept playback `get_token` calls
        else:
            return self.settings.get_credentials()

    def create_client_from_credential(self, client_class, credential, **kwargs):

        # Real client creation
        # TODO decide what is the final argument for that
        # if self.is_playback():
        #     kwargs.setdefault("polling_interval", 0)
        if _is_autorest_v3(client_class):
            kwargs.setdefault("logging_enable", True)
            client = client_class(credential=credential, **kwargs)
        else:
            client = client_class(credentials=credential, **kwargs)

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

    def create_random_name(self, name):
        unique_test_name = os.getenv("PYTEST_CURRENT_TEST").encode("utf-8")
        return get_resource_name(name, unique_test_name)

    def get_resource_name(self, name):
        """Alias to create_random_name for back compatibility."""
        return self.create_random_name(name)

    def get_replayable_random_resource_name(self, name):
        """In a replay scenario (not live), gives the static moniker. In the random scenario, gives generated name."""
        if self.is_live:
            created_name = self.create_random_name(name)
            self.scrubber.register_name_pair(created_name, name)
        return name

    def get_preparer_resource_name(self, prefix):
        """Random name generation for use by preparers.

        If prefix is a blank string, use the fully qualified test name instead.
        This is what legacy tests do for resource groups."""
        return self.get_resource_name(prefix)

    @staticmethod
    def await_prepared_test(test_fn):
        """Synchronous wrapper for async test methods. Used to avoid making changes
        upstream to AbstractPreparer, which only awaits async tests that use preparers.
        (Add @AzureTestCase.await_prepared_test decorator to async tests without preparers)

        # Note: this will only be needed so long as we maintain unittest.TestCase in our
        test-class inheritance chain.
        """

        if sys.version_info < (3, 5):
            raise ImportError("Async wrapper is not needed for Python 2.7 code.")

        import asyncio

        @functools.wraps(test_fn)
        def run(test_class_instance, *args, **kwargs):
            trim_kwargs_from_test_function(test_fn, kwargs)
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(test_fn(test_class_instance, **kwargs))

        return run

    def sleep(self, seconds):
        if self.is_live:
            time.sleep(seconds)

    def generate_sas(self, *args, **kwargs):
        """This is a deprecated method that just returns the token from the passed-in function as-is.

        SAS token sanitization is now handled by test proxy centrally.

        :keyword fake_parameters: A dictionary with token parameter names as keys, and the values to sanitize these keys
            with as values. For example: {"sktid": "00000000-0000-0000-0000-000000000000", "sig": "Sanitized"}
        :paramtype fake_parameters: Dict[str, str]
        :keyword str fake_value: The value used to sanitize `sig`. Defaults to "Sanitized".
        """
        sas_func = args[0]
        sas_func_pos_args = args[1:]
        token = sas_func(*sas_func_pos_args, **kwargs)
        return token


def get_credential(**kwargs):
    tenant_id = os.environ.get("AZURE_TENANT_ID", getattr(os.environ, "TENANT_ID", None))
    client_id = os.environ.get("AZURE_CLIENT_ID", getattr(os.environ, "CLIENT_ID", None))
    secret = os.environ.get("AZURE_CLIENT_SECRET", getattr(os.environ, "CLIENT_SECRET", None))

    use_pwsh = os.environ.get("AZURE_TEST_USE_PWSH_AUTH", "false")
    use_cli = os.environ.get("AZURE_TEST_USE_CLI_AUTH", "false")
    use_vscode = os.environ.get("AZURE_TEST_USE_VSCODE_AUTH", "false")
    use_azd = os.environ.get("AZURE_TEST_USE_AZD_AUTH", "false")
    is_async = kwargs.pop("is_async", False)

    # Return live credentials only in live mode
    if is_live():
        # User-based authentication through Azure PowerShell, if requested
        if use_pwsh.lower() == "true":
            _LOGGER.info(
                "Environment variable AZURE_TEST_USE_PWSH_AUTH set to 'true'. Using AzurePowerShellCredential."
            )
            from azure.identity import AzurePowerShellCredential

            if is_async:
                from azure.identity.aio import AzurePowerShellCredential
            return AzurePowerShellCredential(**kwargs)
        # User-based authentication through Azure CLI (az), if requested
        if use_cli.lower() == "true":
            _LOGGER.info("Environment variable AZURE_TEST_USE_CLI_AUTH set to 'true'. Using AzureCliCredential.")
            from azure.identity import AzureCliCredential

            if is_async:
                from azure.identity.aio import AzureCliCredential
            return AzureCliCredential(**kwargs)
        # User-based authentication through Visual Studio Code, if requested
        if use_vscode.lower() == "true":
            _LOGGER.info(
                "Environment variable AZURE_TEST_USE_VSCODE_AUTH set to 'true'. Using VisualStudioCodeCredential."
            )
            from azure.identity import VisualStudioCodeCredential

            if is_async:
                from azure.identity.aio import VisualStudioCodeCredential
            return VisualStudioCodeCredential(**kwargs)
        # User-based authentication through Azure Developer CLI (azd), if requested
        if use_azd.lower() == "true":
            _LOGGER.info(
                "Environment variable AZURE_TEST_USE_AZD_AUTH set to 'true'. Using AzureDeveloperCliCredential."
            )
            from azure.identity import AzureDeveloperCliCredential

            if is_async:
                from azure.identity.aio import AzureDeveloperCliCredential
            return AzureDeveloperCliCredential(**kwargs)

        # Service principal authentication
        if tenant_id and client_id and secret:
            _LOGGER.info(
                "Service principal client ID, secret, and tenant ID detected. Using ClientSecretCredential.\n"
                "For user-based auth, set AZURE_TEST_USE_PWSH_AUTH or AZURE_TEST_USE_CLI_AUTH to 'true'."
            )
            from azure.identity import ClientSecretCredential

            if is_async:
                from azure.identity.aio import ClientSecretCredential
            return ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=secret, **kwargs)

        # If AzurePipelinesCredential is detected, use it.
        service_connection_id = os.environ.get("AZURESUBSCRIPTION_SERVICE_CONNECTION_ID")
        client_id = os.environ.get("AZURESUBSCRIPTION_CLIENT_ID")
        tenant_id = os.environ.get("AZURESUBSCRIPTION_TENANT_ID")
        system_access_token = os.environ.get("SYSTEM_ACCESSTOKEN")
        if service_connection_id and client_id and tenant_id and system_access_token:
            from azure.identity import AzurePipelinesCredential

            if is_async:
                from azure.identity.aio import AzurePipelinesCredential
            return AzurePipelinesCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                service_connection_id=service_connection_id,
                system_access_token=system_access_token,
                **kwargs,
            )
        # This is for testing purposes only, to ensure that the AzurePipelinesCredential is used when available
        else:
            force_fallback_dac = os.environ.get("AZURE_TEST_FORCE_FALLBACK_DAC", "false")
            if service_connection_id and not (force_fallback_dac):
                # if service_connection_id is set, we believe it is running in CI
                system_access_token = SANITIZED if system_access_token else None
                raise ValueError(
                    "Running in Azure Pipelines. Environment variables not set for service principal authentication. "
                    f"service_connection_id: {service_connection_id}, client_id: {client_id}, tenant_id: {tenant_id}, system_access_token: {system_access_token}"
                )
        # Fall back to DefaultAzureCredential
        from azure.identity import DefaultAzureCredential

        if is_async:
            from azure.identity.aio import DefaultAzureCredential
        return DefaultAzureCredential(exclude_managed_identity_credential=True, **kwargs)

    # For playback tests, return credentials that will accept playback `get_token` calls
    if is_async:
        return AsyncFakeCredential()
    else:
        return fake_settings.get_azure_core_credentials()
