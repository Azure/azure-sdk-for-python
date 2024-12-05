# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import types
from typing import Optional, Type

from promptflow._sdk._constants import PF_FLOW_ENTRY_IN_TMP


class TargetRunContext:
    """Context manager for target batch run.

    :param upload_snapshot: Whether to upload target snapshot.
    :type upload_snapshot: bool
    """

    def __init__(self, upload_snapshot: bool) -> None:
        self._upload_snapshot = upload_snapshot

    def __enter__(self) -> None:
        # Address "[WinError 32] The process cannot access the file" error,
        # caused by conflicts when the venv and target function are in the same directory.
        # Setting PF_FLOW_ENTRY_IN_TMP to true uploads only the flex entry file (flow.flex.yaml).
        if not self._upload_snapshot:
            os.environ[PF_FLOW_ENTRY_IN_TMP] = "true"

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[types.TracebackType],
    ) -> None:
        if not self._upload_snapshot:
            os.environ.pop(PF_FLOW_ENTRY_IN_TMP, None)
