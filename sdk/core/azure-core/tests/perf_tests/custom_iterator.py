# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.core.paging import PageIterator
from azure.core.async_paging import AsyncPageIterator

class MockResponse:
    pass
    
class CustomIterator(PageIterator):
    def __init__(
            self,
            command,
            max_results=None,
            continuation_token=None,
        ):
        super(CustomIterator, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.max_results = max_results
        self.results_per_page = int(max_results or "1")

    def _get_next_cb(self, continuation_token):
        return self._command(
            maxresults=self.max_results,
            marker=continuation_token or None,
        ) 

    def _extract_data_cb(self, response):
        try:
            next_marker = response.text().split('<NextMarker>')[1].split('</NextMarker>')[0]
        except IndexError:
            next_marker = None

        # TODO: test with parsing blob responses - see how much time it adds
        # if max results specified, then return that list of length max results
        return next_marker, [MockResponse() for _ in range(self.results_per_page)]

class AsyncCustomIterator(AsyncPageIterator):
    def __init__(
            self,
            command,
            max_results=None,
            continuation_token=None,
        ):
        super(AsyncCustomIterator, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.max_results = max_results
        self.results_per_page = int(max_results or "1")

    async def _get_next_cb(self, continuation_token):
        return await self._command(
            maxresults=self.max_results,
            marker=continuation_token or None,
        ) 

    async def _extract_data_cb(self, response):
        try:
            next_marker = response.text().split('<NextMarker>')[1].split('</NextMarker>')[0]
        except IndexError:
            next_marker = None

        # TODO: test with parsing blob responses - see how much time it adds
        return next_marker, [MockResponse() for _ in range(self.results_per_page)]
