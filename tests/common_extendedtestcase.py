#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import sys
import unittest
from contextlib import contextmanager


class ExtendedTestCase(unittest.TestCase):
    '''Backport some asserts to Python 2.6 and earlier.'''

    def assertNamedItemInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                return

        standardMsg = '{0} not found in {1}'.format(
            repr(item_name), repr(container))
        self.fail(self._formatMessage(msg, standardMsg))

    def assertNamedItemNotInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                standardMsg = '{0} unexpectedly found in {1}'.format(
                    repr(item_name), repr(container))
                self.fail(self._formatMessage(msg, standardMsg))

    if sys.version_info < (2,7):
        def assertIsNone(self, obj):
            self.assertEqual(obj, None)

        def assertIsNotNone(self, obj):
            self.assertNotEqual(obj, None)

        def assertIsInstance(self, obj, type):
            self.assertTrue(isinstance(obj, type))

        def assertGreater(self, a, b):
            self.assertTrue(a > b)

        def assertGreaterEqual(self, a, b):
            self.assertTrue(a >= b)

        def assertLess(self, a, b):
            self.assertTrue(a < b)

        def assertLessEqual(self, a, b):
            self.assertTrue(a <= b)

        def assertIn(self, member, container):
            if member not in container:
                self.fail('{0} not found in {1}.'.format(
                    safe_repr(member), safe_repr(container)))

        @contextmanager
        def _assertRaisesContextManager(self, excClass):
            try:
                yield
                self.fail('{0} was not raised'.format(safe_repr(excClass)))
            except excClass:
                pass

        def assertRaises(self, excClass, callableObj=None, *args, **kwargs):
            if callableObj:
                super(ExtendedTestCase, self).assertRaises(
                    excClass,
                    callableObj,
                    *args,
                    **kwargs
                )
            else:
                return self._assertRaisesContextManager(excClass)
