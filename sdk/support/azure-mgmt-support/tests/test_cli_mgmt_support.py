# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 14
# Methods Covered : 14
# Examples Total  : 35
# Examples Tested : 7
# Coverage %      : 20
# ----------------------

import unittest

import azure.mgmt.support
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtMicrosoftSupportTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMicrosoftSupportTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.support.MicrosoftSupport
        )
    
    @unittest.skip("skip test")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_support(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        SERVICE_NAME = "06bfd9d3-516b-d5c6-5802-169c800dec89"
        PROBLEM_CLASSIFICATION_NAME = "831b2fb3-4db3-3d32-af35-bbb3d3eaeba2"
        SUPPORT_TICKET_NAME = "mySupportTicket"
        VIRTUAL_MACHINE_NAME = "myVirtualMachine"
        COMMUNICATION_NAME = "myCommunication"

        # /SupportTickets/put/Create a ticket to request Quota increase for Low-priority cores for a Batch account[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/quota_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/quota_service_guid/problemClassifications/batch_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          },
          "quota_ticket_details": {
            "quota_change_request_version": "1.0",
            "quota_change_request_sub_type": "Account",
            "quota_change_requests": [
              {
                "region": "EastUS",
                "payload": "{\"AccountName\":\"test\",\"NewLimit\":200,\"Type\":\"LowPriority\"}"
              }
            ]
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket to request Quota increase for Servers for Azure Synapse Analytics[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/quota_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/quota_service_guid/problemClassifications/sql_datawarehouse_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          },
          "quota_ticket_details": {
            "quota_change_request_version": "1.0",
            "quota_change_request_sub_type": "Servers",
            "quota_change_requests": [
              {
                "region": "EastUS",
                "payload": "{\"NewLimit\":200}"
              }
            ]
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket to request Quota increase for DTUs for Azure Synapse Analytics[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/quota_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/quota_service_guid/problemClassifications/sql_datawarehouse_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          },
          "quota_ticket_details": {
            "quota_change_request_version": "1.0",
            "quota_change_request_sub_type": "DTUs",
            "quota_change_requests": [
              {
                "region": "EastUS",
                "payload": "{\"ServerName\":\"testserver\",\"NewLimit\":54000}"
              }
            ]
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket to request Quota increase for Servers for SQL Database[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/quota_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/quota_service_guid/problemClassifications/sql_database_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          },
          "quota_ticket_details": {
            "quota_change_request_version": "1.0",
            "quota_change_request_sub_type": "Servers",
            "quota_change_requests": [
              {
                "region": "EastUS",
                "payload": "{\"NewLimit\":200}"
              }
            ]
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket to request Quota increase for DTUs for SQL Database[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/quota_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/quota_service_guid/problemClassifications/sql_database_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          },
          "quota_ticket_details": {
            "quota_change_request_version": "1.0",
            "quota_change_request_sub_type": "DTUs",
            "quota_change_requests": [
              {
                "region": "EastUS",
                "payload": "{\"ServerName\":\"testserver\",\"NewLimit\":54000}"
              }
            ]
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket to request Quota increase for specific VM family cores for Machine Learning service[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/quota_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/quota_service_guid/problemClassifications/machine_learning_service_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          },
          "quota_ticket_details": {
            "quota_change_request_version": "1.0",
            "quota_change_request_sub_type": "BatchAml",
            "quota_change_requests": [
              {
                "region": "EastUS",
                "payload": "{\"VMFamily\":\"standardA0_A7Family\",\"NewLimit\":200,\"Type\":\"Dedicated\"}"
              }
            ]
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket to request Quota increase for Active Jobs and Job Schedules for a Batch account[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/quota_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/quota_service_guid/problemClassifications/batch_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          },
          "quota_ticket_details": {
            "quota_change_request_version": "1.0",
            "quota_change_request_sub_type": "Account",
            "quota_change_requests": [
              {
                "region": "EastUS",
                "payload": "{\"AccountName\":\"test\",\"NewLimit\":200,\"Type\":\"Jobs\"}"
              }
            ]
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket to request Quota increase for Pools for a Batch account[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/quota_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/quota_service_guid/problemClassifications/batch_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          },
          "quota_ticket_details": {
            "quota_change_request_version": "1.0",
            "quota_change_request_sub_type": "Account",
            "quota_change_requests": [
              {
                "region": "EastUS",
                "payload": "{\"AccountName\":\"test\",\"NewLimit\":200,\"Type\":\"Pools\"}"
              }
            ]
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket to request Quota increase for specific VM family cores for a Batch account[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/quota_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/quota_service_guid/problemClassifications/batch_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          },
          "quota_ticket_details": {
            "quota_change_request_version": "1.0",
            "quota_change_request_sub_type": "Account",
            "quota_change_requests": [
              {
                "region": "EastUS",
                "payload": "{\"AccountName\":\"test\",\"VMFamily\":\"standardA0_A7Family\",\"NewLimit\":200,\"Type\":\"Dedicated\"}"
              }
            ]
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket for Billing related issues[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/billing_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/billing_service_guid/problemClassifications/billing_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket for Subscription Management related issues[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/subscription_management_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/subscription_management_service_guid/problemClassifications/subscription_management_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket to request Quota increase for Low-priority cores for Machine Learning service[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/quota_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/quota_service_guid/problemClassifications/machine_learning_service_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          },
          "quota_ticket_details": {
            "quota_change_request_version": "1.0",
            "quota_change_request_sub_type": "BatchAml",
            "quota_change_requests": [
              {
                "region": "EastUS",
                "payload": "{\"NewLimit\":200,\"Type\":\"LowPriority\"}"
              }
            ]
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket for Technical issue related to a specific resource[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/cddd3eb5-1830-b494-44fd-782f691479dc",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/virtual_machine_running_linux_service_guid/problemClassifications/problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          },
          "technical_ticket_details": {
            "resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket to request Quota increase for Compute VM Cores[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/quota_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/quota_service_guid/problemClassifications/cores_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          },
          "quota_ticket_details": {
            "quota_change_request_version": "1.0",
            "quota_change_requests": [
              {
                "region": "EastUS",
                "payload": "{\"SKU\":\"DSv3 Series\",\"NewLimit\":104}"
              }
            ]
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /SupportTickets/put/Create a ticket to request Quota increase for Batch accounts for a subscription[put]
        BODY = {
          "service_id": "/providers/Microsoft.Support/services/quota_service_guid",
          "title": "my title",
          "description": "my description",
          "problem_classification_id": "/providers/Microsoft.Support/services/quota_service_guid/problemClassifications/batch_problemClassification_guid",
          "severity": "moderate",
          "contact_details": {
            "first_name": "abc",
            "last_name": "xyz",
            "primary_email_address": "abc@contoso.com",
            "preferred_contact_method": "email",
            "preferred_time_zone": "Pacific Standard Time",
            "preferred_support_language": "en-US",
            "country": "usa"
          },
          "quota_ticket_details": {
            "quota_change_request_version": "1.0",
            "quota_change_request_sub_type": "Subscription",
            "quota_change_requests": [
              {
                "region": "EastUS",
                "payload": "{\"NewLimit\":200,\"Type\":\"Account\"}"
              }
            ]
          }
        }
        # result = self.mgmt_client.support_tickets.create(support_ticket_name=SUPPORT_TICKET_NAME, create_support_ticket_parameters=BODY)
        # result = result.result()

        # /Communications/put/AddCommunicationToSubscriptionTicket[put]
        BODY = {
          "subject": "This is a test message from a customer!",
          "body": "This is a test message from a customer!",
          "sender": "user@contoso.com"
        }
        # result = self.mgmt_client.communications.create(support_ticket_name=SUPPORT_TICKET_NAME, communication_name=COMMUNICATION_NAME, create_communication_parameters=BODY)
        # result = result.result()

        # /Communications/get/Get communication details for a subscription support ticket[get]
        # result = self.mgmt_client.communications.get(support_ticket_name=SUPPORT_TICKET_NAME, communication_name=COMMUNICATION_NAME)

        # /Communications/get/List web communications for a subscription support ticket[get]
        # result = self.mgmt_client.communications.list(support_ticket_name=SUPPORT_TICKET_NAME, filter="communicationType eq 'web'")

        # /Communications/get/List communications for a subscription support ticket[get]
        # result = self.mgmt_client.communications.list(support_ticket_name=SUPPORT_TICKET_NAME)

        # /Communications/get/List web communication created on or after a specific date for a subscription support ticket[get]
        # result = self.mgmt_client.communications.list(support_ticket_name=SUPPORT_TICKET_NAME, filter="communicationType eq 'web' and createdDate ge 2020-03-10T22:08:51Z")

        # /ProblemClassifications/get/Gets details of problemClassification for Azure service[get]
        result = self.mgmt_client.problem_classifications.get(service_name=SERVICE_NAME, problem_classification_name=PROBLEM_CLASSIFICATION_NAME)

        # /SupportTickets/get/Get details of a subscription ticket[get]
        # result = self.mgmt_client.support_tickets.get(support_ticket_name=SUPPORT_TICKET_NAME)

        # /SupportTickets/get/List support tickets in open state for a subscription[get]
        result = self.mgmt_client.support_tickets.list(filter="status eq 'Open'")

        # /ProblemClassifications/get/Gets list of problemClassifications for a service for which a support ticket can be created[get]
        result = self.mgmt_client.problem_classifications.list(service_name=SERVICE_NAME)

        # /SupportTickets/get/List support tickets created on or after a certain date and in open state for a subscription[get]
        result = self.mgmt_client.support_tickets.list(filter="createdDate ge 2020-03-10T22:08:51Z and status eq 'Open'")

        # /Services/get/Gets list of services for which a support ticket can be created[get]
        result = self.mgmt_client.services.list()

        # /Communications/post/Checks whether name is available for Communication resource[post]
        result = self.mgmt_client.communications.check_name_availability(support_ticket_name=SUPPORT_TICKET_NAME, name="sampleName", type="Microsoft.Support/communications")

        # /SupportTickets/patch/Update contact details of a support ticket[patch]
        BODY = {
          "contact_details": {
            "first_name": "first name",
            "last_name": "last name",
            "preferred_contact_method": "email",
            "primary_email_address": "test.name@contoso.com",
            "additional_email_addresses": [
              "tname@contoso.com",
              "teamtest@contoso.com"
            ],
            "phone_number": "123-456-7890",
            "preferred_time_zone": "Pacific Standard Time",
            "country": "USA",
            "preferred_support_language": "en-US"
          }
        }
        # result = self.mgmt_client.support_tickets.update(support_ticket_name=SUPPORT_TICKET_NAME, update_support_ticket=BODY)

        # /SupportTickets/patch/Update severity of a support ticket[patch]
        BODY = {
          "severity": "critical"
        }
        # result = self.mgmt_client.support_tickets.update(support_ticket_name=SUPPORT_TICKET_NAME, update_support_ticket=BODY)

        # /SupportTickets/patch/Update status of a support ticket[patch]
        BODY = {
          "status": "closed"
        }
        # result = self.mgmt_client.support_tickets.update(support_ticket_name=SUPPORT_TICKET_NAME, update_support_ticket=BODY)

        # /SupportTickets/post/Checks whether name is available for SupportTicket resource[post]
        result = self.mgmt_client.support_tickets.check_name_availability(name="sampleName", type="Microsoft.Support/supportTickets")


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
