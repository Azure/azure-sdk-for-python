# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from typing import Callable, Any

from devtools_testutils import is_live, is_live_and_not_recording, trim_kwargs_from_test_function
from azure.communication.messages._shared.utils import parse_connection_str


class MessagesPreparersAsync(object):

    @staticmethod
    def messages_test_decorator_async(func: Callable[[], object], **kwargs: Any):
        async def wrapper(self, *args, **kwargs):
            if is_live() or is_live_and_not_recording():
                self.connection_string = os.getenv("COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING")
                endpoint, _ = parse_connection_str(self.connection_string)
                self.resource_name = endpoint.split(".")[0]

            else:
                self.connection_string = (
                    "endpoint=https://sanitized.unitedstates.communication.azure.com/;accesskey=fake==="
                )
                self.resource_name = "sanitized"

            return await func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def messages_test_decorator_for_token_async(func: Callable[[], object], **kwargs: Any):
        async def wrapper(self, *args, **kwargs):
            breakpoint
            if is_live() or is_live_and_not_recording():
                self.endpoint_str = os.getenv("COMMUNICATION_LIVETEST_DYNAMIC_ENDPOINT")
            else:
                self.endpoint = "sanitized.unitedstates.communication.azure.com"

            return await func(self, *args, **kwargs)

        return wrapper
