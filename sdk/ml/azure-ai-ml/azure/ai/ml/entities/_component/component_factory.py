# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Callable, Dict, Optional, Tuple

from marshmallow import Schema

from azure.ai.ml._restclient.v2022_05_01.models import ComponentVersionData
from azure.ai.ml.constants._common import SOURCE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._component import NodeType, DataTransferTaskType
from azure.ai.ml.entities._component.automl_component import AutoMLComponent
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._component.import_component import ImportComponent
from azure.ai.ml.entities._component.parallel_component import ParallelComponent
from azure.ai.ml.entities._component.pipeline_component import PipelineComponent
from azure.ai.ml.entities._component.spark_component import SparkComponent
from azure.ai.ml.entities._component.datatransfer_component import (
    DataTransferCopyComponent,
    DataTransferImportComponent,
    DataTransferExportComponent,
)
from azure.ai.ml.entities._util import get_type_from_spec


class _ComponentFactory:
    """A class to create component instances from yaml dict or rest objects without hard-coded type check."""

    def __init__(self):
        self._create_instance_funcs = {}
        self._create_schema_funcs = {}

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

    def get_create_funcs(self, yaml_spec: dict) -> Tuple[Callable[..., Component], Callable[[Any], Schema]]:
        """Get registered functions to create instance & its corresponding schema for the given type."""

        _type = get_type_from_spec(yaml_spec, valid_keys=self._create_instance_funcs)
        create_instance_func = self._create_instance_funcs[_type]
        create_schema_func = self._create_schema_funcs[_type]
        return create_instance_func, create_schema_func

    def register_type(
        self,
        _type: str,
        create_instance_func: Callable[..., Component],
        create_schema_func: Callable[[Any], Schema],
    ):
        """Register a new component type.

        :param _type: the type name of the component.
        :type _type: str
        :param create_instance_func: a function to create an instance of the component.
        :type create_instance_func: Callable[..., Component]
        :param create_schema_func: A function to create a schema for the component.
        :type create_schema_func: Callable[[Any], Schema]
        """
        self._create_instance_funcs[_type] = create_instance_func
        self._create_schema_funcs[_type] = create_schema_func

    @classmethod
    def load_from_dict(cls, *, data: Dict, context: Dict, _type: Optional[str] = None, **kwargs) -> Component:
        """Load a component from a yaml dict.

        :param data: the yaml dict.
        :type data: Dict
        :param context: the context of the yaml dict.
        :type context: Dict
        :param _type: the type name of the component. When None, it will be inferred from the yaml dict.
        :type _type: str
        """

        return Component._load(
            data=data,
            yaml_path=context.get(SOURCE_PATH_CONTEXT_KEY, None),
            params_override=[{"type": _type}] if _type is not None else [],
            **kwargs,
        )

    @classmethod
    def load_from_rest(cls, *, obj: ComponentVersionData, _type: Optional[str] = None) -> Component:
        """Load a component from a rest object.

        :param obj: The rest object.
        :type obj: ComponentVersionData
        :param _type: the type name of the component. When None, it will be inferred from the rest object.
        :type _type: str
        """
        if _type is not None:
            obj.properties.component_spec["type"] = _type
        return Component._from_rest_object(obj)


component_factory = _ComponentFactory()
