#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys
import os
import pytest

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, CloudEvent, EventGridEvent

from eventgrid_preparer import (
    EventGridTopicPreparer
)


class EventGridConsumerTests(AzureMgmtTestCase):
    pass
    #@pytest.mark.liveTest
    #@ResourceGroupPreparer(name_prefix='eventgridtest')
    #@EventGridTopicPreparer(name_prefix='eventgridtest')
    #def test_eg_consumer(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, **kwargs):
    #    akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
    #    hostname = eventgrid_topic.endpoint
    #    client = EventGridPublisherClient(hostname, akc_credential)
    #    eg_event = EventGridEvent(
    #            subject="sample", 
    #            data={"sample": "eventgridevent"}, 
    #            event_type="Sample.EventGrid.Event",
    #            data_version="2.0"
    #            )
    #    client.send([eg_event])
