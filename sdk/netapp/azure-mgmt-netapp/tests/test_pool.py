import time
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy
from azure.mgmt.netapp.models import CapacityPool, CapacityPoolPatch
from test_account import create_account, delete_account
import setup
import azure.mgmt.netapp.models

DEFAULT_SIZE = 4398046511104


def create_pool(
    client,
    rg=setup.TEST_RG,
    acc_name=setup.TEST_ACC_1,
    pool_name=setup.TEST_POOL_1,
    location=setup.LOCATION,
    pool_only=False,
):
    if not pool_only:
        create_account(client, rg, acc_name, location)
    print("Creating pool {0} in NetApp Account {1}".format(pool_name, acc_name))
    pool_body = CapacityPool(SERVICE_LEVEL=setup.SERVICE_LEVEL, size=DEFAULT_SIZE, location=location)
    pool = client.pools.begin_create_or_update(rg, acc_name, pool_name, pool_body).result()
    wait_for_pool(client, rg, acc_name, pool_name)
    print("\tDone creating pool {0} in NetApp Account {1}".format(pool_name, acc_name))
    return pool


def wait_for_pool(client, rg, account_name, pool_name):
    # a work around for the async nature of certain ARM processes
    retry = 0
    while retry < 60:
        pool = client.pools.get(rg, account_name, pool_name)
        if pool.provisioning_state == "Succeeded":
            break
        if setup.LIVE:
            time.sleep(3)
        retry += 1
    if retry == 60:
        raise Exception("Timeout when waiting for pool")


def wait_for_no_pool(client, rg, acc_name, pool_name):
    # a workaround for the async nature of certain ARM processes
    retry = 0
    while retry < 100:
        try:
            client.pools.get(rg, acc_name, pool_name)
        except:
            # not found is an exception case (status code 200 expected)
            # and is actually what we are waiting for
            break
        if setup.LIVE:
            time.sleep(3)
        retry += 1
    if retry == 100:
        raise Exception("Timeout when waiting for no pool")


def delete_pool(client, rg, acc_name, pool_name):
    # nest resources seem to hang around for a little while even
    # when apparently deleted, therefore give it a chance
    print("Deleting pool {0} in NetApp Account {1}".format(pool_name, acc_name))
    retry = 0
    while retry < 3:
        try:
            client.pools.begin_delete(rg, acc_name, pool_name).wait()
            break
        except Exception as e:
            print("failed to delete pool. Retry number: {0}".format(retry))
            print(e)
            retry += 1
            if setup.LIVE:
                time.sleep(10)
    if retry == 3:
        raise Exception("Timeout when deleting pool")
    wait_for_no_pool(client, rg, acc_name, pool_name)
    print("\tDone deleting pool {0} in NetApp Account {1}".format(pool_name, acc_name))


class TestNetAppCapacityPool(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        if self.is_live:
            setup.LIVE = True

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_create_delete_pool(self):
        print("Starting test_create_delete_pool")
        account_name1 = self.get_resource_name(setup.TEST_ACC_1 + "-")
        pool = create_pool(self.client, setup.TEST_RG, account_name1, setup.TEST_POOL_1, setup.LOCATION)
        assert pool.size == DEFAULT_SIZE
        assert pool.name == account_name1 + "/" + setup.TEST_POOL_1

        pool_list = self.client.pools.list(setup.TEST_RG, account_name1)
        assert len(list(pool_list)) == 1

        delete_pool(self.client, setup.TEST_RG, account_name1, setup.TEST_POOL_1)
        pool_list = self.client.pools.list(setup.TEST_RG, account_name1)
        assert len(list(pool_list)) == 0

        delete_account(self.client, setup.TEST_RG, account_name1)

        print("Finished with test_create_delete_pool")

    @recorded_by_proxy
    def test_list_pools(self):
        print("Starting test_list_pools")
        account_name1 = self.get_resource_name(setup.TEST_ACC_1 + "-")
        create_pool(self.client, setup.TEST_RG, account_name1, setup.TEST_POOL_1, setup.LOCATION)
        create_pool(self.client, setup.TEST_RG, account_name1, setup.TEST_POOL_2, setup.LOCATION, pool_only=True)
        pools = [setup.TEST_POOL_1, setup.TEST_POOL_2]

        pool_list = self.client.pools.list(setup.TEST_RG, account_name1)
        assert len(list(pool_list)) == 2
        idx = 0
        for pool in pool_list:
            assert pool.name == pools[idx]
            idx += 1

        delete_pool(self.client, setup.TEST_RG, account_name1, setup.TEST_POOL_1)
        delete_pool(self.client, setup.TEST_RG, account_name1, setup.TEST_POOL_2)
        delete_account(self.client, setup.TEST_RG, account_name1)
        print("Finished with test_list_pools")

    @recorded_by_proxy
    def test_get_pool_by_name(self):
        print("Starting test_get_pool_by_name")
        account_name1 = self.get_resource_name(setup.TEST_ACC_1 + "-")
        create_pool(self.client, setup.TEST_RG, account_name1, setup.TEST_POOL_1, setup.LOCATION)

        pool = self.client.pools.get(setup.TEST_RG, account_name1, setup.TEST_POOL_1)
        assert pool.name == account_name1 + "/" + setup.TEST_POOL_1

        delete_pool(self.client, setup.TEST_RG, account_name1, setup.TEST_POOL_1)
        delete_account(self.client, setup.TEST_RG, account_name1)
        print("Finished with test_get_pool_by_name")

    @recorded_by_proxy
    def test_update_pool(self):
        print("Starting test_update_pool")
        account_name1 = self.get_resource_name(setup.TEST_ACC_1 + "-")
        pool = create_pool(self.client, setup.TEST_RG, account_name1, setup.TEST_POOL_1)
        assert pool.qos_type == "Auto"

        pool_body = CapacityPoolPatch(qos_type="Manual", size=DEFAULT_SIZE, location=setup.LOCATION)
        pool = self.client.pools.begin_create_or_update(
            setup.TEST_RG, account_name1, setup.TEST_POOL_1, pool_body
        ).result()
        assert pool.qos_type == "Manual"

        delete_pool(self.client, setup.TEST_RG, account_name1, setup.TEST_POOL_1)
        delete_account(self.client, setup.TEST_RG, account_name1)
        print("Finished with test_update_pool")

    @recorded_by_proxy
    def test_patch_pool(self):
        print("Starting test_patch_pool")
        account_name1 = self.get_resource_name(setup.TEST_ACC_1 + "-")
        create_pool(self.client, setup.TEST_RG, account_name1, setup.TEST_POOL_1)

        tag = {"Tag2": "Value1"}
        capacity_pool_patch = CapacityPoolPatch(qos_type="Manual", tags=tag)

        print("Updating pool")
        self.client.pools.begin_update(setup.TEST_RG, account_name1, setup.TEST_POOL_1, capacity_pool_patch).result()
        print("Done updating pool")
        pool = self.client.pools.get(setup.TEST_RG, account_name1, setup.TEST_POOL_1)
        assert pool.qos_type == "Manual"
        assert pool.tags["Tag2"] == "Value1"

        delete_pool(self.client, setup.TEST_RG, account_name1, setup.TEST_POOL_1)
        delete_account(self.client, setup.TEST_RG, account_name1)
        print("Finished with test_patch_pool")
