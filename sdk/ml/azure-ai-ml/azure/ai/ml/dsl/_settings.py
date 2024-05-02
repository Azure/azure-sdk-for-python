# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from collections import deque
from typing import Any, Deque, Dict, Optional, Union

from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.exceptions import UserErrorException

module_logger = logging.getLogger(__name__)


class _DSLSettingsStack:
    def __init__(self) -> None:
        self._stack: Deque["_DSLSettings"] = deque()

    def push(self) -> None:
        self._stack.append(_DSLSettings())

    def pop(self) -> "_DSLSettings":
        self._check_stack()
        return self._stack.pop()

    def top(self) -> "_DSLSettings":
        self._check_stack()
        return self._stack[-1]

    def _check_stack(self) -> None:
        # as there is a separate stack push & pop operation management, if stack is empty,
        # it should be the scenario that user call `set_pipeline_settings` out of `pipeline` decorator,
        # then directly raise user error.
        if len(self._stack) == 0:
            error_message = "Please call `set_pipeline_settings` inside a `pipeline` decorated function."
            raise UserErrorException(
                message=error_message,
                no_personal_data_message=error_message,
            )


_dsl_settings_stack = _DSLSettingsStack()


class _DSLSettings:
    """Initialization & finalization job settings for DSL pipeline job.

    Store settings from `dsl.set_pipeline_settings` during pipeline definition.
    """

    def __init__(self) -> None:
        self._init_job: Any = None
        self._finalize_job: Any = None

    @property
    def init_job(self) -> Union[BaseNode, str]:
        return self._init_job

    @init_job.setter
    def init_job(self, value: Optional[Union[BaseNode, str]]) -> None:
        # pylint: disable=logging-fstring-interpolation
        if isinstance(value, (BaseNode, str)):
            self._init_job = value
        else:
            module_logger.warning(f"Initialization job setting is ignored as input parameter type is {type(value)!r}.")

    @property
    def init_job_set(self) -> bool:
        # note: need to use `BaseNode is not None` as `bool(BaseNode)` will return False
        return self._init_job is not None

    def init_job_name(self, jobs: Dict[str, BaseNode]) -> Optional[str]:
        if isinstance(self._init_job, str):
            return self._init_job
        for name, job in jobs.items():
            if id(self.init_job) == id(job):
                return name
        module_logger.warning("Initialization job setting is ignored as cannot find corresponding job node.")
        return None

    @property
    def finalize_job(self) -> Union[BaseNode, str]:
        return self._finalize_job

    @finalize_job.setter
    def finalize_job(self, value: Optional[Union[BaseNode, str]]) -> None:
        # pylint: disable=logging-fstring-interpolation
        if isinstance(value, (BaseNode, str)):
            self._finalize_job = value
        else:
            module_logger.warning(f"Finalization job setting is ignored as input parameter type is {type(value)!r}.")

    @property
    def finalize_job_set(self) -> bool:
        # note: need to use `BaseNode is not None` as `bool(BaseNode)` will return False
        return self._finalize_job is not None

    def finalize_job_name(self, jobs: Dict[str, BaseNode]) -> Optional[str]:
        if isinstance(self._finalize_job, str):
            return self._finalize_job
        for name, job in jobs.items():
            if id(self.finalize_job) == id(job):
                return name
        module_logger.warning("Finalization job setting is ignored as cannot find corresponding job node.")
        return None


def set_pipeline_settings(
    *,
    on_init: Optional[Union[BaseNode, str]] = None,
    on_finalize: Optional[Union[BaseNode, str]] = None,
) -> None:
    """Set pipeline settings for current `dsl.pipeline` definition.

    This function should be called inside a `dsl.pipeline` decorated function, otherwise will raise exception.

    :keyword on_init: On_init job node or name. On init job will be executed before all other jobs, \
                it should not have data connections to regular nodes.
    :paramtype on_init: Union[BaseNode, str]
    :keyword on_finalize: On_finalize job node or name. On finalize job will be executed after pipeline run \
                finishes (completed/failed/canceled), it should not have data connections to regular nodes.
    :paramtype on_finalize: Union[BaseNode, str]
    :return:
    """
    dsl_settings = _dsl_settings_stack.top()
    if on_init is not None:
        dsl_settings.init_job = on_init
    if on_finalize is not None:
        dsl_settings.finalize_job = on_finalize
