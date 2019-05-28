# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import time

from msrestazure.azure_exceptions import CloudError
import azure.mgmt.eventhub.models
from azure.mgmt.eventhub.models import EHNamespace
from azure.mgmt.eventhub.models import EHNamespace, Sku, SkuName, AuthorizationRule, AccessRights, AccessKeys, Eventhub, CaptureDescription, Destination, EncodingCaptureDescription, ConsumerGroup, ErrorResponseException, ErrorResponse
from azure.common.credentials import ServicePrincipalCredentials

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtEventHubTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtEventHubTest, self).setUp()

        self.eventhub_client = self.create_mgmt_client(
            azure.mgmt.eventhub.EventHubManagementClient
        )

    @ResourceGroupPreparer()
    def test_eh_consumergroup_curd(self, resource_group, location):

        resource_group_name = resource_group.name

        # Create a Namespace
        namespace_name = "pythontestcaseeventhubnamespaceConsumerGroup"

        namespaceparameter = EHNamespace(location=location, tags={'tag1': 'value1', 'tag2': 'value2'}, sku=Sku(name=SkuName.standard))
        poller = self.eventhub_client.namespaces.create_or_update(resource_group_name, namespace_name,
                                                                  namespaceparameter)
        creatednamespace = poller.result()
        self.assertEqual(creatednamespace.name, namespace_name)

        #
        # # Get created Namespace
        #
        getnamespaceresponse = self.eventhub_client.namespaces.get(resource_group_name, namespace_name)
        self.assertEqual(getnamespaceresponse.name, namespace_name)

        # # Create a Eventhub
        eventhub_name = "testingpythontestcaseeventhubConsumerGroup"
        eventhubparameter = Eventhub(
            message_retention_in_days=4,
            partition_count=4,
            capture_description=CaptureDescription(
                enabled=True,
                encoding=EncodingCaptureDescription.avro,
                interval_in_seconds=120,
                size_limit_in_bytes=10485763,
                destination=Destination(
                    name="EventHubArchive.AzureBlockBlob",
                    storage_account_resource_id="/subscriptions/"+self.settings.SUBSCRIPTION_ID+"/resourceGroups/Default-Storage-SouthCentralUS/providers/Microsoft.ClassicStorage/storageAccounts/arjunteststorage",
                    blob_container="container",
                    archive_name_format="{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}")
            )
        )
        createdeventhubresponse = self.eventhub_client.event_hubs.create_or_update(resource_group_name, namespace_name,
                                                                                   eventhub_name, eventhubparameter)
        self.assertEqual(createdeventhubresponse.name,eventhub_name)
        self.assertEqual(createdeventhubresponse.capture_description.interval_in_seconds, 120)

        # Get the created eventhub
        geteventhubresponse = self.eventhub_client.event_hubs.get(resource_group_name, namespace_name, eventhub_name)
        self.assertEqual(geteventhubresponse.name, eventhub_name)
        self.assertEqual(geteventhubresponse.capture_description.interval_in_seconds, 120)
        #Get the List of eventhub by namespaces
        getlistbynamespaceeventhubresponse = list(self.eventhub_client.event_hubs.list_by_namespace(resource_group_name,
                                                                                                    namespace_name))
        self.assertGreater(len(getlistbynamespaceeventhubresponse), 0)

        # # update the Created eventhub
        eventhubupdateparameter = Eventhub(
            message_retention_in_days=6,
            partition_count=4,
            capture_description=CaptureDescription(
                enabled=True,
                encoding=EncodingCaptureDescription.avro,
                interval_in_seconds=130,
                size_limit_in_bytes=10485900,
                destination=Destination(
                    name="EventHubArchive.AzureBlockBlob",
                    storage_account_resource_id="/subscriptions/"+self.settings.SUBSCRIPTION_ID+"/resourceGroups/Default-Storage-SouthCentralUS/providers/Microsoft.ClassicStorage/storageAccounts/arjunteststorage",
                    blob_container="container",
                    archive_name_format="{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}")
            )
        )

        updateeventhubresponse = self.eventhub_client.event_hubs.create_or_update(resource_group_name, namespace_name,
                                                                                   eventhub_name, eventhubupdateparameter)
        self.assertEqual(updateeventhubresponse.name, eventhub_name)
        self.assertEqual(updateeventhubresponse.capture_description.interval_in_seconds, 130)
        self.assertEqual(updateeventhubresponse.message_retention_in_days, 6)
        self.assertEqual(updateeventhubresponse.capture_description.size_limit_in_bytes, 10485900)

        # Create ConsumerGroup
        consumergroup_name = "testingpythontestcaseconsumergroup"
        createconsumergroupresponse = self.eventhub_client.consumer_groups.create_or_update(resource_group_name, namespace_name,
                                                                                  eventhub_name, consumergroup_name,
                                                                                            "Testing the User Metadata")

        self.assertEqual(createconsumergroupresponse.name, consumergroup_name)
        self.assertEqual(createconsumergroupresponse.user_metadata, "Testing the User Metadata")

        # Get the Created Consumer group
        getconsumergroupresponse = self.eventhub_client.consumer_groups.get(resource_group_name,
                                                                                           namespace_name,
                                                                                           eventhub_name,
                                                                                           consumergroup_name)
        # update the Created Consumer group
        updateconsumergroupresponse = self.eventhub_client.consumer_groups.create_or_update(resource_group_name,
                                                                                           namespace_name,
                                                                                           eventhub_name,
                                                                                           consumergroup_name,
                                                                                            "update user matadata for testing")
        self.assertEqual(updateconsumergroupresponse.name, consumergroup_name)
        self.assertEqual(updateconsumergroupresponse.user_metadata, "update user matadata for testing")

        # delete the consumergroup
        deleteconsumergroupresponse = self.eventhub_client.consumer_groups.delete(resource_group_name,
                                                                                            namespace_name,
                                                                                            eventhub_name,
                                                                                            consumergroup_name)
        # Delete the created eventhub
        geteventhubresponse = self.eventhub_client.event_hubs.delete(resource_group_name, namespace_name, eventhub_name)

        # Delete the create namespace
        try:
            deletenamespace = self.eventhub_client.namespaces.delete(resource_group_name, namespace_name).result()
        except CloudError as ErrorResponse:
            self.assertTrue("not found" in ErrorResponse.message)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()