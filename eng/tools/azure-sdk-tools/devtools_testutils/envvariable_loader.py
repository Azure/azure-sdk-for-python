# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import os
from typing import Optional

from dotenv import load_dotenv, find_dotenv

from . import AzureMgmtPreparer
from .exceptions import AzureTestError
from .sanitizers import add_general_string_sanitizer


_logger = logging.getLogger(__name__)


class EnvironmentVariableOptions:
    """
    Options for the EnvironmentVariableLoader.

    :param hide_secrets: Case insensitive list of environment variable names whose values should be hidden. Instead of
        being passed to tests as plain strings, these values will be wrapped in an EnvironmentVariable object that hides
        the value when printed. Use `.secret` to get the actual value (and don't store the value in a local variable).
    """

    def __init__(self, *, hide_secrets: Optional[list[str]] = None) -> None:
        # Store all names as lowercase for easier case insensitive comparison in EnvironmentVariableLoader
        self.hide_secrets: list[str] = [name.lower() for name in hide_secrets] if hide_secrets else []


class EnvironmentVariableLoader(AzureMgmtPreparer):
    """
    Preparer to load environment variables during test setup.

    Refer to
    https://github.com/Azure/azure-sdk-for-python/tree/main/eng/tools/azure-sdk-tools/devtools_testutils#use-the-environmentvariableloader
    for usage information.

    :param str directory: The service directory prefix for the environment variables; e.g. "keyvault".
    :param str name_prefix: Not used; present for compatibility with other preparers.
    :param bool disable_recording: Not used; present for compatibility with other preparers.
    :param dict client_kwargs: Not used; present for compatibility with other preparers.
    :param bool random_name_enabled: Not used; present for compatibility with other preparers.
    :param bool use_cache: Not used; present for compatibility with other preparers.
    :param list preparers: Not used; present for compatibility with other preparers.

    :param options: An EnvironementVariableOptions object containing additional options for the preparer.
    :param kwargs: Keyword arguments representing environment variable names and their fake values for use in
        recordings. For example, `client_id="fake_client_id"`.
    """

    def __init__(
        self,
        directory,
        name_prefix="",
        disable_recording=True,
        client_kwargs=None,
        random_name_enabled=False,
        use_cache=True,
        preparers=None,
        *,
        options: Optional[EnvironmentVariableOptions] = None,
        **kwargs,
    ):
        super(EnvironmentVariableLoader, self).__init__(
            name_prefix,
            24,
            disable_recording=disable_recording,
            client_kwargs=client_kwargs,
            random_name_enabled=random_name_enabled,
        )

        self.directory = directory
        self.hide_secrets = options.hide_secrets if options else []
        self.fake_values = {}
        self.real_values = {}
        self._set_secrets(**kwargs)
        self._backup_preparers = preparers

    def _set_secrets(self, **kwargs):
        keys = {key.lower() for key in kwargs.keys()}
        if self.hide_secrets and not all(name in keys for name in self.hide_secrets):
            missing = [name for name in self.hide_secrets if name not in keys]
            raise AzureTestError(
                f"The following environment variables were specified to be hidden, but no fake values were "
                f"provided for them: {', '.join(missing)}. Please provide fake values for these variables."
            )

        needed_keys = []
        for key in keys:
            if self.directory in key:
                needed_keys.append(key)
                # Store the fake value, wrapping in EnvironmentVariable if it should be hidden
                # Even fake values can cause security alerts if they're formatted like real secrets
                self.fake_values[key] = (
                    EnvironmentVariable(key.upper(), kwargs[key]) if key in self.hide_secrets else kwargs[key]
                )
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
                use_azd = os.environ.get("AZURE_TEST_USE_AZD_AUTH", "false").lower()
                user_auth = use_pwsh == "true" or use_cli == "true" or use_azd == "true"
                if not user_auth:
                    # All variables are required for service principal authentication
                    _logger.warning(
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
        """
        Fetches required environment variables if running live; otherwise returns fake values.

        "create_resource" name is misleading, but is left over from when preparers were mostly used to create test
        resources at runtime.
        """
        load_dotenv(find_dotenv())

        if self.is_live:
            self._set_mgmt_settings_real_values()
            try:
                for key in self.needed_keys:

                    scrubbed_value = self.fake_values[key]
                    if scrubbed_value:
                        # Store the real value, wrapping in EnvironmentVariable if it should be hidden
                        self.real_values[key.lower()] = (
                            EnvironmentVariable(key.upper(), os.environ[key.upper()])
                            if key in self.hide_secrets
                            else os.environ[key.upper()]
                        )

                        try:
                            add_general_string_sanitizer(
                                value=scrubbed_value,
                                target=self.real_values[key],
                            )
                        except:
                            _logger.info(
                                "A sanitizer could not be registered with the test proxy, so the "
                                f"EnvironmentVariableLoader will not scrub the value of {key} in recordings."
                            )
                    else:
                        raise AzureTestError(
                            "To pass a live ID you must provide the scrubbed value for recordings to prevent secrets "
                            f"from being written to files. {key} was not given. For example: "
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


class EnvironmentVariable:
    def __init__(self, name: str, secret: str) -> None:
        self.name = name
        self.secret = secret

    def __str__(self):
        return f"Environment variable {self.name}'s value hidden for security."
