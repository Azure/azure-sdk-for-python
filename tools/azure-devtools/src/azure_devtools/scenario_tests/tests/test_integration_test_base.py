# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests.base import IntegrationTestBase, LiveTest


class TestIntegrationTestBase(unittest.TestCase):
    def test_integration_test_default_constructor(self):
        class MockTest(IntegrationTestBase):
            def __init__(self):
                super(MockTest, self).__init__('sample_test')

            def sample_test(self):
                pass

        tb = MockTest()

        random_name = tb.create_random_name('example', 90)
        self.assertEqual(len(random_name), 90)
        self.assertTrue(random_name.startswith('example'))

        random_file = tb.create_temp_file(size_kb=16, full_random=False)
        self.addCleanup(lambda: os.remove(random_file))
        self.assertTrue(os.path.isfile(random_file))
        self.assertEqual(os.path.getsize(random_file), 16 * 1024)
        self.assertEqual(len(tb._cleanups), 1)  # pylint: disable=protected-access
        with open(random_file, 'rb') as fq:
            # the file is blank
            self.assertFalse(any(b for b in fq.read(16 * 1024) if b != '\x00'))

        random_file_2 = tb.create_temp_file(size_kb=8, full_random=True)
        self.addCleanup(lambda: os.remove(random_file_2))
        self.assertTrue(os.path.isfile(random_file_2))
        self.assertEqual(os.path.getsize(random_file_2), 8 * 1024)
        self.assertEqual(len(tb._cleanups), 2)  # pylint: disable=protected-access
        with open(random_file_2, 'rb') as fq:
            # the file is blank
            self.assertTrue(any(b for b in fq.read(8 * 1024) if b != '\x00'))

        random_dir = tb.create_temp_dir()
        self.addCleanup(lambda: os.rmdir(random_dir))
        self.assertTrue(os.path.isdir(random_dir))
        self.assertEqual(len(tb._cleanups), 3)  # pylint: disable=protected-access

    def test_live_test_default_constructor(self):
        class MockTest(LiveTest):
            def __init__(self):
                super(MockTest, self).__init__('sample_test')

            def sample_test(self):
                pass

        self.assertIsNone(MockTest().run(), 'The live test is not skipped as expected')
