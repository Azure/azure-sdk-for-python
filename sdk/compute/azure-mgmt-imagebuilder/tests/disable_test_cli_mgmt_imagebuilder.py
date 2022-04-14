# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 10
# Methods Covered : 9
# Examples Total  : 11
# Examples Tested : 11
# Coverage %      : 90
# ----------------------

import unittest

import azure.mgmt.imagebuilder
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'
IMAGE_TEMPLATE_NAME = "MyImageTemplate"
IMAGE_NAME = 'MyImage'
RUN_OUTPUT_NAME = 'image_it_pir_1'

# make sure to create user identity with this doc before running live test: https://github.com/danielsollondon/azvmimagebuilder/tree/master/quickquickstarts/0_Creating_a_Custom_Windows_Managed_Image#step-2--permissions-create-user-idenity-and-role-for-aib
IDENTITY_NAME = 'aibIdentity1588309486'

class MgmtImageBuilderClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtImageBuilderClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.imagebuilder.ImageBuilderClient
        )
    
    @unittest.skip('hard to test')
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_imagebuilder(self, resource_group):

        # Create an Image Template with a user assigned identity configured[put]
        BODY = {
          "location": "eastus",
          "tags": {
            "imagetemplate_tag1": "IT_T1",
            "imagetemplate_tag2": "IT_T2"
          },
          "identity": {
            "type": "UserAssigned",
            "user_assigned_identities": { "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{}".format(self.settings.SUBSCRIPTION_ID, resource_group.name, IDENTITY_NAME): {}}
          },
          "properties": {
            "source": {
              "type": "ManagedImage",
              "image_id": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + resource_group.name + "/providers/Microsoft.Compute/images/" + IMAGE_NAME + ""
            },
            "customize": [
              {
                "type": "Shell",
                "name": "Shell Customizer Example",
                "script_uri": "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/619a017566f2bdb2d9a85afd1fe2018bed822cc8/sdk/compute/azure-mgmt-imagebuilder/tests/script.sh"
              }
            ],
            "distribute": [
              {
                "type": "ManagedImage",
                "location": "eastus",
                "run_output_name": "image_it_pir_1",
                "image_id": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + resource_group.name + "/providers/Microsoft.Compute/images/" + IMAGE_NAME + "",
                "artifact_tags": {
                  "tag_name": "value"
                }
              }
            ],
            "vm_profile": {
              "vm_size": "Standard_D2s_v3"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_image_templates.create_or_update(BODY, resource_group.name, IMAGE_TEMPLATE_NAME)
        result = result.result()

        # Retrieve an Image Template.[get]
        result = self.mgmt_client.virtual_machine_image_templates.get(resource_group.name, IMAGE_TEMPLATE_NAME)

        # List images by resource group[get]
        result = self.mgmt_client.virtual_machine_image_templates.list_by_resource_group(resource_group.name)

        # List images by subscription.[get]
        result = self.mgmt_client.virtual_machine_image_templates.list()

        # Create image(s) from existing imageTemplate.[post]
        result = self.mgmt_client.virtual_machine_image_templates.run(resource_group.name, IMAGE_TEMPLATE_NAME)
        result = result.result()

        # Retrieve single runOutput[get]
        result = self.mgmt_client.virtual_machine_image_templates.get_run_output(resource_group.name, IMAGE_TEMPLATE_NAME, RUN_OUTPUT_NAME)

        # Retrieve a list of all outputs created by the last run of an Image Template[get]
        result = self.mgmt_client.virtual_machine_image_templates.list_run_outputs(resource_group.name, IMAGE_TEMPLATE_NAME)

        # Remove identities for an Image Template.[patch]
        BODY = {
          "identity": {
            "type": "None"
          }
        }
        #result = self.mgmt_client.virtual_machine_image_templates.update(resource_group.name, IMAGE_TEMPLATE_NAME, BODY)
        #result = result.result()

        # Update the tags for an Image Template.[patch]
        BODY = {
          "tags": {
            "new-tag": "new-value"
          }
        }
        #result = self.mgmt_client.virtual_machine_image_templates.update(resource_group.name, IMAGE_TEMPLATE_NAME, BODY)
        #result = result.result()

        # Delete an Image Template.[delete]
        result = self.mgmt_client.virtual_machine_image_templates.delete(resource_group.name, IMAGE_TEMPLATE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()