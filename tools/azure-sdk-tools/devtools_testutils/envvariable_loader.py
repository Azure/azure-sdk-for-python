# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import os

from . import AzureMgmtPreparer
from azure_devtools.scenario_tests.exceptions import AzureTestError
from dotenv import load_dotenv, find_dotenv
from .sanitizers import add_general_regex_sanitizer


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
            os.environ["AZURE_TENANT_ID"] = os.environ["{}_TENANT_ID".format(self.directory.upper())]
            os.environ["AZURE_CLIENT_ID"] = os.environ["{}_CLIENT_ID".format(self.directory.upper())]
            os.environ["AZURE_CLIENT_SECRET"] = os.environ["{}_CLIENT_SECRET".format(self.directory.upper())]

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
                                add_general_regex_sanitizer(value=scrubbed_value, regex=self.real_values[key.lower()])
                            except:
                                logger = logging.getLogger()
                                logger.info(
                                    "This test class instance has no scrubber and a sanitizer could not be registered "
                                    "with the test proxy, so the EnvironmentVariableLoader will not scrub the value of {} in "
                                    "recordings.".format(key)
                                )
                    else:
                        template = 'To pass a live ID you must provide the scrubbed value for recordings to \
                            prevent secrets from being written to files. {} was not given. For example: \
                                @EnvironmentVariableLoader("schemaregistry", schemaregistry_endpoint="fake_endpoint.servicebus.windows.net")'
                        raise AzureTestError(template.format(key))
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
