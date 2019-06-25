# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import time

from devtools_testutils import AzureMgmtTestCase


class KeyVaultTestCase(AzureMgmtTestCase):
    def setUp(self):
        self.list_test_size = 7
        super(KeyVaultTestCase, self).setUp()

    def tearDown(self):
        super(KeyVaultTestCase, self).tearDown()

    def _poll_until_no_exception(self, fn, expected_exception, max_retries=20, retry_delay=3):
        """polling helper for live tests because some operations take an unpredictable amount of time to complete"""

        for i in range(max_retries):
            try:
                return fn()
            except expected_exception:
                if i == max_retries - 1:
                    raise
                if self.is_live:
                    time.sleep(retry_delay)

    def _poll_until_exception(self, fn, expected_exception, max_retries=20, retry_delay=3):
        """polling helper for live tests because some operations take an unpredictable amount of time to complete"""

        for _ in range(max_retries):
            try:
                fn()
                if self.is_live:
                    time.sleep(retry_delay)
            except expected_exception:
                return

        self.fail("expected exception {expected_exception} was not raised")
