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

import unittest

from azure.core.paging import Paged

from msrest.serialization import Deserializer

class FakePaged(Paged):
    _attribute_map = {
        'next_link': {'key': 'nextLink', 'type': 'str'},
        'current_page': {'key': 'value', 'type': '[str]'}
    }

    def __init__(self, *args, **kwargs):
        super(FakePaged, self).__init__(*args, **kwargs)

_test_deserializer = Deserializer({})

class TestPaging(unittest.TestCase):

    def test_basic_paging(self):

        def internal_paging(next_link=None, raw=False):
            if not next_link:
                return {
                    'nextLink': 'page2',
                    'value': ['value1.0', 'value1.1']
                }
            else:
                return {
                    'nextLink': None,
                    'value': ['value2.0', 'value2.1']
                }

        deserialized = FakePaged(internal_paging, _test_deserializer)
        result_iterated = list(deserialized)
        self.assertListEqual(
            ['value1.0', 'value1.1', 'value2.0', 'value2.1'],
            result_iterated
        )

    def test_advance_paging(self):

        def internal_paging(next_link=None, raw=False):
            if not next_link:
                return {
                    'nextLink': 'page2',
                    'value': ['value1.0', 'value1.1']
                }
            else:
                return {
                    'nextLink': None,
                    'value': ['value2.0', 'value2.1']
                }

        deserialized = FakePaged(internal_paging, _test_deserializer)
        page1 = next(deserialized)
        assert page1 == 'value1.0'
        page1 = next(deserialized)
        assert page1 == 'value1.1'
     
        page2 = next(deserialized)
        assert page2 == 'value2.0'
        page2 = next(deserialized)
        assert page2 == 'value2.1'

        with self.assertRaises(StopIteration):
            next(deserialized)

    def test_none_value(self):
        def internal_paging(next_link=None, raw=False):
            return {
                'nextLink': None,
                'value': None
            }

        deserialized = FakePaged(internal_paging, _test_deserializer)
        result_iterated = list(deserialized)
        self.assertEqual(len(result_iterated), 0)
