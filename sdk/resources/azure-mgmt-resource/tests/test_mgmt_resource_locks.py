# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# coverd ops:
#   management_locks: 16/16
#   authorization_operations: 1/1

import unittest

import azure.mgmt.resource
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

class TestMgmtResourceLocks(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.locks_client = self.create_mgmt_client(
            azure.mgmt.resource.ManagementLockClient
        )

        self.resource_client = self.create_mgmt_client(
            azure.mgmt.resource.ResourceManagementClient
        )

    @recorded_by_proxy
    def test_locks_at_subscription_level(self):
        lock_name = 'pylockrg'

        lock = self.locks_client.management_locks.create_or_update_at_subscription_level(
            lock_name,
            {
                'level': 'CanNotDelete'
            }
        )
        assert lock is not None

        self.locks_client.management_locks.get_at_subscription_level(
            lock_name
        )

        locks = list(self.locks_client.management_locks.list_at_subscription_level())

        lock = self.locks_client.management_locks.delete_at_subscription_level(
            lock_name
        )

    @RandomNameResourceGroupPreparer()
    @recorded_by_proxy
    def test_locks_by_scope(self, **kwargs):
        resource_group = kwargs.pop("resource_group")
        location = kwargs.pop("location")
        lock_name = "pylockrg"
        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        resource_name = self.get_resource_name("pytestavset")

        resource_id = "/subscriptions/{guid}/resourceGroups/{resourcegroupname}/providers/{resourceprovidernamespace}/{resourcetype}/{resourcename}".format(
            guid=SUBSCRIPTION_ID,
            resourcegroupname=resource_group.name,
            resourceprovidernamespace="Microsoft.Compute",
            resourcetype="availabilitySets",
            resourcename=resource_name
        )

        create_result = self.resource_client.resources.begin_create_or_update_by_id(
            resource_id,
            parameters={'location': location},
            api_version="2019-07-01"
        )

        lock = self.locks_client.management_locks.create_or_update_by_scope(
            resource_id,
            lock_name,
            {
                'level': 'CanNotDelete'
            }
        )

        self.locks_client.management_locks.get_by_scope(
            resource_id,
            lock_name
        )

        self.locks_client.management_locks.list_by_scope(
            resource_id
        )

        self.locks_client.management_locks.delete_by_scope(
            resource_id,
            lock_name
        )

        result = self.resource_client.resources.begin_delete_by_id(
            resource_id,
            api_version="2019-07-01"
        )
        result = result.result()

    @RandomNameResourceGroupPreparer()
    @recorded_by_proxy
    def test_locks_at_resource_level(self, **kwargs):
        resource_group = kwargs.pop("resource_group")
        location = kwargs.pop("location")
        lock_name = 'pylockrg'
        resource_name = self.get_resource_name("pytestavset")

        # create resource
        create_result = self.resource_client.resources.begin_create_or_update(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            parameters={'location': location},
            api_version="2019-07-01"
        )

        lock = self.locks_client.management_locks.create_or_update_at_resource_level(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            lock_name=lock_name,
            parameters={
                'level': 'CanNotDelete'
            }
        )
        assert lock is not None

        self.locks_client.management_locks.get_at_resource_level(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            lock_name=lock_name,
        )

        locks = list(self.locks_client.management_locks.list_at_resource_level(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
        ))
        assert len(locks) == 1

        lock = self.locks_client.management_locks.delete_at_resource_level(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            lock_name=lock_name,
        )

        # delete resource
        delete_result = self.resource_client.resources.begin_delete(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            api_version="2019-07-01"
        )
        delete_result.wait()

    @RandomNameResourceGroupPreparer()
    @recorded_by_proxy
    def test_locks_at_resource_group_level(self, **kwargs):
        resource_group = kwargs.pop("resource_group")
        location = kwargs.pop("location")
        lock_name = 'pylockrg'

        lock = self.locks_client.management_locks.create_or_update_at_resource_group_level(
            resource_group.name,
            lock_name,
            {
                'level': 'CanNotDelete'
            }
        )
        assert lock is not None

        self.locks_client.management_locks.get_at_resource_group_level(
            resource_group.name,
            lock_name
        )

        locks = list(self.locks_client.management_locks.list_at_resource_group_level(
            resource_group.name
        ))
        assert len(locks) == 1

        lock = self.locks_client.management_locks.delete_at_resource_group_level(
            resource_group.name,
            lock_name
        )

    @recorded_by_proxy
    def test_operations(self):
        self.locks_client.authorization_operations.list()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
