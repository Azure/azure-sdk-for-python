# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import abstractmethod
from typing import Optional

from azure.ai.ml import Input

from .automl_job import AutoMLJob


class AutoMLVertical(AutoMLJob):
    """Abstract class for AutoML verticals."""

    @abstractmethod
    def __init__(
        self, task_type: str, training_data: Input, validation_data: Input, test_data: Optional[Input] = None, **kwargs
    ) -> None:
        self._task_type = task_type
        self.training_data = training_data
        self.validation_data = validation_data
        self.test_data = test_data
        super().__init__(**kwargs)

    @property
    def task_type(self) -> str:
        return self._task_type

    @task_type.setter
    def task_type(self, task_type: str) -> None:
        self._task_type = task_type

    @property
    def training_data(self) -> Input:
        return self._training_data

    @training_data.setter
    def training_data(self, training_data: Input) -> None:
        self._training_data = training_data

    @property
    def validation_data(self) -> Input:
        return self._validation_data

    @validation_data.setter
    def validation_data(self, validation_data: Input) -> None:
        self._validation_data = validation_data

    @property
    def test_data(self) -> Input:
        return self._test_data

    @test_data.setter
    def test_data(self, test_data: Input) -> None:
        self._test_data = test_data
