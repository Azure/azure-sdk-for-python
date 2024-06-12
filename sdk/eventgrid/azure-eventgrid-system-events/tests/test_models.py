# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.eventgrid.system.events.models import AcsChatEventBaseProperties

class EventGridSystemEvents(object):
    def test_system_event(self):
        event = AcsChatEventBaseProperties()

        assert event is not None