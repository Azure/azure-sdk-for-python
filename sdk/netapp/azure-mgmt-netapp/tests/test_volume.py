import time
import json
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.netapp.models import Volume, VolumePatch
from test_pool import create_pool, delete_pool
from test_account import delete_account
from setup import *
import azure.mgmt.netapp.models

volumes = [TEST_VOL_1, TEST_VOL_2]


def create_volume_body(volume_name, location):
    volume_body = Volume(
        usage_threshold = 100 * GIGABYTE,
        creation_token=volume_name,
        service_level=SERVICE_LEVEL,
        location=location,
        subnet_id = "/subscriptions/" + SUBSID + "/resourceGroups/" + TEST_RG + "/providers/Microsoft.Network/virtualNetworks/" + VNET + "/subnets/default"
    )

    return volume_body

def create_volume(client, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1, volume_name=TEST_VOL_1, location=LOCATION, volume_only=False, live=False):
    if not volume_only:
        pool = create_pool(client)
        if live:
            time.sleep(10)

    volume_body = create_volume_body(volume_name, location)
    volume = client.volumes.create_or_update(
        volume_body,
        rg,
        account_name,
        pool_name,
        volume_name
    ).result()

    return volume

def get_volume(client, rg, account_name, pool_name, volume_name):
    volume = client.volumes.get(rg, account_name, pool_name, volume_name)
    return volume

def wait_for_no_volume(client, rg, account_name, pool_name, volume_name, live=False):
    # a workaround for the async nature of certain ARM processes
    co=0
    while co<10:
        co += 1
        if live:
            time.sleep(5)
        try:
            get_volume(client, rg, account_name, pool_name, volume_name)
        except:
            # not found is an exception case (status code 200 expected)
            # but is what we are waiting for
            break

def wait_for_volume(client, rg, account_name, pool_name, volume_name, live=False):
    # a work around for the async nature of certain ARM processes
    co=0
    while co<10:
        co += 1
        if live:
            time.sleep(5)
        try:
            get_volume(client, rg, account_name, pool_name, volume_name)
            break
        except:
            # not found is an exception case (status code 200 expected)
            # but is what we are waiting for
            pass

def delete_volume(client, rg, account_name, pool_name, volume_name, live=False):
    client.volumes.delete(rg, account_name, pool_name, volume_name).wait()
    wait_for_no_volume(client, rg, account_name, pool_name, volume_name, live)


class NetAppAccountTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.AzureNetAppFilesManagementClient)

    def test_create_delete_list_volume(self):
        volume = create_volume(
            self.client,
            TEST_RG,
            TEST_ACC_1,
            TEST_POOL_1,
            TEST_VOL_1,
            live=self.is_live
        )
        self.assertEqual(volume.name, TEST_ACC_1 + '/' + TEST_POOL_1 + '/' + TEST_VOL_1)

        volume_list = self.client.volumes.list(TEST_RG, TEST_ACC_1, TEST_POOL_1)
        self.assertEqual(len(list(volume_list)), 1)

        self.client.volumes.delete(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1).wait()
        volume_list = self.client.volumes.list(TEST_RG, TEST_ACC_1, TEST_POOL_1)
        self.assertEqual(len(list(volume_list)), 0)

        wait_for_no_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)

    def test_list_volumes(self):
        volume = create_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, LOCATION, live=self.is_live)
        volume = create_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_2, LOCATION, volume_only=True, live=self.is_live)

        volume_list = self.client.volumes.list(TEST_RG, TEST_ACC_1, TEST_POOL_1)
        self.assertEqual(len(list(volume_list)), 2)
        idx = 0
        for volume in volume_list:
            self.assertEqual(volume.name, volumes[idx])
            idx += 1

        self.client.volumes.delete(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1).wait()
        self.client.volumes.delete(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_2).wait()
        for volume in volumes:
            wait_for_no_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, volumes[idx], live=self.is_live)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)

    def test_get_volume_by_name(self):
        volume = create_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, LOCATION, live=self.is_live)

        volume = self.client.volumes.get(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        self.assertEqual(volume.name, TEST_ACC_1 + '/' + TEST_POOL_1 + '/' + TEST_VOL_1)

        self.client.volumes.delete(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1).wait()
        wait_for_no_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, live=self.is_live)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)

    def test_update_volume(self):
        volume = create_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, live=self.is_live)
        self.assertEqual(volume.service_level, "Premium")
        self.assertEqual(volume.usage_threshold, 100 * GIGABYTE)

        volume_body = Volume(
            usage_threshold = 100 * GIGABYTE,
            creation_token=TEST_VOL_1,
            service_level="Standard",
            location=LOCATION,
            subnet_id = "/subscriptions/" + SUBSID + "/resourceGroups/" + TEST_RG + "/providers/Microsoft.Network/virtualNetworks/" + VNET + "/subnets/default"
        )

        volume = self.client.volumes.create_or_update(
            volume_body,
            TEST_RG,
            TEST_ACC_1,
            TEST_POOL_1,
            TEST_VOL_1
        ).result()
        self.assertEqual(volume.service_level, "Standard")

        delete_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, live=self.is_live)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)

    def test_patch_volume(self):
        volume = create_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, live=self.is_live)
        self.assertEqual("Premium", volume.service_level);

        volume_patch = VolumePatch(service_level = "Standard")
        volume = self.client.volumes.update(volume_patch, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        self.assertEqual("Standard", volume.service_level);

        self.client.volumes.delete(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1).wait()
        wait_for_no_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, live=self.is_live)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)

