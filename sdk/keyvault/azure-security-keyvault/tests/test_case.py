# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureMgmtTestCase

from auth_request_filter import OAuthv2RequestResponsesFilter


class KeyVaultTestCase(AzureMgmtTestCase):
    def __init__(self, *args, **kwargs):
        super(KeyVaultTestCase, self).__init__(*args, **kwargs)
        # workaround for upstream issue https://github.com/Azure/azure-python-devtools/pull/57
        self.recording_processors.append(OAuthv2RequestResponsesFilter())

    def setUp(self):
        self.list_test_size = 7
        super(KeyVaultTestCase, self).setUp()

    def tearDown(self):
        super(KeyVaultTestCase, self).tearDown()
