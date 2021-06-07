# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core import MatchConditions
from devtools_testutils import AzureTestCase
from azure.core.exceptions import (
    ResourceModifiedError,
    ResourceNotFoundError,
    ResourceExistsError,
    AzureError,
)
from azure.appconfiguration import (
    ResourceReadOnlyError,
    ConfigurationSetting,
    SecretReferenceConfigurationSetting,
    FeatureFlagConfigurationSetting,
    PERCENTAGE,
    TARGETING,
    TIME_WINDOW,
)
from azure.appconfiguration.aio import AzureAppConfigurationClient
from consts import (
    KEY,
    LABEL,
    TEST_VALUE,
    TEST_CONTENT_TYPE,
    LABEL_RESERVED_CHARS,
    PAGE_SIZE,
    KEY_UUID,
)
import pytest
import copy
import datetime
import os
import logging
import asyncio
import re
import copy

from async_wrapper import app_config_decorator
from async_proxy import AzureAppConfigurationClientProxy


class AppConfigurationClientTest(AzureTestCase):
    def __init__(self, method_name):
        super(AppConfigurationClientTest, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]

    def _delete_setting(self, client, item):
        client.delete_configuration_setting(
            key=item.key, label=item.label
        )

    def create_aad_client(self, base_url):
        cred = self.get_credential(AzureAppConfigurationClient, is_async=True)
        client = AzureAppConfigurationClient(base_url, cred)
        return AzureAppConfigurationClientProxy(client)

    # method: add_configuration_setting
    @app_config_decorator
    def test_add_configuration_setting(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        kv = ConfigurationSetting(
            key=KEY + "_ADD",
            label=LABEL,
            value=TEST_VALUE,
            content_type=TEST_CONTENT_TYPE,
            tags={"tag1": "tag1", "tag2": "tag2"},
        )
        created_kv = client.add_configuration_setting(kv)
        self._delete_setting(client, created_kv)
        assert (
            created_kv.label == kv.label
            and kv.value == kv.value
            and created_kv.content_type == kv.content_type
            and created_kv.tags == kv.tags
        )
        assert (
            created_kv.etag is not None
            and created_kv.last_modified is not None
            and created_kv.read_only is False
        )

    @app_config_decorator
    def test_add_existing_configuration_setting(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        with pytest.raises(ResourceExistsError):
            client.add_configuration_setting(
                ConfigurationSetting(
                    key=test_config_setting.key,
                    lable=test_config_setting.label,
                )
            )

    # method: set_configuration_setting
    @app_config_decorator
    def test_set_existing_configuration_setting_label_etag(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_set_kv = test_config_setting
        to_set_kv.value = to_set_kv.value + "a"
        to_set_kv.tags = {"a": "b", "c": "d"}
        set_kv = client.set_configuration_setting(to_set_kv)
        assert (
            to_set_kv.key == set_kv.key
            and to_set_kv.label == to_set_kv.label
            and to_set_kv.value == set_kv.value
            and to_set_kv.content_type == set_kv.content_type
            and to_set_kv.tags == set_kv.tags
            and to_set_kv.etag != set_kv.etag
        )

    @app_config_decorator
    def test_set_existing_configuration_setting_label_wrong_etag(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_set_kv = test_config_setting
        to_set_kv.value = to_set_kv.value + "a"
        to_set_kv.tags = {"a": "b", "c": "d"}
        to_set_kv.etag = "wrong etag"
        with pytest.raises(ResourceModifiedError):
            client.set_configuration_setting(to_set_kv, match_condition=MatchConditions.IfNotModified)

    @app_config_decorator
    def test_set_configuration_setting_etag(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        kv = ConfigurationSetting(
            key=KEY + "_SET",
            label=LABEL,
            value=TEST_VALUE,
            content_type=TEST_CONTENT_TYPE,
            tags={"tag1": "tag1", "tag2": "tag2"},
        )
        kv.etag = "random etag"
        with pytest.raises(ResourceModifiedError):
            client.set_configuration_setting(kv, match_condition=MatchConditions.IfNotModified)

    @app_config_decorator
    def test_set_configuration_setting_no_etag(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_set_kv = ConfigurationSetting(
            key=KEY + "_SET",
            label=LABEL,
            value=TEST_VALUE,
            content_type=TEST_CONTENT_TYPE,
            tags={"tag1": "tag1", "tag2": "tag2"},
        )
        set_kv = client.set_configuration_setting(to_set_kv)
        self._delete_setting(client, to_set_kv)
        assert (
            to_set_kv.key == set_kv.key
            and to_set_kv.label == set_kv.label
            and to_set_kv.value == set_kv.value
            and to_set_kv.content_type == set_kv.content_type
            and to_set_kv.tags == set_kv.tags
            and to_set_kv.etag != set_kv.etag
        )

    # method: get_configuration_setting
    @app_config_decorator
    def test_get_configuration_setting_no_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        compare_kv = test_config_setting_no_label
        fetched_kv = client.get_configuration_setting(compare_kv.key)
        assert (
            fetched_kv.key == compare_kv.key
            and fetched_kv.value == compare_kv.value
            and fetched_kv.content_type == compare_kv.content_type
            and fetched_kv.tags == compare_kv.tags
        )
        assert fetched_kv.label is None

    @app_config_decorator
    def test_get_configuration_setting_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        compare_kv = test_config_setting
        fetched_kv = client.get_configuration_setting(
            compare_kv.key, compare_kv.label
        )
        assert (
            fetched_kv.key == compare_kv.key
            and fetched_kv.value == compare_kv.value
            and fetched_kv.content_type == compare_kv.content_type
            and fetched_kv.tags == compare_kv.tags
        )
        assert fetched_kv.label is not None

    @app_config_decorator
    def test_get_non_existing_configuration_setting(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        compare_kv = test_config_setting
        with pytest.raises(ResourceNotFoundError):
            client.get_configuration_setting(
                compare_kv.key, compare_kv.label + "a"
            )

    # method: delete_configuration_setting
    @app_config_decorator
    def test_delete_with_key_no_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_delete_kv = test_config_setting_no_label
        client.delete_configuration_setting(to_delete_kv.key)
        with pytest.raises(ResourceNotFoundError):
            client.get_configuration_setting(to_delete_kv.key)

    @app_config_decorator
    def test_delete_with_key_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_delete_kv = test_config_setting
        client.delete_configuration_setting(
            to_delete_kv.key, label=to_delete_kv.label
        )
        with pytest.raises(ResourceNotFoundError):
            client.get_configuration_setting(
                to_delete_kv.key, label=to_delete_kv.label
            )

    @app_config_decorator
    def test_delete_non_existing(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        deleted_kv = client.delete_configuration_setting(
            "not_exist_" + KEY
        )
        assert deleted_kv is None

    @app_config_decorator
    def test_delete_correct_etag(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_delete_kv = test_config_setting_no_label
        deleted_kv = client.delete_configuration_setting(
            to_delete_kv.key, etag=to_delete_kv.etag
        )
        assert deleted_kv is not None
        with pytest.raises(ResourceNotFoundError):
            client.get_configuration_setting(to_delete_kv.key)

    @app_config_decorator
    def test_delete_wrong_etag(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_delete_kv = test_config_setting_no_label
        with pytest.raises(ResourceModifiedError):
            client.delete_configuration_setting(
                to_delete_kv.key, etag="wrong etag", match_condition=MatchConditions.IfNotModified
            )

    # method: list_configuration_settings
    @app_config_decorator
    def test_list_configuration_settings_key_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = client.list_configuration_settings(
            label_filter=LABEL, key_filter=KEY
        )
        assert len(items) == 1
        assert all(x.key == KEY and x.label == LABEL for x in items)


    @app_config_decorator
    def test_list_configuration_settings_only_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = client.list_configuration_settings(label_filter=LABEL)
        assert len(items) == 1
        assert all(x.label == LABEL for x in items)


    @app_config_decorator
    def test_list_configuration_settings_only_key(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = client.list_configuration_settings(key_filter=KEY)
        assert len(items) == 2
        assert all(x.key == KEY for x in items)


    @app_config_decorator
    def test_list_configuration_settings_fields(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = client.list_configuration_settings(
            key_filter="*", label_filter=LABEL, fields=["key", "content_type"]
        )
        assert len(items) == 1
        assert all(x.key and not x.label and x.content_type for x in items)

    @app_config_decorator
    def test_list_configuration_settings_reserved_chars(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        resered_char_kv = ConfigurationSetting(
            key=KEY, label=LABEL_RESERVED_CHARS, value=TEST_VALUE
        )
        resered_char_kv = client.add_configuration_setting(
            resered_char_kv
        )
        escaped_label = re.sub(r"((?!^)\*(?!$)|\\|,)", r"\\\1", LABEL_RESERVED_CHARS)
        items = client.list_configuration_settings(
            label_filter=escaped_label
        )
        assert len(items) == 1
        assert all(x.label == LABEL_RESERVED_CHARS for x in items)
        client.delete_configuration_setting(resered_char_kv.key)

    # NOTE: Label filter does not support wildcard at beginning on filters. https://docs.microsoft.com/en-us/azure/azure-app-configuration/rest-api-key-value#supported-filters
    @app_config_decorator
    def test_list_configuration_settings_contains(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = client.list_configuration_settings(
            label_filter=LABEL + "*"
        )
        assert len(items) == 1
        assert all(x.label == LABEL for x in items)

    @app_config_decorator
    def test_list_configuration_settings_correct_etag(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_list_kv = test_config_setting
        custom_headers = {"If-Match": to_list_kv.etag}
        items = client.list_configuration_settings(
            key_filter=to_list_kv.key, label_filter=to_list_kv.label, headers=custom_headers
        )
        assert len(items) == 1
        assert all(x.key == to_list_kv.key and x.label == to_list_kv.label for x in items)

    @app_config_decorator
    def test_list_configuration_settings_multi_pages(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        # create PAGE_SIZE+1 configuration settings to have at least two pages
        try:
            delete_me = [
                client.add_configuration_setting(
                    ConfigurationSetting(
                        key="multi_" + str(i) + KEY_UUID,
                        label="multi_label_" + str(i),
                        value="multi value",
                    )
                )
                for i in range(PAGE_SIZE + 1)
            ]
        except ResourceExistsError:
            pass
        items = client.list_configuration_settings(key_filter="multi_*")
        assert len(list(items)) > PAGE_SIZE

        # Remove the configuration settings
        try:
            [
                client.delete_configuration_setting(
                    key="multi_" + str(i) + KEY_UUID, label="multi_label_" + str(i)
                )
                for i in range(PAGE_SIZE + 1)
            ]
        except AzureError:
            pass

    @app_config_decorator
    def test_list_configuration_settings_null_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = client.list_configuration_settings(label_filter="\0")
        assert len(list(items)) > 0

    @app_config_decorator
    def test_list_configuration_settings_only_accepttime(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        exclude_today = client.list_configuration_settings(
            accept_datetime=datetime.datetime.today() + datetime.timedelta(days=-1)
        )
        all_inclusive = client.list_configuration_settings()
        assert len(list(all_inclusive)) > len(list(exclude_today))

    # method: list_revisions
    @app_config_decorator
    def test_list_revisions_key_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_list1 = test_config_setting
        items = client.list_revisions(
            label_filter=to_list1.label, key_filter=to_list1.key
        )
        assert len(items) >= 2
        assert all(x.key == to_list1.key and x.label == to_list1.label for x in items)

    @app_config_decorator
    def test_list_revisions_only_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = client.list_revisions(label_filter=LABEL)
        assert len(items) >= 1
        assert all(x.label == LABEL for x in items)

    @app_config_decorator
    def test_list_revisions_key_no_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = client.list_revisions(key_filter=KEY)
        assert len(items) >= 1
        assert all(x.key == KEY for x in items)

    @app_config_decorator
    def test_list_revisions_fields(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = client.list_revisions(
            key_filter="*", label_filter=LABEL, fields=["key", "content_type"]
        )
        assert all(
            x.key and not x.label and x.content_type
            and not x.tags and not x.etag
            for x in items)

    @app_config_decorator
    def test_list_revisions_correct_etag(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_list_kv = test_config_setting
        custom_headers = {"If-Match": to_list_kv.etag}
        items = client.list_revisions(
            key_filter=to_list_kv.key, label_filter=to_list_kv.label, headers=custom_headers
        )
        assert len(items) >= 1
        assert all(x.key == to_list_kv.key and x.label == to_list_kv.label for x in items)

    @app_config_decorator
    def test_read_only(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        kv = test_config_setting_no_label
        read_only_kv = client.set_read_only(kv)
        assert read_only_kv.read_only
        readable_kv = client.set_read_only(read_only_kv, False)
        assert not readable_kv.read_only

    @app_config_decorator
    def test_delete_read_only(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_delete_kv = test_config_setting_no_label
        read_only_kv = client.set_read_only(to_delete_kv)
        with pytest.raises(ResourceReadOnlyError):
            client.delete_configuration_setting(to_delete_kv.key)
        client.set_read_only(read_only_kv, False)
        client.delete_configuration_setting(to_delete_kv.key)
        with pytest.raises(ResourceNotFoundError):
            client.get_configuration_setting(to_delete_kv.key)

    @app_config_decorator
    def test_set_read_only(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_set_kv = test_config_setting
        to_set_kv.value = to_set_kv.value + "a"
        to_set_kv.tags = {"a": "b", "c": "d"}
        read_only_kv = client.set_read_only(to_set_kv)
        with pytest.raises(ResourceReadOnlyError):
            client.set_configuration_setting(read_only_kv)
        readable_kv = client.set_read_only(read_only_kv, False)
        readable_kv.value = to_set_kv.value
        readable_kv.tags = to_set_kv.tags
        set_kv = client.set_configuration_setting(readable_kv)
        assert (
                to_set_kv.key == set_kv.key
                and to_set_kv.label == to_set_kv.label
                and to_set_kv.value == set_kv.value
                and to_set_kv.content_type == set_kv.content_type
                and to_set_kv.tags == set_kv.tags
                and to_set_kv.etag != set_kv.etag
        )

    def _order_dict(self, d):
        from collections import OrderedDict
        new = OrderedDict()
        for k, v in d.items():
            new[k] = str(v)
        return new


    @app_config_decorator
    def test_sync_tokens(self, client):

        sync_tokens = copy.deepcopy(client.obj._sync_token_policy._sync_tokens)
        sync_token_header = self._order_dict(sync_tokens)
        sync_token_header = ",".join(str(x) for x in sync_token_header.values())

        new = ConfigurationSetting(
                key="KEY1",
                label=None,
                value="TEST_VALUE1",
                content_type=TEST_CONTENT_TYPE,
                tags={"tag1": "tag1", "tag2": "tag2"},
        )

        sent = client.set_configuration_setting(new)
        sync_tokens2 = copy.deepcopy(client.obj._sync_token_policy._sync_tokens)
        sync_token_header2 = self._order_dict(sync_tokens2)
        sync_token_header2 = ",".join(str(x) for x in sync_token_header2.values())
        assert sync_token_header != sync_token_header2

        new = ConfigurationSetting(
                key="KEY2",
                label=None,
                value="TEST_VALUE2",
                content_type=TEST_CONTENT_TYPE,
                tags={"tag1": "tag1", "tag2": "tag2"},
        )

        sent = client.set_configuration_setting(new)
        sync_tokens3 = copy.deepcopy(client.obj._sync_token_policy._sync_tokens)
        sync_token_header3 = self._order_dict(sync_tokens3)
        sync_token_header3 = ",".join(str(x) for x in sync_token_header3.values())
        assert sync_token_header2 != sync_token_header3

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
    def test_config_setting_feature_flag(self, client):
        feature_flag = FeatureFlagConfigurationSetting("test_feature", True)
        set_flag = client.set_configuration_setting(feature_flag)

        self._assert_same_keys(feature_flag, set_flag)

        set_flag.enabled = not set_flag.enabled
        changed_flag = client.set_configuration_setting(set_flag)
        self._assert_same_keys(set_flag, changed_flag)

        changed_flag.enabled = False
        assert changed_flag.value['enabled'] == False

        c = copy.deepcopy(changed_flag.value)
        c['enabled'] = True
        changed_flag.value = c
        assert changed_flag.enabled == True

        changed_flag.value = {}
        assert changed_flag.enabled == None
        assert changed_flag.value == {}

        with pytest.raises(ValueError):
            set_flag.value = "bad_value"
            _ = set_flag.enabled

        client.delete_configuration_setting(changed_flag.key)

    @app_config_decorator
    def test_config_setting_secret_reference(self, client):
        secret_reference = SecretReferenceConfigurationSetting(
            "ConnectionString", "https://test-test.vault.azure.net/secrets/connectionString")
        set_flag = client.set_configuration_setting(secret_reference)
        self._assert_same_keys(secret_reference, set_flag)

        set_flag.secret_uri = "https://test-test.vault.azure.net/new_secrets/connectionString"
        updated_flag = client.set_configuration_setting(set_flag)
        self._assert_same_keys(set_flag, updated_flag)

        assert isinstance(updated_flag, SecretReferenceConfigurationSetting)
        new_uri = "https://aka.ms/azsdk"
        new_uri2 = "https://aka.ms/azsdk/python"
        updated_flag.secret_uri = new_uri
        assert updated_flag.value['secret_uri'] == new_uri

        updated_flag.value = {'secret_uri': new_uri2}
        assert updated_flag.secret_uri == new_uri2

        with pytest.raises(ValueError):
            set_flag.value = "bad_value"
            _ = set_flag.secret_uri

        client.delete_configuration_setting(secret_reference.key)

    @app_config_decorator
    def test_feature_filter_targeting(self, client):
        new = FeatureFlagConfigurationSetting(
            "newflag",
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
        self._assert_same_keys(sent_config, new)

        assert isinstance(sent_config.filters[0], dict)
        assert len(sent_config.filters) == 1

        sent_config.filters[0]["parameters"]["Audience"]["DefaultRolloutPercentage"] = 80
        updated_sent_config = client.set_configuration_setting(sent_config)
        self._assert_same_keys(sent_config, updated_sent_config)

        updated_sent_config.filters.append(
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
        updated_sent_config.filters.append(
            {
                "name": TARGETING,
                "parameters": {
                    u"Audience": {
                        u"Users": [u"abcde", u"defgh"],
                        u"Groups": [u"ghijk", u"jklmn"],
                        u"DefaultRolloutPercentage": 100
                    }
                }
            }
        )

        sent_config = client.set_configuration_setting(updated_sent_config)
        self._assert_same_keys(sent_config, updated_sent_config)
        assert len(sent_config.filters) == 3

        client.delete_configuration_setting(updated_sent_config.key)

    @app_config_decorator
    def test_feature_filter_time_window(self, client):
        new = FeatureFlagConfigurationSetting(
            'time_window',
            True,
            filters=[
                {
                    "name": TIME_WINDOW,
                    "parameters": {
                        "Start": "Wed, 10 Mar 2021 05:00:00 GMT",
                        "End": "Fri, 02 Apr 2021 04:00:00 GMT"
                    }
                }
            ]
        )

        sent = client.set_configuration_setting(new)
        self._assert_same_keys(sent, new)

        sent.filters[0]["parameters"]["Start"] = "Thurs, 11 Mar 2021 05:00:00 GMT"
        new_sent = client.set_configuration_setting(sent)
        self._assert_same_keys(sent, new_sent)

        client.delete_configuration_setting(new_sent.key)

    @app_config_decorator
    def test_feature_filter_custom(self, client):
        new = FeatureFlagConfigurationSetting(
            'custom',
            True,
            filters=[
                {
                    "name": PERCENTAGE,
                    "parameters": {
                        "Value": 10,
                        "User": "user1"
                    }
                }
            ]
        )

        sent = client.set_configuration_setting(new)
        self._assert_same_keys(sent, new)

        sent.filters[0]["parameters"]["Value"] = 100
        new_sent = client.set_configuration_setting(sent)
        self._assert_same_keys(sent, new_sent)

        client.delete_configuration_setting(new_sent.key)

    @app_config_decorator
    def test_feature_filter_multiple(self, client):
        new = FeatureFlagConfigurationSetting(
            'custom',
            True,
            filters=[
                {
                    "name": PERCENTAGE,
                    "parameters": {
                        "Value": 10
                    }
                },
                {
                    "name": TIME_WINDOW,
                    "parameters": {
                        "Start": "Wed, 10 Mar 2021 05:00:00 GMT",
                        "End": "Fri, 02 Apr 2021 04:00:00 GMT"
                    }
                },
                {
                    "name": TARGETING,
                    "parameters": {
                        u"Audience": {
                            u"Users": [u"abcde", u"defgh"],
                            u"Groups": [u"ghijk", u"jklmn"],
                            u"DefaultRolloutPercentage": 100
                        }
                    }
                }
            ]
        )

        sent = client.set_configuration_setting(new)
        self._assert_same_keys(sent, new)

        sent.filters[0]["parameters"]["Value"] = 100
        sent.filters[1]["parameters"]["Start"] = "Wed, 10 Mar 2021 08:00:00 GMT"
        sent.filters[2]["parameters"]["Audience"]["DefaultRolloutPercentage"] = 100

        new_sent = client.set_configuration_setting(sent)
        self._assert_same_keys(sent, new_sent)

        assert new_sent.filters[0]["parameters"]["Value"] == 100
        assert new_sent.filters[1]["parameters"]["Start"] == "Wed, 10 Mar 2021 08:00:00 GMT"
        assert new_sent.filters[2]["parameters"]["Audience"]["DefaultRolloutPercentage"] == 100

        client.delete_configuration_setting(new_sent.key)