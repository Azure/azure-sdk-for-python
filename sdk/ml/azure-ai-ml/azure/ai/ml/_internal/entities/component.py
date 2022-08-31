# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from pathlib import Path
from typing import Dict, Union

from marshmallow import INCLUDE, Schema

from azure.ai.ml._restclient.v2022_05_01.models import ComponentVersionData, ComponentVersionDetails, SystemData
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, ComponentSource
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict
from azure.ai.ml.entities._validation import ValidationResult

from ... import Input, Output
from ...entities._assets import Code
from .._schema.component import InternalBaseComponentSchema
from ._additional_includes import _AdditionalIncludes
from .node import InternalBaseNode

YAML_CODE_FIELD_NAME = "code"
YAML_ENVIRONMENT_CONDA_FIELD_NAME = "conda"
YAML_CONDA_DEPENDENCIES_FIELD_NAME = "conda_dependencies"
YAML_CONDA_DEPENDENCIES_FILE = "conda_dependencies_file"
YAML_PIP_REQUIREMENTS_FILE = "pip_requirements_file"
DEFAULT_PYTHON_VERSION = "3.8.5"


class InternalComponent(Component):
    """Base class for internal component version, used to define an internal
    component. Recommended to create instance with component_factory.

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the resource.
    :type version: str
    :param id:  Global id of the resource, Azure Resource Manager ID.
    :type id: str
    :param type:  Type of the command, supported is 'command'.
    :type type: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param properties: Internal use only.
    :type properties: dict
    :param display_name: Display name of the component.
    :type display_name: str
    :param is_deterministic: Whether the component is deterministic.
    :type is_deterministic: bool
    :param inputs: Inputs of the component.
    :type inputs: dict
    :param outputs: Outputs of the component.
    :type outputs: dict
    :param yaml_str: The yaml string of the component.
    :type yaml_str: str
    :param _schema: Schema of the component.
    :type _schema: str
    :param creation_context: Creation metadata of the component.
    :type creation_context: SystemData
    """

    def __init__(
        self,
        *,
        _schema: str = None,
        name: str = None,
        version: str = None,
        display_name: str = None,
        type: str = None,
        description: str = None,
        tags: Dict = None,
        is_deterministic: bool = None,
        successful_return_code: str = None,
        inputs: Dict = None,
        outputs: Dict = None,
        code: str = None,
        environment: Dict = None,
        environment_variables: Dict = None,
        command: str = None,
        id: str = None,
        properties: Dict = None,
        yaml_str: str = None,
        creation_context: SystemData = None,
        scope: Dict = None,
        hemera: Dict = None,
        hdinsight: Dict = None,
        parallel: Dict = None,
        starlite: Dict = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            version=version,
            id=id,
            type=type,
            description=description,
            tags=tags,
            properties=properties,
            display_name=display_name,
            is_deterministic=is_deterministic,
            inputs=inputs,
            outputs=outputs,
            yaml_str=yaml_str,
            _schema=_schema,
            creation_context=creation_context,
            **kwargs,
        )
        # Store original yaml
        self._yaml_str = yaml_str
        self._other_parameter = kwargs

        self.successful_return_code = successful_return_code
        self.code = code
        self.environment = environment
        self.environment_variables = environment_variables
        # TODO: remove this to keep it a general component class
        self.command = command
        self.scope = scope
        self.hemera = hemera
        self.hdinsight = hdinsight
        self.parallel = parallel
        self.starlite = starlite
        self.__additional_includes = None

        # add some internal specific attributes to inputs/outputs after super().__init__()
        self._build_internal_inputs_outputs(inputs, outputs)

    def _build_internal_inputs_outputs(
        self,
        inputs_dict: Union[Dict, Input, Output],
        outputs_dict: Union[Dict, Input, Output],
    ):
        for io_name, io_object in self.inputs.items():
            original = inputs_dict[io_name]
            # force append attribute for internal inputs
            if isinstance(original, dict):
                for attr_name in ["is_resource", "default", "optional"]:
                    if attr_name in original:
                        io_object.__setattr__(attr_name, original[attr_name])

        for io_name, io_object in self.outputs.items():
            original = outputs_dict[io_name]
            # force append attribute for internal inputs
            if isinstance(original, dict):
                for attr_name in ["datastore_mode"]:
                    if attr_name in original:
                        io_object.__setattr__(attr_name, original[attr_name])

    @property
    def _additional_includes(self):
        if self.__additional_includes is None:
            # use property as `self._source_path` is set after __init__ now
            # `self._source_path` is not None when enter this function
            self.__additional_includes = _AdditionalIncludes(
                code_path=self.code,
                yaml_path=self._source_path,
            )
        return self.__additional_includes

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return InternalBaseComponentSchema(context=context)

    def _customized_validate(self) -> ValidationResult:
        validation_result = super(InternalComponent, self)._customized_validate()
        validation_result.merge_with(self._validate_environment())
        if self._additional_includes is not None:
            validation_result.merge_with(self._additional_includes.validate())
        return validation_result

    @classmethod
    def _load_from_rest(cls, obj: ComponentVersionData) -> "InternalComponent":
        loaded_data = cls._create_schema_for_validation({BASE_PATH_CONTEXT_KEY: "./"}).load(
            obj.properties.component_spec, unknown=INCLUDE
        )
        return InternalComponent(
            _source=ComponentSource.REMOTE_WORKSPACE_COMPONENT,
            **loaded_data,
        )

    def _to_rest_object(self) -> ComponentVersionData:
        component = convert_ordered_dict_to_dict(self._to_dict())

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

    def _resolve_local_dependencies(self) -> None:
        # if `self._source_path` is None, component is not loaded from local yaml and no need to resolve
        if self._source_path is None:
            return
        self._additional_includes.resolve()
        # use absolute path in case temp folder & work dir are in different drive
        self.code = self._additional_includes.code.absolute()
        self._resolve_local_environment()

    def _cleanup_tmp_local_dependencies(self) -> None:
        # if `self._source_path` is None, component is not loaded from local yaml and no need to clean
        if self._source_path is None:
            return
        self._additional_includes.cleanup()

    def _resolve_local_code(self, get_code_arm_id_and_fill_back) -> None:
        if self._source_path is not None and self._additional_includes:
            self._resolve_local_dependencies()
            self.code = get_code_arm_id_and_fill_back(Code(base_path=self._base_path, path=self.code))
            self._cleanup_tmp_local_dependencies()
        else:
            super(InternalComponent, self)._resolve_local_code(get_code_arm_id_and_fill_back)

    def __call__(self, *args, **kwargs) -> InternalBaseNode:
        return super(InternalComponent, self).__call__(*args, **kwargs)

    def _schema_validate(self) -> ValidationResult:
        """Validate the resource with the schema.

        return type: ValidationResult
        """
        result = super(InternalComponent, self)._schema_validate()
        # skip unknown field warnings for internal components
        # TODO: move this logic into base class
        result._warnings = list(filter(lambda x: x.descriptor.message != "Unknown field.", result._warnings))
        return result

    def _validate_environment(self) -> ValidationResult:
        validation_result = self._create_empty_validation_result()
        if not self.environment or not self.environment.get(YAML_ENVIRONMENT_CONDA_FIELD_NAME):
            return validation_result
        environment_conda_dict = self.environment[YAML_ENVIRONMENT_CONDA_FIELD_NAME]
        # only one of "conda_dependencies", "conda_dependencies_file" and "pip_requirements_file" should exist
        dependencies_field_names = {
            YAML_CONDA_DEPENDENCIES_FIELD_NAME,
            YAML_CONDA_DEPENDENCIES_FILE,
            YAML_PIP_REQUIREMENTS_FILE,
        }
        if len(set(environment_conda_dict.keys()) & dependencies_field_names) > 1:
            validation_result.append_warning(
                yaml_path="environment.conda",
                message="Duplicated declaration of dependencies, will honor in the order "
                "conda_dependencies, conda_dependencies_file, pip_requirements_file.",
            )
        # if dependencies file is specified, check its existence
        if environment_conda_dict.get(YAML_CONDA_DEPENDENCIES_FILE):
            conda_dependencies_file = environment_conda_dict[YAML_CONDA_DEPENDENCIES_FILE]
            if not (Path(self._source_path).parent / conda_dependencies_file).is_file():
                validation_result.append_error(
                    yaml_path=f"environment.conda.{YAML_CONDA_DEPENDENCIES_FILE}",
                    message=f"Conda dependencies file not exists: {conda_dependencies_file}",
                )
        if environment_conda_dict.get(YAML_PIP_REQUIREMENTS_FILE):
            pip_requirements_file = environment_conda_dict[YAML_PIP_REQUIREMENTS_FILE]
            if not (Path(self._source_path).parent / pip_requirements_file).is_file():
                validation_result.append_error(
                    yaml_path=f"environment.conda.{YAML_PIP_REQUIREMENTS_FILE}",
                    message=f"Conda dependencies file not exists: {pip_requirements_file}",
                )
        return validation_result

    def _resolve_local_environment(self) -> None:
        """Resolve environment dependencies when refer to local file."""
        if not self.environment or not self.environment.get(YAML_ENVIRONMENT_CONDA_FIELD_NAME, {}):
            return
        environment_conda_dict = self.environment[YAML_ENVIRONMENT_CONDA_FIELD_NAME]
        if environment_conda_dict.get(YAML_CONDA_DEPENDENCIES_FILE):
            conda_dependencies_file = environment_conda_dict[YAML_CONDA_DEPENDENCIES_FILE]
            conda_dependencies_file_path = Path(self._source_path).parent / conda_dependencies_file
            conda_dependencies_dict = load_yaml(conda_dependencies_file_path)
            self.environment[YAML_ENVIRONMENT_CONDA_FIELD_NAME].pop(YAML_CONDA_DEPENDENCIES_FILE)
            self.environment[YAML_ENVIRONMENT_CONDA_FIELD_NAME] = {
                YAML_CONDA_DEPENDENCIES_FIELD_NAME: conda_dependencies_dict
            }
            return
        if environment_conda_dict.get(YAML_PIP_REQUIREMENTS_FILE):
            pip_requirements_file = environment_conda_dict[YAML_PIP_REQUIREMENTS_FILE]
            pip_requirements_file_path = Path(self._source_path).parent / pip_requirements_file
            self.environment[YAML_ENVIRONMENT_CONDA_FIELD_NAME].pop(YAML_PIP_REQUIREMENTS_FILE)
            with open(pip_requirements_file_path, "r") as fin:
                pip_requirements = fin.read().splitlines()
                self.environment[YAML_ENVIRONMENT_CONDA_FIELD_NAME] = {
                    YAML_CONDA_DEPENDENCIES_FIELD_NAME: {
                        "name": "project_environment",
                        "dependencies": [
                            f"python={DEFAULT_PYTHON_VERSION}",
                            {
                                "pip": pip_requirements,
                            },
                        ],
                    }
                }
            return
