# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import abstractmethod

from .automl_job import AutoMLJob


class AutoMLVertical(AutoMLJob):
    """
    Abstract class for AutoML verticals.
    """

    @abstractmethod
    def __init__(self, task_type: str, **kwargs) -> None:
        self._task_type = task_type
        super().__init__(**kwargs)

    @property
    def task_type(self) -> str:
        return self._task_type

    @task_type.setter
    def task_type(self, task_type: str) -> None:
        self._task_type = task_type
