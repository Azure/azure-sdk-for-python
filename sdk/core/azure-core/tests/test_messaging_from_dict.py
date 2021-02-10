import logging
import sys
import os
import pytest
import json

from azure.core.messaging import CloudEvent
from devtools_testutils import AzureMgmtTestCase
from _mocks import (
    cloud_storage_dict,
    cloud_custom_dict_base64,
    cloud_custom_dict_with_extensions,
)

class EventGridDeserializerTests(AzureMgmtTestCase):

    # Cloud Event tests
    def test_cloud_storage_dict(self, **kwargs):
        event = CloudEvent.from_dict(cloud_storage_dict)
        assert event.data == {
            "api":"PutBlockList",
            "client_request_id":"6d79dbfb-0e37-4fc4-981f-442c9ca65760",
            "request_id":"831e1650-001e-001b-66ab-eeb76e000000",
            "e_tag":"0x8D4BCC2E4835CD0",
            "content_type":"application/octet-stream",
            "content_length":524288,
            "blob_type":"BlockBlob",
            "url":"https://oc2d2817345i60006.blob.core.windows.net/oc2d2817345i200097container/oc2d2817345i20002296blob",
            "sequencer":"00000000000004420000000000028963",
            "storage_diagnostics":{"batchId":"b68529f3-68cd-4744-baa4-3c0498ec19f0"}
        }
        assert event.specversion == "1.0"
        assert event.__class__ == CloudEvent


    def test_cloud_custom_dict_with_extensions(self, **kwargs):
        event = CloudEvent.from_dict(cloud_custom_dict_with_extensions)
        assert event.data == {"team": "event grid squad"}
        assert event.__class__ == CloudEvent
        assert event.extensions == {"ext1": "example", "ext2": "example2"}

    def test_cloud_custom_dict_base64(self, **kwargs):
        event = CloudEvent.from_dict(cloud_custom_dict_base64)
        assert event.data == b'cloudevent'
        assert event.data_base64 == None
        assert event.specversion == "1.0"
        assert event.__class__ == CloudEvent