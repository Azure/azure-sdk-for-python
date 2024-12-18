# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import contextlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Tuple, Union

import yaml  # type: ignore[import]
from marshmallow import EXCLUDE, Schema, ValidationError

from azure.ai.ml.constants._common import (
    BASE_PATH_CONTEXT_KEY,
    COMPONENT_TYPE,
    PROMPTFLOW_AZUREML_OVERRIDE_KEY,
    SOURCE_PATH_CONTEXT_KEY,
    AssetTypes,
    SchemaUrl,
)
from azure.ai.ml.constants._component import ComponentParameterTypes, NodeType

from ..._restclient.v2022_10_01.models import ComponentVersion
from ..._schema import PathAwareSchema
from ..._schema.component.flow import FlowComponentSchema, FlowSchema, RunSchema
from ...exceptions import ErrorCategory, ErrorTarget, ValidationException
from .. import Environment
from .._inputs_outputs import GroupInput, Input, Output
from ._additional_includes import AdditionalIncludesMixin
from .component import Component

# avoid circular import error
if TYPE_CHECKING:
    from azure.ai.ml.entities._builders.parallel import Parallel

# pylint: disable=protected-access


class _FlowPortNames:
    """Common yaml fields.

    Common yaml fields are used to define the common fields in yaml files. It can be one of the following values: type,
    name, $schema.
    """

    DATA = "data"
    RUN_OUTPUTS = "run_outputs"
    CONNECTIONS = "connections"

    FLOW_OUTPUTS = "flow_outputs"
    DEBUG_INFO = "debug_info"


class _FlowComponentPortDict(dict):
    def __init__(self, ports: Dict):
        self._allow_update_item = True
        super().__init__()
        for input_port_name, input_port in ports.items():
            self[input_port_name] = input_port
        self._allow_update_item = False

    def __setitem__(self, key: Any, value: Any) -> None:
        if not self._allow_update_item:
            raise RuntimeError("Ports of flow component are not editable.")
        super().__setitem__(key, value)

    def __delitem__(self, key: Any) -> None:
        if not self._allow_update_item:
            raise RuntimeError("Ports of flow component are not editable.")
        super().__delitem__(key)


class FlowComponentInputDict(_FlowComponentPortDict):
    """Input port dictionary for FlowComponent, with fixed input ports."""

    def __init__(self) -> None:
        super().__init__(
            {
                _FlowPortNames.CONNECTIONS: GroupInput(values={}, _group_class=None),
                _FlowPortNames.DATA: Input(type=AssetTypes.URI_FOLDER, optional=False),
                _FlowPortNames.FLOW_OUTPUTS: Input(type=AssetTypes.URI_FOLDER, optional=True),
            }
        )

    @contextlib.contextmanager
    def _fit_inputs(self, inputs: Optional[Dict]) -> Generator:
        """Add dynamic input ports to the input port dictionary.
        Input ports of a flow component include:
        1. data: required major uri_folder input
        2. run_output: optional uri_folder input
        3. connections.xxx.xxx: group of string parameters, first layer key can be any node name,
           but we won't resolve the exact keys in SDK
        4. xxx: input_mapping parameters, key can be any node name, but we won't resolve the exact keys in SDK

        #3 will be grouped into connections, we make it a fixed group input port.
        #4 are dynamic input ports, we will add them temporarily in this context manager and remove them
        after the context manager is finished.

        :param inputs: The dynamic input to fit.
        :type inputs: Dict[str, Any]
        :return: None
        :rtype: None
        """
        dynamic_columns_mapping_keys = []
        dynamic_connections_inputs = defaultdict(list)
        from azure.ai.ml.entities._job.pipeline._io import _GroupAttrDict
        from azure.ai.ml.entities._job.pipeline._io.mixin import flatten_dict

        flattened_inputs = flatten_dict(inputs, _GroupAttrDict, allow_dict_fields=[_FlowPortNames.CONNECTIONS])

        for flattened_input_key in flattened_inputs:
            if flattened_input_key.startswith(f"{_FlowPortNames.CONNECTIONS}."):
                if flattened_input_key.count(".") != 2:
                    raise ValidationException(
                        message="flattened connection input prot name must be "
                        "in the format of connections.<node_name>.<port_name>, "
                        "but got %s" % flattened_input_key,
                        no_personal_data_message="flattened connection input prot name must be in the format of "
                        "connections.<node_name>.<port_name>",
                        target=ErrorTarget.COMPONENT,
                        error_category=ErrorCategory.USER_ERROR,
                    )
                _, node_name, param_name = flattened_input_key.split(".")
                dynamic_connections_inputs[node_name].append(param_name)
                continue
            if flattened_input_key not in self:
                dynamic_columns_mapping_keys.append(flattened_input_key)

        self._allow_update_item = True
        for flattened_input_key in dynamic_columns_mapping_keys:
            self[flattened_input_key] = Input(type=ComponentParameterTypes.STRING, optional=True)
        if dynamic_connections_inputs:
            self[_FlowPortNames.CONNECTIONS] = GroupInput(
                values={
                    node_name: GroupInput(
                        values={
                            parameter_name: Input(
                                type=ComponentParameterTypes.STRING,
                            )
                            for parameter_name in param_names
                        },
                        _group_class=None,
                    )
                    for node_name, param_names in dynamic_connections_inputs.items()
                },
                _group_class=None,
            )
        self._allow_update_item = False

        yield

        self._allow_update_item = True
        for flattened_input_key in dynamic_columns_mapping_keys:
            del self[flattened_input_key]
        self[_FlowPortNames.CONNECTIONS] = GroupInput(values={}, _group_class=None)
        self._allow_update_item = False


class FlowComponentOutputDict(_FlowComponentPortDict):
    """Output port dictionary for FlowComponent, with fixed output ports."""

    def __init__(self) -> None:
        super().__init__(
            {
                _FlowPortNames.FLOW_OUTPUTS: Output(type=AssetTypes.URI_FOLDER),
                _FlowPortNames.DEBUG_INFO: Output(type=AssetTypes.URI_FOLDER),
            }
        )


class FlowComponent(Component, AdditionalIncludesMixin):
    """Flow component version, used to define a Flow Component or Job.

    :keyword name: The name of the Flow job or component.
    :type name: Optional[str]
    :keyword version: The version of the Flow job or component.
    :type version: Optional[str]
    :keyword description: The description of the component. Defaults to None.
    :type description: Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated. Defaults to None.
    :type tags: Optional[dict]
    :keyword display_name: The display name of the component.
    :type display_name: Optional[str]
    :keyword flow: The path to the flow directory or flow definition file. Defaults to None and base path of this
        component will be used as flow directory.
    :type flow: Optional[Union[str, Path]]
    :keyword column_mappings: The column mapping for the flow. Defaults to None.
    :type column_mapping: Optional[dict[str, str]]
    :keyword variant: The variant of the flow. Defaults to None.
    :type variant: Optional[str]
    :keyword connections: The connections for the flow. Defaults to None.
    :type connections: Optional[dict[str, dict[str, str]]]
    :keyword environment_variables: The environment variables for the flow. Defaults to None.
    :type environment_variables: Optional[dict[str, str]]
    :keyword environment: The environment for the flow component. Defaults to None.
    :type environment: Optional[Union[str, Environment])
    :keyword is_deterministic: Specifies whether the Flow will return the same output given the same input.
        Defaults to True. When True, if a Flow (component) is deterministic and has been run before in the
        current workspace with the same input and settings, it will reuse results from a previous submitted job
        when used as a node or step in a pipeline. In that scenario, no compute resources will be used.
    :type is_deterministic: Optional[bool]
    :keyword additional_includes: A list of shared additional files to be included in the component. Defaults to None.
    :type additional_includes: Optional[list[str]]
    :keyword properties: The job property dictionary. Defaults to None.
    :type properties: Optional[dict[str, str]]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if FlowComponent cannot be successfully validated.
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
        flow: Optional[Union[str, Path]] = None,
        column_mapping: Optional[Dict[str, str]] = None,
        variant: Optional[str] = None,
        connections: Optional[Dict[str, Dict[str, str]]] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        environment: Optional[Union[str, Environment]] = None,
        is_deterministic: bool = True,
        additional_includes: Optional[List] = None,
        properties: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        # validate init params are valid type
        kwargs[COMPONENT_TYPE] = NodeType.FLOW_PARALLEL

        # always use flow directory as base path
        # Note: we suppose that there is no relative path in run.yaml other than flow.
        #   If there are any, we will need to rebase them so that they have the same base path as attributes in
        #   flow.dag.yaml
        flow_dir, self._flow = self._get_flow_definition(
            flow=flow,
            base_path=kwargs.pop(BASE_PATH_CONTEXT_KEY, Path.cwd()),
            source_path=kwargs.get(SOURCE_PATH_CONTEXT_KEY, None),
        )
        kwargs[BASE_PATH_CONTEXT_KEY] = flow_dir

        super().__init__(
            name=name or self._normalize_component_name(flow_dir.name),
            version=version or "1",
            description=description,
            tags=tags,
            display_name=display_name,
            inputs={},
            outputs={},
            is_deterministic=is_deterministic,
            properties=properties,
            **kwargs,
        )
        self._environment = environment
        self._column_mapping = column_mapping or {}
        self._variant = variant
        self._connections = connections or {}

        self._inputs = FlowComponentInputDict()
        self._outputs = FlowComponentOutputDict()

        if flow:
            # file existence has been checked in _get_flow_definition
            # we don't need to rebase additional_includes as we have updated base_path
            with open(Path(self.base_path, self._flow), "r", encoding="utf-8") as f:
                flow_content = yaml.safe_load(f.read())
            additional_includes = flow_content.get("additional_includes", None)
            # environment variables in run.yaml have higher priority than those in flow.dag.yaml
            self._environment_variables = flow_content.get("environment_variables", {})
            self._environment_variables.update(environment_variables or {})
        else:
            self._environment_variables = environment_variables or {}

        self._additional_includes = additional_includes or []

        # unlike other Component, code is a private property in FlowComponent and
        # will be used to store the arm id of the created code before constructing rest object
        # we haven't used self.flow directly as self.flow can be a path to the flow dag yaml file instead of a directory
        self._code_arm_id: Optional[str] = None

    # region valid properties
    @property
    def flow(self) -> str:
        """The path to the flow definition file relative to the flow directory.

        :rtype: str
        """
        return self._flow

    @property
    def environment(self) -> Optional[Union[str, Environment]]:
        """The environment for the flow component. Defaults to None.

        :rtype: Union[str, Environment])
        """
        return self._environment

    @environment.setter
    def environment(self, value: Union[str, Environment]) -> None:
        """The environment for the flow component. Defaults to None.

        :param value: The column mapping for the flow.
        :type value: Union[str, Environment])
        """
        self._environment = value

    @property
    def column_mapping(self) -> Dict[str, str]:
        """The column mapping for the flow. Defaults to None.

        :rtype: Dict[str, str]
        """
        return self._column_mapping

    @column_mapping.setter
    def column_mapping(self, value: Optional[Dict[str, str]]) -> None:
        """
        The column mapping for the flow. Defaults to None.

        :param value: The column mapping for the flow.
        :type value: Optional[Dict[str, str]]
        """
        self._column_mapping = value or {}

    @property
    def variant(self) -> Optional[str]:
        """The variant of the flow. Defaults to None.

        :rtype: Optional[str]
        """
        return self._variant

    @variant.setter
    def variant(self, value: Optional[str]) -> None:
        """The variant of the flow. Defaults to None.

        :param value: The variant of the flow.
        :type value: Optional[str]
        """
        self._variant = value

    @property
    def connections(self) -> Dict[str, Dict[str, str]]:
        """The connections for the flow. Defaults to None.

        :rtype: Dict[str, Dict[str, str]]
        """
        return self._connections

    @connections.setter
    def connections(self, value: Optional[Dict[str, Dict[str, str]]]) -> None:
        """
        The connections for the flow. Defaults to None.

        :param value: The connections for the flow.
        :type value: Optional[Dict[str, Dict[str, str]]]
        """
        self._connections = value or {}

    @property
    def environment_variables(self) -> Dict[str, str]:
        """The environment variables for the flow. Defaults to None.

        :rtype: Dict[str, str]
        """
        return self._environment_variables

    @environment_variables.setter
    def environment_variables(self, value: Optional[Dict[str, str]]) -> None:
        """The environment variables for the flow. Defaults to None.

        :param value: The environment variables for the flow.
        :type value: Optional[Dict[str, str]]
        """
        self._environment_variables = value or {}

    @property
    def additional_includes(self) -> List:
        """A list of shared additional files to be included in the component. Defaults to None.

        :rtype: List
        """
        return self._additional_includes

    @additional_includes.setter
    def additional_includes(self, value: Optional[List]) -> None:
        """A list of shared additional files to be included in the component. Defaults to None.
        All local additional includes should be relative to the flow directory.

        :param value: A list of shared additional files to be included in the component.
        :type value: Optional[List]
        """
        self._additional_includes = value or []

    # endregion

    @classmethod
    def _normalize_component_name(cls, value: str) -> str:
        return value.replace("-", "_")

    # region Component
    @classmethod
    def _from_rest_object_to_init_params(cls, obj: ComponentVersion) -> Dict:
        raise RuntimeError("FlowComponent does not support loading from REST object.")

    def _to_rest_object(self) -> ComponentVersion:
        rest_obj = super()._to_rest_object()
        rest_obj.properties.component_spec["code"] = self._code_arm_id
        rest_obj.properties.component_spec["flow_file_name"] = self._flow
        return rest_obj

    def _func(self, **kwargs: Any) -> "Parallel":  # pylint: disable=invalid-overridden-method
        from azure.ai.ml.entities._builders.parallel import Parallel

        with self._inputs._fit_inputs(kwargs):  # type: ignore[attr-defined]
            # pylint: disable=not-callable
            return super()._func(**kwargs)  # type: ignore

    @classmethod
    def _get_flow_definition(
        cls,
        base_path: Path,
        *,
        flow: Optional[Union[str, os.PathLike]] = None,
        source_path: Optional[Union[str, os.PathLike]] = None,
    ) -> Tuple[Path, str]:
        """
        Get the path to the flow directory and the file name of the flow dag yaml file.
        If flow is not specified, we will assume that the source_path is the path to the flow dag yaml file.
        If flow is specified, it can be either a path to the flow dag yaml file or a path to the flow directory.
        If flow is a path to the flow directory, we will assume that the flow dag yaml file is named flow.dag.yaml.

        :param base_path: The base path of the flow component.
        :type base_path: Path
        :keyword flow: The path to the flow directory or flow definition file. Defaults to None and base path of this
            component will be used as flow directory.
        :type flow: Optional[Union[str, Path]]
        :keyword source_path: The source path of the flow component, should be path to the flow dag yaml file
            if specified.
        :type source_path: Optional[Union[str, os.PathLike]]
        :return: The path to the flow directory and the file name of the flow dag yaml file.
        :rtype: Tuple[Path, str]
        """
        flow_file_name = "flow.dag.yaml"

        if flow is None and source_path is None:
            raise cls._create_validation_error(
                message="Either flow or source_path must be specified.",
                no_personal_data_message="Either flow or source_path must be specified.",
            )

        if flow is None:
            # Flow component must be created with a local yaml file, so no need to check if source_path exists
            if isinstance(source_path, (os.PathLike, str)):
                flow_file_name = os.path.basename(source_path)
            return Path(base_path), flow_file_name

        flow_path = Path(flow)
        if not flow_path.is_absolute():
            # if flow_path points to a symlink, we still use the parent of the symlink as origin code
            flow_path = Path(base_path, flow)

        if flow_path.is_dir() and (flow_path / flow_file_name).is_file():
            return flow_path, flow_file_name

        if flow_path.is_file():
            return flow_path.parent, flow_path.name

        raise cls._create_validation_error(
            message="Flow path must be a directory containing flow.dag.yaml or a file, but got %s" % flow_path,
            no_personal_data_message="Flow path must be a directory or a file",
        )

    # endregion

    # region SchemaValidatableMixin
    @classmethod
    def _load_with_schema(
        cls, data: Any, *, context: Optional[Any] = None, raise_original_exception: bool = False, **kwargs: Any
    ) -> Any:
        # FlowComponent should be loaded with FlowSchema or FlowRunSchema instead of FlowComponentSchema
        context = context or {BASE_PATH_CONTEXT_KEY: Path.cwd()}
        _schema = data.get("$schema", None)
        if _schema == SchemaUrl.PROMPTFLOW_RUN:
            schema = RunSchema(context=context)
        elif _schema == SchemaUrl.PROMPTFLOW_FLOW:
            schema = FlowSchema(context=context)
        else:
            raise cls._create_validation_error(
                message="$schema must be specified correctly for loading component from flow, but got %s" % _schema,
                no_personal_data_message="$schema must be specified for loading component from flow",
            )

        # unlike other component, we should ignore unknown fields in flow to keep init_params clean and avoid
        # too much understanding of flow.dag.yaml & run.yaml
        kwargs["unknown"] = EXCLUDE
        try:
            loaded_dict = schema.load(data, **kwargs)
        except ValidationError as e:
            if raise_original_exception:
                raise e
            msg = "Trying to load data with schema failed. Data:\n%s\nError: %s" % (
                json.dumps(data, indent=4) if isinstance(data, dict) else data,
                json.dumps(e.messages, indent=4),
            )
            raise cls._create_validation_error(
                message=msg,
                no_personal_data_message=str(e),
            ) from e
        loaded_dict.update(loaded_dict.pop(PROMPTFLOW_AZUREML_OVERRIDE_KEY, {}))
        return loaded_dict

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        return FlowComponentSchema(context=context)

    # endregion

    # region AdditionalIncludesMixin
    def _get_origin_code_value(self) -> Union[str, os.PathLike, None]:
        if self._code_arm_id:
            return self._code_arm_id
        res: Union[str, os.PathLike, None] = self.base_path
        return res

    def _fill_back_code_value(self, value: str) -> None:
        self._code_arm_id = value

    @contextlib.contextmanager
    def _try_build_local_code(self) -> Generator:
        with super()._try_build_local_code() as code:  # pylint:disable=contextmanager-generator-missing-cleanup
            if not code or not code.path:
                yield code
                return

            if not (Path(code.path) / ".promptflow" / "flow.tools.json").is_file():
                raise self._create_validation_error(
                    message="Flow component must be created with a ./promptflow/flow.tools.json, "
                    "please run `pf flow validate` to generate it or skip it in your ignore file.",
                    no_personal_data_message="Flow component must be created with a ./promptflow/flow.tools.json, "
                    "please run `pf flow validate` to generate it or skip it in your ignore file.",
                )
            # TODO: should we remove additional includes from flow.dag.yaml? for now we suppose it will be removed
            #  by mldesigner compile if needed

            yield code

    # endregion
