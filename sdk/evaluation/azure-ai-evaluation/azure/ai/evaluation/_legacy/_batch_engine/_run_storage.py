# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Original source:
# promptflow-devkit/promptflow/_sdk/operations/_local_storage_operations.py

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final, Mapping, Optional, Tuple, Union

from ._result import BatchResult, TokenMetrics, BatchStatus


EVAL_USER_SUBFOLDER: Final[str] = ".evaluation"


class AbstractRunLogger(AbstractContextManager):
    @property
    @abstractmethod
    def file_path(self) -> Path:
        """Get the file path of the logger.

        :return: The file path of the logger.
        :rtype: Path
        """
        ...

    @abstractmethod
    def get_logs(self) -> str:
        """Get the logs of the run.

        :return: The logs of the run.
        :rtype: str
        """
        ...


class AbstractRunStorage(ABC):
    @property
    @abstractmethod
    def logger(self) -> "AbstractRunLogger":
        """Get the logger of the run.

        :return: The logger of the run.
        :rtype: ~promptflow.contracts.run_logger.RunLogger
        """
        ...

    @abstractmethod
    def persist_result(self, result: Optional[BatchResult]) -> None:
        """Persist results of a batch engine execution (including any errors).

        :param Optional[BatchResult] result: The result to persist.
        """
        ...

    @abstractmethod
    def load_exception(self) -> Mapping[str, Any]:
        """Load the exception from the storage. If there was no exception, an empty
        mapping will be returned.

        :return: The exception.
        :rtype: Optional[Exception]
        """
        ...

    @abstractmethod
    def load_inputs_and_outputs(self) -> Tuple[Mapping[str, Any], BatchResult]:
        """Load the inputs and outputs from the storage.

        :return: The inputs and outputs.
        :rtype: Tuple(Mapping[str, Any], BatchResult)
        """
        ...

    @abstractmethod
    def load_metrics(self) -> Mapping[str, Union[int, float, str]]:
        """Load the metrics from the storage.

        :return: The metrics.
        :rtype: Mapping[str, Union[int, float, str]]
        """
        ...


class NoOpRunStorage(AbstractRunStorage):
    """A no-op implementation of the run storage."""

    def __init__(self):
        self._logger = NoOpLogger()
        pass

    @property
    def logger(self) -> AbstractRunLogger:
        return self._logger

    def persist_result(self, result: Optional[BatchResult]) -> None:
        pass

    def load_exception(self) -> Mapping[str, Any]:
        return {}

    def load_inputs_and_outputs(self) -> Tuple[Mapping[str, Any], BatchResult]:
        now = datetime.now(timezone.utc)
        return {}, BatchResult(BatchStatus.NotStarted, 0, 0, now, now, TokenMetrics(0, 0, 0), [])

    def load_metrics(self) -> Mapping[str, Union[int, float, str]]:
        return {}


class NoOpLogger(AbstractRunLogger):
    """A no-op implementation of the run logger."""

    @property
    def file_path(self) -> Path:
        return Path.home() / EVAL_USER_SUBFOLDER

    def __enter__(self) -> None:
        pass

    def __exit__(self, *args) -> None:
        pass

    def get_logs(self) -> str:
        return ""
