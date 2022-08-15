# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Dict, Union

from azure.ai.ml._schema.job.loadable_mixin import LoadableMixin

from ..resource_configuration import ResourceConfiguration
from .parallel_task import ParallelTask
from .retry_settings import RetrySettings

module_logger = logging.getLogger(__name__)


class ParameterizedParallel(LoadableMixin):
    """Parallel component that contains the traning parallel and supporting
    parameters for the parallel.

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
    :type resources: Union[Dict, ~azure.ai.ml.entities.ResourceConfiguration]
    """

    def __init__(
        self,
        retry_settings: RetrySettings = None,
        logging_level: str = None,
        max_concurrency_per_instance: int = None,
        error_threshold: int = None,
        mini_batch_error_threshold: int = None,
        input_data: str = None,
        task: ParallelTask = None,
        mini_batch_size: int = None,
        resources: Union[dict, ResourceConfiguration] = None,
        environment_variables: Dict = None,
    ):
        self.mini_batch_size = mini_batch_size
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
    def task(self) -> ParallelTask:
        return self._task

    @task.setter
    def task(self, value):
        if isinstance(value, dict):
            value = ParallelTask(**value)
        self._task = value

    @property
    def resources(self) -> ResourceConfiguration:
        return self._resources

    @resources.setter
    def resources(self, value):
        if isinstance(value, dict):
            value = ResourceConfiguration(**value)
        self._resources = value

    @property
    def retry_settings(self) -> RetrySettings:
        return self._retry_settings

    @retry_settings.setter
    def retry_settings(self, value):
        if isinstance(value, dict):
            value = RetrySettings(**value)
        self._retry_settings = value
