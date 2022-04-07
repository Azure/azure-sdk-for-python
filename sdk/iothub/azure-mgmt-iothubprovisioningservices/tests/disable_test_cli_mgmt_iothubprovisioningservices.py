# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 18
# Methods Covered : 18
# Examples Total  : 18
# Examples Tested : 11
# Coverage %      : 61
# ----------------------

import unittest

import azure.mgmt.iothubprovisioningservices
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtIotDpsClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtIotDpsClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.iothubprovisioningservices.IotDpsClient
        )
    
    @unittest.skip('hard to test')
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_iothubprovisioningservices(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        PROVISIONING_SERVICE_NAME = "myProvisioningServiceRND"
        CERTIFICATE_NAME = "myCertificate"
        OPERATION_ID = "myOperationId"
        KEY_NAME = "myKey"

        # /IotDpsResource/put/DPSCreate[put]
        BODY = {
          "location": "East US",
          "type": "Microsoft.Devices/ProvisioningServices",
          "sku": {
            "name": "S1",
            "tier": "Standard",
            "capacity": "1"
          },
          "properties": {}
        }
        result = self.mgmt_client.iot_dps_resource.create_or_update(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME, iot_dps_description=BODY)
        result = result.result()

        # /DpsCertificate/put/DPSCreateOrUpdateCertificate[put]
        BODY = {
          "certificate": "############################################"
        }
        # result = self.mgmt_client.dps_certificate.create_or_update(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME, certificate_name=CERTIFICATE_NAME, certificate_description=BODY)

        # Certificates not tested yet
        # /DpsCertificate/get/DPSGetCertificate[get]
        # result = self.mgmt_client.dps_certificate.get(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME, certificate_name=CERTIFICATE_NAME)

        # Certificates not tested yet
        # /IotDpsResource/get/DPSGetOperationResult[get]
        # result = self.mgmt_client.iot_dps_resource.get_operation_result(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME, operation_id=OPERATION_ID, asyncinfo="1508265712453")

        # /DpsCertificate/get/DPSGetCertificates[get]
        result = self.mgmt_client.dps_certificate.list(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME)

        # /IotDpsResource/get/DPSGetValidSku[get]
        result = self.mgmt_client.iot_dps_resource.list_valid_skus(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME)

        # /IotDpsResource/get/DPSGet[get]
        result = self.mgmt_client.iot_dps_resource.get(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME)

        # /IotDpsResource/get/DPSListByResourceGroup[get]
        result = self.mgmt_client.iot_dps_resource.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /IotDpsResource/get/DPSListBySubscription[get]
        result = self.mgmt_client.iot_dps_resource.list_by_subscription()

        # /Operations/get/DPSOperations[get]
        result = self.mgmt_client.operations.list()

        # Certificates not tested yet
        # /DpsCertificate/post/DPSGenerateVerificationCode[post]
        # result = self.mgmt_client.dps_certificate.generate_verification_code(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME, certificate_name=CERTIFICATE_NAME)

        # Certificates not tested yet
        # /DpsCertificate/post/DPSVerifyCertificate[post]
        BODY = {
          "certificate": "#####################################"
        }
        # result = self.mgmt_client.dps_certificate.verify_certificate(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME, certificate_name=CERTIFICATE_NAME, request=BODY)

        # Certificates not tested yet
        # /IotDpsResource/post/DPSGetKey[post]
        # result = self.mgmt_client.iot_dps_resource.list_keys_for_key_name(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME, key_name=KEY_NAME)

        # /IotDpsResource/post/DPSListKeys[post]
        result = self.mgmt_client.iot_dps_resource.list_keys(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME)

        # /IotDpsResource/patch/DPSPatch[patch]
        BODY = {
          "tags": {
            "foo": "bar"
          }
        }
        result = self.mgmt_client.iot_dps_resource.update(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME, provisioning_service_tags=BODY)
        result = result.result()

        # /IotDpsResource/post/DPSCheckName[post]
        BODY = {
          "name": "test213123"
        }
        result = self.mgmt_client.iot_dps_resource.check_provisioning_service_name_availability(name="test213123")

        # Certificates not tested yet
        # /DpsCertificate/delete/DPSDeleteCertificate[delete]
        # result = self.mgmt_client.dps_certificate.delete(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME, certificate_name=CERTIFICATE_NAME)

        # /IotDpsResource/delete/DPSDelete[delete]
        result = self.mgmt_client.iot_dps_resource.delete(resource_group_name=RESOURCE_GROUP, provisioning_service_name=PROVISIONING_SERVICE_NAME)

        try:
          result = result.result()
        except:
          print("poller failing")


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
