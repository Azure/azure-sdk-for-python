# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import copy
import datetime
import json
import re
import copy
from azure.core import MatchConditions
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
    FILTER_PERCENTAGE,
    FILTER_TARGETING,
    FILTER_TIME_WINDOW,
)
from azure.appconfiguration.aio import AzureAppConfigurationClient
from asynctestcase import AsyncAppConfigTestCase
from consts import (
    KEY,
    LABEL,
    TEST_VALUE,
    TEST_CONTENT_TYPE,
    LABEL_RESERVED_CHARS,
    PAGE_SIZE,
    KEY_UUID,
)
from devtools_testutils.aio import recorded_by_proxy_async
from async_preparers import app_config_decorator_async
from typing import Any
from uuid import uuid4


class TestAppConfigurationClientAsync(AsyncAppConfigTestCase):
    # method: add_configuration_setting
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_add_configuration_setting(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            kv = ConfigurationSetting(
                key=KEY + "_ADD",
                label=LABEL,
                value=TEST_VALUE,
                content_type=TEST_CONTENT_TYPE,
                tags={"tag1": "tag1", "tag2": "tag2"},
            )
            created_kv = await client.add_configuration_setting(kv)
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
            await client.delete_configuration_setting(key=created_kv.key, label=created_kv.label)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_add_existing_configuration_setting(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            test_config_setting = self.create_config_setting()
            await self.add_for_test(client, test_config_setting)
            with pytest.raises(ResourceExistsError):
                await client.add_configuration_setting(
                    ConfigurationSetting(
                        key=test_config_setting.key,
                        label=test_config_setting.label,
                    )
                )
            await client.delete_configuration_setting(key=test_config_setting.key, label=test_config_setting.label)

    # method: set_configuration_setting
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_set_existing_configuration_setting_label_etag(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            to_set_kv = self.create_config_setting()
            to_set_kv.value = to_set_kv.value + "a"
            to_set_kv.tags = {"a": "b", "c": "d"}
            set_kv = await client.set_configuration_setting(to_set_kv)
            assert (
                to_set_kv.key == set_kv.key
                and to_set_kv.label == to_set_kv.label
                and to_set_kv.value == set_kv.value
                and to_set_kv.content_type == set_kv.content_type
                and to_set_kv.tags == set_kv.tags
                and to_set_kv.etag != set_kv.etag
            )
            await client.delete_configuration_setting(key=to_set_kv.key, label=to_set_kv.label)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_set_existing_configuration_setting_label_wrong_etag(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            to_set_kv = self.create_config_setting()
            to_set_kv.value = to_set_kv.value + "a"
            to_set_kv.tags = {"a": "b", "c": "d"}
            to_set_kv.etag = "wrong etag"
            with pytest.raises(ResourceModifiedError):
                await client.set_configuration_setting(to_set_kv, match_condition=MatchConditions.IfNotModified)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_set_configuration_setting_etag(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            kv = ConfigurationSetting(
                key=KEY + "_SET",
                label=LABEL,
                value=TEST_VALUE,
                content_type=TEST_CONTENT_TYPE,
                tags={"tag1": "tag1", "tag2": "tag2"},
            )
            kv.etag = "random etag"
            with pytest.raises(ResourceModifiedError):
                await client.set_configuration_setting(kv, match_condition=MatchConditions.IfNotModified)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_set_configuration_setting_no_etag(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            to_set_kv = ConfigurationSetting(
                key=KEY + "_SET",
                label=LABEL,
                value=TEST_VALUE,
                content_type=TEST_CONTENT_TYPE,
                tags={"tag1": "tag1", "tag2": "tag2"},
            )
            set_kv = await client.set_configuration_setting(to_set_kv)
            assert (
                to_set_kv.key == set_kv.key
                and to_set_kv.label == set_kv.label
                and to_set_kv.value == set_kv.value
                and to_set_kv.content_type == set_kv.content_type
                and to_set_kv.tags == set_kv.tags
                and to_set_kv.etag != set_kv.etag
            )
            await client.delete_configuration_setting(key=to_set_kv.key, label=to_set_kv.label)

    # method: get_configuration_setting
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_get_configuration_setting_no_label(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            compare_kv = self.create_config_setting_no_label()
            await self.add_for_test(client, compare_kv)
            fetched_kv = await client.get_configuration_setting(compare_kv.key)
            assert (
                fetched_kv.key == compare_kv.key
                and fetched_kv.value == compare_kv.value
                and fetched_kv.content_type == compare_kv.content_type
                and fetched_kv.tags == compare_kv.tags
            )
            assert fetched_kv.label is None
            await client.delete_configuration_setting(key=compare_kv.key, label=compare_kv.label)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_get_configuration_setting_label(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            compare_kv = self.create_config_setting()
            await self.add_for_test(client, compare_kv)
            fetched_kv = await client.get_configuration_setting(
                compare_kv.key, compare_kv.label
            )
            assert (
                fetched_kv.key == compare_kv.key
                and fetched_kv.value == compare_kv.value
                and fetched_kv.content_type == compare_kv.content_type
                and fetched_kv.tags == compare_kv.tags
            )
            assert fetched_kv.label is not None
            await client.delete_configuration_setting(key=compare_kv.key, label=compare_kv.label)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_get_non_existing_configuration_setting(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            compare_kv = self.create_config_setting()
            await self.add_for_test(client, compare_kv)
            with pytest.raises(ResourceNotFoundError):
                await client.get_configuration_setting(
                    compare_kv.key, compare_kv.label + "a"
                )
            await client.delete_configuration_setting(key=compare_kv.key, label=compare_kv.label)

    # method: delete_configuration_setting
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_delete_with_key_no_label(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            to_delete_kv = self.create_config_setting_no_label()
            await self.add_for_test(client, to_delete_kv)
            deleted_kv = await client.delete_configuration_setting(key=to_delete_kv.key, label=to_delete_kv.label)
            assert deleted_kv is not None
            with pytest.raises(ResourceNotFoundError):
                await client.get_configuration_setting(to_delete_kv.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_delete_with_key_label(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            to_delete_kv = self.create_config_setting()
            await self.add_for_test(client, to_delete_kv)
            deleted_kv = await client.delete_configuration_setting(key=to_delete_kv.key, label=to_delete_kv.label)
            assert deleted_kv is not None
            with pytest.raises(ResourceNotFoundError):
                await client.get_configuration_setting(to_delete_kv.key, label=to_delete_kv.label)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_delete_not_existing(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            deleted_kv = await client.delete_configuration_setting("not_exist_" + KEY)
            assert deleted_kv is None

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_delete_correct_etag(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            to_delete_kv = self.create_config_setting_no_label()
            await self.add_for_test(client, to_delete_kv)
            deleted_kv = await client.delete_configuration_setting(to_delete_kv.key, etag=to_delete_kv.etag)
            assert deleted_kv is not None
            with pytest.raises(ResourceNotFoundError):
                await client.get_configuration_setting(to_delete_kv.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_delete_wrong_etag(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            to_delete_kv = self.create_config_setting_no_label()
            await self.add_for_test(client, to_delete_kv)
            with pytest.raises(ResourceModifiedError):
                await client.delete_configuration_setting(
                    to_delete_kv.key, etag="wrong etag", match_condition=MatchConditions.IfNotModified
                )
            await client.delete_configuration_setting(key=to_delete_kv.key, label=to_delete_kv.label)

    # method: list_configuration_settings
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_configuration_settings_key_label(self, appconfiguration_connection_string):
        await self.set_up(appconfiguration_connection_string)
        items = await self.convert_to_list(self.client.list_configuration_settings(label_filter=LABEL, key_filter=KEY))
        assert len(items) == 1
        assert all(x.key == KEY and x.label == LABEL for x in items)
        await self.tear_down()

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_configuration_settings_only_label(self, appconfiguration_connection_string):
        await self.set_up(appconfiguration_connection_string)
        items = await self.convert_to_list(self.client.list_configuration_settings(label_filter=LABEL))
        assert len(items) == 1
        assert all(x.label == LABEL for x in items)
        await self.tear_down()

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_configuration_settings_only_key(self, appconfiguration_connection_string):
        await self.set_up(appconfiguration_connection_string)
        items = await self.convert_to_list(self.client.list_configuration_settings(key_filter=KEY))
        assert len(items) == 2
        assert all(x.key == KEY for x in items)
        await self.tear_down()

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_configuration_settings_fields(self, appconfiguration_connection_string):
        await self.set_up(appconfiguration_connection_string)
        items = await self.convert_to_list(self.client.list_configuration_settings(
            key_filter="*", label_filter=LABEL, fields=["key", "content_type"]
        ))
        assert len(items) == 1
        assert all(x.key and not x.label and x.content_type for x in items)
        await self.tear_down()

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_configuration_settings_reserved_chars(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            reserved_char_kv = ConfigurationSetting(key=KEY, label=LABEL_RESERVED_CHARS, value=TEST_VALUE)
            reserved_char_kv = await client.add_configuration_setting(reserved_char_kv)
            escaped_label = re.sub(r"((?!^)\*(?!$)|\\|,)", r"\\\1", LABEL_RESERVED_CHARS)
            items = await self.convert_to_list(client.list_configuration_settings(label_filter=escaped_label))
            assert len(items) == 1
            assert all(x.label == LABEL_RESERVED_CHARS for x in items)
            await client.delete_configuration_setting(reserved_char_kv.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_configuration_settings_contains(self, appconfiguration_connection_string):
        await self.set_up(appconfiguration_connection_string)
        items = await self.convert_to_list(self.client.list_configuration_settings(label_filter=LABEL + "*"))
        assert len(items) == 1
        assert all(x.label == LABEL for x in items)
        await self.tear_down()

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_configuration_settings_correct_etag(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            to_list_kv = self.create_config_setting()
            await self.add_for_test(client, to_list_kv)
            custom_headers = {"If-Match": to_list_kv.etag or ""}
            items = await self.convert_to_list(client.list_configuration_settings(
                key_filter=to_list_kv.key, label_filter=to_list_kv.label, headers=custom_headers
            ))
            assert len(items) == 1
            assert all(x.key == to_list_kv.key and x.label == to_list_kv.label for x in items)
            await client.delete_configuration_setting(to_list_kv.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_configuration_settings_multi_pages(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            # create PAGE_SIZE+1 configuration settings to have at least two pages
            try:
                [
                    await client.add_configuration_setting(
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
            items = await self.convert_to_list(client.list_configuration_settings(key_filter="multi_*"))
            assert len(items) > PAGE_SIZE

            # Remove the configuration settings
            try:
                [
                    await client.delete_configuration_setting(
                        key="multi_" + str(i) + KEY_UUID, label="multi_label_" + str(i)
                    )
                    for i in range(PAGE_SIZE + 1)
                ]
            except AzureError:
                pass

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_configuration_settings_no_label(self, appconfiguration_connection_string):
        await self.set_up(appconfiguration_connection_string)
        items = await self.convert_to_list(self.client.list_configuration_settings(label_filter="\0"))
        assert len(items) > 0
        await self.tear_down()

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_configuration_settings_only_accepttime(self, appconfiguration_connection_string, **kwargs):
        recorded_variables = kwargs.pop("variables", {})
        await self.set_up(appconfiguration_connection_string)
        exclude_today = await self.convert_to_list(self.client.list_configuration_settings(
            accept_datetime=recorded_variables.setdefault(
                "datetime", str(datetime.datetime.today() + datetime.timedelta(days=-1))
            )
        ))
        all_inclusive = await self.convert_to_list(self.client.list_configuration_settings())
        assert len(all_inclusive) > len(exclude_today)
        await self.tear_down()
        return recorded_variables

    # method: list_revisions
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_revisions_key_label(self, appconfiguration_connection_string):
        await self.set_up(appconfiguration_connection_string)
        to_list1 = self.create_config_setting()
        items = await self.convert_to_list(self.client.list_revisions(
            label_filter=to_list1.label, key_filter=to_list1.key
        ))
        assert len(items) >= 2
        assert all(x.key == to_list1.key and x.label == to_list1.label for x in items)
        await self.tear_down()

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_revisions_only_label(self, appconfiguration_connection_string):
        await self.set_up(appconfiguration_connection_string)
        items = await self.convert_to_list(self.client.list_revisions(label_filter=LABEL))
        assert len(items) >= 1
        assert all(x.label == LABEL for x in items)
        await self.tear_down()

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_revisions_key_no_label(self, appconfiguration_connection_string):
        await self.set_up(appconfiguration_connection_string)
        items = await self.convert_to_list(self.client.list_revisions(key_filter=KEY))
        assert len(items) >= 1
        assert all(x.key == KEY for x in items)
        await self.tear_down()

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_revisions_fields(self, appconfiguration_connection_string):
        await self.set_up(appconfiguration_connection_string)
        items = await self.convert_to_list(self.client.list_revisions(
            key_filter="*", label_filter=LABEL, fields=["key", "content_type"]
        ))
        assert all(x.key and not x.label and x.content_type and not x.tags and not x.etag for x in items)
        await self.tear_down()

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_list_revisions_correct_etag(self, appconfiguration_connection_string):
        await self.set_up(appconfiguration_connection_string)
        to_list_kv = self.create_config_setting()
        custom_headers = {"If-Match": to_list_kv.etag or ""}
        items = await self.convert_to_list(self.client.list_revisions(
            key_filter=to_list_kv.key, label_filter=to_list_kv.label, headers=custom_headers
        ))
        assert len(items) >= 1
        assert all(x.key == to_list_kv.key and x.label == to_list_kv.label for x in items)
        await self.tear_down()

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_read_only(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            kv = self.create_config_setting_no_label()
            await self.add_for_test(client, kv)
            read_only_kv = await client.set_read_only(kv)
            assert read_only_kv.read_only
            readable_kv = await client.set_read_only(read_only_kv, False)
            assert not readable_kv.read_only
            await client.delete_configuration_setting(kv.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_delete_read_only(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            to_delete_kv = self.create_config_setting_no_label()
            await self.add_for_test(client, to_delete_kv)
            read_only_kv = await client.set_read_only(to_delete_kv)
            with pytest.raises(ResourceReadOnlyError):
                await client.delete_configuration_setting(to_delete_kv.key)
            await client.set_read_only(read_only_kv, False)
            await client.delete_configuration_setting(to_delete_kv.key)
            with pytest.raises(ResourceNotFoundError):
                await client.get_configuration_setting(to_delete_kv.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_set_read_only(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            to_set_kv = self.create_config_setting_no_label()
            await self.add_for_test(client, to_set_kv)
            to_set_kv.value = to_set_kv.value + "a"
            to_set_kv.tags = {"a": "b", "c": "d"}
            read_only_kv = await client.set_read_only(to_set_kv)
            with pytest.raises(ResourceReadOnlyError):
                await client.set_configuration_setting(read_only_kv)
            readable_kv = await client.set_read_only(read_only_kv, False)
            readable_kv.value = to_set_kv.value
            readable_kv.tags = to_set_kv.tags
            set_kv = await client.set_configuration_setting(readable_kv)
            assert (
                    to_set_kv.key == set_kv.key
                    and to_set_kv.label == to_set_kv.label
                    and to_set_kv.value == set_kv.value
                    and to_set_kv.content_type == set_kv.content_type
                    and to_set_kv.tags == set_kv.tags
                    and to_set_kv.etag != set_kv.etag
            )
            set_kv.etag = "bad"
            with pytest.raises(ResourceModifiedError):
                await client.set_read_only(set_kv, True, match_condition=MatchConditions.IfNotModified)
            await client.delete_configuration_setting(to_set_kv.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_sync_tokens_with_configuration_setting(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            sync_tokens = copy.deepcopy(client._sync_token_policy._sync_tokens)
            sync_token_header = self._order_dict(sync_tokens)
            sync_token_header = ",".join(str(x) for x in sync_token_header.values())

            new = ConfigurationSetting(
                    key="KEY1",
                    label=None,
                    value="TEST_VALUE1",
                    content_type=TEST_CONTENT_TYPE,
                    tags={"tag1": "tag1", "tag2": "tag2"},
            )

            await client.set_configuration_setting(new)
            sync_tokens2 = copy.deepcopy(client._sync_token_policy._sync_tokens)
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

            await client.set_configuration_setting(new)
            sync_tokens3 = copy.deepcopy(client._sync_token_policy._sync_tokens)
            sync_token_header3 = self._order_dict(sync_tokens3)
            sync_token_header3 = ",".join(str(x) for x in sync_token_header3.values())
            assert sync_token_header2 != sync_token_header3

            await client.delete_configuration_setting(new.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_sync_tokens_with_feature_flag_configuration_setting(self, appconfiguration_connection_string):
        await self.set_up(appconfiguration_connection_string)
        new = FeatureFlagConfigurationSetting(
            'custom',
            enabled=True,
            filters = [
                {
                    "name": "Microsoft.Percentage",
                    "parameters": {
                        "Value": 10,
                        "User": "user1",
                    }
                }
            ]
        )

        sync_tokens = copy.deepcopy(self.client._sync_token_policy._sync_tokens)
        keys = list(sync_tokens.keys())
        seq_num = sync_tokens[keys[0]].sequence_number
        await self.client.set_configuration_setting(new)

        new = FeatureFlagConfigurationSetting(
            'time_window',
            enabled=True,
            filters = [
                {
                    u"name": FILTER_TIME_WINDOW,
                    u"parameters": {
                        "Start": "Wed, 10 Mar 2021 05:00:00 GMT",
                        "End": "Fri, 02 Apr 2021 04:00:00 GMT"
                    }
                },
            ]
        )

        await self.client.set_configuration_setting(new)
        sync_tokens2 = copy.deepcopy(self.client._sync_token_policy._sync_tokens)
        keys = list(sync_tokens2.keys())
        seq_num2 = sync_tokens2[keys[0]].sequence_number

        new = FeatureFlagConfigurationSetting(
            "newflag",
            enabled=True,
            filters=[
                {
                    "name": FILTER_TARGETING,
                    "parameters": {
                        u"Audience": {
                            u"Users": [u"abc", u"def"],
                            u"Groups": [u"ghi", u"jkl"],
                            u"DefaultRolloutPercentage": 75
                        }
                    }
                },
            ]
        )

        await self.client.set_configuration_setting(new)
        sync_tokens3 = copy.deepcopy(self.client._sync_token_policy._sync_tokens)
        keys = list(sync_tokens3.keys())
        seq_num3 = sync_tokens3[keys[0]].sequence_number

        assert seq_num < seq_num2
        assert seq_num2 < seq_num3

        await self.client.delete_configuration_setting(new.key)
        await self.client.close()

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_config_setting_feature_flag(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            feature_flag = FeatureFlagConfigurationSetting("test_feature", enabled=True)
            set_flag = await client.set_configuration_setting(feature_flag)

            self._assert_same_keys(feature_flag, set_flag)

            set_flag.enabled = not set_flag.enabled
            changed_flag = await client.set_configuration_setting(set_flag)

            changed_flag.enabled = False
            temp = json.loads(changed_flag.value)
            assert temp['enabled'] == False

            c = json.loads(copy.deepcopy(changed_flag.value))
            c['enabled'] = True
            changed_flag.value = json.dumps(c)
            assert changed_flag.enabled == True

            changed_flag.value = json.dumps({})
            assert changed_flag.enabled == None
            assert changed_flag.value == json.dumps({'enabled': None, "conditions": {"client_filters": None}})

            set_flag.value = "bad_value"
            assert set_flag.enabled == None
            assert set_flag.filters == None

            await client.delete_configuration_setting(changed_flag.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_config_setting_secret_reference(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            secret_reference = SecretReferenceConfigurationSetting(
                "ConnectionString", "https://test-test.vault.azure.net/secrets/connectionString")
            set_flag = await client.set_configuration_setting(secret_reference)
            self._assert_same_keys(secret_reference, set_flag)

            set_flag.secret_id = "https://test-test.vault.azure.net/new_secrets/connectionString"
            updated_flag = await client.set_configuration_setting(set_flag)
            self._assert_same_keys(set_flag, updated_flag)

            assert isinstance(updated_flag, SecretReferenceConfigurationSetting)
            new_uri = "https://aka.ms/azsdk"
            new_uri2 = "https://aka.ms/azsdk/python"
            updated_flag.secret_id = new_uri
            temp = json.loads(updated_flag.value)
            assert temp['uri'] == new_uri

            updated_flag.value = json.dumps({'uri': new_uri2})
            assert updated_flag.secret_id == new_uri2

            set_flag.value = "bad_value"
            assert set_flag.secret_id == None

            await client.delete_configuration_setting(secret_reference.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_feature_filter_targeting(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            new = FeatureFlagConfigurationSetting(
                "newflag",
                enabled=True,
                filters=[
                    {
                        "name": FILTER_TARGETING,
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

            sent_config = await client.set_configuration_setting(new)
            self._assert_same_keys(sent_config, new)

            assert isinstance(sent_config.filters[0], dict)
            assert len(sent_config.filters) == 1

            sent_config.filters[0]["parameters"]["Audience"]["DefaultRolloutPercentage"] = 80
            updated_sent_config = await client.set_configuration_setting(sent_config)
            self._assert_same_keys(sent_config, updated_sent_config)

            updated_sent_config.filters.append(
                {
                    "name": FILTER_TARGETING,
                    "parameters": {
                        u"Audience": {
                            u"Users": [u"abcd", u"defg"], # cspell:disable-line
                            u"Groups": [u"ghij", u"jklm"], # cspell:disable-line
                            u"DefaultRolloutPercentage": 50
                        }
                    }
                }
            )
            updated_sent_config.filters.append(
                {
                    "name": FILTER_TARGETING,
                    "parameters": {
                        u"Audience": {
                            u"Users": [u"abcde", u"defgh"], # cspell:disable-line
                            u"Groups": [u"ghijk", u"jklmn"], # cspell:disable-line
                            u"DefaultRolloutPercentage": 100
                        }
                    }
                }
            )
            sent_config = await client.set_configuration_setting(updated_sent_config)
            self._assert_same_keys(sent_config, updated_sent_config)
            assert len(sent_config.filters) == 3

            await client.delete_configuration_setting(updated_sent_config.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_feature_filter_time_window(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            new = FeatureFlagConfigurationSetting(
                'time_window',
                enabled=True,
                filters=[
                    {
                        "name": FILTER_TIME_WINDOW,
                        "parameters": {
                            "Start": "Wed, 10 Mar 2021 05:00:00 GMT",
                            "End": "Fri, 02 Apr 2021 04:00:00 GMT"
                        }
                    }
                ]
            )

            sent = await client.set_configuration_setting(new)
            self._assert_same_keys(sent, new)

            sent.filters[0]["parameters"]["Start"] = "Thurs, 11 Mar 2021 05:00:00 GMT"
            new_sent = await client.set_configuration_setting(sent)
            self._assert_same_keys(sent, new_sent)

            await client.delete_configuration_setting(new_sent.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_feature_filter_custom(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            new = FeatureFlagConfigurationSetting(
                'custom',
                enabled=True,
                filters=[
                    {
                        "name": FILTER_PERCENTAGE,
                        "parameters": {
                            "Value": 10,
                            "User": "user1"
                        }
                    }
                ]
            )

            sent = await client.set_configuration_setting(new)
            self._assert_same_keys(sent, new)

            sent.filters[0]["parameters"]["Value"] = 100
            new_sent = await client.set_configuration_setting(sent)
            self._assert_same_keys(sent, new_sent)

            await client.delete_configuration_setting(new_sent.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_feature_filter_multiple(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            new = FeatureFlagConfigurationSetting(
                'custom',
                enabled=True,
                filters=[
                    {
                        "name": FILTER_PERCENTAGE,
                        "parameters": {
                            "Value": 10
                        }
                    },
                    {
                        "name": FILTER_TIME_WINDOW,
                        "parameters": {
                            "Start": "Wed, 10 Mar 2021 05:00:00 GMT",
                            "End": "Fri, 02 Apr 2021 04:00:00 GMT"
                        }
                    },
                    {
                        "name": FILTER_TARGETING,
                        "parameters": {
                            u"Audience": {
                                u"Users": [u"abcde", u"defgh"], # cspell:disable-line
                                u"Groups": [u"ghijk", u"jklmn"], # cspell:disable-line
                                u"DefaultRolloutPercentage": 100
                            }
                        }
                    }
                ]
            )

            sent = await client.set_configuration_setting(new)
            self._assert_same_keys(sent, new)

            sent.filters[0]["parameters"]["Value"] = 100
            sent.filters[1]["parameters"]["Start"] = "Wed, 10 Mar 2021 08:00:00 GMT"
            sent.filters[2]["parameters"]["Audience"]["DefaultRolloutPercentage"] = 100

            new_sent = await client.set_configuration_setting(sent)
            self._assert_same_keys(sent, new_sent)

            assert new_sent.filters[0]["parameters"]["Value"] == 100
            assert new_sent.filters[1]["parameters"]["Start"] == "Wed, 10 Mar 2021 08:00:00 GMT"
            assert new_sent.filters[2]["parameters"]["Audience"]["DefaultRolloutPercentage"] == 100

            await client.delete_configuration_setting(new_sent.key)
    
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_breaking_with_feature_flag_configuration_setting(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            new = FeatureFlagConfigurationSetting(
                'breaking1',
                enabled=True,
                filters=[
                    {
                        "name": FILTER_TIME_WINDOW,
                        "parameters": {
                            "Start": "bababooey, 31 Mar 2021 25:00:00 GMT", # cspell:disable-line
                            "End": "Fri, 02 Apr 2021 04:00:00 GMT"
                        }
                    },
                ]
            )
            await client.set_configuration_setting(new)
            await client.get_configuration_setting(new.key)

            new = FeatureFlagConfigurationSetting(
                'breaking2',
                enabled=True,
                filters=[
                    {
                        "name": FILTER_TIME_WINDOW,
                        "parameters": {
                            "Start": "bababooey, 31 Mar 2021 25:00:00 GMT", # cspell:disable-line
                            "End": "not even trying to be a date"
                        }
                    },
                ]
            )
            await client.set_configuration_setting(new)
            await client.get_configuration_setting(new.key)

            # This will show up as a Custom filter
            new = FeatureFlagConfigurationSetting(
                'breaking3',
                enabled=True,
                filters=[
                    {
                        "name": FILTER_TIME_WINDOW,
                        "parameters": {
                            "Start": "bababooey, 31 Mar 2021 25:00:00 GMT", # cspell:disable-line
                            "End": "not even trying to be a date"
                        }
                    },
                ]
            )
            await client.set_configuration_setting(new)
            await client.get_configuration_setting(new.key)

            new = FeatureFlagConfigurationSetting(
                'breaking4',
                enabled=True,
                filters=[
                    {
                        "name": FILTER_TIME_WINDOW,
                        "parameters": "stringystring"
                    },
                ]
            )
            await client.set_configuration_setting(new)
            await client.get_configuration_setting(new.key)

            new = FeatureFlagConfigurationSetting(
                'breaking5',
                enabled=True,
                filters=[
                    {
                        "name": FILTER_TARGETING,
                        "parameters": {
                            u"Audience": {
                                u"Users": '123'
                            }
                        }
                    }
                ]
            )
            await client.set_configuration_setting(new)
            await client.get_configuration_setting(new.key)

            new = FeatureFlagConfigurationSetting(
                'breaking6',
                enabled=True,
                filters=[
                    {
                        "name": FILTER_TARGETING,
                        "parameters": "invalidformat"
                    }
                ]
            )
            await client.set_configuration_setting(new)
            await client.get_configuration_setting(new.key)

            new = FeatureFlagConfigurationSetting(
                'breaking7',
                enabled=True,
                filters=[
                    {
                        'abc': 'def'
                    }
                ]
            )
            await client.set_configuration_setting(new)
            await client.get_configuration_setting(new.key)

            new = FeatureFlagConfigurationSetting(
                'breaking8',
                enabled=True,
                filters=[
                    {
                        'abc': 'def'
                    }
                ]
            )
            new.feature_flag_content_type = "fakeyfakey" # cspell:disable-line
            await client.set_configuration_setting(new)
            await client.get_configuration_setting(new.key)

            await client.delete_configuration_setting(new.key)

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_breaking_with_secret_reference_configuration_setting(self, appconfiguration_connection_string):
        async with self.create_client(appconfiguration_connection_string) as client:
            new = SecretReferenceConfigurationSetting(
                "aref", # cspell:disable-line
                "notaurl"
            )
            await client.set_configuration_setting(new)
            await client.get_configuration_setting(new.key)

            new = SecretReferenceConfigurationSetting(
                "aref1", # cspell:disable-line
                "notaurl"
            )
            new.content_type = "fkaeyjfdkal;" # cspell:disable-line
            await client.set_configuration_setting(new)
            await client.get_configuration_setting(new.key)

            await client.delete_configuration_setting(new.key)


class TestAppConfigurationClientUnitTest:
    @pytest.mark.asyncio
    async def test_mock_policies(self):
        from azure.core.pipeline.transport import HttpResponse, AsyncHttpTransport
        from azure.core.pipeline import PipelineRequest, PipelineResponse
        from consts import APPCONFIGURATION_CONNECTION_STRING
        class MockTransport(AsyncHttpTransport):
            def __init__(self):
                self.auth_headers = []
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
            async def close(self):
                pass
            async def open(self):
                pass

            async def send(self, request: PipelineRequest, **kwargs: Any) -> PipelineResponse:
                assert request.headers['Authorization'] != self.auth_headers
                self.auth_headers.append(request.headers['Authorization'])
                response = HttpResponse(request, None)
                response.status_code = 429
                return response

        def new_method(self, request):
            request.http_request.headers["Authorization"] = str(uuid4())

        from azure.appconfiguration._azure_appconfiguration_requests import AppConfigRequestsCredentialsPolicy
        # Store the method to restore later
        temp = AppConfigRequestsCredentialsPolicy._signed_request
        AppConfigRequestsCredentialsPolicy._signed_request = new_method

        client = AzureAppConfigurationClient.from_connection_string(
            APPCONFIGURATION_CONNECTION_STRING, transport=MockTransport()
        )
        client.list_configuration_settings()

        # Reset the actual method
        AppConfigRequestsCredentialsPolicy._signed_request = temp
