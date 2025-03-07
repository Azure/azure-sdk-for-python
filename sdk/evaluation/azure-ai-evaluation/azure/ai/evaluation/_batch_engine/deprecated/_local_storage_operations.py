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

from ._run import Run
from .._result import BatchResult, TokenMetrics, BatchStatus


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


class LocalStorageOperations(AbstractRunStorage):
    # The original code created a directory structure to store files in. Most of the files
    # and directory structures crearted were empty, or not relevant. For now, bring this in
    # as a stub. In the future, this will be replaced by a single file that contains all
    # the relevant information.

    def __init__(self, run: Run, **kwargs: Any):
        self._run = run
        self._logger = LoggerOperations(run.name, **kwargs)

    @property
    def logger(self) -> AbstractRunLogger:
        return self._logger

    def persist_result(self, result: Optional[BatchResult]):
        raise NotImplementedError("Not implemented")

    def load_exception(self) -> Mapping[str, Any]:
        raise NotImplementedError("Not implemented")

    def load_inputs_and_outputs(self) -> Tuple[Mapping[str, Any], BatchResult]:
        raise NotImplementedError("Not implemented")

    def load_metrics(self) -> Mapping[str, Union[int, float, str]]:
        raise NotImplementedError("Not implemented")


class LoggerOperations(AbstractRunLogger):
    # Original code logged to a file within a certain directory structure. For now, bring this in
    # as a stub. In the future, this will be replaced by code that logs to a single file.

    def __init__(self, run_name: str, **kwargs: Any):
        self._evaluation_dir = Path.home() / EVAL_USER_SUBFOLDER
        self._file_path = self._evaluation_dir / f"{run_name}.log"

    @property
    def file_path(self) -> Path:
        return self._file_path

    def __enter__(self) -> None:
        self._evaluation_dir.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)
        pass

    def __exit__(self, *args) -> None:
        pass

    def get_logs(self) -> str:
        """Get the logs of the run.

        :return: The logs of the run.
        :rtype: str
        """
        raise NotImplementedError("Not implemented")
