# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING  # pylint: disable=unused-import

if TYPE_CHECKING:
    from ._generated.operations import CallRecordingOperations

class CallRecording(object):
    def __init__(
            self,
            call_recording_client,  # type: CallRecordingOperations
        ): # type: (...) -> None

        self._call_recording_client = call_recording_client