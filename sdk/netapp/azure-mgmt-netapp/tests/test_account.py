import time
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy
import azure.mgmt.netapp.models
from azure.mgmt.netapp.models import NetAppAccount, NetAppAccountPatch
from setup import *

LIVE = False

def create_account(client, rg, acc_name, location=LOCATION, tags=None, active_directories=None):
    account_body = NetAppAccount(location=location, tags=tags, active_directories=active_directories)
    
    print("Creating NetApp Account {0}".format(acc_name))
    account = client.accounts.begin_create_or_update(
        rg,
        acc_name,
        account_body
    ).result()
    wait_for_account(client, rg, acc_name)
    print("\tdone")
    return account

def wait_for_account(client, rg, acc_name):
    # a work around for the async nature of certain ARM processes
    co = 0
    while co < 60:
        account = client.accounts.get(rg, acc_name)
        if account.provisioning_state == "Succeeded":
            break
        co += 1
        if LIVE:
            time.sleep(3)
    print("Retried {0} times".format(co))

def wait_for_no_account(client, rg, acc_name):
    # a workaround for the async nature of certain ARM processes
    co = 0
    while co < 60:
        try:
            client.accounts.get(rg, acc_name)
        except:
            # not found is an exception case (status code 200 expected)
            # and is actually what we are waiting for
            break
        co += 1
        if LIVE:
            time.sleep(3)
    print("Retried {0} times".format(co))

def delete_account(client, rg, acc_name):
    print("Deleting NetApp Account {0}".format(acc_name))
    retry = 0
    while retry < 3:
        try:
            client.accounts.begin_delete(rg, acc_name).wait()
            break
        except Exception as e: 
            print("failed to delete account. Retry number: {0}".format(retry))
            print(e)
            retry += 1
            if LIVE:
                time.sleep(10)

    wait_for_no_account(client, rg, acc_name)

class TestNetAppAccount(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        if self.is_live:
            global LIVE
            LIVE = True

    # Before tests are run live a resource group needs to be created
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_create_delete_account(self):
        print("Starting test_create_delete_account")
        account_name = self.get_resource_name(TEST_ACC_1+"-")
        account_list = self.client.accounts.list(TEST_RG)
        account_list_lenght = len(list(account_list))

        print("create_delete_account {0}".format(account_name))
        account = create_account(self.client, TEST_RG, account_name)
        assert account.name == account_name

        account_list = self.client.accounts.list(TEST_RG)
        assert len(list(account_list)) == account_list_lenght+1

        delete_account(self.client, TEST_RG, account_name)
        account_list = self.client.accounts.list(TEST_RG)
        assert len(list(account_list)) == account_list_lenght
        print("Finished with test_create_delete_account")

    @recorded_by_proxy
    def test_list_accounts(self):
        print("Starting test_list_accounts")
        account_name1 = self.get_resource_name(TEST_ACC_1+"-")
        account_name2 = self.get_resource_name(TEST_ACC_2+"-")
        account_list = self.client.accounts.list(TEST_RG)
        account_list_lenght = len(list(account_list))

        create_account(self.client, TEST_RG, account_name1)
        create_account(self.client, TEST_RG, account_name2)
        accounts = [account_name1, account_name2]

        account_list = self.client.accounts.list(TEST_RG)
        assert len(list(account_list)) == account_list_lenght+2
        idx = 0
        for account in account_list:
            assert account.name == accounts[idx]
            idx += 1

        delete_account(self.client, TEST_RG, account_name1)
        delete_account(self.client, TEST_RG, account_name2)
        print("Finished with test_list_accounts")

    @recorded_by_proxy
    def test_get_account_by_name(self):
        print("Starting test_get_account_by_name")
        account_name1 = self.get_resource_name(TEST_ACC_1+"-")
        create_account(self.client, TEST_RG, account_name1)

        account = self.client.accounts.get(TEST_RG, account_name1)
        assert account.name == account_name1

        delete_account(self.client, TEST_RG, account_name1)
        print("Finished with test_get_account_by_name")

    @recorded_by_proxy
    def test_patch_account(self):
        print("Starting test_patch_account")
        account_name1 = self.get_resource_name(TEST_ACC_1+"-")
        create_account(self.client, TEST_RG, account_name1)

        tag = {'Tag1': 'Value2'}
        netapp_account_patch = NetAppAccountPatch(tags=tag)

        account = self.client.accounts.begin_update(TEST_RG, account_name1, netapp_account_patch).result()
        assert account.tags['Tag1'] == 'Value2'

        delete_account(self.client, TEST_RG, account_name1)
        print("Finished with test_patch_account")
