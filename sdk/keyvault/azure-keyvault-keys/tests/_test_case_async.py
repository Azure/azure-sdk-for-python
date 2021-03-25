# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from _test_case_base import KeysTestCaseBase
from _shared.test_case_async import KeyVaultTestCase


class KeysTestCase(KeysTestCaseBase, KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
