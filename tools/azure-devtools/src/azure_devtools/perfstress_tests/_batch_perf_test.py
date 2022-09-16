# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import cProfile
import os
import aiohttp
import time
from typing import Optional, Any, Dict, List

from urllib.parse import urljoin

from ._perf_stress_base import _PerfTestBase
from ._policies import PerfTestProxyPolicy


class BatchPerfTest(_PerfTestBase):

    def __init__(self, arguments):
        super().__init__(arguments)

        self._session: Optional[aiohttp.ClientSession] = None
        self._test_proxy: Optional[List[str]] = None
        self._test_proxy_policy: Optional[PerfTestProxyPolicy] = None
        self._client_kwargs: Dict[str, Any] = {}
        self._recording_id: Optional[str] = None

        if self.args.insecure:
            # Disable SSL verification for SDK Client
            self._client_kwargs['connection_verify'] = False

            # Disable SSL verification for test proxy session
            self._session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))

            # Suppress warnings
            import warnings
            from urllib3.exceptions import InsecureRequestWarning
            warnings.simplefilter('ignore', InsecureRequestWarning)
        else:
            self._session = aiohttp.ClientSession()

        if self.args.test_proxies:
            # Add policy to redirect requests to the test proxy
            self._test_proxy = self.args.test_proxies[self._parallel_index % len(self.args.test_proxies)]
            self._test_proxy_policy = PerfTestProxyPolicy(self._test_proxy)
            self._client_kwargs['per_retry_policies'] = [self._test_proxy_policy]

    async def post_setup(self) -> None:
        """
        Post-setup called once per parallel test instance.
        Used by base classes to setup state (like test-proxy) after all derived class setup is complete.
        """
        if self._test_proxy_policy:
            # Make one call to run() before starting recording, to avoid capturing
            # one-time setup like authorization requests.
            if self.args.sync:
                self.run_batch_sync()
            else:
                await self.run_batch_async()
            await self._start_recording()
            self._test_proxy_policy.recording_id = self._recording_id
            self._test_proxy_policy.mode = "record"
            
            # Record one call to run()
            if self.args.sync:
                self.run_batch_sync()
            else:
                await self.run_batch_async()

            await self._stop_recording()
            await self._start_playback()
            self._test_proxy_policy.recording_id = self._recording_id
            self._test_proxy_policy.mode = "playback"

    async def pre_cleanup(self) -> None:
        """
        Pre-cleanup called once per parallel test instance.
        Used by base classes to cleanup state (like test-proxy) before all derived class cleanup runs.
        """
        # Only stop playback if it was successfully started
        if self._test_proxy_policy and self._test_proxy_policy.mode == 'playback':
            headers = {
                "x-recording-id": self._recording_id,
                "x-purge-inmemory-recording": "true"
            }
            url = urljoin(self._test_proxy, "/playback/stop")
            async with self._session.post(url, headers=headers) as resp:
                assert resp.status == 200

            # Stop redirecting requests to test proxy
            self._test_proxy_policy.recording_id = None
            self._test_proxy_policy.mode = None

    async def close(self) -> None:
        """
        Close any open client resources/connections per parallel test instance.
        """
        await self._session.close()

    async def _start_recording(self) -> None:
        url = urljoin(self._test_proxy, "/record/start")
        async with self._session.post(url) as resp:
            assert resp.status == 200
            self._recording_id = resp.headers["x-recording-id"]

    async def _stop_recording(self) -> None:
        headers = {"x-recording-id": self._recording_id}
        url = urljoin(self._test_proxy, "/record/stop")
        async with self._session.post(url, headers=headers) as resp:
            assert resp.status == 200

    async def _start_playback(self) -> None:
        headers = {"x-recording-id": self._recording_id}
        url = urljoin(self._test_proxy, "/playback/start")
        async with self._session.post(url, headers=headers) as resp:
            assert resp.status == 200
            self._recording_id = resp.headers["x-recording-id"]

    def run_batch_sync(self) -> int:
        """
        Run cumultive operation(s) - i.e. an operation that results in more than a single logical result.
        :returns: The number of completed results.
        :rtype: int
        """
        raise NotImplementedError("run_batch_sync must be implemented for {}".format(self.__class__.__name__))

    async def run_batch_async(self) -> int:
        """
        Run cumultive operation(s) - i.e. an operation that results in more than a single logical result.
        :returns: The number of completed results.
        :rtype: int
        """
        raise NotImplementedError("run_batch_async must be implemented for {}".format(self.__class__.__name__))

    def run_all_sync(self, duration: int) -> None:
        """
        Run all sync tests, including both warmup and duration.
        """
        self._completed_operations = 0
        self._last_completion_time = 0.0
        starttime = time.time()
        if self.args.profile:
            # If the profiler is used, ignore the duration and run once.
            import cProfile
            profile = cProfile.Profile()
            try:
                profile.enable()
                self._completed_operations += self.run_batch_sync()
            finally:
                profile.disable()
            self._last_completion_time = time.time() - starttime
            self._save_profile(profile, "sync")
        else:
            while self._last_completion_time < duration:
                self._completed_operations += self.run_batch_sync()
                self._last_completion_time = time.time() - starttime

    async def run_all_async(self, duration: int) -> None:
        """
        Run all async tests, including both warmup and duration.
        """
        self._completed_operations = 0
        self._last_completion_time = 0.0
        starttime = time.time()
        if self.args.profile:
            # If the profiler is used, ignore the duration and run once. 
            import cProfile
            profile = cProfile.Profile()
            try:
                profile.enable()
                self._completed_operations += await self.run_batch_async()
            finally:
                profile.disable()
            self._last_completion_time = time.time() - starttime
            self._save_profile(profile, "async")
        else:
            while self._last_completion_time < duration:
                self._completed_operations += await self.run_batch_async()
                self._last_completion_time = time.time() - starttime

    def _save_profile(self, profile: cProfile.Profile, sync: str) -> None:
        """
        Dump the profiler data to file in the current working directory.
        """
        if profile:
            profile_name = "{}/cProfile-{}-{}-{}.pstats".format(
                os.getcwd(),
                self.__class__.__name__,
                self._parallel_index,
                sync)
            print("Dumping profile data to {}".format(profile_name))
            profile.dump_stats(profile_name)
        else:
            print("No profile generated.")
