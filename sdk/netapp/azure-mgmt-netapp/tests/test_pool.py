import time
import json
import unittest
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.netapp.models import CapacityPool, CapacityPoolPatch
from test_account import create_account, delete_account
from setup import *
import azure.mgmt.netapp.models
import unittest

pools = [TEST_POOL_1, TEST_POOL_2]

def create_pool(client, rg=TEST_RG, acc_name=TEST_ACC_1, pool_name=TEST_POOL_1, location=LOCATION, pool_only=False):
    if not pool_only:
        create_account(client, rg, acc_name, location)

    pool_body = CapacityPool(service_level=SERVICE_LEVEL, size=DEFAULT_SIZE, location=location)
    pool = client.pools.create_or_update(
        pool_body,
        rg,
        acc_name,
        pool_name,
        {'location': location}
    ).result()

    return pool

def wait_for_no_pool(client, rg, acc_name, pool_name, live=False):
    # a workaround for the async nature of certain ARM processes
    co=0
    while co<5:
        co += 1
        if live:
            time.sleep(10)
        try:
            pool = client.pools.get(rg, acc_name, pool_name)
        except:
            # not found is an exception case (status code 200 expected)
            # and is actually what we are waiting for
            break

def delete_pool(client, rg, acc_name, pool_name, live=False):
    # nest resources seem to hang around for a little while even
    # when apparently deleted, therefore give it a chance
    co=0
    while co<5:
        co += 1
        if live:
            time.sleep(10)
        try:
            client.pools.delete(rg, acc_name, pool_name).wait()
        except:
            # Want to catch specifically "Can not delete resource before nested resources are deleted."
            # but should be safe to generalise
            break
    wait_for_no_pool(client, rg, acc_name, pool_name, live)


@unittest.skip("skip test")
class NetAppAccountTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.AzureNetAppFilesManagementClient)

    def test_create_delete_pool(self):
        pool = create_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, LOCATION)
        self.assertEqual(pool.size, DEFAULT_SIZE)
        self.assertEqual(pool.name, TEST_ACC_1 + '/' + TEST_POOL_1)

        pool_list = self.client.pools.list(TEST_RG, TEST_ACC_1)
        self.assertEqual(len(list(pool_list)), 1)

        self.client.pools.delete(TEST_RG, TEST_ACC_1, TEST_POOL_1).wait()
        pool_list = self.client.pools.list(TEST_RG, TEST_ACC_1)
        self.assertEqual(len(list(pool_list)), 0)

        wait_for_no_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)

    def test_list_pools(self):
        pool = create_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, LOCATION)
        pool = create_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_2, LOCATION, pool_only=True)

        pool_list = self.client.pools.list(TEST_RG, TEST_ACC_1)
        self.assertEqual(len(list(pool_list)), 2)
        idx = 0
        for pool in pool_list:
            self.assertEqual(pool.name, pools[idx])
            idx += 1

        self.client.pools.delete(TEST_RG, TEST_ACC_1, TEST_POOL_1).wait()
        self.client.pools.delete(TEST_RG, TEST_ACC_1, TEST_POOL_2).wait()
        for pool in pools:
            wait_for_no_pool(self.client, TEST_RG, TEST_ACC_1, pools[idx], live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)

    def test_get_pool_by_name(self):
        pool = create_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, LOCATION)

        pool = self.client.pools.get(TEST_RG, TEST_ACC_1, TEST_POOL_1)
        self.assertEqual(pool.name, TEST_ACC_1 + '/' + TEST_POOL_1)

        self.client.pools.delete(TEST_RG, TEST_ACC_1, TEST_POOL_1).wait()
        wait_for_no_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)

    def test_update_pool(self):
        pool = create_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1)
        self.assertEqual(pool.service_level, "Premium")

        pool_body = CapacityPool(service_level="Standard", size=DEFAULT_SIZE, location=LOCATION)
        pool = self.client.pools.create_or_update(
            pool_body,
            TEST_RG,
            TEST_ACC_1,
            TEST_POOL_1,
            {'location': LOCATION}
        ).result()
        self.assertEqual(pool.service_level, "Standard")

        self.client.pools.delete(TEST_RG, TEST_ACC_1, TEST_POOL_1).wait()
        wait_for_no_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)

    def test_patch_pool(self):
        create_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1)

        tag = {'Tag2': 'Value1'}
        capacity_pool_patch = CapacityPoolPatch(service_level="Standard", tags=tag)

        pool = self.client.pools.update(capacity_pool_patch, TEST_RG, TEST_ACC_1, TEST_POOL_1).result()
        self.assertEqual(pool.service_level, "Standard")
        self.assertTrue(pool.tags['Tag2'] == 'Value1')

        self.client.pools.delete(TEST_RG, TEST_ACC_1, TEST_POOL_1).wait()
        wait_for_no_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)

