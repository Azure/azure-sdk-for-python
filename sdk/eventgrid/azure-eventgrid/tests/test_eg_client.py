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

from eventgrid_preparer import EventGridBetaPreparer


class TestEGClientExceptions(AzureRecordedTestCase):
    def create_eg_client(self, endpoint, key):
        client = EventGridClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        return client

    @pytest.mark.skip("need to update conftest")
    @EventGridBetaPreparer()
    @recorded_by_proxy
    def test_publish_receive_cloud_event(self, variables, eventgrid_endpoint, eventgrid_key):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=b'this is binary data',
        )

        client.publish_cloud_events(
            "testtopic1", body=[event]
        )

        time.sleep(5)

        events = client.receive_cloud_events("testtopic1", "testsubscription1",max_events=1)
        lock_token = events.value[0].broker_properties.lock_token

        ack = client.acknowledge_cloud_events("testtopic1", "testsubscription1", lock_tokens=AcknowledgeOptions(lock_tokens=[lock_token]))
        assert len(ack.succeeded_lock_tokens) == 1
        assert len(ack.failed_lock_tokens) == 0

    @pytest.mark.skip("need to update conftest")
    @EventGridBetaPreparer()
    @recorded_by_proxy
    def test_publish_release_cloud_event(self, variables, eventgrid_endpoint, eventgrid_key):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=b'this is binary data',
        )

        client.publish_cloud_events(
            "testtopic1", body=[event]
        )

        time.sleep(5)

        events = client.receive_cloud_events("testtopic1", "testsubscription1",max_events=1)
        lock_token = events.value[0].broker_properties.lock_token

        ack = client.release_cloud_events("testtopic1", "testsubscription1", lock_tokens=ReleaseOptions(lock_tokens=[lock_token]))
        assert len(ack.succeeded_lock_tokens) == 1
        assert len(ack.failed_lock_tokens) == 0

        events = client.receive_cloud_events("testtopic1", "testsubscription1",max_events=1)
        assert events.value[0].broker_properties.delivery_count > 1