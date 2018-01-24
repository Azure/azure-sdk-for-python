# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

from collections import namedtuple

from msrestazure.azure_exceptions import CloudError

import azure.mgmt.compute
import azure.mgmt.network.models

from devtools_testutils import (
    AzureMgmtTestCase,
    ResourceGroupPreparer,
)

ComputeResourceNames = namedtuple(
    'ComputeResourceNames',
    ['storage', 'vm' ,'network', 'nic', 'subnet'],
)

class MgmtManagedDisksTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtManagedDisksTest, self).setUp()
        self.compute_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )
        if not self.is_playback():
            self.network_client = self.create_mgmt_client(
                azure.mgmt.network.NetworkManagementClient
            )

    @ResourceGroupPreparer()
    def test_empty_md(self, resource_group, location):
        '''Create an empty Managed Disk.'''
        DiskCreateOption = self.compute_client.disks.models.DiskCreateOption

        async_creation = self.compute_client.disks.create_or_update(
            resource_group.name,
            'my_disk_name',
            {
                'location': location,
                'disk_size_gb': 20,
                'creation_data': {
                    'create_option': DiskCreateOption.empty
                }
            }
        )
        disk_resource = async_creation.result()

    @ResourceGroupPreparer()
    def test_md_from_storage_blob(self, resource_group, location):
        '''Create a Managed Disk from Blob Storage.'''
        DiskCreateOption = self.compute_client.disks.models.DiskCreateOption

        async_creation = self.compute_client.disks.create_or_update(
            resource_group.name,
            'my_disk_name',
            {
                'location': location,
                'creation_data': {
                    'create_option': DiskCreateOption.import_enum,
                    'source_uri': 'https://mystorageaccount.blob.core.windows.net/inputtestdatadonotdelete/ubuntu.vhd'
                }
            }
        )
        disk_resource = async_creation.result()

    @ResourceGroupPreparer()
    def test_md_from_md_id(self, resource_group, location):
        '''Create a Managed Disk from an existing image.'''
        DiskCreateOption = self.compute_client.disks.models.DiskCreateOption

        # Out of sample, the initial creation
        async_creation = self.compute_client.disks.create_or_update(
            resource_group.name,
            'myImageDisk',
            {
                'location': location,
                'disk_size_gb': 20,
                'creation_data': {
                    'create_option': DiskCreateOption.empty
                }
            }
        )
        disk_resource = async_creation.result()

        # Sample from here

        # You can also build the id yourself: '<...id...>/Microsoft.Compute/disks/mdvm1_OsDisk_1_<guid>'
        managed_disk = self.compute_client.disks.get(resource_group.name, 'myImageDisk')

        async_creation = self.compute_client.disks.create_or_update(
            resource_group.name,
            'my_disk_name',
            {
                'location': location,
                'creation_data': {
                    'create_option': DiskCreateOption.copy,
                    'source_resource_id': managed_disk.id
                }
            }
        )
        disk_resource = async_creation.result()

    @ResourceGroupPreparer()
    def test_create_vm_implicit_md(self, resource_group, location):
        '''Create a VM with implicit MD'''
        virtual_machine_models = self.compute_client.virtual_machines.models
        disks_models = self.compute_client.disks.models

        names = self.get_resource_names('pyvmir')
        if not self.is_playback():
            subnet = self.create_virtual_network(resource_group.name, location, names.network, names.subnet)
            nic_id = self.create_network_interface(resource_group.name, location, names.nic, subnet)
        else:
            nic_id = ("/subscriptions/00000000-0000-0000-0000-000000000000"
                      "/resourceGroups/test_mgmt_compute_test_virtual_machines_operations122014cf"
                      "/providers/Microsoft.Network/networkInterfaces/pyvmirnic122014cf")

        storage_profile = virtual_machine_models.StorageProfile(
            image_reference = virtual_machine_models.ImageReference(
                publisher='Canonical',
                offer='UbuntuServer',
                sku='16.04.0-LTS',
                version='latest'
            )
        )

        params_create = virtual_machine_models.VirtualMachine(
            location=location,
            os_profile=self.get_os_profile(resource_group.name),
            hardware_profile=self.get_hardware_profile(),
            network_profile=self.get_network_profile(nic_id),
            storage_profile=storage_profile,
        )

        # Create VM test
        result_create = self.compute_client.virtual_machines.create_or_update(
            resource_group.name,
            names.vm,
            params_create,
        )
        vm_result = result_create.result()
        self.assertEqual(vm_result.name, names.vm)

        # Attach a new disk
        async_creation = self.compute_client.disks.create_or_update(
            resource_group.name,
            'mySecondDisk',
            {
                'location': self.region,
                'disk_size_gb': 20,
                'creation_data': {
                    'create_option': disks_models.DiskCreateOption.empty
                }
            }
        )
        disk_resource = async_creation.result()

        vm_result.storage_profile.data_disks.append({
            'lun': 12, # You choose the value, depending of what is available for you
            'name': disk_resource.name,
            'create_option': virtual_machine_models.DiskCreateOptionTypes.attach,
            'managed_disk': {
                'id': disk_resource.id
            }
        })
        result_create = self.compute_client.virtual_machines.create_or_update(
            resource_group.name,
            names.vm,
            vm_result,
        )
        result_create.wait()


    @ResourceGroupPreparer()
    def test_resize_md(self, resource_group, location):
        '''Resizing a Managed Disk'''
        # Out of sample, the initial creation
        disks_models = self.compute_client.disks.models
        async_creation = self.compute_client.disks.create_or_update(
            resource_group.name,
            'myDisk',
            {
                'location': location,
                'disk_size_gb': 20,
                'creation_data': {
                    'create_option': disks_models.DiskCreateOption.empty
                }
            }
        )
        async_creation.wait()

        # Sample from here
        managed_disk = self.compute_client.disks.get(resource_group.name, 'myDisk')
        managed_disk.disk_size_gb = 25
        async_update = self.compute_client.disks.create_or_update(
            resource_group.name,
            'myDisk',
            managed_disk
        )
        async_update.wait()

    @ResourceGroupPreparer()
    def test_change_account_type(self, resource_group, location):
        '''Change account type of a Managed Disk'''
        # Out of sample, the initial creation
        DiskCreateOption = self.compute_client.disks.models.DiskCreateOption
        async_creation = self.compute_client.disks.create_or_update(
            resource_group.name,
            'myDisk',
            {
                'location': location,
                'disk_size_gb': 20,
                'creation_data': {
                    'create_option': DiskCreateOption.empty
                }
            }
        )
        disk_resource = async_creation.result()

        # Sample from here
        StorageAccountTypes = self.compute_client.disks.models.StorageAccountTypes
        managed_disk = self.compute_client.disks.get(resource_group.name, 'myDisk')
        managed_disk.account_type = StorageAccountTypes.standard_lrs
        async_update = self.compute_client.disks.create_or_update(
            resource_group.name,
            'myDisk',
            managed_disk
        )
        async_update.wait()

    @ResourceGroupPreparer()
    def test_create_image_from_blob(self, resource_group, location):
        async_create_image = self.compute_client.images.create_or_update(
            resource_group.name,
            'myImage',
            {
                'location': location,
                'storage_profile': {
                    'os_disk': {
                        'os_type': 'Linux',
                        'os_state': "Generalized",
                        'blob_uri': 'https://mystorageaccount.blob.core.windows.net/inputtestdatadonotdelete/ubuntu.vhd',
                        'caching': "ReadWrite",
                    }
                }
            }
        )
        image = async_create_image.result()

    @ResourceGroupPreparer()
    def test_create_snapshot(self, resource_group, location):
        # Out of sample, the initial creation
        DiskCreateOption = self.compute_client.disks.models.DiskCreateOption
        async_creation = self.compute_client.disks.create_or_update(
            resource_group.name,
            'myDisk',
            {
                'location': location,
                'disk_size_gb': 20,
                'creation_data': {
                    'create_option': DiskCreateOption.empty
                }
            }
        )
        disk_resource = async_creation.result()

        # Sample from here
        managed_disk = self.compute_client.disks.get(resource_group.name, 'myDisk')
        async_snapshot_creation = self.compute_client.snapshots.create_or_update(
                resource_group.name,
                'mySnapshot',
                {
                    'location': self.region,
                    'creation_data': {
                        'create_option': 'Copy',
                        'source_uri': managed_disk.id
                    }
                }
            )
        snapshot = async_snapshot_creation.result()

    @ResourceGroupPreparer()
    def test_create_virtual_machine_scale_set(self, resource_group, location):

        names = self.get_resource_names('pyvmir')
        if not self.is_playback():
            subnet = self.create_virtual_network(resource_group.name, location, names.network, names.subnet)
            subnet_id = subnet.id
        else:
            subnet_id = ("/subscriptions/00000000-0000-0000-0000-000000000000"
                         "/resourceGroups/test_mgmt_compute_test_virtual_machines_operations122014cf"
                         "/providers/Microsoft.Network/networkInterfaces/pyvmirnic122014cf")

        naming_infix = "PyTestInfix"
        vmss_parameters = {
            'location': location,
            "overprovision": True,
            "upgrade_policy": {
                "mode": "Manual"
            },
            'sku': {
                'name': 'Standard_A1',
                'tier': 'Standard',
                'capacity': 5
            },
            'virtual_machine_profile': {
                'storage_profile': {
                    'image_reference': {
                        "publisher": "Canonical",
                        "offer": "UbuntuServer",
                        "sku": "16.04.0-LTS",
                        "version": "latest"
                    }
                },
                'os_profile': {
                    'computer_name_prefix': naming_infix,
                    'admin_username': 'Foo12',
                    'admin_password': 'BaR@123!!!!',
                },
                'network_profile': {
                    'network_interface_configurations' : [{
                        'name': naming_infix + 'nic',
                        "primary": True,
                        'ip_configurations': [{
                            'name': naming_infix + 'ipconfig',
                            'subnet': {
                                'id': subnet_id
                            } 
                        }]
                    }]
                }
            }
        }

        # Create VMSS test
        result_create = self.compute_client.virtual_machine_scale_sets.create_or_update(
            resource_group.name,
            names.vm,
            vmss_parameters,
        )
        vmss_result = result_create.result()
        self.assertEqual(vmss_result.name, names.vm)

    @ResourceGroupPreparer()
    def test_list_disks(self, resource_group, location):
        disks = list(self.compute_client.disks.list_by_resource_group(resource_group.name))
        self.assertEqual(len(disks), 0)

    def test_list_disks_fake(self):
        with self.assertRaises(CloudError) as cm:
            list(self.compute_client.disks.list_by_resource_group("fakename"))
        self.assertIn("Resource group 'fakename' could not be found", cm.exception.message)

    def get_resource_names(self, base):
        return ComputeResourceNames(
            self.get_resource_name(base + 'stor'),
            self.get_resource_name(base + 'vm'),
            self.get_resource_name(base + 'net'),
            self.get_resource_name(base + 'nic'),
            self.get_resource_name(base + 'sub'),
        )

    def create_virtual_network(self, resource_group_name, location, network_name, subnet_name):
        params_create = azure.mgmt.network.models.VirtualNetwork(
            location=location,
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
            resource_group_name,
            network_name,
            params_create,
        )
        result_create = azure_operation_poller.result()
        self.assertEqual(result_create.name, network_name)

        result_get = self.network_client.subnets.get(
            resource_group_name,
            network_name,
            subnet_name,
        )
        self.assertEqual(result_get.name, subnet_name)

        return result_get

    def create_network_interface(self, resource_group_name, location, interface_name, subnet):
        config_name = 'pyarmconfig'

        params_create = azure.mgmt.network.models.NetworkInterface(
            location=location,
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
            resource_group_name,
            interface_name,
            params_create,
        )
        result_create = result_create.result()
        self.assertEqual(result_create.name, interface_name)
        return result_create.id

    def get_os_profile(self, resource_group_name):
       virtual_machine_models = self.compute_client.virtual_machines.models
       return virtual_machine_models.OSProfile(
           admin_username='Foo12',
           admin_password='BaR@123' + resource_group_name,
           computer_name='test',
       )

    def get_hardware_profile(self):
        virtual_machine_models = self.compute_client.virtual_machines.models
        return virtual_machine_models.HardwareProfile(
            vm_size=virtual_machine_models.VirtualMachineSizeTypes.standard_a0
        )

    def get_network_profile(self, network_interface_id):
        virtual_machine_models = self.compute_client.virtual_machines.models
        return virtual_machine_models.NetworkProfile(
            network_interfaces=[
                virtual_machine_models.NetworkInterfaceReference(
                    id=network_interface_id,
                ),
            ],
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
