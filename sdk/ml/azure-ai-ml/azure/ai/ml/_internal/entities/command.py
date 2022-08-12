# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Union, List

from marshmallow import Schema

from azure.ai.ml._internal._schema.component import NodeType

from azure.ai.ml._internal.entities.component import InternalComponent
from azure.ai.ml._internal.entities.node import InternalBaseNode
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml.entities import CommandJobLimits, ResourceConfiguration
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    CommandJobLimits as RestCommandJobLimits,
    ResourceConfiguration as RestResourceConfiguration,
)
from azure.ai.ml.entities._job.distribution import DistributionConfiguration


class Command(InternalBaseNode):
    """Node of internal command components in pipeline with specific run settings.
    Different from azure.ai.ml.entities.Command, type of this class is CommandComponent.
    """

    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(Command, self).__init__(type=NodeType.COMMAND, **kwargs)
        self._init = True
        self._resources = ResourceConfiguration()
        self._compute = kwargs.pop("compute", None)
        self._environment = kwargs.pop("environment", None)
        self._limits = kwargs.pop("limits", CommandJobLimits())
        self._init = False

    @property
    def compute(self) -> str:
        """Get the compute definition for the command."""
        return self._compute

    @compute.setter
    def compute(self, value: str):
        """Set the compute definition for the command."""
        if value is not None and not isinstance(value, str):
            raise ValueError(f"Failed in setting compute: only string is supported in DPv2 but got {type(value)}")
        self._compute = value

    @property
    def environment(self) -> str:
        """Get the environment definition for the command."""
        return self._environment

    @environment.setter
    def environment(self, value: str):
        """Set the environment definition for the command."""
        if value is not None and not isinstance(value, str):
            raise ValueError(f"Failed in setting environment: only string is supported in DPv2 but got {type(value)}")
        self._environment = value

    @property
    def limits(self) -> CommandJobLimits:
        return self._limits

    @limits.setter
    def limits(self, value: CommandJobLimits):
        self._limits = value

    @property
    def resources(self):
        return self._resources

    @resources.setter
    def resources(self, value: ResourceConfiguration):
        self._resources = value

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return ["environment", "limits"]

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from .._schema.command import CommandSchema

        return CommandSchema(context=context)

    @classmethod
    def _from_rest_object(cls, obj: dict):
        # resources, sweep won't have resources
        if "resources" in obj and obj["resources"]:
            resources = RestResourceConfiguration.from_dict(obj["resources"])
            obj["resources"] = ResourceConfiguration._from_rest_object(resources)

        # Change componentId -> component
        component_id = obj.pop("componentId", None)
        obj["component"] = component_id

        # Change componentId -> component
        obj["compute"] = obj.pop("computeId", None)

        # distribution
        if "distribution" in obj and obj["distribution"]:
            obj["distribution"] = DistributionConfiguration._from_rest_object(obj["distribution"])

        # handle limits
        if "limits" in obj and obj["limits"]:
            obj["limits"] = CommandJobLimits(**obj["limits"])
        return Command(**obj)


class Distributed(Command):
    def __init__(self, **kwargs):
        super(Distributed, self).__init__(**kwargs)
        self._type = NodeType.DISTRIBUTED

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from .._schema.command import DistributedSchema

        return DistributedSchema(context=context)


class CommandComponent(InternalComponent):
    """Command component. Override __call__ to enable strong type intelligence for command specific run settings."""

    def __call__(self, *args, **kwargs) -> Command:
        return super(InternalComponent, self).__call__(*args, **kwargs)
