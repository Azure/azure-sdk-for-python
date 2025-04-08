import time
import pytest
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from azure.mgmt.netapp.models import (
    Volume,
    VolumePatch,
    ReplicationObject,
    VolumePropertiesDataProtection,
    AuthorizeRequest,
    PoolChangeRequest,
    RemotePath,
    PeerClusterForVolumeMigrationRequest,
)
from test_pool import create_pool, delete_pool
from test_account import delete_account
import setup
import azure.mgmt.netapp.models

GIGABYTE = 1024 * 1024 * 1024
SUBSID = "69a75bda-882e-44d5-8431-63421204132a"


def create_volume_body(volume_name, location, rg=setup.TEST_RG, vnet=setup.PERMA_VNET, enable_subvolumes=None):
    default_protocol_type = ["NFSv3"]
    volume_body = Volume(
        location=location,
        usage_threshold=100 * GIGABYTE,
        protocol_types=default_protocol_type,
        creation_token=volume_name,
        enable_subvolumes=enable_subvolumes,
        service_level=setup.SERVICE_LEVEL,
        subnet_id="/subscriptions/"
        + SUBSID
        + "/resourceGroups/"
        + rg
        + "/providers/Microsoft.Network/virtualNetworks/"
        + vnet
        + "/subnets/"
        + setup.PERMA_SUBNET,
        network_features="Standard",
    )

    return volume_body


def create_volume(
    client,
    rg=setup.TEST_RG,
    account_name=setup.TEST_ACC_1,
    pool_name=setup.TEST_POOL_1,
    volume_name=setup.TEST_VOL_1,
    location=setup.LOCATION,
    vnet=setup.PERMA_VNET,
    volume_only=False,
    enable_subvolumes=None,
):
    if not volume_only:
        create_pool(client, rg, account_name, pool_name, location, False)
    print("Creating volume {0} in NetApp Account {1}".format(volume_name, account_name))

    volume_body = create_volume_body(volume_name, location, rg, vnet, enable_subvolumes)
    client.volumes.begin_create_or_update(rg, account_name, pool_name, volume_name, volume_body).result()
    volume = wait_for_volume(client, rg, account_name, pool_name, volume_name)
    print("\tDone creating volume {0} in NetApp Account {1}".format(volume_name, account_name))
    return volume


def create_dp_volume(
    client,
    source_volume,
    rg=setup.TEST_REPL_REMOTE_RG,
    account_name=setup.TEST_ACC_2,
    pool_name=setup.TEST_POOL_2,
    volume_name=setup.TEST_VOL_2,
    location=setup.REMOTE_LOCATION,
    vnet=setup.PERMA_REMOTE_VNET,
    volume_only=False,
):
    if not volume_only:
        create_pool(client, rg, account_name, pool_name, location, False)
    print("Creating DP volume {0} in NetApp Account {1}".format(volume_name, account_name))
    # data protection and replication object
    replication = ReplicationObject(
        endpoint_type="dst", remote_volume_resource_id=source_volume.id, replication_schedule="_10minutely"
    )

    data_protection = VolumePropertiesDataProtection(replication=replication)

    default_protocol_type = ["NFSv3"]

    volume_body = Volume(
        location=location,
        usage_threshold=100 * GIGABYTE,
        protocol_types=default_protocol_type,
        creation_token=volume_name,
        subnet_id="/subscriptions/"
        + SUBSID
        + "/resourceGroups/"
        + rg
        + "/providers/Microsoft.Network/virtualNetworks/"
        + vnet
        + "/subnets/"
        + setup.PERMA_REMOTE_SUBNET,
        volume_type="DataProtection",
        data_protection=data_protection,
    )

    destination_volume = client.volumes.begin_create_or_update(
        rg, account_name, pool_name, volume_name, volume_body
    ).result()
    wait_for_volume(client, rg, account_name, pool_name, volume_name)
    print("\tDone creating DP volume in NetApp Account {0}".format(account_name))
    return destination_volume


def create_migration_volume(
    client,
    rg=setup.TEST_REPL_REMOTE_RG,
    account_name=setup.TEST_ACC_1,
    pool_name=setup.TEST_POOL_1,
    volume_name=setup.TEST_VOL_1,
    location=setup.LOCATION,
    vnet=setup.PERMA_VNET,
    volume_only=False,
):
    if not volume_only:
        create_pool(client, rg, account_name, pool_name, location, False)
    print("Creating Migration volume {0} in NetApp Account {1}".format(volume_name, account_name))
    # data protection and replication object
    replication = ReplicationObject(
        remote_path=RemotePath(
            external_host_name="externalHostName", server_name="serverName", volume_name="volumeName"
        )
    )

    data_protection = VolumePropertiesDataProtection(replication=replication)

    default_protocol_type = ["NFSv3"]

    volume_body = Volume(
        location=location,
        usage_threshold=100 * GIGABYTE,
        protocol_types=default_protocol_type,
        creation_token=volume_name,
        subnet_id="/subscriptions/"
        + SUBSID
        + "/resourceGroups/"
        + rg
        + "/providers/Microsoft.Network/virtualNetworks/"
        + vnet
        + "/subnets/"
        + setup.PERMA_SUBNET,
        volume_type="Migration",
        data_protection=data_protection,
    )

    destination_volume = client.volumes.begin_create_or_update(
        rg, account_name, pool_name, volume_name, volume_body
    ).result()
    wait_for_volume(client, rg, account_name, pool_name, volume_name)
    print("\tDone creating Migration volume in NetApp Account {0}".format(account_name))
    return destination_volume


def get_volume(client, rg, account_name, pool_name, volume_name):
    volume = client.volumes.get(rg, account_name, pool_name, volume_name)
    return volume


def wait_for_no_volume(client, rg, account_name, pool_name, volume_name):
    # a workaround for the async nature of certain ARM processes
    retry = 0
    while retry < 100:
        try:
            vol = get_volume(client, rg, account_name, pool_name, volume_name)
            print("\tgot volume. Still waiting. state = " + vol.provisioning_state)
        except:
            # not found is an exception case (status code 200 expected)
            # but is what we are waiting for
            break
        if setup.LIVE:
            time.sleep(3)
        retry += 1
    if retry == 100:
        raise Exception("Timeout when waiting for no volume")
    print("Retried {0} times".format(retry))


def wait_for_volume(client, rg, account_name, pool_name, volume_name):
    # a work around for the async nature of certain ARM processes
    retry = 0
    while retry < 100:
        volume = get_volume(client, rg, account_name, pool_name, volume_name)
        if volume.provisioning_state == "Succeeded":
            break
        if volume.provisioning_state == "Failed":
            print("\t Wait for volume. Volume is in a failed state.")
            break
        if setup.LIVE:
            time.sleep(3)
        retry += 1
    if retry == 100:
        raise Exception("Timeout when waiting for volume")
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
            if setup.LIVE:
                time.sleep(10)
    if retry == 3:
        raise Exception("Timeout when trying to delete volume")
    wait_for_no_volume(client, rg, account_name, pool_name, volume_name)
    print("\tDone deleting volume {0}".format(volume_name))


def wait_for_replication_status(
    client,
    target_state,
    dp_rg=setup.TEST_REPL_REMOTE_RG,
    dp_account_name=setup.TEST_ACC_2,
    dp_pool_name=setup.TEST_POOL_2,
    dp_volume_name=setup.TEST_VOL_2,
):
    print("Waiting for replication status")
    retry = 0
    while retry < 11:
        replication_status = client.volumes.replication_status(dp_rg, dp_account_name, dp_pool_name, dp_volume_name)
        if replication_status.mirror_state == target_state:
            break
        if setup.LIVE:
            time.sleep(60)
        retry += 1
    if retry == 11:
        raise Exception("Timeout when waiting for replication status")
    print("\tDone waiting for replication status")


def wait_for_succeeded(
    client,
    rg=setup.TEST_RG,
    account_name=setup.TEST_ACC_1,
    pool_name=setup.TEST_POOL_1,
    volume_name=setup.TEST_VOL_1,
    dp_rg=setup.TEST_REPL_REMOTE_RG,
    dp_account_name=setup.TEST_ACC_2,
    dp_pool_name=setup.TEST_POOL_2,
    dp_volume_name=setup.TEST_VOL_2,
    live=False,
):
    print("Waiting for success status on source and dest volume")
    retry = 0
    while retry < 20:
        source_volume = client.volumes.get(rg, account_name, pool_name, volume_name)
        dp_volume = client.volumes.get(dp_rg, dp_account_name, dp_pool_name, dp_volume_name)
        if (source_volume.provisioning_state == "Succeeded") and (dp_volume.provisioning_state == "Succeeded"):
            break
        if setup.LIVE:
            time.sleep(10)
    if retry == 20:
        raise Exception("Timeout when waiting for success status on source and dest volume")
    print("\tDone waiting for success status on source and dest volume")


def create_virtual_network(network_client, group_name, location, network_name, subnet_name):
    print("Create vnet {0}".format(network_name))
    azure_operation_poller = network_client.virtual_networks.begin_create_or_update(
        group_name,
        network_name,
        {"location": location, "address_space": {"address_prefixes": ["10.0.0.0/16"]}},
    )
    result_create = azure_operation_poller.result()
    print("Create subnet {0}".format(subnet_name))
    async_subnet_creation = network_client.subnets.begin_create_or_update(
        group_name,
        network_name,
        subnet_name,
        {
            "address_prefix": "10.0.0.0/24",
            "delegations": [{"service_name": "Microsoft.Netapp/volumes", "name": "netAppVolumes"}],
        },
    )
    subnet_info = async_subnet_creation.result()
    print("\tdone")
    return subnet_info


class TestNetAppVolume(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        if self.is_live:
            setup.LIVE = True
            from azure.mgmt.network import NetworkManagementClient

            self.network_client = self.create_mgmt_client(NetworkManagementClient)

    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_create_delete_list_volume(self):
        ACCOUNT1 = self.get_resource_name(setup.TEST_ACC_1 + "-")
        print("Starting test_create_delete_list_volume")
        try:
            set_bodiless_matcher()
            volume = create_volume(
                self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1, setup.TEST_VOL_1, vnet=setup.PERMA_VNET
            )
            assert volume.name == ACCOUNT1 + "/" + setup.TEST_POOL_1 + "/" + setup.TEST_VOL_1
            # check default export policy and protocol
            assert volume.export_policy.rules[0].nfsv3
            assert not volume.export_policy.rules[0].nfsv41
            assert "0.0.0.0/0" == volume.export_policy.rules[0].allowed_clients
            assert volume.protocol_types[0] == "NFSv3"

            volume_list = self.client.volumes.list(setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1)
            assert len(list(volume_list)) == 1

            delete_volume(self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1, setup.TEST_VOL_1)
            volume_list = self.client.volumes.list(setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1)
            assert len(list(volume_list)) == 0
        finally:
            delete_pool(self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1)
            delete_account(self.client, setup.TEST_RG, ACCOUNT1)

        print("Finished with test_create_delete_list_volume")

    @recorded_by_proxy
    def test_list_volumes(self):
        print("Starting test_list_volumes")
        try:
            ACCOUNT1 = self.get_resource_name(setup.TEST_ACC_1 + "-")
            volumeName1 = self.get_resource_name(setup.TEST_VOL_1 + "-")
            volumeName2 = self.get_resource_name(setup.TEST_VOL_2 + "-")

            set_bodiless_matcher()
            create_volume(
                self.client,
                setup.TEST_RG,
                ACCOUNT1,
                setup.TEST_POOL_1,
                volumeName1,
                setup.LOCATION,
                vnet=setup.PERMA_VNET,
            )
            create_volume(
                self.client,
                setup.TEST_RG,
                ACCOUNT1,
                setup.TEST_POOL_1,
                volumeName2,
                setup.LOCATION,
                vnet=setup.PERMA_VNET,
                volume_only=True,
            )
            volumes = [volumeName1, volumeName2]

            volume_list = self.client.volumes.list(setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1)
            assert len(list(volume_list)) == 2
            idx = 0
            for volume in volume_list:
                assert volume.name == volumes[idx]
                idx += 1
        finally:
            delete_volume(self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1, volumeName1)
            delete_volume(self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1, volumeName2)
            delete_pool(self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1)
            delete_account(self.client, setup.TEST_RG, ACCOUNT1)

        print("Finished with test_list_volumes")

    @recorded_by_proxy
    def test_volume_replication(self):
        set_bodiless_matcher()
        print("Starting test_volume_replication")
        ACCOUNT1 = self.get_resource_name(setup.TEST_ACC_1 + "-b2-")
        ACCOUNT2 = self.get_resource_name(setup.TEST_ACC_2 + "-b2-")
        volumeName1 = self.get_resource_name(setup.TEST_VOL_1 + "-b2-")
        dbVolumeName = self.get_resource_name(setup.TEST_VOL_2 + "-b2-")

        try:
            source_volume = create_volume(
                self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1, volumeName1, vnet=setup.PERMA_VNET
            )
            dp_volume = create_dp_volume(
                self.client,
                source_volume,
                setup.TEST_REPL_REMOTE_RG,
                ACCOUNT2,
                setup.TEST_POOL_2,
                dbVolumeName,
                vnet=setup.PERMA_REMOTE_VNET,
            )

            # sync replication
            print("Syncing replication")
            body = AuthorizeRequest(remote_volume_resource_id=dp_volume.id)
            self.client.volumes.begin_authorize_replication(
                setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1, volumeName1, body
            )
            wait_for_succeeded(
                self.client,
                setup.TEST_RG,
                account_name=ACCOUNT1,
                pool_name=setup.TEST_POOL_1,
                volume_name=volumeName1,
                dp_account_name=ACCOUNT2,
                dp_pool_name=setup.TEST_POOL_2,
                dp_volume_name=dbVolumeName,
            )
            wait_for_replication_status(
                self.client,
                "Mirrored",
                dp_account_name=ACCOUNT2,
                dp_pool_name=setup.TEST_POOL_2,
                dp_volume_name=dbVolumeName,
            )

            # list replications
            replications = self.client.volumes.list_replications(
                setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1, volumeName1
            )
            assert len(list(replications)) == 1

            # break replication
            print("Breaking replication")
            self.client.volumes.begin_break_replication(
                setup.TEST_REPL_REMOTE_RG, ACCOUNT2, setup.TEST_POOL_2, dbVolumeName
            )
            wait_for_replication_status(
                self.client,
                "Mirrored",
                dp_account_name=ACCOUNT2,
                dp_pool_name=setup.TEST_POOL_2,
                dp_volume_name=dbVolumeName,
            )
            wait_for_succeeded(
                self.client,
                setup.TEST_RG,
                account_name=ACCOUNT1,
                pool_name=setup.TEST_POOL_1,
                volume_name=volumeName1,
                dp_account_name=ACCOUNT2,
                dp_pool_name=setup.TEST_POOL_2,
                dp_volume_name=dbVolumeName,
            )

            # resync
            print("Resyncing replication")
            self.client.volumes.begin_resync_replication(
                setup.TEST_REPL_REMOTE_RG, ACCOUNT2, setup.TEST_POOL_2, dbVolumeName
            )
            wait_for_replication_status(
                self.client,
                "Mirrored",
                dp_account_name=ACCOUNT2,
                dp_pool_name=setup.TEST_POOL_2,
                dp_volume_name=dbVolumeName,
            )
            wait_for_succeeded(
                self.client,
                setup.TEST_RG,
                account_name=ACCOUNT1,
                pool_name=setup.TEST_POOL_1,
                volume_name=volumeName1,
                dp_account_name=ACCOUNT2,
                dp_pool_name=setup.TEST_POOL_2,
                dp_volume_name=dbVolumeName,
            )

            # break again
            print("Breaking replication again")
            self.client.volumes.begin_break_replication(
                setup.TEST_REPL_REMOTE_RG, ACCOUNT2, setup.TEST_POOL_2, dbVolumeName
            )
            wait_for_replication_status(
                self.client,
                "Mirrored",
                dp_account_name=ACCOUNT2,
                dp_pool_name=setup.TEST_POOL_2,
                dp_volume_name=dbVolumeName,
            )
            wait_for_succeeded(
                self.client,
                setup.TEST_RG,
                account_name=ACCOUNT1,
                pool_name=setup.TEST_POOL_1,
                volume_name=volumeName1,
                dp_account_name=ACCOUNT2,
                dp_pool_name=setup.TEST_POOL_2,
                dp_volume_name=dbVolumeName,
            )

            # delete the data protection object
            #  - initiate delete replication on destination, this then releases on source, both resulting in object deletion
            print("Deleting replication")
            self.client.volumes.begin_delete_replication(
                setup.TEST_REPL_REMOTE_RG, ACCOUNT2, setup.TEST_POOL_2, dbVolumeName
            )

            print("Making sure no replication is found replication")
            retry = 0
            while retry < 10:
                try:
                    self.client.volumes.replication_status(
                        setup.TEST_REPL_REMOTE_RG, ACCOUNT2, setup.TEST_POOL_2, dbVolumeName
                    )
                except:
                    # an exception means the replication was not found
                    # i.e. it has been deleted
                    # ok without checking it could have been for another reason
                    # but then the delete below will fail
                    break

                if setup.LIVE:
                    time.sleep(10)
                retry += 1
            if retry == 10:
                raise Exception("Timeout when making sure no replication is found replication")

            # seems the volumes are not always in a terminal state here so check again
            # and ensure the replication objects are removed
            # python isn't good at do-while loops but loop until we get volumes in succeeded state
            print("Checking if volumes are in succeeded state and have no replication")
            retry = 0
            while retry < 10:
                source_volume = self.client.volumes.get(setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1, volumeName1)
                dp_volume = self.client.volumes.get(
                    setup.TEST_REPL_REMOTE_RG, ACCOUNT2, setup.TEST_POOL_2, dbVolumeName
                )
                if (
                    (source_volume.provisioning_state == "Succeeded")
                    and (dp_volume.provisioning_state == "Succeeded")
                    and (source_volume.data_protection.replication is None)
                    and (dp_volume.data_protection.replication is None)
                ):
                    break
                if setup.LIVE:
                    time.sleep(10)
            if retry == 10:
                raise Exception("Timeout when checking if volumes are in succeeded state and have no replication")

            # now proceed with the delete of the volumes and tidy up resources
        except:
            if setup.LIVE:
                time.sleep(10)
            self.client.volumes.begin_break_replication(
                setup.TEST_REPL_REMOTE_RG, ACCOUNT2, setup.TEST_POOL_2, dbVolumeName
            )
            if setup.LIVE:
                time.sleep(10)
            self.client.volumes.begin_delete_replication(
                setup.TEST_REPL_REMOTE_RG, ACCOUNT2, setup.TEST_POOL_2, dbVolumeName
            )
        finally:
            # delete destination volume
            delete_volume(self.client, setup.TEST_REPL_REMOTE_RG, ACCOUNT2, setup.TEST_POOL_2, dbVolumeName)
            delete_pool(self.client, setup.TEST_REPL_REMOTE_RG, ACCOUNT2, setup.TEST_POOL_2)
            delete_account(self.client, setup.TEST_REPL_REMOTE_RG, ACCOUNT2)

            # delete source volume
            delete_volume(self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1, volumeName1)
            delete_pool(self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1)
            delete_account(self.client, setup.TEST_RG, ACCOUNT1)

        print("Finished with test_volume_replication")

    @recorded_by_proxy
    def test_get_volume_by_name(self):
        set_bodiless_matcher()
        print("Starting test_get_volume_by_name")
        try:
            volumeName1 = self.get_resource_name(setup.TEST_VOL_1 + "-")

            create_volume(
                self.client,
                setup.TEST_RG,
                setup.PERMA_ACCOUNT,
                setup.PERMA_POOL,
                volumeName1,
                setup.LOCATION,
                vnet=setup.PERMA_VNET,
                volume_only=True,
            )

            volume = self.client.volumes.get(setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1)
            assert volume.name == setup.PERMA_ACCOUNT + "/" + setup.PERMA_POOL + "/" + volumeName1
        finally:
            delete_volume(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1)

        print("Finished with test_get_volume_by_name")

    @recorded_by_proxy
    def test_update_volume(self):
        set_bodiless_matcher()
        print("Starting test_update_volume")
        try:
            volumeName1 = self.get_resource_name(setup.TEST_VOL_1 + "-")

            volume = create_volume(
                self.client,
                setup.TEST_RG,
                setup.PERMA_ACCOUNT,
                setup.PERMA_POOL,
                volumeName1,
                setup.LOCATION,
                vnet=setup.PERMA_VNET,
                volume_only=True,
            )
            assert "Premium" == volume.service_level
            assert 100 * GIGABYTE == volume.usage_threshold

            volume_body = Volume(
                usage_threshold=200 * GIGABYTE,
                creation_token=volumeName1,
                SERVICE_LEVEL="Premium",  # cannot differ from pool
                location=setup.LOCATION,
                subnet_id="/subscriptions/"
                + SUBSID
                + "/resourceGroups/"
                + setup.TEST_RG
                + "/providers/Microsoft.Network/virtualNetworks/"
                + setup.PERMA_VNET
                + "/subnets/"
                + setup.PERMA_SUBNET,
                network_features="Standard",
            )

            volume = self.client.volumes.begin_create_or_update(
                setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1, volume_body
            ).result()
            assert "Premium" == volume.service_level  # unchanged
            assert 200 * GIGABYTE == volume.usage_threshold
        finally:
            delete_volume(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1)

        print("Finished with test_update_volume")

    @recorded_by_proxy
    def test_patch_volume(self):
        set_bodiless_matcher()
        print("Starting test_patch_volume")
        volumeName1 = self.get_resource_name(setup.TEST_VOL_1 + "-")
        try:
            volume = create_volume(
                self.client,
                setup.TEST_RG,
                setup.PERMA_ACCOUNT,
                setup.PERMA_POOL,
                volumeName1,
                setup.LOCATION,
                vnet=setup.PERMA_VNET,
            )
            assert "Premium" == volume.service_level
            assert 100 * GIGABYTE == volume.usage_threshold

            volume_patch = VolumePatch(usage_threshold=200 * GIGABYTE)
            volume = self.client.volumes.begin_update(
                setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1, volume_patch
            ).result()
            assert "Premium" == volume.service_level
            assert 200 * GIGABYTE == volume.usage_threshold
        finally:
            delete_volume(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1)
        print("Finished with test_patch_volume")

    @recorded_by_proxy
    def test_pool_change(self):
        set_bodiless_matcher()
        print("Starting test_pool_change")
        try:
            volumeName1 = self.get_resource_name(setup.TEST_VOL_1 + "-")

            volume = create_volume(
                self.client,
                setup.TEST_RG,
                setup.PERMA_ACCOUNT,
                setup.PERMA_POOL,
                volumeName1,
                setup.LOCATION,
                vnet=setup.PERMA_VNET,
                volume_only=True,
            )
            pool2 = create_pool(
                self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.TEST_POOL_2, setup.LOCATION, pool_only=True
            )

            body = PoolChangeRequest(new_pool_resource_id=pool2.id)
            self.client.volumes.begin_pool_change(
                setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1, body
            ).wait()
            wait_for_volume(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.TEST_POOL_2, volumeName1)
            volume = self.client.volumes.get(setup.TEST_RG, setup.PERMA_ACCOUNT, setup.TEST_POOL_2, volumeName1)
            assert volume.name == setup.PERMA_ACCOUNT + "/" + setup.TEST_POOL_2 + "/" + volumeName1

            volume_list = self.client.volumes.list(setup.TEST_RG, setup.PERMA_ACCOUNT, setup.TEST_POOL_2)
            assert len(list(volume_list)) == 1
        finally:
            delete_volume(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.TEST_POOL_2, volumeName1)
            delete_pool(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.TEST_POOL_2)
        print("Finished with test_pool_change")

    @recorded_by_proxy
    def test_begin_populate_availability_zone(self):
        set_bodiless_matcher()
        print("Starting begin_populate_availability_zone")

        volume = self.client.volumes.begin_populate_availability_zone(
            setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, setup.PERMA_VOLUME
        ).result()
        assert len(list(volume.zones)) > 0

        print("Finished with begin_populate_availability_zone")

    @pytest.mark.skip(reason="Skipping this test for service side issue re-enable when fixed")
    @recorded_by_proxy
    def test_external_migration_volume_fails(self):
        set_bodiless_matcher()
        print("Starting test_volume_replication")
        volumeName1 = self.get_resource_name(setup.TEST_VOL_1 + "-m2-")

        try:
            migration_volume = create_migration_volume(
                self.client,
                setup.TEST_RG,
                setup.PERMA_ACCOUNT,
                setup.PERMA_POOL,
                volumeName1,
                vnet=setup.PERMA_VNET,
                volume_only=True,
            )

            # peer external replication
            print("Peer external replication")
            body = PeerClusterForVolumeMigrationRequest(
                peer_ip_addresses=["0.0.0.1", "0.0.0.2", "0.0.0.3", "0.0.0.4", "0.0.0.5"]
            )
            try:
                self.client.volumes.begin_peer_external_cluster(
                    setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1, body
                )
            except Exception as e:
                assert str(e).startswith("(Something unexpected occurred)")

            try:
                self.client.volumes.begin_authorize_external_replication(
                    setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1
                )
            except Exception as e:  # ExternalClusterPeerMissing
                assert str(e).startswith("(Cluster peer targeting)")

            try:
                self.client.volumes.begin_perform_replication_transfer(
                    setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1
                )
            except Exception as e:  # VolumeReplicationHasNotBeenCreated
                assert str(e).startswith(
                    "(This operation cannot be performed since the replication setup has not been completed)"
                )

            try:
                self.client.volumes.begin_finalize_relocation(
                    setup.TEST_RG, PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1
                )
            except Exception as e:  # VolumeReplicationMissingFor
                assert str(e).startswith("(Volume Replication was not found for volume:)")

            # now proceed with the delete of the volumes and tidy up resources
        finally:
            # delete migration volume
            delete_volume(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1)

        print("Finished with external_migration_volume_fails")
