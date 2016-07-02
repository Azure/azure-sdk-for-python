# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import unittest

from collections import namedtuple

import azure.mgmt.compute.models
import azure.mgmt.network.models
import azure.mgmt.storage.models
from azure.mgmt.compute.models import InstanceViewTypes
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase

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
        self.storage_client = self.create_mgmt_client(
            azure.mgmt.storage.StorageManagementClient
        )
        self.network_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )

        self.linux_img_ref_id = "/" + self.compute_client.config.subscription_id + "/services/images/b4590d9e3ed742e4a1d46e5424aa335e__sles12-azure-guest-priority.x86-64-0.4.3-build1.1"
        self.windows_img_ref_id = "/" + self.compute_client.config.subscription_id + "/services/images/a699494373c04fc0bc8f2bb1389d6106__Windows-Server-2012-Datacenter-201503.01-en.us-127GB.vhd"

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
            dhcp_options=azure.mgmt.network.models.DhcpOptions(
                dns_servers=[
                    '10.1.1.1',
                    '10.1.2.4',
                ],
            ),
            subnets=[
                azure.mgmt.network.models.Subnet(
                    name=subnet_name,
                    address_prefix='10.0.1.0/24',
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

        result_get = self.network_client.network_interfaces.get(
            self.group_name,
            interface_name,
        )
        self.assertEqual(result_get.name, interface_name)

        return result_get.id

    def get_os_profile(self):
       return azure.mgmt.compute.models.OSProfile(
           admin_username='Foo12',
           admin_password='BaR@123' + self.group_name,
           computer_name='test',
       )

    def get_hardware_profile(self):
        return azure.mgmt.compute.models.HardwareProfile(
            vm_size=azure.mgmt.compute.models.VirtualMachineSizeTypes.standard_a0
        )

    def get_storage_profile(self, os_vhd_uri):
        return azure.mgmt.compute.models.StorageProfile(
            os_disk=azure.mgmt.compute.models.OSDisk(
                caching=azure.mgmt.compute.models.CachingTypes.none,
                create_option=azure.mgmt.compute.models.DiskCreateOptionTypes.from_image,
                name='test',
                vhd=azure.mgmt.compute.models.VirtualHardDisk(
                    uri=os_vhd_uri,
                ),
            ),
        )

    def get_network_profile(self, network_interface_id):
        return azure.mgmt.compute.models.NetworkProfile(
            network_interfaces=[
                azure.mgmt.compute.models.NetworkInterfaceReference(
                    id=network_interface_id,
                ),
            ],
        )

    def get_vhd_uri(self, storage_name, vhd_name):
        return 'https://{0}.blob.core.windows.net/vhds/{1}.vhd'.format(
            storage_name,
            vhd_name,
        )

    @record
    def test_vms_with_image_reference(self):
        self.create_resource_group()

        names = self.get_resource_names('pyvmir')
        os_vhd_uri = self.get_vhd_uri(names.storage, 'osdisk')

        self.create_storage_account(names.storage)
        subnet = self.create_virtual_network(names.network, names.subnet)
        nic_id = self.create_network_interface(names.nic, subnet)

        storage_profile = self.get_storage_profile(os_vhd_uri)
        storage_profile.image_reference = azure.mgmt.compute.models.ImageReference(
            publisher='Canonical',
            offer='UbuntuServer',
            sku='15.10',
            version='15.10.201603150',
        )

        params_create = azure.mgmt.compute.models.VirtualMachine(
            location=self.region,
            os_profile=self.get_os_profile(),
            hardware_profile=self.get_hardware_profile(),
            network_profile=self.get_network_profile(nic_id),
            storage_profile=storage_profile,
        )

        result_create = self.compute_client.virtual_machines.create_or_update(
            self.group_name,
            names.vm,
            params_create,
        )
        vm_result = result_create.result()
        self.assertEqual(vm_result.name, names.vm)
        
        result_get = self.compute_client.virtual_machines.get(
            self.group_name,
            names.vm
        )
        self.assertEqual(result_get.name, names.vm)
        self.assertIsNone(result_get.instance_view)
        result_iv = self.compute_client.virtual_machines.get(
            self.group_name,
            names.vm,
            expand=InstanceViewTypes.instance_view
        )
        self.assertTrue(result_iv.instance_view)


    @unittest.skip("reference_uri seems to be not supported in new ARM")
    @record
    def test_vm_extensions(self):
        #WARNING: this test may take 40 mins to complete against live server
        self.create_resource_group()

        names = self.get_resource_names('pyvmext')
        os_vhd_uri = self.get_vhd_uri(names.storage, 'osdisk')
        ext_name = 'extension1'

        self.create_storage_account(names.storage)
        subnet = self.create_virtual_network(names.network, names.subnet)
        nic_id = self.create_network_interface(names.nic, subnet)

        storage_profile = self.get_storage_profile(os_vhd_uri)
        storage_profile.source_image = azure.mgmt.compute.models.SourceImageReference(
            reference_uri=self.windows_img_ref_id,
        )

        params_create = azure.mgmt.compute.models.VirtualMachine(
            location=self.region,
            name=names.vm,
            type='Microsoft.Compute/virtualMachines', # don't know if needed
            os_profile=self.get_os_profile(),
            hardware_profile=self.get_hardware_profile(),
            network_profile=self.get_network_profile(nic_id),
            storage_profile=storage_profile,
        )

        result_create = self.compute_client.virtual_machines.create_or_update(
            self.group_name,
            params_create,
        )
        #self.assertEqual(result_create.status_code, HttpStatusCode.OK)

        params_create = azure.mgmt.compute.models.VirtualMachineExtension(
            location=self.region,
            name=ext_name,
            publisher='Microsoft.Compute',
            extension_type='VMAccessAgent',
            type_handler_version='2.0',
            auto_upgrade_minor_version=True,
            settings='{}',
            protected_settings='{}',
            tags={
                'tag1': 'value1',
            },
        )
        result_create = self.compute_client.virtual_machine_extensions.create_or_update(
            self.group_name,
            names.vm,
            params_create,
        )
        #self.assertEqual(result_create.status_code, HttpStatusCode.OK)

        result_get = self.compute_client.virtual_machine_extensions.get(
            self.group_name,
            names.vm,
            ext_name,
        )
        self.assertEqual(result_get.status_code, HttpStatusCode.OK)

        result_get_view = self.compute_client.virtual_machine_extensions.get_with_instance_view(
            self.group_name,
            names.vm,
            ext_name,
        )
        #self.assertEqual(result_get.status_code, HttpStatusCode.OK)

        result_delete = self.compute_client.virtual_machine_extensions.delete(
            self.group_name,
            names.vm,
            ext_name,
        )
        #self.assertEqual(result_get.status_code, HttpStatusCode.OK)

    @record
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

    @record
    def test_vm_images(self):
        result_list_pub = self.compute_client.virtual_machine_images.list_publishers(
            self.region
        )
        #self.assertEqual(result_list_pub.status_code, HttpStatusCode.OK)
        self.assertGreater(len(result_list_pub), 0)

        for res in result_list_pub:
            publisher_name = res.name

            result_list_offers = self.compute_client.virtual_machine_images.list_offers(
                self.region,
                publisher_name
            )
            #self.assertEqual(result_list_offers.status_code, HttpStatusCode.OK)

            for res in result_list_offers:
                offer = res.name

                result_list_skus = self.compute_client.virtual_machine_images.list_skus(
                    self.region,
                    publisher_name,
                    offer
                )
                #self.assertEqual(result_list_skus.status_code, HttpStatusCode.OK)

                for res in result_list_skus:
                    skus = res.name

                    result_list = self.compute_client.virtual_machine_images.list(
                        self.region,
                        publisher_name,
                        offer,
                        skus
                    )
                    #self.assertEqual(result_list.status_code, HttpStatusCode.OK)

                    for res in result_list:
                        version = res.name

                        result_get = self.compute_client.virtual_machine_images.get(
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
        self.create_resource_group()

        availability_set_name = self.get_resource_name('pyarmset')

        params_create = azure.mgmt.compute.models.AvailabilitySet(
            location=self.region,
            platform_fault_domain_count=2,
            platform_update_domain_count=4,
            statuses=[
                azure.mgmt.compute.models.InstanceViewStatus(
                    code='test1',
                    display_status='test1 display',
                    message='test1 message',
                ),
                azure.mgmt.compute.models.InstanceViewStatus(
                    code='test2',
                    display_status='test2 display',
                    message='test2 message',
                ),
            ],
            tags={
                'tag1': 'value1',
            },
        )
        result_create = self.compute_client.availability_sets.create_or_update(
            self.group_name,
            availability_set_name,
            params_create,
        )
        self.assertEqual(result_create.name, availability_set_name)

        result_get = self.compute_client.availability_sets.get(
            self.group_name,
            availability_set_name,
        )
        self.assertEqual(result_get.name, availability_set_name)
        #TODO: error, we get 0 back, not 2
        #self.assertEqual(
        #    len(result_get.statuses),
        #    len(params_create.statuses),
        #)
        #self.assertEqual(
        #    result_get.statuses[0].code,
        #    view_status1.code,
        #)
        #self.assertEqual(
        #    result_get.availability_set.statuses[1].code,
        #    view_status2.code,
        #)
        self.assertEqual(
            result_get.platform_fault_domain_count,
            params_create.platform_fault_domain_count,
        )
        self.assertEqual(
            result_get.platform_update_domain_count,
            params_create.platform_update_domain_count,
        )

        result_list = self.compute_client.availability_sets.list(
            self.group_name,
        )
        #self.assertEqual(result_list.status_code, HttpStatusCode.OK)
        self.assertIsNotNone(result_list)

        result_list_sizes = self.compute_client.availability_sets.list_available_sizes(
            self.group_name,
            availability_set_name,
        )
        #self.assertEqual(result_list_sizes.status_code, HttpStatusCode.OK)
        self.assertIsNotNone(result_list_sizes)

        self.compute_client.availability_sets.delete(
            self.group_name,
            availability_set_name,
        )
        #self.assertEqual(result_delete.status_code, HttpStatusCode.OK)

    @record
    def test_usage(self):
        usages = self.compute_client.usage.list(self.region)
        #self.assertEqual(result_list.status_code, HttpStatusCode.OK)
        usages = list(usages)
        self.assertGreater(len(usages), 0)

    @record
    def test_vm_sizes(self):
        virtual_machine_sizes = self.compute_client.virtual_machine_sizes.list(self.region)
        #self.assertEqual(result_list.status_code, HttpStatusCode.OK)
        virtual_machine_sizes = list(virtual_machine_sizes)
        self.assertGreater(len(virtual_machine_sizes), 0)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
