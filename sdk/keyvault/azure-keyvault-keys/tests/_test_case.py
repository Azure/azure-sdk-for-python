# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from _test_case_base import KeysTestCaseBase
from _shared.test_case import KeyVaultTestCase


class KeysTestCase(KeysTestCaseBase, KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        super(KeysTestCase, self).__init__(*args, **kwargs)
