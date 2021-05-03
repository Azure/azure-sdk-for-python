# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.core.exceptions import (
    ResourceModifiedError,
    ResourceNotFoundError,
    ResourceExistsError,
    AzureError,
)
from azure.appconfiguration import (
    ResourceReadOnlyError,
    AzureAppConfigurationClient,
    ConfigurationSetting,
    FeatureFlagConfigurationSetting,
    SecretReferenceConfigurationSetting,
    PERCENTAGE,
    TARGETING,
    TIME_WINDOW,
)
from azure.identity import DefaultAzureCredential

from consts import (
    KEY,
    LABEL,
    TEST_VALUE,
    TEST_CONTENT_TYPE,
    LABEL_RESERVED_CHARS,
    PAGE_SIZE,
    KEY_UUID,
)
from wrapper import app_config_decorator

from uuid import uuid4
import pytest


class AppConfigurationClientTest(AzureTestCase):


    def _assert_same_keys(self, key1, key2):
        assert type(key1) == type(key2)
        assert key1.key == key2.key
        assert key1.label == key2.label
        assert key1.content_type == key2.content_type
        assert key1.tags == key2.tags
        assert key1.etag != key2.etag
        if isinstance(key1, FeatureFlagConfigurationSetting):
            assert key1.enabled == key2.enabled
            assert len(key1.filters) == len(key2.filters)
        elif isinstance(key1, SecretReferenceConfigurationSetting):
            assert key1.secret_uri == key2.secret_uri
        else:
            assert key1.value == key2.value

    @app_config_decorator
    def test_update_json_by_value(self, client):
        key = self.get_resource_name("key")
        try:
            feature_flag = FeatureFlagConfigurationSetting(key, True)
            set_flag = client.set_configuration_setting(feature_flag)
            set_flag.filters.append(
                {
                    "name": TARGETING,
                    "parameters": {
                        u"Audience": {
                            u"Users": [u"abcd", u"defg"],
                            u"Groups": [u"ghij", u"jklm"],
                            u"DefaultRolloutPercentage": 50
                        }
                    }
                }
            )

            updated_flag = client.set_configuration_setting(set_flag)

            assert isinstance(updated_flag, FeatureFlagConfigurationSetting)
            assert isinstance(set_flag.filters, list)
        finally:
            client.delete_configuration_setting(key)

    @pytest.mark.skip("abc")
    @app_config_decorator
    def test_update_json_invalid_value(self, client):
        key = self.get_resource_name("key")
        try:
            new = FeatureFlagConfigurationSetting(
                key,
                True,
                filters=[
                    {
                        "name": TARGETING,
                        "parameters": {
                            u"Audience": {
                                u"Users": [u"abc", u"def"],
                                u"Groups": [u"ghi", u"jkl"],
                                u"DefaultRolloutPercentage": 75
                            }
                        }
                    }
                ]
            )

            sent_config = client.set_configuration_setting(new)

            self._assert_same_keys(new, sent_config)

            received = client.get_configuration_setting(key)
            received.filters = []
            invalid_flag = client.set_configuraiton_setting(received)

            assert isinstance(invalid_flag, ConfigurationSetting)
            assert not isinstance(invalid_flag, FeatureFlagConfigurationSetting)
        finally:
            client.delete_configuration_setting(key)