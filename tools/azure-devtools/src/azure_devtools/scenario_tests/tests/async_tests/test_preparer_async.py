# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import asyncio
from azure_devtools.scenario_tests.preparers import AbstractPreparer

traces = []

# Separated into its own file to not disrupt 2.7 code with syntax errors from the use of async.
class _TestPreparer(AbstractPreparer):
    def __init__(self, name, use_cache=False):
        super(_TestPreparer, self).__init__("test", 20)
        self._name = name
        self.set_cache(use_cache, name)

    def create_resource(self, name, **kwargs):
        traces.append("create " + self._name)
        return {}

    def remove_resource(self, name, **kwargs):
        traces.append("remove " + self._name)


class _AsyncTestClassSample(unittest.TestCase):
    @_TestPreparer("A")
    @_TestPreparer("B")
    async def example_async_test(self):
        traces.append("ran async")

    @_TestPreparer("A")
    @_TestPreparer("B")
    def example_test(self):
        traces.append("ran sync")


def test_preparer_async_handling():
    # Mimic a real test runner, for better compat 2.7 / 3.x
    # This test won't work for 2.7, however, because it relies on asyncio.

    suite = unittest.TestSuite()
    suite.addTest(_AsyncTestClassSample("example_test"))
    suite.addTest(_AsyncTestClassSample("example_async_test"))
    unittest.TextTestRunner().run(suite)

    assert len(traces) == 10
    assert traces == [
        "create A",
        "create B",
        "ran sync",
        "remove B",
        "remove A",
        "create A",
        "create B",
        "ran async",
        "remove B",
        "remove A",
    ]
