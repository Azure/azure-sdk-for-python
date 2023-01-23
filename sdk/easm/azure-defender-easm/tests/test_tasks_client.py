# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import EasmTest, EasmPowerShellPreparer

class EasmTasksTest(EasmTest):
    existing_task_id = 'a23b2f6b-a1ce-4b89-9bfd-97339d39c847'
    time_format = '%Y-%m-%dT%H:%M:%S.%f%z'

    @EasmPowerShellPreparer()
    def test_list_tasks(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        tasks = client.tasks.list()
        task = tasks.next()
        self.check_guid_format(task['id'])
        self.check_timestamp_format(self.time_format, task['startedAt'])

    @EasmPowerShellPreparer()
    def test_get_task(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        task = client.tasks.get(self.existing_task_id)
        self.check_guid_format(task['id'])
        self.check_timestamp_format(self.time_format, task['startedAt'])
