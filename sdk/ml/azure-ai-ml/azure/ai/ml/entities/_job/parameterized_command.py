# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Dict, Union

from marshmallow import INCLUDE

from azure.ai.ml._restclient.v2022_02_01_preview.models import SweepJob
from azure.ai.ml._schema.job.loadable_mixin import LoadableMixin
from azure.ai.ml.entities._assets import Environment

from ..._schema import NestedField, UnionField
from ..._schema.job.distribution import MPIDistributionSchema, PyTorchDistributionSchema, TensorFlowDistributionSchema
from .distribution import MpiDistribution, PyTorchDistribution, TensorFlowDistribution
from .resource_configuration import ResourceConfiguration

module_logger = logging.getLogger(__name__)

# no reference found. leave it for future use.
INPUT_BINDING_PREFIX = "AZURE_ML_INPUT_"
OLD_INPUT_BINDING_PREFIX = "AZURE_ML_INPUT"


class ParameterizedCommand(LoadableMixin):
    """Command component that contains the training command and supporting
    parameters for the command.

    :param command: Command to be executed in training.
    :type command: str
    :param code: A local or remote path pointing at source code.
    :type code: str
    :param distribution: Distribution configuration for distributed training.
    :type distribution: Union[Dict, PyTorchDistribution, MpiDistribution, TensorFlowDistribution]
    :param environment: Environment that training job will run in.
    :type environment: Union[Environment, str]
    :param resources: Compute Resource configuration for the job.
    :type resources: Union[Dict, ~azure.ai.ml.entities.ResourceConfiguration]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        command: str = "",
        resources: Union[dict, ResourceConfiguration] = None,
        code: str = None,
        environment_variables: Dict = None,
        distribution: Union[dict, MpiDistribution, TensorFlowDistribution, PyTorchDistribution] = None,
        environment: Union["Environment", str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.command = command
        self.code = code
        self.environment_variables = dict(environment_variables) if environment_variables else {}
        self.environment = environment
        self.distribution: Union[MpiDistribution, TensorFlowDistribution, PyTorchDistribution] = distribution
        self.resources = resources

    @property
    def distribution(
        self,
    ) -> Union[MpiDistribution, TensorFlowDistribution, PyTorchDistribution]:
        return self._distribution

    @distribution.setter
    def distribution(self, value):
        if isinstance(value, dict):
            dist_schema = UnionField(
                [
                    NestedField(PyTorchDistributionSchema, unknown=INCLUDE),
                    NestedField(TensorFlowDistributionSchema, unknown=INCLUDE),
                    NestedField(MPIDistributionSchema, unknown=INCLUDE),
                ]
            )
            value = dist_schema._deserialize(value=value, attr=None, data=None)
        self._distribution = value

    @property
    def resources(self) -> ResourceConfiguration:
        return self._resources

    @resources.setter
    def resources(self, value):
        if isinstance(value, dict):
            value = ResourceConfiguration(**value)
        self._resources = value

    @classmethod
    def _load_from_sweep_job(cls, sweep_job: SweepJob) -> "ParameterizedCommand":
        parameterized_command = cls(
            command=sweep_job.trial.command,
            code=sweep_job.trial.code_id,
            environment_variables=sweep_job.trial.environment_variables,
            environment=sweep_job.trial.environment_id,
            distribution=sweep_job.trial.distribution,
            resources=ResourceConfiguration._from_rest_object(sweep_job.trial.resources),
        )
        return parameterized_command
