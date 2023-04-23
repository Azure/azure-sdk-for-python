# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from pathlib import Path
from typing import Dict, Optional, Union, List
from contextlib import contextmanager

from marshmallow import Schema

from azure.ai.ml._schema.component.command_component import CommandComponentSchema
from azure.ai.ml.constants._common import COMPONENT_TYPE
from azure.ai.ml.constants._component import NodeType
from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.entities._job.distribution import (
    DistributionConfiguration,
    MpiDistribution,
    PyTorchDistribution,
    TensorFlowDistribution,
    RayDistribution,
)
from azure.ai.ml.entities._job.job_resource_configuration import JobResourceConfiguration
from azure.ai.ml.entities._job.parameterized_command import ParameterizedCommand
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

from .code import ComponentIgnoreFile
from ._additional_includes import AdditionalIncludes

from ...entities._assets import Code
from ..._restclient.v2022_10_01.models import ComponentVersion
from ..._schema import PathAwareSchema
from ..._utils.utils import get_all_data_binding_expressions, parse_args_description_from_docstring
from .._util import convert_ordered_dict_to_dict, validate_attribute_type
from .._validation import MutableValidationResult
from .component import Component

# pylint: disable=protected-access


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
    :type distribution: Union[dict, PyTorchDistribution, MpiDistribution, TensorFlowDistribution, RayDistribution]
    :param resources: Compute Resource configuration for the component.
    :type resources: Union[dict, ~azure.ai.ml.entities.JobResourceConfiguration]
    :param inputs: Inputs of the component.
    :type inputs: dict
    :param outputs: Outputs of the component.
    :type outputs: dict
    :param instance_count: promoted property from resources.instance_count
    :type instance_count: int
    :param is_deterministic: Whether the command component is deterministic.
    :type is_deterministic: bool
    :param additional_includes: A list of shared additional files to be included in the component.
    :type additional_includes: list
    :param properties: Properties of the component. Contents inside will pass through to backend as a dictionary.
    :type properties: dict

    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if CommandComponent cannot be successfully validated.
        Details will be provided in the error message.
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
        code: Optional[str] = None,
        environment: Optional[Union[str, Environment]] = None,
        distribution: Optional[
            Union[PyTorchDistribution, MpiDistribution, TensorFlowDistribution, RayDistribution]
        ] = None,
        resources: Optional[JobResourceConfiguration] = None,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        instance_count: Optional[int] = None,  # promoted property from resources.instance_count
        is_deterministic: bool = True,
        additional_includes: Optional[List] = None,
        properties: Optional[Dict] = None,
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
        self.additional_includes = additional_includes or []
        self.__additional_includes_obj = None

    @property
    def _additional_includes_obj(self):
        if (
            self.__additional_includes_obj is None
            and self.additional_includes
            and isinstance(self.additional_includes, list)
        ):
            # use property as `self._source_path` is set after __init__ now
            # `self._source_path` is not None when enter this function
            self.__additional_includes_obj = AdditionalIncludes(
                code_path=self.code, yaml_path=self._source_path, additional_includes=self.additional_includes
            )
        return self.__additional_includes_obj

    @property
    def instance_count(self) -> int:
        """Return value of promoted property resources.instance_count.

        :return: Value of resources.instance_count.
        :rtype: Optional[int]
        """
        return self.resources.instance_count if self.resources else None

    @instance_count.setter
    def instance_count(self, value: int):
        if not value:
            return
        if not self.resources:
            self.resources = JobResourceConfiguration(instance_count=value)
        else:
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
        """Dump the command component content into a dictionary."""
        return convert_ordered_dict_to_dict({**self._other_parameter, **super(CommandComponent, self)._to_dict()})

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: ComponentVersion) -> Dict:
        # put it here as distribution is shared by some components, e.g. command
        distribution = obj.properties.component_spec.pop("distribution", None)
        init_kwargs = super()._from_rest_object_to_init_params(obj)
        if distribution:
            init_kwargs["distribution"] = DistributionConfiguration._from_rest_object(distribution)
        return init_kwargs

    def _get_environment_id(self) -> Union[str, None]:
        # Return environment id of environment
        # handle case when environment is defined inline
        if isinstance(self.environment, Environment):
            return self.environment.id
        return self.environment

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return CommandComponentSchema(context=context)

    def _customized_validate(self):
        validation_result = super(CommandComponent, self)._customized_validate()
        if self._additional_includes_obj and self._additional_includes_obj.with_includes:
            validation_result.merge_with(self._additional_includes_obj._validate())
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
            if output.early_available is True and output.is_control is not True:
                msg = f"Early available output {name!r} requires is_control as True, got {output.is_control!r}."
                validation_result.append_error(message=msg, yaml_path=f"outputs.{name}")
        return validation_result

    def _is_valid_data_binding_expression(self, data_binding_expression: str) -> bool:
        current_obj = self
        for item in data_binding_expression.split("."):
            if hasattr(current_obj, item):
                current_obj = getattr(current_obj, item)
            else:
                try:
                    current_obj = current_obj[item]
                except Exception:  # pylint: disable=broad-except
                    return False
        return True

    @classmethod
    def _parse_args_description_from_docstring(cls, docstring):
        return parse_args_description_from_docstring(docstring)

    def __str__(self):
        try:
            return self._to_yaml()
        except BaseException:  # pylint: disable=broad-except
            return super(CommandComponent, self).__str__()

    @contextmanager
    def _resolve_local_code(self) -> Optional[Code]:
        """Try to create a Code object pointing to local code and yield it.

        If there is no local code to upload, yield None. Otherwise, yield a Code object pointing to the code.
        """
        # if there is no local code, yield super()._resolve_local_code() and return early
        if self.code is not None:
            with super()._resolve_local_code() as code:
                if not isinstance(code, Code) or code._is_remote:
                    yield code
                    return

        # This is forbidden by schema CodeFields for now so won't happen.
        if isinstance(self.code, Code):
            yield code
            return

        if self._additional_includes_obj is not None:
            self._additional_includes_obj.resolve()

            # use absolute path in case temp folder & work dir are in different drive
            tmp_code_dir = (
                self._additional_includes_obj.code.absolute()
                if self._additional_includes_obj.code
                else self._additional_includes_obj.yaml_path.absolute()
            )
            rebased_ignore_file = ComponentIgnoreFile(
                tmp_code_dir,
            )

            yield Code(
                base_path=self._base_path,
                path=tmp_code_dir,
                ignore_file=rebased_ignore_file,
            )

            self._additional_includes_obj.cleanup()
        elif self.code is not None:
            yield code
        else:
            yield None
