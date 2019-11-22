# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import datetime
import logging
import pytest

from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceModifiedError,
    ResourceNotFoundError,
    ResourceExistsError,
    AzureError,
)
from azure.appconfiguration import ResourceReadOnlyError
from azure.appconfiguration import AzureAppConfigurationClient
from azure.appconfiguration import ConfigurationSetting
from devtools_testutils import AzureMgmtTestCase
from app_config_test_settings_fake import FAKE_APP_CONFIG_CONNECTION

PAGE_SIZE = 100
KEY_UUID = "test_key_a6af8952-54a6-11e9-b600-2816a84d0309"
LABEL_UUID = "1d7b2b28-549e-11e9-b51c-2816a84d0309"
KEY = "PYTHON_UNIT_" + KEY_UUID
LABEL = "test_label1_" + LABEL_UUID
LABEL_RESERVED_CHARS = "test_label2_*, \\" + LABEL_UUID  # contains reserved chars *,\
TEST_CONTENT_TYPE = "test content type"
TEST_VALUE = "test value"

class AzureAppConfigurationClientTestBase(AzureMgmtTestCase):
    def __init__(self, method_name, client_class):
        super(AzureAppConfigurationClientTestBase, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]
        if self.is_playback():
            connection_str = FAKE_APP_CONFIG_CONNECTION
        else:
            from app_config_test_settings_real import REAL_APP_CONFIG_CONNECTION

            connection_str = REAL_APP_CONFIG_CONNECTION
        self.app_config_client = client_class.from_connection_string(connection_str)

    def setUp(self):
        super(AzureAppConfigurationClientTestBase, self).setUp()
        self.test_config_setting = self._add_for_test(
            ConfigurationSetting(
                key=KEY,
                label=LABEL,
                value=TEST_VALUE,
                content_type=TEST_CONTENT_TYPE,
                tags={"tag1": "tag1", "tag2": "tag2"},
            )
        )
        self.test_config_setting_no_label = self._add_for_test(
            ConfigurationSetting(
                key=KEY,
                label=None,
                value=TEST_VALUE,
                content_type=TEST_CONTENT_TYPE,
                tags={"tag1": "tag1", "tag2": "tag2"},
            )
        )
        self.to_delete = [self.test_config_setting, self.test_config_setting_no_label]

    def tearDown(self):
        super(AzureAppConfigurationClientTestBase, self).tearDown()
        for item in self.to_delete:
            self.get_config_client().delete_configuration_setting(
                key=item.key, label=item.label
            )

    def get_config_client(self):
        return self.app_config_client

    def _add_for_test(self, kv):
        exist = bool(
            list(
                self.get_config_client().list_configuration_settings(
                    keys=[kv.key], labels=[kv.label]
                )
            )
        )
        if exist:
            self._delete_from_test(kv.key, kv.label)
        return self.get_config_client().add_configuration_setting(kv)

    def _delete_from_test(self, key, label):
        try:
            self.get_config_client().delete_configuration_setting(key=key, label=label)
        except AzureError:
            logging.debug(
                "Error occurred removing configuration setting %s %s during unit test"
                % (key, label)
            )
