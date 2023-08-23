# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Dict, List, Optional, Union

from marshmallow import Schema

from azure.ai.ml._restclient.v2022_10_01_preview.models import JobBase
from azure.ai.ml._schema.job.data_transfer_job import (
    DataTransferCopyJobSchema,
    DataTransferImportJobSchema,
    DataTransferExportJobSchema,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._component import (
    NodeType,
    ExternalDataType,
    DataTransferTaskType,
)
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.data_transfer.data_transfer_job import (
    DataTransferCopyJob,
    DataTransferImportJob,
    DataTransferExportJob,
)
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AssetTypes
from azure.ai.ml.exceptions import (
    ErrorCategory,
    ErrorTarget,
    ValidationErrorType,
    ValidationException,
)
from azure.ai.ml.data_index import DataIndex


from ..._schema import PathAwareSchema
from .._util import (
    convert_ordered_dict_to_dict,
    load_from_dict,
    validate_attribute_type,
)
from .base_node import BaseNode
from .._job.pipeline._io import NodeOutput

module_logger = logging.getLogger(__name__)

# TODO: Decide if need to clone DataTransferImportComponent defs for DataIndex
#from azure.ai.ml.entities._component.dataindex_component import DataIndexComponent
# For now just using registry published components
DataIndexComponent = str


def _build_data_index(io_dict: Union[Dict, DataIndex]):
    if io_dict is None:
        return io_dict
    if isinstance(io_dict, DataIndex):
        component_io = io_dict
    else:
        if isinstance(io_dict, dict):
            component_io = DataIndex(**io_dict) 
        else:
            msg = "data_index only support dict and DataIndex"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.DATA,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

    return component_io


class DataIngestionNode(BaseNode):
    """Base class for data index node.

    You should not instantiate this class directly. Instead, you should
    create from builder function: index_data.

    :param component: Id of the data transfer built in component to be run for the step
    :type component: str
    :param data_index: The data configuration
    :type data_index: Union[Dict, DataIndex]
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: Dict[str, Union[str, Output, dict]]
    :param name: Name of the data index.
    :type name: str
    :param description: Description of the data index.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param display_name: Display name of the job.
    :type display_name: str
    :param experiment_name:  Name of the experiment the job will be created under,
        if None is provided, default will be set to current directory name.
    :type experiment_name: str
    :param compute: The compute target the job runs on.
    :type compute: str
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if DataIndex cannot be successfully validated.
        Details will be provided in the error message.
    """

    def __init__(
        self,
        *,
        component: Union[str, DataIndexComponent],
        compute: Optional[str] = None,
        #inputs: Optional[Dict[str, Union[NodeOutput, Input, str]]] = None,
        #data_index: Optional[Union[Dict, DataIndex]] = None,
        input_data: Input, # Data?
        chunk_size: int,
        chunk_overlap: int,
        embeddings_model: str,
        embeddings_dataset_name: str,
        data_source_url: Optional[str] = None,
        document_path_replacement_regex: Optional[str] = None,
        embeddings_connection: Optional[str] = None,
        embeddings_container: Optional[str] = None,
        outputs: Optional[Dict[str, Union[str, Output]]] = None,
        **kwargs,
    ):
        # resolve normal dict to dict[str, JobService]
        kwargs.pop("type", None)
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())
        super().__init__(
            type=NodeType.PIPELINE,
            inputs={
                "input_data": input_data,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "embeddings_model": embeddings_model,
                "embeddings_dataset_name": embeddings_dataset_name,
                "data_source_url": data_source_url,
                "document_path_replacement_regex": document_path_replacement_regex,
                "embeddings_connection": embeddings_connection,
                "embeddings_container": embeddings_container,
            },
            outputs=outputs,
            component=component,
            compute=compute,
            **kwargs,
        )
        # init mark for _AttrDict
        self._init = True
        # self.task = DataTransferTaskType.IMPORT_DATA
        is_component = isinstance(component, DataIndexComponent)
        # if is_component:
        #     self.task = component.task or self.task
        #self.data_index = _build_data_index(data_index)
        self._init = False

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "component": (str, DataIndexComponent),
        }

    @classmethod
    def _load_from_rest_job(cls, obj: JobBase) -> "DataIngestionNode":
        # Todo: need update rest api
        raise NotImplementedError("Not support submit standalone job for now")

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "DataIngestionNode":
        raise NotImplementedError("[DataIndexCogSearch._load_from_dict] Not support submit standalone job for now")
        from .data_index_func import index_data

        loaded_data = load_from_dict(DataTransferImportJobSchema, data, context, additional_message, **kwargs)
        data_index_job = index_data(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

        return data_index_job

    @classmethod
    def _get_supported_outputs_types(cls):
        return str, Output

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        raise NotImplementedError("[DataIndexCogSearch._customized_validate]")
        from azure.ai.ml._schema.pipeline import DataTransferImportSchema

        return DataTransferImportSchema(context=context)

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        raise NotImplementedError("[DataIndexCogSearch._customized_validate]")
        return ["type", "data_index"]

    @property
    def component(self) -> Union[str, DataIndexComponent]:
        return self._component

    def _customized_validate(self):
        raise NotImplementedError("[DataIndexCogSearch._customized_validate]")
        result = super()._customized_validate()
        if self.source is None:
            result.append_error(
                yaml_path="source",
                message="Source is a required field for import data task in DataTransfer job",
            )
        if len(self.outputs) != 1 or list(self.outputs.keys())[0] != "sink":
            result.append_error(
                yaml_path="outputs.sink",
                message="Outputs field only support one output called sink in import task",
            )
        if "sink" in self.outputs and isinstance(self.outputs["sink"]._data, Output):
            sink_output = self.outputs["sink"]._data
            if (self.source.type == ExternalDataType.DATABASE and sink_output.type != AssetTypes.MLTABLE) or (
                self.source.type == ExternalDataType.FILE_SYSTEM and sink_output.type != AssetTypes.URI_FOLDER
            ):
                result.append_error(
                    yaml_path="outputs.sink.type",
                    message="Outputs field only support type {} for {} and {} for {}".format(
                        AssetTypes.MLTABLE,
                        ExternalDataType.DATABASE,
                        AssetTypes.URI_FOLDER,
                        ExternalDataType.FILE_SYSTEM,
                    ),
                )
        return result

    def _to_rest_object(self, **kwargs) -> dict:
        raise NotImplementedError("[DataIndexCogSearch._to_rest_object]")
        rest_obj = super()._to_rest_object(**kwargs)
        for key, value in {
            "componentId": self._get_component_id(),
        }.items():
            if value is not None:
                rest_obj[key] = value
        return convert_ordered_dict_to_dict(rest_obj)

    def _to_job(self) -> DataTransferImportJob:
        raise NotImplementedError("[DataIndexCogSearch._to_job] Not support submit standalone job for now")
        return DataTransferImportJob(
            experiment_name=self.experiment_name,
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            tags=self.tags,
            status=self.status,
            source=self.source,
            outputs=self._job_outputs,
            services=self.services,
            compute=self.compute,
        )

    def _build_inputs(self):
        inputs = super(DataIngestionNode, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value

        return built_inputs
