# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from typing import Any, Dict, List, Optional, Union, cast

from marshmallow import Schema

from azure.ai.ml._schema.component.command_component import CommandComponentSchema
from azure.ai.ml.constants._common import COMPONENT_TYPE
from azure.ai.ml.constants._component import NodeType
from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.entities._job.distribution import (
    DistributionConfiguration,
    MpiDistribution,
    PyTorchDistribution,
    RayDistribution,
    TensorFlowDistribution,
)
from azure.ai.ml.entities._job.job_resource_configuration import JobResourceConfiguration
from azure.ai.ml.entities._job.parameterized_command import ParameterizedCommand
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

from ..._restclient.v2022_10_01.models import ComponentVersion
from ..._schema import PathAwareSchema
from ..._utils.utils import get_all_data_binding_expressions, parse_args_description_from_docstring
from .._util import convert_ordered_dict_to_dict, validate_attribute_type
from .._validation import MutableValidationResult
from ._additional_includes import AdditionalIncludesMixin
from .component import Component

# pylint: disable=protected-access


class CommandComponent(Component, ParameterizedCommand, AdditionalIncludesMixin):
    """Command component version, used to define a Command Component or Job.

    :keyword name: The name of the Command job or component.
    :paramtype name: Optional[str]
    :keyword version: The version of the Command job or component.
    :paramtype version: Optional[str]
    :keyword description: The description of the component. Defaults to None.
    :paramtype description: Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated. Defaults to None.
    :paramtype tags: Optional[dict]
    :keyword display_name: The display name of the component.
    :paramtype display_name: Optional[str]
    :keyword command: The command to be executed.
    :paramtype command: Optional[str]
    :keyword code: The source code to run the job. Can be a local path or "http:", "https:", or "azureml:" url pointing
        to a remote location.
    :type code: Optional[str]
    :keyword environment: The environment that the job will run in.
    :paramtype environment: Optional[Union[str, ~azure.ai.ml.entities.Environment]]
    :keyword distribution: The configuration for distributed jobs. Defaults to None.
    :paramtype distribution: Optional[Union[~azure.ai.ml.PyTorchDistribution, ~azure.ai.ml.MpiDistribution,
        ~azure.ai.ml.TensorFlowDistribution, ~azure.ai.ml.RayDistribution]]
    :keyword resources: The compute resource configuration for the command.
    :paramtype resources: Optional[~azure.ai.ml.entities.JobResourceConfiguration]
    :keyword inputs: A mapping of input names to input data sources used in the job. Defaults to None.
    :paramtype inputs: Optional[dict[str, Union[
        ~azure.ai.ml.Input,
        str,
        bool,
        int,
        float,
        Enum,
        ]]]
    :keyword outputs: A mapping of output names to output data sources used in the job. Defaults to None.
    :paramtype outputs: Optional[dict[str, Union[str, ~azure.ai.ml.Output]]]
    :keyword instance_count: The number of instances or nodes to be used by the compute target. Defaults to 1.
    :paramtype instance_count: Optional[int]
    :keyword is_deterministic: Specifies whether the Command will return the same output given the same input.
        Defaults to True. When True, if a Command (component) is deterministic and has been run before in the
        current workspace with the same input and settings, it will reuse results from a previous submitted job
        when used as a node or step in a pipeline. In that scenario, no compute resources will be used.
    :paramtype is_deterministic: Optional[bool]
    :keyword additional_includes: A list of shared additional files to be included in the component. Defaults to None.
    :paramtype additional_includes: Optional[List[str]]
    :keyword properties: The job property dictionary. Defaults to None.
    :paramtype properties: Optional[dict[str, str]]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if CommandComponent cannot be successfully validated.
        Details will be provided in the error message.

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_command_configurations.py
            :start-after: [START command_component_definition]
            :end-before: [END command_component_definition]
            :language: python
            :dedent: 8
            :caption: Creating a CommandComponent.
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        display_name: Optional[str] = None,
        command: Optional[str] = None,
        code: Optional[Union[str, os.PathLike]] = None,
        environment: Optional[Union[str, Environment]] = None,
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
        resources: Optional[JobResourceConfiguration] = None,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        instance_count: Optional[int] = None,  # promoted property from resources.instance_count
        is_deterministic: bool = True,
        additional_includes: Optional[List] = None,
        properties: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        kwargs[COMPONENT_TYPE] = NodeType.COMMAND

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
            is_deterministic=is_deterministic,
            properties=properties,
            **kwargs,
        )

        # No validation on value passed here because in pipeline job, required code&environment maybe absent
        # and fill in later with job defaults.
        self.command = command
        self.code = code
        self.environment_variables = environment_variables
        self.environment = environment
        self.resources = resources  # type: ignore[assignment]
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
        self.additional_includes = additional_includes or []

    def _to_ordered_dict_for_yaml_dump(self) -> Dict:
        """Dump the component content into a sorted yaml string.

        :return: The ordered dict
        :rtype: Dict
        """

        obj: dict = super()._to_ordered_dict_for_yaml_dump()
        # dict dumped base on schema will transfer code to an absolute path, while we want to keep its original value
        if self.code and isinstance(self.code, str):
            obj["code"] = self.code
        return obj

    @property
    def instance_count(self) -> Optional[int]:
        """The number of instances or nodes to be used by the compute target.

        :return: The number of instances or nodes.
        :rtype: int
        """
        return self.resources.instance_count if self.resources and not isinstance(self.resources, dict) else None

    @instance_count.setter
    def instance_count(self, value: int) -> None:
        """Sets the number of instances or nodes to be used by the compute target.

        :param value: The number of instances of nodes to be used by the compute target. Defaults to 1.
        :type value: int
        """
        if not value:
            return
        if not self.resources:
            self.resources = JobResourceConfiguration(instance_count=value)
        else:
            if not isinstance(self.resources, dict):
                self.resources.instance_count = value

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "environment": (str, Environment),
            "environment_variables": dict,
            "resources": (dict, JobResourceConfiguration),
            "code": (str, os.PathLike),
        }

    def _to_dict(self) -> Dict:
        return cast(
            dict, convert_ordered_dict_to_dict({**self._other_parameter, **super(CommandComponent, self)._to_dict()})
        )

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: ComponentVersion) -> Dict:
        # put it here as distribution is shared by some components, e.g. command
        distribution = obj.properties.component_spec.pop("distribution", None)
        init_kwargs: dict = super()._from_rest_object_to_init_params(obj)
        if distribution:
            init_kwargs["distribution"] = DistributionConfiguration._from_rest_object(distribution)
        return init_kwargs

    def _get_environment_id(self) -> Union[str, None]:
        # Return environment id of environment
        # handle case when environment is defined inline
        if isinstance(self.environment, Environment):
            _id: Optional[str] = self.environment.id
            return _id
        return self.environment

    # region SchemaValidatableMixin
    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        return CommandComponentSchema(context=context)

    def _customized_validate(self) -> MutableValidationResult:
        validation_result = super(CommandComponent, self)._customized_validate()
        self._append_diagnostics_and_check_if_origin_code_reliable_for_local_path_validation(validation_result)
        validation_result.merge_with(self._validate_command())
        validation_result.merge_with(self._validate_early_available_output())
        return validation_result

    def _validate_command(self) -> MutableValidationResult:
        validation_result = self._create_empty_validation_result()
        # command
        if self.command:
            invalid_expressions = []
            for data_binding_expression in get_all_data_binding_expressions(self.command, is_singular=False):
                if not self._is_valid_data_binding_expression(data_binding_expression):
                    invalid_expressions.append(data_binding_expression)

            if invalid_expressions:
                validation_result.append_error(
                    yaml_path="command",
                    message="Invalid data binding expression: {}".format(", ".join(invalid_expressions)),
                )
        return validation_result

    def _validate_early_available_output(self) -> MutableValidationResult:
        validation_result = self._create_empty_validation_result()
        for name, output in self.outputs.items():
            if output.early_available is True and output._is_primitive_type is not True:
                msg = (
                    f"Early available output {name!r} requires output is primitive type, "
                    f"got {output._is_primitive_type!r}."
                )
                validation_result.append_error(message=msg, yaml_path=f"outputs.{name}")
        return validation_result

    def _is_valid_data_binding_expression(self, data_binding_expression: str) -> bool:
        current_obj: Any = self
        for item in data_binding_expression.split("."):
            if hasattr(current_obj, item):
                current_obj = getattr(current_obj, item)
            else:
                try:
                    current_obj = current_obj[item]
                except Exception:  # pylint: disable=W0718
                    return False
        return True

    # endregion

    @classmethod
    def _parse_args_description_from_docstring(cls, docstring: str) -> Dict:
        res: dict = parse_args_description_from_docstring(docstring)
        return res

    def __str__(self) -> str:
        try:
            toYaml: str = self._to_yaml()
            return toYaml
        except BaseException:  # pylint: disable=W0718
            toStr: str = super(CommandComponent, self).__str__()
            return toStr
