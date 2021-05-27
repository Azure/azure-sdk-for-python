# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure_devtools.scenario_tests.preparers import AbstractPreparer

traces = []


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


class _TestClassSample(unittest.TestCase):
    @_TestPreparer("A")
    @_TestPreparer("B")
    def example_test(self):
        pass


class _CachedTestClassSample(unittest.TestCase):
    @_TestPreparer("A", True)
    @_TestPreparer("B", True)
    def example_test(self):
        pass

    @_TestPreparer("A", True)
    @_TestPreparer("C", True)
    def example_test_2(self):
        pass

    @_TestPreparer("A", True)
    @_TestPreparer("C", False)
    def example_test_3(self):
        pass

    @_TestPreparer("A", True)
    @_TestPreparer("C", False)
    def fail_test(self):
        raise Exception("Intentional failure to test cache.")

    @_TestPreparer("PARENT", True)
    @_TestPreparer("A", True)
    @_TestPreparer("C", True)
    def parent_cache_test(self):
        pass


def test_preparer_order():
    # Mimic a real test runner, for better compat 2.7 / 3.x
    suite = unittest.TestSuite()
    suite.addTest(_TestClassSample("example_test"))
    unittest.TextTestRunner().run(suite)

    assert len(traces) == 4
    assert traces[0] == "create A"
    assert traces[1] == "create B"
    assert traces[2] == "remove B"
    assert traces[3] == "remove A"


def test_cached_preparer_order():
    # Mimic a real test runner, for better compat 2.7 / 3.x
    suite = unittest.TestSuite()
    suite.addTest(_CachedTestClassSample("example_test"))
    suite.addTest(_CachedTestClassSample("example_test_2"))
    suite.addTest(_CachedTestClassSample("example_test_3"))
    unittest.TextTestRunner().run(suite)

    assert len(traces) == 5
    assert traces[0] == "create A"
    assert traces[1] == "create B"
    assert traces[2] == "create C"
    assert traces[3] == "create C"
    assert traces[4] == "remove C"  # One of the C's is cached, one is not.

    # Note: unit test runner doesn't trigger the pytest session fixture that deletes resources when all tests are done.
    # let's run that manually now to test it.
    AbstractPreparer._perform_pending_deletes()

    assert len(traces) == 8
    # we're technically relying on an implementation detail (for earlier versions of python
    # dicts did not guarantee ordering by insertion order, later versions do)
    # to order removal by relying on dict ordering.
    assert traces[5] == "remove C"
    assert traces[6] == "remove B"
    assert traces[7] == "remove A"


def test_cached_preparer_failure():
    # Mimic a real test runner, for better compat 2.7 / 3.x
    suite = unittest.TestSuite()
    suite.addTest(_CachedTestClassSample("fail_test"))
    suite.addTest(_CachedTestClassSample("example_test"))
    suite.addTest(_CachedTestClassSample("example_test_2"))
    suite.addTest(_CachedTestClassSample("example_test_3"))
    unittest.TextTestRunner().run(suite)
    AbstractPreparer._perform_pending_deletes()
    # the key here is that the cached A and noncached C is used even though the test failed, and successfully removed later.
    assert traces == [
        "create A",
        "create C",
        "remove C",
        "create B",
        "create C",
        "create C",
        "remove C",
        "remove C",
        "remove B",
        "remove A",
    ]


def test_cached_preparer_parent_cache_keying():
    # Mimic a real test runner, for better compat 2.7 / 3.x
    suite = unittest.TestSuite()
    suite.addTest(_CachedTestClassSample("example_test_2"))
    suite.addTest(_CachedTestClassSample("example_test_3"))
    suite.addTest(_CachedTestClassSample("parent_cache_test"))
    unittest.TextTestRunner().run(suite)
    AbstractPreparer._perform_pending_deletes()
    # The key here is to observe that changing a parent preparer means the child preparers can't utilize a cache from a cache-stack not including that parent.
    assert traces == [
        "create A",
        "create C",
        "create C",
        "remove C",
        "create PARENT",
        "create A",
        "create C",
        "remove C",
        "remove A",
        "remove PARENT",
        "remove C",
        "remove A",
    ]
