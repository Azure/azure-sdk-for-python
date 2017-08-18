# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import unittest

try:
    import mock
except ImportError:
    from unittest import mock


from azure_devtools.scenario_tests.const import ENV_LIVE_TEST
from azure_devtools.scenario_tests.config import TestConfig


class TestScenarioConfig(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as cfgfile:
            cfgfile.write('live-mode: yes')
            self.cfgfile = cfgfile.name

    def tearDown(self):
        os.remove(self.cfgfile)

    def test_env_var(self):
        with mock.patch.dict('os.environ', {ENV_LIVE_TEST: 'yes'}):
            config = TestConfig()
        self.assertTrue(config.record_mode)

    def test_config_file(self):
        config = TestConfig(config_file=self.cfgfile)
        self.assertTrue(config.record_mode)
