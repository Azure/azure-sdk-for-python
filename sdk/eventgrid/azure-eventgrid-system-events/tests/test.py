import pytest
from azure.eventgrid.system.events.models import AcsChatEventBaseProperties
from devtools_testutils import AzureRecordedTestCase


class SystemEventTest(AzureRecordedTestCase):

    @pytest.mark.live_test_only
    def test_acs_chat_event_base_properties():
        event = AcsChatEventBaseProperties()
        assert event is not None