# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from os import path
from azure.core.exceptions import AzureError
from azure.appconfiguration import ConfigurationSetting
from devtools_testutils import AzureMgmtTestCase


class AppConfigurationClientSamples(AzureMgmtTestCase):
    def _add_for_test(self, key, label):
        exist = bool(
            list(self.client.list_configuration_settings(keys=[key], labels=[label]))
        )
        if not exist:
            sc = ConfigurationSetting(
                key=key,
                label=label,
                value="my value",
                content_type="my content type",
                tags={"my tag": "my tag value"},
            )
            self.client.add_configuration_setting(sc)

    def _delete_from_test(self, key, label):
        try:
            self.client.delete_configuration_setting(key=key, label=label)
        except AzureError:
            pass

    def setUp(self):
        self.working_folder = path.dirname(__file__)
        super(AppConfigurationClientSamples, self).setUp()
        # [START create_app_configuration_client]
        import os
        from azure.appconfiguration import AzureAppConfigurationClient

        connection_str = os.environ["APP_CONFIG_CONNECTION"]
        client = AzureAppConfigurationClient(connection_str)
        # [END create_app_configuration_client]

        self.client = client

    def tearDown(self):
        self._delete_from_test("MyKey", "MyLabel")

    def test_appconfig_client_sample(self):
        # This is not unit test code. Just to verify if these sample code snippets work.

        client = self.client
        # [START add_configuration_setting]
        config_setting = ConfigurationSetting(
            key="MyKey",
            label="MyLabel",
            value="my value",
            content_type="my content type",
            tags={"my tag": "my tag value"},
        )
        added_config_setting = client.add_configuration_setting(config_setting)
        # [END add_configuration_setting]

        # [START update_configuration_setting]
        updated_kv = client.update_configuration_setting(
            key="MyKey",
            label="MyLabel",
            value="my updated value",
            content_type=None,  # None means not to update it
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

        # [START get_configuration_setting]
        fetched_config_setting = client.get_configuration_setting(
            key="MyKey", label="MyLabel"
        )
        # [END get_configuration_setting]

        # [START list_configuration_setting]
        from datetime import datetime, timedelta

        accept_datetime = datetime.today() + timedelta(days=-1)

        all_listed = client.list_configuration_settings()
        for item in all_listed:
            pass  # do something

        filtered_listed = client.list_configuration_settings(
            labels=["*Labe*"], keys=["*Ke*"], accept_datetime=accept_datetime
        )
        for item in filtered_listed:
            pass  # do something
        # [END list_configuration_setting]

        # [START list_revisions]
        from datetime import datetime, timedelta

        accept_datetime = datetime.today() + timedelta(days=-1)

        all_revisions = client.list_configuration_settings()
        for item in all_revisions:
            pass  # do something

        filtered_revisions = client.list_revisions(
            labels=["*Labe*"], keys=["*Ke*"], accept_datetime=accept_datetime
        )
        for item in filtered_revisions:
            pass  # do something
        # [END list_revisions]

        # [START delete_configuration_setting]
        deleted_config_setting = client.delete_configuration_setting(
            key="MyKey", label="MyLabel"
        )
        # [END delete_configuration_setting]
