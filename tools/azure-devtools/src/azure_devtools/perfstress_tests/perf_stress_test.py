# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import aiohttp

from urllib.parse import urljoin
from ._policies import PerfTestProxyPolicy


class PerfStressTest:
    """Base class for implementing a python perf test.

    - run_sync and run_async must be implemented.
    - global_setup and global_cleanup are optional and run once, ever, regardless of parallelism.
    - setup and cleanup are run once per test instance (where each instance runs in its own thread/process), regardless of #iterations.
    - close is run once per test instance, after cleanup and global_cleanup.
    - run_sync/run_async are run once per iteration.
    """

    args = {}

    def __init__(self, arguments):
        self.args = arguments
        self._session = None
        self._test_proxy_policy = None
        self._client_kwargs = {}
        self._recording_id = None

        if self.args.test_proxy:
            self._session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))

            # SSL will be disabled for the test proxy requests, so suppress warnings
            import warnings
            from urllib3.exceptions import InsecureRequestWarning
            warnings.simplefilter('ignore', InsecureRequestWarning)

            # Add policy to redirect requests to the test proxy
            self._test_proxy_policy = PerfTestProxyPolicy(self.args.test_proxy)
            self._client_kwargs['per_retry_policies'] = [self._test_proxy_policy]

    async def global_setup(self):
        return

    async def global_cleanup(self):
        return

    async def record_and_start_playback(self):
        # Make one call to Run() before starting recording, to avoid capturing one-time setup like authorization requests
        if self.args.sync:
            self.run_sync()
        else:
            await self.run_async()

        await self._start_recording()
        self._test_proxy_policy.recording_id = self._recording_id
        self._test_proxy_policy.mode = "record"

        # Record one call to run()
        if self.args.sync:
            self.run_sync()
        else:
            await self.run_async()

        await self._stop_recording()
        await self._start_playback()
        self._test_proxy_policy.recording_id = self._recording_id
        self._test_proxy_policy.mode = "playback"

    async def stop_playback(self):
        headers = {
            "x-recording-id": self._recording_id,
            "x-purge-inmemory-recording": "true"
        }
        url = urljoin(self.args.test_proxy, "/playback/stop")
        async with self._session.post(url, headers=headers) as resp:
            assert resp.status == 200

        self._test_proxy_policy.recording_id = None
        self._test_proxy_policy.mode = None

    async def setup(self):
        return

    async def cleanup(self):
        return

    async def close(self):
        if self._session:
            await self._session.close()

    def run_sync(self):
        raise Exception("run_sync must be implemented for {}".format(self.__class__.__name__))

    async def run_async(self):
        raise Exception("run_async must be implemented for {}".format(self.__class__.__name__))

    async def _start_recording(self):
        url = urljoin(self.args.test_proxy, "/record/start")
        async with self._session.post(url) as resp:
            assert resp.status == 200
            self._recording_id = resp.headers["x-recording-id"]

    async def _stop_recording(self):
        headers = {"x-recording-id": self._recording_id}
        url = urljoin(self.args.test_proxy, "/record/stop")
        async with self._session.post(url, headers=headers) as resp:
            assert resp.status == 200

    async def _start_playback(self):
        headers = {"x-recording-id": self._recording_id}
        url = urljoin(self.args.test_proxy, "/playback/start")
        async with self._session.post(url, headers=headers) as resp:
            assert resp.status == 200
            self._recording_id = resp.headers["x-recording-id"]

    @staticmethod
    def add_arguments(parser):
        """
        Override this method to add test-specific argparser args to the class.
        These are accessible in __init__() and the self.args property.
        """
        return

    @staticmethod
    def get_from_env(variable):
        value = os.environ.get(variable)
        if not value:
            raise Exception("Undefined environment variable {}".format(variable))
        return value
