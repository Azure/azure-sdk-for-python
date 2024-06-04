# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Callable, Dict, Optional, Tuple

from marshmallow import Schema

from ..._restclient.v2022_10_01.models import ComponentVersion
from ..._utils.utils import is_internal_component_data
from ...constants._common import SOURCE_PATH_CONTEXT_KEY
from ...constants._component import DataTransferTaskType, NodeType
from ...entities._component.automl_component import AutoMLComponent
from ...entities._component.command_component import CommandComponent
from ...entities._component.component import Component
from ...entities._component.datatransfer_component import (
    DataTransferCopyComponent,
    DataTransferExportComponent,
    DataTransferImportComponent,
)
from ...entities._component.import_component import ImportComponent
from ...entities._component.parallel_component import ParallelComponent
from ...entities._component.pipeline_component import PipelineComponent
from ...entities._component.spark_component import SparkComponent
from ...entities._util import get_type_from_spec
from .flow import FlowComponent


class _ComponentFactory:
    """A class to create component instances from yaml dict or rest objects without hard-coded type check."""

    def __init__(self) -> None:
        self._create_instance_funcs: Dict = {}
        self._create_schema_funcs: Dict = {}

        self.register_type(
            _type=NodeType.PARALLEL,
            create_instance_func=lambda: ParallelComponent.__new__(ParallelComponent),
            create_schema_func=ParallelComponent._create_schema_for_validation,
        )
        self.register_type(
            _type=NodeType.COMMAND,
            create_instance_func=lambda: CommandComponent.__new__(CommandComponent),
            create_schema_func=CommandComponent._create_schema_for_validation,
        )
        self.register_type(
            _type=NodeType.IMPORT,
            create_instance_func=lambda: ImportComponent.__new__(ImportComponent),
            create_schema_func=ImportComponent._create_schema_for_validation,
        )
        self.register_type(
            _type=NodeType.PIPELINE,
            create_instance_func=lambda: PipelineComponent.__new__(PipelineComponent),
            create_schema_func=PipelineComponent._create_schema_for_validation,
        )
        self.register_type(
            _type=NodeType.AUTOML,
            create_instance_func=lambda: AutoMLComponent.__new__(AutoMLComponent),
            create_schema_func=AutoMLComponent._create_schema_for_validation,
        )
        self.register_type(
            _type=NodeType.SPARK,
            create_instance_func=lambda: SparkComponent.__new__(SparkComponent),
            create_schema_func=SparkComponent._create_schema_for_validation,
        )
        self.register_type(
            _type="_".join([NodeType.DATA_TRANSFER, DataTransferTaskType.COPY_DATA]),
            create_instance_func=lambda: DataTransferCopyComponent.__new__(DataTransferCopyComponent),
            create_schema_func=DataTransferCopyComponent._create_schema_for_validation,
        )

        self.register_type(
            _type="_".join([NodeType.DATA_TRANSFER, DataTransferTaskType.IMPORT_DATA]),
            create_instance_func=lambda: DataTransferImportComponent.__new__(DataTransferImportComponent),
            create_schema_func=DataTransferImportComponent._create_schema_for_validation,
        )

        self.register_type(
            _type="_".join([NodeType.DATA_TRANSFER, DataTransferTaskType.EXPORT_DATA]),
            create_instance_func=lambda: DataTransferExportComponent.__new__(DataTransferExportComponent),
            create_schema_func=DataTransferExportComponent._create_schema_for_validation,
        )

        self.register_type(
            _type=NodeType.FLOW_PARALLEL,
            create_instance_func=lambda: FlowComponent.__new__(FlowComponent),
            create_schema_func=FlowComponent._create_schema_for_validation,
        )

    def get_create_funcs(
        self, yaml_spec: dict, for_load: bool = False
    ) -> Tuple[Callable[..., Component], Callable[[Any], Schema]]:
        """Get registered functions to create an instance and its corresponding schema for the given type.

        :param yaml_spec: The YAML specification.
        :type yaml_spec: dict
        :param for_load: Whether the function is called for loading a component. Defaults to False.
        :type for_load: bool
        :return: A tuple containing the create_instance_func and create_schema_func.
        :rtype: tuple
        """

        _type = get_type_from_spec(yaml_spec, valid_keys=self._create_instance_funcs)
        # SparkComponent and InternalSparkComponent share the same type name, but they are different types.
        if for_load and is_internal_component_data(yaml_spec, raise_if_not_enabled=True) and _type == NodeType.SPARK:
            from azure.ai.ml._internal._schema.node import NodeType as InternalNodeType

            _type = InternalNodeType.SPARK

        create_instance_func = self._create_instance_funcs[_type]
        create_schema_func = self._create_schema_funcs[_type]
        return create_instance_func, create_schema_func

    def register_type(
        self,
        _type: str,
        create_instance_func: Callable[..., Component],
        create_schema_func: Callable[[Any], Schema],
    ) -> None:
        """Register a new component type.

        :param _type: The type name of the component.
        :type _type: str
        :param create_instance_func: A function to create an instance of the component.
        :type create_instance_func: Callable[..., ~azure.ai.ml.entities.Component]
        :param create_schema_func: A function to create a schema for the component.
        :type create_schema_func: Callable[[Any], Schema]
        """
        self._create_instance_funcs[_type] = create_instance_func
        self._create_schema_funcs[_type] = create_schema_func

    @classmethod
    def load_from_dict(cls, *, data: Dict, context: Dict, _type: Optional[str] = None, **kwargs: Any) -> Component:
        """Load a component from a YAML dict.

        :keyword data: The YAML dict.
        :paramtype data: dict
        :keyword context: The context of the YAML dict.
        :paramtype context: dict
        :keyword _type: The type name of the component. When None, it will be inferred from the YAML dict.
        :paramtype _type: str
        :return: The loaded component.
        :rtype: ~azure.ai.ml.entities.Component
        """

        return Component._load(
            data=data,
            yaml_path=context.get(SOURCE_PATH_CONTEXT_KEY, None),
            params_override=[{"type": _type}] if _type is not None else [],
            **kwargs,
        )

    @classmethod
    def load_from_rest(cls, *, obj: ComponentVersion, _type: Optional[str] = None) -> Component:
        """Load a component from a REST object.

        :keyword obj: The REST object.
        :paramtype obj: ComponentVersion
        :keyword _type: The type name of the component. When None, it will be inferred from the REST object.
        :paramtype _type: str
        :return: The loaded component.
        :rtype: ~azure.ai.ml.entities.Component
        """
        if _type is not None:
            obj.properties.component_spec["type"] = _type
        return Component._from_rest_object(obj)


component_factory = _ComponentFactory()
