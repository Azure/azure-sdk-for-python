# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import uuid
import functools

import requests

from azure_devtools.perfstress_tests import PerfStressTest

from azure.storage.blob import BlockBlobService


def test_proxy_callback(proxy_policy, request):
    if proxy_policy.recording_id and proxy_policy.mode:
        live_endpoint = request.host
        request.host = proxy_policy._proxy_url.netloc
        request.headers["x-recording-id"] = proxy_policy.recording_id
        request.headers["x-recording-mode"] = proxy_policy.mode
        request.headers["x-recording-remove"] = "false"

        # Ensure x-recording-upstream-base-uri header is only set once, since the
        # same HttpMessage will be reused on retries
        if "x-recording-upstream-base-uri" not in request.headers:
            original_endpoint = "https://{}".format(live_endpoint)
            request.headers["x-recording-upstream-base-uri"] = original_endpoint


class _LegacyServiceTest(PerfStressTest):
    service_client = None
    async_service_client = None

    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_STORAGE_CONNECTION_STRING")
        session = None
        if self.args.test_proxies:
            session = requests.Session()
            session.verify = False
        if not _LegacyServiceTest.service_client or self.args.no_client_share:
            _LegacyServiceTest.service_client = BlockBlobService(
                connection_string=connection_string,
                request_session=session)
            _LegacyServiceTest.service_client.MAX_SINGLE_PUT_SIZE = self.args.max_put_size
            _LegacyServiceTest.service_client.MAX_BLOCK_SIZE = self.args.max_block_size
            _LegacyServiceTest.service_client.MIN_LARGE_BLOCK_UPLOAD_THRESHOLD = self.args.buffer_threshold
        self.async_service_client = None
        self.service_client = _LegacyServiceTest.service_client

        if self.args.test_proxies:
            self.service_client.request_callback = functools.partial(
                test_proxy_callback,
                self._test_proxy_policy
            )

    @staticmethod
    def add_arguments(parser):
        super(_LegacyServiceTest, _LegacyServiceTest).add_arguments(parser)
        parser.add_argument('--max-put-size', nargs='?', type=int, help='Maximum size of data uploading in single HTTP PUT. Defaults to 64*1024*1024', default=64*1024*1024)
        parser.add_argument('--max-block-size', nargs='?', type=int, help='Maximum size of data in a block within a blob. Defaults to 4*1024*1024', default=4*1024*1024)
        parser.add_argument('--buffer-threshold', nargs='?', type=int, help='Minimum block size to prevent full block buffering. Defaults to 4*1024*1024+1', default=4*1024*1024+1)
        parser.add_argument('--max-concurrency', nargs='?', type=int, help='Maximum number of concurrent threads used for data transfer. Defaults to 1', default=1)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of data to transfer.  Default is 10240.', default=10240)
        parser.add_argument('--no-client-share', action='store_true', help='Create one ServiceClient per test instance.  Default is to share a single ServiceClient.', default=False)


class _LegacyContainerTest(_LegacyServiceTest):
    container_name = "perfstress-legacy-" + str(uuid.uuid4())

    def __init__(self, arguments):
        super().__init__(arguments)

    async def global_setup(self):
        await super().global_setup()
        self.service_client.create_container(self.container_name)

    async def global_cleanup(self):
        self.service_client.delete_container(self.container_name)
        await super().global_cleanup()
