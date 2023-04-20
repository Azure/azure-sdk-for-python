# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access, redefined-builtin
# disable redefined-builtin to use id/type as argument name
from contextlib import contextmanager
from os import PathLike
from pathlib import Path
from typing import Dict, Optional, Union
from uuid import UUID

from marshmallow import Schema

from ... import Input, Output
from ..._restclient.v2022_10_01.models import ComponentVersion, ComponentVersionProperties
from ..._schema import PathAwareSchema
from ..._utils._arm_id_utils import parse_name_label
from ..._utils._asset_utils import IgnoreFile
from ...entities import Component
from ...entities._assets import Code
from ...entities._component.code import ComponentIgnoreFile
from ...entities._job.distribution import DistributionConfiguration
from ...entities._system_data import SystemData
from ...entities._util import convert_ordered_dict_to_dict
from ...entities._validation import MutableValidationResult
from .._schema.component import InternalComponentSchema
from ._additional_includes import ADDITIONAL_INCLUDES_SUFFIX, InternalAdditionalIncludes
from ._input_outputs import InternalInput, InternalOutput
from ._merkle_tree import create_merkletree
from .code import InternalCode
from .environment import InternalEnvironment
from .node import InternalBaseNode


class InternalComponent(Component):
    # pylint: disable=too-many-instance-attributes, too-many-locals
    """Base class for internal component version, used to define an internal component. Recommended to create instance
    with component_factory.

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
        _schema: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        display_name: Optional[str] = None,
        type: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        is_deterministic: Optional[bool] = None,
        successful_return_code: Optional[str] = None,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        code: Optional[str] = None,
        environment: Optional[Dict] = None,
        environment_variables: Optional[Dict] = None,
        command: Optional[str] = None,
        id: Optional[str] = None,
        properties: Optional[Dict] = None,
        yaml_str: Optional[str] = None,
        creation_context: Optional[SystemData] = None,
        scope: Optional[Dict] = None,
        hemera: Optional[Dict] = None,
        hdinsight: Optional[Dict] = None,
        parallel: Optional[Dict] = None,
        starlite: Optional[Dict] = None,
        ae365exepool: Optional[Dict] = None,
        launcher: Optional[Dict] = None,
        datatransfer: Optional[Dict] = None,
        **kwargs,
    ):
        type, self._type_label = parse_name_label(type)
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
        self.__ignore_file = None
        # TODO: remove these to keep it a general component class
        self.command = command
        self.scope = scope
        self.hemera = hemera
        self.hdinsight = hdinsight
        self.parallel = parallel
        self.starlite = starlite
        self.ae365exepool = ae365exepool
        self.launcher = launcher
        self.datatransfer = datatransfer

    @classmethod
    def _build_io(cls, io_dict: Union[Dict, Input, Output], is_input: bool):
        component_io = {}
        for name, port in io_dict.items():
            if is_input:
                component_io[name] = InternalInput._from_base(port)
            else:
                component_io[name] = InternalOutput._from_base(port)
        return component_io

    @property
    def _additional_includes(self):
        if self.__additional_includes is None:
            # use property as `self._source_path` is set after __init__ now
            # `self._source_path` is not None when enter this function
            self.__additional_includes = InternalAdditionalIncludes(
                code_path=self.code,
                yaml_path=self._source_path,
            )
        return self.__additional_includes

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return InternalComponentSchema(context=context)

    def _customized_validate(self) -> MutableValidationResult:
        validation_result = super(InternalComponent, self)._customized_validate()
        # if the code is not local path, no need for additional includes
        code = Path(self.code) if self.code is not None else Path(self._source_path).parent
        if code.exists() and self._additional_includes.with_includes:
            validation_result.merge_with(self._additional_includes._validate())
            # resolving additional includes & update self._base_path can be dangerous,
            # so we just skip path validation if additional_includes is used
            # note that there will still be runtime error in submission or execution
            skip_path_validation = True
        else:
            skip_path_validation = False
        if isinstance(self.environment, InternalEnvironment):
            validation_result.merge_with(
                self.environment._validate(self._base_path, skip_path_validation=skip_path_validation),
                field_name="environment",
            )
        return validation_result

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: ComponentVersion) -> Dict:
        # put it here as distribution is shared by some components, e.g. command
        distribution = obj.properties.component_spec.pop("distribution", None)
        init_kwargs = super()._from_rest_object_to_init_params(obj)
        if distribution:
            init_kwargs["distribution"] = DistributionConfiguration._from_rest_object(distribution)
        return init_kwargs

    def _to_rest_object(self) -> ComponentVersion:
        component = convert_ordered_dict_to_dict(self._to_dict())
        component["_source"] = self._source

        properties = ComponentVersionProperties(
            component_spec=component,
            description=self.description,
            is_anonymous=self._is_anonymous,
            properties=self.properties,
            tags=self.tags,
        )
        result = ComponentVersion(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _get_snapshot_id(
        cls,
        code_path: Union[str, PathLike],
        ignore_file: IgnoreFile,
    ) -> str:
        """Get the snapshot id of a component with specific working directory in ml-components. Use this as the name of
        code asset to reuse steps in a pipeline job from ml-components runs.

        :param code_path: The path of the working directory.
        :type code_path: str
        :param ignore_file: The ignore file of the snapshot.
        :type ignore_file: IgnoreFile
        :return: The snapshot id of a component in ml-components with code_path as its working directory.
        """
        curr_root = create_merkletree(code_path, ignore_file.is_file_excluded)
        snapshot_id = str(UUID(curr_root.hexdigest_hash[::4]))
        return snapshot_id

    @contextmanager
    def _resolve_local_code(self) -> Optional[Code]:
        """Try to create a Code object pointing to local code and yield it.

        If there is no local code to upload, yield None. Otherwise, yield a Code object pointing to the code.
        """
        # an internal component always has a default local code of its base path
        # otherwise, if there is no local code, yield super()._resolve_local_code() and return early
        if self.code is not None:
            with super()._resolve_local_code() as code:
                if not isinstance(code, Code) or code._is_remote:
                    yield code
                    return

        # This is forbidden by schema CodeFields for now so won't happen.
        if isinstance(self.code, Code):
            yield code
            return

        def get_additional_include_file_name():
            if self._source_path is not None:
                return Path(self._source_path).with_suffix(ADDITIONAL_INCLUDES_SUFFIX).name
            return None

        self._additional_includes.resolve()

        # file dependency in code will be read during internal environment resolution
        # for example, docker file of the environment may be in additional includes
        # and it will be read then insert to the environment object during resolution
        # so we need to resolve environment based on the temporary code path
        if isinstance(self.environment, InternalEnvironment):
            self.environment.resolve(self._additional_includes.code)
        # use absolute path in case temp folder & work dir are in different drive
        tmp_code_dir = self._additional_includes.code.absolute()
        rebased_ignore_file = ComponentIgnoreFile(
            tmp_code_dir,
            additional_includes_file_name=get_additional_include_file_name(),
        )
        # Use the snapshot id in ml-components as code name to enable anonymous
        # component reuse from ml-component runs.
        # calculate snapshot id here instead of inside InternalCode to ensure that
        # snapshot id is calculated based on the resolved code path
        yield InternalCode(
            name=self._get_snapshot_id(
                # use absolute path in case temp folder & work dir are in different drive
                self._additional_includes.code.absolute(),
                # this ignore-file should be rebased to the resolved code path
                rebased_ignore_file,
            ),
            version="1",
            base_path=self._base_path,
            path=tmp_code_dir,
            is_anonymous=True,
            ignore_file=rebased_ignore_file,
        )

        self._additional_includes.cleanup()

    def __call__(self, *args, **kwargs) -> InternalBaseNode:  # pylint: disable=useless-super-delegation
        return super(InternalComponent, self).__call__(*args, **kwargs)
