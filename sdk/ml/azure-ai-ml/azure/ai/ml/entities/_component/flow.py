# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import contextlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import yaml
from marshmallow import EXCLUDE, Schema, ValidationError

from azure.ai.ml.constants._common import (
    BASE_PATH_CONTEXT_KEY,
    COMPONENT_TYPE,
    SOURCE_PATH_CONTEXT_KEY,
    AssetTypes,
    SchemaUrl,
)
from azure.ai.ml.constants._component import ComponentParameterTypes, NodeType

from ..._restclient.v2022_10_01.models import ComponentVersion
from ..._schema import PathAwareSchema
from ..._schema.component.flow import FlowComponentSchema, FlowSchema, RunSchema
from ...exceptions import ErrorCategory, ValidationException
from .._assets import Code
from .._inputs_outputs import GroupInput, Input, Output
from .._job.pipeline._io import _GroupAttrDict
from ._additional_includes import AdditionalIncludesMixin
from .component import Component

# pylint: disable=protected-access


class FlowComponentPortDict(dict):
    def __setitem__(self, key, value):
        raise RuntimeError("Ports of flow component are not editable.")

    def __getitem__(self, item):
        raise RuntimeError("Ports of flow component are not readable before creation.")


class FlowComponent(Component, AdditionalIncludesMixin):
    """Command component version, used to define a Command Component or Job.

    :keyword name: The name of the Command job or component.
    :type name: Optional[str]
    :keyword version: The version of the Command job or component.
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
    :keyword column_mappings: The column mappings for the flow. Defaults to None.
    :type column_mappings: Optional[dict[str, str]]
    :keyword variant: The variant of the flow. Defaults to None.
    :type variant: Optional[str]
    :keyword connections: The connections for the flow. Defaults to None.
    :type connections: Optional[dict[str, dict[str, str]]]
    :keyword environment_variables: The environment variables for the flow. Defaults to None.
    :type environment_variables: Optional[dict[str, str]]
    :keyword is_deterministic: Specifies whether the Command will return the same output given the same input.
        Defaults to True. When True, if a Command (component) is deterministic and has been run before in the
        current workspace with the same input and settings, it will reuse results from a previous submitted job
        when used as a node or step in a pipeline. In that scenario, no compute resources will be used.
    :type is_deterministic: Optional[bool]
    :keyword additional_includes: A list of shared additional files to be included in the component. Defaults to None.
    :type additional_includes: Optional[list[str]]
    :keyword properties: The job property dictionary. Defaults to None.
    :type properties: Optional[dict[str, str]]
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
        flow: Optional[Union[str, Path]] = None,
        column_mappings: Optional[Dict[str, str]] = None,
        variant: Optional[str] = None,
        connections: Optional[Dict[str, Dict[str, str]]] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        is_deterministic: bool = True,
        additional_includes: Optional[List] = None,
        properties: Optional[Dict] = None,
        **kwargs,
    ) -> None:
        # validate init params are valid type
        kwargs[COMPONENT_TYPE] = NodeType.FLOW_PARALLEL

        flow_dir, flow_file_name = self._get_flow_definition(
            flow,
            kwargs.get(BASE_PATH_CONTEXT_KEY, Path.cwd()),
            kwargs.get(SOURCE_PATH_CONTEXT_KEY, None),
        )

        super().__init__(
            name=name or flow_dir.name,
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
        self._flow = flow
        self._column_mappings = column_mappings or {}
        self._variant = variant
        self._connections = connections or {}
        self._environment_variables = environment_variables or {}

        if flow:
            # file existence has been checked in _get_flow_definition
            with open(Path(flow_dir, flow_file_name), "r", encoding="utf-8") as f:
                flow_content = f.read()
                additional_includes = yaml.safe_load(flow_content).get("additional_includes", None)
        self._additional_includes = additional_includes or []

        # unlike other Component, code is a private property in FlowComponent
        self._code, self._flow_file_name = None, None

    # region valid properties
    @property
    def flow(self) -> Optional[Union[str, Path]]:
        """The path to the flow directory or flow definition file. Defaults to None and base path of this
        component will be used as flow directory.

        :rtype: Optional[Union[str, Path]]
        """
        return self._flow

    @flow.setter
    def flow(self, value: Optional[Union[str, Path]]) -> None:
        if self._flow != value:
            # reset code and flow file name when flow is changed
            self._code = None
            self._flow_file_name = None
        self._flow = value

    @property
    def column_mappings(self) -> Dict[str, str]:
        """The column mappings for the flow. Defaults to None.

        :rtype: Dict[str, str]
        """
        return self._column_mappings

    @column_mappings.setter
    def column_mappings(self, value: Optional[Dict[str, str]]) -> None:
        self._column_mappings = value or {}

    @property
    def variant(self) -> Optional[str]:
        """The variant of the flow. Defaults to None.

        :rtype: Optional[str]
        """
        return self._variant

    @variant.setter
    def variant(self, value: Optional[str]) -> None:
        self._variant = value

    @property
    def connections(self) -> Dict[str, Dict[str, str]]:
        """The connections for the flow. Defaults to None.

        :rtype: Dict[str, Dict[str, str]]
        """
        return self._connections

    @connections.setter
    def connections(self, value: Optional[Dict[str, Dict[str, str]]]) -> None:
        self._connections = value or {}

    @property
    def environment_variables(self) -> Dict[str, str]:
        """The environment variables for the flow. Defaults to None.

        :rtype: Dict[str, str]
        """
        return self._environment_variables

    @environment_variables.setter
    def environment_variables(self, value: Optional[Dict[str, str]]) -> None:
        self._environment_variables = value or {}

    @property
    def additional_includes(self) -> List:
        """A list of shared additional files to be included in the component. Defaults to None.

        :rtype: List
        """
        return self._additional_includes

    @additional_includes.setter
    def additional_includes(self, value: Optional[List]) -> None:
        self._additional_includes = value or []

    # endregion

    # region Component

    @property
    def inputs(self) -> Dict:
        return self._inputs or FlowComponentPortDict()

    @property
    def outputs(self) -> Dict:
        return self._outputs or FlowComponentPortDict()

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: ComponentVersion) -> Dict:
        raise RuntimeError("FlowComponent does not support loading from REST object.")

    def _to_rest_object(self) -> ComponentVersion:
        rest_obj = super()._to_rest_object()
        rest_obj.properties.component_spec["code"] = self._code
        rest_obj.properties.component_spec["flow_file_name"] = self._flow_file_name
        return rest_obj

    @contextlib.contextmanager
    def _use_actual_input_output_ports(self, input_values: Dict[str, Any]):
        if self._inputs:
            yield
            return

        self._outputs = {
            "flow_outputs": Output(
                type=AssetTypes.URI_FOLDER,
            ),
            "debug_info": Output(
                type=AssetTypes.URI_FOLDER,
            ),
        }

        self._inputs = {
            "data": Input(
                type=AssetTypes.URI_FOLDER,
                optional=False,
            ),
            "run_outputs": Input(
                type=AssetTypes.URI_FOLDER,
            ),
        }

        connection_parameters_root = "connections"
        involved_connection_paths = set()

        def _get_paths(cur_node, cur_paths, target_depth):
            if target_depth == 0:
                return [".".join(cur_paths)]
            paths = []
            if isinstance(cur_node, dict):
                for key, value in cur_node.items():
                    cur_paths.append(key)
                    paths.extend(_get_paths(value, cur_paths, target_depth - 1))
                    cur_paths.pop()
            elif isinstance(cur_node, _GroupAttrDict):
                # TODO: is it necessary to support this?
                raise ValidationException(
                    message="Connection parameters must be a dict for now, but got %s" % cur_node,
                    no_personal_data_message="Connection parameters must be a dict for now",
                    target=self._get_validation_error_target(),
                    error_category=ErrorCategory.USER_ERROR,
                )
            return paths

        for input_port_name, input_value in input_values.items():
            if input_port_name in self._inputs:
                continue
            if input_port_name == connection_parameters_root:
                involved_connection_paths.update(_get_paths(input_value, [connection_parameters_root], 2))
            elif input_port_name.startswith(connection_parameters_root + "."):
                involved_connection_paths.add(input_port_name)
            else:
                self._inputs[input_port_name] = Input(
                    type=ComponentParameterTypes.STRING,
                )

        node_names, param_names = set(), set()
        for connection_path in involved_connection_paths:
            if connection_path.count(".") != 2:
                raise ValidationException(
                    message="Connection path must be in the format of connections.<node_name>.<connection_name>, but "
                    "detected %s" % connection_path,
                    no_personal_data_message="Invalid connection path",
                    target=self._get_validation_error_target(),
                    error_category=ErrorCategory.USER_ERROR,
                )
            _, node_name, parameter_name = connection_path.split(".")
            node_names.add(node_name)
            param_names.add(parameter_name)

        self._inputs[connection_parameters_root] = GroupInput(
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
                for node_name in node_names
            },
            _group_class=None,
        )

        yield
        self._inputs, self._outputs = {}, {}
        return

    def _func(self, **kwargs) -> "Parallel":  # pylint: disable=invalid-overridden-method
        with self._use_actual_input_output_ports(kwargs):
            return super()._func(**kwargs)  # pylint: disable=not-callable

    @classmethod
    def _get_flow_definition(cls, flow, base_path, source_path) -> Tuple[Path, str]:
        flow_file_name = "flow.dag.yaml"

        if flow is None:
            # Flow component must be created with a local yaml file, so no need to check if source_path exists
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

        raise ValidationException(
            message="Flow path must be a directory containing flow.dag.yaml or a file, but got %s" % flow_path,
            no_personal_data_message="Flow path must be a directory or a file",
            target=cls._get_validation_error_target(),
            error_category=ErrorCategory.USER_ERROR,
        )

    # endregion

    # region SchemaValidatableMixin
    @classmethod
    def _load_with_schema(cls, data, *, context=None, raise_original_exception=False, **kwargs):
        # FlowComponent should be loaded with FlowSchema or FlowRunSchema instead of FlowComponentSchema
        context = context or {BASE_PATH_CONTEXT_KEY: Path.cwd()}
        _schema = data.get("$schema", None)
        if _schema == SchemaUrl.PROMPTFLOW_RUN:
            schema = RunSchema(context=context)
        elif _schema == SchemaUrl.PROMPTFLOW_FLOW:
            schema = FlowSchema(context=context)
        else:
            raise ValidationException(
                message="$schema must be specified correctly for loading component from flow, but got %s" % _schema,
                no_personal_data_message="$schema must be specified for loading component from flow",
                target=cls._get_validation_error_target(),
                error_category=ErrorCategory.USER_ERROR,
            )

        # unlike other component, we should ignore unknown fields in flow to keep init_params clean and avoid
        # too much understanding of flow.dag.yaml & run.yaml
        kwargs["unknown"] = EXCLUDE
        try:
            return schema.load(data, **kwargs)
        except ValidationError as e:
            if raise_original_exception:
                raise e
            msg = "Trying to load data with schema failed. Data:\n%s\nError: %s" % (
                json.dumps(data, indent=4) if isinstance(data, dict) else data,
                json.dumps(e.messages, indent=4),
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=str(e),
                target=cls._get_validation_error_target(),
                error_category=ErrorCategory.USER_ERROR,
            ) from e

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return FlowComponentSchema(context=context)

    # endregion

    # region AdditionalIncludesMixin
    def _get_origin_code_value(self) -> Union[str, os.PathLike, None]:
        if self._code:
            return self._code
        return self._get_flow_definition(self.flow, self.base_path, self._source_path)[0]

    def _fill_back_code_value(self, value: str) -> None:
        if not self._flow_file_name:
            _, self._flow_file_name = self._get_flow_definition(self.flow, self.base_path, self._source_path)
        self._code = value

    @contextlib.contextmanager
    def _try_build_local_code(self) -> Iterable[Optional[Code]]:
        with super()._try_build_local_code() as code:
            if code and code.path:
                if not (Path(code.path) / ".promptflow" / "flow.tools.json").is_file():
                    raise ValidationException(
                        message="Flow component must be created with a ./promptflow/flow.tools.json, "
                        "please run `pf flow build` to generate it or skip it in your ignore file.",
                        no_personal_data_message="Flow component must be created with a ./promptflow/flow.tools.json, "
                        "please run `pf flow build` to generate it or skip it in your ignore file.",
                        target=self._get_validation_error_target(),
                        error_category=ErrorCategory.USER_ERROR,
                    )
            yield code

    # endregion
