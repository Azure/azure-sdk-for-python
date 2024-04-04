# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import sys
import os
import json
import pytest
import uuid
from datetime import datetime, timedelta
from azure.core.exceptions import (
    HttpResponseError,
    ClientAuthenticationError,
    ServiceRequestError,
)
from msrest.serialization import UTC
import datetime as dt

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, EventGridEvent
from azure.core.messaging import CloudEvent

from eventgrid_preparer import (
    EventGridPreparer,
)


class TestEventGridPublisherClientExceptions(AzureMgmtRecordedTestCase):
    def create_eg_publisher_client(self, endpoint):
        credential = self.get_credential(EventGridPublisherClient)
        client = self.create_client_from_credential(
            EventGridPublisherClient, credential=credential, endpoint=endpoint
        )
        return client

    @EventGridPreparer()
    @recorded_by_proxy
    def test_raise_on_auth_error(self, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential("bad credential")
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        eg_event = EventGridEvent(
            subject="sample",
            data={"sample": "eventgridevent"},
            event_type="Sample.EventGrid.Event",
            data_version="2.0",
        )
        with pytest.raises(
            ClientAuthenticationError,
            match="The request authorization key is not authorized for*",
        ):
            client.send(eg_event)

    @pytest.mark.skip("Fix during MQ - skip to unblock pipeline")
    @pytest.mark.live_test_only
    def test_raise_on_bad_resource(self):
        credential = AzureKeyCredential(os.environ["EVENTGRID_TOPIC_KEY"])
        client = EventGridPublisherClient(
            "https://bad-resource.eastus-1.eventgrid.azure.net/api/events",
            credential,
        )
        eg_event = CloudEvent(
            subject="sample",
            data={"sample": "eventgridevent"},
            source="source",
            type="Sample.Cloud.Event",
        )
        with pytest.raises(HttpResponseError):
            client.send(eg_event)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_raise_on_large_payload(self, eventgrid_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_topic_endpoint)

        path = os.path.abspath(
            os.path.join(os.path.abspath(__file__), "..", "./large_data.json")
        )
        with open(path) as json_file:
            data = json.load(json_file)
        eg_event = EventGridEvent(
            subject="sample",
            data=data,
            event_type="Sample.EventGrid.Event",
            data_version="2.0",
        )
        with pytest.raises(HttpResponseError) as err:
            client.send(eg_event)
        assert "The maximum size (1536000) has been exceeded." in err.value.message
