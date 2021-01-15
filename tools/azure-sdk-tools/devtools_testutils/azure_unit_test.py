from dotenv import load_dotenv, find_dotenv
import logging
import os
import unittest

from azure_devtools.scenario_tests import GeneralNameReplacer, AzureTestError
# from azure_devtools.scenario_tests.config import TestConfig

from . import mgmt_settings_fake as fake_settings
from .azure_testcase import get_resource_name, get_qualified_method_name
from .config import TEST_SETTING_FILENAME


class AzureUnitTest(unittest.TestCase):
    def __init__(self, method_name, config_file=None):
        self.unit_test = True
        load_dotenv(find_dotenv())
        self.qualified_test_name = get_qualified_method_name(self, method_name)

        self.working_folder = os.path.dirname(__file__)
        self.scrubber = GeneralNameReplacer()
        # config_file = config_file or os.path.join(
        #     self.working_folder, TEST_SETTING_FILENAME
        # )
        # if not os.path.exists(config_file):
        #     config_file = None

        # For now leaving this as live always, the recordings don't generate traffic so passing in credentials is fine
        self.is_live = False
        # This should always be false, these tests don't generate live traffic
        self.in_recording = False
        self._fake_settings, self._real_settings = self._load_settings()
        super(AzureUnitTest, self).__init__(method_name)

    def setUp(self):
        # Incorporating this for leftover unittest dependent
        # tests. Will test without as well
        pass

    def create_client_from_credential(self):
        pass

    def get_resource_name(self, name):
        """Alias to create_random_name for back compatibility."""
        return get_resource_name(name, self.qualified_test_name.encode())

    def get_preparer_resource_name(self, prefix):
        """Random name generation for use by preparers.

        If prefix is a blank string, use the fully qualified test name instead.
        This is what legacy tests do for resource groups."""
        return self.get_resource_name(
            prefix or self.qualified_test_name.replace(".", "_")
        )

    def get_credential(self, client_class, **kwargs):

        tenant_id = os.environ.get(
            "AZURE_TENANT_ID", getattr(self._real_settings, "TENANT_ID", None)
        )
        client_id = os.environ.get(
            "AZURE_CLIENT_ID", getattr(self._real_settings, "CLIENT_ID", None)
        )
        secret = os.environ.get(
            "AZURE_CLIENT_SECRET", getattr(self._real_settings, "CLIENT_SECRET", None)
        )
        is_async = kwargs.pop("is_async", False)

        if tenant_id and client_id and secret and self.is_live:
            if _is_autorest_v3(client_class):
                # Create azure-identity class
                from azure.identity import ClientSecretCredential

                if is_async:
                    from azure.identity.aio import ClientSecretCredential
                return ClientSecretCredential(
                    tenant_id=tenant_id, client_id=client_id, client_secret=secret
                )
            else:
                # Create msrestazure class
                from msrestazure.azure_active_directory import (
                    ServicePrincipalCredentials,
                )

                return ServicePrincipalCredentials(
                    tenant=tenant_id, client_id=client_id, secret=secret
                )
        else:
            if _is_autorest_v3(client_class):
                if is_async:
                    if self.is_live:
                        raise ValueError(
                            "Async live doesn't support mgmt_setting_real, please set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET"
                        )
                    return AsyncFakeCredential()
                else:
                    return self.settings.get_azure_core_credentials()
            else:
                return self.settings.get_credentials()

    def create_client_from_credential(self, client_class, credential, **kwargs):

        # Real client creation
        if _is_autorest_v3(client_class):
            kwargs.setdefault("logging_enable", True)
            client = client_class(credential=credential, **kwargs)
        else:
            client = client_class(credentials=credential, **kwargs)

        if self.is_playback():
            try:
                client._config.polling_interval = (
                    0  # FIXME in azure-mgmt-core, make this a kwargs
                )
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

    def get_settings_value(self, key):
        key_value = os.environ.get("AZURE_" + key, None)

        if (
            key_value
            and self._real_settings
            and getattr(self._real_settings, key) != key_value
        ):
            print(key_value, getattr(self._real_settings, key))
            logger = logging.getLogger()
            logger.warning(
                "You have both AZURE_{key} env variable and mgmt_settings_real.py for {key} to different values. Defaulting to the env variable".format(
                    key=key
                )
            )

        if not key_value:
            try:
                key_value = getattr(self.settings, key)
            except Exception:
                print("Could not get {}".format(key))
                raise
        return key_value

    def _load_settings(self):
        try:
            from . import mgmt_settings_real as real_settings

            return fake_settings, real_settings
        except ImportError:
            return fake_settings, None

    @property
    def settings(self):
        print("in settings")
        quit()
        if self.is_live:
            if self._real_settings:
                return self._real_settings
            else:
                raise AzureTestError(
                    "Need a mgmt_settings_real.py file to run tests live."
                )
        else:
            return self._fake_settings