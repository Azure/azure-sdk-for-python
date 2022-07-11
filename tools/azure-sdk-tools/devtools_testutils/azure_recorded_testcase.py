# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import os
import os.path
import six
import sys
import time
from typing import TYPE_CHECKING

from dotenv import load_dotenv, find_dotenv

from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function

from . import mgmt_settings_fake as fake_settings
from .azure_testcase import (
    _is_autorest_v3,
    get_resource_name,
    get_qualified_method_name,
)
from .helpers import is_live
from .sanitizers import add_general_regex_sanitizer

try:
    # Try to import the AsyncFakeCredential, if we cannot assume it is Python 2
    from .fake_credentials_async import AsyncFakeCredential
except SyntaxError:
    pass

if TYPE_CHECKING:
    from typing import Any


load_dotenv(find_dotenv())


def _sanitize_token(token, fake_token):
    add_general_regex_sanitizer(value=fake_token, regex=token)
    url_safe_token = token.replace("/", "%2F")
    add_general_regex_sanitizer(value=fake_token, regex=url_safe_token)
    async_token = token.replace("%3A", ":")
    add_general_regex_sanitizer(value=fake_token, regex=async_token)


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
        tenant_id = os.environ.get("AZURE_TENANT_ID", getattr(os.environ, "TENANT_ID", None))
        client_id = os.environ.get("AZURE_CLIENT_ID", getattr(os.environ, "CLIENT_ID", None))
        secret = os.environ.get("AZURE_CLIENT_SECRET", getattr(os.environ, "CLIENT_SECRET", None))
        is_async = kwargs.pop("is_async", False)

        if tenant_id and client_id and secret and self.is_live:
            if _is_autorest_v3(client_class):
                # Create azure-identity class
                from azure.identity import ClientSecretCredential

                if is_async:
                    from azure.identity.aio import ClientSecretCredential
                return ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=secret)
            else:
                # Create msrestazure class
                from msrestazure.azure_active_directory import (
                    ServicePrincipalCredentials,
                )

                return ServicePrincipalCredentials(tenant=tenant_id, client_id=client_id, secret=secret)
        else:
            if _is_autorest_v3(client_class):
                if is_async:
                    if self.is_live:
                        raise ValueError(
                            "Async live doesn't support mgmt_setting_real, please set AZURE_TENANT_ID, "
                            "AZURE_CLIENT_ID, AZURE_CLIENT_SECRET"
                        )
                    return AsyncFakeCredential()
                else:
                    return self.settings.get_azure_core_credentials()
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
        sas_func = args[0]
        sas_func_pos_args = args[1:]

        fake_value = kwargs.pop("fake_value", "fake_token_value")
        token = sas_func(*sas_func_pos_args, **kwargs)

        fake_token = self._create_fake_token(token, fake_value)
        _sanitize_token(token, fake_token)

        if self.is_live:
            return token
        return fake_token

    def _create_fake_token(self, token, fake_value):
        parts = token.split("&")

        for idx, part in enumerate(parts):
            if part.startswith("sig"):
                key = part.split("=")
                key[1] = fake_value
                parts[idx] = "=".join(key)
            elif part.startswith("st"):
                key = part.split("=")
                key[1] = "start"
                parts[idx] = "=".join(key)
            elif part.startswith("se"):
                key = part.split("=")
                key[1] = "end"
                parts[idx] = "=".join(key)

        return "&".join(parts)
