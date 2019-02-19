# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import uuid

from collections import namedtuple

import azure.mgmt.compute
import azure.mgmt.network.models
import azure.mgmt.authorization.models

from devtools_testutils import (
    AzureMgmtTestCase,
    ResourceGroupPreparer,
)

from test_mgmt_compute import ComputeResourceNames

class MgmtMSIComputeTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMSIComputeTest, self).setUp()
        self.compute_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )

        if not self.is_playback():
            self.network_client = self.create_mgmt_client(
                azure.mgmt.network.NetworkManagementClient
            )
            self.authorization_client = self.create_mgmt_client(
                azure.mgmt.authorization.AuthorizationManagementClient
            )

    def get_resource_names(self, base):
        return ComputeResourceNames(
            self.get_resource_name(base + 'stor'),
            self.get_resource_name(base + 'vm'),
            self.get_resource_name(base + 'net'),
            self.get_resource_name(base + 'nic'),
            self.get_resource_name(base + 'sub'),
        )

    @ResourceGroupPreparer()
    def test_create_msi_enabled_vm(self, resource_group, location):
        virtual_machines_models = self.compute_client.virtual_machines.models

        names = self.get_resource_names('pyvmir')
        if not self.is_playback():
            subnet = self.create_virtual_network(resource_group.name, location, names.network, names.subnet)
            nic_id = self.create_network_interface(resource_group.name, location, names.nic, subnet)
        else:
            nic_id = ("/subscriptions/00000000-0000-0000-0000-000000000000"
                      "/resourceGroups/test_mgmt_compute_test_virtual_machines_operations122014cf"
                      "/providers/Microsoft.Network/networkInterfaces/pyvmirnic122014cf")

        storage_profile = virtual_machines_models.StorageProfile(
            image_reference = virtual_machines_models.ImageReference(
                publisher='Canonical',
                offer='UbuntuServer',
                sku='16.04.0-LTS',
                version='latest'
            )
        )

        params_create = virtual_machines_models.VirtualMachine(
            location=location,
            os_profile=self.get_os_profile(resource_group.name),
            hardware_profile=self.get_hardware_profile(),
            network_profile=self.get_network_profile(nic_id),
            storage_profile=storage_profile,
            # Activate MSI on that VM
            identity=virtual_machines_models.VirtualMachineIdentity(
                type=virtual_machines_models.ResourceIdentityType.system_assigned
            )
        )

        # Create VM
        result_create = self.compute_client.virtual_machines.create_or_update(
            resource_group.name,
            names.vm,
            params_create,
        )
        vm_result = result_create.result()
        self.assertEqual(vm_result.name, names.vm)

        # Get the Principal id of that VM
        msi_principal_id = vm_result.identity.principal_id

        # Do not do the Authorization part in playback, since it has nothing to do with Compute
        if not self.is_playback():

            # Get the Role ID of Contributor of a Resource Group
            role_name = 'Contributor'
            roles = list(self.authorization_client.role_definitions.list(
                resource_group.id,
                filter="roleName eq '{}'".format(role_name)
            ))
            assert len(roles) == 1
            contributor_role = roles[0]

            # Add RG scope to the MSI token
            self.authorization_client.role_assignments.create(
                resource_group.id,
                uuid.uuid4(), # Role assignment name
                {
                    'role_definition_id': contributor_role.id,
                    'principal_id': msi_principal_id
                }
            )

        # Adds the MSI extension
        # This is deprecated, no extension needed anymore. Keep the code as extension example still.
        # ext_type_name = 'ManagedIdentityExtensionForLinux'
        # ext_name = vm_result.name + ext_type_name
        # params_create = virtual_machines_models.VirtualMachineExtension(
        #     location=location,
        #     publisher='Microsoft.ManagedIdentity',
        #     virtual_machine_extension_type=ext_type_name,
        #     type_handler_version='1.0',
        #     auto_upgrade_minor_version=True,
        #     settings={'port': 50342}, # Default port that should be used
        #     protected_settings={},
        # )
        # result_create = self.compute_client.virtual_machine_extensions.create_or_update(
        #     resource_group.name,
        #     names.vm,
        #     ext_name,
        #     params_create,
        # )
        # result_create.wait()


    ############# Should be generalized

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
        virtual_machines_models = self.compute_client.virtual_machines.models
        return virtual_machines_models.OSProfile(
            admin_username='Foo12',
            admin_password='BaR@123' + resource_group_name,
            computer_name='test',
        )

    def get_hardware_profile(self):
        virtual_machines_models = self.compute_client.virtual_machines.models
        return virtual_machines_models.HardwareProfile(
            vm_size=virtual_machines_models.VirtualMachineSizeTypes.standard_a0
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
