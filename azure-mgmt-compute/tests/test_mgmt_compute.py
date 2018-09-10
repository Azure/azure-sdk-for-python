# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

from collections import namedtuple

import azure.mgmt.compute
import azure.mgmt.network.models
import azure.mgmt.storage.models
from devtools_testutils import (
    AzureMgmtTestCase,
    ResourceGroupPreparer,
)

ComputeResourceNames = namedtuple(
    'ComputeResourceNames',
    ['storage', 'vm' ,'network', 'nic', 'subnet'],
)

class MgmtComputeTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtComputeTest, self).setUp()
        self.compute_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )

        self.linux_img_ref_id = "/" + self.compute_client.config.subscription_id + "/services/images/b4590d9e3ed742e4a1d46e5424aa335e__sles12-azure-guest-priority.x86-64-0.4.3-build1.1"
        self.windows_img_ref_id = "/" + self.compute_client.config.subscription_id + "/services/images/a699494373c04fc0bc8f2bb1389d6106__Windows-Server-2012-Datacenter-201503.01-en.us-127GB.vhd"
        if not self.is_playback():
            self.storage_client = self.create_mgmt_client(
                azure.mgmt.storage.StorageManagementClient
            )
            self.network_client = self.create_mgmt_client(
                azure.mgmt.network.NetworkManagementClient
            )

    def get_resource_names(self, base):
        return ComputeResourceNames(
            self.get_resource_name(base + 'stor'),
            self.get_resource_name(base + 'vm'),
            self.get_resource_name(base + 'net'),
            self.get_resource_name(base + 'nic'),
            self.get_resource_name(base + 'sub'),
        )

    def create_storage_account(self, group_name, location, storage_name):
        params_create = azure.mgmt.storage.models.StorageAccountCreateParameters(
            sku=azure.mgmt.storage.models.Sku(name=azure.mgmt.storage.models.SkuName.standard_lrs),
            kind=azure.mgmt.storage.models.Kind.storage,
            location=location
        )
        result_create = self.storage_client.storage_accounts.create(
            group_name,
            storage_name,
            params_create,
        )
        result_create.wait()

    def create_virtual_network(self, group_name, location, network_name, subnet_name):
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
            group_name,
            network_name,
            params_create,
        )
        result_create = azure_operation_poller.result()
        self.assertEqual(result_create.name, network_name)

        result_get = self.network_client.subnets.get(
            group_name,
            network_name,
            subnet_name,
        )
        self.assertEqual(result_get.name, subnet_name)

        return result_get

    def create_network_interface(self, group_name, location, interface_name, subnet):
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
            group_name,
            interface_name,
            params_create,
        )
        result_create = result_create.result()
        self.assertEqual(result_create.name, interface_name)
        return result_create.id

    def get_os_profile(self, group_name):
        virtual_machines_models = self.compute_client.virtual_machines.models
        return virtual_machines_models.OSProfile(
            admin_username='Foo12',
            admin_password='BaR@123' + group_name,
            computer_name='test',
        )

    def get_hardware_profile(self):
        virtual_machines_models = self.compute_client.virtual_machines.models
        return virtual_machines_models.HardwareProfile(
            vm_size=virtual_machines_models.VirtualMachineSizeTypes.standard_a0
        )

    def get_storage_profile(self, os_vhd_uri):
        virtual_machines_models = self.compute_client.virtual_machines.models
        return virtual_machines_models.StorageProfile(
            os_disk=virtual_machines_models.OSDisk(
                caching=virtual_machines_models.CachingTypes.none,
                create_option=virtual_machines_models.DiskCreateOptionTypes.from_image,
                name='test',
                vhd=virtual_machines_models.VirtualHardDisk(
                    uri=os_vhd_uri,
                ),
            ),
        )

    def get_network_profile(self, network_interface_id):
        virtual_machines_models = self.compute_client.virtual_machines.models
        return virtual_machines_models.NetworkProfile(
            network_interfaces=[
                virtual_machines_models.NetworkInterfaceReference(
                    id=network_interface_id,
                ),
            ],
        )

    def get_vhd_uri(self, storage_name, vhd_name):
        return 'https://{0}.blob.core.windows.net/vhds/{1}.vhd'.format(
            storage_name,
            vhd_name,
        )

    @ResourceGroupPreparer()
    def test_virtual_machines_operations(self, resource_group, location):
        virtual_machines_models = self.compute_client.virtual_machines.models
        names = self.get_resource_names('pyvmir')
        os_vhd_uri = self.get_vhd_uri(names.storage, 'osdisk')

        if not self.is_playback():
            self.create_storage_account(resource_group.name, location, names.storage)
            subnet = self.create_virtual_network(resource_group.name, location, names.network, names.subnet)
            nic_id = self.create_network_interface(resource_group.name, location, names.nic, subnet)
        else:
            nic_id = ("/subscriptions/00000000-0000-0000-0000-000000000000"
                      "/resourceGroups/test_mgmt_compute_test_virtual_machines_operations122014cf"
                      "/providers/Microsoft.Network/networkInterfaces/pyvmirnic122014cf")

        storage_profile = self.get_storage_profile(os_vhd_uri)
        storage_profile.image_reference = virtual_machines_models.ImageReference(
            publisher='Canonical',
            offer='UbuntuServer',
            sku='16.04.0-LTS',
            version='latest'
        )

        params_create = virtual_machines_models.VirtualMachine(
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

        # Get by name
        result_get = self.compute_client.virtual_machines.get(
            resource_group.name,
            names.vm
        )
        self.assertEqual(result_get.name, names.vm)
        self.assertIsNone(result_get.instance_view)

        # Get instanceView
        result_iv = self.compute_client.virtual_machines.get(
            resource_group.name,
            names.vm,
            expand=virtual_machines_models.InstanceViewTypes.instance_view
        )
        self.assertTrue(result_iv.instance_view)

        # Deallocate
        async_vm_deallocate = self.compute_client.virtual_machines.deallocate(resource_group.name, names.vm)
        async_vm_deallocate.wait()

        # Start VM
        async_vm_start =self.compute_client.virtual_machines.start(resource_group.name, names.vm)
        async_vm_start.wait()

        # Restart VM
        async_vm_restart = self.compute_client.virtual_machines.restart(resource_group.name, names.vm)
        async_vm_restart.wait()

        # Stop VM
        async_vm_stop = self.compute_client.virtual_machines.power_off(resource_group.name, names.vm)
        async_vm_stop.wait()

        # List in resouce group
        vms_rg = list(self.compute_client.virtual_machines.list(resource_group.name))
        self.assertEqual(len(vms_rg), 1)

        # Delete
        async_vm_delete = self.compute_client.virtual_machines.delete(resource_group.name, names.vm)
        async_vm_delete.wait()

    @ResourceGroupPreparer()
    def test_virtual_machine_capture(self, resource_group, location):
        virtual_machines_models = self.compute_client.virtual_machines.models
        names = self.get_resource_names('pyvmir')
        os_vhd_uri = self.get_vhd_uri(names.storage, 'osdisk')

        if not self.is_playback():
            self.create_storage_account(resource_group.name, location, names.storage)
            subnet = self.create_virtual_network(resource_group.name, location, names.network, names.subnet)
            nic_id = self.create_network_interface(resource_group.name, location, names.nic, subnet)
        else:
            nic_id = ("/subscriptions/00000000-0000-0000-0000-000000000000"
                      "/resourceGroups/test_mgmt_compute_test_virtual_machine_capturec0f9130c"
                      "/providers/Microsoft.Network/networkInterfaces/pyvmirnicc0f9130c")

        storage_profile = self.get_storage_profile(os_vhd_uri)
        storage_profile.image_reference = virtual_machines_models.ImageReference(
            publisher='Canonical',
            offer='UbuntuServer',
            sku='16.04.0-LTS',
            version='latest'
        )

        params_create = virtual_machines_models.VirtualMachine(
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

        # Deallocate
        async_vm_deallocate = self.compute_client.virtual_machines.deallocate(resource_group.name, names.vm)
        async_vm_deallocate.wait()

        # Generalize (possible because deallocated)
        self.compute_client.virtual_machines.generalize(resource_group.name, names.vm)

        # Capture VM (VM must be generalized before)
        async_capture = self.compute_client.virtual_machines.capture(
            resource_group.name,
            names.vm,
            {
                "vhd_prefix":"pslib",
                "destination_container_name":"dest",
                "overwrite_vhds": True
            }
        )
        capture_result = async_capture.result()
        assert capture_result.content_version == "1.0.0.0"

    @ResourceGroupPreparer()
    def test_vm_extensions(self, resource_group, location):
        #WARNING: this test may take 40 mins to complete against live server
        virtual_machines_models = self.compute_client.virtual_machines.models
        names = self.get_resource_names('pyvmext')
        os_vhd_uri = self.get_vhd_uri(names.storage, 'osdisk')
        ext_name = names.vm + 'AccessAgent'

        if not self.is_playback():
            self.create_storage_account(resource_group.name, location, names.storage)
            subnet = self.create_virtual_network(resource_group.name, location, names.network, names.subnet)
            nic_id = self.create_network_interface(resource_group.name, location, names.nic, subnet)
        else:
            nic_id = ("/subscriptions/00000000-0000-0000-0000-000000000000"
                    "/resourceGroups/test_mgmt_compute_test_vm_extensions15a60f10"
                    "/providers/Microsoft.Network/networkInterfaces/pyvmextnic15a60f10")

        storage_profile = self.get_storage_profile(os_vhd_uri)
        storage_profile.image_reference = virtual_machines_models.ImageReference(
            publisher='MicrosoftWindowsServer',
            offer='WindowsServer',
            sku='2016-Datacenter',
            version='latest'
        )

        params_create = virtual_machines_models.VirtualMachine(
            location=location,
            os_profile=self.get_os_profile(resource_group.name),
            hardware_profile=self.get_hardware_profile(),
            network_profile=self.get_network_profile(nic_id),
            storage_profile=storage_profile,
        )

        result_create = self.compute_client.virtual_machines.create_or_update(
            resource_group.name,
            names.vm,
            params_create,
        )
        result_create.wait()

        params_create = virtual_machines_models.VirtualMachineExtension(
            location=location,
            publisher='Microsoft.Compute',
            virtual_machine_extension_type='VMAccessAgent',
            type_handler_version='2.0',
            auto_upgrade_minor_version=True,
            settings={},
            protected_settings={},
        )
        result_create = self.compute_client.virtual_machine_extensions.create_or_update(
            resource_group.name,
            names.vm,
            ext_name,
            params_create,
        )
        result_create.wait()

        result_get = self.compute_client.virtual_machine_extensions.get(
            resource_group.name,
            names.vm,
            ext_name,
        )
        self.assertEqual(result_get.name, ext_name)

        result_delete = self.compute_client.virtual_machine_extensions.delete(
            resource_group.name,
            names.vm,
            ext_name,
        )
        result_delete.wait()

    def test_vm_extension_images(self):
        result_list_pub = self.compute_client.virtual_machine_images.list_publishers(
            self.region,
        )

        for res in result_list_pub:
            publisher_name = res.name

            result_list = self.compute_client.virtual_machine_extension_images.list_types(
                self.region,
                publisher_name,
            )

            for res in result_list:
                type_name = res.name

                result_list_versions = self.compute_client.virtual_machine_extension_images.list_versions(
                    self.region,
                    publisher_name,
                    type_name,
                )

                for res in result_list_versions:
                    version = res.name

                    result_get = self.compute_client.virtual_machine_extension_images.get(
                        self.region,
                        publisher_name,
                        type_name,
                        version,
                    )
                    return

    def test_vm_images(self):
        location = "westus"
        result_list_pub = self.compute_client.virtual_machine_images.list_publishers(
            location
        )
        self.assertGreater(len(result_list_pub), 0)

        for res in result_list_pub:
            publisher_name = res.name

            result_list_offers = self.compute_client.virtual_machine_images.list_offers(
                location,
                publisher_name
            )

            for res in result_list_offers:
                offer = res.name

                result_list_skus = self.compute_client.virtual_machine_images.list_skus(
                    location,
                    publisher_name,
                    offer
                )

                for res in result_list_skus:
                    skus = res.name

                    result_list = self.compute_client.virtual_machine_images.list(
                        location,
                        publisher_name,
                        offer,
                        skus
                    )

                    for res in result_list:
                        version = res.name

                        result_get = self.compute_client.virtual_machine_images.get(
                            location,
                            publisher_name,
                            offer,
                            skus,
                            version
                        )

                        print('PUBLISHER: {0}, OFFER: {1}, SKUS: {2}, VERSION: {3}'.format(
                            publisher_name,
                            offer,
                            skus,
                            version,
                        ))
                        return

    @ResourceGroupPreparer()
    def test_availability_sets(self, resource_group, location):
        availability_sets_models = self.compute_client.availability_sets.models
        availability_set_name = self.get_resource_name('pyarmset')

        params_create = availability_sets_models.AvailabilitySet(
            location=location,
            platform_fault_domain_count=2,
            platform_update_domain_count=4,
            tags={
                'tag1': 'value1',
            },
        )
        result_create = self.compute_client.availability_sets.create_or_update(
            resource_group.name,
            availability_set_name,
            params_create,
        )
        self.assertEqual(result_create.name, availability_set_name)

        result_get = self.compute_client.availability_sets.get(
            resource_group.name,
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

        result_list = self.compute_client.availability_sets.list(
            resource_group.name,
        )
        result_list = list(result_list)

        result_list_sizes = self.compute_client.availability_sets.list_available_sizes(
            resource_group.name,
            availability_set_name,
        )
        result_list_sizes = list(result_list_sizes)

        self.compute_client.availability_sets.delete(
            resource_group.name,
            availability_set_name,
        )

    def test_usage(self):
        location = "westus"
        usages = list(self.compute_client.usage.list(location))
        self.assertGreater(len(usages), 0)

    def test_vm_sizes(self):
        location = "westus"
        virtual_machine_sizes = list(self.compute_client.virtual_machine_sizes.list(location))
        self.assertGreater(len(virtual_machine_sizes), 0)

    def test_run_command(self):
        # FIXME, test unfinished
        run_commands_models = self.compute_client.virtual_machines.models

        run_command_parameters = run_commands_models.RunCommandInput(
            command_id="RunShellScript",
            script=[
                'echo $1 $2'
            ],
            parameters=[
                run_commands_models.RunCommandInputParameter(name="arg1", value="hello"),
                run_commands_models.RunCommandInputParameter(name="arg2", value="world"),
            ]
        )

        run_command_parameters = {
            'command_id': 'RunShellScript',
            'script': [
                'echo $arg1'
            ],
            'parameters': [
                {'name':"arg1", 'value':"hello world"}
            ]
        }

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
