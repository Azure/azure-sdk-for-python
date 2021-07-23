# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any

from azure.core.tracing.decorator_async import distributed_trace_async

from .._generated.aio.operations import CallConnectionsOperations


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

    @distributed_trace_async()
    async def hang_up(
        self,
        **kwargs: Any
    ):
        # type: (...) -> None

        return await self.call_connection_client.hangup_call(
            call_connection_id=self.call_connection_id,
            **kwargs
        )

    async def close(self) -> None:
        await self.call_connection_client.close()

    async def __aenter__(self) -> "CallConnection":
        await self.call_connection_client.__aenter__()
        return self

    async def __aexit__(self, *args):
        # type: (*Any) -> None
        await self.call_connection_client.__aexit__(*args)
