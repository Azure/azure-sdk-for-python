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

from azure.common import AzureHttpError, AzureConflictHttpError
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, CloudEvent, EventGridEvent
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError,
)
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from eventgrid_preparer import (
    EventGridTopicPreparer
)

class EventGridClientTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @ResourceGroupPreparer(name_prefix='eventgridtest')
    @EventGridTopicPreparer(name_prefix='eventgridtest')
    def test_eg_client_good_credentials(self, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_location, **kwargs):
        print("testing")
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)

        client = EventGridPublisherClient(eventgrid_topic.endpoint, akc_credential)
        print("authenticating")

        dtime = datetime.now().strftime("%m-%d-%YT%I:%M:%S.%f")
        eg_event = EventGridEvent(id='831e1650-001e-001b-66ab-eeb76e06l631', subject="/blobServices/default/containers/oc2d2817345i200097container/blobs/oc2d2817345i20002296blob", data="{\"artist\": \"G\"}", event_type='recordInserted', event_time=dtime, data_version="1.0")
        print(eventgrid_topic)
        hostname = eventgrid_topic.endpoint
        try:
            print("publishing")
            response = client.publish_events(hostname, [eg_event])
            print(response)
        except ValueError:
            print("could not publish events")
        