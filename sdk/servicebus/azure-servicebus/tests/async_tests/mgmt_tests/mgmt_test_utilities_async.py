#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#-------------------------------------------------------------------------
import pytest

from azure.core.exceptions import HttpResponseError


class AsyncMgmtListTestHelperInterface(object):
    def __init__(self, mgmt_client):
        self.sb_mgmt_client = mgmt_client

    async def list_resource_method(self, start_index=0, max_count=100):
        pass

    async def create_resource_method(self, name):
        pass

    async def delete_resource_by_name_method(self, name):
        pass

    async def get_resource_name(self, resource):
        pass


class AsyncMgmtQueueListTestHelper(AsyncMgmtListTestHelperInterface):
    async def list_resource_method(self, start_index=0, max_count=100):
        return await async_pageable_to_list(self.sb_mgmt_client.list_queues(start_index=start_index, max_count=max_count))

    async def create_resource_method(self, name):
        await self.sb_mgmt_client.create_queue(name)

    async def delete_resource_by_name_method(self, name):
        await self.sb_mgmt_client.delete_queue(name)

    async def get_resource_name(self, queue):
        return queue.queue_name


class AsyncMgmtQueueListRuntimeInfoTestHelper(AsyncMgmtListTestHelperInterface):
    async def list_resource_method(self, start_index=0, max_count=100):
        return await async_pageable_to_list(self.sb_mgmt_client.list_queues_runtime_info(start_index=start_index, max_count=max_count))

    async def create_resource_method(self, name):
        await self.sb_mgmt_client.create_queue(name)

    async def delete_resource_by_name_method(self, name):
        await self.sb_mgmt_client.delete_queue(name)

    async def get_resource_name(self, queue_info):
        return queue_info.queue_name


async def run_test_async_mgmt_list_with_parameters(test_helper):
    result = await test_helper.list_resource_method()
    assert len(result) == 0

    resources_names = []
    for i in range(20):
        await test_helper.create_resource_method("test_resource{}".format(i))
        resources_names.append("test_resource{}".format(i))

    result = await test_helper.list_resource_method()
    assert len(result) == 20

    sorted_resources_names = sorted(resources_names)

    result = await test_helper.list_resource_method(start_index=5, max_count=10)
    expected_result = sorted_resources_names[5:15]
    assert len(result) == 10
    for item in result:
        expected_result.remove(await test_helper.get_resource_name(item))
    assert len(expected_result) == 0

    result = await test_helper.list_resource_method(max_count=0)
    assert len(result) == 0

    queues = await test_helper.list_resource_method(start_index=0, max_count=0)
    assert len(queues) == 0

    cnt = 20
    for name in resources_names:
        await test_helper.delete_resource_by_name_method(name)
        cnt -= 1
        assert len(await test_helper.list_resource_method()) == cnt

    assert cnt == 0

    result = await test_helper.list_resource_method()
    assert len(result) == 0


async def run_test_async_mgmt_list_with_negative_parameters(test_helper):
    result = await test_helper.list_resource_method()
    assert len(result) == 0

    with pytest.raises(HttpResponseError):
        await test_helper.list_resource_method(start_index=-1)

    with pytest.raises(HttpResponseError):
        await test_helper.list_resource_method(max_count=-1)

    with pytest.raises(HttpResponseError):
        await test_helper.list_resource_method(start_index=-1, max_count=-1)

    await test_helper.create_resource_method("test_resource")
    result = await test_helper.list_resource_method()
    assert len(result) == 1 and (await test_helper.get_resource_name(result[0])) == "test_resource"

    with pytest.raises(HttpResponseError):
        await test_helper.list_resource_method(start_index=-1)

    with pytest.raises(HttpResponseError):
        await test_helper.list_resource_method(max_count=-1)

    with pytest.raises(HttpResponseError):
        await test_helper.list_resource_method(start_index=-1, max_count=-1)

    await test_helper.delete_resource_by_name_method("test_resource")
    result = await test_helper.list_resource_method()
    assert len(result) == 0


async def async_pageable_to_list(pageable):
    res = []
    async for item in pageable:
        res.append(item)
    return res


async def clear_queues(servicebus_management_client):
    queues = await async_pageable_to_list(servicebus_management_client.list_queues())
    for queue in queues:
        try:
            await servicebus_management_client.delete_queue(queue.name)
        except:
            pass


async def clear_topics(servicebus_management_client):
    topics = await async_pageable_to_list(servicebus_management_client.list_topics())
    for topic in topics:
        try:
            await servicebus_management_client.delete_topic(topic.name)
        except:
            pass
