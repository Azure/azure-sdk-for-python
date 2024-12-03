# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import types
from typing import Optional, Type

from promptflow._sdk._constants import PF_FLOW_ENTRY_IN_TMP
from azure.ai.evaluation._constants import PF_DISABLE_TRACING


class TargetRunContext:
    """Context manager for target batch run.

    :param upload_snapshot: Whether to upload target snapshot.
    :type upload_snapshot: bool
    """

    def __init__(self, upload_snapshot: bool = False) -> None:
        self._upload_snapshot = upload_snapshot
        self._original_cwd = os.getcwd()

    def __enter__(self) -> None:
        # Preserve current working directory, as PF may change it without restoring it afterward
        self._original_cwd = os.getcwd()

        # Address "[WinError 32] The process cannot access the file" error,
        # caused by conflicts when the venv and target function are in the same directory.
        # Setting PF_FLOW_ENTRY_IN_TMP to true uploads only the flex entry file (flow.flex.yaml).
        if not self._upload_snapshot:
            os.environ[PF_FLOW_ENTRY_IN_TMP] = "true"

        os.environ[PF_DISABLE_TRACING] = "true"

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[types.TracebackType],
    ) -> None:
        os.chdir(self._original_cwd)

        if not self._upload_snapshot:
            os.environ.pop(PF_FLOW_ENTRY_IN_TMP, None)

        os.environ.pop(PF_DISABLE_TRACING, None)
