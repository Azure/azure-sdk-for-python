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
        self.plain_text = b"5063e6aaa845f150200547944fd199679c98ed6f99da0a0b2dafeaf1f4684496fd532c1c229968cb9dee44957fcef7ccef59ceda0b362e56bcd78fd3faee5781c623c0bb22b35beabde0664fd30e0e824aba3dd1b0afffc4a3d955ede20cf6a854d52cfd"
        super(KeyVaultTestCase, self).setUp()

    def tearDown(self):
        super(KeyVaultTestCase, self).tearDown()
