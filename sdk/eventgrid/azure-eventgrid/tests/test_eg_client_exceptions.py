# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import os
import time
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from azure.eventgrid import EventGridClient
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from eventgrid_preparer import EventGridPreparer


class TestEGClientExceptions(AzureRecordedTestCase):
    def create_eg_client(self, endpoint, key):
        client = EventGridClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        return client

    @EventGridPreparer()
    @recorded_by_proxy
    def test_publish_cloud_event_bad_request(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)
        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source=None,
            subject="MySubject",
            data={"itemSku": "Contoso Item SKU #1"},
        )

        with pytest.raises(HttpResponseError):
            client.publish_cloud_events(eventgrid_topic_name, [event])

    @EventGridPreparer()
    @recorded_by_proxy    
    def test_publish_cloud_event_not_found(self, eventgrid_endpoint, eventgrid_key):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)
        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source=None,
            subject="MySubject",
            data={"itemSku": "Contoso Item SKU #1"},
        )

        with pytest.raises(ResourceNotFoundError):
            client.publish_cloud_events("faketopic", [event])

    @EventGridPreparer()
    @recorded_by_proxy
    def test_receive_cloud_event_not_found(self, eventgrid_endpoint, eventgrid_key, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        with pytest.raises(ResourceNotFoundError):
            client.receive_cloud_events("faketopic", eventgrid_event_subscription_name)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_receive_cloud_event_max_events_negative(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        with pytest.raises(HttpResponseError):
            client.receive_cloud_events(
                eventgrid_topic_name, eventgrid_event_subscription_name, max_events=-20
            )

    @EventGridPreparer()
    @recorded_by_proxy
    def test_receive_cloud_event_timeout_negative(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        with pytest.raises(HttpResponseError):
            client.receive_cloud_events(
                eventgrid_topic_name, eventgrid_event_subscription_name, max_wait_time=-20
            )

    @EventGridPreparer()
    @recorded_by_proxy
    def test_receive_cloud_event_timeout_max_value(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        with pytest.raises(HttpResponseError):
            client.receive_cloud_events(
                eventgrid_topic_name, eventgrid_event_subscription_name, max_wait_time=121
            )

    @EventGridPreparer()
    @recorded_by_proxy
    def test_receive_cloud_event_timeout_min_value(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        with pytest.raises(HttpResponseError):
            client.receive_cloud_events(
                eventgrid_topic_name, eventgrid_event_subscription_name, max_wait_time=9
            )

    @EventGridPreparer()
    @recorded_by_proxy
    def test_acknowledge_cloud_event_not_found(self, eventgrid_endpoint, eventgrid_key, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        with pytest.raises(ResourceNotFoundError):
            lock_tokens = AcknowledgeOptions(lock_tokens=["faketoken"])
            client.acknowledge_cloud_events(
                "faketopic", eventgrid_event_subscription_name, acknowledge_options=lock_tokens
            )

    @EventGridPreparer()
    @recorded_by_proxy
    def test_release_cloud_event_not_found(self, eventgrid_endpoint, eventgrid_key, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        with pytest.raises(ResourceNotFoundError):
            lock_tokens = ReleaseOptions(lock_tokens=["faketoken"])
            client.release_cloud_events(
                "faketopic", eventgrid_event_subscription_name, release_options=lock_tokens
            )

    @EventGridPreparer()
    @recorded_by_proxy
    def test_reject_cloud_event_not_found(self, eventgrid_endpoint, eventgrid_key, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)
        lock_tokens = RejectOptions(lock_tokens=["faketoken"])

        with pytest.raises(ResourceNotFoundError):
            client.reject_cloud_events(
                "faketopic", eventgrid_event_subscription_name, reject_options=lock_tokens
            )

    @EventGridPreparer()
    @recorded_by_proxy
    def test_acknowledge_cloud_event_invalid_token(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        lock_tokens = AcknowledgeOptions(lock_tokens=["faketoken"])
        ack = client.acknowledge_cloud_events(
            eventgrid_topic_name, eventgrid_event_subscription_name, acknowledge_options=lock_tokens
        )
        assert type(ack) == AcknowledgeResult
        assert ack.succeeded_lock_tokens == []
        assert type(ack.failed_lock_tokens[0]) == FailedLockToken
        assert ack.failed_lock_tokens[0].lock_token == "faketoken"

    @EventGridPreparer()
    @recorded_by_proxy
    def test_release_cloud_event_invalid_token(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        lock_tokens = ReleaseOptions(lock_tokens=["faketoken"])
        release = client.release_cloud_events(
            eventgrid_topic_name, eventgrid_event_subscription_name, release_options=lock_tokens
        )
        assert type(release) == ReleaseResult
        assert release.succeeded_lock_tokens == []
        assert type(release.failed_lock_tokens[0]) == FailedLockToken
        assert release.failed_lock_tokens[0].lock_token == "faketoken"

    @EventGridPreparer()
    @recorded_by_proxy
    def test_reject_cloud_event_invalid_token(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)
        lock_tokens = RejectOptions(lock_tokens=["faketoken"])

        reject = client.reject_cloud_events(
            eventgrid_topic_name, eventgrid_event_subscription_name, reject_options=lock_tokens
        )
        assert type(reject) == RejectResult
        assert reject.succeeded_lock_tokens == []
        assert type(reject.failed_lock_tokens[0]) == FailedLockToken
        assert reject.failed_lock_tokens[0].lock_token == "faketoken"
