# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import EasmTest, EasmParameterProvider
from devtools_testutils import recorded_by_proxy

class TestEasmTaskClient(EasmTest):
    existing_task_id = '7cf2c2d9-8125-4043-a82c-b86baa2c60fd'
    time_format = '%Y-%m-%dT%H:%M:%S.%f%z'

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_list_tasks(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        tasks = client.tasks.list()
        task = tasks.next()
        self.check_guid_format(task['id'])
        self.check_timestamp_format(self.time_format, task['startedAt'])

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_get_task(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        task = client.tasks.get(self.existing_task_id)
        self.check_guid_format(task['id'])
        self.check_timestamp_format(self.time_format, task['startedAt'])
