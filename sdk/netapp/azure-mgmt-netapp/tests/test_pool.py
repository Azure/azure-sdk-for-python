import time
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy
from azure.mgmt.netapp.models import CapacityPool, CapacityPoolPatch
from test_account import create_account, delete_account
from setup import *
import azure.mgmt.netapp.models

DEFAULT_SIZE = 4398046511104
LIVE = False

def create_pool(client, rg=TEST_RG, acc_name=TEST_ACC_1, pool_name=TEST_POOL_1, location=LOCATION, pool_only=False):    
    if not pool_only:
        create_account(client, rg, acc_name, location)
    print("Creating pool {0} in NetApp Account {1}".format(pool_name,acc_name))
    pool_body = CapacityPool(service_level=SERVICE_LEVEL, size=DEFAULT_SIZE, location=location)
    pool = client.pools.begin_create_or_update(
        rg,
        acc_name,
        pool_name,
        pool_body
    ).result()
    wait_for_pool(client, rg, acc_name, pool_name)
    print("\tdone")
    return pool

def wait_for_pool(client, rg, account_name, pool_name):
    # a work around for the async nature of certain ARM processes
    co = 0
    while co < 60:
        pool = client.pools.get(rg, account_name, pool_name)
        if pool.provisioning_state == "Succeeded":
            break
        if LIVE:
            time.sleep(3)
        co += 1
    print("Retried {0} times".format(co))

def wait_for_no_pool(client, rg, acc_name, pool_name):
    # a workaround for the async nature of certain ARM processes
    co = 0
    while co < 100:
        try:
            client.pools.get(rg, acc_name, pool_name)
        except:
            # not found is an exception case (status code 200 expected)
            # and is actually what we are waiting for
            break
        if LIVE:
            time.sleep(3)
        co += 1
    print("Retried {0} times".format(co))

def delete_pool(client, rg, acc_name, pool_name):
    # nest resources seem to hang around for a little while even
    # when apparently deleted, therefore give it a chance
    print("Deleting pool {0} in NetApp Account {1}".format(pool_name,acc_name))
    retry = 0
    while retry < 3:
        try:
            client.pools.begin_delete(rg, acc_name, pool_name).wait()
            break
        except Exception as e: 
            print("failed to delete pool. Retry number: {0}".format(retry))
            print(e)
            retry += 1
            if LIVE:
                time.sleep(10)

    wait_for_no_pool(client, rg, acc_name, pool_name)
    print("\tdone")

class TestNetAppCapacityPool(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        if self.is_live:
            global LIVE
            LIVE = True

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_create_delete_pool(self):
        print("Starting test_create_delete_pool")
        account_name1 = self.get_resource_name(TEST_ACC_1+"-")
        pool = create_pool(self.client, TEST_RG, account_name1, TEST_POOL_1, LOCATION)
        assert pool.size == DEFAULT_SIZE
        assert pool.name == account_name1 + '/' + TEST_POOL_1

        pool_list = self.client.pools.list(TEST_RG, account_name1)
        assert len(list(pool_list)) == 1

        delete_pool(self.client, TEST_RG, account_name1, TEST_POOL_1)
        pool_list = self.client.pools.list(TEST_RG, account_name1)
        assert len(list(pool_list)) == 0

        delete_account(self.client, TEST_RG, account_name1)
        
        print("Finished with test_create_delete_pool")

    @recorded_by_proxy
    def test_list_pools(self):
        print("Starting test_list_pools")
        account_name1 = self.get_resource_name(TEST_ACC_1+"-")
        create_pool(self.client, TEST_RG, account_name1, TEST_POOL_1, LOCATION)
        create_pool(self.client, TEST_RG, account_name1, TEST_POOL_2, LOCATION, pool_only=True)
        pools = [TEST_POOL_1, TEST_POOL_2]

        pool_list = self.client.pools.list(TEST_RG, account_name1)
        assert len(list(pool_list)) == 2
        idx = 0
        for pool in pool_list:
            assert pool.name == pools[idx]
            idx += 1

        delete_pool(self.client, TEST_RG, account_name1, TEST_POOL_1)
        delete_pool(self.client, TEST_RG, account_name1, TEST_POOL_2)
        delete_account(self.client, TEST_RG, account_name1)
        print("Finished with test_list_pools")

    @recorded_by_proxy
    def test_get_pool_by_name(self):
        print("Starting test_get_pool_by_name")
        account_name1 = self.get_resource_name(TEST_ACC_1+"-")
        create_pool(self.client, TEST_RG, account_name1, TEST_POOL_1, LOCATION)

        pool = self.client.pools.get(TEST_RG, account_name1, TEST_POOL_1)
        assert pool.name == account_name1 + '/' + TEST_POOL_1

        delete_pool(self.client, TEST_RG, account_name1, TEST_POOL_1)
        delete_account(self.client, TEST_RG, account_name1)
        print("Finished with test_get_pool_by_name")

    @recorded_by_proxy
    def test_update_pool(self):
        print("Starting test_update_pool")
        account_name1 = self.get_resource_name(TEST_ACC_1+"-")
        pool = create_pool(self.client, TEST_RG, account_name1, TEST_POOL_1)
        assert pool.qos_type == "Auto"

        pool_body = CapacityPoolPatch(qos_type="Manual", size=DEFAULT_SIZE, location=LOCATION)
        pool = self.client.pools.begin_create_or_update(
            TEST_RG,
            account_name1,
            TEST_POOL_1,
            pool_body
        ).result()
        assert pool.qos_type == "Manual"

        delete_pool(self.client, TEST_RG, account_name1, TEST_POOL_1)
        delete_account(self.client, TEST_RG, account_name1)
        print("Finished with test_update_pool")

    @recorded_by_proxy
    def test_patch_pool(self):
        print("Starting test_patch_pool")
        account_name1 = self.get_resource_name(TEST_ACC_1+"-")
        create_pool(self.client, TEST_RG, account_name1, TEST_POOL_1)

        tag = {'Tag2': 'Value1'}
        capacity_pool_patch = CapacityPoolPatch(qos_type="Manual", tags=tag)

        pool = self.client.pools.begin_update(TEST_RG, account_name1, TEST_POOL_1, capacity_pool_patch).result()
        assert pool.qos_type == "Manual"
        assert pool.tags['Tag2'] == 'Value1'

        delete_pool(self.client, TEST_RG, account_name1, TEST_POOL_1)
        delete_account(self.client, TEST_RG, account_name1)
        print("Finished with test_patch_pool")