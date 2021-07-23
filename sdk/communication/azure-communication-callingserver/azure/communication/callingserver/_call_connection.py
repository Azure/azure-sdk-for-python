# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any

from azure.core.tracing.decorator import distributed_trace

from ._generated.aio.operations import CallConnectionsOperations


class CallConnection(object):
    def __init__(
        self,
        call_connection_id: str,  # type: str
        call_connection_client: CallConnectionsOperations,  # type: AsyncTokenCredential
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        self.call_connection_id = call_connection_id
        self.call_connection_client = call_connection_client

    @distributed_trace()
    def hang_up(
        self,
        **kwargs: Any
    ):
        # type: (...) -> None

        return self.call_connection_client.hangup_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    def close(self):
        # type: () -> None
        self.call_connection_client.close()

    def __enter__(self):
        # type: () -> CallConnection
        self.call_connection_client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self.call_connection_client.__exit__(*args)  # pylint:disable=no-member
