# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import abstractmethod
from typing import Any, Optional

from azure.ai.ml import Input

from .automl_job import AutoMLJob


class AutoMLVertical(AutoMLJob):
    """Abstract class for AutoML verticals.

    :param task_type: The type of task to run. Possible values include: "classification", "regression", "forecasting".
    :type task_type: str
    :param training_data: Training data input
    :type training_data: Input
    :param validation_data: Validation data input
    :type validation_data: Input
    :param test_data: Test data input, defaults to None
    :type test_data: typing.Optional[Input]
    :raises ValueError: If task_type is not one of "classification", "regression", "forecasting".
    :raises ValueError: If training_data is not of type Input.
    :raises ValueError: If validation_data is not of type Input.
    :raises ValueError: If test_data is not of type Input.
    """

    @abstractmethod
    def __init__(
        self,
        task_type: str,
        training_data: Input,
        validation_data: Input,
        test_data: Optional[Input] = None,
        **kwargs: Any
    ) -> None:
        """Initialize AutoMLVertical.

        Constructor for AutoMLVertical.

        :param task_type: The type of task to run. Possible values include: "classification", "regression"
            , "forecasting".
        :type task_type: str
        :param training_data: Training data input
        :type training_data: Input
        :param validation_data: Validation data input
        :type validation_data: Input
        :param test_data: Test data input, defaults to None
        :type test_data: typing.Optional[Input]
        :raises ValueError: If task_type is not one of "classification", "regression", "forecasting".
        :raises ValueError: If training_data is not of type Input.
        :raises ValueError: If validation_data is not of type Input.
        :raises ValueError: If test_data is not of type Input.
        """
        self._task_type = task_type
        self.training_data = training_data
        self.validation_data = validation_data
        self.test_data = test_data  # type: ignore
        super().__init__(**kwargs)

    @property
    def task_type(self) -> str:
        """Get task type.

        :return: The type of task to run. Possible values include: "classification", "regression", "forecasting".
        :rtype: str
        """
        return self._task_type

    @task_type.setter
    def task_type(self, task_type: str) -> None:
        """Set task type.

        :param task_type: The type of task to run. Possible values include: "classification", "regression"
            , "forecasting".
        :type task_type: str
        """
        self._task_type = task_type

    @property
    def training_data(self) -> Input:
        """Get training data.

        :return: Training data input
        :rtype: Input
        """
        return self._training_data

    @training_data.setter
    def training_data(self, training_data: Input) -> None:
        """Set training data.

        :param training_data: Training data input
        :type training_data: Input
        """
        self._training_data = training_data

    @property
    def validation_data(self) -> Input:
        """Get validation data.

        :return: Validation data input
        :rtype: Input
        """
        return self._validation_data

    @validation_data.setter
    def validation_data(self, validation_data: Input) -> None:
        """Set validation data.

        :param validation_data: Validation data input
        :type validation_data: Input
        """
        self._validation_data = validation_data

    @property
    def test_data(self) -> Input:
        """Get test data.

        :return: Test data input
        :rtype: Input
        """
        return self._test_data

    @test_data.setter
    def test_data(self, test_data: Input) -> None:
        """Set test data.

        :param test_data: Test data input
        :type test_data: Input
        """
        self._test_data = test_data
