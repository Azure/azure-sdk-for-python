# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access, redefined-builtin
# disable redefined-builtin to use id/type as argument name
from contextlib import contextmanager
from typing import Dict, Union

from marshmallow import INCLUDE, Schema

from azure.ai.ml._restclient.v2022_05_01.models import ComponentVersionData, ComponentVersionDetails
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._component import ComponentSource
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict
from azure.ai.ml.entities._validation import ValidationResult

from ... import Input, Output
from .._schema.component import InternalBaseComponentSchema
from ._additional_includes import _AdditionalIncludes
from ._input_outputs import InternalInput
from .environment import InternalEnvironment
from .node import InternalBaseNode


class InternalComponent(Component):
    # pylint: disable=too-many-instance-attributes, too-many-locals
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
    :type creation_context: ~azure.ai.ml.entities.SystemData
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
        ae365exepool: Dict = None,
        launcher: Dict = None,
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
        self.environment = InternalEnvironment(**environment) if isinstance(environment, dict) else environment
        self.environment_variables = environment_variables
        self.__additional_includes = None
        # TODO: remove these to keep it a general component class
        self.command = command
        self.scope = scope
        self.hemera = hemera
        self.hdinsight = hdinsight
        self.parallel = parallel
        self.starlite = starlite
        self.ae365exepool = ae365exepool
        self.launcher = launcher

        # add some internal specific attributes to inputs/outputs after super().__init__()
        self._post_process_internal_inputs_outputs(inputs, outputs)

    @classmethod
    def _build_io(cls, io_dict: Union[Dict, Input, Output], is_input: bool):
        if not is_input:
            return super()._build_io(io_dict, is_input)
        component_io = {}
        for name, port in io_dict.items():
            component_io[name] = InternalInput._cast_from_input_or_dict(port)
        return component_io

    def _post_process_internal_inputs_outputs(
        self,
        inputs_dict: Union[Dict, Input, Output],
        outputs_dict: Union[Dict, Input, Output],
    ):
        for io_name, io_object in self.inputs.items():
            original = inputs_dict[io_name]
            # force append attribute for internal inputs
            if isinstance(original, dict):
                for attr_name in ["is_resource"]:
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
        if isinstance(self.environment, InternalEnvironment):
            validation_result.merge_with(self.environment.validate(self._source_path))
        if self._additional_includes is not None:
            validation_result.merge_with(self._additional_includes.validate())
        return validation_result

    @classmethod
    def _load_from_rest(cls, obj: ComponentVersionData) -> "InternalComponent":
        # pylint: disable=no-member
        loaded_data = cls._create_schema_for_validation({BASE_PATH_CONTEXT_KEY: "./"}).load(
            obj.properties.component_spec, unknown=INCLUDE
        )
        return InternalComponent(
            _source=ComponentSource.REMOTE_WORKSPACE_COMPONENT,
            **loaded_data,
        )

    def _to_rest_object(self) -> ComponentVersionData:
        if isinstance(self.environment, InternalEnvironment):
            self.environment.resolve(self._source_path)
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

    @contextmanager
    def _resolve_local_code(self):
        # if `self._source_path` is None, component is not loaded from local yaml and
        # no need to resolve
        if self._source_path is None:
            yield self.code
        else:
            self._additional_includes.resolve()
            # use absolute path in case temp folder & work dir are in different drive
            yield self._additional_includes.code.absolute()
            self._additional_includes.cleanup()

    def __call__(self, *args, **kwargs) -> InternalBaseNode:  # pylint: disable=useless-super-delegation
        return super(InternalComponent, self).__call__(*args, **kwargs)

    def _schema_validate(self) -> ValidationResult:
        """Validate the resource with the schema.

        return type: ValidationResult
        """
        result = super(InternalComponent, self)._schema_validate()
        # skip unknown field warnings for internal components
        # TODO: move this logic into base class
        result._warnings = list(filter(lambda x: x.message != "Unknown field.", result._warnings))
        return result
