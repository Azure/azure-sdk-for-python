# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 17
# Methods Covered : 17
# Examples Total  : 18
# Examples Tested : 18
# Coverage %      : 100
# ----------------------

import unittest

import azure.mgmt.recoveryservices
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtRecoveryServicesClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtRecoveryServicesClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.recoveryservices.RecoveryServicesClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_recoveryservices(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        VAULT_NAME = "myVault"
        CERTIFICATE_NAME = "myCertificate"
        PRIVATE_LINK_RESOURCE_NAME = "myPrivateLinkResource"
        LOCATION = "myLocation"
        IDENTITY_NAME = "myIdentity"

        # /Vaults/put/Create of Update Recovery Services vault[put]
        BODY = {
          "sku": {
            "name": "Standard"
          },
          "location": "West US",
          "identity": {
            "type": "SystemAssigned"
          }
        }
        result = self.mgmt_client.vaults.create_or_update(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, vault=BODY)

        # /VaultCertificates/put/Download vault credential file[put]
        PROPERTIES = {
          "auth_type": "AAD",
          "certificate": "MTTC3TCCAcWgAwIBAgIQEj9h+ZLlXK9KrqZX9UkAnzANBgkqhkiG9w0BAQUFADAeMRwwGgYDVQQDExNXaW5kb3dzIEF6dXJlIFRvb2xzMB4XDTE3MTIxODA5MTc1M1oXDTE3MTIyMzA5Mjc1M1owHjEcMBoGA1UEAxMTV2luZG93cyBBenVyZSBUb29sczCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAK773/eZZ69RbZZAT05r9MjUxu9y1L1Pn1EgPk62IPJyHlO3OZA922eSBahhP4bgmFljN4LVReqQ5eT/wqO0Zhc+yFkUy4U4RdbQLeUZt2W7yy9XLXgVvqeYDgsjg/QhHetgHArQBW+tlQq5+zPdU7zchI4rbShSJrWhLrZFWiOyFPsuAE4joUQHNlRifdCTsBGKk8HRCY3j1S3c4bfEn3zxlrvrXXssRuW5mJM95rMk0tskoRxXSCi6i9bnlki2Cs9mpVMmBFeofs41KwzlWU0TgpdD8s1QEdvfGB5NbByfetPX7MfJaTBeHZEGbv/Iq8l72u8sPBoOhcaH7qDE/mECAwEAAaMXMBUwEwYDVR0lBAwwCgYIKwYBBQUHAwIwDQYJKoZIhvcNAQEFBQADggEBAILfgHluye1Q+WelhgWhpBBdIq2C0btfV8eFsZaTlBUrM0fwpxQSlAWc2oYHVMQI4A5iUjbDOY35O4yc+TnWKDBKf+laqDP+yos4aiUPuadGUZfvDk7kuw7xeECs64JpHAIEKdRHFW9rD3gwG+nIWaDnEL/7rTyhL3kXrRW2MSUAL8g3GX8Z45c+MQY0jmASIqWdhGn1vpAGyA9mKkzsqg7FXjg8GZb24tGl5Ky85+ip4dkBfXinDD8WwaGyjhGGK97ErvNmN36qly/H0H1Qngiovg1FbHDmkcFO5QclnEJsFFmcO2CcHp5Fqh2wXn5O1cQaxCIRTpQ/uXRpDjl2wKs="
        }
        result = self.mgmt_client.vault_certificates.create(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, certificate_name=CERTIFICATE_NAME, properties= PROPERTIES)

        # /VaultExtendedInfo/put/Put ExtendedInfo of Resource[put]
        BODY = {
          "integrity_key": "J99wzS27fmJ+Wjot7xO5wA==",
          "algorithm": "None"
        }
        result = self.mgmt_client.vault_extended_info.create_or_update(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, resource_resource_extended_info_details=BODY)

        # /PrivateLinkResources/get/Get PrivateLinkResource[get]
        result = self.mgmt_client.private_link_resources.get(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, private_link_resource_name=PRIVATE_LINK_RESOURCE_NAME)

        # /VaultExtendedInfo/get/Get ExtendedInfo of Resource[get]
        result = self.mgmt_client.vault_extended_info.get(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME)

        # /PrivateLinkResources/get/List PrivateLinkResources[get]
        result = self.mgmt_client.private_link_resources.list(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME)

        # /ReplicationUsages/get/Gets Replication usages of vault[get]
        result = self.mgmt_client.replication_usages.list(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME)

        # /Usages/get/Gets vault usages[get]
        result = self.mgmt_client.usages.list_by_vaults(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME)

        # /Vaults/get/Get Recovery Services Resource[get]
        result = self.mgmt_client.vaults.get(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME)

        # /Vaults/get/List of Recovery Services Resources in ResourceGroup[get]
        result = self.mgmt_client.vaults.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /Vaults/get/List of Recovery Services Resources in SubscriptionId[get]
        result = self.mgmt_client.vaults.list_by_subscription_id()

        # /Operations/get/ListOperations[get]
        result = self.mgmt_client.operations.list()

        # /VaultExtendedInfo/patch/PATCH ExtendedInfo of Resource[patch]
        BODY = {
          "integrity_key": "J99wzS27fmJ+Wjot7xO5wA==",
          "algorithm": "None"
        }
        result = self.mgmt_client.vault_extended_info.update(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, resource_resource_extended_info_details=BODY)

        # /RecoveryServices/post/Availability status of Resource Name when no resource with same name, type and subscription exists, nor has been deleted within last 24 hours[post]
        result = self.mgmt_client.recovery_services.check_name_availability(resource_group_name=RESOURCE_GROUP, location=LOCATION, name="swaggerExample", type="Microsoft.RecoveryServices/Vaults")

        # /RecoveryServices/post/Availability status of Resource Name when resource with same name, type and subscription exists[post]
        result = self.mgmt_client.recovery_services.check_name_availability(resource_group_name=RESOURCE_GROUP, location=LOCATION, name="swaggerExample2", type="Microsoft.RecoveryServices/Vaults")

        # /Vaults/patch/Update Resource[patch]
        TAGS = {
          "patch_key": "PatchKeyUpdated"
        }
        result = self.mgmt_client.vaults.update(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, tags= TAGS)

        # /RegisteredIdentities/delete/Delete registered Identity[delete]
        result = self.mgmt_client.registered_identities.delete(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, identity_name=IDENTITY_NAME)

        # /Vaults/delete/Delete Recovery Services Vault[delete]
        result = self.mgmt_client.vaults.delete(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
