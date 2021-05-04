import json
import time
import unittest
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtTestCase
import azure.mgmt.netapp.models
from azure.mgmt.netapp.models import NetAppAccount, NetAppAccountPatch
from setup import *

accounts = [TEST_ACC_1, TEST_ACC_2]

def create_account(client, rg, acc_name, location=LOCATION, tags=None, active_directories=None):
    account_body = NetAppAccount(location=location, tags=tags, active_directories=active_directories)

    account = client.accounts.create_or_update(
        account_body,
        rg,
        acc_name
    ).result()

    return account

def wait_for_no_account(client, rg, acc_name, live=False):
    # a workaround for the async nature of certain ARM processes
    co=0
    while co<5:
        co += 1
        if live:
            time.sleep(2)
        try:
            account = client.accounts.get(rg, acc_name)
        except:
            # not found is an exception case (status code 200 expected)
            # and is actually what we are waiting for
            break

def delete_account(client, rg, acc_name, live=False):
    client.accounts.delete(rg, acc_name).wait()
    wait_for_no_account(client, rg, acc_name, live)


@unittest.skip("skip test")
class NetAppAccountTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.AzureNetAppFilesManagementClient)

    def test_create_delete_account(self):
        account = create_account(self.client, TEST_RG, TEST_ACC_1)
        self.assertEqual(account.name, TEST_ACC_1)

        account_list = self.client.accounts.list(TEST_RG)
        self.assertEqual(len(list(account_list)), 1)

        delete_account(self.client, TEST_RG, TEST_ACC_1)
        account_list = self.client.accounts.list(TEST_RG)
        self.assertEqual(len(list(account_list)), 0)

    def test_list_accounts(self):
        account = create_account(self.client, TEST_RG, TEST_ACC_1)
        account = create_account(self.client, TEST_RG, TEST_ACC_2)

        account_list = self.client.accounts.list(TEST_RG)
        self.assertEqual(len(list(account_list)), 2)
        idx = 0
        for account in account_list:
            self.assertEqual(account.name, accounts[idx])
            idx += 1

        delete_account(self.client, TEST_RG, TEST_ACC_1)
        delete_account(self.client, TEST_RG, TEST_ACC_2)

    def test_get_account_by_name(self):
        create_account(self.client, TEST_RG, TEST_ACC_1)

        account = self.client.accounts.get(TEST_RG, TEST_ACC_1)
        self.assertEqual(account.name, TEST_ACC_1)

        delete_account(self.client, TEST_RG, TEST_ACC_1)

    def test_patch_account(self):
        create_account(self.client, TEST_RG, TEST_ACC_1)

        tag = {'Tag1': 'Value2'}
        netapp_account_patch = NetAppAccountPatch(tags=tag)

        account = self.client.accounts.update(netapp_account_patch, TEST_RG, TEST_ACC_1)
        self.assertTrue(account.tags['Tag1'] == 'Value2')

        delete_account(self.client, TEST_RG, TEST_ACC_1)

