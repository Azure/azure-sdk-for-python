# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# covered ops:
#   galleries: 6/6
#   gallery_applications: 5/5
#   gallery_application_versions: 0/5
#   gallery_images: 5/5
#   gallery_image_versions: 5/5

import os
import unittest

import pytest
import azure.mgmt.compute
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus2'

class TestMgmtCompute(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )

        if self.is_live:
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )

    def create_snapshot(self, group_name, disk_name, snapshot_name):
        # Create an empty managed disk.[put]
        BODY = {
          "location": AZURE_LOCATION,
          "creation_data": {
            "create_option": "Empty"
          },
          "disk_size_gb": "200"
        }
        result = self.mgmt_client.disks.begin_create_or_update(group_name, disk_name, BODY)
        disk = result.result()

      # Create a snapshot by copying a disk.
        BODY = {
          "location": AZURE_LOCATION,
          "creation_data": {
            "create_option": "Copy",
            # "source_uri": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/disks/" + DISK_NAME
            "source_uri": disk.id
          }
        }
        result = self.mgmt_client.snapshots.begin_create_or_update(group_name, snapshot_name, BODY)
        result = result.result()

    def delete_snapshot(self, group_name, snapshot_name):

        # Revoke access snapshot (TODO: need swagger file)
        result = self.mgmt_client.snapshots.begin_revoke_access(group_name, snapshot_name)
        result = result.result()

        # Delete snapshot (TODO: need swagger file)
        result = self.mgmt_client.snapshots.begin_delete(group_name, snapshot_name)
        result = result.result()

    @pytest.mark.skipif(os.getenv('AZURE_TEST_RUN_LIVE') not in ('true', 'yes'), reason='only run live test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_compute_galleries(self, resource_group):
        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        GALLERY_NAME = self.get_resource_name("galleryname")
        APPLICATION_NAME = self.get_resource_name("applicationname")
        IMAGE_NAME = self.get_resource_name("imagex")
        DISK_NAME = self.get_resource_name("diskname")
        SNAPSHOT_NAME = self.get_resource_name("snapshotname")
        VERSION_NAME = "1.0.0"

        if self.is_live:
            self.create_snapshot(RESOURCE_GROUP, DISK_NAME, SNAPSHOT_NAME)

        # Create or update a simple gallery.[put]
        BODY = {
          "location": AZURE_LOCATION,
          "description": "This is the gallery description."
        }
        result = self.mgmt_client.galleries.begin_create_or_update(resource_group.name, GALLERY_NAME, BODY)
        result = result.result()

        # Create or update a simple gallery Application.[put]
        BODY = {
          "location": AZURE_LOCATION,
          "description": "This is the gallery application description.",
          "eula": "This is the gallery application EULA.",
          # "privacy_statement_uri": "myPrivacyStatementUri}",
          # "release_note_uri": "myReleaseNoteUri",
          "supported_os_type": "Windows"
        }
        result = self.mgmt_client.gallery_applications.begin_create_or_update(resource_group.name, GALLERY_NAME, APPLICATION_NAME, BODY)
        result = result.result()

        # TODO: NEED CREATE BLOB
        # # Create or update a simple gallery Application Version.[put]
        # BODY = {
        #   "location": "eastus",
        #   "publishing_profile": {
        #     "source": {
        #       "file_name": "package.zip",
        #       "media_link": "https://mystorageaccount.blob.core.windows.net/mycontainer/package.zip?{sasKey}"
        #     },
        #     "target_regions": [
        #       {
        #         "name": "eastus",
        #         "regional_replica_count": "1",
        #         "storage_account_type": "Standard_LRS"
        #       }
        #     ],
        #     "replica_count": "1",
        #     "end_of_life_date": "2019-07-01T07:00:00Z",
        #     "storage_account_type": "Standard_LRS"
        #   }
        # }
        # result = self.mgmt_client.gallery_application_versions.create_or_update(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME, BODY)
        # result = result.result()

        # Create or update a simple gallery image.[put]
        BODY = {
          "location": AZURE_LOCATION,
          "os_type": "Windows",
          "os_state": "Generalized",
          "hyper_vgeneration": "V1",
          "identifier": {
            "publisher": "myPublisherName",
            "offer": "myOfferName",
            "sku": "mySkuName"
          }
        }
        result = self.mgmt_client.gallery_images.begin_create_or_update(resource_group.name, GALLERY_NAME, IMAGE_NAME, BODY)
        result = result.result()

        # Create or update a simple Gallery Image Version using snapshots as a source.[put]
        BODY = {
          "location": AZURE_LOCATION,
          "publishing_profile": {
            "target_regions": [
              {
                "name": AZURE_LOCATION,
                "regional_replica_count": "2",
                "storage_account_type": "Standard_ZRS"
              }
            ]
          },
          "storage_profile": {
            "os_disk_image": {
              "source": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/snapshots/" + SNAPSHOT_NAME + ""
              },
              "host_caching": "ReadOnly"
            }
          }
        }
        result = self.mgmt_client.gallery_image_versions.begin_create_or_update(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME, BODY)
        result = result.result()

        # # TODO:need finish
        # # Get a gallery Application Version with replication status.[get]
        # result = self.mgmt_client.gallery_application_versions.get(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME)

        # Get a gallery Image Version.[get]
        result = self.mgmt_client.gallery_image_versions.get(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME)

        # Get a gallery image.[get]
        result = self.mgmt_client.gallery_images.get(resource_group.name, GALLERY_NAME, IMAGE_NAME)

        # Get a gallery Application.[get]
        result = self.mgmt_client.gallery_applications.get(resource_group.name, GALLERY_NAME, APPLICATION_NAME)

        # Get a gallery.[get]
        result = self.mgmt_client.galleries.get(resource_group.name, GALLERY_NAME)

        # List gallery Image Versions in a gallery Image Definition.[get]
        result = self.mgmt_client.gallery_image_versions.list_by_gallery_image(resource_group.name, GALLERY_NAME, IMAGE_NAME)

        # List gallery images in a gallery.[get]
        result = self.mgmt_client.gallery_images.list_by_gallery(resource_group.name, GALLERY_NAME)

        # TODO:need finish
        # # List gallery Application Versions in a gallery Application Definition.[get]
        # result = self.mgmt_client.gallery_application_versions.list_by_gallery_application(resource_group.name, GALLERY_NAME, APPLICATION_NAME)

        # List gallery Applications in a gallery.[get]
        result = self.mgmt_client.gallery_applications.list_by_gallery(resource_group.name, GALLERY_NAME)

        # List galleries in a resource group.[get]
        result = self.mgmt_client.galleries.list_by_resource_group(resource_group.name)

        # List galleries in a subscription.[get]
        result = self.mgmt_client.galleries.list()

        # Update a simple Gallery Image Version (Managed Image as source).[patch]
        BODY = {
          "publishing_profile": {
            "target_regions": [
              # {
              #   "name": "eastus",
              #   "regional_replica_count": "1"
              # },
              {
                "name": AZURE_LOCATION,
                "regional_replica_count": "2",
                "storage_account_type": "Standard_ZRS"
              }
            ]
          },
          "storage_profile": {
            "os_disk_image": {
              "source": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/snapshots/" + SNAPSHOT_NAME + ""
              },
              "host_caching": "ReadOnly"
            },
            # TODO: NEED A IMAGE
            # "source": {
            #   "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/images/" + IMAGE_NAME + ""
            # }
          }
        }
        result = self.mgmt_client.gallery_image_versions.begin_update(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME, BODY)
        result = result.result()

        # Update a simple gallery image.[patch]
        BODY = {
          "os_type": "Windows",
          "os_state": "Generalized",
          "hyper_vgeneration": "V1",
          "identifier": {
            "publisher": "myPublisherName",
            "offer": "myOfferName",
            "sku": "mySkuName"
          }
        }
        result = self.mgmt_client.gallery_images.begin_update(resource_group.name, GALLERY_NAME, IMAGE_NAME, BODY)
        result = result.result()

        # TODO: dont finish
        # Update a simple gallery Application Version.[patch]
        # BODY = {
        #   "properties": {
        #     "publishing_profile": {
        #       "source": {
        #         "file_name": "package.zip",
        #         "media_link": "https://mystorageaccount.blob.core.windows.net/mycontainer/package.zip?{sasKey}"
        #       },
        #       "target_regions": [
        #         {
        #           "name": "eastus",
        #           "regional_replica_count": "1",
        #           "storage_account_type": "Standard_LRS"
        #         }
        #       ],
        #       "replica_count": "1",
        #       "end_of_life_date": "2019-07-01T07:00:00Z",
        #       "storage_account_type": "Standard_LRS"
        #     }
        #   }
        # }
        # result = self.mgmt_client.gallery_application_versions.update(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME, BODY)
        # result = result.result()

        # Update a simple gallery Application.[patch]
        BODY = {
          "description": "This is the gallery application description.",
          "eula": "This is the gallery application EULA.",
          # "privacy_statement_uri": "myPrivacyStatementUri}",
          # "release_note_uri": "myReleaseNoteUri",
          "supported_os_type": "Windows",
          "tags": {
            "tag1": "tag1"
          }
        }
        result = self.mgmt_client.gallery_applications.begin_update(resource_group.name, GALLERY_NAME, APPLICATION_NAME, BODY)
        result = result.result()

        # Update a simple gallery.[patch]
        BODY = {
          "description": "This is the gallery description."
        }
        result = self.mgmt_client.galleries.begin_update(resource_group.name, GALLERY_NAME, BODY)
        result = result.result()

        # Delete a gallery Image Version.[delete]
        result = self.mgmt_client.gallery_image_versions.begin_delete(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME)
        result = result.result()

        # Delete a gallery Application.[delete]
        result = self.mgmt_client.gallery_applications.begin_delete(resource_group.name, GALLERY_NAME, APPLICATION_NAME)
        result = result.result()

        if self.is_live:
            self.delete_snapshot(RESOURCE_GROUP, SNAPSHOT_NAME)

        # Delete a gallery image.[delete]
        result = self.mgmt_client.gallery_images.begin_delete(resource_group.name, GALLERY_NAME, IMAGE_NAME)
        result = result.result()

        # TODO: need finish
        # # Delete a gallery Application Version.[delete]
        # result = self.mgmt_client.gallery_application_versions.delete(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME)
        # result = result.result()

        # Delete a gallery.[delete]
        result = self.mgmt_client.galleries.begin_delete(resource_group.name, GALLERY_NAME)
        result = result.result()
