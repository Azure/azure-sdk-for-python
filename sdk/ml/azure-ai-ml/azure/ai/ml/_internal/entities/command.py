# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access
from typing import Dict, List, Union

from marshmallow import INCLUDE, Schema

from ... import MpiDistribution, PyTorchDistribution, TensorFlowDistribution, RayDistribution
from ..._schema import PathAwareSchema
from ..._schema.core.fields import DistributionField
from ...entities import CommandJobLimits, JobResourceConfiguration
from ...entities._util import get_rest_dict_for_node_attrs
from .._schema.component import NodeType
from ..entities.component import InternalComponent
from ..entities.node import InternalBaseNode


class Command(InternalBaseNode):
    """Node of internal command components in pipeline with specific run settings.

    Different from azure.ai.ml.entities.Command, type of this class is CommandComponent.
    """

    def __init__(self, **kwargs):
        node_type = kwargs.pop("type", None) or NodeType.COMMAND
        super(Command, self).__init__(type=node_type, **kwargs)
        self._init = True
        self._resources = kwargs.pop("resources", JobResourceConfiguration())
        self._compute = kwargs.pop("compute", None)
        self._environment = kwargs.pop("environment", None)
        self._environment_variables = kwargs.pop("environment_variables", None)
        self._limits = kwargs.pop("limits", CommandJobLimits())
        self._init = False

    @property
    def compute(self) -> str:
        """Get the compute definition for the command."""
        return self._compute

    @compute.setter
    def compute(self, value: str):
        """Set the compute definition for the command."""
        self._compute = value

    @property
    def environment(self) -> str:
        """Get the environment definition for the command."""
        return self._environment

    @environment.setter
    def environment(self, value: str):
        """Set the environment definition for the command."""
        self._environment = value

    @property
    def environment_variables(self) -> Dict[str, str]:
        """Get the environment variables for the command."""
        return self._environment_variables

    @environment_variables.setter
    def environment_variables(self, value: Dict[str, str]):
        """Set the environment variables for the command."""
        self._environment_variables = value

    @property
    def limits(self) -> CommandJobLimits:
        return self._limits

    @limits.setter
    def limits(self, value: CommandJobLimits):
        self._limits = value

    @property
    def resources(self) -> JobResourceConfiguration:
        """Compute Resource configuration for the component."""
        return self._resources

    @resources.setter
    def resources(self, value: JobResourceConfiguration):
        self._resources = value

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return ["environment", "limits", "resources", "environment_variables"]

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from .._schema.command import CommandSchema

        return CommandSchema(context=context)

    def _to_rest_object(self, **kwargs) -> dict:
        rest_obj = super()._to_rest_object(**kwargs)
        rest_obj.update(
            dict(
                limits=get_rest_dict_for_node_attrs(self.limits, clear_empty_value=True),
                resources=get_rest_dict_for_node_attrs(self.resources, clear_empty_value=True),
            )
        )
        return rest_obj

    @classmethod
    def _from_rest_object_to_init_params(cls, obj):
        obj = InternalBaseNode._from_rest_object_to_init_params(obj)

        if "resources" in obj and obj["resources"]:
            obj["resources"] = JobResourceConfiguration._from_rest_object(obj["resources"])

        # handle limits
        if "limits" in obj and obj["limits"]:
            obj["limits"] = CommandJobLimits._from_rest_object(obj["limits"])
        return obj


class Distributed(Command):
    def __init__(self, **kwargs):
        super(Distributed, self).__init__(**kwargs)
        self._distribution = kwargs.pop("distribution", None)
        self._type = NodeType.DISTRIBUTED
        if self._distribution is None:
            # hack: distribution.type is required to set distribution, which is defined in launcher.type
            if (
                isinstance(self.component, InternalComponent)
                and self.component.launcher
                and "type" in self.component.launcher
            ):
                self.distribution = {"type": self.component.launcher["type"]}
            else:
                raise ValueError(
                    "launcher.type must be specified in definition of DistributedComponent but got {}".format(
                        self.component
                    )
                )

    @property
    def distribution(
        self,
    ) -> Union[PyTorchDistribution, MpiDistribution, TensorFlowDistribution, RayDistribution]:
        """The distribution config of component, e.g. distribution={'type': 'mpi'}."""
        return self._distribution

    @distribution.setter
    def distribution(
        self,
        value: Union[Dict, PyTorchDistribution, TensorFlowDistribution, MpiDistribution, RayDistribution],
    ):
        if isinstance(value, dict):
            dist_schema = DistributionField(unknown=INCLUDE)
            value = dist_schema._deserialize(value=value, attr=None, data=None)
        self._distribution = value

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from .._schema.command import DistributedSchema

        return DistributedSchema(context=context)

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return Command._picked_fields_from_dict_to_rest_object() + ["distribution"]

    def _to_rest_object(self, **kwargs) -> dict:
        rest_obj = super()._to_rest_object(**kwargs)
        distribution = self.distribution._to_rest_object() if self.distribution else None  # pylint: disable=no-member
        rest_obj.update(
            dict(
                distribution=get_rest_dict_for_node_attrs(distribution),
            )
        )
        return rest_obj
