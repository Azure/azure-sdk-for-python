# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import uuid
import pytest
from copy import copy
import os
import unittest
import logging
import datetime

from msrestazure.azure_exceptions import CloudError
from azure.configuration import AzureConfigurationClient
from azure.configuration import ConfigurationSetting
from devtools_testutils import AzureMgmtTestCase

PAGE_SIZE = 100


class AzConfigTestData:
    def __init__(self):
        self.key_uuid = None
        self.label1 = None
        self.label2 = None  # contains reserved chars *,\
        self.label_uuid = None
        self.label1_data = []
        self.label2_data = []
        self.no_label_data = []


class AzConfigurationClientTest(AzureMgmtTestCase):
    def _add_for_test(self, kv):
        exist = bool(list(self.app_config_client.list_configuration_settings(keys=[kv.key], labels=[kv.label])))
        if exist:
            self._delete_from_test(key=kv.key, label=kv.label)
        return self.app_config_client.add_configuration_setting(kv)

    def _delete_from_test(self, key, label):
        try:
            self.app_config_client.delete_configuration_setting(key=key, label=label)
        except CloudError:
            logging.debug("Error occurred removing configuration setting %s %s" % (key, label))

    def setUp(self):
        self.working_folder = os.path.dirname(__file__)
        super(AzConfigurationClientTest, self).setUp()

        connection_str = os.environ['AZ_CONFIG_CONNECTION']
        app_config_client = AzureConfigurationClient(connection_str)
        self.app_config_client = app_config_client

        key_uuid = "test_key_a6af8952-54a6-11e9-b600-2816a84d0309"
        label_uuid = "1d7b2b28-549e-11e9-b51c-2816a84d0309"
        label1 = "test_label1_" + label_uuid
        label2 = "test_label2_*, \\" + label_uuid
        test_content_type = "test_content_type"
        test_value = "test_value"

        test_data = AzConfigTestData()
        self.test_data = test_data
        test_data.key_uuid = key_uuid
        test_data.label_uuid = label_uuid
        test_data.label1 = label1
        test_data.label2 = label2

        test_data.label1_data.append(
            self._add_for_test(
                ConfigurationSetting(
                    key=key_uuid + "_1",
                    label=label1,
                    value=test_value,
                    tags={
                        "tag1": "tag1",
                        "tag2": "tag2"
                    },
                    content_type=test_content_type
                )
            )
        )
        test_data.label2_data.append(
            self._add_for_test(
                ConfigurationSetting(
                    key=key_uuid + "_2",
                    label=label2,
                    value=test_value,
                    tags={
                        "tag1": "tag1",
                        "tag2": "tag2"
                    },
                    content_type=test_content_type
                )
            )
        )

        # create a configuration_setting object without label
        test_data.no_label_data.append(
            self._add_for_test(
                ConfigurationSetting(
                    key=key_uuid + "_3",
                    label=None,
                    value=test_value,
                    tags={
                        "tag1": "tag1",
                        "tag2": "tag2"
                    },
                    content_type=test_content_type
                )
            )
        )

    def tearDown(self):
        for kv in self.test_data.label1_data:
            self._delete_from_test(kv.key, label=kv.label)
        for kv in self.test_data.label2_data:
            self._delete_from_test(kv.key, label=kv.label)
        for kv in self.test_data.no_label_data:
            self._delete_from_test(kv.key, label=kv.label)

    # method: add_configuration_setting
    # @record
    def test_add_configuration_setting(self):

        kv = ConfigurationSetting()
        kv.key = "unit_test_key_add_" + self.test_data.key_uuid
        kv.label = self.test_data.label1
        kv.value = "test value"
        kv.content_type = "test content type"
        kv.tags = {"tag1": "tag1", "tag2": "tag2"}
        kv.etag = "not needed"  # this etag will not be processed.
        created_kv = self.app_config_client.add_configuration_setting(kv)
        self.app_config_client.delete_configuration_setting(kv.key, kv.label)
        assert (
            created_kv.label == kv.label
            and kv.value == kv.value
            and created_kv.content_type == kv.content_type
            and created_kv.tags == kv.tags
        )
        assert (
            created_kv.etag is not None
            and created_kv.last_modified is not None
            and created_kv.locked is False
        )

    def test_add_existing_configuration_setting(self):
        kv = ConfigurationSetting()
        compare_kv = self.test_data.label1_data[0]
        kv.key = compare_kv.key
        kv.label = compare_kv.label
        kv.value = compare_kv.value
        kv.content_type = compare_kv.content_type

        with pytest.raises(CloudError):
            self.app_config_client.add_configuration_setting(kv)

    def test_add_configuration_setting_no_label(self):
        kv = ConfigurationSetting()
        kv.key = "unit_test_key_add" + self.test_data.key_uuid
        # kv.label is None by default
        kv.value = "test value"
        kv.content_type = "test content type"
        kv.tags = {"tag1": "tag1", "tag2": "tag2"}
        kv.etag = "not needed"  # this etag will not be processed.
        created_kv = self.app_config_client.add_configuration_setting(kv)
        self.app_config_client.delete_configuration_setting(kv.key, kv.label)
        assert (
            kv.value == kv.value
            and created_kv.content_type == kv.content_type
            and created_kv.tags == kv.tags
        )
        assert (
            created_kv.etag is not None
            and created_kv.last_modified is not None
            and created_kv.locked is False
            and created_kv.label is None
        )

    def test_add_existing_configuration_setting_no_label(self):
        kv = ConfigurationSetting()
        compare_kv = self.test_data.no_label_data[0]
        kv.key = compare_kv.key
        kv.value = compare_kv.value
        kv.content_type = compare_kv.content_type

        with pytest.raises(CloudError):
            self.app_config_client.add_configuration_setting(kv)

    # method: set_configuration_setting
    def test_set_existing_configuration_setting_no_label_etag(self):
        sample_kv = copy(self.test_data.no_label_data[-1])

        # create a new key value into AzConfig service
        sample_kv.key = "unit_test_key_set_" + self.test_data.key_uuid
        to_set_kv = self.app_config_client.add_configuration_setting(sample_kv)
        to_set_kv.value = to_set_kv.value + "a"
        to_set_kv.tags = {"a": "b", "c": "d"}
        set_kv = self.app_config_client.set_configuration_setting(to_set_kv)
        # remove the new key value from the service
        self.app_config_client.delete_configuration_setting(set_kv.key)
        assert (
            to_set_kv.key == set_kv.key
            and None is set_kv.label
            and to_set_kv.value == set_kv.value
            and to_set_kv.content_type == set_kv.content_type
            and to_set_kv.tags == set_kv.tags
            and to_set_kv.etag != set_kv.etag
        )

    def test_set_existing_configuration_setting_label_etag(self):
        sample_kv = copy(self.test_data.label1_data[-1])

        # create a new key value into AzConfig service
        sample_kv.key = "unit_test_key_set" + self.test_data.key_uuid
        to_set_kv = self.app_config_client.add_configuration_setting(sample_kv)
        to_set_kv.value = to_set_kv.value + "a"
        to_set_kv.tags = {"a": "b", "c": "d"}
        set_kv = self.app_config_client.set_configuration_setting(to_set_kv)
        # remove the new key value from the service
        self.app_config_client.delete_configuration_setting(set_kv.key, label=set_kv.label)
        assert (
            to_set_kv.key == set_kv.key
            and to_set_kv.label == to_set_kv.label
            and to_set_kv.value == set_kv.value
            and to_set_kv.content_type == set_kv.content_type
            and to_set_kv.tags == set_kv.tags
            and to_set_kv.etag != set_kv.etag
        )

    def test_set_existing_configuration_setting_label_wrong_etag(self):
        sample_kv = copy(self.test_data.label1_data[-1])

        # create a new key value into AzConfig service
        sample_kv.key = "unit_test_key_set" + self.test_data.key_uuid
        to_set_kv = self.app_config_client.add_configuration_setting(sample_kv)
        to_set_kv.value = to_set_kv.value + "a"
        to_set_kv.tags = {"a": "b", "c": "d"}
        to_set_kv.etag = "wrong etag"
        with pytest.raises(CloudError):
            self.app_config_client.set_configuration_setting(to_set_kv)
        self.app_config_client.delete_configuration_setting(to_set_kv.key, label=to_set_kv.label)

    def test_set_configuration_setting_no_label_etag(self):
        to_set_kv = copy(self.test_data.no_label_data[-1])
        to_set_kv.key = "unit_test_key_set" + self.test_data.key_uuid
        with pytest.raises(CloudError):
            self.app_config_client.set_configuration_setting(to_set_kv)

    def test_set_configuration_setting_label_etag(self):
        to_set_kv = copy(self.test_data.label1_data[-1])
        to_set_kv.key = "unit_test_key_set" + self.test_data.key_uuid
        with pytest.raises(CloudError):
            self.app_config_client.set_configuration_setting(to_set_kv)

    def test_set_configuration_setting_no_label_no_etag(self):
        to_set_kv = copy(self.test_data.no_label_data[-1])
        to_set_kv.key = "unit_test_key_set" + self.test_data.key_uuid
        to_set_kv.etag = None
        set_kv = self.app_config_client.set_configuration_setting(to_set_kv)
        # remove immediately from the AzConfig service
        self.app_config_client.delete_configuration_setting(set_kv.key)
        assert (
            to_set_kv.key == set_kv.key
            and None is set_kv.label
            and to_set_kv.value == set_kv.value
            and to_set_kv.content_type == set_kv.content_type
            and to_set_kv.tags == set_kv.tags
            and to_set_kv.etag != set_kv.etag
        )

    def test_set_configuration_setting_label_no_etag(
        self
    ):
        to_set_kv = copy(self.test_data.label1_data[-1])
        to_set_kv.key = "unit_test_key_set" + self.test_data.key_uuid
        to_set_kv.etag = None
        set_kv = self.app_config_client.set_configuration_setting(to_set_kv)
        # remove immediately from the AzConfig service
        self.app_config_client.delete_configuration_setting(set_kv.key, label=set_kv.label)
        assert (
            to_set_kv.key == set_kv.key
            and to_set_kv.label == set_kv.label
            and to_set_kv.value == set_kv.value
            and to_set_kv.content_type == set_kv.content_type
            and to_set_kv.tags == set_kv.tags
            and to_set_kv.etag != set_kv.etag
        )

    # method: update_configuration_setting
    def test_update_existing_configuration_setting_no_label_etag(
        self
    ):
        sample_kv = copy(self.test_data.no_label_data[-1])

        # create a new key value into AzConfig service
        sample_kv.key = "unit_test_key_" + self.test_data.key_uuid
        to_update_kv = self.app_config_client.add_configuration_setting(sample_kv)
        tags = {"a": "b", "c": "d"}
        updated_kv = self.app_config_client.update_configuration_setting(
            to_update_kv.key, value="updated_value", tags=tags, etag=to_update_kv.etag
        )
        # remove the new key value from the service
        self.app_config_client.delete_configuration_setting(updated_kv.key)
        assert (
            to_update_kv.key == updated_kv.key
            and None is updated_kv.label
            and "updated_value" == updated_kv.value
            and to_update_kv.content_type == updated_kv.content_type
            and tags == updated_kv.tags
            and to_update_kv.etag != updated_kv.etag
        )

    def test_update_existing_configuration_setting_label_etag(
        self
    ):
        sample_kv = copy(self.test_data.label1_data[-1])

        # create a new key value into AzConfig service
        sample_kv.key = "unit_test_key_" + self.test_data.key_uuid
        to_update_kv = self.app_config_client.add_configuration_setting(sample_kv)
        tags = {"a": "b", "c": "d"}
        updated_kv = self.app_config_client.update_configuration_setting(
            to_update_kv.key,
            label=to_update_kv.label,
            value="updated_value",
            tags=tags,
            etag=to_update_kv.etag,
        )
        # remove the new key value from the service
        self.app_config_client.delete_configuration_setting(updated_kv.key, label=updated_kv.label)
        assert (
            to_update_kv.key == updated_kv.key
            and to_update_kv.label == updated_kv.label
            and "updated_value" == updated_kv.value
            and to_update_kv.content_type == updated_kv.content_type
            and tags == updated_kv.tags
            and to_update_kv.etag != updated_kv.etag
        )

    def test_update_existing_configuration_setting_label_noetag(
        self
    ):
        sample_kv = copy(self.test_data.label1_data[-1])

        # create a new key value into AzConfig service
        sample_kv.key = "unit_test_key_" + self.test_data.key_uuid
        to_update_kv = self.app_config_client.add_configuration_setting(sample_kv)
        tags = {"a": "b", "c": "d"}
        updated_kv = self.app_config_client.update_configuration_setting(
            to_update_kv.key, label=to_update_kv.label, value="updated_value", tags=tags
        )
        # remove the new key value from the service
        self.app_config_client.delete_configuration_setting(updated_kv.key, label=updated_kv.label)
        assert (
            to_update_kv.key == updated_kv.key
            and to_update_kv.label == updated_kv.label
            and "updated_value" == updated_kv.value
            and to_update_kv.content_type == updated_kv.content_type
            and tags == updated_kv.tags
            and to_update_kv.etag != updated_kv.etag
        )

    def test_update_existing_configuration_setting_label_wrong_etag(
        self
    ):
        sample_kv = copy(self.test_data.label1_data[-1])

        # create a new key value into AzConfig service
        sample_kv.key = "unit_test_key_" + self.test_data.key_uuid
        to_update_kv = self.app_config_client.add_configuration_setting(sample_kv)
        tags = {"a": "b", "c": "d"}
        etag = "wrong etag"
        with pytest.raises(CloudError):
            self.app_config_client.update_configuration_setting(
                to_update_kv.key,
                label=to_update_kv.label,
                value="updated_value",
                tags=tags,
                etag=etag,
            )
        self.app_config_client.delete_configuration_setting(to_update_kv.key, label=to_update_kv.label)

    def test_update_no_existing_configuration_setting_label_noetag(
        self
    ):
        key = self.test_data.key_uuid
        label = "test_label1"
        with pytest.raises(CloudError):
            self.app_config_client.update_configuration_setting(key, label=label, value="some value")

    # method: get_configuration_setting
    def test_get_configuration_setting_no_label(self):
        compare_kv = self.test_data.no_label_data[0]
        fetched_kv = self.app_config_client.get_configuration_setting(compare_kv.key)
        assert (
            fetched_kv.key == compare_kv.key
            and fetched_kv.value == compare_kv.value
            and fetched_kv.content_type == compare_kv.content_type
            and fetched_kv.tags == compare_kv.tags
        )
        assert fetched_kv.label is None

    def test_get_configuration_setting_label(self):
        compare_kv = self.test_data.label1_data[0]
        fetched_kv = self.app_config_client.get_configuration_setting(compare_kv.key, compare_kv.label)
        assert (
            fetched_kv.key == compare_kv.key
            and fetched_kv.value == compare_kv.value
            and fetched_kv.content_type == compare_kv.content_type
            and fetched_kv.tags == compare_kv.tags
        )
        assert fetched_kv.label is not None

    def test_get_non_existing_configuration_setting(self):
        compare_kv = self.test_data.label1_data[0]
        with pytest.raises(CloudError):
            self.app_config_client.get_configuration_setting(compare_kv.key, compare_kv.label + "a")

    # method: lock_configuration_setting and unlock_configuration_setting
    def test_lock_unlock_no_label(self):
        # lock, assert locked, then unlock and assert locked
        to_lock_kv = self.test_data.no_label_data[0]
        locked_kv = self.app_config_client.lock_configuration_setting(to_lock_kv.key)
        assert locked_kv.locked is True
        unlocked_kv = self.app_config_client.unlock_configuration_setting(to_lock_kv.key)
        assert unlocked_kv.locked is False

    def test_lock_unlock_with_label(self):
        # lock, assert locked, then unlock and assert locked
        to_lock_kv = self.test_data.label1_data[0]
        locked_kv = self.app_config_client.lock_configuration_setting(to_lock_kv.key, to_lock_kv.label)
        assert locked_kv.locked is True
        unlocked_kv = self.app_config_client.unlock_configuration_setting(to_lock_kv.key, to_lock_kv.label)
        assert unlocked_kv.locked is False

    def test_lock_no_existing(self):
        to_lock_kv = self.test_data.label1_data[0]
        with pytest.raises(CloudError):
            self.app_config_client.lock_configuration_setting(to_lock_kv.key, to_lock_kv.label + "a")

    def test_unlock_no_existing(self):
        to_lock_kv = self.test_data.label1_data[0]
        with pytest.raises(CloudError):
            self.app_config_client.unlock_configuration_setting(to_lock_kv.key, to_lock_kv.label + "a")

    # method: delete_configuration_setting
    def test_delete_with_key_no_label(self):
        to_delete_kv = copy(self.test_data.no_label_data[-1])
        to_delete_kv.key = "unit_test_key_" + self.test_data.key_uuid
        to_delete_kv = self.app_config_client.add_configuration_setting(to_delete_kv)
        self.app_config_client.delete_configuration_setting(to_delete_kv.key)
        with pytest.raises(CloudError):
            self.app_config_client.get_configuration_setting(to_delete_kv.key)

    def test_delete_with_key_label(self):
        to_delete_kv = copy(self.test_data.label1_data[-1])
        to_delete_kv.key = "unit_test_key_" + self.test_data.key_uuid
        to_delete_kv = self.app_config_client.add_configuration_setting(to_delete_kv)
        self.app_config_client.delete_configuration_setting(to_delete_kv.key, label=to_delete_kv.label)
        with pytest.raises(CloudError):
            self.app_config_client.get_configuration_setting(to_delete_kv.key, label=to_delete_kv.label)

    def test_delete_non_existing(self):
        deleted_kv = self.app_config_client.delete_configuration_setting("not_exist_" + self.test_data.key_uuid)
        assert deleted_kv is None

    def test_delete_correct_etag(self):
        to_delete_kv = copy(self.test_data.no_label_data[-1])
        to_delete_kv.key = "unit_test_key_" + self.test_data.key_uuid
        to_delete_kv = self.app_config_client.add_configuration_setting(to_delete_kv)
        deleted_kv = self.app_config_client.delete_configuration_setting(
            to_delete_kv.key, etag=to_delete_kv.etag
        )
        assert deleted_kv is not None
        with pytest.raises(CloudError):
            self.app_config_client.get_configuration_setting(to_delete_kv.key)

    def test_delete_wrong_etag(self):
        to_delete_kv = copy(self.test_data.no_label_data[-1])
        to_delete_kv.key = "unit_test_key_" + self.test_data.key_uuid
        to_delete_kv = self.app_config_client.add_configuration_setting(to_delete_kv)
        with pytest.raises(CloudError):
            self.app_config_client.delete_configuration_setting(to_delete_kv.key, etag="wrong etag")
        self.app_config_client.delete_configuration_setting(to_delete_kv.key)

    # method: list_configuration_settings
    def test_list_configuration_settings_key_label(self):
        to_list1 = self.test_data.label1_data[0]
        to_list2 = self.test_data.label2_data[0]
        items = self.app_config_client.list_configuration_settings(
            labels=[to_list1.label, to_list2.label], keys=[to_list1.key, to_list2.key]
        )
        cnt = 0
        for kv in items:
            assert kv.key in [to_list1.key, to_list2.key] and kv.label in [
                to_list1.label,
                to_list2.label,
            ]
            cnt += 1
        assert cnt == 2

    def test_list_configuration_settings_only_label(self):
        items = self.app_config_client.list_configuration_settings(labels=[self.test_data.label1])
        cnt = 0
        for kv in items:
            assert kv.label == self.test_data.label1
            cnt += 1
        assert cnt == 1

    def test_list_configuration_settings_only_key(self):
        to_list1 = self.test_data.no_label_data[0]
        items = self.app_config_client.list_configuration_settings(keys=[to_list1.key])
        cnt = 0
        for kv in items:
            assert kv.key == to_list1.key
            cnt += 1
        assert cnt >= 1

    def test_list_configuration_settings_fields(self):
        items = self.app_config_client.list_configuration_settings(
            keys=["*"], labels=[self.test_data.label1], fields=["key", "content_type"]
        )
        cnt = 0
        for kv in items:
            assert kv.key is not None and kv.label is None and kv.content_type is not None
            cnt += 1
        assert cnt == 1

    def test_list_configuration_settings_reserved_chars(self):
        items = self.app_config_client.list_configuration_settings(
            keys=None, labels=[self.test_data.label2]
        )
        cnt = 0
        for kv in items:
            assert kv.label == self.test_data.label2
            cnt += 1
        assert cnt == 1

    def test_list_configuration_settings_contains(self):
        items = self.app_config_client.list_configuration_settings(
            keys=None, labels=["*"+self.test_data.label2+"*"]
        )
        cnt = 0
        for kv in items:
            assert kv.label == self.test_data.label2
            cnt += 1
        assert cnt == 1

    def test_list_configuration_settings_correct_etag(self):
        to_list_kv = self.test_data.label1_data[0]
        custom_headers = {"If-Match": to_list_kv.etag}
        items = self.app_config_client.list_configuration_settings(
            keys=[to_list_kv.key], labels=[to_list_kv.label], headers=custom_headers
        )
        cnt = 0
        for kv in items:
            assert kv.key == to_list_kv.key and kv.label == to_list_kv.label
            cnt += 1
        assert cnt == 1

    def test_list_configuration_settings_multi_pages(self):
        # create PAGE_SIZE+1 configuration settings to have at least two pages
        delete_me = [
            self.app_config_client.add_configuration_setting(ConfigurationSetting(
                key="multi_" + str(i) + self.test_data.key_uuid,
                label="multi_label_" + str(i),
                value="multi value"
            )) for i in range(PAGE_SIZE + 1)
        ]
        items = self.app_config_client.list_configuration_settings(keys=["multi_*"])
        assert len(list(items)) > PAGE_SIZE

        # Remove the delete_me
        for kv in delete_me:
            self._delete_from_test(kv.key, kv.label)

    def test_list_configuration_settings_null_label(self):
        items = self.app_config_client.list_configuration_settings(
            keys=None,
            labels=[""]
        )
        assert len(list(items)) > 0

    def test_list_configuration_settings_only_accept_time(self):
        exclude_today = self.app_config_client.list_configuration_settings(
            accept_date_time=datetime.datetime.today() + datetime.timedelta(days=-1)
        )
        all_inclusive = self.app_config_client.list_configuration_settings()
        assert len(list(all_inclusive)) > len(list(exclude_today))

    # method: list_revisions
    def test_list_revisions_key_label(self):
        to_list1 = self.test_data.label1_data[0]
        to_list2 = self.test_data.label2_data[0]
        items = self.app_config_client.list_revisions(
            labels=[to_list1.label, to_list2.label], keys=[to_list1.key, to_list2.key]
        )
        cnt = 0
        for kv in items:
            assert kv.key in [to_list1.key, to_list2.key] and kv.label in [
                to_list1.label,
                to_list2.label,
            ]
            cnt += 1
        assert cnt >= 2

    def test_list_revisions_only_label(self):
        items = self.app_config_client.list_revisions(labels=[self.test_data.label1])
        cnt = 0
        for kv in items:
            assert kv.label == self.test_data.label1
            cnt += 1
        assert cnt >= 1

    def test_list_revisions_key_no_label(self):
        to_list1 = self.test_data.no_label_data[0]
        items = self.app_config_client.list_revisions(keys=[to_list1.key])
        cnt = 0
        for kv in items:
            assert kv.key == to_list1.key
            cnt += 1
        assert cnt >= 1

    def test_list_revisions_fields(self):
        items = self.app_config_client.list_revisions(
            keys=["*"], labels=[self.test_data.label1], fields=["key", "content_type"]
        )
        for kv in items:
            assert (
                kv.key is not None
                and kv.label is None
                and kv.content_type is not None
                and not kv.tags
                and not kv.etag
            )

    def test_list_revisions_correct_etag(self):
        to_list_kv = self.test_data.label1_data[0]
        custom_headers = {"If-Match": to_list_kv.etag}
        items = self.app_config_client.list_revisions(
            keys=[to_list_kv.key], labels=[to_list_kv.label], headers=custom_headers
        )
        cnt = 0
        for kv in items:
            assert kv.key == to_list_kv.key and kv.label == to_list_kv.label
            cnt += 1
        assert cnt > 0
