Managed Disks
=============

Azure Managed Disks and 1000 VMs in a Scale Set are now `generally
available <https://azure.microsoft.com/en-us/blog/announcing-general-availability-of-managed-disks-and-larger-scale-sets/>`__.
Azure Managed Disks provide a simplified disk Management, enhanced
Scalability, better Security and Scale. It takes away the notion of
storage account for disks, enabling customers to scale without worrying
about the limitations associated with storage
accounts. This post provides a quick introduction and
reference on consuming the service from Python.



From a developer perspective, the Managed Disks experience in Azure CLI
is idomatic to the CLI experience in other cross-platform tools. You can
use the `Azure Python
SDK <https://azure.microsoft.com/develop/python/>`__ and the
`azure-mgmt-compute package
0.33.0 <https://pypi.python.org/pypi/azure-mgmt-compute>`__ to
administer Managed Disks. You can create a compute client using this
`tutorial <http://azure-sdk-for-python.readthedocs.io/en/latest/resourcemanagementcomputenetwork.html>`__.
The complete API documentation is available on
`ReadTheDocs <http://azure-sdk-for-python.readthedocs.io/en/latest/ref/azure.mgmt.compute.html>`__.

Standalone Managed Disks
========================

You can easily create standalone Managed Disks in a variety of ways.

Create an empty Managed Disk.
-----------------------------

.. code:: python

            from azure.mgmt.compute.models import DiskCreateOption

            async_creation = compute_client.disks.create_or_update(
                'my_resource_group',
                'my_disk_name',
                {
                    'location': 'westus',
                    'disk_size_gb': 20,
                    'creation_data': {
                        'create_option': DiskCreateOption.empty
                    }
                }
            )
            disk_resource = async_creation.result()

Create a Managed Disk from Blob Storage.
----------------------------------------

.. code:: python

            from azure.mgmt.compute.models import DiskCreateOption

            async_creation = compute_client.disks.create_or_update(
                'my_resource_group',
                'my_disk_name',
                {
                    'location': 'westus',
                    'creation_data': {
                        'create_option': DiskCreateOption.import_enum,
                        'source_uri': 'https://bg09.blob.core.windows.net/vm-images/non-existent.vhd'
                    }
                }
            )
            disk_resource = async_creation.result()

Create a Managed Disk from your own Image
-----------------------------------------

.. code:: python

            from azure.mgmt.compute.models import DiskCreateOption

            # If you don't know the id, do a 'get' like this to obtain it
            managed_disk = compute_client.disks.get(self.group_name, 'myImageDisk')
            async_creation = compute_client.disks.create_or_update(
                'my_resource_group',
                'my_disk_name',
                {
                    'location': 'westus',
                    'creation_data': {
                        'create_option': DiskCreateOption.copy,
                        'source_resource_id': managed_disk.id
                    }
                }
            )

            disk_resource = async_creation.result()

Virtual Machine with Managed Disks
==================================

You can create a Virtual Machine with an implicit Managed Disk for a
specific disk image. Creation is simplified with implicit creation of
managed disks without specifying all the disk details. You do not have
to worry about creating and managing Storage Accounts.

A Managed Disk is created implicitly when creating VM from an OS image
in Azure. In the ``storage_profile`` parameter, ``os_disk`` is now
optional and you don't have to create a storage account as required
precondition to create a Virtual Machine.

.. code:: python

               storage_profile = azure.mgmt.compute.models.StorageProfile(
                    image_reference = azure.mgmt.compute.models.ImageReference(
                        publisher='Canonical',
                        offer='UbuntuServer',
                        sku='16.04-LTS',
                        version='latest'
                    )
                )

This ``storage_profile`` parameter is now valid. To get a complete
example on how to create a VM in Python (including network, etc), check
the full VM tutorial in Python
`here <https://github.com/Azure-Samples/virtual-machines-python-manage>`__.

You can easily attach a previously provisioned Managed Disk.

.. code:: python

                vm = compute.virtual_machines.get(
                    'my_resource_group',
                    'my_vm'
                )
                managed_disk = compute_client.disks.get('my_resource_group', 'myDisk')
                vm.storage_profile.data_disks.append({
                    'lun': 12, # You choose the value, depending of what is available for you
                    'name': managed_disk.name,
                    'create_option': DiskCreateOption.attach,
                    'managed_disk': {
                        'id': managed_disk.id
                    }
                })
                async_update = compute_client.virtual_machines.create_or_update(
                    'my_resource_group',
                    vm.name,
                    vm,
                )
                async_update.wait()

Virtual Machine Scale Sets with Managed Disks
=============================================

Before Managed Disks, you needed to create a storage account manually
for all the VMs you wanted inside your Scale Set, and then use the list
parameter ``vhd_containers`` to provide all the storage account name to
the Scale Set RestAPI. The official transition guide is available in
this
`article <https://docs.microsoft.com/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-convert-template-to-md>`__.

Now with Managed Disk, you don't have to manage any storage account at
all. If you're are used to the VMSS Python SDK, your ``storage_profile``
can now be exactly the same as the one used in VM creation:

.. code:: python

                        'storage_profile': {
                            'image_reference': {
                                "publisher": "Canonical",
                                "offer": "UbuntuServer",
                                "sku": "16.04-LTS",
                                "version": "latest"
                            }
                        },

The full sample being:

.. code:: python

                naming_infix = "PyTestInfix"
                vmss_parameters = {
                    'location': self.region,
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
                                "sku": "16.04-LTS",
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
                                        'id': subnet.id
                                    } 
                                }]
                            }]
                        }
                    }
                }

                # Create VMSS test
                result_create = compute_client.virtual_machine_scale_sets.create_or_update(
                    'my_resource_group',
                    'my_scale_set',
                    vmss_parameters,
                )
                vmss_result = result_create.result()

Other Operations with Managed Disks
===================================

Resizing a managed disk.
------------------------

.. code:: python

            managed_disk = compute_client.disks.get('my_resource_group', 'myDisk')
            managed_disk.disk_size_gb = 25
            async_update = self.compute_client.disks.create_or_update(
                'my_resource_group',
                'myDisk',
                managed_disk
            )
            async_update.wait()

Update the Storage Account type of the Managed Disks.
-----------------------------------------------------

.. code:: python

            from azure.mgmt.compute.models import StorageAccountTypes

            managed_disk = compute_client.disks.get('my_resource_group', 'myDisk')
            managed_disk.account_type = StorageAccountTypes.standard_lrs
            async_update = self.compute_client.disks.create_or_update(
                'my_resource_group',
                'myDisk',
                managed_disk
            )
            async_update.wait()

Create an image from Blob Storage.
----------------------------------

.. code:: python

            async_create_image = compute_client.images.create_or_update(
                'my_resource_group',
                'myImage',
                {
                    'location': 'westus',
                    'storage_profile': {
                        'os_disk': {
                            'os_type': 'Linux',
                            'os_state': "Generalized",
                            'blob_uri': 'https://bg09.blob.core.windows.net/vm-images/non-existent.vhd',
                            'caching': "ReadWrite",
                        }
                    }
                }
            )
            image = async_create_image.result()

Create a snapshot of a Managed Disk that is currently attached to a Virtual Machine.
------------------------------------------------------------------------------------

.. code:: python

            managed_disk = compute_client.disks.get('my_resource_group', 'myDisk')
            async_snapshot_creation = self.compute_client.snapshots.create_or_update(
                    'my_resource_group',
                    'mySnapshot',
                    {
                        'location': 'westus',
                        'creation_data': {
                            'create_option': 'Copy',
                            'source_uri': managed_disk.id
                        }
                    }
                )
            snapshot = async_snapshot_creation.result()
