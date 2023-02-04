# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Any  # pylint: disable=unused-import

if TYPE_CHECKING:
    from ._generated.operations import CallConnectionOperations, CallMediaOperations

from ._call_media import CallMedia

class CallConnection(object):
    def __init__(
            self,
            call_connection_id,  # type: str
            call_connection_client,  # type: CallConnectionOperations
            call_media_client,  # type: CallMediaOperations
        ): # type: (...) -> None

        self.call_connection_id = call_connection_id
        self._call_connection_client = call_connection_client
        self._call_media_client = call_media_client

    def get_call_media(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> CallMedia

        return CallMedia(
            self.call_connection_id,
            self._call_media_client,
            **kwargs
            )
