# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Mapping, Optional, Sequence

from ._status import BatchStatus


@dataclass
class TokenMetrics:
    """The token metrics of a run."""

    prompt_tokens: int
    """The number of tokens used in the prompt for the run."""
    completion_tokens: int
    """The number of tokens used in the completion for the run."""
    total_tokens: int
    """The total number of tokens used in the run."""


@dataclass
class BatchRunError:
    """The error of a batch run."""

    details: str
    """The details of the error."""
    exception: Optional[BaseException]
    """The exception of the error."""


@dataclass
class BatchRunDetails:
    """The error of a line in a batch run."""

    id: str
    """The ID of the line run."""
    status: BatchStatus
    """The status of the line run."""
    result: Optional[Mapping[str, Any]]
    """The result of the line run."""
    start_time: Optional[datetime]
    """The start time of the line run. If this was never started, this should be None."""
    end_time: Optional[datetime]
    """The end time of the line run. If this never completed, this should be None."""
    tokens: TokenMetrics
    """The token metrics of the line run."""
    error: Optional[BatchRunError]
    """The error of the line run. This will only be set if the status is Failed."""

    @property
    def duration(self) -> timedelta:
        """The duration of the line run."""
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time
        return timedelta(0)

    @staticmethod
    def create_id(run_id: str, index: int) -> str:
        """Helper method to create the ID for a line run."""
        return f"{run_id}_{index}"


@dataclass
class BatchResult:
    """The result of a batch run."""

    status: BatchStatus
    """The overall status of the batch run."""
    total_lines: int
    """The total number of lines in the batch run."""
    failed_lines: int
    """The number of failed lines in the batch run."""
    start_time: datetime
    """The start time of the batch run."""
    end_time: datetime
    """The end time of the batch run."""
    tokens: TokenMetrics
    """The overall token metrics of the batch run."""
    details: Sequence[BatchRunDetails]
    """The details of each line in the batch run."""
    error: Optional[Exception] = None
    """The error of the batch run. This will only be set if the status does not indicate success."""

    @property
    def duration(self) -> timedelta:
        """The duration of the batch run."""
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time
        return timedelta(0)

    @property
    def results(self) -> Sequence[Optional[Mapping[str, Any]]]:
        """The results of the batch run."""
        if not self.details:
            return []
        return [d.result for d in self.details]