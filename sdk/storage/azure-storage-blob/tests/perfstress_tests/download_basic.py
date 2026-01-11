# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
import aiohttp
import requests
from concurrent.futures import ThreadPoolExecutor

from devtools_testutils.perfstress_tests import RandomStream

from ._test_base import _BlobTest


TOKEN_SCOPE = "https://storage.azure.com/.default"

class DownloadBasicTest(_BlobTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.chunk_size = self.args.max_block_size or 4 * 1024 * 1024

    async def setup(self):
        await super().setup()
        data = RandomStream(self.args.size)
        await self.async_blob_client.upload_blob(data, max_concurrency=10)

        if self.async_token_credential:
            token = await self.async_token_credential.get_token(TOKEN_SCOPE)
            self.auth_header = "Bearer " + token.token
        else:
            raise NotImplementedError("DownloadBasicTest requires Entra ID authentication.")

    def run_sync(self):
        chunk_ranges = self._get_chunk_ranges()
        with ThreadPoolExecutor(self.args.max_concurrency) as executor:
            with requests.sessions.Session() as session:
                executor.map(lambda r: self.download_chunk_requests(
                    session, r[0], r[1]), chunk_ranges)

    async def run_async(self):
        chunk_ranges = self._get_chunk_ranges()
        semaphore = asyncio.Semaphore(self.args.max_concurrency)
        
        async with aiohttp.ClientSession() as session:
            tasks = [self.download_chunk_aiohttp(session, offset, end, semaphore) for offset, end in chunk_ranges]
            await asyncio.gather(*tasks)

    def _get_chunk_ranges(self):
        chunk_ranges = []
        offset = 0
        while offset < self.args.size:
            end = min(offset + self.chunk_size - 1, self.args.size - 1)
            chunk_ranges.append((offset, end))
            offset = end + 1
        return chunk_ranges

    def download_chunk_requests(self, session: requests.sessions.Session, offset: int, end: int):
        headers = {'x-ms-version': self.blob_client.api_version, 'Range': f'bytes={offset}-{end}', 'Authorization': self.auth_header}
        response = session.get(self.blob_client.url, headers=headers)

        if response.status_code in (200, 206):
            pass
        else:
            raise Exception(f"Download failed with status code {response.status_code}")

    async def download_chunk_aiohttp(self, session: aiohttp.ClientSession, offset: int, end: int, semaphore: asyncio.Semaphore):
        async with semaphore:
            headers = {'x-ms-version': self.blob_client.api_version, 'Range': f'bytes={offset}-{end}', 'Authorization': self.auth_header}
            async with session.get(self.blob_client.url, headers=headers) as response:
                if response.status in (200, 206):
                    await response.read()
                else:
                    raise Exception(f"Download failed with status code {response.status}")
