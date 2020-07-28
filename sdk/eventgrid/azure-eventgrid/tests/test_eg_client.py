#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys
import os
import pytest
import time
from datetime import datetime, timedelta

#PACKAGE_PARENT = '..'
#SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))))
#sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
#print(sys.path)

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, CloudEvent, EventGridEvent

from eventgrid_preparer import (
    EventGridTopicPreparer
)


class EventGridClientTests(AzureMgmtTestCase):
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @ResourceGroupPreparer(name_prefix='eventgridtest')
    @EventGridTopicPreparer(name_prefix='eventgridtest')
    def test_eg_client_good_credentials(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, **kwargs):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        # remove "https://" and "/api/events" since 
        hostname = eventgrid_topic.endpoint.replace("https://", "").replace("/api/events", "")
        client = EventGridPublisherClient(hostname, akc_credential)
        eg_event = EventGridEvent(
                subject="sample", 
                data={"sample": "0"}, 
                event_type="Sample.Event",
                data_version="2.0"
                )
        client.send([eg_event])
        