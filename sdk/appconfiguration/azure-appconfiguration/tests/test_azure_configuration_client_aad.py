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
    AzureAppConfigurationClient,
    ConfigurationSetting,
)
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
import datetime
import os
import logging
import re
import functools

from wrapper import app_config_decorator


class AppConfigurationClientTest(AzureTestCase):
    def __init__(self, method_name):
        super(AppConfigurationClientTest, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]

    def _delete_setting(self, client, item):
        client.delete_configuration_setting(
            key=item.key, label=item.label
        )

    def create_aad_client(self, base_url):
        cred = self.get_credential(AzureAppConfigurationClient)
        return AzureAppConfigurationClient(base_url, cred)

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
        self._delete_setting(client, to_delete_kv)
        with pytest.raises(ResourceNotFoundError):
            client.get_configuration_setting(to_delete_kv.key)

    @app_config_decorator
    def test_delete_with_key_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_delete_kv = test_config_setting
        client.delete_configuration_setting(
            to_delete_kv.key, label=to_delete_kv.label
        )
        self._delete_setting(client, to_delete_kv)
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
        self._delete_setting(client, to_delete_kv)
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
        items = list(client.list_configuration_settings(
            label_filter=LABEL, key_filter=KEY
        ))
        assert len(items) == 1
        assert all(x.key == KEY and x.label == LABEL for x in items)

    @app_config_decorator
    def test_list_configuration_settings_only_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = list(client.list_configuration_settings(label_filter=LABEL))
        assert len(items) == 1
        assert all(x.label == LABEL for x in items)

    @pytest.mark.skip("3 != 2, three items are returned")
    @app_config_decorator
    def test_list_configuration_settings_only_key(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = list(client.list_configuration_settings(key_filter=KEY))
        assert len(items) == 2
        assert all(x.key == KEY for x in items)

    @app_config_decorator
    def test_list_configuration_settings_fields(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = list(client.list_configuration_settings(
            key_filter="*", label_filter=LABEL, fields=["key", "content_type"]
        ))
        assert len(items) == 1
        assert all(x.key and not x.label and x.content_type for x in items)

    @pytest.mark.skip("ResourceExistsError: Operation returned an invalid status 'Precondition Failed'")
    @app_config_decorator
    def test_list_configuration_settings_reserved_chars(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        resered_char_kv = ConfigurationSetting(
            key=KEY, label=LABEL_RESERVED_CHARS, value=TEST_VALUE
        )
        resered_char_kv = client.add_configuration_setting(
            resered_char_kv
        )
        self._delete_setting(client, resered_char_kv)
        escaped_label = re.sub(r"((?!^)\*(?!$)|\\|,)", r"\\\1", LABEL_RESERVED_CHARS)
        items = list(client.list_configuration_settings(
            label_filter=escaped_label
        ))
        assert len(items) == 1
        assert all(x.label == LABEL_RESERVED_CHARS for x in items)

    @pytest.mark.skip("Bad Request")
    @app_config_decorator
    def test_list_configuration_settings_contains(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = list(client.list_configuration_settings(
            label_filter="*" + LABEL + "*"
        ))
        assert len(items) == 1
        assert all(x.label == LABEL for x in items)

    @app_config_decorator
    def test_list_configuration_settings_correct_etag(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_list_kv = test_config_setting
        custom_headers = {"If-Match": to_list_kv.etag}
        items = list(client.list_configuration_settings(
            key_filter=to_list_kv.key, label_filter=to_list_kv.label, headers=custom_headers
        ))
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
        items = list(client.list_revisions(
            label_filter=to_list1.label, key_filter=to_list1.key
        ))
        assert len(items) >= 2
        assert all(x.key == to_list1.key and x.label == to_list1.label for x in items)

    @app_config_decorator
    def test_list_revisions_only_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = list(client.list_revisions(label_filter=LABEL))
        assert len(items) >= 1
        assert all(x.label == LABEL for x in items)

    @app_config_decorator
    def test_list_revisions_key_no_label(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = list(client.list_revisions(key_filter=KEY))
        assert len(items) >= 1
        assert all(x.key == KEY for x in items)

    @pytest.mark.skip("Operation returned an invalid status 'Internal Server Error'")
    @app_config_decorator
    def test_list_revisions_fields(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        items = list(client.list_revisions(
            key_filter="*", label_filter=LABEL, fields=["key", "content_type"]
        ))
        assert all(x.key and not x.label and x.content_type and not x.tags and not x.etag for x in items)

    @app_config_decorator
    def test_list_revisions_correct_etag(self, appconfiguration_endpoint_string, test_config_setting, test_config_setting_no_label):
        client = self.create_aad_client(appconfiguration_endpoint_string)
        to_list_kv = test_config_setting
        custom_headers = {"If-Match": to_list_kv.etag}
        items = list(client.list_revisions(
            key_filter=to_list_kv.key, label_filter=to_list_kv.label, headers=custom_headers
        ))
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
        self._delete_setting(client, to_delete_kv)
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
