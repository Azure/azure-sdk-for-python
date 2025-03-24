# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from uuid import uuid4
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Mapping, Optional, Sequence

from ._utils import normalize_identifier_name
from ._result import BatchResult
from ._status import BatchStatus


class RunStatus(Enum):
    # TODO ralphe: Trim this to just the statuses we need
    # QUEUED = "Queued"
    NOT_STARTED = "NotStarted"
    PREPARING = "Preparing"
    # PROVISIONING = "Provisioning"
    # STARTING = "Starting"
    RUNNING = "Running"
    # CANCEL_REQUESTED = "CancelRequested"
    CANCELED = "Canceled"
    # FINALIZING = "Finalizing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    # UNAPPROVED = "Unapproved"
    # NOTRESPONDING = "NotResponding"
    # PAUSING = "Pausing"
    # PAUSED = "Paused"

    @staticmethod
    def from_batch_result_status(status: BatchStatus) -> "RunStatus":
        if status == BatchStatus.NotStarted:
            return RunStatus.NOT_STARTED
        if status == BatchStatus.Running:
            return RunStatus.RUNNING
        if status == BatchStatus.Completed:
            return RunStatus.COMPLETED
        if status == BatchStatus.Canceled:
            return RunStatus.CANCELED
        if status == BatchStatus.Failed:
            return RunStatus.FAILED

        return RunStatus.FAILED


class Run:
    """The equivalent of a Promptflow Run
    promptflow-devkit/promptflow/_sdk/entities/_run.py

    THIS WILL BE REMOVED IN A FUTURE CODE UPDATE"""

    def __init__(
        self,
        *,
        dynamic_callable: Callable,
        name_prefix: Optional[str],
        inputs: Sequence[Mapping[str, Any]],
        column_mapping: Mapping[str, str],
        created_on: Optional[datetime] = None,
    ):
        self._status: RunStatus = RunStatus.NOT_STARTED
        self._created_on = created_on or datetime.now(timezone.utc)
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None

        self.dynamic_callable = dynamic_callable
        self.name = self._generate_run_name(name_prefix, self._created_on)
        self.inputs = inputs
        self.column_mapping = column_mapping
        self.result: Optional[BatchResult] = None
        self.metrics: Mapping[str, Any] = {}

        # self._use_remote_flow = False
        # self._from_flex_flow = True
        # self._from_prompty = False
        # self.flow = path to pointless flow file
        # self._experiment_name = name of folder containing pointless flow file
        # self._lineage_id = basically equivalent to a hex digest of the SHA256 hash of:
        #                    f"{uuid.getnod()}/{posix_full_path_to_pointless_folder}"
        # self._output_path = Path("<user_folder>/.promptflow/runs/<self.name>")
        # self._flow_name = name of pointless folder

    @property
    def status(self) -> RunStatus:
        return self._status

    @property
    def created_on(self) -> datetime:
        return self._created_on

    @property
    def duration(self) -> Optional[timedelta]:
        if self._start_time is None or self._end_time is None:
            return None

        return self._end_time - self._start_time

    @property
    def outputs(self) -> Sequence[Mapping[str, Any]]:
        if self.result is None:
            return []

        return [value or {} for value in self.result.results]

    @staticmethod
    def _generate_run_name(name_prefix: Optional[str], creation_time: datetime) -> str:
        # The Promptflow code looked at the folder name  of the temporary folder used to
        # store the temporary flow YAML file which was a single entry that told it look
        # at the passed in dynamic_callable. Example folder name:
        # azure_ai_evaluation_evaluators_common_base_eval_asyncevaluatorbase_l82059h3
        # instead we will use the passed in name_prefix or use a UUID (which is equally
        # opaque as what the original code did)
        if not name_prefix:
            name_prefix = str(uuid4())

        timestamp = creation_time.strftime("%Y%m%d_%H%M%S_%f")
        name = f"{name_prefix}_{timestamp}"
        return normalize_identifier_name(name)
