# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core import MatchConditions
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
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
import hashlib
from app_configuration_preparer import AppConfigurationPreparer
from app_configuration_client_preparer import AppConfigurationClientPreparer

class AppConfigurationClientTest(AzureMgmtTestCase):
    try:
        name_prefix = "appconfig-" + hashlib.md5(os.environ['RUN_IDENTIFIER'].encode()).hexdigest()[-3:]
    except KeyError:
        name_prefix = "appconfig"

    def __init__(self, method_name):
        super(AppConfigurationClientTest, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]

    def prepare_kv(self, app_config_client):
        self.test_config_setting = self._add_for_test(
            ConfigurationSetting(
                key=KEY,
                label=LABEL,
                value=TEST_VALUE,
                content_type=TEST_CONTENT_TYPE,
                tags={"tag1": "tag1", "tag2": "tag2"},
            ), app_config_client
        )
        self.test_config_setting_no_label = self._add_for_test(
            ConfigurationSetting(
                key=KEY,
                label=None,
                value=TEST_VALUE,
                content_type=TEST_CONTENT_TYPE,
                tags={"tag1": "tag1", "tag2": "tag2"},
            ), app_config_client
        )
        self.to_delete = [self.test_config_setting, self.test_config_setting_no_label]

    def cleanup_kv(self, app_config_client):
        for item in self.to_delete:
            app_config_client.delete_configuration_setting(
                key=item.key, label=item.label
            )

    def _add_for_test(self, kv, app_config_client):
        exist = bool(
            list(
                app_config_client.list_configuration_settings(
                    key_filter=kv.key, label_filter=kv.label
                )
            )
        )
        if exist:
            self._delete_from_test(kv.key, kv.label, app_config_client)
        return app_config_client.add_configuration_setting(kv)

    def _delete_from_test(self, key, label, app_config_client):
        try:
            app_config_client.delete_configuration_setting(key=key, label=label)
        except AzureError:
            logging.debug(
                "Error occurred removing configuration setting %s %s during unit test"
                % (key, label)
            )
    
    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    # method: add_configuration_setting
    def test_add_configuration_setting(self, app_config_client):
        self.prepare_kv(app_config_client)
        kv = ConfigurationSetting(
            key=KEY + "_ADD",
            label=LABEL,
            value=TEST_VALUE,
            content_type=TEST_CONTENT_TYPE,
            tags={"tag1": "tag1", "tag2": "tag2"},
        )
        created_kv = app_config_client.add_configuration_setting(kv)
        self.to_delete.append(created_kv)
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
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_add_existing_configuration_setting(self, app_config_client):
        self.prepare_kv(app_config_client)
        with pytest.raises(ResourceExistsError):
            app_config_client.add_configuration_setting(
                ConfigurationSetting(
                    key=self.test_config_setting.key,
                    label=self.test_config_setting.label,
                )
            )
        self.cleanup_kv(app_config_client)


    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    # method: set_configuration_setting
    def test_set_existing_configuration_setting_label_etag(self, app_config_client):
        self.prepare_kv(app_config_client)
        to_set_kv = self.test_config_setting
        to_set_kv.value = to_set_kv.value + "a"
        to_set_kv.tags = {"a": "b", "c": "d"}
        set_kv = app_config_client.set_configuration_setting(to_set_kv)
        assert (
            to_set_kv.key == set_kv.key
            and to_set_kv.label == to_set_kv.label
            and to_set_kv.value == set_kv.value
            and to_set_kv.content_type == set_kv.content_type
            and to_set_kv.tags == set_kv.tags
            and to_set_kv.etag != set_kv.etag
        )
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_set_existing_configuration_setting_label_wrong_etag(self, app_config_client):
        self.prepare_kv(app_config_client)
        to_set_kv = self.test_config_setting
        to_set_kv.value = to_set_kv.value + "a"
        to_set_kv.tags = {"a": "b", "c": "d"}
        to_set_kv.etag = "wrong etag"
        with pytest.raises(ResourceModifiedError):
            app_config_client.set_configuration_setting(to_set_kv, match_condition=MatchConditions.IfNotModified)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_set_configuration_setting_etag(self, app_config_client):
        self.prepare_kv(app_config_client)
        kv = ConfigurationSetting(
            key=KEY + "_SET",
            label=LABEL,
            value=TEST_VALUE,
            content_type=TEST_CONTENT_TYPE,
            tags={"tag1": "tag1", "tag2": "tag2"},
        )
        kv.etag = "random etag"
        with pytest.raises(ResourceModifiedError):
            app_config_client.set_configuration_setting(kv, match_condition=MatchConditions.IfNotModified)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_set_configuration_setting_no_etag(self, app_config_client):
        self.prepare_kv(app_config_client)
        to_set_kv = ConfigurationSetting(
            key=KEY + "_SET",
            label=LABEL,
            value=TEST_VALUE,
            content_type=TEST_CONTENT_TYPE,
            tags={"tag1": "tag1", "tag2": "tag2"},
        )
        set_kv = app_config_client.set_configuration_setting(to_set_kv)
        self.to_delete.append(to_set_kv)
        assert (
            to_set_kv.key == set_kv.key
            and to_set_kv.label == set_kv.label
            and to_set_kv.value == set_kv.value
            and to_set_kv.content_type == set_kv.content_type
            and to_set_kv.tags == set_kv.tags
            and to_set_kv.etag != set_kv.etag
        )
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    # method: get_configuration_setting
    def test_get_configuration_setting_no_label(self, app_config_client):
        self.prepare_kv(app_config_client)
        compare_kv = self.test_config_setting_no_label
        fetched_kv = app_config_client.get_configuration_setting(compare_kv.key)
        assert (
            fetched_kv.key == compare_kv.key
            and fetched_kv.value == compare_kv.value
            and fetched_kv.content_type == compare_kv.content_type
            and fetched_kv.tags == compare_kv.tags
        )
        assert fetched_kv.label is None
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_get_configuration_setting_label(self, app_config_client):
        self.prepare_kv(app_config_client)
        compare_kv = self.test_config_setting
        fetched_kv = app_config_client.get_configuration_setting(
            compare_kv.key, compare_kv.label
        )
        assert (
            fetched_kv.key == compare_kv.key
            and fetched_kv.value == compare_kv.value
            and fetched_kv.content_type == compare_kv.content_type
            and fetched_kv.tags == compare_kv.tags
        )
        assert fetched_kv.label is not None
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_get_non_existing_configuration_setting(self, app_config_client):
        self.prepare_kv(app_config_client)
        compare_kv = self.test_config_setting
        with pytest.raises(ResourceNotFoundError):
            app_config_client.get_configuration_setting(
                compare_kv.key, compare_kv.label + "a"
            )
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    # method: delete_configuration_setting
    def test_delete_with_key_no_label(self, app_config_client):
        self.prepare_kv(app_config_client)
        to_delete_kv = self.test_config_setting_no_label
        app_config_client.delete_configuration_setting(to_delete_kv.key)
        self.to_delete.remove(to_delete_kv)
        with pytest.raises(ResourceNotFoundError):
            app_config_client.get_configuration_setting(to_delete_kv.key)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_delete_with_key_label(self, app_config_client):
        self.prepare_kv(app_config_client)
        to_delete_kv = self.test_config_setting
        app_config_client.delete_configuration_setting(
            to_delete_kv.key, label=to_delete_kv.label
        )
        self.to_delete.remove(to_delete_kv)
        with pytest.raises(ResourceNotFoundError):
            app_config_client.get_configuration_setting(
                to_delete_kv.key, label=to_delete_kv.label
            )
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_delete_non_existing(self, app_config_client):
        self.prepare_kv(app_config_client)
        deleted_kv = app_config_client.delete_configuration_setting(
            "not_exist_" + KEY
        )
        assert deleted_kv is None
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_delete_correct_etag(self, app_config_client):
        self.prepare_kv(app_config_client)
        to_delete_kv = self.test_config_setting_no_label
        deleted_kv = app_config_client.delete_configuration_setting(
            to_delete_kv.key, etag=to_delete_kv.etag
        )
        self.to_delete.remove(to_delete_kv)
        assert deleted_kv is not None
        with pytest.raises(ResourceNotFoundError):
            app_config_client.get_configuration_setting(to_delete_kv.key)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_delete_wrong_etag(self, app_config_client):
        self.prepare_kv(app_config_client)
        to_delete_kv = self.test_config_setting_no_label
        with pytest.raises(ResourceModifiedError):
            app_config_client.delete_configuration_setting(
                to_delete_kv.key, etag="wrong etag", match_condition=MatchConditions.IfNotModified
            )
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    # method: list_configuration_settings
    def test_list_configuration_settings_key_label(self, app_config_client):
        self.prepare_kv(app_config_client)
        items = list(app_config_client.list_configuration_settings(
            label_filter=LABEL, key_filter=KEY
        ))
        assert len(items) == 1
        assert all(x.label == LABEL and x.label == LABEL for x in items)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_list_configuration_settings_only_label(self, app_config_client):
        self.prepare_kv(app_config_client)
        items = list(app_config_client.list_configuration_settings(label_filter=LABEL))
        assert len(items) == 1
        assert all(x.label == LABEL for x in items)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_list_configuration_settings_only_key(self, app_config_client):
        self.prepare_kv(app_config_client)
        items = list(app_config_client.list_configuration_settings(key_filter=KEY))
        assert len(items) == 2
        assert all(x.key == KEY for x in items)
        self.cleanup_kv(app_config_client)


    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_list_configuration_settings_fields(self, app_config_client):
        self.prepare_kv(app_config_client)
        items = list(app_config_client.list_configuration_settings(
            key_filter="*", label_filter=LABEL, fields=["key", "content_type"]
        ))
        assert len(items) == 1
        assert all(x.key and not x.label and x.content_type for x in items)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_list_configuration_settings_reserved_chars(self, app_config_client):
        self.prepare_kv(app_config_client)
        resered_char_kv = ConfigurationSetting(
            key=KEY, label=LABEL_RESERVED_CHARS, value=TEST_VALUE
        )
        resered_char_kv = app_config_client.add_configuration_setting(
            resered_char_kv
        )
        self.to_delete.append(resered_char_kv)
        escaped_label = re.sub(r"((?!^)\*(?!$)|\\|,)", r"\\\1", LABEL_RESERVED_CHARS)
        items = list(app_config_client.list_configuration_settings(
            label_filter=escaped_label
        ))
        assert len(items) == 1
        assert all(x.label == LABEL_RESERVED_CHARS for x in items)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_list_configuration_settings_contains(self, app_config_client):
        self.prepare_kv(app_config_client)
        items = list(app_config_client.list_configuration_settings(
            label_filter="*" + LABEL + "*"
        ))
        assert len(items) == 1
        assert all(x.label == LABEL for x in items)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_list_configuration_settings_correct_etag(self, app_config_client):
        self.prepare_kv(app_config_client)
        to_list_kv = self.test_config_setting
        custom_headers = {"If-Match": to_list_kv.etag}
        items = list(app_config_client.list_configuration_settings(
            key_filter=to_list_kv.key, label_filter=to_list_kv.label, headers=custom_headers
        ))
        assert len(items) == 1
        assert all(x.key == to_list_kv.key and x.label == to_list_kv.label for x in items)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_list_configuration_settings_multi_pages(self, app_config_client):
        # create PAGE_SIZE+1 configuration settings to have at least two pages
        try:
            delete_me = [
                app_config_client.add_configuration_setting(
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
        items = app_config_client.list_configuration_settings(key_filter="multi_*")
        assert len(list(items)) > PAGE_SIZE

        # Remove the configuration settings
        try:
            [
                app_config_client.delete_configuration_setting(
                    key="multi_" + str(i) + KEY_UUID, label="multi_label_" + str(i)
                )
                for i in range(PAGE_SIZE + 1)
            ]
        except AzureError:
            pass

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_list_configuration_settings_null_label(self, app_config_client):
        self.prepare_kv(app_config_client)
        items = app_config_client.list_configuration_settings(label_filter="\0")
        assert len(list(items)) > 0
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_list_configuration_settings_only_accepttime(self, app_config_client):
        self.prepare_kv(app_config_client)
        exclude_today = app_config_client.list_configuration_settings(
            accept_datetime=datetime.datetime.today() + datetime.timedelta(days=-1)
        )
        all_inclusive = app_config_client.list_configuration_settings()
        assert len(list(all_inclusive)) > len(list(exclude_today))
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    # method: list_revisions
    def test_list_revisions_key_label(self, app_config_client):
        self.prepare_kv(app_config_client)
        to_list1 = self.test_config_setting
        items = list(app_config_client.list_revisions(
            label_filter=to_list1.label, key_filter=to_list1.key
        ))
        assert len(items) >= 1
        assert all(x.key == to_list1.key and x.label == to_list1.label for x in items)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_list_revisions_only_label(self, app_config_client):
        self.prepare_kv(app_config_client)
        items = list(app_config_client.list_revisions(label_filter=LABEL))
        assert len(items) >= 1
        assert all(x.label == LABEL for x in items)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_list_revisions_key_no_label(self, app_config_client):
        self.prepare_kv(app_config_client)
        items = list(app_config_client.list_revisions(key_filter=KEY))
        assert len(items) >= 1
        assert all(x.key == KEY for x in items)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_list_revisions_fields(self, app_config_client):
        self.prepare_kv(app_config_client)
        items = list(app_config_client.list_revisions(
            key_filter="*", label_filter=LABEL, fields=["key", "content_type"]
        ))
        assert all(x.key and not x.label and x.content_type and not x.tags and not x.etag for x in items)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_list_revisions_correct_etag(self, app_config_client):
        self.prepare_kv(app_config_client)
        to_list_kv = self.test_config_setting
        custom_headers = {"If-Match": to_list_kv.etag}
        items = list(app_config_client.list_revisions(
            key_filter=to_list_kv.key, label_filter=to_list_kv.label, headers=custom_headers
        ))
        assert len(items) >= 1
        assert all(x.key == to_list_kv.key and x.label == to_list_kv.label for x in items)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_read_only(self, app_config_client):
        self.prepare_kv(app_config_client)
        kv = self.test_config_setting_no_label
        read_only_kv = app_config_client.set_read_only(kv)
        assert read_only_kv.read_only
        readable_kv = app_config_client.set_read_only(read_only_kv, False)
        assert not readable_kv.read_only
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_delete_read_only(self, app_config_client):
        self.prepare_kv(app_config_client)
        to_delete_kv = self.test_config_setting_no_label
        read_only_kv = app_config_client.set_read_only(to_delete_kv)
        with pytest.raises(ResourceReadOnlyError):
            app_config_client.delete_configuration_setting(to_delete_kv.key)
        app_config_client.set_read_only(read_only_kv, False)
        app_config_client.delete_configuration_setting(to_delete_kv.key)
        self.to_delete.remove(to_delete_kv)
        with pytest.raises(ResourceNotFoundError):
            app_config_client.get_configuration_setting(to_delete_kv.key)
        self.cleanup_kv(app_config_client)

    @ResourceGroupPreparer(name_prefix=name_prefix)
    @AppConfigurationPreparer(aad_mode=True)
    @AppConfigurationClientPreparer(aad_mode=True)
    def test_set_read_only(self, app_config_client):
        self.prepare_kv(app_config_client)
        to_set_kv = self.test_config_setting
        to_set_kv.value = to_set_kv.value + "a"
        to_set_kv.tags = {"a": "b", "c": "d"}
        read_only_kv = app_config_client.set_read_only(to_set_kv)
        with pytest.raises(ResourceReadOnlyError):
            app_config_client.set_configuration_setting(read_only_kv)
        readable_kv = app_config_client.set_read_only(read_only_kv, False)
        readable_kv.value = to_set_kv.value
        readable_kv.tags = to_set_kv.tags
        set_kv = app_config_client.set_configuration_setting(readable_kv)
        assert (
                to_set_kv.key == set_kv.key
                and to_set_kv.label == to_set_kv.label
                and to_set_kv.value == set_kv.value
                and to_set_kv.content_type == set_kv.content_type
                and to_set_kv.tags == set_kv.tags
                and to_set_kv.etag != set_kv.etag
        )
        self.cleanup_kv(app_config_client)
