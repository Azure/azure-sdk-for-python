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

import azure.mgmt.compute
import azure.mgmt.network
import azure.mgmt.storage
from .common_recordingtestcase import record
from .mgmt_testcase import HttpStatusCode, AzureMgmtTestCase

ComputeResourceNames = namedtuple(
    'ComputeResourceNames',
    ['storage', 'vm' ,'network', 'nic', 'subnet'],
)

class MgmtComputeTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtComputeTest, self).setUp()
        self.compute_client = self.create_mgmt_client(azure.mgmt.compute.ComputeManagementClient)
        self.storage_client = self.create_mgmt_client(azure.mgmt.storage.StorageManagementClient)
        self.network_client = self.create_mgmt_client(azure.mgmt.network.NetworkResourceProviderClient)

        self.linux_img_ref_id = "/" + self.compute_client.credentials.subscription_id + "/services/images/b4590d9e3ed742e4a1d46e5424aa335e__sles12-azure-guest-priority.x86-64-0.4.3-build1.1"
        self.windows_img_ref_id = "/" + self.compute_client.credentials.subscription_id + "/services/images/a699494373c04fc0bc8f2bb1389d6106__Windows-Server-2012-Datacenter-201503.01-en.us-127GB.vhd"

    def get_resource_names(self, base):
        return ComputeResourceNames(
            self.get_resource_name(base + 'stor'),
            self.get_resource_name(base + 'vm'),
            self.get_resource_name(base + 'net'),
            self.get_resource_name(base + 'nic'),
            self.get_resource_name(base + 'sub'),
        )

    def create_storage_account(self, storage_name):
        params_create = azure.mgmt.storage.StorageAccountCreateParameters(
            location=self.region,
            account_type=azure.mgmt.storage.AccountType.standard_lrs,
        )
        result_create = self.storage_client.storage_accounts.create(
            self.group_name,
            storage_name,
            params_create,
        )
        self.assertEqual(result_create.status_code, HttpStatusCode.OK)

    def create_virtual_network(self, network_name, subnet_name):
        params_create = azure.mgmt.network.VirtualNetwork(
            location=self.region,
            address_space=azure.mgmt.network.AddressSpace(
                address_prefixes=[
                    '10.0.0.0/16',
                ],
            ),
            dhcp_options=azure.mgmt.network.DhcpOptions(
                dns_servers=[
                    '10.1.1.1',
                    '10.1.2.4',
                ],
            ),
            subnets=[
                azure.mgmt.network.Subnet(
                    name=subnet_name,
                    address_prefix='10.0.1.0/24',
                ),
            ],
        )
        result_create = self.network_client.virtual_networks.create_or_update(
            self.group_name,
            network_name,
            params_create,
        )
        self.assertEqual(result_create.status_code, HttpStatusCode.OK)

        result_get = self.network_client.subnets.get(
            self.group_name,
            network_name,
            subnet_name,
        )
        self.assertEqual(result_get.status_code, HttpStatusCode.OK)

        return result_get.subnet

    def create_network_interface(self, interface_name, subnet):
        config_name = 'pyarmconfig'

        params_create = azure.mgmt.network.NetworkInterface(
            name=interface_name,
            location=self.region,
            ip_configurations=[
                azure.mgmt.network.NetworkInterfaceIpConfiguration(
                    name=config_name,
                    private_ip_allocation_method=azure.mgmt.network.IpAllocationMethod.dynamic,
                    subnet=subnet,
                ),
            ],
        )
        result_create = self.network_client.network_interfaces.create_or_update(
            self.group_name,
            interface_name,
            params_create,
        )
        self.assertEqual(result_create.status_code, HttpStatusCode.OK)

        result_get = self.network_client.network_interfaces.get(
            self.group_name,
            interface_name,
        )
        self.assertEqual(result_get.status_code, HttpStatusCode.OK)

        return result_get.network_interface.id

    def get_os_profile(self):
       return azure.mgmt.compute.OSProfile(
           admin_username='Foo12',
           admin_password='BaR@123' + self.group_name,
           computer_name='test',
       )

    def get_hardware_profile(self):
        return azure.mgmt.compute.HardwareProfile(
            virtual_machine_size=azure.mgmt.compute.VirtualMachineSizeTypes.standard_a0
        )

    def get_storage_profile(self, os_vhd_uri):
        return azure.mgmt.compute.StorageProfile(
            os_disk=azure.mgmt.compute.OSDisk(
                caching=azure.mgmt.compute.CachingTypes.none,
                create_option=azure.mgmt.compute.DiskCreateOptionTypes.from_image,
                name='test',
                virtual_hard_disk=azure.mgmt.compute.VirtualHardDisk(
                    uri=os_vhd_uri,
                ),
            ),
        )

    def get_network_profile(self, network_interface_id):
        return azure.mgmt.compute.NetworkProfile(
            network_interfaces=[
                azure.mgmt.compute.NetworkInterfaceReference(
                    reference_uri=network_interface_id,
                ),
            ],
        )

    def get_vhd_uri(self, storage_name, vhd_name):
        return 'https://{0}.blob.core.windows.net/vhds/{1}.vhd'.format(
            storage_name,
            vhd_name,
        )

    @record
    def test_vms_with_source_image(self):
        self.create_resource_group()

        names = self.get_resource_names('pyvmsm')
        os_vhd_uri = self.get_vhd_uri(names.storage, 'osdisk')

        self.create_storage_account(names.storage)
        subnet = self.create_virtual_network(names.network, names.subnet)
        nic_id = self.create_network_interface(names.nic, subnet)

        storage_profile = self.get_storage_profile(os_vhd_uri)
        storage_profile.source_image = azure.mgmt.compute.SourceImageReference(
            reference_uri=self.windows_img_ref_id,
        )

        params_create = azure.mgmt.compute.VirtualMachine(
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
        self.assertEqual(result_create.status_code, HttpStatusCode.OK)

    @record
    def test_vms_with_image_reference(self):
        self.create_resource_group()

        names = self.get_resource_names('pyvmir')
        os_vhd_uri = self.get_vhd_uri(names.storage, 'osdisk')

        self.create_storage_account(names.storage)
        subnet = self.create_virtual_network(names.network, names.subnet)
        nic_id = self.create_network_interface(names.nic, subnet)

        storage_profile = self.get_storage_profile(os_vhd_uri)
        storage_profile.image_reference = azure.mgmt.compute.ImageReference(
            publisher='Canonical',
            offer='UbuntuServer',
            sku='15.04',
            version='15.04.201504220',
        )

        params_create = azure.mgmt.compute.VirtualMachine(
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
        self.assertEqual(result_create.status_code, HttpStatusCode.OK)

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
        storage_profile.source_image = azure.mgmt.compute.SourceImageReference(
            reference_uri=self.windows_img_ref_id,
        )

        params_create = azure.mgmt.compute.VirtualMachine(
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
        self.assertEqual(result_create.status_code, HttpStatusCode.OK)

        params_create = azure.mgmt.compute.VirtualMachineExtension(
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
        self.assertEqual(result_create.status_code, HttpStatusCode.OK)

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
        self.assertEqual(result_get.status_code, HttpStatusCode.OK)

        result_delete = self.compute_client.virtual_machine_extensions.delete(
            self.group_name,
            names.vm,
            ext_name,
        )
        self.assertEqual(result_get.status_code, HttpStatusCode.OK)

    @record
    def test_vm_extension_images(self):
        result_list_pub = self.compute_client.virtual_machine_images.list_publishers(
            azure.mgmt.compute.VirtualMachineImageListPublishersParameters(
                location=self.region,
            ),
        )
        self.assertEqual(result_list_pub.status_code, HttpStatusCode.OK)

        for res in result_list_pub.resources:
            publisher_name = res.name

            result_list = self.compute_client.virtual_machine_extension_images.list_types(
                azure.mgmt.compute.VirtualMachineExtensionImageListTypesParameters(
                    location=self.region,
                    publisher_name=publisher_name,
                ),
            )
            self.assertEqual(result_list.status_code, HttpStatusCode.OK)

            for res in result_list.resources:
                type_name = res.name

                result_list_versions = self.compute_client.virtual_machine_extension_images.list_versions(
                    azure.mgmt.compute.VirtualMachineExtensionImageListVersionsParameters(
                        location=self.region,
                        publisher_name=publisher_name,
                        type=type_name,
                    ),
                )
                self.assertEqual(result_list.status_code, HttpStatusCode.OK)

                for res in result_list_versions.resources:
                    version = res.name

                    result_get = self.compute_client.virtual_machine_extension_images.get(
                        azure.mgmt.compute.VirtualMachineExtensionImageGetParameters(
                            location=self.region,
                            publisher_name=publisher_name,
                            type=type_name,
                            version=version,
                        ),
                    )
                    self.assertEqual(result_get.status_code, HttpStatusCode.OK)

                    print('PUBLISHER: {0}, TYPE: {1}, VERSION: {2}'.format(
                        publisher_name,
                        type_name,
                        version,
                    ))

    @record
    def test_vm_images(self):
        result_list_pub = self.compute_client.virtual_machine_images.list_publishers(
            azure.mgmt.compute.VirtualMachineImageListPublishersParameters(
                location=self.region,
            ),
        )
        self.assertEqual(result_list_pub.status_code, HttpStatusCode.OK)
        self.assertGreater(len(result_list_pub.resources), 0)

        for res in result_list_pub.resources:
            publisher_name = res.name

            result_list_offers = self.compute_client.virtual_machine_images.list_offers(
                azure.mgmt.compute.VirtualMachineImageListOffersParameters(
                    location=self.region,
                    publisher_name=publisher_name,
                ),
            )
            self.assertEqual(result_list_offers.status_code, HttpStatusCode.OK)

            for res in result_list_offers.resources:
                offer = res.name

                result_list_skus = self.compute_client.virtual_machine_images.list_skus(
                    azure.mgmt.compute.VirtualMachineImageListSkusParameters(
                        location=self.region,
                        publisher_name=publisher_name,
                        offer=offer,
                    ),
                )
                self.assertEqual(result_list_skus.status_code, HttpStatusCode.OK)

                for res in result_list_skus.resources:
                    skus = res.name

                    result_list = self.compute_client.virtual_machine_images.list(
                        azure.mgmt.compute.VirtualMachineImageListParameters(
                            location=self.region,
                            publisher_name=publisher_name,
                            offer=offer,
                            skus=skus,
                        ),
                    )
                    self.assertEqual(result_list.status_code, HttpStatusCode.OK)

                    for res in result_list.resources:
                        version = res.name

                        result_get = self.compute_client.virtual_machine_images.get(
                            azure.mgmt.compute.VirtualMachineImageGetParameters(
                                location=self.region,
                                publisher_name=publisher_name,
                                offer=offer,
                                skus=skus,
                                version=version,
                            ),
                        )
                        self.assertEqual(result_get.status_code, HttpStatusCode.OK)

                        print('PUBLISHER: {0}, OFFER: {1}, SKUS: {2}, VERSION: {3}'.format(
                            publisher_name,
                            offer,
                            skus,
                            version,
                        ))

    @record
    def test_availability_sets(self):
        self.create_resource_group()

        availability_set_name = self.get_resource_name('pyarmset')

        params_create = azure.mgmt.compute.AvailabilitySet(
            location=self.region,
            name=availability_set_name,
            platform_fault_domain_count=2,
            platform_update_domain_count=4,
            statuses=[
                azure.mgmt.compute.InstanceViewStatus(
                    code='test1',
                    display_status='test1 display',
                    message='test1 message',
                ),
                azure.mgmt.compute.InstanceViewStatus(
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
            params_create,
        )
        self.assertEqual(result_create.status_code, HttpStatusCode.OK)

        result_get = self.compute_client.availability_sets.get(
            self.group_name,
            availability_set_name,
        )
        self.assertEqual(result_get.status_code, HttpStatusCode.OK)
        #TODO: error, we get 0 back, not 2
        #self.assertEqual(
        #    len(result_get.availability_set.statuses),
        #    len(params_create.statuses),
        #)
        #self.assertEqual(
        #    result_get.availability_set.statuses[0].code,
        #    view_status1.code,
        #)
        #self.assertEqual(
        #    result_get.availability_set.statuses[1].code,
        #    view_status2.code,
        #)
        self.assertEqual(
            result_get.availability_set.platform_fault_domain_count,
            params_create.platform_fault_domain_count,
        )
        self.assertEqual(
            result_get.availability_set.platform_update_domain_count,
            params_create.platform_update_domain_count,
        )

        result_list = self.compute_client.availability_sets.list(
            self.group_name,
        )
        self.assertEqual(result_list.status_code, HttpStatusCode.OK)

        result_list_sizes = self.compute_client.availability_sets.list_available_sizes(
            self.group_name,
            availability_set_name,
        )
        self.assertEqual(result_list_sizes.status_code, HttpStatusCode.OK)

        result_delete = self.compute_client.availability_sets.delete(
            self.group_name,
            availability_set_name,
        )
        self.assertEqual(result_delete.status_code, HttpStatusCode.OK)

    @record
    def test_usage(self):
        result_list = self.compute_client.usage.list(self.region)
        self.assertEqual(result_list.status_code, HttpStatusCode.OK)
        self.assertGreater(len(result_list.usages), 0)

    @record
    def test_vm_sizes(self):
        result_list = self.compute_client.virtual_machine_sizes.list(self.region)
        self.assertEqual(result_list.status_code, HttpStatusCode.OK)
        self.assertGreater(len(result_list.virtual_machine_sizes), 0)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
