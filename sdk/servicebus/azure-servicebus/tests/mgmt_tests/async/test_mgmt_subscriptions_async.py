#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import logging
import pytest
import datetime

from azure.servicebus.aio.management import ServiceBusAdministrationClient
from azure.servicebus.management import SubscriptionProperties
from utilities import get_logger
from azure.core.exceptions import HttpResponseError, ResourceExistsError

from devtools_testutils import AzureMgmtRecordedTestCase, CachedResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from sb_env_loader import (
    ServiceBusPreparer
)
from servicebus_preparer import (
    SERVICEBUS_ENDPOINT_SUFFIX
)

from mgmt_test_utilities_async import async_pageable_to_list, clear_topics

_logger = get_logger(logging.DEBUG)


class TestServiceBusAdministrationClientSubscriptionAsync(AzureMgmtRecordedTestCase):
    @ServiceBusPreparer()
    @recorded_by_proxy_async
    async def test_async_mgmt_subscription_create_by_name(self, servicebus_connection_str, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_connection_str)
        await clear_topics(mgmt_service)
        topic_name = "topic_testaddf"
        subscription_name = "sub_testkkk"

        try:
            await mgmt_service.create_topic(topic_name)
            await mgmt_service.create_subscription(topic_name, subscription_name)
            subscription = await mgmt_service.get_subscription(topic_name, subscription_name)
            assert subscription.name == subscription_name
            assert subscription.availability_status == 'Available'
            assert subscription.status == 'Active'
        finally:
            await mgmt_service.delete_subscription(topic_name, subscription_name)
            await mgmt_service.delete_topic(topic_name)

    @ServiceBusPreparer()
    @recorded_by_proxy_async
    async def test_async_mgmt_sub_create_w_sub_desc(self, servicebus_connection_str, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_connection_str)
        await clear_topics(mgmt_service)
        topic_name = "iweidk"
        subscription_name = "kdosako"
        subscription_name_2 = "owazmq"
        try:
            await mgmt_service.create_topic(topic_name)
            await mgmt_service.create_subscription(
                topic_name,
                subscription_name=subscription_name,
                auto_delete_on_idle=datetime.timedelta(minutes=10),
                dead_lettering_on_message_expiration=True,
                default_message_time_to_live=datetime.timedelta(minutes=11),
                enable_batched_operations=True,
                lock_duration=datetime.timedelta(seconds=13),
                max_delivery_count=14,
                requires_session=True
            )
            subscription = await mgmt_service.get_subscription(topic_name, subscription_name)
            assert subscription.name == subscription_name
            assert subscription.auto_delete_on_idle == datetime.timedelta(minutes=10)
            assert subscription.dead_lettering_on_message_expiration == True
            assert subscription.default_message_time_to_live == datetime.timedelta(minutes=11)
            assert subscription.enable_batched_operations == True
            assert subscription.lock_duration == datetime.timedelta(seconds=13)
            assert subscription.max_delivery_count == 14
            assert subscription.requires_session == True

            await mgmt_service.create_subscription(
                topic_name,
                subscription_name=subscription_name_2,
                auto_delete_on_idle="PT10M",
                dead_lettering_on_message_expiration=True,
                default_message_time_to_live="PT11M",
                enable_batched_operations=True,
                lock_duration="PT13S",
                max_delivery_count=14,
                requires_session=True
            )
            subscription_2 = await mgmt_service.get_subscription(topic_name, subscription_name_2)
            assert subscription_2.name == subscription_name_2
            assert subscription_2.auto_delete_on_idle == datetime.timedelta(minutes=10)
            assert subscription_2.dead_lettering_on_message_expiration == True
            assert subscription_2.default_message_time_to_live == datetime.timedelta(minutes=11)
            assert subscription_2.enable_batched_operations == True
            assert subscription_2.lock_duration == datetime.timedelta(seconds=13)
            assert subscription_2.max_delivery_count == 14
            assert subscription_2.requires_session == True
        finally:
            await mgmt_service.delete_subscription(topic_name, subscription_name)
            await mgmt_service.delete_subscription(topic_name, subscription_name_2)
            await mgmt_service.delete_topic(topic_name)

    @ServiceBusPreparer()
    @recorded_by_proxy_async
    async def test_async_mgmt_sub_create_w_fwd_to(self, servicebus_connection_str, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_connection_str)
        await clear_topics(mgmt_service)
        topic_name = "iweidkforward"
        subscription_name = "kdosakoforward"
        queue_name = "dkfthj"
        try:
            await mgmt_service.create_queue(queue_name)
            await mgmt_service.create_topic(topic_name)
            await mgmt_service.create_subscription(
                topic_name,
                subscription_name=subscription_name,
                forward_dead_lettered_messages_to=queue_name,
                forward_to=queue_name,
            )
            subscription = await mgmt_service.get_subscription(topic_name, subscription_name)
            # Test forward_to (separately, as it changes auto_delete_on_idle when you enable it.)
            # Note: We endswith to avoid the fact that the servicebus_fully_qualified_namespace_name is replacered locally but not in the properties bag, and still test this.
            assert subscription.forward_to.endswith(f"{SERVICEBUS_ENDPOINT_SUFFIX}/{queue_name}")
            assert subscription.forward_dead_lettered_messages_to.endswith(f"{SERVICEBUS_ENDPOINT_SUFFIX}/{queue_name}")

        finally:
            await mgmt_service.delete_subscription(topic_name, subscription_name)
            await mgmt_service.delete_topic(topic_name)
            await mgmt_service.delete_queue(queue_name)
            await mgmt_service.close()

    @ServiceBusPreparer()
    @recorded_by_proxy_async
    async def test_async_mgmt_subscription_create_duplicate(self, servicebus_connection_str, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_connection_str)
        await clear_topics(mgmt_service)
        topic_name = "dqkodq"
        subscription_name = 'kkaqo'
        try:
            await mgmt_service.create_topic(topic_name)
            await mgmt_service.create_subscription(topic_name, subscription_name)
            with pytest.raises(ResourceExistsError):
                await mgmt_service.create_subscription(topic_name, subscription_name)
        finally:
            await mgmt_service.delete_subscription(topic_name, subscription_name)
            await mgmt_service.delete_topic(topic_name)

    @ServiceBusPreparer()
    @recorded_by_proxy_async
    async def test_async_mgmt_subscription_update_success(self, servicebus_connection_str, servicebus_fully_qualified_namespace, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_connection_str)
        await clear_topics(mgmt_service)
        topic_name = "fjrui"
        subscription_name = "eqkovc"
        queue_name = "dfkla"

        try:
            await mgmt_service.create_queue(queue_name)
            topic_description = await mgmt_service.create_topic(topic_name)
            subscription_description = await mgmt_service.create_subscription(topic_description.name, subscription_name)

            # Try updating one setting.
            subscription_description.lock_duration = datetime.timedelta(minutes=2)
            await mgmt_service.update_subscription(topic_description.name, subscription_description)
            subscription_description = await mgmt_service.get_subscription(topic_name, subscription_name)
            assert subscription_description.lock_duration == datetime.timedelta(minutes=2)

            # Now try updating all settings.
            subscription_description.auto_delete_on_idle = datetime.timedelta(minutes=10)
            subscription_description.dead_lettering_on_message_expiration = True
            subscription_description.default_message_time_to_live = datetime.timedelta(minutes=11)
            subscription_description.lock_duration = datetime.timedelta(seconds=12)
            subscription_description.max_delivery_count = 14
            # topic_description.enable_partitioning = True # Cannot be changed after creation
            # topic_description.requires_session = True # Cannot be changed after creation

            await mgmt_service.update_subscription(topic_description.name, subscription_description)
            subscription_description = await mgmt_service.get_subscription(topic_description.name, subscription_name)

            assert subscription_description.auto_delete_on_idle == datetime.timedelta(minutes=10)
            assert subscription_description.dead_lettering_on_message_expiration == True
            assert subscription_description.default_message_time_to_live == datetime.timedelta(minutes=11)
            assert subscription_description.max_delivery_count == 14
            assert subscription_description.lock_duration == datetime.timedelta(seconds=12)
            # assert topic_description.enable_partitioning == True
            # assert topic_description.requires_session == True

            # Finally, test forward_to (separately, as it changes auto_delete_on_idle when you enable it.)
            subscription_description.forward_to = "sb://{}/{}".format(servicebus_fully_qualified_namespace, topic_name)
            subscription_description.forward_dead_lettered_messages_to = "sb://{}/{}".format(servicebus_fully_qualified_namespace, topic_name)
            await mgmt_service.update_subscription(topic_description.name, subscription_description)
            subscription_description = await mgmt_service.get_subscription(topic_description.name, subscription_name)
            # Note: We endswith to avoid the fact that the servicebus_fully_qualified_namespace_name is replacered locally but not in the properties bag, and still test this.
            assert subscription_description.forward_to.endswith(f"{SERVICEBUS_ENDPOINT_SUFFIX}/{topic_name}")
            assert subscription_description.forward_dead_lettered_messages_to.endswith(f"{SERVICEBUS_ENDPOINT_SUFFIX}/{topic_name}")

            # Update forward_to with entity name
            subscription_description.forward_to = queue_name
            subscription_description.forward_dead_lettered_messages_to = queue_name
            await mgmt_service.update_subscription(topic_description.name, subscription_description)
            subscription_description = await mgmt_service.get_subscription(topic_description.name, subscription_name)
            # Note: We endswith to avoid the fact that the servicebus_fully_qualified_namespace_name is replacered locally but not in the properties bag, and still test this.
            assert subscription_description.forward_to.endswith(f"{SERVICEBUS_ENDPOINT_SUFFIX}/{queue_name}")
            assert subscription_description.forward_dead_lettered_messages_to.endswith(f"{SERVICEBUS_ENDPOINT_SUFFIX}/{queue_name}")

            # Update forward_to with None
            subscription_description.forward_to = None
            subscription_description.forward_dead_lettered_messages_to = None
            await mgmt_service.update_subscription(topic_description.name, subscription_description)
            subscription_description = await mgmt_service.get_subscription(topic_description.name, subscription_name)
            # Note: We endswith to avoid the fact that the servicebus_fully_qualified_namespace_name is replacered locally but not in the properties bag, and still test this.
            assert subscription_description.forward_to is None
            assert subscription_description.forward_dead_lettered_messages_to is None

            subscription_description.auto_delete_on_idle = "PT10M1S"
            subscription_description.default_message_time_to_live = "PT11M2S"
            subscription_description.lock_duration = "PT3M3S"
            await mgmt_service.update_subscription(topic_description.name, subscription_description)
            subscription_description = await mgmt_service.get_subscription(topic_description.name, subscription_name)
            assert subscription_description.auto_delete_on_idle == datetime.timedelta(minutes=10, seconds=1)
            assert subscription_description.default_message_time_to_live == datetime.timedelta(minutes=11, seconds=2)
            assert subscription_description.lock_duration == datetime.timedelta(minutes=3, seconds=3)

            # updating all settings with keyword arguments.
            await mgmt_service.update_subscription(
                topic_description.name,
                subscription_description,
                auto_delete_on_idle=datetime.timedelta(minutes=15),
                dead_lettering_on_message_expiration=False,
                default_message_time_to_live=datetime.timedelta(minutes=16),
                lock_duration=datetime.timedelta(seconds=17),
                max_delivery_count=15,
                forward_to=None,
                forward_dead_lettered_messages_to=None
            )

            subscription_description = await mgmt_service.get_subscription(topic_description.name, subscription_name)

            assert subscription_description.auto_delete_on_idle == datetime.timedelta(minutes=15)
            assert subscription_description.dead_lettering_on_message_expiration == False
            assert subscription_description.default_message_time_to_live == datetime.timedelta(minutes=16)
            assert subscription_description.max_delivery_count == 15
            assert subscription_description.lock_duration == datetime.timedelta(seconds=17)
            assert subscription_description.forward_to == None
            assert subscription_description.forward_dead_lettered_messages_to == None

        finally:
            await mgmt_service.delete_subscription(topic_name, subscription_name)
            await mgmt_service.delete_topic(topic_name)
            await mgmt_service.delete_queue(queue_name)
            await mgmt_service.close()

    @ServiceBusPreparer()
    @recorded_by_proxy_async
    async def test_async_mgmt_subscription_update_invalid(self, servicebus_connection_str, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_connection_str)
        await clear_topics(mgmt_service)
        topic_name = "dfjfj"
        subscription_name = "kwqxc"
        try:
            topic_description = await mgmt_service.create_topic(topic_name)
            subscription_description = await mgmt_service.create_subscription(topic_name, subscription_name)

            # handle a null update properly.
            with pytest.raises(TypeError):
                await mgmt_service.update_subscription(topic_name, None)

            # handle an invalid type update properly.
            with pytest.raises(TypeError):
                await mgmt_service.update_subscription(topic_name, Exception("test"))

            # change the name to a topic that doesn't exist; should fail.
            subscription_description.name = "iewdm"
            with pytest.raises(HttpResponseError):
                await mgmt_service.update_subscription(topic_name, subscription_description)
            subscription_description.name = subscription_name

            # change the name to a topic with an invalid name exist; should fail.
            subscription_description.name = ''
            with pytest.raises(HttpResponseError):
                await mgmt_service.update_subscription(topic_name, subscription_description)
            subscription_description.name = topic_name

            # change to a setting with an invalid value; should still fail.
            subscription_description.lock_duration = datetime.timedelta(days=25)
            with pytest.raises(HttpResponseError):
                await mgmt_service.update_subscription(topic_name, subscription_description)
            subscription_description.lock_duration = datetime.timedelta(minutes=5)
        finally:
            await mgmt_service.delete_subscription(topic_name, subscription_name)
            await mgmt_service.delete_topic(topic_name)

    @ServiceBusPreparer()
    @recorded_by_proxy_async
    async def test_async_mgmt_subscription_delete(self, servicebus_connection_str):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_connection_str)
        await clear_topics(mgmt_service)
        topic_name = 'test_topicgda'
        subscription_name_1 = 'test_sub1da'
        subscription_name_2 = 'test_sub2gcv'
        await mgmt_service.create_topic(topic_name)

        await mgmt_service.create_subscription(topic_name, subscription_name_1)
        subscriptions = await async_pageable_to_list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 1

        await mgmt_service.create_subscription(topic_name, subscription_name_2)
        subscriptions = await async_pageable_to_list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 2

        description = await mgmt_service.get_subscription(topic_name, subscription_name_1)
        await mgmt_service.delete_subscription(topic_name, description.name)

        subscriptions = await async_pageable_to_list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 1 and subscriptions[0].name == subscription_name_2

        await mgmt_service.delete_subscription(topic_name, subscription_name_2)

        subscriptions = await async_pageable_to_list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 0
        await mgmt_service.delete_topic(topic_name)

    @ServiceBusPreparer()
    @recorded_by_proxy_async
    async def test_async_mgmt_subscription_list(self, servicebus_connection_str, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_connection_str)
        await clear_topics(mgmt_service)
        topic_name = 'lkoqxc'
        subscription_name_1 = 'testsub1'
        subscription_name_2 = 'testsub2'

        await mgmt_service.create_topic(topic_name)
        subscriptions = await async_pageable_to_list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 0
        await mgmt_service.create_subscription(topic_name, subscription_name_1)
        await mgmt_service.create_subscription(topic_name, subscription_name_2)
        subscriptions = await async_pageable_to_list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 2
        assert subscriptions[0].name == subscription_name_1
        assert subscriptions[1].name == subscription_name_2
        await mgmt_service.delete_subscription(topic_name, subscription_name_1)
        await mgmt_service.delete_subscription(topic_name, subscription_name_2)
        subscriptions = await async_pageable_to_list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 0
        await mgmt_service.delete_topic(topic_name)

    @ServiceBusPreparer()
    @recorded_by_proxy_async
    async def test_async_mgmt_sub_list_runtime_props(self, servicebus_connection_str, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_connection_str)
        await clear_topics(mgmt_service)
        topic_name = 'dkoamv'
        subscription_name = 'cxqplc'
        await mgmt_service.create_topic(topic_name)

        subs = await async_pageable_to_list(mgmt_service.list_subscriptions(topic_name))
        subs_infos = await async_pageable_to_list(mgmt_service.list_subscriptions_runtime_properties(topic_name))

        assert len(subs) == len(subs_infos) == 0

        await mgmt_service.create_subscription(topic_name, subscription_name)

        subs = await async_pageable_to_list(mgmt_service.list_subscriptions(topic_name))
        subs_infos = await async_pageable_to_list(mgmt_service.list_subscriptions_runtime_properties(topic_name))

        assert len(subs) == 1 and len(subs_infos) == 1

        assert subs[0].name == subs_infos[0].name == subscription_name

        info = subs_infos[0]

        assert info.accessed_at_utc is not None
        assert info.updated_at_utc is not None
        assert info.created_at_utc is not None
        assert info.total_message_count == 0
        assert info.active_message_count == 0
        assert info.dead_letter_message_count == 0
        assert info.transfer_dead_letter_message_count == 0
        assert info.transfer_message_count == 0

        await mgmt_service.delete_subscription(topic_name, subscription_name)
        subs_infos = await async_pageable_to_list(mgmt_service.list_subscriptions_runtime_properties(topic_name))
        assert len(subs_infos) == 0

        await mgmt_service.delete_topic(topic_name)

    @ServiceBusPreparer()
    @recorded_by_proxy_async
    async def test_async_mgmt_sub_get_runtime_props_basic(self, servicebus_connection_str):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_connection_str)
        await clear_topics(mgmt_service)
        topic_name = 'dcvxqa'
        subscription_name = 'xvazzag'

        await mgmt_service.create_topic(topic_name)
        await mgmt_service.create_subscription(topic_name, subscription_name)
        sub_runtime_properties = await mgmt_service.get_subscription_runtime_properties(topic_name, subscription_name)

        assert sub_runtime_properties
        assert sub_runtime_properties.name == subscription_name
        assert sub_runtime_properties.created_at_utc is not None
        assert sub_runtime_properties.accessed_at_utc is not None
        assert sub_runtime_properties.updated_at_utc is not None
        assert sub_runtime_properties.total_message_count == 0
        assert sub_runtime_properties.active_message_count == 0
        assert sub_runtime_properties.dead_letter_message_count == 0
        assert sub_runtime_properties.transfer_dead_letter_message_count == 0
        assert sub_runtime_properties.transfer_message_count == 0

        await mgmt_service.delete_subscription(topic_name, subscription_name)
        await mgmt_service.delete_topic(topic_name)

    @ServiceBusPreparer()
    @recorded_by_proxy_async
    async def test_mgmt_sub_async_update_dict_success(self, servicebus_connection_str, servicebus_fully_qualified_namespace, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_connection_str)
        await clear_topics(mgmt_service)
        topic_name = "fjrui"
        subscription_name = "eqkovc"

        try:
            topic_description = await mgmt_service.create_topic(topic_name)
            subscription_description = await mgmt_service.create_subscription(topic_description.name, subscription_name)
            subscription_description_dict = dict(subscription_description)

            # Try updating one setting.
            subscription_description_dict["lock_duration"] = datetime.timedelta(minutes=2)
            await mgmt_service.update_subscription(topic_description.name, subscription_description_dict)
            subscription_description = await mgmt_service.get_subscription(topic_name, subscription_name)
            assert subscription_description.lock_duration == datetime.timedelta(minutes=2)

            # Now try updating all settings.
            subscription_description_dict = dict(subscription_description)
            subscription_description_dict["auto_delete_on_idle"] = datetime.timedelta(minutes=10)
            subscription_description_dict["dead_lettering_on_message_expiration"] = True
            subscription_description_dict["default_message_time_to_live"] = datetime.timedelta(minutes=11)
            subscription_description_dict["lock_duration"] = datetime.timedelta(seconds=12)
            subscription_description_dict["max_delivery_count"] = 14
            # topic_description.enable_partitioning = True # Cannot be changed after creation
            # topic_description.requires_session = True # Cannot be changed after creation

            await mgmt_service.update_subscription(topic_description.name, subscription_description_dict)
            subscription_description = await mgmt_service.get_subscription(topic_description.name, subscription_name)

            assert subscription_description.auto_delete_on_idle == datetime.timedelta(minutes=10)
            assert subscription_description.dead_lettering_on_message_expiration == True
            assert subscription_description.default_message_time_to_live == datetime.timedelta(minutes=11)
            assert subscription_description.max_delivery_count == 14
            assert subscription_description.lock_duration == datetime.timedelta(seconds=12)
            # assert topic_description.enable_partitioning == True
            # assert topic_description.requires_session == True

            # Finally, test forward_to (separately, as it changes auto_delete_on_idle when you enable it.)
            subscription_description_dict = dict(subscription_description)
            subscription_description_dict["forward_to"] = "sb://{}/{}".format(servicebus_fully_qualified_namespace, topic_name)
            subscription_description_dict["forward_dead_lettered_messages_to"] = "sb://{}/{}".format(servicebus_fully_qualified_namespace, topic_name)
            await mgmt_service.update_subscription(topic_description.name, subscription_description_dict)
            subscription_description = await mgmt_service.get_subscription(topic_description.name, subscription_name)
            # Note: We endswith to avoid the fact that the servicebus_fully_qualified_namespace_name is replacered locally but not in the properties bag, and still test this.
            assert subscription_description.forward_to.endswith(f"{SERVICEBUS_ENDPOINT_SUFFIX}/{topic_name}")
            assert subscription_description.forward_dead_lettered_messages_to.endswith(f"{SERVICEBUS_ENDPOINT_SUFFIX}/{topic_name}")

            # updating all settings with keyword arguments.
            await mgmt_service.update_subscription(
                topic_description.name,
                dict(subscription_description),
                auto_delete_on_idle=datetime.timedelta(minutes=15),
                dead_lettering_on_message_expiration=False,
                default_message_time_to_live=datetime.timedelta(minutes=16),
                lock_duration=datetime.timedelta(seconds=17),
                max_delivery_count=15,
                forward_to=None,
                forward_dead_lettered_messages_to=None
            )

            subscription_description = await mgmt_service.get_subscription(topic_description.name, subscription_name)

            assert subscription_description.auto_delete_on_idle == datetime.timedelta(minutes=15)
            assert subscription_description.dead_lettering_on_message_expiration == False
            assert subscription_description.default_message_time_to_live == datetime.timedelta(minutes=16)
            assert subscription_description.max_delivery_count == 15
            assert subscription_description.lock_duration == datetime.timedelta(seconds=17)
            assert subscription_description.forward_to == None
            assert subscription_description.forward_dead_lettered_messages_to == None
        finally:
            await mgmt_service.delete_subscription(topic_name, subscription_name)
            await mgmt_service.delete_topic(topic_name)
            await mgmt_service.close()

    @ServiceBusPreparer()
    @recorded_by_proxy_async
    async def test_mgmt_subscription_async_update_dict_error(self, servicebus_connection_str, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_connection_str)
        await clear_topics(mgmt_service)
        topic_name = "fjrui"
        subscription_name = "eqkovc"

        try:
            topic_description = await mgmt_service.create_topic(topic_name)
            subscription_description = await mgmt_service.create_subscription(topic_description.name, subscription_name)
            # send in subscription dict without non-name keyword args
            subscription_description_only_name = {"name": topic_name}
            with pytest.raises(TypeError):
                await mgmt_service.update_subscription(topic_description.name, subscription_description_only_name)
        finally:
            await mgmt_service.delete_subscription(topic_name, subscription_name)
            await mgmt_service.delete_topic(topic_name)
