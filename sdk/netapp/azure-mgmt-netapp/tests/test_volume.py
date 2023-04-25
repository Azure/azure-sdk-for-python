import time
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from azure.mgmt.netapp.models import Volume, VolumePatch, ReplicationObject, VolumePropertiesDataProtection, AuthorizeRequest, PoolChangeRequest
from test_pool import create_pool, delete_pool
from test_account import delete_account
from setup import *
import azure.mgmt.netapp.models

GIGABYTE = 1024 * 1024 * 1024
SUBSID = '69a75bda-882e-44d5-8431-63421204132a'
LIVE = False

def create_volume_body(volume_name, location, rg=TEST_RG, vnet=PERMA_VNET, enable_subvolumes=None):
    default_protocol_type = ["NFSv3"]    
    volume_body = Volume(
        location=location,
        usage_threshold=100 * GIGABYTE,
        protocol_types=default_protocol_type,
        creation_token=volume_name,
        enable_subvolumes=enable_subvolumes,
        service_level=SERVICE_LEVEL,
        subnet_id="/subscriptions/" + SUBSID + "/resourceGroups/" + rg + "/providers/Microsoft.Network/virtualNetworks/"
                  + vnet + "/subnets/" + PERMA_SUBNET,
        network_features="Standard"
    )

    return volume_body


def create_volume(client, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1, volume_name=TEST_VOL_1,
                  location=LOCATION, vnet=PERMA_VNET, volume_only=False, enable_subvolumes=None):    
    if not volume_only:
        create_pool(
            client,
            rg,
            account_name,
            pool_name,
            location,
            False)
    print("Creating volume {0} in NetApp Account {1}".format(volume_name, account_name))

    volume_body = create_volume_body(volume_name, location, rg, vnet, enable_subvolumes)
    client.volumes.begin_create_or_update(
        rg,
        account_name,
        pool_name,
        volume_name,
        volume_body
    ).result()
    volume = wait_for_volume(client, rg, account_name, pool_name, volume_name)
    print("\tdone")
    return volume


def create_dp_volume(client, source_volume, rg=TEST_REPL_REMOTE_RG, account_name=TEST_ACC_2, pool_name=TEST_POOL_2,
                     volume_name=TEST_VOL_2, location=REMOTE_LOCATION, vnet=PERMA_REMOTE_VNET, volume_only=False):    
    if not volume_only:
        create_pool(
            client,
            rg,
            account_name,
            pool_name,
            location,
            False)
    print("Creating DP volume in NetApp Account {0}".format(account_name))
    # data protection and replication object
    replication = ReplicationObject(
        endpoint_type="dst",
        remote_volume_resource_id=source_volume.id,
        replication_schedule="_10minutely"
    )

    data_protection = VolumePropertiesDataProtection(
        replication=replication
    )

    default_protocol_type = ["NFSv3"]

    volume_body = Volume(
        location=location,
        usage_threshold=100 * GIGABYTE,
        protocol_types=default_protocol_type,
        creation_token=volume_name,
        subnet_id="/subscriptions/" + SUBSID + "/resourceGroups/" + rg + "/providers/Microsoft.Network/virtualNetworks/"
                  + PERMA_REMOTE_VNET + "/subnets/" + PERMA_REMOTE_SUBNET,
        volume_type="DataProtection",
        data_protection=data_protection
    )

    destination_volume = client.volumes.begin_create_or_update(
        rg,
        account_name,
        pool_name,
        volume_name,
        volume_body
    ).result()
    wait_for_volume(client, rg, account_name, pool_name, volume_name)
    print("\tdone")
    return destination_volume


def get_volume(client, rg, account_name, pool_name, volume_name):
    volume = client.volumes.get(rg, account_name, pool_name, volume_name)
    return volume


def wait_for_no_volume(client, rg, account_name, pool_name, volume_name):
    # a workaround for the async nature of certain ARM processes
    co = 0
    while co < 100:
        try:
            vol = get_volume(client, rg, account_name, pool_name, volume_name)
            print("\tgot volume. Still waiting. state = " + vol.provisioning_state)
        except:
            # not found is an exception case (status code 200 expected)
            # but is what we are waiting for
            break
        if LIVE:
            time.sleep(3)
        co += 1
    print("Retried {0} times".format(co))

def wait_for_volume(client, rg, account_name, pool_name, volume_name):
    # a work around for the async nature of certain ARM processes
    co = 0
    while co < 100:
        volume = get_volume(client, rg, account_name, pool_name, volume_name)
        if volume.provisioning_state == "Succeeded":
            break
        if volume.provisioning_state == "Failed":
            print("\t Wait for volume. Volume is in a failed state.")
            break
        if LIVE:
            time.sleep(3)
        co += 1
    print("Retried {0} times".format(co))
    return volume

def delete_volume(client, rg, account_name, pool_name, volume_name):
    print("Delete volume {0}".format(volume_name))
    retry = 0
    while retry < 3:
        try:
            client.volumes.begin_delete(rg, account_name, pool_name, volume_name).wait()
            break
        except Exception as e: 
            print("failed to delete volume. Retry number: {0}".format(retry))
            print(e)
            retry += 1
            if LIVE:
                time.sleep(10)
    wait_for_no_volume(client, rg, account_name, pool_name, volume_name)
    print("\tdone")

def wait_for_replication_status(client, target_state, dp_rg=TEST_REPL_REMOTE_RG, dp_account_name=TEST_ACC_2, dp_pool_name=TEST_POOL_2, dp_volume_name=TEST_VOL_2):
    # python isn't good at do-while loops but loop until we get the target state
    print("Waiting for replication status")
    while True:
        replication_status = client.volumes.replication_status(dp_rg, dp_account_name, dp_pool_name, dp_volume_name)
        if replication_status.mirror_state == target_state:
            break
        if LIVE:
            time.sleep(3)
    print("\tdone")

def wait_for_succeeded(client, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1, volume_name=TEST_VOL_1, dp_rg=TEST_REPL_REMOTE_RG, dp_account_name=TEST_ACC_2, dp_pool_name=TEST_POOL_2, dp_volume_name=TEST_VOL_2,live=False):
    # python isn't good at do-while loops but loop until we get volumes in succeeded state
    print("Waiting for success status on source and dest volume")
    while True:
        source_volume = client.volumes.get(rg, account_name, pool_name, volume_name)
        dp_volume = client.volumes.get(dp_rg, dp_account_name, dp_pool_name, dp_volume_name)
        if (source_volume.provisioning_state == "Succeeded") and (dp_volume.provisioning_state == "Succeeded"):
            break
        if LIVE:
            time.sleep(5)
    print("\tdone")

def create_virtual_network(network_client, group_name, location, network_name, subnet_name):
    print("Create vnet {0}".format(network_name))    
    azure_operation_poller = network_client.virtual_networks.begin_create_or_update(
        group_name,
        network_name,
        {
            'location': location,
            'address_space': {
                'address_prefixes': ['10.0.0.0/16']
            }
        },
    )
    result_create = azure_operation_poller.result()
    print("Create subnet {0}".format(subnet_name))    
    async_subnet_creation = network_client.subnets.begin_create_or_update(
        group_name,
        network_name,
        subnet_name,
        {
            'address_prefix': '10.0.0.0/24',
            'delegations': [
                {
                    "service_name": "Microsoft.Netapp/volumes",
                    "name": "netAppVolumes"
                }
            ]
        }
    )
    subnet_info = async_subnet_creation.result()
    print("\tdone")
    return subnet_info

class TestNetAppVolume(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        if self.is_live:
            global LIVE
            LIVE = True
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(NetworkManagementClient)             

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_create_delete_list_volume(self):
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        print("Starting test_create_delete_list_volume")
        set_bodiless_matcher()
        volume = create_volume(
            self.client,
            TEST_RG,
            ACCOUNT1,
            TEST_POOL_1,
            TEST_VOL_1,
            vnet=PERMA_VNET
        )
        assert volume.name == ACCOUNT1 + '/' + TEST_POOL_1 + '/' + TEST_VOL_1
        # check default export policy and protocol
        assert volume.export_policy.rules[0].nfsv3
        assert not volume.export_policy.rules[0].nfsv41
        assert "0.0.0.0/0" == volume.export_policy.rules[0].allowed_clients
        assert volume.protocol_types[0] == "NFSv3"

        volume_list = self.client.volumes.list(TEST_RG, ACCOUNT1, TEST_POOL_1)
        assert len(list(volume_list)) == 1

        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, TEST_VOL_1)
        volume_list = self.client.volumes.list(TEST_RG, ACCOUNT1, TEST_POOL_1)
        assert len(list(volume_list)) == 0

        delete_pool(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1)
        delete_account(self.client, TEST_RG, ACCOUNT1)

        print("Finished with test_create_delete_list_volume")

    @recorded_by_proxy
    def test_list_volumes(self):
        print("Starting test_list_volumes")
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        volumeName2 = self.get_resource_name(TEST_VOL_2+"-")
        
        set_bodiless_matcher()
        create_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, LOCATION, vnet=PERMA_VNET)
        create_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName2, LOCATION, vnet=PERMA_VNET, volume_only=True)
        volumes = [volumeName1, volumeName2]

        volume_list = self.client.volumes.list(TEST_RG, ACCOUNT1, TEST_POOL_1)
        assert len(list(volume_list)) == 2
        idx = 0
        for volume in volume_list:
            assert volume.name == volumes[idx]
            idx += 1

        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1)
        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName2)
        delete_pool(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1)
        delete_account(self.client, TEST_RG, ACCOUNT1)
        
        print("Finished with test_list_volumes")

    @recorded_by_proxy
    def test_volume_replication(self):
        set_bodiless_matcher()
        print("Starting test_volume_replication")
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-b2-")
        ACCOUNT2 = self.get_resource_name(TEST_ACC_2+"-b2-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-b2-")        
        dbVolumeName = self.get_resource_name(TEST_VOL_2+"-b2-")
        
        source_volume = create_volume(
            self.client,
            TEST_RG,
            ACCOUNT1,
            TEST_POOL_1,
            volumeName1,
            vnet=PERMA_VNET)
        dp_volume = create_dp_volume(
            self.client,
            source_volume,
            TEST_REPL_REMOTE_RG,
            ACCOUNT2,
            TEST_POOL_2,
            dbVolumeName,
            vnet=PERMA_REMOTE_VNET)

        # sync replication
        print("Syncing replication")
        body = AuthorizeRequest(remote_volume_resource_id=dp_volume.id)
        self.client.volumes.begin_authorize_replication(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, body)
        wait_for_succeeded(self.client, TEST_RG, account_name=ACCOUNT1, pool_name=TEST_POOL_1, volume_name=volumeName1, dp_account_name=ACCOUNT2,dp_pool_name=TEST_POOL_2, dp_volume_name=dbVolumeName)
        wait_for_replication_status(self.client, "Mirrored", dp_account_name=ACCOUNT2,dp_pool_name=TEST_POOL_2, dp_volume_name=dbVolumeName)

        # list replications
        replications = self.client.volumes.list_replications(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1)
        assert len(list(replications)) == 1

        # break replication
        print("Breaking replication")
        self.client.volumes.begin_break_replication(TEST_REPL_REMOTE_RG, ACCOUNT2, TEST_POOL_2, dbVolumeName)
        wait_for_replication_status(self.client, "Mirrored", dp_account_name=ACCOUNT2,dp_pool_name=TEST_POOL_2, dp_volume_name=dbVolumeName)
        wait_for_succeeded(self.client, TEST_RG, account_name=ACCOUNT1, pool_name=TEST_POOL_1, volume_name=volumeName1, dp_account_name=ACCOUNT2,dp_pool_name=TEST_POOL_2, dp_volume_name=dbVolumeName)

        # resync
        print("Resyncing replication")
        self.client.volumes.begin_resync_replication(TEST_REPL_REMOTE_RG, ACCOUNT2, TEST_POOL_2, dbVolumeName)
        wait_for_replication_status(self.client, "Mirrored", dp_account_name=ACCOUNT2,dp_pool_name=TEST_POOL_2, dp_volume_name=dbVolumeName)
        wait_for_succeeded(self.client, TEST_RG, account_name=ACCOUNT1, pool_name=TEST_POOL_1, volume_name=volumeName1, dp_account_name=ACCOUNT2,dp_pool_name=TEST_POOL_2, dp_volume_name=dbVolumeName)

        # break again
        print("Breaking replication again")
        self.client.volumes.begin_break_replication(TEST_REPL_REMOTE_RG, ACCOUNT2, TEST_POOL_2, dbVolumeName)
        wait_for_replication_status(self.client, "Mirrored", dp_account_name=ACCOUNT2,dp_pool_name=TEST_POOL_2, dp_volume_name=dbVolumeName)
        wait_for_succeeded(self.client, TEST_RG, account_name=ACCOUNT1, pool_name=TEST_POOL_1, volume_name=volumeName1, dp_account_name=ACCOUNT2,dp_pool_name=TEST_POOL_2, dp_volume_name=dbVolumeName)

        # delete the data protection object
        #  - initiate delete replication on destination, this then releases on source, both resulting in object deletion
        print("Deleting replication")
        self.client.volumes.begin_delete_replication(TEST_REPL_REMOTE_RG, ACCOUNT2, TEST_POOL_2, dbVolumeName)

        print("Making sure no replication is found replication")
        replication_found = True  # because it was previously present
        while replication_found:
            try:
                self.client.volumes.replication_status(TEST_REPL_REMOTE_RG, ACCOUNT2, TEST_POOL_2, dbVolumeName)
            except:
                # an exception means the replication was not found
                # i.e. it has been deleted
                # ok without checking it could have been for another reason
                # but then the delete below will fail
                replication_found = False

            if LIVE:
                time.sleep(3)

        # seems the volumes are not always in a terminal state here so check again
        # and ensure the replication objects are removed
        # python isn't good at do-while loops but loop until we get volumes in succeeded state
        print("Checking if volumes are in succeeded state and have no replication")
        while True:
            source_volume = self.client.volumes.get(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1)
            dp_volume = self.client.volumes.get(TEST_REPL_REMOTE_RG, ACCOUNT2, TEST_POOL_2, dbVolumeName)
            if (source_volume.provisioning_state == "Succeeded") and (dp_volume.provisioning_state == "Succeeded") and \
                    (source_volume.data_protection.replication is None) and \
                    (dp_volume.data_protection.replication is None):
                break
            if LIVE:
                time.sleep(1)

        # now proceed with the delete of the volumes and tidy up resources

        # delete destination volume
        delete_volume(self.client, TEST_REPL_REMOTE_RG, ACCOUNT2, TEST_POOL_2, dbVolumeName)
        delete_pool(self.client, TEST_REPL_REMOTE_RG, ACCOUNT2, TEST_POOL_2)
        delete_account(self.client, TEST_REPL_REMOTE_RG, ACCOUNT2)

        # delete source volume
        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1)
        delete_pool(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1)
        delete_account(self.client, TEST_RG, ACCOUNT1)

        print("Finished with test_volume_replication")

    @recorded_by_proxy
    def test_get_volume_by_name(self):
        set_bodiless_matcher()
        print("Starting test_get_volume_by_name")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")

        create_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, LOCATION, vnet=PERMA_VNET, volume_only=True)

        volume = self.client.volumes.get(TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1)
        assert volume.name == PERMA_ACCOUNT + '/' + PERMA_POOL + '/' + volumeName1

        delete_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1)
        
        print("Finished with test_get_volume_by_name")

    @recorded_by_proxy
    def test_update_volume(self):
        set_bodiless_matcher()
        print("Starting test_update_volume")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
                      
        volume = create_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, LOCATION, vnet=PERMA_VNET, volume_only=True)
        assert "Premium" == volume.service_level
        assert 100 * GIGABYTE == volume.usage_threshold

        volume_body = Volume(
            usage_threshold=200 * GIGABYTE,
            creation_token=volumeName1,
            service_level="Premium",  # cannot differ from pool
            location=LOCATION,
            subnet_id="/subscriptions/" + SUBSID + "/resourceGroups/" + TEST_RG +
                      "/providers/Microsoft.Network/virtualNetworks/" + PERMA_VNET + "/subnets/" + PERMA_SUBNET,
            network_features="Standard"
        )

        volume = self.client.volumes.begin_create_or_update(
            TEST_RG,
            PERMA_ACCOUNT,
            PERMA_POOL,
            volumeName1,
            volume_body
        ).result()
        assert "Premium" == volume.service_level  # unchanged
        assert 200 * GIGABYTE == volume.usage_threshold

        delete_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1)
        
        print("Finished with test_update_volume")

    @recorded_by_proxy
    def test_patch_volume(self):
        set_bodiless_matcher()
        print("Starting test_patch_volume")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")

        volume = create_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, LOCATION, vnet=PERMA_VNET)
        assert "Premium" == volume.service_level
        assert 100 * GIGABYTE == volume.usage_threshold

        volume_patch = VolumePatch(usage_threshold=200 * GIGABYTE)
        volume = self.client.volumes.begin_update(TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, volume_patch).result()
        assert "Premium" == volume.service_level
        assert 200 * GIGABYTE == volume.usage_threshold

        delete_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1)
        print("Finished with test_patch_volume")

    @recorded_by_proxy
    def test_pool_change(self):
        set_bodiless_matcher()
        print("Starting test_pool_change")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
                    
        volume = create_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, LOCATION, vnet=PERMA_VNET, volume_only=True)
        pool2 = create_pool(self.client, TEST_RG, PERMA_ACCOUNT, TEST_POOL_2, LOCATION, pool_only=True)

        body = PoolChangeRequest(new_pool_resource_id=pool2.id)
        self.client.volumes.begin_pool_change(TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, body).wait()
        wait_for_volume(self.client, TEST_RG, PERMA_ACCOUNT, TEST_POOL_2, volumeName1)
        volume = self.client.volumes.get(TEST_RG, PERMA_ACCOUNT, TEST_POOL_2, volumeName1)
        assert volume.name == PERMA_ACCOUNT + "/" + TEST_POOL_2 + "/" + volumeName1

        volume_list = self.client.volumes.list(TEST_RG, PERMA_ACCOUNT, PERMA_POOL)
        assert len(list(volume_list)) == 1

        delete_volume(self.client, TEST_RG, PERMA_ACCOUNT, TEST_POOL_2, volumeName1)
        delete_pool(self.client, TEST_RG, PERMA_ACCOUNT, TEST_POOL_2)
        print("Finished with test_pool_change")