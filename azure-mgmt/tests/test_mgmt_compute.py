# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

from collections import namedtuple

import azure.mgmt.compute
import azure.mgmt.network
import azure.mgmt.storage
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase

ComputeResourceNames = namedtuple(
    'ComputeResourceNames',
    ['storage', 'vm' ,'network', 'nic', 'subnet'],
)

class MgmtComputeTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtComputeTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.compute.Client
        )

        self.linux_img_ref_id = "/" + self.settings.SUBSCRIPTION_ID + "/services/images/b4590d9e3ed742e4a1d46e5424aa335e__sles12-azure-guest-priority.x86-64-0.4.3-build1.1"
        self.windows_img_ref_id = "/" + self.settings.SUBSCRIPTION_ID + "/services/images/a699494373c04fc0bc8f2bb1389d6106__Windows-Server-2012-Datacenter-201503.01-en.us-127GB.vhd"
        if not self.is_playback():
            self.storage_client = self.create_mgmt_client(
                azure.mgmt.storage.StorageManagementClient
            )
            self.network_client = self.create_mgmt_client(
                azure.mgmt.network.NetworkManagementClient
            )
            self.create_resource_group()

    def get_resource_names(self, base):
        return ComputeResourceNames(
            self.get_resource_name(base + 'stor'),
            self.get_resource_name(base + 'vm'),
            self.get_resource_name(base + 'net'),
            self.get_resource_name(base + 'nic'),
            self.get_resource_name(base + 'sub'),
        )

    def create_storage_account(self, storage_name):
        params_create = azure.mgmt.storage.models.StorageAccountCreateParameters(
            sku=azure.mgmt.storage.models.Sku(azure.mgmt.storage.models.SkuName.standard_lrs),
            kind=azure.mgmt.storage.models.Kind.storage,
            location=self.region
        )
        result_create = self.storage_client.storage_accounts.create(
            self.group_name,
            storage_name,
            params_create,
        )
        result_create.wait()

    def create_virtual_network(self, network_name, subnet_name):
        params_create = azure.mgmt.network.models.VirtualNetwork(
            location=self.region,
            address_space=azure.mgmt.network.models.AddressSpace(
                address_prefixes=[
                    '10.0.0.0/16',
                ],
            ),
            subnets=[
                azure.mgmt.network.models.Subnet(
                    name=subnet_name,
                    address_prefix='10.0.0.0/24',
                ),
            ],
        )
        azure_operation_poller = self.network_client.virtual_networks.create_or_update(
            self.group_name,
            network_name,
            params_create,
        )
        result_create = azure_operation_poller.result()
        self.assertEqual(result_create.name, network_name)

        result_get = self.network_client.subnets.get(
            self.group_name,
            network_name,
            subnet_name,
        )
        self.assertEqual(result_get.name, subnet_name)

        return result_get

    def create_network_interface(self, interface_name, subnet):
        config_name = 'pyarmconfig'

        params_create = azure.mgmt.network.models.NetworkInterface(
            location=self.region,
            ip_configurations=[
                azure.mgmt.network.models.NetworkInterfaceIPConfiguration(
                    name=config_name,
                    # bug in Swagger azure.mgmt.network.models.enums.IPAllocationMethod.dynamic,
                    private_ip_allocation_method="Dynamic",
                    subnet=subnet,
                ),
            ],
        )
        result_create = self.network_client.network_interfaces.create_or_update(
            self.group_name,
            interface_name,
            params_create,
        )
        result_create = result_create.result()
        self.assertEqual(result_create.name, interface_name)
        return result_create.id

    def get_os_profile(self):
       models = azure.mgmt.compute.models('2016-04-30-preview')
       return models.OSProfile(
           admin_username='Foo12',
           admin_password='BaR@123' + self.group_name,
           computer_name='test',
       )

    def get_hardware_profile(self):
        models = azure.mgmt.compute.models('2016-04-30-preview')
        return models.HardwareProfile(
            vm_size=models.VirtualMachineSizeTypes.standard_a0
        )

    def get_storage_profile(self, os_vhd_uri):
        models = azure.mgmt.compute.models('2016-04-30-preview')
        return models.StorageProfile(
            os_disk=models.OSDisk(
                caching=models.CachingTypes.none,
                create_option=models.DiskCreateOptionTypes.from_image,
                name='test',
                vhd=models.VirtualHardDisk(
                    uri=os_vhd_uri,
                ),
            ),
        )

    def get_network_profile(self, network_interface_id):
        models = azure.mgmt.compute.models('2016-04-30-preview')
        return models.NetworkProfile(
            network_interfaces=[
                models.NetworkInterfaceReference(
                    id=network_interface_id,
                ),
            ],
        )

    def get_vhd_uri(self, storage_name, vhd_name):
        return 'https://{0}.blob.core.windows.net/vhds/{1}.vhd'.format(
            storage_name,
            vhd_name,
        )

    def test_virtual_machines_operations(self):
        virtual_machines_operations = self.client.virtual_machines()
        models = azure.mgmt.compute.models('2016-04-30-preview')

        names = self.get_resource_names('pyvmir')
        os_vhd_uri = self.get_vhd_uri(names.storage, 'osdisk')

        if not self.is_playback():
            self.create_storage_account(names.storage)
            subnet = self.create_virtual_network(names.network, names.subnet)
            nic_id = self.create_network_interface(names.nic, subnet)
        else:
            nic_id = ("/subscriptions/00000000-0000-0000-0000-000000000000"
                      "/resourceGroups/test_mgmt_compute_test_virtual_machines_operations122014cf"
                      "/providers/Microsoft.Network/networkInterfaces/pyvmirnic122014cf")

        with self.recording():
            storage_profile = self.get_storage_profile(os_vhd_uri)
            storage_profile.image_reference = models.ImageReference(
                publisher='Canonical',
                offer='UbuntuServer',
                sku='16.04.0-LTS',
                version='latest'
            )

            params_create = models.VirtualMachine(
                location=self.region,
                os_profile=self.get_os_profile(),
                hardware_profile=self.get_hardware_profile(),
                network_profile=self.get_network_profile(nic_id),
                storage_profile=storage_profile,
            )

            # Create VM test
            result_create = virtual_machines_operations.create_or_update(
                self.group_name,
                names.vm,
                params_create,
            )
            vm_result = result_create.result()
            self.assertEqual(vm_result.name, names.vm)
        
            # Get by name
            result_get = virtual_machines_operations.get(
                self.group_name,
                names.vm
            )
            self.assertEqual(result_get.name, names.vm)
            self.assertIsNone(result_get.instance_view)

            # Get instanceView
            result_iv = virtual_machines_operations.get(
                self.group_name,
                names.vm,
                expand=models.InstanceViewTypes.instance_view
            )
            self.assertTrue(result_iv.instance_view)

            # Deallocate
            async_vm_deallocate = virtual_machines_operations.deallocate(self.group_name, names.vm)
            async_vm_deallocate.wait()

            # Start VM
            async_vm_start = virtual_machines_operations.start(self.group_name, names.vm)
            async_vm_start.wait()

            # Restart VM
            async_vm_restart = virtual_machines_operations.restart(self.group_name, names.vm)
            async_vm_restart.wait()

            # Stop VM
            async_vm_stop = virtual_machines_operations.power_off(self.group_name, names.vm)
            async_vm_stop.wait()

            # List in resouce group
            vms_rg = list(virtual_machines_operations.list(self.group_name))
            self.assertEqual(len(vms_rg), 1)

            # Delete
            async_vm_delete = virtual_machines_operations.delete(self.group_name, names.vm)
            async_vm_delete.wait()

    def test_virtual_machine_capture(self):
        virtual_machines_operations = self.client.virtual_machines()
        models = azure.mgmt.compute.models('2016-04-30-preview')

        names = self.get_resource_names('pyvmir')
        os_vhd_uri = self.get_vhd_uri(names.storage, 'osdisk')

        if not self.is_playback():
            self.create_storage_account(names.storage)
            subnet = self.create_virtual_network(names.network, names.subnet)
            nic_id = self.create_network_interface(names.nic, subnet)
        else:
            nic_id = ("/subscriptions/00000000-0000-0000-0000-000000000000"
                      "/resourceGroups/test_mgmt_compute_test_virtual_machine_capturec0f9130c"
                      "/providers/Microsoft.Network/networkInterfaces/pyvmirnicc0f9130c")

        with self.recording():
            storage_profile = self.get_storage_profile(os_vhd_uri)
            storage_profile.image_reference = models.ImageReference(
                publisher='Canonical',
                offer='UbuntuServer',
                sku='16.04.0-LTS',
                version='latest'
            )

            params_create = models.VirtualMachine(
                location=self.region,
                os_profile=self.get_os_profile(),
                hardware_profile=self.get_hardware_profile(),
                network_profile=self.get_network_profile(nic_id),
                storage_profile=storage_profile,
            )

            # Create VM test
            result_create = virtual_machines_operations.create_or_update(
                self.group_name,
                names.vm,
                params_create,
            )
            vm_result = result_create.result()
            self.assertEqual(vm_result.name, names.vm)

            # Deallocate
            async_vm_deallocate = virtual_machines_operations.deallocate(self.group_name, names.vm)
            async_vm_deallocate.wait()

            # Generalize (possible because deallocated)
            virtual_machines_operations.generalize(self.group_name, names.vm)

            # Capture VM (VM must be generalized before)
            async_capture = virtual_machines_operations.capture(
                self.group_name,
                names.vm,
                {
                   "vhd_prefix":"pslib",
                   "destination_container_name":"dest",
                   "overwrite_vhds": True
                }
            )
            capture_result = async_capture.result()
            self.assertTrue(hasattr(capture_result, 'output'))

    def test_vm_extensions(self):
        virtual_machines_operations = self.client.virtual_machines()
        virtual_machine_extensions = self.client.virtual_machine_extensions()
        models = azure.mgmt.compute.models('2016-04-30-preview')

        #WARNING: this test may take 40 mins to complete against live server
        names = self.get_resource_names('pyvmext')
        os_vhd_uri = self.get_vhd_uri(names.storage, 'osdisk')
        ext_name = names.vm + 'AccessAgent'

        if not self.is_playback():
            self.create_storage_account(names.storage)
            subnet = self.create_virtual_network(names.network, names.subnet)
            nic_id = self.create_network_interface(names.nic, subnet)
        else:
            nic_id = ("/subscriptions/00000000-0000-0000-0000-000000000000"
                    "/resourceGroups/test_mgmt_compute_test_vm_extensions15a60f10"
                    "/providers/Microsoft.Network/networkInterfaces/pyvmextnic15a60f10")

        with self.recording():
            storage_profile = self.get_storage_profile(os_vhd_uri)
            storage_profile.image_reference = models.ImageReference(
                publisher='MicrosoftWindowsServerEssentials',
                offer='WindowsServerEssentials',
                sku='WindowsServerEssentials',
                version='latest'
            )

            params_create = models.VirtualMachine(
                location=self.region,
                os_profile=self.get_os_profile(),
                hardware_profile=self.get_hardware_profile(),
                network_profile=self.get_network_profile(nic_id),
                storage_profile=storage_profile,
            )

            result_create = virtual_machines_operations.create_or_update(
                self.group_name,
                names.vm,
                params_create,
            )
            result_create.wait()

            params_create = models.VirtualMachineExtension(
                location=self.region,
                publisher='Microsoft.Compute',
                virtual_machine_extension_type='VMAccessAgent',
                type_handler_version='2.0',
                auto_upgrade_minor_version=True,
                settings={},
                protected_settings={},
            )
            result_create = virtual_machine_extensions.create_or_update(
                self.group_name,
                names.vm,
                ext_name,
                params_create,
            )
            result_create.wait()

            result_get = virtual_machine_extensions.get(
                self.group_name,
                names.vm,
                ext_name,
            )
            self.assertEqual(result_get.name, ext_name)

            result_delete = virtual_machine_extensions.delete(
                self.group_name,
                names.vm,
                ext_name,
            )
            result_delete.wait()

    @record
    def test_vm_extension_images(self):
        virtual_machine_images = self.client.virtual_machine_images()
        virtual_machine_extension_images = self.client.virtual_machine_extension_images()
        models = azure.mgmt.compute.models('2016-04-30-preview')

        result_list_pub = virtual_machine_images.list_publishers(
            self.region,
        )

        for res in result_list_pub:
            publisher_name = res.name

            result_list = virtual_machine_extension_images.list_types(
                self.region,
                publisher_name,
            )

            for res in result_list:
                type_name = res.name

                result_list_versions = virtual_machine_extension_images.list_versions(
                    self.region,
                    publisher_name,
                    type_name,
                )

                for res in result_list_versions:
                    version = res.name

                    result_get = virtual_machine_extension_images.get(
                        self.region,
                        publisher_name,
                        type_name,
                        version,
                    )
                    return

    @record
    def test_vm_images(self):
        virtual_machine_images = self.client.virtual_machine_images()

        result_list_pub = virtual_machine_images.list_publishers(
            self.region
        )
        #self.assertEqual(result_list_pub.status_code, HttpStatusCode.OK)
        self.assertGreater(len(result_list_pub), 0)

        for res in result_list_pub:
            publisher_name = res.name

            result_list_offers = virtual_machine_images.list_offers(
                self.region,
                publisher_name
            )
            #self.assertEqual(result_list_offers.status_code, HttpStatusCode.OK)

            for res in result_list_offers:
                offer = res.name

                result_list_skus = virtual_machine_images.list_skus(
                    self.region,
                    publisher_name,
                    offer
                )
                #self.assertEqual(result_list_skus.status_code, HttpStatusCode.OK)

                for res in result_list_skus:
                    skus = res.name

                    result_list = virtual_machine_images.list(
                        self.region,
                        publisher_name,
                        offer,
                        skus
                    )
                    #self.assertEqual(result_list.status_code, HttpStatusCode.OK)

                    for res in result_list:
                        version = res.name

                        result_get = virtual_machine_images.get(
                            self.region,
                            publisher_name,
                            offer,
                            skus,
                            version
                        )
                        #self.assertEqual(result_get.status_code, HttpStatusCode.OK)

                        print('PUBLISHER: {0}, OFFER: {1}, SKUS: {2}, VERSION: {3}'.format(
                            publisher_name,
                            offer,
                            skus,
                            version,
                        ))
                        return

    @record
    def test_availability_sets(self):
        availability_sets_operations = self.client.availability_sets()
        models = azure.mgmt.compute.models('2016-04-30-preview')

        availability_set_name = self.get_resource_name('pyarmset')

        params_create = models.AvailabilitySet(
            location=self.region,
            platform_fault_domain_count=2,
            platform_update_domain_count=4,
            tags={
                'tag1': 'value1',
            },
        )
        result_create = availability_sets_operations.create_or_update(
            self.group_name,
            availability_set_name,
            params_create,
        )
        self.assertEqual(result_create.name, availability_set_name)

        result_get = availability_sets_operations.get(
            self.group_name,
            availability_set_name,
        )
        self.assertEqual(result_get.name, availability_set_name)
        self.assertEqual(
            result_get.platform_fault_domain_count,
            params_create.platform_fault_domain_count,
        )
        self.assertEqual(
            result_get.platform_update_domain_count,
            params_create.platform_update_domain_count,
        )

        result_list = availability_sets_operations.list(
            self.group_name,
        )
        result_list = list(result_list)

        result_list_sizes = availability_sets_operations.list_available_sizes(
            self.group_name,
            availability_set_name,
        )
        result_list_sizes = list(result_list_sizes)

        availability_sets_operations.delete(
            self.group_name,
            availability_set_name,
        )

    @record
    def test_usage(self):
        usages = self.client.usage().list(self.region)
        #self.assertEqual(result_list.status_code, HttpStatusCode.OK)
        usages = list(usages)
        self.assertGreater(len(usages), 0)

    @record
    def test_vm_sizes(self):
        virtual_machine_sizes = self.client.virtual_machine_sizes().list(self.region)
        #self.assertEqual(result_list.status_code, HttpStatusCode.OK)
        virtual_machine_sizes = list(virtual_machine_sizes)
        self.assertGreater(len(virtual_machine_sizes), 0)

    @record
    def test_container(self):
        container_services_operations = self.client.container_services()
        container_name = self.get_resource_name('pycontainer')
        
        # https://msdn.microsoft.com/en-us/library/azure/mt711471.aspx
        async_create = container_services_operations.create_or_update(
            self.group_name,
            container_name,
            {
                'location': self.region,
                "orchestrator_profile": {
                    "orchestrator_type": "DCOS"
                },
                "master_profile": {
                    "count": 1,
                    "dns_prefix": "MasterPrefixTest"
                },
                "agent_pool_profiles": [{
                    "name": "AgentPool1",
                    "count": 3,
                    "vm_size": "Standard_A1",
                        "dns_prefix": "AgentPrefixTest"
                }],
                "linux_profile": {
                    "admin_username": "acslinuxadmin",
                    "ssh": {
                       "public_keys": [{
                            "key_data": "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEAlj9UC6+57XWVu0fd6zqXa256EU9EZdoLGE3TqdZqu9fvUvLQOX2G0d5DmFhDCyTmWLQUx3/ONQ9RotYmHGymBIPQcpx43nnxsuihAILcpGZ5NjCj4IOYnmhdULxN4ti7k00S+udqokrRYpmwt0N4NA4VT9cN+7uJDL8Opqa1FYu0CT/RqSW+3aoQ0nfGj11axoxM37FuOMZ/c7mBSxvuI9NsDmcDQOUmPXjlgNlxrLzf6VcjxnJh4AO83zbyLok37mW/C7CuNK4WowjPO1Ix2kqRHRxBrzxYZ9xqZPc8GpFTw/dxJEYdJ3xlitbOoBoDgrL5gSITv6ESlNqjPk6kHQ== azureuser@linuxvm"
                       }]
                    }
                },
            },
            retries=0
        )
        container = async_create.result()

        container = container_services_operations.get(
            self.group_name,
            container.name
        )

        containers = list(container_services_operations.list_by_resource_group(
            self.group_name
        ))
        self.assertEqual(len(containers), 1)

        containers = list(container_services_operations.list())
        self.assertEqual(len(containers), 1)

        async_delete = container_services_operations.delete(
            self.group_name,
            container.name
        )
        async_delete.wait()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
