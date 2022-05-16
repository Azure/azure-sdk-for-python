# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from abc import abstractmethod

from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor,
    ResponseReplacerProcessor
)
from azure_devtools.scenario_tests import LargeResponseBodyReplacer
from _recording_processors import (
    RouterHeaderSanitizer,
    RouterQuerySanitizer,
    RouterURIIdentityReplacer,
    RouterScrubber
)

from _shared.utils import get_http_logging_policy
from azure.communication.jobrouter import (
    RouterClient,
)


class RouterTestCaseBase(CommunicationTestCase):
    def __init__(self, method_name, *args, **kwargs):
        super(RouterTestCaseBase, self).__init__(method_name, *args, **kwargs)

    def setUp(self):
        super(RouterTestCaseBase, self).setUp()

        self.recording_processors.extend([
            BodyReplacerProcessor(keys = ["id",
                                          "distributionPolicyId",
                                          "exceptionPolicyId",
                                          "classificationPolicyId",
                                          "queueId",
                                          ]),
            LargeResponseBodyReplacer(),
            ResponseReplacerProcessor(keys = [self._resource_name]),
            RouterScrubber(keys = ["Id",
                                   "etag",
                                   "id",
                                   "distributionPolicyId",
                                   "exceptionPolicyId",
                                   "classificationPolicyId",
                                   "fallbackQueueId",
                                   "queueId",
                                   "workerId"]),
            RouterHeaderSanitizer(headers = ["etag"]),
            RouterQuerySanitizer(exceptions = ["api-version"]),
            RouterURIIdentityReplacer(),
        ])


class RouterTestCase(RouterTestCaseBase):
    def setUp(self):
        super(RouterTestCase, self).setUp()

    @abstractmethod
    def clean_up(self):
        pass

    def tearDown(self):
        super(RouterTestCase, self).tearDown()
        self.clean_up()

    def create_client(self) -> RouterClient:
        return RouterClient.from_connection_string(
            conn_str = self.connection_str,
            http_logging_policy=get_http_logging_policy())

    def _poll_until_no_exception(self, fn, expected_exception, *args, **kwargs):
        """polling helper for live tests because some operations take an unpredictable amount of time to complete"""
        max_retries = kwargs.pop('max_retries', 20)
        retry_delay = kwargs.pop('retry_delay', 3)

        for i in range(max_retries):
            try:
                return fn(*args, **kwargs)
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
