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

from azure.core.paging import ItemPaged
from azure.core.exceptions import HttpResponseError

import pytest


class TestPaging(object):

    def test_basic_paging(self):

        def get_next(continuation_token=None):
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

        def extract_data(response):
            return response['nextLink'], iter(response['value'])

        pager = ItemPaged(get_next, extract_data)
        result_iterated = list(pager)

        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == result_iterated

    def test_by_page_paging(self):

        def get_next(continuation_token=None):
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

        def extract_data(response):
            return response['nextLink'], iter(response['value'])

        pager = ItemPaged(get_next, extract_data).by_page()
        page1 = next(pager)
        assert list(page1) == ['value1.0', 'value1.1']

        page2 = next(pager)
        assert list(page2) == ['value2.0', 'value2.1']

        with pytest.raises(StopIteration):
            next(pager)

    def test_advance_paging(self):

        def get_next(continuation_token=None):
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

        def extract_data(response):
            return response['nextLink'], iter(response['value'])

        pager = ItemPaged(get_next, extract_data)
        page1 = next(pager)
        assert page1 == 'value1.0'
        page1 = next(pager)
        assert page1 == 'value1.1'

        page2 = next(pager)
        assert page2 == 'value2.0'
        page2 = next(pager)
        assert page2 == 'value2.1'

        with pytest.raises(StopIteration):
            next(pager)

    def test_none_value(self):
        def get_next(continuation_token=None):
            return {
                'nextLink': None,
                'value': None
            }
        def extract_data(response):
            return response['nextLink'], iter(response['value'] or [])

        pager = ItemPaged(get_next, extract_data)
        result_iterated = list(pager)
        assert len(result_iterated) == 0

    def test_print(self):
        def get_next(continuation_token=None):
            return {
                'nextLink': None,
                'value': None
            }
        def extract_data(response):
            return response['nextLink'], iter(response['value'] or [])

        pager = ItemPaged(get_next, extract_data)
        output = repr(pager)
        assert output.startswith('<iterator object azure.core.paging.ItemPaged at')

    def test_paging_continue_on_error(self):
        def get_next(continuation_token=None):
            if not continuation_token:
                return {
                    'nextLink': 'foo',
                    'value': ['bar']
                }
            else:
                raise HttpResponseError()
        def extract_data(response):
            return response['nextLink'], iter(response['value'] or [])
        
        pager = ItemPaged(get_next, extract_data)
        assert next(pager) == 'bar'
        with pytest.raises(HttpResponseError) as err:
            next(pager)
        assert err.value.continuation_token == 'foo'
