# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest

import pytest

import azure.cosmos._base as base


@pytest.mark.cosmosEmulator
class TestIdAndNameBased(unittest.TestCase):
    def test_is_name_based(self):
        self.assertFalse(base.IsNameBased("dbs/xjwmAA==/"))

        # This is a database name that ran into 'Incorrect padding'
        # exception within base.IsNameBased function
        self.assertTrue(base.IsNameBased("dbs/paas_cmr"))
