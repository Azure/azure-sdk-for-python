# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.keyvault.keys import KeyVaultKey, KeyClient
from azure.mgmt.hdinsight import HDInsightManagementClient
from azure.mgmt.hdinsight.models import *
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.msi import ManagedServiceIdentityClient
from azure.mgmt.keyvault.models import SecretPermissions, KeyPermissions, CertificatePermissions, StoragePermissions, \
    Permissions, Sku, SkuName, AccessPolicyEntry, VaultProperties, VaultCreateOrUpdateParameters, Vault
from azure.mgmt.loganalytics import LogAnalyticsManagementClient
from azure.mgmt.loganalytics.models import Workspace
from azure.mgmt.storage.models import Kind
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer, StorageAccountPreparer, FakeStorageAccount
from mgmt_hdinsight_preparers import KeyVaultPreparer

LOCATION = 'North Central US'

# ADLS Gen1 does not support North Central US, use East US 2 instead
ADLS_LOCATION = 'East US 2'

STORAGE_BLOB_SERVICE_ENDPOINT_SUFFIX = '.blob.core.windows.net'

STORAGE_ADLS_FILE_SYSTEM_ENDPOINT_SUFFIX = '.dfs.core.windows.net'

FAKE_WORKSPACE_ID = '1d364e89-bb71-4503-aa3d-a23535aea7bd'


class MgmtHDInsightTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtHDInsightTest, self).setUp()

        # create client
        self.hdinsight_client = self.create_mgmt_client(HDInsightManagementClient)
        self.msi_client = self.create_mgmt_client(ManagedServiceIdentityClient)
        self.vault_mgmt_client = self.create_mgmt_client(KeyVaultManagementClient)

        # sensitive test configs
        self.tenant_id = self.settings.TENANT_ID
        self.adls_account_name = self.settings.HDI_ADLS_ACCOUNT_NAME
        self.adls_client_id = self.settings.HDI_ADLS_CLIENT_ID

        # Non-sensitive test configs
        self.cluster_username = 'admin'
        self.cluster_password = 'Password1!'
        self.ssh_username = 'sshuser'
        self.ssh_password = 'Password1!'
        self.adls_home_mountpoint = '/clusters/hdi'
        self.cert_password = 'password'
        self.cert_content = 'MIIE5TCCAs0CFDGDR+Zz5To67BBDmsF3agvAtdUvMA0GCSqGSIb3DQEBCwUAMC8xCzAJBgNVBAYTAmNuMQ4wDAYDVQQIDAVjaGluYTEQMA4GA1UECgwHenp5dGVzdDAeFw0yMDA0MTYxMDEzNTlaFw0yMTA0MTYxMDEzNTlaMC8xCzAJBgNVBAYTAmNuMQ4wDAYDVQQIDAVjaGluYTEQMA4GA1UECgwHenp5dGVzdDCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAMmvOHmbbD5kIXnvIdEGFPVd3dHe8RFHBKMBSyqVdcwiijPsaQGkx2/PHyD019FTFPDcwo5Wt2rPXdkOm5Em7NiHcYWjZTF/UDZytf+B2pihI1jDz5qUGf65vIGWI5VVtuuXHSGMOZ4RGyM8/3SyMfAy02db6bJnat2RziZJ2F3FSPfMebGYgFn8uxfYKLGQj7mPEqVyGHxcx0KqbH+2jfzBqDjbaQfo7vBsqxvMfG+2G9SAHaiZPBveym4HuyDDtBZ3ChslVHitWUw0qsbPEuR7Jp8NenAqKVrzvixoepAm7vvErRs/olkJFu3OcIusDIOEQcYem30/rSQejQvrXTcdIvD3UPcqApdzrEZvdiCvIr0ys1Ie2OoOwdz391KCIlH3zgGu4Tdg0vJ+RQIYNT8DNK2PUbbw1bENEcwklgkdT2uIjgh6kOIjMCuy6UzAPnWBF8bl9YY3rB5p/EjnGk8BSp/nCEggMVxzfUhUNQJGKo1C85yFl8Olet/jtPZgf8JV9TOJLdNHlzdkidwrcLGJ8SAEsbveF2w5CtobqeDoClrSieK6ANPPLOWplMNFPZWqUaLe45ReExGYlm7Q+hpdnJem7ywWanJTzI1GoVJMr04ZJmsMEmVYhoSqN4yvFfyWM+rDrKdpzBF6ZqknzWxw+T59u+Eu+PrRMOMAWsDJAgMBAAEwDQYJKoZIhvcNAQELBQADggIBAC/5VPkcsb8sH6wpS3LeKViG2Z+XBZ70Q7FUliE4wfLwP5duzN8DN6eJyxS/nTyxohvI6p18MVgZdhjPcvndR1FE8eBsMqZM0D3eDyCYoiB9Ghm1DSxn0AZyk7/aC4nNYLorZouWa1DdCCdOFZegod5I3USXIvUOBDh9eIQQAGCYdANSLkYsyaZgTaKWiBDH0pTVvCOroCJ7NCayibCMc4vdHUQY/UyKSgOZG0Y2M6AgwNI/yC3tyizu/D8OoF7RUb/A4JqvHnqkY2hGF3/GwEBO4eQrCmHFozrA5qZx40bWP4sXGzcmZz/4Nl9TWRWdIKe5Wh3xz6ZMtJ3gPDwt4Vi59ZHcmq187uwYIRvuvGzD4/oI4zeZ80nxhJUQrZdPh3beaA5GhvTS9MM/RGgkXgB+CA61iF0euAb3FEC3MvpjDwDq9DZDiBulAscRn3QnYhxaL2AxMkNgtj6oaHGx+RlepXKqPd11hsdWhKo8X0zcCVrtrz73b6yDQesSP+lDapLuo/74APJVyAuEXM7zGQSt3zTmeE6RTIywB00VpifqL9HmcekllopPuQrBgs0cpgrs6/VjbC6uwIwV9dUrIsP6geLeocS9j6aQmEIr/E/HjvEZ0kI+03Cw+gQqeAlSeKP6ZY9AgQsCFBIBsgORNcn/Aii0QenXC19LeFC0dJYm'
        self.workspace_id = '3741ffb2-a54e-407c-952a-43ab44b57c9d'
        self.primary_key = 'qFmud5LfxcCxWUvWcGMhKDp0v0KuBRLsO/AIddX734W7lzdInsVMsB5ILVoOrF+0fCfk/IYYy5SJ9Q+2v4aihQ=='

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_humboldt_cluster(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-humboldt')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @unittest.skip('(BadRequest) Premium Cluster Tier available only for ESP Clusters.')
    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_humboldt_cluster_with_premium_tier(self, resource_group, location, storage_account,
                                                       storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-premium')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.tier = Tier.premium
        create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_with_empty_extended_parameters(self, resource_group, location, storage_account,
                                                   storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-cluster')
        create_params = ClusterCreateParametersExtended()

        # try to create cluster and ensure it throws
        try:
            create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name,
                                                                        create_params)
            cluster = create_poller.result()
            self.assertTrue(False, 'should not have made it here')
        except Exception:
            pass

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_humboldt_cluster_with_custom_vm_sizes(self, resource_group, location, storage_account,
                                                          storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-customvmsizes')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        headnode = next(item for item in create_params.properties.compute_profile.roles if item.name == 'headnode')
        headnode.hardware_profile = HardwareProfile(vm_size="ExtraLarge")
        zookeepernode = next(
            item for item in create_params.properties.compute_profile.roles if item.name == 'zookeepernode')
        zookeepernode.hardware_profile = HardwareProfile(vm_size="Medium")
        create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_linux_spark_cluster_with_component_version(self, resource_group, location, storage_account,
                                                               storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-sparkcomponentversions')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.cluster_definition.kind = 'Spark'
        create_params.properties.cluster_definition.Component_version = {'Spark': '2.2'}
        create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_kafka_cluster_with_managed_disks(self, resource_group, location, storage_account,
                                                     storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-kafka')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.cluster_definition.kind = 'Kafka'
        workernode = next(item for item in create_params.properties.compute_profile.roles if item.name == 'workernode')
        workernode.data_disks_groups = [
            DataDisksGroups(
                disks_per_node=8
            )
        ]
        create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @unittest.skip('skipping temporarily to unblock azure-keyvault checkin')
    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    @KeyVaultPreparer(name_prefix='hdipy', location=LOCATION, enable_soft_delete=True)
    def test_create_kafka_cluster_with_disk_encryption(self, resource_group, location, storage_account,
                                                       storage_account_key, vault):
        # create managed identities for Azure resources.
        msi_name = self.get_resource_name('hdipyuai')
        msi_principal_id = "00000000-0000-0000-0000-000000000000"
        msi_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/{}/providers/microsoft.managedidentity/userassignedidentities/{}".format(
            resource_group.name, msi_name)
        if self.is_live:
            msi = self.msi_client.user_assigned_identities.create_or_update(resource_group.name, msi_name, location)
            msi_id = msi.id
            msi_principal_id = msi.principal_id

        # add managed identity to vault
        required_permissions = Permissions(
            keys=[KeyPermissions.get, KeyPermissions.wrap_key, KeyPermissions.unwrap_key],
            secrets=[SecretPermissions.get, SecretPermissions.set, SecretPermissions.delete])
        vault.properties.access_policies.append(
            AccessPolicyEntry(tenant_id=self.tenant_id,
                              object_id=msi_principal_id,
                              permissions=required_permissions)
        )
        update_params = VaultCreateOrUpdateParameters(location=location,
                                                      properties=vault.properties)
        vault = self.vault_mgmt_client.vaults.begin_create_or_update(resource_group.name, vault.name,
                                                                     update_params).result()
        self.assertIsNotNone(vault)

        # create keyclient
        key_client_credential = self.settings.get_azure_core_credentials(scope="https://vault.azure.net/.default")
        self.vault_client = KeyClient(vault_url=vault.properties.vault_uri, credential=key_client_credential)

        # create key
        key_name = self.get_resource_name('hdipykey1')
        vault_key = self.vault_client.create_key(key_name, 'RSA')

        # create a new key for test rotate
        new_key_name = self.get_resource_name('hdipykey2')
        new_vault_key = self.vault_client.create_key(new_key_name, 'RSA')

        # create HDInsight cluster with Kafka disk encryption
        rg_name = resource_group.name
        cluster_name = self.get_resource_name('hdisdk-kafka-byok')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.cluster_definition.kind = 'Kafka'
        workernode = next(item for item in create_params.properties.compute_profile.roles if item.name == 'workernode')
        workernode.data_disks_groups = [
            DataDisksGroups(
                disks_per_node=8
            )
        ]
        create_params.identity = ClusterIdentity(
            type=ResourceIdentityType.user_assigned,
            user_assigned_identities={msi_id: ClusterIdentityUserAssignedIdentitiesValue()}
        )
        create_params.properties.disk_encryption_properties = DiskEncryptionProperties(
            vault_uri=vault_key.properties.vault_url,
            key_name=vault_key.name,
            key_version=vault_key.properties.version,
            msi_resource_id=msi_id
        )
        cluster = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params).result()
        self.validate_cluster(cluster_name, create_params, cluster)

        # check disk encryption properties
        self.assertIsNotNone(cluster.properties.disk_encryption_properties)
        self.assertEqual(create_params.properties.disk_encryption_properties.vault_uri,
                         cluster.properties.disk_encryption_properties.vault_uri)
        self.assertEqual(create_params.properties.disk_encryption_properties.key_name,
                         cluster.properties.disk_encryption_properties.key_name)
        self.assertEqual(create_params.properties.disk_encryption_properties.msi_resource_id.lower(),
                         cluster.properties.disk_encryption_properties.msi_resource_id.lower())

        rotate_params = ClusterDiskEncryptionParameters(
            vault_uri=new_vault_key.properties.vault_url,
            key_name=new_vault_key.name,
            key_version=new_vault_key.properties.version
        )

        # rotate cluster key
        self.hdinsight_client.clusters.rotate_disk_encryption_key(rg_name, cluster_name, rotate_params).wait()
        cluster = self.hdinsight_client.clusters.get(rg_name, cluster_name)

        # check disk encryption properties
        self.assertIsNotNone(cluster.properties.disk_encryption_properties)
        self.assertEqual(rotate_params.vault_uri, cluster.properties.disk_encryption_properties.vault_uri)
        self.assertEqual(rotate_params.key_name, cluster.properties.disk_encryption_properties.key_name)
        self.assertEqual(msi_id.lower(), cluster.properties.disk_encryption_properties.msi_resource_id.lower())

    @unittest.skip("There is something wrong in ADLS Gen1 from RP.")
    @ResourceGroupPreparer(name_prefix='hdipy-', location=ADLS_LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=ADLS_LOCATION)
    def test_create_with_adls_gen1(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-adlsgen1')
        create_params = self.get_cluster_create_params_for_adls_gen1(location, cluster_name)

        # Add additional storage account
        create_params.properties.storage_profile.storageaccounts.append(
            StorageAccount(
                name=storage_account.name + STORAGE_BLOB_SERVICE_ENDPOINT_SUFFIX,
                key=storage_account_key,
                container=cluster_name.lower(),
                is_default=False
            )
        )

        cluster = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params).result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION, kind=Kind.storage_v2)
    @StorageAccountPreparer(name_prefix='hdipy2', location=LOCATION, parameter_name='second_storage_account')
    def test_create_with_adls_gen2(self, resource_group, location, storage_account, storage_account_key,
                                   second_storage_account, second_storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-adlgen2')
        create_params = self.get_cluster_create_params_for_adls_gen2(location, cluster_name, storage_account,
                                                                     storage_account_key)

        # Add additional storage account
        create_params.properties.storage_profile.storageaccounts.append(
            StorageAccount(
                name=second_storage_account.name + STORAGE_BLOB_SERVICE_ENDPOINT_SUFFIX,
                key=second_storage_account_key,
                container=cluster_name.lower(),
                is_default=False
            )
        )

        cluster = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params).result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @unittest.skip("This test depends on ADLS Gen1. Now there is something wrong with ADLS Gen1.")
    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy2', location=LOCATION, parameter_name='second_storage_account')
    def test_create_with_additional_storage(self, resource_group, location, storage_account, storage_account_key,
                                            second_storage_account, second_storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-additional')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)

        # Add additional storage account
        create_params.properties.storage_profile.storageaccounts.append(
            StorageAccount(
                name=second_storage_account.name + STORAGE_BLOB_SERVICE_ENDPOINT_SUFFIX,
                key=second_storage_account_key,
                container=cluster_name.lower(),
                is_default=False
            )
        )

        # Add data lake storage gen1 access
        create_params = self.get_cluster_create_params_for_adls_gen1(location, cluster_name, create_params)
        cluster = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params).result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_rserver_cluster(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-rserver')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.cluster_definition.kind = 'RServer'
        create_params.properties.compute_profile.roles.append(
            Role(
                name="edgenode",
                target_instance_count=1,
                hardware_profile=HardwareProfile(vm_size="Standard_D4_v2"),
                os_profile=OsProfile(
                    linux_operating_system_profile=LinuxOperatingSystemProfile(
                        username=self.ssh_username,
                        password=self.ssh_password
                    )
                )
            )
        )
        create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @unittest.skip("HDInsight will not support to create MLService cluster after 1/1/2021.")
    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_mlservices_cluster(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-mlservices')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.cluster_version = "3.6"
        create_params.properties.cluster_definition.kind = 'MLServices'
        create_params.properties.compute_profile.roles.append(
            Role(
                name="edgenode",
                target_instance_count=1,
                hardware_profile=HardwareProfile(vm_size="Standard_D4_v2"),
                os_profile=OsProfile(
                    linux_operating_system_profile=LinuxOperatingSystemProfile(
                        username=self.ssh_username,
                        password=self.ssh_password
                    )
                )
            )
        )
        create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_list_clusters_in_resource_group(self, resource_group, location, storage_account, storage_account_key):
        rg_name = resource_group.name
        cluster_name1 = self.get_resource_name("hdisdk-cluster-rg1")
        cluster_name2 = self.get_resource_name("hdisdk-cluster-rg2")
        cluster_list = list(self.hdinsight_client.clusters.list_by_resource_group(rg_name))
        self.assertFalse(any(c.name == cluster_name1 for c in cluster_list))
        self.assertFalse(any(c.name == cluster_name2 for c in cluster_list))

        create_params1 = self.get_cluster_create_params(location, cluster_name1, storage_account, storage_account_key)
        create_params2 = self.get_cluster_create_params(location, cluster_name2, storage_account, storage_account_key)
        self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name1, create_params1).wait()
        self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name2, create_params2).wait()

        cluster_list = list(self.hdinsight_client.clusters.list_by_resource_group(rg_name))
        self.assertTrue(any(c.name == cluster_name1 for c in cluster_list))
        self.assertTrue(any(c.name == cluster_name2 for c in cluster_list))

    @unittest.skip('This test case lists all clusters under a subscription. '
                   'In order to avoid storing those cluster infos in session records, skip it for now.')
    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_list_clusters_in_subscription(self, resource_group, location, storage_account, storage_account_key):
        rg_name = resource_group.name
        cluster_name1 = self.get_resource_name("hdisdk-cluster")
        cluster_name2 = self.get_resource_name("hdisdk-cluster")
        cluster_list = list(self.hdinsight_client.clusters.list())
        self.assertFalse(any(c.name == cluster_name1 for c in cluster_list))
        self.assertFalse(any(c.name == cluster_name2 for c in cluster_list))

        create_params1 = self.get_cluster_create_params(location, cluster_name1, storage_account, storage_account_key)
        create_params2 = self.get_cluster_create_params(location, cluster_name2, storage_account, storage_account_key)
        self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name1, create_params1).wait()
        self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name2, create_params2).wait()

        cluster_list = list(self.hdinsight_client.clusters.list())
        self.assertTrue(any(c.name == cluster_name1 for c in cluster_list))
        self.assertTrue(any(c.name == cluster_name2 for c in cluster_list))

    @unittest.skip(''' (Conflict) Delete application operation cannot be performed on this cluster at this time as it 
    is not in 'Running' state. It is possible that the cluster is undergoing other update operations.  Please retry later.''')
    @ResourceGroupPreparer(name_prefix='hdipy1', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_hue_on_running_cluster(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-applications-hue')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.cluster_version = "3.6"
        create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

        application_name = "MyApplication"
        application = Application(
            properties=ApplicationProperties(
                install_script_actions=[
                    RuntimeScriptAction(
                        name="InstallHue",
                        uri="https://hdiconfigactions.blob.core.windows.net/linuxhueconfigactionv02/install-hue-uber-v02.sh",
                        parameters="-version latest -port 20000",
                        roles=["edgenode"]
                    )
                ],
                application_type="CustomApplication",
                compute_profile=ComputeProfile(
                    roles=[
                        Role(
                            name="edgenode",
                            hardware_profile=HardwareProfile(
                                vm_size="Large"
                            ),
                            target_instance_count=1
                        )
                    ]
                )
            )
        )

        self.hdinsight_client.applications.begin_create(resource_group.name, cluster_name, application_name,
                                                        application).wait()
        application_list = list(self.hdinsight_client.applications.list_by_cluster(resource_group.name, cluster_name))
        self.assertGreater(len(application_list), 0)
        application_match = [item for item in application_list if item.name == application_name]
        self.assertIsNotNone(application_match)
        self.assertEqual(len(application_match), 1)

        # sleep for robust
        import time
        time.sleep(120)

        self.hdinsight_client.applications.begin_delete(resource_group.name, cluster_name, application_name).wait()
        application_list = list(self.hdinsight_client.applications.list_by_cluster(resource_group.name, cluster_name))
        self.assertEqual(len(application_list), 0)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_get_configurations(self, resource_group, location, storage_account, storage_account_key):
        rg_name = resource_group.name
        cluster_name = self.get_resource_name('hdisdk-configs')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        hive_site = 'hive-site'
        hive_config = {
            'key1': 'value1',
            'key2': 'value2'
        }

        mapred_site = 'mapred-site'
        mapred_config = {
            'key5': 'value5',
            'key6': 'value6'
        }

        yarn_site = 'yarn-site'
        yarn_config = {
            'key7': 'value7',
            'key8': 'value8'
        }

        core_site = 'core-site'
        gateway = 'gateway'
        create_params.properties.cluster_definition.configurations[hive_site] = hive_config
        create_params.properties.cluster_definition.configurations[mapred_site] = mapred_config
        create_params.properties.cluster_definition.configurations[yarn_site] = yarn_config

        create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

        hive = self.hdinsight_client.configurations.get(rg_name, cluster_name, hive_site)
        self.assertEqual(hive, hive_config)

        mapred = self.hdinsight_client.configurations.get(rg_name, cluster_name, mapred_site)
        self.assertEqual(mapred, mapred_config)

        yarn = self.hdinsight_client.configurations.get(rg_name, cluster_name, yarn_site)
        self.assertEqual(yarn, yarn_config)

        gateway = self.hdinsight_client.configurations.get(rg_name, cluster_name, gateway)
        self.assertEqual(len(gateway), 3)

        core = self.hdinsight_client.configurations.get(rg_name, cluster_name, core_site)
        self.assertEqual(len(core), 2)
        self.assertTrue('fs.defaultFS' in core)
        storage_key_prefix = 'fs.azure.account.key.'
        self.assertTrue(any(key.startswith(storage_key_prefix) for key in core))

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_gateway_settings(self, resource_group, location, storage_account, storage_account_key):
        rg_name = resource_group.name
        cluster_name = self.get_resource_name('hdisdk-http')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

        user_name = self.cluster_username
        user_password = self.cluster_password
        gateway_settings = self.hdinsight_client.clusters.get_gateway_settings(rg_name, cluster_name)
        self.validate_gateway_settings(gateway_settings, user_name, user_password)

        new_password = 'NewPassword1!'
        update_params = UpdateGatewaySettingsParameters(is_credential_enabled=True, user_name=user_name,
                                                        password=new_password)
        self.hdinsight_client.clusters.begin_update_gateway_settings(rg_name, cluster_name, update_params).wait()
        gateway_settings = self.hdinsight_client.clusters.get_gateway_settings(rg_name, cluster_name)
        self.validate_gateway_settings(gateway_settings, user_name, new_password)

    def test_get_usages(self):
        usages = self.hdinsight_client.locations.list_usages(LOCATION)
        self.assertIsNotNone(usages)
        self.assertIsNotNone(usages.value)
        for usage in usages.value:
            self.assertIsNotNone(usage)
            self.assertIsNotNone(usage.current_value)
            self.assertIsNotNone(usage.limit)
            self.assertIsNotNone(usage.name)
            self.assertIsNotNone(usage.unit)

    @unittest.skip("Script executed failed due to Internal server. The issue is related with RP not SDK.")
    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_oms_on_running_cluster(self, resource_group, location, storage_account, storage_account_key):
        rg_name = resource_group.name
        cluster_name = self.get_resource_name('hdisdk-oms')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.cluster_definition.kind = 'Spark'
        create_params.properties.cluster_version = "3.6"
        create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

        # create log analytics workspace
        self.loganalytics_mgmt_client = self.create_mgmt_client(LogAnalyticsManagementClient)
        workspace_name = self.get_resource_name('workspaceforpytest')
        workspace_params = Workspace(name=workspace_name, location=location)
        workspace_poller = self.loganalytics_mgmt_client.workspaces.create_or_update(rg_name, workspace_name,
                                                                                     workspace_params)
        workspace = workspace_poller.result()
        self.workspace_id = workspace.customer_id
        self.primary_key = self.loganalytics_mgmt_client.shared_keys.get_shared_keys(rg_name, workspace_name)

        self.hdinsight_client.extensions.enable_monitoring(rg_name, cluster_name, self.workspace_id,
                                                           self.primary_key).wait()
        monitoring_status = self.hdinsight_client.extensions.get_monitoring_status(rg_name, cluster_name)
        self.assertTrue(monitoring_status.cluster_monitoring_enabled)
        self.assertEqual(monitoring_status.workspace_id, self.workspace_id)

        self.hdinsight_client.extensions.disable_monitoring(rg_name, cluster_name).wait()
        monitoring_status = self.hdinsight_client.extensions.get_monitoring_status(rg_name, cluster_name)
        self.assertFalse(monitoring_status.cluster_monitoring_enabled)
        self.assertIsNone(monitoring_status.workspace_id)

    @unittest.skip('(BadRequest) \'targetInstanceCount\' has an invalid value. It must be greater than zero')
    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_resize_cluster(self, resource_group, location, storage_account, storage_account_key):
        rg_name = resource_group.name
        cluster_name = self.get_resource_name('hdisdk-clusterresize')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        workernode_params = next(
            item for item in create_params.properties.compute_profile.roles if item.name == 'workernode')
        create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

        cluster = self.hdinsight_client.clusters.get(rg_name, cluster_name)
        workernode = next(item for item in cluster.properties.compute_profile.roles if item.name == 'workernode')
        self.assertEqual(workernode_params.target_instance_count, workernode.target_instance_count)

        self.hdinsight_client.clusters.begin_resize(rg_name, cluster_name,
                                                    workernode_params.target_instance_count + 1).wait()
        cluster = self.hdinsight_client.clusters.get(rg_name, cluster_name)
        workernode = next(item for item in cluster.properties.compute_profile.roles if item.name == 'workernode')
        self.assertEqual(workernode_params.target_instance_count + 1, workernode.target_instance_count)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_script_actions_on_running_cluster(self, resource_group, location, storage_account, storage_account_key):
        rg_name = resource_group.name
        cluster_name = self.get_resource_name('hdisdk-scriptactions')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_poller = self.hdinsight_client.clusters.begin_create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

        install_giraph = "https://hdiconfigactions.blob.core.windows.net/linuxgiraphconfigactionv01/giraph-installer-v01.sh"
        script_name = "script1"

        # Execute script actions, and persist on success.
        script_action_params = self.get_execute_script_action_params(script_name, install_giraph)
        self.hdinsight_client.clusters.begin_execute_script_actions(rg_name, cluster_name, True,
                                                                    script_action_params).wait()

        # List script actions and validate script is persisted.
        script_action_list = list(self.hdinsight_client.script_actions.list_by_cluster(rg_name, cluster_name))
        self.assertEqual(1, len(script_action_list))
        script_action = script_action_list[0]
        self.assertEqual(script_action_params[0].name, script_action.name)
        self.assertEqual(script_action_params[0].uri, script_action.uri)
        self.assertEqual(script_action_params[0].roles, script_action.roles)

        # Delete script action.
        self.hdinsight_client.script_actions.delete(rg_name, cluster_name, script_name)

        # List script actions and validate script is deleted.
        script_action_list = list(self.hdinsight_client.script_actions.list_by_cluster(rg_name, cluster_name))
        self.assertEqual(0, len(script_action_list))

        # List script action history and validate script appears there.
        list_history_response = list(
            self.hdinsight_client.script_execution_history.list_by_cluster(rg_name, cluster_name))
        self.assertEqual(1, len(list_history_response))
        script_action = list_history_response[0]
        self.assertEqual(1, len(script_action.execution_summary))
        self.assertEqual(script_action_params[0].name, script_action.name)
        self.assertEqual(script_action_params[0].uri, script_action.uri)
        self.assertEqual(script_action_params[0].roles, script_action.roles)
        self.assertEqual("Succeeded", script_action.status)

        # Get the script action by ID and validate it's the same action.
        script_action = self.hdinsight_client.script_actions.get_execution_detail(rg_name, cluster_name, str(
            list_history_response[0].script_execution_id))
        self.assertEqual(script_action_params[0].name, script_action.name)

        # Execute script actions, but don't persist on success.
        script_action_params = self.get_execute_script_action_params("script5baf", install_giraph)
        self.hdinsight_client.clusters.begin_execute_script_actions(rg_name, cluster_name, False,
                                                                    script_action_params).wait()

        # List script action history and validate the new script also appears.
        list_history_response = list(
            self.hdinsight_client.script_execution_history.list_by_cluster(rg_name, cluster_name))
        self.assertEqual(2, len(list_history_response))
        script_action = next(a for a in list_history_response if a.name == script_action_params[0].name)
        self.assertIsNotNone(script_action)
        self.assertEqual(1, len(script_action.execution_summary))
        self.assertEqual(script_action_params[0].name, script_action.name)
        self.assertEqual(script_action_params[0].uri, script_action.uri)
        self.assertEqual(script_action_params[0].roles, script_action.roles)
        self.assertEqual("Succeeded", script_action.status)

        # Promote non-persisted script.
        self.hdinsight_client.script_execution_history.promote(rg_name, cluster_name,
                                                               str(list_history_response[0].script_execution_id))

        # List script action list and validate the promoted script is the only one there.
        script_action_list = list(self.hdinsight_client.script_actions.list_by_cluster(rg_name, cluster_name))
        self.assertEqual(1, len(script_action_list))
        script_action = script_action_list[0]
        self.assertEqual(script_action_params[0].name, script_action.name)
        self.assertEqual(script_action_params[0].uri, script_action.uri)
        self.assertEqual(script_action_params[0].roles, script_action.roles)

        # List script action history and validate all three scripts are there.
        list_history_response = list(
            self.hdinsight_client.script_execution_history.list_by_cluster(rg_name, cluster_name))
        self.assertEqual(2, len(list_history_response))
        self.assertTrue(all(a.status == "Succeeded" for a in list_history_response))

    def get_execute_script_action_params(self, script_name, script_uri):
        return [
            RuntimeScriptAction(
                name=script_name,
                uri=script_uri,
                roles=['headnode', 'workernode']
            )
        ]

    def get_cluster_create_params_for_adls_gen1(self, location, cluster_name, create_params=None):
        if create_params is None:
            create_params = self.get_cluster_create_params(location, cluster_name)

        cluster_identity = 'clusterIdentity'
        cluster_identity_config = {
            'clusterIdentity.applicationId': self.adls_client_id,
            'clusterIdentity.certificate': self.cert_content,
            'clusterIdentity.aadTenantId': 'https://login.windows.net/{}'.format(self.tenant_id),
            'clusterIdentity.resourceUri': 'https://datalake.azure.net/',
            'clusterIdentity.certificatePassword': self.cert_password
        }
        create_params.properties.cluster_definition.configurations[cluster_identity] = cluster_identity_config

        is_default = len(create_params.properties.storage_profile.storageaccounts) == 0
        if is_default:
            core_site = 'core-site'
            core_config = {
                'fs.defaultFS': 'adl://home',
                'dfs.adls.home.hostname': '{}.azuredatalakestore.net'.format(self.adls_account_name),
                'dfs.adls.home.mountpoint': self.adls_home_mountpoint
            }
            create_params.properties.cluster_definition.configurations[core_site] = core_config

        return create_params

    def get_cluster_create_params_for_adls_gen2(self, location, cluster_name, storage_account, storage_account_key,
                                                create_params=None):
        if create_params is None:
            create_params = self.get_cluster_create_params(location, cluster_name)
        is_default = len(create_params.properties.storage_profile.storageaccounts) == 0
        create_params.properties.storage_profile.storageaccounts.append(
            StorageAccount(
                name=storage_account.name + STORAGE_ADLS_FILE_SYSTEM_ENDPOINT_SUFFIX,
                key=storage_account_key,
                file_system=cluster_name.lower(),
                is_default=is_default
            )
        )

        return create_params

    def get_cluster_create_params(self, location, cluster_name, storage_account=None, storage_account_key=None):
        storage_accounts = []
        if storage_account:
            # Specify storage account details only when storage arguments are provided
            storage_accounts.append(
                StorageAccount(
                    name=storage_account.name + STORAGE_BLOB_SERVICE_ENDPOINT_SUFFIX,
                    key=storage_account_key,
                    container=cluster_name.lower(),
                    is_default=True
                )
            )

        return ClusterCreateParametersExtended(
            location=location,
            tags={},
            properties=ClusterCreateProperties(
                cluster_version="3.6",
                os_type=OSType.linux,
                tier=Tier.standard,
                cluster_definition=ClusterDefinition(
                    kind="hadoop",
                    configurations={
                        "gateway": {
                            "restAuthCredential.isEnabled": "true",
                            "restAuthCredential.username": self.cluster_username,
                            "restAuthCredential.password": self.cluster_password
                        }
                    }
                ),
                compute_profile=ComputeProfile(
                    roles=[
                        Role(
                            name="headnode",
                            target_instance_count=2,
                            hardware_profile=HardwareProfile(vm_size="Large"),
                            os_profile=OsProfile(
                                linux_operating_system_profile=LinuxOperatingSystemProfile(
                                    username=self.ssh_username,
                                    password=self.ssh_password
                                )
                            )
                        ),
                        Role(
                            name="workernode",
                            target_instance_count=3,
                            hardware_profile=HardwareProfile(vm_size="Large"),
                            os_profile=OsProfile(
                                linux_operating_system_profile=LinuxOperatingSystemProfile(
                                    username=self.ssh_username,
                                    password=self.ssh_password
                                )
                            )
                        ),
                        Role(
                            name="zookeepernode",
                            target_instance_count=3,
                            hardware_profile=HardwareProfile(vm_size="Small"),
                            os_profile=OsProfile(
                                linux_operating_system_profile=LinuxOperatingSystemProfile(
                                    username=self.ssh_username,
                                    password=self.ssh_password
                                )
                            )
                        )
                    ]
                ),
                storage_profile=StorageProfile(
                    storageaccounts=storage_accounts
                )
            )
        )

    def validate_cluster(self, cluster_name, create_parameters, cluster_response):
        self.assertEqual(cluster_name, cluster_response.name)
        self.assertEqual(create_parameters.properties.tier.lower(), cluster_response.properties.tier.lower())
        self.assertIsNotNone(cluster_response.etag)
        self.assertTrue(cluster_response.id.endswith(cluster_name))
        self.assertEqual("Running", cluster_response.properties.cluster_state)
        self.assertEqual("Microsoft.HDInsight/clusters", cluster_response.type)
        self.assertEqual(create_parameters.location, cluster_response.location)
        self.assertEqual(create_parameters.tags, cluster_response.tags)
        self.assertEqual(1, len([endpoint for endpoint in cluster_response.properties.connectivity_endpoints
                                 if endpoint.name == "HTTPS"]))
        self.assertEqual(1, len([endpoint for endpoint in cluster_response.properties.connectivity_endpoints
                                 if endpoint.name == "SSH"]))
        self.assertEqual(create_parameters.properties.os_type, cluster_response.properties.os_type)
        self.assertIsNone(cluster_response.properties.errors)
        self.assertEqual(HDInsightClusterProvisioningState.succeeded, cluster_response.properties.provisioning_state)
        self.assertEqual(create_parameters.properties.cluster_definition.kind,
                         cluster_response.properties.cluster_definition.kind)
        self.assertEqual(create_parameters.properties.cluster_version, cluster_response.properties.cluster_version[0:3])
        self.assertIsNone(cluster_response.properties.cluster_definition.configurations)

    def validate_gateway_settings(self, gateway_settings, expected_user_name, expected_user_password):
        self.assertIsNotNone(gateway_settings)
        self.assertEqual('true', gateway_settings.is_credential_enabled)
        self.assertEqual(expected_user_name, gateway_settings.user_name)
        self.assertEqual(expected_user_password, gateway_settings.password)

    def _setup_scrubber(self):
        super(MgmtHDInsightTest, self)._setup_scrubber()
        constants_to_scrub = ['HDI_ADLS_ACCOUNT_NAME', 'HDI_ADLS_CLIENT_ID']
        for key in constants_to_scrub:
            if hasattr(self.settings, key) and hasattr(self._fake_settings, key):
                self.scrubber.register_name_pair(getattr(self.settings, key),
                                                 getattr(self._fake_settings, key))


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
