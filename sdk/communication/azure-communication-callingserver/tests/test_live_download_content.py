# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
'''
    Adding testing for the download recording async use cases.
'''
from io import BytesIO
import pytest
import utils._test_constants as CONST
from _shared.testcase  import CommunicationTestCase

from azure.communication.callingserver import CallingServerClient
from azure.communication.callingserver._models import ParallelDownloadOptions

class ContentDownloadTests(CommunicationTestCase):

    def setUp(self):
        super(ContentDownloadTests, self).setUp()
        self._document_id = "0-wus-d3-008713a3abdb3f3ae4904369277244c5"
        self._metadata_url = \
            'https://storage.asm.skype.com/v1/objects/{}/content/acsmetadata'.format(self._document_id)
        self._calling_server_client = \
            CallingServerClient.from_connection_string(self.connection_str)

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    def test_download_content_to_stream(self):
        stream = self._execute_test()
        metadata = stream.getvalue()
        self._verify_metadata(metadata)

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    def test_download_content_to_stream_on_chunks(self):
        stream = self._execute_test({'block_size': 400})
        metadata = stream.getvalue()
        self._verify_metadata(metadata)

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    def test_download_content_to_stream_on_chunks_parallel(self):
        stream = self._execute_test(
                {
                    'max_concurrency': 3,
                    'block_size': 400
                })
        metadata = stream.getvalue()
        self._verify_metadata(metadata)

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    def test_download_content_to_stream_with_redirection(self):
        stream = self._execute_test()
        metadata = stream.getvalue()
        self._verify_metadata(metadata)

    def _execute_test(self, download_options={}):
        downloader = self._calling_server_client.download(self._metadata_url, **download_options)

        stream = BytesIO()
        downloader.readinto(stream)
        return stream

    def _verify_metadata(self, metadata):
        self.assertIsNotNone(metadata)
        self.assertTrue(metadata.__contains__(bytes(self._document_id.encode('utf-8'))))
