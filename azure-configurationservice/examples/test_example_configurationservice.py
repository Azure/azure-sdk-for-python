# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
from msrestazure.azure_exceptions import CloudError
from azure.configuration import AzureConfigurationClient
from azure.configuration import ConfigurationSetting


class AzConfigurationClientExamples(unittest.TestCase):

    def _add_for_test(self, key, label):
        exist = bool(list(self.client.list_configuration_settings(keys=[key], labels=[label])))
        if not exist:
            sc = ConfigurationSetting(
                key=key,
                label=label,
                value="my value",
                content_type="my content type",
                tags={"my tag": "my tag value"}
            )
            self.client.add_configuration_setting(sc)

    def _delete_from_test(self, key, label):
        try:
            self.client.delete_configuration_setting(key=key, label=label)
        except CloudError:
            pass

    def setUp(self):
        super(AzConfigurationClientExamples, self).setUp()
        # [START create_app_configuration_client]
        import os
        from azure.configuration import AzureConfigurationClient

        connection_str = os.environ["AZ_CONFIG_CONNECTION"]
        client = AzureConfigurationClient(connection_str)
        # [END create_app_configuration_client]

        self.client = client

    def tearDown(self):
        self._delete_from_test("MyKey", "MyLabel")

    def test_azconfig_client_sample(self):
        # This is not unit test code. Just to verify if these sample code snippets work.

        client = self.client
        # [START add_configuration_setting]
        config_setting = ConfigurationSetting(
            key="MyKey",
            label="MyLabel",
            value="my value",
            content_type="my content type",
            tags={"my tag": "my tag value"}
        )
        added_config_setting = client.add_configuration_setting(config_setting)
        # [END add_configuration_setting]

        # [START update_configuration_setting]
        updated_kv = client.update_configuration_setting(
            key="MyKey",
            label="MyLabel",
            value="my updated value",
            content_type="my updated content type",
            tags={"my updated tag": "my updated tag value"}
            # TODO: etag handling
        )
        # [END update_configuration_setting]

        # [START set_configuration_setting]
        config_setting = ConfigurationSetting(
            key="MyKey",
            label="MyLabel",
            value="my set value",
            content_type="my set content type",
            tags={"my set tag": "my set tag value"}
            # TODO: etag handling
        )
        returned_config_setting = client.set_configuration_setting(config_setting)
        # [END set_configuration_setting]

        # [START lock_configuration_setting]
        locked_config_setting = client.lock_configuration_setting(key="MyKey", label="MyLabel")
        # [END lock_configuration_setting]

        # [START unlock_configuration_setting]
        unlocked_config_setting = client.unlock_configuration_setting(key="MyKey", label="MyLabel")
        # [END unlock_configuration_setting]

        # [START get_configuration_setting]
        from datetime import datetime, timedelta

        accept_date_time = datetime.today() + timedelta(days=1)
        fetched_config_setting = client.get_configuration_setting(
            key="MyKey", label="MyLabel"
        )
        # [END get_configuration_setting]

        # [START list_configuration_setting]
        from datetime import datetime, timedelta

        accept_date_time = datetime.today() + timedelta(days=-1)

        all_listed = client.list_configuration_settings()
        for item in all_listed:
            pass  # do something

        filtered_listed = client.list_configuration_settings(
            labels=["*Labe*"], keys=["*Ke*"], accept_date_time=accept_date_time
        )
        for item in filtered_listed:
            pass  # do something
        # [END list_configuration_setting]

        # [START list_revisions]
        from datetime import datetime, timedelta

        accept_date_time = datetime.today() + timedelta(days=-1)

        all_revisions = client.list_configuration_settings()
        for item in all_revisions:
            pass  # do something

        filtered_revisions = client.list_revisions(
            labels=["*Labe*"], keys=["*Ke*"], accept_date_time=accept_date_time
        )
        for item in filtered_revisions:
            pass  # do something
        # [END list_revisions]

        # [START delete_configuration_setting]
        deleted_config_setting = client.delete_configuration_setting(
            key="MyKey", label="MyLabel"
        )
        # [END delete_configuration_setting]



