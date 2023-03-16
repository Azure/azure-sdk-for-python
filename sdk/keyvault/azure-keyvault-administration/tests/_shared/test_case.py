# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time

from devtools_testutils import AzureRecordedTestCase

from azure.keyvault.administration._internal import HttpChallengeCache
from azure.keyvault.keys._shared import HttpChallengeCache as _HttpChallengeCache


class KeyVaultTestCase(AzureRecordedTestCase):
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

    def teardown_method(self, method):
        HttpChallengeCache.clear()
        _HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        assert len(_HttpChallengeCache._cache) == 0
