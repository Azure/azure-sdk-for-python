# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure_devtools.scenario_tests import GeneralNameReplacer
from devtools_testutils import AzureMgmtTestCase


class KeyVaultTestCase(AzureMgmtTestCase):
    def setUp(self):
        self.list_test_size = 7
        super(KeyVaultTestCase, self).setUp()

    def tearDown(self):
        super(KeyVaultTestCase, self).tearDown()
