# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import List, Union

from marshmallow import Schema

from ..._schema import PathAwareSchema
from ...entities import BatchRetrySettings
from .._schema.component import NodeType
from ..entities import Command


class Parallel(Command):
    """Node of scope components in pipeline with specific run settings."""

    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(Parallel, self).__init__(type=NodeType.PARALLEL, **kwargs)
        self._init = True
        self._max_concurrency_per_instance = kwargs.pop("max_concurrency_per_instance", None)
        self._error_threshold = kwargs.pop("error_threshold", None)
        self._mini_batch_size = kwargs.pop("mini_batch_size", None)
        self._partition_keys = kwargs.pop("partition_keys", None)
        self._logging_level = kwargs.pop("logging_level", None)
        self._retry_settings = kwargs.pop("retry_settings", BatchRetrySettings())
        self._init = False

    @property
    def max_concurrency_per_instance(self) -> int:
        """The max parallellism that each compute instance has.

        :return: The max concurrence per compute instance
        :rtype: int
        """
        return self._max_concurrency_per_instance

    @max_concurrency_per_instance.setter
    def max_concurrency_per_instance(self, value: int):
        self._max_concurrency_per_instance = value

    @property
    def error_threshold(self) -> int:
        """The number of record failures for Tabular Dataset and file failures for File Dataset that should be ignored
        during processing.

        If the error count goes above this value, then the job will be aborted. Error threshold is for the entire input
        rather than the individual mini-batch sent to run() method. The range is [-1, int.max]. -1 indicates ignore all
        failures during processing.

        :return: The error threshold
        :rtype: int
        """
        return self._error_threshold

    @error_threshold.setter
    def error_threshold(self, value: int):
        self._error_threshold = value

    @property
    def mini_batch_size(self) -> int:
        """The number of records to be sent to run() method for each mini-batch.

        :return: The batch size
        :rtype: int
        """
        return self._mini_batch_size

    @mini_batch_size.setter
    def mini_batch_size(self, value: int):
        self._mini_batch_size = value

    @property
    def logging_level(self) -> str:
        """A string of the logging level name.

        :return: The loggin level
        :rtype: str
        """
        return self._logging_level

    @logging_level.setter
    def logging_level(self, value: str):
        self._logging_level = value

    @property
    def retry_settings(self) -> BatchRetrySettings:
        """Parallel job run failed retry.

        :return: The retry settings
        :rtype: BatchRetrySettings
        """
        return self._retry_settings

    @retry_settings.setter
    def retry_settings(self, value: BatchRetrySettings):
        self._retry_settings = value

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return Command._picked_fields_from_dict_to_rest_object() + [
            "max_concurrency_per_instance",
            "error_threshold",
            "logging_level",
            "retry_settings",
            "mini_batch_size",
        ]

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from .._schema.command import ParallelSchema

        return ParallelSchema(context=context)
