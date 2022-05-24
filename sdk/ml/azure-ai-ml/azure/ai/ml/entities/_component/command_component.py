# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
from pathlib import Path
from marshmallow import INCLUDE, Schema
from typing import Dict, Union

from azure.ai.ml._restclient.v2022_05_01.models import (
    ComponentVersionData,
    ComponentVersionDetails,
)
from azure.ai.ml._schema.component.command_component import CommandComponentSchema, RestCommandComponentSchema
from azure.ai.ml.entities._job.distribution import (
    DistributionConfiguration,
    MpiDistribution,
    TensorFlowDistribution,
    PyTorchDistribution,
)
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration
from azure.ai.ml.entities._job.parameterized_command import ParameterizedCommand
from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, COMPONENT_TYPE, ComponentSource
from azure.ai.ml.constants import NodeType
from azure.ai.ml.entities._component.input_output import ComponentInput, ComponentOutput
from .component import Component
from .._util import validate_attribute_type
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget
from .._validation import ValidationResult
from ..._schema import PathAwareSchema
from ..._utils.utils import get_all_data_binding_expressions


class CommandComponent(Component, ParameterizedCommand):
    """Command component version, used to define a command component.

    :param name: Name of the component.
    :type name: str
    :param version: Version of the component.
    :type version: str
    :param description: Description of the component.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param display_name: Display name of the component.
    :type display_name: str
    :param command: Command to be executed in component.
    :type command: str
    :param code: Code file or folder that will be uploaded to the cloud for component execution.
    :type code: str
    :param environment: Environment that component will run in.
    :type environment: Union[Environment, str]
    :param distribution: Distribution configuration for distributed training.
    :type distribution: Union[dict, PyTorchDistribution, MpiDistribution, TensorFlowDistribution]
    :param resources: Compute Resource configuration for the component.
    :type resources: Union[dict, ~azure.ai.ml.entities.ResourceConfiguration]
    :param inputs: Inputs of the component.
    :type inputs: dict
    :param outputs: Outputs of the component.
    :type outputs: dict
    :param instance_count: promoted property from resources.instance_count
    :type instance_count: int
    """

    def __init__(
        self,
        *,
        name: str = None,
        version: str = None,
        description: str = None,
        tags: Dict = None,
        display_name: str = None,
        command: str = None,
        code: str = None,
        environment: Union[str, Environment] = None,
        distribution: Union[PyTorchDistribution, MpiDistribution, TensorFlowDistribution] = None,
        resources: ResourceConfiguration = None,
        inputs: Dict = None,
        outputs: Dict = None,
        instance_count: int = None,  # promoted property from resources.instance_count
        **kwargs,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        kwargs[COMPONENT_TYPE] = NodeType.COMMAND
        # Set default base path
        if "base_path" not in kwargs:
            kwargs["base_path"] = Path(".")

        # Component backend doesn't support environment_variables yet,
        # this is to support the case of CommandComponent being the trial of
        # a SweepJob, where environment_variables is stored as part of trial
        environment_variables = kwargs.pop("environment_variables", None)
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            display_name=display_name,
            inputs=inputs,
            outputs=outputs,
            **kwargs,
        )

        # No validation on value passed here because in pipeline job, required code&environment maybe absent
        # and fill in later with job defaults.
        self.command = command
        self.code = code
        self.environment_variables = environment_variables
        self.environment = environment
        self.resources = resources
        self.distribution = distribution

        # check mutual exclusivity of promoted properties
        if self.resources is not None and instance_count is not None:
            msg = "instance_count and resources are mutually exclusive"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPONENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        self.instance_count = instance_count

    @property
    def instance_count(self) -> int:
        """
        Return value of promoted property resources.instance_count.

        :return: Value of resources.instance_count.
        :rtype: Optional[int]
        """
        return self.resources.instance_count if self.resources else None

    @instance_count.setter
    def instance_count(self, value: int):
        if not value:
            return
        if not self.resources:
            self.resources = ResourceConfiguration(instance_count=value)
        else:
            self.resources.instance_count = value

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "environment": (str, Environment),
            "environment_variables": dict,
            "resources": (dict, ResourceConfiguration),
            "code": (str, os.PathLike),
        }

    def _to_dict(self) -> Dict:
        """Dump the command component content into a dictionary."""

        # Distribution inherits from autorest generated class, use as_dist() to dump to json
        # Replace the name of $schema to schema.
        component_schema_dict = self._get_schema().dump(self)
        component_schema_dict.pop("base_path", None)
        return {**self._other_parameter, **component_schema_dict}

    def _get_environment_id(self) -> Union[str, None]:
        # Return environment id of environment
        # handle case when environment is defined inline
        if isinstance(self.environment, Environment):
            return self.environment.id
        else:
            return self.environment

    @classmethod
    def _get_schema(cls) -> Union[Schema, PathAwareSchema]:
        return CommandComponentSchema(context={BASE_PATH_CONTEXT_KEY: "./"})

    def _validate(self, raise_error=False) -> ValidationResult:
        """Validate the command component."""
        validation_result = super()._validate(raise_error=raise_error)

        # command
        if self.command:
            invalid_expressions = []
            for data_binding_expression in get_all_data_binding_expressions(self.command, is_singular=False):
                if not self._is_valid_data_binding_expression(data_binding_expression):
                    invalid_expressions.append(data_binding_expression)

            if invalid_expressions:
                error_msg = "Invalid data binding expression: {}".format(", ".join(invalid_expressions))
                if raise_error:
                    raise ValidationException(
                        message=error_msg,
                        target=ErrorTarget.COMPONENT,
                        no_personal_data_message="Invalid data binding expression",
                        error_category=ErrorCategory.USER_ERROR,
                    )
                else:
                    validation_result._append_diagnostic("command", message=error_msg)

        return validation_result

    def _is_valid_data_binding_expression(self, data_binding_expression: str) -> bool:
        current_obj = self
        for item in data_binding_expression.split("."):
            if hasattr(current_obj, item):
                current_obj = getattr(current_obj, item)
            else:
                try:
                    current_obj = current_obj[item]
                except Exception:
                    return False
        return True

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs) -> "CommandComponent":
        return CommandComponent(
            yaml_str=kwargs.pop("yaml_str", None),
            _source=kwargs.pop("_source", ComponentSource.YAML),
            **(CommandComponentSchema(context=context).load(data, unknown=INCLUDE, **kwargs)),
        )

    def _to_rest_object(self) -> ComponentVersionData:
        # Convert nested ordered dict to dict.
        # TODO: we may need to use original dict from component YAML(only change code and environment), returning
        # parsed dict might add default value for some field, eg: if we add property "optional" with default value
        # to ComponentInput, it will add field "optional" to all inputs even if user doesn't specify one
        component = json.loads(json.dumps(self._to_dict()))

        properties = ComponentVersionDetails(
            component_spec=component,
            description=self.description,
            is_anonymous=self._is_anonymous,
            properties=self.properties,
            tags=self.tags,
        )
        result = ComponentVersionData(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _load_from_rest(cls, obj: ComponentVersionData) -> "CommandComponent":
        rest_component_version = obj.properties
        inputs = {
            k: ComponentInput._from_rest_object(v)
            for k, v in rest_component_version.component_spec.pop("inputs", {}).items()
        }
        outputs = {
            k: ComponentOutput._from_rest_object(v)
            for k, v in rest_component_version.component_spec.pop("outputs", {}).items()
        }

        distribution = rest_component_version.component_spec.pop("distribution", None)
        if distribution:
            distribution = DistributionConfiguration._from_rest_object(distribution)

        command_component = CommandComponent(
            id=obj.id,
            is_anonymous=rest_component_version.is_anonymous,
            creation_context=obj.system_data,
            inputs=inputs,
            outputs=outputs,
            distribution=distribution,
            # use different schema for component from rest since name may be "invalid"
            **RestCommandComponentSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).load(
                rest_component_version.component_spec, unknown=INCLUDE
            ),
            _source=ComponentSource.REST,
        )
        return command_component

    def __str__(self):
        try:
            return self._ordered_yaml()
        except BaseException:
            return super(CommandComponent, self).__str__()
