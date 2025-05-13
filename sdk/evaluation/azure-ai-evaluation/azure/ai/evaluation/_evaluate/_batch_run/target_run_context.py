# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import types
from typing import Optional, Type

from azure.ai.evaluation._evaluate._batch_run.batch_clients import BatchClient
from azure.ai.evaluation._evaluate._batch_run import RunSubmitterClient
from azure.ai.evaluation._legacy._adapters._constants import PF_FLOW_ENTRY_IN_TMP
from azure.ai.evaluation._legacy._batch_engine._openai_injector import (
    inject_openai_api as ported_inject_openai_api,
    recover_openai_api as ported_recover_openai_api,
)
from azure.ai.evaluation._constants import PF_DISABLE_TRACING
from azure.ai.evaluation._evaluate._utils import set_event_loop_policy


class TargetRunContext:
    """Context manager for target batch run.

    :param upload_snapshot: Whether to upload target snapshot.
    :type upload_snapshot: bool
    """

    def __init__(self, client: BatchClient, upload_snapshot: bool = False) -> None:
        self._client = client
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

        if isinstance(self._client, RunSubmitterClient):
            ported_inject_openai_api()
            # For addressing the issue of asyncio event loop closed on Windows
            set_event_loop_policy()

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

        if isinstance(self._client, RunSubmitterClient):
            ported_recover_openai_api()
