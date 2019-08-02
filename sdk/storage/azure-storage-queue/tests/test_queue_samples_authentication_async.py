# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta
import pytest
import asyncio
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
try:
    import settings_real as settings
except ImportError:
    import queue_settings_fake as settings

from queuetestcase import (
    QueueTestCase,
    TestMode,
    record
)


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response

class TestQueueAuthSamplesAsync(QueueTestCase):
    url = "{}://{}.queue.core.windows.net".format(
        settings.PROTOCOL,
        settings.STORAGE_ACCOUNT_NAME
    )

    connection_string = settings.CONNECTION_STRING
    shared_access_key = settings.STORAGE_ACCOUNT_KEY
    active_directory_application_id = settings.ACTIVE_DIRECTORY_APPLICATION_ID
    active_directory_application_secret = settings.ACTIVE_DIRECTORY_APPLICATION_SECRET
    active_directory_tenant_id = settings.ACTIVE_DIRECTORY_TENANT_ID

    async def _test_auth_connection_string(self):
        # Instantiate a QueueServiceClient using a connection string
        # [START auth_from_connection_string]
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(self.connection_string)
        # [END auth_from_connection_string]

        # Get information for the Queue Service
        properties = await queue_service.get_service_properties()

        assert properties is not None
    
    @record
    def test_auth_connection_string(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_auth_connection_string())

    async def _test_auth_shared_key(self):

        # Instantiate a QueueServiceClient using a shared access key
        # [START create_queue_service_client]
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient(account_url=self.url, credential=self.shared_access_key, transport=AiohttpTestTransport())
        # [END create_queue_service_client]
        # Get information for the Queue Service
        properties = await queue_service.get_service_properties()

        assert properties is not None

    @record
    def test_auth_shared_key(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_auth_shared_key())

    async def _test_auth_active_directory(self):
        pytest.skip('pending azure identity')

        # Get a token credential for authentication
        from azure.identity import ClientSecretCredential
        token_credential = ClientSecretCredential(
            self.active_directory_application_id,
            self.active_directory_application_secret,
            self.active_directory_tenant_id
        )

        # Instantiate a QueueServiceClient using a token credential
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient(account_url=self.url, credential=token_credential)

        # Get information for the Queue Service
        properties = await queue_service.get_service_properties()

        assert properties is not None

    @record
    def test_auth_active_directory(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_auth_active_directory())

    async def _test_auth_shared_access_signature(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Instantiate a QueueServiceClient using a connection string
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(self.connection_string, transport=AiohttpTestTransport())

        # Create a SAS token to use for authentication of a client
        sas_token = queue_service.generate_shared_access_signature(
            resource_types="object",
            permission="read",
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        assert sas_token is not None
    
    @record
    def test_auth_shared_access_signature(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_auth_shared_access_signature())
