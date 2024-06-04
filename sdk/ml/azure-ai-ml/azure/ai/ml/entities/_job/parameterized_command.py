# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
import os
from typing import Dict, Optional, Union

from marshmallow import INCLUDE

from azure.ai.ml._restclient.v2023_04_01_preview.models import SweepJob
from azure.ai.ml._schema.core.fields import ExperimentalField
from azure.ai.ml.entities._assets import Environment

from ..._schema import NestedField, UnionField
from ..._schema.job.distribution import (
    MPIDistributionSchema,
    PyTorchDistributionSchema,
    RayDistributionSchema,
    TensorFlowDistributionSchema,
)
from .distribution import (
    DistributionConfiguration,
    MpiDistribution,
    PyTorchDistribution,
    RayDistribution,
    TensorFlowDistribution,
)
from .job_resource_configuration import JobResourceConfiguration
from .queue_settings import QueueSettings

module_logger = logging.getLogger(__name__)

# no reference found. leave it for future use.
INPUT_BINDING_PREFIX = "AZURE_ML_INPUT_"
OLD_INPUT_BINDING_PREFIX = "AZURE_ML_INPUT"


class ParameterizedCommand:
    """Command component version that contains the command and supporting parameters for a Command component
    or job.

    This class should not be instantiated directly. Instead, use the child class
    ~azure.ai.ml.entities.CommandComponent.

    :param command: The command to be executed. Defaults to "".
    :type command: str
    :param resources: The compute resource configuration for the command.
    :type resources: Optional[Union[dict, ~azure.ai.ml.entities.JobResourceConfiguration]]
    :param code: The source code to run the job. Can be a local path or "http:", "https:", or "azureml:" url pointing
        to a remote location.
    :type code: Optional[str]
    :param environment_variables: A dictionary of environment variable names and values.
        These environment variables are set on the process where user script is being executed.
    :type environment_variables: Optional[dict[str, str]]
    :param distribution: The distribution configuration for distributed jobs.
    :type distribution: Optional[Union[dict, ~azure.ai.ml.PyTorchDistribution, ~azure.ai.ml.MpiDistribution,
        ~azure.ai.ml.TensorFlowDistribution, ~azure.ai.ml.RayDistribution]]
    :param environment: The environment that the job will run in.
    :type environment: Optional[Union[str, ~azure.ai.ml.entities.Environment]]
    :param queue_settings: The queue settings for the job.
    :type queue_settings: Optional[~azure.ai.ml.entities.QueueSettings]
    :keyword kwargs: A dictionary of additional configuration parameters.
    :paramtype kwargs: dict
    """

    def __init__(
        self,
        command: Optional[str] = "",
        resources: Optional[Union[dict, JobResourceConfiguration]] = None,
        code: Optional[Union[str, os.PathLike]] = None,
        environment_variables: Optional[Dict] = None,
        distribution: Optional[
            Union[
                Dict,
                MpiDistribution,
                TensorFlowDistribution,
                PyTorchDistribution,
                RayDistribution,
                DistributionConfiguration,
            ]
        ] = None,
        environment: Optional[Union[Environment, str]] = None,
        queue_settings: Optional[QueueSettings] = None,
        **kwargs: Dict,
    ) -> None:
        super().__init__(**kwargs)
        self.command = command
        self.code = code
        self.environment_variables = dict(environment_variables) if environment_variables else {}
        self.environment = environment
        self.distribution = distribution
        self.resources = resources  # type: ignore[assignment]
        self.queue_settings = queue_settings

    @property
    def distribution(
        self,
    ) -> Optional[
        Union[
            dict,
            MpiDistribution,
            TensorFlowDistribution,
            PyTorchDistribution,
            RayDistribution,
            DistributionConfiguration,
        ]
    ]:
        """The configuration for the distributed command component or job.

        :return: The distribution configuration.
        :rtype: Union[~azure.ai.ml.PyTorchDistribution, ~azure.ai.ml.MpiDistribution,
            ~azure.ai.ml.TensorFlowDistribution, ~azure.ai.ml.RayDistribution]
        """
        return self._distribution

    @distribution.setter
    def distribution(self, value: Union[dict, PyTorchDistribution, MpiDistribution]) -> None:
        """Sets the configuration for the distributed command component or job.

        :param value: The distribution configuration for distributed jobs.
        :type value: Union[dict, ~azure.ai.ml.PyTorchDistribution, ~azure.ai.ml.MpiDistribution,
            ~azure.ai.ml.TensorFlowDistribution, ~azure.ai.ml.RayDistribution]
        """
        if isinstance(value, dict):
            dist_schema = UnionField(
                [
                    NestedField(PyTorchDistributionSchema, unknown=INCLUDE),
                    NestedField(TensorFlowDistributionSchema, unknown=INCLUDE),
                    NestedField(MPIDistributionSchema, unknown=INCLUDE),
                    ExperimentalField(NestedField(RayDistributionSchema, unknown=INCLUDE)),
                ]
            )
            value = dist_schema._deserialize(value=value, attr=None, data=None)
        self._distribution = value

    @property
    def resources(self) -> JobResourceConfiguration:
        """The compute resource configuration for the command component or job.

        :return: The compute resource configuration for the command component or job.
        :rtype: ~azure.ai.ml.entities.JobResourceConfiguration
        """
        return self._resources

    @resources.setter
    def resources(self, value: Union[dict, JobResourceConfiguration]) -> None:
        """Sets the compute resource configuration for the command component or job.

        :param value: The compute resource configuration for the command component or job.
        :type value: Union[dict, ~azure.ai.ml.entities.JobResourceConfiguration]
        """
        if isinstance(value, dict):
            value = JobResourceConfiguration(**value)
        self._resources = value

    @classmethod
    def _load_from_sweep_job(cls, sweep_job: SweepJob) -> "ParameterizedCommand":
        parameterized_command = cls(
            command=sweep_job.trial.command,
            code=sweep_job.trial.code_id,
            environment_variables=sweep_job.trial.environment_variables,
            environment=sweep_job.trial.environment_id,
            distribution=DistributionConfiguration._from_rest_object(sweep_job.trial.distribution),
            resources=JobResourceConfiguration._from_rest_object(sweep_job.trial.resources),
            queue_settings=QueueSettings._from_rest_object(sweep_job.queue_settings),
        )
        return parameterized_command
