# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

from azure.keyvault import KeyVaultId, KeyVaultClient, KeyVaultAuthentication, AccessToken
from azure.mgmt.hdinsight import HDInsightManagementClient
from azure.mgmt.hdinsight.models import *
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.msi import ManagedServiceIdentityClient
from azure.mgmt.keyvault.models import SecretPermissions, KeyPermissions, CertificatePermissions, StoragePermissions, \
    Permissions, Sku, SkuName, AccessPolicyEntry, VaultProperties, VaultCreateOrUpdateParameters, Vault
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
        if self.is_live:
            self.vault_client = self.create_basic_client(KeyVaultClient)
        else:
            def _auth_callback(server, resource, scope):
                return AccessToken('Bearer', 'fake-token')
            self.vault_client = KeyVaultClient(KeyVaultAuthentication(authorization_callback=_auth_callback))

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
        self.cert_password = '123'
        self.cert_content = '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'
        self.workspace_id = '1d364e89-bb71-4503-aa3d-a23535aea7bd'

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_humboldt_cluster(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-humboldt')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_humboldt_cluster_with_premium_tier(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-premium')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.tier=Tier.premium
        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_with_empty_extended_parameters(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-cluster')
        create_params = ClusterCreateParametersExtended()

        # try to create cluster and ensure it throws
        try:
            create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
            cluster = create_poller.result()
            self.assertTrue(False, 'should not have made it here')
        except Exception:
            pass

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_humboldt_cluster_with_custom_vm_sizes(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-customvmsizes')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        headnode = next(item for item in create_params.properties.compute_profile.roles if item.name == 'headnode')
        headnode.hardware_profile = HardwareProfile(vm_size="ExtraLarge")
        zookeepernode = next(item for item in create_params.properties.compute_profile.roles if item.name == 'zookeepernode')
        zookeepernode.hardware_profile = HardwareProfile(vm_size="Medium")
        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_linux_spark_cluster_with_component_version(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-sparkcomponentversions')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.cluster_definition.kind = 'Spark'
        create_params.properties.cluster_definition.Component_version = {'Spark' : '2.2'}
        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_kafka_cluster_with_managed_disks(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-kafka')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.cluster_definition.kind = 'Kafka'
        workernode = next(item for item in create_params.properties.compute_profile.roles if item.name == 'workernode')
        workernode.data_disks_groups = [
            DataDisksGroups(
                disks_per_node=8
            )
        ]
        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    @KeyVaultPreparer(name_prefix='hdipy', location=LOCATION, enable_soft_delete=True)
    def test_create_kafka_cluster_with_disk_encryption(self, resource_group, location, storage_account, storage_account_key, vault):
        # create managed identities for Azure resources.
        msi_name = self.get_resource_name('hdipyuai')
        msi_principal_id = "00000000-0000-0000-0000-000000000000"
        msi_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/{}/providers/microsoft.managedidentity/userassignedidentities/{}".format(resource_group.name, msi_name)
        if self.is_live:
            msi = self.msi_client.user_assigned_identities.create_or_update(resource_group.name, msi_name, location)
            msi_id = msi.id
            msi_principal_id = msi.principal_id

        # add managed identity to vault
        required_permissions = Permissions(keys=[KeyPermissions.get, KeyPermissions.wrap_key, KeyPermissions.unwrap_key],
                                           secrets=[SecretPermissions.get, SecretPermissions.set,SecretPermissions.delete])
        vault.properties.access_policies.append(
            AccessPolicyEntry(tenant_id=self.tenant_id,
                              object_id=msi_principal_id,
                              permissions=required_permissions)
        )
        update_params = VaultCreateOrUpdateParameters(location=location,
                                                      properties=vault.properties)
        vault = self.vault_mgmt_client.vaults.create_or_update(resource_group.name, vault.name, update_params).result()
        self.assertIsNotNone(vault)

        # create key
        vault_uri = vault.properties.vault_uri
        key_name = self.get_resource_name('hdipykey1')
        created_bundle = self.vault_client.create_key(vault_uri, key_name, 'RSA')
        vault_key = KeyVaultId.parse_key_id(created_bundle.key.kid)

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
            vault_uri=vault_key.vault,
            key_name=vault_key.name,
            key_version=vault_key.version,
            msi_resource_id=msi_id
        )
        cluster = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params).result()
        self.validate_cluster(cluster_name, create_params, cluster)

        # check disk encryption properties
        self.assertIsNotNone(cluster.properties.disk_encryption_properties)
        self.assertEqual(create_params.properties.disk_encryption_properties.vault_uri, cluster.properties.disk_encryption_properties.vault_uri)
        self.assertEqual(create_params.properties.disk_encryption_properties.key_name, cluster.properties.disk_encryption_properties.key_name)
        self.assertEqual(create_params.properties.disk_encryption_properties.msi_resource_id.lower(), cluster.properties.disk_encryption_properties.msi_resource_id.lower())

        # create a new key
        new_key_name = self.get_resource_name('hdipykey2')
        created_bundle = self.vault_client.create_key(vault_uri, new_key_name, 'RSA')
        new_vault_key = KeyVaultId.parse_key_id(created_bundle.key.kid)
        rotate_params = ClusterDiskEncryptionParameters(
            vault_uri=new_vault_key.vault,
            key_name=new_vault_key.name,
            key_version=new_vault_key.version
        )

        # rotate cluster key
        self.hdinsight_client.clusters.rotate_disk_encryption_key(rg_name, cluster_name, rotate_params).wait()
        cluster = self.hdinsight_client.clusters.get(rg_name, cluster_name)

        # check disk encryption properties
        self.assertIsNotNone(cluster.properties.disk_encryption_properties)
        self.assertEqual(rotate_params.vault_uri, cluster.properties.disk_encryption_properties.vault_uri)
        self.assertEqual(rotate_params.key_name, cluster.properties.disk_encryption_properties.key_name)
        self.assertEqual(msi_id.lower(), cluster.properties.disk_encryption_properties.msi_resource_id.lower())

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

        cluster = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params).result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION, kind=Kind.storage_v2)
    @StorageAccountPreparer(name_prefix='hdipy2', location=LOCATION, parameter_name='second_storage_account')
    def test_create_with_adls_gen2(self, resource_group, location, storage_account, storage_account_key,
                                   second_storage_account, second_storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-adlgen2')
        create_params = self.get_cluster_create_params_for_adls_gen2(location, cluster_name, storage_account, storage_account_key)

        # Add additional storage account
        create_params.properties.storage_profile.storageaccounts.append(
            StorageAccount(
                name=second_storage_account.name + STORAGE_BLOB_SERVICE_ENDPOINT_SUFFIX,
                key=second_storage_account_key,
                container=cluster_name.lower(),
                is_default=False
            )
        )

        cluster = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params).result()
        self.validate_cluster(cluster_name, create_params, cluster)

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
        cluster = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params).result()
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
        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_create_mlservices_cluster(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-mlservices')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.cluster_version="3.6"
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
        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
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
        self.hdinsight_client.clusters.create(resource_group.name, cluster_name1, create_params1).wait()
        self.hdinsight_client.clusters.create(resource_group.name, cluster_name2, create_params2).wait()

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
        self.hdinsight_client.clusters.create(resource_group.name, cluster_name1, create_params1).wait()
        self.hdinsight_client.clusters.create(resource_group.name, cluster_name2, create_params2).wait()

        cluster_list = list(self.hdinsight_client.clusters.list())
        self.assertTrue(any(c.name == cluster_name1 for c in cluster_list))
        self.assertTrue(any(c.name == cluster_name2 for c in cluster_list))

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_hue_on_running_cluster(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-applications-hue')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.cluster_version="3.6"
        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
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
                            target_instance_count = 1
                        )
                    ]
                )
            )
        )

        self.hdinsight_client.applications.create(resource_group.name, cluster_name, application_name, application).wait()
        application_list = list(self.hdinsight_client.applications.list_by_cluster(resource_group.name, cluster_name))
        self.assertGreater(len(application_list), 0)
        application_match = [item for item in application_list if item.name == application_name]
        self.assertIsNotNone(application_match)
        self.assertEqual(len(application_match), 1)

        self.hdinsight_client.applications.delete(resource_group.name, cluster_name, application_name).wait()
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

        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
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
    def test_http_extended(self, resource_group, location, storage_account, storage_account_key):
        rg_name = resource_group.name
        cluster_name = self.get_resource_name('hdisdk-http')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

        gateway = 'gateway'
        user_name = self.cluster_username
        user_password = self.cluster_password
        http_settings = self.hdinsight_client.configurations.get(rg_name, cluster_name, gateway)
        self.validate_http_settings(http_settings, user_name, user_password)

        new_password = 'NewPassword1!'
        update_params = {
            'restAuthCredential.isEnabled': 'true',
            'restAuthCredential.username': user_name,
            'restAuthCredential.password': new_password
        }
        self.hdinsight_client.configurations.update(rg_name, cluster_name, gateway, update_params).wait()
        http_settings = self.hdinsight_client.configurations.get(rg_name, cluster_name, gateway)
        self.validate_http_settings(http_settings, user_name, new_password)

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

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_oms_on_running_cluster(self, resource_group, location, storage_account, storage_account_key):
        rg_name = resource_group.name
        cluster_name = self.get_resource_name('hdisdk-oms')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_params.properties.cluster_definition.kind = 'Spark'
        create_params.properties.cluster_version="3.6"
        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

        self.hdinsight_client.extensions.enable_monitoring(rg_name, cluster_name, self.workspace_id).wait()
        monitoring_status = self.hdinsight_client.extensions.get_monitoring_status(rg_name, cluster_name)
        self.assertTrue(monitoring_status.cluster_monitoring_enabled)
        self.assertEqual(monitoring_status.workspace_id, self.workspace_id)

        self.hdinsight_client.extensions.disable_monitoring(rg_name, cluster_name).wait()
        monitoring_status = self.hdinsight_client.extensions.get_monitoring_status(rg_name, cluster_name)
        self.assertFalse(monitoring_status.cluster_monitoring_enabled)
        self.assertIsNone(monitoring_status.workspace_id)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_resize_cluster(self, resource_group, location, storage_account, storage_account_key):
        rg_name = resource_group.name
        cluster_name = self.get_resource_name('hdisdk-clusterresize')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        workernode_params = next(item for item in create_params.properties.compute_profile.roles if item.name == 'workernode')
        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

        cluster = self.hdinsight_client.clusters.get(rg_name, cluster_name)
        workernode = next(item for item in cluster.properties.compute_profile.roles if item.name == 'workernode')
        self.assertEqual(workernode_params.target_instance_count, workernode.target_instance_count)

        self.hdinsight_client.clusters.resize(rg_name, cluster_name, workernode_params.target_instance_count + 1).wait()
        cluster = self.hdinsight_client.clusters.get(rg_name, cluster_name)
        workernode = next(item for item in cluster.properties.compute_profile.roles if item.name == 'workernode')
        self.assertEqual(workernode_params.target_instance_count + 1, workernode.target_instance_count)

    @ResourceGroupPreparer(name_prefix='hdipy-', location=LOCATION)
    @StorageAccountPreparer(name_prefix='hdipy', location=LOCATION)
    def test_script_actions_on_running_cluster(self, resource_group, location, storage_account, storage_account_key):
        rg_name = resource_group.name
        cluster_name = self.get_resource_name('hdisdk-scriptactions')
        create_params = self.get_cluster_create_params(location, cluster_name, storage_account, storage_account_key)
        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(cluster_name, create_params, cluster)

        install_giraph = "https://hdiconfigactions.blob.core.windows.net/linuxgiraphconfigactionv01/giraph-installer-v01.sh"
        script_name = "script1"

        # Execute script actions, and persist on success.
        script_action_params = self.get_execute_script_action_params(script_name, install_giraph)
        self.hdinsight_client.clusters.execute_script_actions(rg_name, cluster_name, True, script_action_params).wait()

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
        list_history_response = list(self.hdinsight_client.script_execution_history.list_by_cluster(rg_name, cluster_name))
        self.assertEqual(1, len(list_history_response))
        script_action = list_history_response[0]
        self.assertEqual(1, len(script_action.execution_summary))
        self.assertEqual(script_action_params[0].name, script_action.name)
        self.assertEqual(script_action_params[0].uri, script_action.uri)
        self.assertEqual(script_action_params[0].roles, script_action.roles)
        self.assertEqual("Succeeded", script_action.status)

        # Get the script action by ID and validate it's the same action.
        script_action = self.hdinsight_client.script_actions.get_execution_detail(rg_name, cluster_name, str(list_history_response[0].script_execution_id))
        self.assertEqual(script_action_params[0].name, script_action.name)

        # Execute script actions, but don't persist on success.
        script_action_params = self.get_execute_script_action_params("script5baf", install_giraph)
        self.hdinsight_client.clusters.execute_script_actions(rg_name, cluster_name, False, script_action_params).wait()

        # List script action history and validate the new script also appears.
        list_history_response = list(self.hdinsight_client.script_execution_history.list_by_cluster(rg_name, cluster_name))
        self.assertEqual(2, len(list_history_response))
        script_action = next(a for a in list_history_response if a.name == script_action_params[0].name)
        self.assertIsNotNone(script_action)
        self.assertEqual(1, len(script_action.execution_summary))
        self.assertEqual(script_action_params[0].name, script_action.name)
        self.assertEqual(script_action_params[0].uri, script_action.uri)
        self.assertEqual(script_action_params[0].roles, script_action.roles)
        self.assertEqual("Succeeded", script_action.status)

        # Promote non-persisted script.
        self.hdinsight_client.script_execution_history.promote(rg_name, cluster_name, str(list_history_response[0].script_execution_id))

        # List script action list and validate the promoted script is the only one there.
        script_action_list = list(self.hdinsight_client.script_actions.list_by_cluster(rg_name, cluster_name))
        self.assertEqual(1, len(script_action_list))
        script_action = script_action_list[0]
        self.assertEqual(script_action_params[0].name, script_action.name)
        self.assertEqual(script_action_params[0].uri, script_action.uri)
        self.assertEqual(script_action_params[0].roles, script_action.roles)

        # List script action history and validate all three scripts are there.
        list_history_response = list(self.hdinsight_client.script_execution_history.list_by_cluster(rg_name, cluster_name))
        self.assertEqual(2, len(list_history_response))
        self.assertTrue(all(a.status == "Succeeded" for a in list_history_response))

    def get_execute_script_action_params(self, script_name, script_uri):
        return [
            RuntimeScriptAction(
                name = script_name,
                uri = script_uri,
                roles = ['headnode', 'workernode']
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

    def get_cluster_create_params_for_adls_gen2(self, location, cluster_name, storage_account, storage_account_key, create_params=None):
        if create_params is None:
            create_params = self.get_cluster_create_params(location, cluster_name)
        is_default = len(create_params.properties.storage_profile.storageaccounts) == 0
        create_params.properties.storage_profile.storageaccounts.append(
            StorageAccount(
                name=storage_account.name + STORAGE_ADLS_FILE_SYSTEM_ENDPOINT_SUFFIX,
                key=storage_account_key,
                file_system=cluster_name.lower(),
                is_default= is_default
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
        self.assertEqual(create_parameters.properties.tier, cluster_response.properties.tier)
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
        self.assertEqual(create_parameters.properties.cluster_definition.kind, cluster_response.properties.cluster_definition.kind)
        self.assertEqual(create_parameters.properties.cluster_version, cluster_response.properties.cluster_version[0:3])
        self.assertIsNone(cluster_response.properties.cluster_definition.configurations)

    def validate_http_settings(self, http_settings, expected_user_name, expected_user_password):
        self.assertIsNotNone(http_settings)
        self.assertEqual('true', http_settings['restAuthCredential.isEnabled'])
        self.assertEqual(expected_user_name, http_settings['restAuthCredential.username'])
        self.assertEqual(expected_user_password, http_settings['restAuthCredential.password'])

    def _setup_scrubber(self):
        super(MgmtHDInsightTest, self)._setup_scrubber()
        constants_to_scrub = ['HDI_ADLS_ACCOUNT_NAME', 'HDI_ADLS_CLIENT_ID']
        for key in constants_to_scrub:
            if hasattr(self.settings, key) and hasattr(self._fake_settings, key):
                self.scrubber.register_name_pair(getattr(self.settings, key),
                                                 getattr(self._fake_settings, key))

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
