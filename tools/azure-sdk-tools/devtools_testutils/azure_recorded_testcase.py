# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import logging
import os
import os.path
import requests
import six
import sys
import time
from typing import TYPE_CHECKING

from dotenv import load_dotenv, find_dotenv

from azure_devtools.scenario_tests import AzureTestError
from azure_devtools.scenario_tests.config import TestConfig
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function

from . import mgmt_settings_fake as fake_settings
from .azure_testcase import _is_autorest_v3, get_resource_name, get_qualified_method_name
from .config import PROXY_URL
from .enums import ProxyRecordingSanitizer

try:
    # Try to import the AsyncFakeCredential, if we cannot assume it is Python 2
    from .fake_async_credential import AsyncFakeCredential
except SyntaxError:
    pass

if TYPE_CHECKING:
    from typing import Optional


load_dotenv(find_dotenv())


def add_sanitizer(sanitizer, regex=None, value=None):
    # type: (ProxyRecordingSanitizer, Optional[str], Optional[str]) -> None
    if sanitizer == ProxyRecordingSanitizer.URI:
        requests.post(
            "{}/Admin/AddSanitizer".format(PROXY_URL),
            headers={"x-abstraction-identifier": ProxyRecordingSanitizer.URI.value},
            json={
                "regex": regex or "[a-z]+(?=(?:-secondary)\\.(?:table|blob|queue)\\.core\\.windows\\.net)",
                "value": value or "fakevalue"
            },
        )


def is_live():
    """A module version of is_live, that could be used in pytest marker."""
    if not hasattr(is_live, "_cache"):
        is_live._cache = TestConfig().record_mode
    return is_live._cache


class AzureRecordedTestCase(object):
    @property
    def settings(self):
        if self.is_live:
            if self._real_settings:
                return self._real_settings
            else:
                raise AzureTestError("Need a mgmt_settings_real.py file to run tests live.")
        else:
            return self._fake_settings

    def _load_settings(self):
        try:
            from . import mgmt_settings_real as real_settings

            return fake_settings, real_settings
        except ImportError:
            return fake_settings, None

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

        if key_value and self._real_settings and getattr(self._real_settings, key) != key_value:
            raise ValueError(
                "You have both AZURE_{key} env variable and mgmt_settings_real.py for {key} to different values".format(
                    key=key
                )
            )

        if not key_value:
            try:
                key_value = getattr(self.settings, key)
            except Exception as ex:
                six.raise_from(ValueError("Could not get {}".format(key)), ex)
        return key_value

    def get_credential(self, client_class, **kwargs):
        tenant_id = os.environ.get("AZURE_TENANT_ID", getattr(self._real_settings, "TENANT_ID", None))
        client_id = os.environ.get("AZURE_CLIENT_ID", getattr(self._real_settings, "CLIENT_ID", None))
        secret = os.environ.get("AZURE_CLIENT_SECRET", getattr(self._real_settings, "CLIENT_SECRET", None))
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

    def create_basic_client(self, client_class, **kwargs):
        """ DO NOT USE ME ANYMORE."""
        logger = logging.getLogger()
        logger.warning(
            "'create_basic_client' will be deprecated in the future. It is recommended that you use \
                'get_credential' and 'create_client_from_credential' to create your client."
        )

        credentials = self.get_credential(client_class)
        return self.create_client_from_credential(client_class, credentials, **kwargs)

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
