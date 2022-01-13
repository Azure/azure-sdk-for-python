# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

raise unittest.SkipTest("Skipping all tests")

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
    Domain,
    NumberLessThanAdvancedFilter,
    RetryPolicy
)

from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy


class TestMgmtEventGrid(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.eventgrid_client = self.create_mgmt_client(EventGridManagementClient)

    def process(self, result):
        pass

    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_topic_types(self, resource_group, location):
        # List all topic types
        for result in self.eventgrid_client.topic_types.list():
            self.process(result)

    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_user_topics(self, resource_group, location):
        topic_name = "kalspython1"
        eventsubscription_name = "kalspythonEventSubscription2"

        # Create a new topic and verify that it is created successfully
        topic_result_create = self.eventgrid_client.topics.create_or_update(resource_group.name, topic_name, Topic(location="westcentralus"))
        topic = topic_result_create.result()
        assert topic.name == topic_name

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
        assert eventsubscription_name == event_subscription.name

        # Delete the event subscription
        self.eventgrid_client.event_subscriptions.delete(scope, eventsubscription_name).wait()

        # Delete the topic
        self.eventgrid_client.topics.delete(resource_group.name, topic_name).wait()


    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_input_mappings_and_queue_destination(self, resource_group, location):
        topic_name = "kalspython2"
        eventsubscription_name = "kalspythonEventSubscription3"

        input_schema = InputSchema.cloud_event_v01_schema
        # Create a new topic and verify that it is created successfully
        topic = Topic(location="westcentralus", tags=None, input_schema=input_schema, input_schema_mapping=None)
        topic_result_create = self.eventgrid_client.topics.create_or_update(resource_group.name, topic_name, topic)
        topic = topic_result_create.result()
        assert topic.name == topic_name
        assert topic.input_schema == "CloudEventV01Schema"

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
        assert eventsubscription_name == event_subscription.name

        # Delete the event subscription
        self.eventgrid_client.event_subscriptions.delete(scope, eventsubscription_name).wait()

        # Delete the topic
        self.eventgrid_client.topics.delete(resource_group.name, topic_name).wait()


    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_domains_and_advanced_filter(self, resource_group, location):
        domain_name = "kalspythond1"
        eventsubscription_name = "kalspythonEventSubscription2"

        # Create a new domain and verify that it is created successfully
        domain_result_create = self.eventgrid_client.domains.create_or_update(resource_group.name, domain_name, Domain(location="westcentralus"))
        domain = domain_result_create.result()
        assert domain.name == domain_name

        # Create a new event subscription to this domain
        # Use this for recording mode
        # scope = "/subscriptions/55f3dcd4-cac7-43b4-990b-a139d62a1eb2/resourceGroups/" + resource_group.name + "/providers/Microsoft.EventGrid/domains/" + domain_name
        scope = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/" + resource_group.name + "/providers/Microsoft.EventGrid/domains/" + domain_name

        destination = WebHookEventSubscriptionDestination(
            # TODO: Before recording tests, replace with a valid Azure function URL
            endpoint_url="https://kalsfunc1.azurewebsites.net/api/HttpTriggerCSharp1?code=hidden"
        )
        filter = EventSubscriptionFilter()
        advanced_filter = NumberLessThanAdvancedFilter(key="data.key1", value=4.0)
        filter.advanced_filters = []
        filter.advanced_filters.append(advanced_filter)

        event_subscription_info = EventSubscription(destination=destination, filter=filter)
        es_result_create = self.eventgrid_client.event_subscriptions.create_or_update(scope, eventsubscription_name, event_subscription_info)
        event_subscription = es_result_create.result()
        assert eventsubscription_name == event_subscription.name

        # Delete the event subscription
        self.eventgrid_client.event_subscriptions.delete(scope, eventsubscription_name).wait()

        # Delete the domain
        self.eventgrid_client.domains.delete(resource_group.name, domain_name).wait()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
