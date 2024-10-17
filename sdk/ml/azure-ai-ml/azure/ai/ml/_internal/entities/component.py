# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access, redefined-builtin
# disable redefined-builtin to use id/type as argument name
import os
from contextlib import contextmanager
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union
from uuid import UUID

import yaml  # type: ignore[import]
from marshmallow import Schema

from ... import Input, Output
from ..._restclient.v2022_10_01.models import ComponentVersion, ComponentVersionProperties
from ..._schema import PathAwareSchema
from ..._utils._arm_id_utils import parse_name_label
from ..._utils._asset_utils import IgnoreFile
from ...constants._common import DefaultOpenEncoding
from ...entities import Component
from ...entities._assets import Code
from ...entities._component._additional_includes import AdditionalIncludes, AdditionalIncludesMixin
from ...entities._component.code import ComponentIgnoreFile
from ...entities._job.distribution import DistributionConfiguration
from ...entities._system_data import SystemData
from ...entities._util import convert_ordered_dict_to_dict
from ...entities._validation import MutableValidationResult
from .._schema.component import InternalComponentSchema
from ._input_outputs import InternalInput, InternalOutput
from ._merkle_tree import create_merkletree
from .code import InternalCode
from .environment import InternalEnvironment
from .node import InternalBaseNode

_ADDITIONAL_INCLUDES_CONFIG_KEY = "additional_includes"
_ADDITIONAL_INCLUDES_SUFFIX = ".additional_includes"


class InternalComponent(Component, AdditionalIncludesMixin):
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
        code: Optional[Union[str, os.PathLike]] = None,
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
        aether: Optional[Dict] = None,
        **kwargs,
    ):
        _type, self._type_label = parse_name_label(type)
        super().__init__(
            name=name,
            version=version,
            id=id,
            type=_type,
            description=description,
            tags=tags,
            properties=properties,
            display_name=display_name,
            is_deterministic=is_deterministic,  # type: ignore[arg-type]
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
        self.aether = aether

    @classmethod
    def _build_io(cls, io_dict: Union[Dict, Input, Output], is_input: bool):
        component_io = {}
        for name, port in io_dict.items():
            if is_input:
                component_io[name] = InternalInput._from_base(port)
            else:
                component_io[name] = InternalOutput._from_base(port)
        return component_io

    # region AdditionalIncludesMixin

    @classmethod
    def _read_additional_include_configs(cls, yaml_path: Path) -> List[str]:
        """Read additional include configs from the additional includes file.
        The name of the file is the same as the component spec file, with a suffix of ".additional_includes".
        It can be either a yaml file or a text file:
        1. If it is a yaml file, yaml format of additional_includes looks like below:
        ```
        additional_includes:
         - your/local/path
         - type: artifact
           organization: devops_organization
           project: devops_project
           feed: artifacts_feed_name
           name: universal_package_name
           version: package_version
           scope: scope_type
        ```
        2. If it is a text file, each line is a path to include. Note that artifact config is not supported
        in this format.

        :param yaml_path: The yaml path
        :type yaml_path: Path
        :return: The list of additional includes
        :rtype: List[str]
        """
        additional_includes_config_path = yaml_path.with_suffix(_ADDITIONAL_INCLUDES_SUFFIX)
        if additional_includes_config_path.is_file():
            with open(additional_includes_config_path, encoding=DefaultOpenEncoding.READ) as f:
                file_content = f.read()
                try:
                    configs = yaml.safe_load(file_content)
                    if isinstance(configs, dict):
                        return configs.get(_ADDITIONAL_INCLUDES_CONFIG_KEY, [])
                except Exception:  # pylint: disable=W0718
                    # TODO: check if we should catch yaml.YamlError instead here
                    pass
                return [line.strip() for line in file_content.splitlines(keepends=False) if len(line.strip()) > 0]
        return []

    @classmethod
    def _get_additional_includes_field_name(cls) -> str:
        # additional includes for internal components are configured by a file, which is not a field in the yaml
        # return '*' as diagnostics yaml paths and override _get_all_additional_includes_configs.
        return "*"

    def _get_all_additional_includes_configs(self) -> List:
        # internal components must have a source path
        return self._read_additional_include_configs(Path(self._source_path))  # type: ignore[arg-type]
        # TODO: Bug 2881943

    def _get_base_path_for_code(self) -> Path:
        # internal components must have a source path
        return Path(self._source_path).parent  # type: ignore[arg-type]
        # TODO: Bug 2881943

    def _get_origin_code_value(self) -> Union[str, PathLike, None]:
        return super()._get_origin_code_value() or "."

    # endregion

    def _to_ordered_dict_for_yaml_dump(self) -> Dict:
        """Dump the component content into a sorted yaml string.

        :return: The ordered dict
        :rtype: Dict
        """

        obj = super()._to_ordered_dict_for_yaml_dump()
        # dict dumped base on schema will transfer code to an absolute path, while we want to keep its original value
        if "code" in obj:
            if not self.code:
                del obj["code"]
            else:
                obj["code"] = self.code
        return obj

    @property
    def _additional_includes(self) -> AdditionalIncludes:
        """This property is kept for compatibility with old mldesigner sdk.

        :return: The additional includes
        :rtype: AdditionalIncludes
        """
        obj = self._generate_additional_includes_obj()
        from azure.ai.ml._internal.entities._additional_includes import InternalAdditionalIncludes

        obj.__class__ = InternalAdditionalIncludes
        return obj

    # region SchemaValidatableMixin
    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return InternalComponentSchema(context=context)

    def _customized_validate(self) -> MutableValidationResult:
        validation_result = super(InternalComponent, self)._customized_validate()
        skip_path_validation = not self._append_diagnostics_and_check_if_origin_code_reliable_for_local_path_validation(
            validation_result
        )
        # resolving additional includes & update self._base_path can be dangerous,
        # so we just skip path validation if additional includes is provided.
        # note that there will still be client-side error on job submission (after code is resolved)
        # if paths in environment are invalid
        if isinstance(self.environment, InternalEnvironment):
            validation_result.merge_with(
                self.environment.validate(
                    self._base_path,
                    skip_path_validation=skip_path_validation,
                ),
                field_name="environment",
            )
        return validation_result

    # endregion

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: ComponentVersion) -> Dict:
        # put it here as distribution is shared by some components, e.g. command
        distribution = obj.properties.component_spec.pop("distribution", None)
        init_kwargs = super()._from_rest_object_to_init_params(obj)
        if distribution:
            init_kwargs["distribution"] = DistributionConfiguration._from_rest_object(distribution)
        return init_kwargs

    def _to_rest_object(self) -> ComponentVersion:
        component: Union[Dict[Any, Any], List[Any]] = convert_ordered_dict_to_dict(self._to_dict())
        component["_source"] = self._source  # type: ignore[call-overload]
        # TODO: 2883063

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
        :rtype: str
        """
        curr_root = create_merkletree(code_path, ignore_file.is_file_excluded)
        snapshot_id = str(UUID(curr_root.hexdigest_hash[::4]))
        return snapshot_id

    @contextmanager  # type: ignore[arg-type]
    def _try_build_local_code(self) -> Iterable[Code]:
        """Build final code when origin code is a local code.
        Will merge code path with additional includes into a temp folder if additional includes is specified.
        For internal components, file dependencies in environment will be resolved based on the final code.

        :return: The code instance
        :rtype: Iterable[Code]
        """

        tmp_code_dir: Path
        # origin code value of internal component will never be None. check _get_origin_code_value for details
        with self._generate_additional_includes_obj().merge_local_code_and_additional_includes() as tmp_code_dir:  # pylint:disable=contextmanager-generator-missing-cleanup
            # use absolute path in case temp folder & work dir are in different drive
            tmp_code_dir = tmp_code_dir.absolute()

            # file dependency in code will be read during internal environment resolution
            # for example, docker file of the environment may be in additional includes;
            # and it will be read then insert to the environment object during resolution.
            # so we need to resolve environment based on the temporary code path
            if isinstance(self.environment, InternalEnvironment):
                self.environment.resolve(base_path=tmp_code_dir)

            # additional includes config file itself should be ignored
            rebased_ignore_file = ComponentIgnoreFile(
                tmp_code_dir,
                additional_includes_file_name=Path(self._source_path)
                .with_suffix(_ADDITIONAL_INCLUDES_SUFFIX)
                .name,  # type: ignore[arg-type]
                # TODO: Bug 2881943
            )

            # Use the snapshot id in ml-components as code name to enable anonymous
            # component reuse from ml-component runs.
            # calculate snapshot id here instead of inside InternalCode to ensure that
            # snapshot id is calculated based on the built code path
            yield InternalCode(
                name=self._get_snapshot_id(
                    # use absolute path in case temp folder & work dir are in different drive
                    tmp_code_dir,
                    # this ignore-file should be rebased to the built code path
                    rebased_ignore_file,
                ),
                version="1",
                base_path=self._base_path,
                path=tmp_code_dir,
                is_anonymous=True,
                ignore_file=rebased_ignore_file,
            )

    def __call__(self, *args, **kwargs) -> InternalBaseNode:  # pylint: disable=useless-super-delegation
        return super(InternalComponent, self).__call__(*args, **kwargs)
