# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.eventgrid.models
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.eventgrid import EventGridManagementClient
from azure.mgmt.eventgrid.models import (
    WebHookEventSubscriptionDestination,
    StorageQueueEventSubscriptionDestination,
    StorageBlobDeadLetterDestination,
    EventSubscriptionFilter,
    EventSubscription,
    InputSchema,
    EventDeliverySchema,
    Topic,
    RetryPolicy
)

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer


class MgmtEventGridTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtEventGridTest, self).setUp()
        self.eventgrid_client = self.create_mgmt_client(EventGridManagementClient)

    def process(self, result):
        pass

    @ResourceGroupPreparer()
    @unittest.skip('Not currently enabled for the 2018-05-01-preview API version')
    def test_topic_types(self, resource_group, location):
        # List all topic types
        for result in self.eventgrid_client.topic_types.list():
            self.process(result)

    @ResourceGroupPreparer()
    def test_user_topics(self, resource_group, location):
        topic_name = "kalspython1"
        eventsubscription_name = "kalspythonEventSubscription2"

        # Create a new topic and verify that it is created successfully
        topic_result_create = self.eventgrid_client.topics.create_or_update(resource_group.name, topic_name, Topic(location="westcentralus"))
        topic = topic_result_create.result()
        self.assertEqual(topic.name, topic_name)

        # Create a new event subscription to this topic
        # Use this for recording mode
        # scope = "/subscriptions/55f3dcd4-cac7-43b4-990b-a139d62a1eb2/resourceGroups/" + resource_group.name + "/providers/Microsoft.EventGrid/topics/" + topic_name
        scope = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/" + resource_group.name + "/providers/Microsoft.EventGrid/topics/" + topic_name

        destination = WebHookEventSubscriptionDestination(
            # TODO: Before recording tests, replace with a valid Azure function URL
            endpoint_url="https://kalsfunc1.azurewebsites.net/api/HttpTriggerCSharp1?code=hidden"
        )
        filter = EventSubscriptionFilter()

        event_subscription_info = EventSubscription(destination=destination, filter=filter)
        es_result_create = self.eventgrid_client.event_subscriptions.create_or_update(scope, eventsubscription_name, event_subscription_info)
        event_subscription = es_result_create.result()
        self.assertEqual(eventsubscription_name, event_subscription.name)

        # Delete the event subscription
        self.eventgrid_client.event_subscriptions.delete(scope, eventsubscription_name).wait()

        # Delete the topic
        self.eventgrid_client.topics.delete(resource_group.name, topic_name).wait()


    @ResourceGroupPreparer()
    def test_input_mappings_and_queue_destination(self, resource_group, location):
        topic_name = "kalspython2"
        eventsubscription_name = "kalspythonEventSubscription3"

        input_schema = InputSchema.cloud_event_v01_schema
        # Create a new topic and verify that it is created successfully
        topic = Topic(location="westcentralus", tags=None, input_schema=input_schema, input_schema_mapping=None)
        topic_result_create = self.eventgrid_client.topics.create_or_update(resource_group.name, topic_name, topic)
        topic = topic_result_create.result()
        self.assertEqual(topic.name, topic_name)
        self.assertEqual(topic.input_schema, "CloudEventV01Schema")        

        # Create a new event subscription to this topic
        # Use this for recording mode
        # scope = "/subscriptions/55f3dcd4-cac7-43b4-990b-a139d62a1eb2/resourceGroups/" + resource_group.name + "/providers/Microsoft.EventGrid/topics/" + topic_name
        scope = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/" + resource_group.name + "/providers/Microsoft.EventGrid/topics/" + topic_name

        destination = StorageQueueEventSubscriptionDestination(
            resource_id= "/subscriptions/55f3dcd4-cac7-43b4-990b-a139d62a1eb2/resourceGroups/kalstest/providers/Microsoft.Storage/storageAccounts/kalsdemo",
            queue_name= "kalsdemoqueue"
        )

        deadletter_destination = StorageBlobDeadLetterDestination(
            resource_id= "/subscriptions/55f3dcd4-cac7-43b4-990b-a139d62a1eb2/resourceGroups/kalstest/providers/Microsoft.Storage/storageAccounts/kalsdemo",
            blob_container_name= "dlq"            
        )

        filter = EventSubscriptionFilter()

        event_subscription_info = EventSubscription(
            destination=destination,
            filter=filter,
            dead_letter_destination=deadletter_destination,
            event_delivery_schema=EventDeliverySchema.cloud_event_v01_schema,
            retry_policy=RetryPolicy(event_time_to_live_in_minutes=5, max_delivery_attempts=10)
        )
        es_result_create = self.eventgrid_client.event_subscriptions.create_or_update(scope, eventsubscription_name, event_subscription_info)
        event_subscription = es_result_create.result()
        self.assertEqual(eventsubscription_name, event_subscription.name)

        # Delete the event subscription
        self.eventgrid_client.event_subscriptions.delete(scope, eventsubscription_name).wait()

        # Delete the topic
        self.eventgrid_client.topics.delete(resource_group.name, topic_name).wait()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
