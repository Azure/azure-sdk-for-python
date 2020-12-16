#--------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#--------------------------------------------------------------------------

from typing import AsyncIterator, TypeVar, List

from azure.core.async_paging import AsyncItemPaged, AsyncList
from azure.core.exceptions import HttpResponseError

import pytest


T = TypeVar("T")


async def _as_list(async_iter: AsyncIterator[T]) -> List[T]:
    """Flatten an async iterator into a list.

    For testing purpose.
    """
    # 3.6 only : result_iterated = [obj async for obj in deserialized]
    result = []
    async for el in async_iter:
        result.append(el)
    return result


class TestPaging:

    @pytest.mark.asyncio
    async def test_basic_paging(self):

        async def get_next(continuation_token=None):
            """Simplify my life and return JSON and not response, but should be response.
            """
            if not continuation_token:
                return {
                    'nextLink': 'page2',
                    'value': ['value1.0', 'value1.1']
                }
            else:
                return {
                    'nextLink': None,
                    'value': ['value2.0', 'value2.1']
                }

        async def extract_data(response):
            return response['nextLink'], AsyncList(response['value'])

        pager = AsyncItemPaged(get_next, extract_data)
        result_iterated = await _as_list(pager)

        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == result_iterated

    @pytest.mark.asyncio
    async def test_advance_paging(self):

        async def get_next(continuation_token=None):
            """Simplify my life and return JSON and not response, but should be response.
            """
            if not continuation_token:
                return {
                    'nextLink': 'page2',
                    'value': ['value1.0', 'value1.1']
                }
            else:
                return {
                    'nextLink': None,
                    'value': ['value2.0', 'value2.1']
                }

        async def extract_data(response):
            return response['nextLink'], AsyncList(response['value'])

        pager = AsyncItemPaged(get_next, extract_data).by_page()

        page1 = await pager.__anext__()
        assert ['value1.0', 'value1.1'] == await _as_list(page1)

        page2 = await pager.__anext__()
        assert ['value2.0', 'value2.1'] == await _as_list(page2)

        with pytest.raises(StopAsyncIteration):
            await pager.__anext__()


    @pytest.mark.asyncio
    async def test_none_value(self):
        async def get_next(continuation_token=None):
            return {
                'nextLink': None,
                'value': None
            }

        async def extract_data(response):
            return response['nextLink'], AsyncList(response['value'] or [])

        pager = AsyncItemPaged(get_next, extract_data)
        result_iterated = await _as_list(pager)

        assert len(result_iterated) == 0


    @pytest.mark.asyncio
    async def test_paging_continue_on_error(self):
        async def get_next(continuation_token=None):
            if not continuation_token:
                return {
                    'nextLink': 'foo',
                    'value': ['bar']
                }
            else:
                raise HttpResponseError()
        async def extract_data(response):
            return response['nextLink'], iter(response['value'] or [])
        
        pager = AsyncItemPaged(get_next, extract_data)
        assert await pager.__anext__() == 'bar'
        with pytest.raises(HttpResponseError) as err:
            await pager.__anext__()
        assert err.value.continuation_token == 'foo'
