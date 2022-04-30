# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio


from _shared.asynctestcase import AsyncCommunicationTestCase
from _shared.testcase import (
    BodyReplacerProcessor,
    ResponseReplacerProcessor
)
from azure_devtools.scenario_tests import LargeResponseBodyReplacer
from _recording_processors import (
    RouterHeaderSanitizer,
    RouterQuerySanitizer,
    RouterURIIdentityReplacer
)


class RouterTestAsyncCase(AsyncCommunicationTestCase):
    def setUp(self):
        super(RouterTestAsyncCase, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(keys = ["id"]),
            LargeResponseBodyReplacer(),
            ResponseReplacerProcessor(keys = [self._resource_name]),
            RouterHeaderSanitizer(headers = ["etag"]),
            RouterQuerySanitizer(exceptions = ["api-version"]),
            RouterURIIdentityReplacer()
        ])
