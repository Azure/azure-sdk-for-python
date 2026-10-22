# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any, Dict, List, Optional, Union

from ..job_resource_configuration import JobResourceConfiguration
from .parallel_task import ParallelTask
from .retry_settings import RetrySettings

module_logger = logging.getLogger(__name__)


class ParameterizedParallel:
    """Parallel component that contains the traning parallel and supporting parameters for the parallel.

    :param retry_settings: parallel component run failed retry
    :type retry_settings: BatchRetrySettings
    :param logging_level: A string of the logging level name
    :type logging_level: str
    :param max_concurrency_per_instance: The max parallellism that each compute instance has.
    :type max_concurrency_per_instance: int
    :param error_threshold: The number of item processing failures should be ignored.
    :type error_threshold: int
    :param mini_batch_error_threshold: The number of mini batch processing failures should be ignored.
    :type mini_batch_error_threshold: int
    :param task: The parallel task.
    :type task: ParallelTask
    :param mini_batch_size: The mini batch size.
    :type mini_batch_size: str
    :param input_data: The input data.
    :type input_data: str
    :param resources: Compute Resource configuration for the job.
    :type resources: Union[Dict, ~azure.ai.ml.entities.JobResourceConfiguration]
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        retry_settings: Optional[RetrySettings] = None,
        logging_level: Optional[str] = None,
        max_concurrency_per_instance: Optional[int] = None,
        error_threshold: Optional[int] = None,
        mini_batch_error_threshold: Optional[int] = None,
        input_data: Optional[str] = None,
        task: Optional[ParallelTask] = None,
        mini_batch_size: Optional[int] = None,
        partition_keys: Optional[List] = None,
        resources: Optional[Union[dict, JobResourceConfiguration]] = None,
        environment_variables: Optional[Dict] = None,
    ):
        self.mini_batch_size = mini_batch_size
        self.partition_keys = partition_keys
        self.task = task
        self.retry_settings = retry_settings
        self.input_data = input_data
        self.logging_level = logging_level
        self.max_concurrency_per_instance = max_concurrency_per_instance
        self.error_threshold = error_threshold
        self.mini_batch_error_threshold = mini_batch_error_threshold
        self.resources = resources
        self.environment_variables = dict(environment_variables) if environment_variables else {}

    @property
    def task(self) -> Optional[ParallelTask]:
        res: Optional[ParallelTask] = self._task
        return res

    @task.setter
    def task(self, value: Any) -> None:
        if isinstance(value, dict):
            value = ParallelTask(**value)
        self._task = value

    @property
    def resources(self) -> Optional[Union[dict, JobResourceConfiguration]]:
        res: Optional[Union[dict, JobResourceConfiguration]] = self._resources
        return res

    @resources.setter
    def resources(self, value: Any) -> None:
        if isinstance(value, dict):
            value = JobResourceConfiguration(**value)
        self._resources = value

    @property
    def retry_settings(self) -> Optional[RetrySettings]:
        res: Optional[RetrySettings] = self._retry_settings
        return res

    @retry_settings.setter
    def retry_settings(self, value: Any) -> None:
        if isinstance(value, dict):
            value = RetrySettings(**value)
        self._retry_settings = value
