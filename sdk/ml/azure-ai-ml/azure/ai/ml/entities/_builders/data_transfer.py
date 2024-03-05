# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from marshmallow import Schema

from azure.ai.ml._restclient.v2022_10_01_preview.models import JobBase
from azure.ai.ml._schema.job.data_transfer_job import (
    DataTransferCopyJobSchema,
    DataTransferExportJobSchema,
    DataTransferImportJobSchema,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AssetTypes
from azure.ai.ml.constants._component import DataTransferTaskType, ExternalDataType, NodeType
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._component.datatransfer_component import (
    DataTransferComponent,
    DataTransferCopyComponent,
    DataTransferExportComponent,
    DataTransferImportComponent,
)
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._inputs_outputs.external_data import Database, FileSystem
from azure.ai.ml.entities._job.data_transfer.data_transfer_job import (
    DataTransferCopyJob,
    DataTransferExportJob,
    DataTransferImportJob,
)
from azure.ai.ml.entities._validation.core import MutableValidationResult
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from ..._schema import PathAwareSchema
from .._job.pipeline._io import NodeOutput
from .._util import convert_ordered_dict_to_dict, load_from_dict, validate_attribute_type
from .base_node import BaseNode

module_logger = logging.getLogger(__name__)


def _build_source_sink(io_dict: Optional[Union[Dict, Database, FileSystem]]) -> Optional[Union[Database, FileSystem]]:
    if io_dict is None:
        return io_dict
    if isinstance(io_dict, (Database, FileSystem)):
        component_io = io_dict
    else:
        if isinstance(io_dict, dict):
            data_type = io_dict.pop("type", None)
            if data_type == ExternalDataType.DATABASE:
                component_io = Database(**io_dict)
            elif data_type == ExternalDataType.FILE_SYSTEM:
                component_io = FileSystem(**io_dict)
            else:
                msg = "Type in source or sink only support {} and {}, currently got {}."
                raise ValidationException(
                    message=msg.format(
                        ExternalDataType.DATABASE,
                        ExternalDataType.FILE_SYSTEM,
                        data_type,
                    ),
                    no_personal_data_message=msg.format(
                        ExternalDataType.DATABASE,
                        ExternalDataType.FILE_SYSTEM,
                        "data_type",
                    ),
                    target=ErrorTarget.DATA_TRANSFER_JOB,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
        else:
            msg = "Source or sink only support dict, Database and FileSystem"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.DATA_TRANSFER_JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

    return component_io


class DataTransfer(BaseNode):
    """Base class for data transfer node, used for data transfer component version consumption.

    You should not instantiate this class directly.
    """

    def __init__(
        self,
        *,
        component: Union[str, DataTransferCopyComponent, DataTransferImportComponent],
        compute: Optional[str] = None,
        inputs: Optional[Dict[str, Union[NodeOutput, Input, str]]] = None,
        outputs: Optional[Dict[str, Union[str, Output]]] = None,
        **kwargs: Any,
    ):
        # resolve normal dict to dict[str, JobService]
        kwargs.pop("type", None)
        super().__init__(
            type=NodeType.DATA_TRANSFER,
            inputs=inputs,
            outputs=outputs,
            component=component,
            compute=compute,
            **kwargs,
        )

    @property
    def component(self) -> Union[str, DataTransferComponent]:
        res: Union[str, DataTransferComponent] = self._component
        return res

    @classmethod
    def _load_from_rest_job(cls, obj: JobBase) -> "DataTransfer":
        # Todo: need update rest api
        raise NotImplementedError("Not support submit standalone job for now")

    @classmethod
    def _get_supported_outputs_types(cls) -> Tuple:
        return str, Output

    def _build_inputs(self) -> Dict:
        inputs = super(DataTransfer, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value

        return built_inputs


@experimental
class DataTransferCopy(DataTransfer):
    """Base class for data transfer copy node.

    You should not instantiate this class directly. Instead, you should
    create from builder function: copy_data.

    :param component: Id or instance of the data transfer component/job to be run for the step
    :type component: DataTransferCopyComponent
    :param inputs: Inputs to the data transfer.
    :type inputs: Dict[str, Union[NodeOutput, Input, str]]
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: Dict[str, Union[str, Output, dict]]
    :param name: Name of the data transfer.
    :type name: str
    :param description: Description of the data transfer.
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
    :param data_copy_mode: data copy mode in copy task, possible value is "merge_with_overwrite", "fail_if_conflict".
    :type data_copy_mode: str
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if DataTransferCopy cannot be successfully validated.
        Details will be provided in the error message.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        *,
        component: Union[str, DataTransferCopyComponent],
        compute: Optional[str] = None,
        inputs: Optional[Dict[str, Union[NodeOutput, Input, str]]] = None,
        outputs: Optional[Dict[str, Union[str, Output]]] = None,
        data_copy_mode: Optional[str] = None,
        **kwargs: Any,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())
        super().__init__(
            inputs=inputs,
            outputs=outputs,
            component=component,
            compute=compute,
            **kwargs,
        )
        # init mark for _AttrDict
        self._init = True
        self.task = DataTransferTaskType.COPY_DATA
        self.data_copy_mode = data_copy_mode
        is_component = isinstance(component, DataTransferCopyComponent)
        if is_component:
            _component: DataTransferCopyComponent = cast(DataTransferCopyComponent, component)
            self.task = _component.task or self.task
            self.data_copy_mode = _component.data_copy_mode or self.data_copy_mode
        self._init = False

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "component": (str, DataTransferCopyComponent),
        }

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline import DataTransferCopySchema

        return DataTransferCopySchema(context=context)

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return ["type", "task", "data_copy_mode"]

    def _to_rest_object(self, **kwargs: Any) -> dict:
        rest_obj = super()._to_rest_object(**kwargs)
        for key, value in {
            "componentId": self._get_component_id(),
            "data_copy_mode": self.data_copy_mode,
        }.items():
            if value is not None:
                rest_obj[key] = value
        return cast(dict, convert_ordered_dict_to_dict(rest_obj))

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> Any:
        from .data_transfer_func import copy_data

        loaded_data = load_from_dict(DataTransferCopyJobSchema, data, context, additional_message, **kwargs)
        data_transfer_job = copy_data(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

        return data_transfer_job

    def _to_job(self) -> DataTransferCopyJob:
        return DataTransferCopyJob(
            experiment_name=self.experiment_name,
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            tags=self.tags,
            status=self.status,
            inputs=self._job_inputs,
            outputs=self._job_outputs,
            services=self.services,
            compute=self.compute,
            data_copy_mode=self.data_copy_mode,
        )

    # pylint: disable-next=docstring-missing-param
    def __call__(self, *args: Any, **kwargs: Any) -> "DataTransferCopy":
        """Call DataTransferCopy as a function will return a new instance each time.

        :return: A DataTransferCopy node
        :rtype: DataTransferCopy
        """
        if isinstance(self._component, Component):
            # call this to validate inputs
            node: DataTransferCopy = self._component(*args, **kwargs)
            # merge inputs
            for name, original_input in self.inputs.items():
                if name not in kwargs:
                    # use setattr here to make sure owner of input won't change
                    setattr(node.inputs, name, original_input._data)
                    node._job_inputs[name] = original_input._data
                # get outputs
            for name, original_output in self.outputs.items():
                # use setattr here to make sure owner of input won't change
                if not isinstance(original_output, str):
                    setattr(node.outputs, name, original_output._data)
            self._refine_optional_inputs_with_no_value(node, kwargs)
            # set default values: compute, environment_variables, outputs
            node._name = self.name
            node.compute = self.compute
            node.tags = self.tags
            # Pass through the display name only if the display name is not system generated.
            node.display_name = self.display_name if self.display_name != self.name else None
            return node
        msg = "copy_data can be called as a function only when referenced component is {}, currently got {}."
        raise ValidationException(
            message=msg.format(type(Component), self._component),
            no_personal_data_message=msg.format(type(Component), "self._component"),
            target=ErrorTarget.DATA_TRANSFER_JOB,
            error_type=ValidationErrorType.INVALID_VALUE,
        )


@experimental
class DataTransferImport(DataTransfer):
    """Base class for data transfer import node.

    You should not instantiate this class directly. Instead, you should
    create from builder function: import_data.

    :param component: Id of the data transfer built in component to be run for the step
    :type component: str
    :param source: The data source of file system or database
    :type source: Union[Dict, Database, FileSystem]
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: Dict[str, Union[str, Output, dict]]
    :param name: Name of the data transfer.
    :type name: str
    :param description: Description of the data transfer.
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
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if DataTransferImport cannot be successfully validated.
        Details will be provided in the error message.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        *,
        component: Union[str, DataTransferImportComponent],
        compute: Optional[str] = None,
        source: Optional[Union[Dict, Database, FileSystem]] = None,
        outputs: Optional[Dict[str, Union[str, Output]]] = None,
        **kwargs: Any,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())
        super(DataTransferImport, self).__init__(
            component=component,
            outputs=outputs,
            compute=compute,
            **kwargs,
        )
        # init mark for _AttrDict
        self._init = True
        self.task = DataTransferTaskType.IMPORT_DATA
        is_component = isinstance(component, DataTransferImportComponent)
        if is_component:
            _component: DataTransferImportComponent = cast(DataTransferImportComponent, component)
            self.task = _component.task or self.task
        self.source = _build_source_sink(source)
        self._init = False

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "component": (str, DataTransferImportComponent),
        }

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline import DataTransferImportSchema

        return DataTransferImportSchema(context=context)

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return ["type", "task", "source"]

    def _customized_validate(self) -> MutableValidationResult:
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
        if (
            "sink" in self.outputs
            and not isinstance(self.outputs["sink"], str)
            and isinstance(self.outputs["sink"]._data, Output)
        ):
            sink_output = self.outputs["sink"]._data
            if self.source is not None:

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

    def _to_rest_object(self, **kwargs: Any) -> dict:
        rest_obj = super()._to_rest_object(**kwargs)
        for key, value in {
            "componentId": self._get_component_id(),
        }.items():
            if value is not None:
                rest_obj[key] = value
        return cast(dict, convert_ordered_dict_to_dict(rest_obj))

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> "DataTransferImport":
        from .data_transfer_func import import_data

        loaded_data = load_from_dict(DataTransferImportJobSchema, data, context, additional_message, **kwargs)
        data_transfer_job: DataTransferImport = import_data(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

        return data_transfer_job

    def _to_job(self) -> DataTransferImportJob:
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


@experimental
class DataTransferExport(DataTransfer):
    """Base class for data transfer export node.

    You should not instantiate this class directly. Instead, you should
    create from builder function: export_data.

    :param component: Id of the data transfer built in component to be run for the step
    :type component: str
    :param sink: The sink of external data and databases.
    :type sink: Union[Dict, Database, FileSystem]
    :param inputs: Mapping of input data bindings used in the job.
    :type inputs: Dict[str, Union[NodeOutput, Input, str, Input]]
    :param name: Name of the data transfer.
    :type name: str
    :param description: Description of the data transfer.
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
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if DataTransferExport cannot be successfully validated.
        Details will be provided in the error message.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        *,
        component: Union[str, DataTransferCopyComponent, DataTransferImportComponent],
        compute: Optional[str] = None,
        sink: Optional[Union[Dict, Database, FileSystem]] = None,
        inputs: Optional[Dict[str, Union[NodeOutput, Input, str]]] = None,
        **kwargs: Any,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())
        super(DataTransferExport, self).__init__(
            component=component,
            inputs=inputs,
            compute=compute,
            **kwargs,
        )
        # init mark for _AttrDict
        self._init = True
        self.task = DataTransferTaskType.EXPORT_DATA
        is_component = isinstance(component, DataTransferExportComponent)
        if is_component:
            _component: DataTransferExportComponent = cast(DataTransferExportComponent, component)
            self.task = _component.task or self.task
        self.sink = sink
        self._init = False

    @property
    def sink(self) -> Optional[Union[Dict, Database, FileSystem]]:
        """The sink of external data and databases.

        :return: The sink of external data and databases.
        :rtype: Union[None, Database, FileSystem]
        """
        return self._sink

    @sink.setter
    def sink(self, value: Union[Dict, Database, FileSystem]) -> None:
        self._sink = _build_source_sink(value)

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "component": (str, DataTransferExportComponent),
        }

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline import DataTransferExportSchema

        return DataTransferExportSchema(context=context)

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return ["type", "task", "sink"]

    def _customized_validate(self) -> MutableValidationResult:
        result = super()._customized_validate()
        if self.sink is None:
            result.append_error(
                yaml_path="sink",
                message="Sink is a required field for export data task in DataTransfer job",
            )
        if len(self.inputs) != 1 or list(self.inputs.keys())[0] != "source":
            result.append_error(
                yaml_path="inputs.source",
                message="Inputs field only support one input called source in export task",
            )
        if "source" in self.inputs and isinstance(self.inputs["source"]._data, Input):
            source_input = self.inputs["source"]._data
            if self.sink is not None and not isinstance(self.sink, Dict):
                if (self.sink.type == ExternalDataType.DATABASE and source_input.type != AssetTypes.URI_FILE) or (
                    self.sink.type == ExternalDataType.FILE_SYSTEM and source_input.type != AssetTypes.URI_FOLDER
                ):
                    result.append_error(
                        yaml_path="inputs.source.type",
                        message="Inputs field only support type {} for {} and {} for {}".format(
                            AssetTypes.URI_FILE,
                            ExternalDataType.DATABASE,
                            AssetTypes.URI_FOLDER,
                            ExternalDataType.FILE_SYSTEM,
                        ),
                    )

        return result

    def _to_rest_object(self, **kwargs: Any) -> dict:
        rest_obj = super()._to_rest_object(**kwargs)
        for key, value in {
            "componentId": self._get_component_id(),
        }.items():
            if value is not None:
                rest_obj[key] = value
        return cast(dict, convert_ordered_dict_to_dict(rest_obj))

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> "DataTransferExport":
        from .data_transfer_func import export_data

        loaded_data = load_from_dict(DataTransferExportJobSchema, data, context, additional_message, **kwargs)
        data_transfer_job: DataTransferExport = export_data(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

        return data_transfer_job

    def _to_job(self) -> DataTransferExportJob:
        return DataTransferExportJob(
            experiment_name=self.experiment_name,
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            tags=self.tags,
            status=self.status,
            sink=self.sink,
            inputs=self._job_inputs,
            services=self.services,
            compute=self.compute,
        )
