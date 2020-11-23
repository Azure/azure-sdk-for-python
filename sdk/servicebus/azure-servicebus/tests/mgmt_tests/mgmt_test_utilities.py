#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#-------------------------------------------------------------------------
import pytest

from azure.core.exceptions import HttpResponseError


class MgmtListTestHelperInterface(object):
    def __init__(self, mgmt_client):
        self.sb_mgmt_client = mgmt_client

    def list_resource_method(self, start_index=0, max_count=100):
        pass

    def create_resource_method(self, name):
        pass

    def delete_resource_by_name_method(self, name):
        pass

    def get_resource_name(self, resource):
        pass


class MgmtQueueListTestHelper(MgmtListTestHelperInterface):
    def list_resource_method(self, start_index=0, max_count=100):
        return list(self.sb_mgmt_client.list_queues(start_index=start_index, max_count=max_count))

    def create_resource_method(self, name):
        self.sb_mgmt_client.create_queue(name)

    def delete_resource_by_name_method(self, name):
        self.sb_mgmt_client.delete_queue(name)

    def get_resource_name(self, queue):
        return queue.queue_name


class MgmtQueueListRuntimeInfoTestHelper(MgmtListTestHelperInterface):
    def list_resource_method(self, start_index=0, max_count=100):
        return list(self.sb_mgmt_client.list_queues_runtime_info(start_index=start_index, max_count=max_count))

    def create_resource_method(self, name):
        self.sb_mgmt_client.create_queue(name)

    def delete_resource_by_name_method(self, name):
        self.sb_mgmt_client.delete_queue(name)

    def get_resource_name(self, queue_info):
        return queue_info.queue_name


def run_test_mgmt_list_with_parameters(test_helper):
    result = test_helper.list_resource_method()
    assert len(result) == 0

    resources_names = []
    for i in range(20):
        test_helper.create_resource_method("test_resource{}".format(i))
        resources_names.append("test_resource{}".format(i))

    result = test_helper.list_resource_method()
    assert len(result) == 20

    sorted_resources_names = sorted(resources_names)

    result = test_helper.list_resource_method(start_index=5, max_count=10)
    expected_result = sorted_resources_names[5:15]
    assert len(result) == 10
    for item in result:
        expected_result.remove(test_helper.get_resource_name(item))
    assert len(expected_result) == 0

    result = test_helper.list_resource_method(max_count=0)
    assert len(result) == 0

    queues = test_helper.list_resource_method(start_index=0, max_count=0)
    assert len(queues) == 0

    cnt = 20
    for name in resources_names:
        test_helper.delete_resource_by_name_method(name)
        cnt -= 1
        assert len(test_helper.list_resource_method()) == cnt

    assert cnt == 0

    result = test_helper.list_resource_method()
    assert len(result) == 0


def run_test_mgmt_list_with_negative_parameters(test_helper):
    result = test_helper.list_resource_method()
    assert len(result) == 0

    with pytest.raises(HttpResponseError):
        test_helper.list_resource_method(start_index=-1)

    with pytest.raises(HttpResponseError):
        test_helper.list_resource_method(max_count=-1)

    with pytest.raises(HttpResponseError):
        test_helper.list_resource_method(start_index=-1, max_count=-1)

    test_helper.create_resource_method("test_resource")
    result = test_helper.list_resource_method()
    assert len(result) == 1 and test_helper.get_resource_name(result[0]) == "test_resource"

    with pytest.raises(HttpResponseError):
        test_helper.list_resource_method(start_index=-1)

    with pytest.raises(HttpResponseError):
        test_helper.list_resource_method(max_count=-1)

    with pytest.raises(HttpResponseError):
        test_helper.list_resource_method(start_index=-1, max_count=-1)

    test_helper.delete_resource_by_name_method("test_resource")
    result = test_helper.list_resource_method()
    assert len(result) == 0


def clear_queues(servicebus_management_client):
    queues = list(servicebus_management_client.list_queues())
    for queue in queues:
        try:
            servicebus_management_client.delete_queue(queue.name)
        except:
            pass


def clear_topics(servicebus_management_client):
    topics = list(servicebus_management_client.list_topics())
    for topic in topics:
        try:
            servicebus_management_client.delete_topic(topic.name)
        except:
            pass
