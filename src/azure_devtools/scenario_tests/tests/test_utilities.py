# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure_devtools.scenario_tests.utilities import create_random_name


class TestUtilityFunctions(unittest.TestCase):
    def test_create_random_name_default_value(self):
        default_generated_name = create_random_name()
        self.assertTrue(default_generated_name.startswith('aztest'))
        self.assertEqual(24, len(default_generated_name))
        self.assertTrue(isinstance(default_generated_name, str))

    def test_create_random_name_randomness(self):
        self.assertEqual(100, len(set([create_random_name() for _ in range(100)])))

    def test_create_random_name_customization(self):
        customized_name = create_random_name(prefix='pauline', length=61)
        self.assertTrue(customized_name.startswith('pauline'))
        self.assertEqual(61, len(customized_name))
        self.assertTrue(isinstance(customized_name, str))

    def test_create_random_name_exception_long_prefix(self):
        prefix = 'prefix-too-long'

        with self.assertRaises(ValueError) as cm:
            create_random_name(prefix, length=len(prefix)-1)
        self.assertEqual(str(cm.exception), 'The length of the prefix must not be longer than random name length')

        self.assertTrue(create_random_name(prefix, length=len(prefix)+4).startswith(prefix))

    def test_create_random_name_exception_not_enough_space_for_randomness(self):
        prefix = 'prefix-too-long'

        for i in range(4):
            with self.assertRaises(ValueError) as cm:
                create_random_name(prefix, length=len(prefix) + i)
            self.assertEqual(str(cm.exception), 'The randomized part of the name is shorter than 4, which may not be '
                                                'able to offer enough randomness')


