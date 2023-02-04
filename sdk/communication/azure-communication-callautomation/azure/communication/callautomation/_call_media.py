# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING  # pylint: disable=unused-import

if TYPE_CHECKING:
    from ._generated.operations import CallMediaOperations

class CallMedia(object):
    def __init__(
            self,
            call_connection_id,  # type: str
            call_media_client,  # type: CallMediaOperations
        ): # type: (...) -> None

        self.call_connection_id = call_connection_id
        self._call_media_client = call_media_client