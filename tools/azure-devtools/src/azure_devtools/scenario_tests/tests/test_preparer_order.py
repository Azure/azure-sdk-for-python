# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure_devtools.scenario_tests.preparers import AbstractPreparer

traces = []


class _TestPreparer(AbstractPreparer):
    def __init__(self, name):
        super(_TestPreparer, self).__init__('test', 20)
        self._name = name

    def create_resource(self, name, **kwargs):
        traces.append('create ' + self._name)
        return {}

    def remove_resource(self, name, **kwargs):
        traces.append('remove ' + self._name)


class _TestClassSample(unittest.TestCase):
    @_TestPreparer('A')
    @_TestPreparer('B')
    def example_test(self):
        pass


def test_preparer_order():
    # Mimic a real test runner, for better compat 2.7 / 3.x
    suite = unittest.TestSuite()
    suite.addTest(_TestClassSample('example_test'))
    unittest.TextTestRunner().run(suite)

    assert len(traces) == 4
    assert traces[0] == 'create A'
    assert traces[1] == 'create B'
    assert traces[2] == 'remove B'
    assert traces[3] == 'remove A'
