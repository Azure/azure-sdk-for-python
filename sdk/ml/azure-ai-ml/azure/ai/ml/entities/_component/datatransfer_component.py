# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from pathlib import Path
from typing import Dict, Optional, Union

from marshmallow import Schema

from azure.ai.ml._schema.component.data_transfer_component import (
    DataTransferCopyComponentSchema,
    DataTransferImportComponentSchema,
    DataTransferExportComponentSchema,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import COMPONENT_TYPE, AssetTypes
from azure.ai.ml.constants._component import (
    NodeType,
    DataTransferTaskType,
    ExternalDataType,
)
from azure.ai.ml.exceptions import (
    ErrorCategory,
    ErrorTarget,
    ValidationException,
    ValidationErrorType,
)
from azure.ai.ml.entities._inputs_outputs.external_data import Database, FileSystem
from azure.ai.ml.entities._inputs_outputs.output import Output
from ..._schema import PathAwareSchema
from .._util import convert_ordered_dict_to_dict, validate_attribute_type
from .component import Component


class DataTransferComponent(Component):  # pylint: disable=too-many-instance-attributes
    """DataTransfer component version, used to define a data transfer component.

    :param task: task type in data transfer component, possible value is "copy_data", "import_data" and "export_data".
    :type task: str
    :param inputs: Mapping of inputs data bindings used in the job.
    :type inputs: dict
    :param outputs: Mapping of outputs data bindings used in the job,
    :type outputs: dict
    """

    def __init__(
        self,
        *,
        task: str = None,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        **kwargs,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        kwargs[COMPONENT_TYPE] = NodeType.DATA_TRANSFER
        # Set default base path
        if "base_path" not in kwargs:
            kwargs["base_path"] = Path(".")

        super().__init__(
            inputs=inputs,
            outputs=outputs,
            **kwargs,
        )
        self._task = task

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {}

    @property
    def task(self) -> str:
        """Task type of the component.

        :return: Task type of the component.
        :rtype: str
        """
        return self._task

    def _to_dict(self) -> Dict:
        """Dump the data transfer component content into a dictionary."""
        return convert_ordered_dict_to_dict({**self._other_parameter, **super(DataTransferComponent, self)._to_dict()})

    def __str__(self):
        try:
            return self._to_yaml()
        except BaseException:  # pylint: disable=broad-except
            return super(DataTransferComponent, self).__str__()

    @classmethod
    def _build_source_sink(cls, io_dict: Union[Dict, Database, FileSystem]):
        if isinstance(io_dict, Database):
            component_io = Database()
        elif isinstance(io_dict, FileSystem):
            component_io = FileSystem()
        else:
            if isinstance(io_dict, dict):
                data_type = io_dict.pop("type", None)
                if data_type == ExternalDataType.DATABASE:
                    component_io = Database()
                elif data_type == ExternalDataType.FILE_SYSTEM:
                    component_io = FileSystem()
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
                        target=ErrorTarget.COMPONENT,
                        error_category=ErrorCategory.USER_ERROR,
                        error_type=ValidationErrorType.INVALID_VALUE,
                    )
            else:
                msg = "Source or sink only support dict, Database and FileSystem"
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.COMPONENT,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )

        return component_io


@experimental
class DataTransferCopyComponent(DataTransferComponent):
    """DataTransfer copy component version, used to define a data transfer copy component.

    :param data_copy_mode: data copy mode in copy task, possible value is "merge_with_overwrite", "fail_if_conflict".
    :type data_copy_mode: str
    :param inputs: Mapping of inputs data bindings used in the job.
    :type inputs: dict
    :param outputs: Mapping of outputs data bindings used in the job.
    :type outputs: dict
    """

    def __init__(
        self,
        *,
        data_copy_mode: str = None,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        **kwargs,
    ):
        kwargs["task"] = DataTransferTaskType.COPY_DATA
        super().__init__(
            inputs=inputs,
            outputs=outputs,
            **kwargs,
        )

        self._data_copy_mode = data_copy_mode

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return DataTransferCopyComponentSchema(context=context)

    @property
    def data_copy_mode(self) -> str:
        """Data copy mode of the component.

        :return: Data copy mode of the component.
        :rtype: str
        """
        return self._data_copy_mode

    def _customized_validate(self):
        validation_result = super(DataTransferCopyComponent, self)._customized_validate()
        validation_result.merge_with(self._validate_input_output_mapping())
        return validation_result

    def _validate_input_output_mapping(self):
        validation_result = self._create_empty_validation_result()
        inputs_count = len(self.inputs)
        outputs_count = len(self.outputs)
        if outputs_count != 1:
            msg = "Only support single output in {}, but there're {} outputs."
            validation_result.append_error(
                message=msg.format(DataTransferTaskType.COPY_DATA, outputs_count),
                yaml_path="outputs",
            )
        else:
            input_type = None
            output_type = None
            if inputs_count == 1:
                for _, input_data in self.inputs.items():
                    input_type = input_data.type
                for _, output_data in self.outputs.items():
                    output_type = output_data.type
                if input_type is None or output_type is None or input_type != output_type:
                    msg = "Input type {} doesn't exactly match with output type {} in task {}"
                    validation_result.append_error(
                        message=msg.format(input_type, output_type, DataTransferTaskType.COPY_DATA),
                        yaml_path="outputs",
                    )
            elif inputs_count > 1:
                for _, output_data in self.outputs.items():
                    output_type = output_data.type
                if output_type is None or output_type != AssetTypes.URI_FOLDER:
                    msg = "output type {} need to be {} in task {}"
                    validation_result.append_error(
                        message=msg.format(
                            output_type,
                            AssetTypes.URI_FOLDER,
                            DataTransferTaskType.COPY_DATA,
                        ),
                        yaml_path="outputs",
                    )
            else:
                msg = "Inputs must be set in task {}."
                validation_result.append_error(
                    message=msg.format(DataTransferTaskType.COPY_DATA),
                    yaml_path="inputs",
                )
        return validation_result


@experimental
class DataTransferImportComponent(DataTransferComponent):
    """DataTransfer import component version, used to define a data transfer import component.

    :param source: The data source of file system or database
    :type source: dict
    :param outputs: Mapping of outputs data bindings used in the job, default will be an output port with key "sink"
    and type "mltable".
    :type outputs: dict
    """

    def __init__(
        self,
        *,
        source: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        **kwargs,
    ):
        outputs = outputs or {"sink": Output(type=AssetTypes.MLTABLE)}
        kwargs["task"] = DataTransferTaskType.IMPORT_DATA
        super().__init__(
            outputs=outputs,
            **kwargs,
        )

        source = source if source else {}
        self.source = self._build_source_sink(source)

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return DataTransferImportComponentSchema(context=context)

    def __call__(self, *args, **kwargs):
        """Call ComponentVersion as a function and get a Component object."""

        msg = "DataTransfer component is not callable for import task."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.COMPONENT,
            error_category=ErrorCategory.USER_ERROR,
        )


@experimental
class DataTransferExportComponent(DataTransferComponent):  # pylint: disable=too-many-instance-attributes
    """DataTransfer export component version, used to define a data transfer export component.

    :param sink: The sink of external data and databases.
    :type sink: Union[Dict, Database, FileSystem]
    :param inputs: Mapping of inputs data bindings used in the job.
    :type inputs: dict
    """

    def __init__(
        self,
        *,
        inputs: Optional[Dict] = None,
        sink: Optional[Dict] = None,
        **kwargs,
    ):
        kwargs["task"] = DataTransferTaskType.EXPORT_DATA
        super().__init__(
            inputs=inputs,
            **kwargs,
        )

        sink = sink if sink else {}
        self.sink = self._build_source_sink(sink)

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return DataTransferExportComponentSchema(context=context)

    def __call__(self, *args, **kwargs):
        """Call ComponentVersion as a function and get a Component object."""

        msg = "DataTransfer component is not callable for export task."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.COMPONENT,
            error_category=ErrorCategory.USER_ERROR,
        )
