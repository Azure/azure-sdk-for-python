# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import os

from dotenv import load_dotenv, find_dotenv

from . import AzureMgmtPreparer
from .exceptions import AzureTestError
from .sanitizers import add_general_string_sanitizer


_logger = logging.getLogger(__name__)


class EnvironmentVariableLoader(AzureMgmtPreparer):
    def __init__(
        self,
        directory,
        name_prefix="",
        disable_recording=True,
        client_kwargs=None,
        random_name_enabled=False,
        use_cache=True,
        preparers=None,
        **kwargs
    ):
        super(EnvironmentVariableLoader, self).__init__(
            name_prefix,
            24,
            disable_recording=disable_recording,
            client_kwargs=client_kwargs,
            random_name_enabled=random_name_enabled,
        )

        self.directory = directory
        self.fake_values = {}
        self.real_values = {}
        self._set_secrets(**kwargs)
        self._backup_preparers = preparers

    def _set_secrets(self, **kwargs):
        keys = kwargs.keys()
        needed_keys = []
        for key in keys:
            if self.directory in key:
                needed_keys.append(key)
                self.fake_values[key] = kwargs[key]
        for key in self.fake_values:
            kwargs.pop(key)

        self.needed_keys = needed_keys

    def _set_mgmt_settings_real_values(self):
        if self.is_live:
            tenant = os.environ.get(f"{self.directory.upper()}_TENANT_ID")
            client = os.environ.get(f"{self.directory.upper()}_CLIENT_ID")
            secret = os.environ.get(f"{self.directory.upper()}_CLIENT_SECRET")

            # If environment variables are not all set, check if user-based authentication is requested
            if not all(x is not None for x in [tenant, client, secret]):
                use_pwsh = os.environ.get("AZURE_TEST_USE_PWSH_AUTH", "false").lower()
                use_cli = os.environ.get("AZURE_TEST_USE_CLI_AUTH", "false").lower()
                use_vscode = os.environ.get("AZURE_TEST_USE_VSCODE_AUTH", "false").lower()
                use_azd = os.environ.get("AZURE_TEST_USE_AZD_AUTH", "false").lower()
                user_auth = use_pwsh == "true" or use_cli == "true" or use_vscode == "true" or use_azd == "true"
                if not user_auth:
                    # All variables are required for service principal authentication
                    _logger.warn(
                        "Environment variables for service principal credentials are not all set. "
                        "Please either set the variables or request user-based authentication by setting "
                        "an 'AZURE_TEST_USE_X_AUTH' environment variable to 'true'. See "
                        "https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#configure-test-variables "
                        "for more information."
                    )

                _logger.debug(
                    "Environment variables for service principal credentials are not all set but user-based "
                    f"authentication was requested. Updating 'AZURE_*' variables to match '{self.directory.upper()}_*'."
                )

            # Set environment vars to directory values (and unset vars if directory vars are missing)
            if tenant is not None:
                os.environ["AZURE_TENANT_ID"] = tenant
            else:
                os.environ.pop("AZURE_TENANT_ID", None)
            if client is not None:
                os.environ["AZURE_CLIENT_ID"] = client
            else:
                os.environ.pop("AZURE_CLIENT_ID", None)
            if secret is not None:
                os.environ["AZURE_CLIENT_SECRET"] = secret
            else:
                os.environ.pop("AZURE_CLIENT_SECRET", None)

    def create_resource(self, name, **kwargs):
        load_dotenv(find_dotenv())

        if self.is_live:
            self._set_mgmt_settings_real_values()
            try:
                for key in self.needed_keys:

                    scrubbed_value = self.fake_values[key]
                    if scrubbed_value:
                        self.real_values[key.lower()] = os.environ[key.upper()]

                        # vcrpy-based tests have a scrubber to register fake values
                        if hasattr(self.test_class_instance, "scrubber"):
                            self.test_class_instance.scrubber.register_name_pair(
                                self.real_values[key.lower()], scrubbed_value
                            )
                        # test proxy tests have no scrubber, and instead register sanitizers using fake values
                        else:
                            try:
                                add_general_string_sanitizer(
                                    value=scrubbed_value,
                                    target=self.real_values[key.lower()],
                                )
                            except:
                                _logger.info(
                                    "This test class instance has no scrubber and a sanitizer could not be registered "
                                    "with the test proxy, so the EnvironmentVariableLoader will not scrub the value of "
                                    f"{key} in recordings."
                                )
                    else:
                        raise AzureTestError(
                            'To pass a live ID you must provide the scrubbed value for recordings to prevent secrets '
                            f'from being written to files. {key} was not given. For example: '
                            '@EnvironmentVariableLoader("schemaregistry", '
                            'schemaregistry_endpoint="fake_endpoint.servicebus.windows.net")'
                        )
            except KeyError as key_error:
                if not self._backup_preparers:
                    raise

                self.real_values = {}
                create_kwargs = {}
                for preparer in self._backup_preparers:
                    resource_name, values = preparer._prepare_create_resource(self.test_class_instance, **create_kwargs)
                    # values = preparer.create_resource(name, **create_kwargs)
                    self.real_values.update(values)
                    if "resource_group" in self.real_values.keys():
                        create_kwargs["resource_group"] = self.real_values["resource_group"]

            return self.real_values

        else:
            return self.fake_values

    def remove_resource(self, name, **kwargs):
        pass
