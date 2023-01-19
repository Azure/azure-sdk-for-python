# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from marshmallow import Schema

from azure.ai.ml._schema.component.data_transfer_component import DataTransferCopyComponentSchema, \
    DataTransferImportComponentSchema, DataTransferExportComponentSchema
from azure.ai.ml.constants._common import COMPONENT_TYPE, AssetTypes, BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._component import NodeType, DataTransferTaskType, DataCopyMode
from azure.ai.ml.entities._inputs_outputs import Source, Sink
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

from ..._schema import PathAwareSchema
from .._util import convert_ordered_dict_to_dict, validate_attribute_type
from .component import Component


class DataTransferComponent(Component):  # pylint: disable=too-many-instance-attributes
    """DataTransfer component version, used to define a data transfer component.

    :param task: task type in data transfer component, possible value is "copy_data", "import_data" and "export_data".
    :type task: str
    :param inputs: Mapping of inputs data bindings used in the job.
    :type inputs: dict
    :param outputs: Mapping of outputs data bindings used in the job.
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

        kwargs[COMPONENT_TYPE] = NodeType.DATATRANSFER
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


class DataTransferCopyComponent(DataTransferComponent):
    """DataTransfer copy component version, used to define a data transfer component.


    :param task: task type in data transfer component, possible value is "copy_data", "import_data" and "export_data".
    :type task: str
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
        task: str = None,
        data_copy_mode: str = None,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        **kwargs,
    ):

        super().__init__(
            task=task,
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
        validation_result.merge_with(self._validate_copy())
        return validation_result

    def _validate_copy(self):
        validation_result = self._create_empty_validation_result()
        # todo validate if need add this in builder case
        if self.data_copy_mode is None or self.data_copy_mode not in [DataCopyMode.MERGE_WITH_OVERWRITE,
                                                                      DataCopyMode.FAIL_IF_CONFLICT]:
            msg = f"data_copy_mode need to be set when task type is {DataTransferTaskType.COPY_DATA} and only " \
                  f"support {DataCopyMode.MERGE_WITH_OVERWRITE} and {DataCopyMode.FAIL_IF_CONFLICT} for now"
            validation_result.append_error(message=msg, yaml_path=f"data_copy_mode")
        validation_result.merge_with(self._validate_input_output_mapping())
        return validation_result

    def _validate_input_output_mapping(self):
        validation_result = self._create_empty_validation_result()
        inputs_count = len(self.inputs)
        outputs_count = len(self.outputs)
        if outputs_count != 1:
            msg = f"Only support single output in {DataTransferTaskType.COPY_DATA}, but there're " \
                  f"{outputs_count} outputs."
            validation_result.append_error(message=msg, yaml_path=f"outputs")
        else:
            input_type = None
            output_type = None
            if inputs_count == 1:
                for _, input_data in self.inputs.items():
                    input_type = input_data.type
                for _, output_data in self.outputs.items():
                    output_type = output_data.type
                if input_type is None or output_type is None or input_type != output_type:
                    msg = f"Input type {input_type} doesn't exactly match with output type {output_type} in task " \
                          f"{DataTransferTaskType.COPY_DATA}"
                    validation_result.append_error(message=msg, yaml_path=f"outputs")
            elif inputs_count > 1:
                for _, output_data in self.outputs.items():
                    output_type = output_data.type
                if output_type is None or output_type != AssetTypes.URI_FOLDER:
                    msg = f"output type {output_type} need to be {AssetTypes.URI_FOLDER} in task " \
                          f"{DataTransferTaskType.COPY_DATA}"
                    validation_result.append_error(message=msg, yaml_path=f"outputs")
            else:
                msg = f"Inputs must be set in task {DataTransferTaskType.COPY_DATA}."
                validation_result.append_error(message=msg, yaml_path=f"outputs")
        return validation_result


class DataTransferImportComponent(DataTransferComponent):
    """DataTransfer import component version, used to define a data transfer component.


    :param task: task type in data transfer component, possible value is "copy_data", "import_data" and "export_data".
    :type task: str
    :param source: The data source of file system or database
    :type source: dict
    :param outputs: Mapping of outputs data bindings used in the job.
    :type outputs: dict
    """

    def __init__(
        self,
        *,
        task: str = None,
        source: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        **kwargs,
    ):

        super().__init__(
            task=task,
            outputs=outputs,
            **kwargs,
        )

        self._task = task
        source = source if source else {}
        self._source = self._build_source_sink(source, is_source=True)

    @classmethod
    def _build_source_sink(cls, io_dict: Union[Dict, Source, Sink], is_source: bool):
        component_io = {}
        for name, port in io_dict.items():
            if is_source:
                component_io[name] = port if isinstance(port, Source) else Source(**port)
            else:
                component_io[name] = port if isinstance(port, Sink) else Sink(**port)
        return component_io

    @classmethod
    def _create_schema_for_validation(cls, context, task_type=None) -> Union[PathAwareSchema, Schema]:
        return DataTransferImportComponentSchema(context=context)

    @property
    def source(self) -> Dict:
        """Source of the component.

        :return: Source of the component.
        :rtype: dict
        """
        return self._source

    def _customized_validate(self):
        validation_result = super(DataTransferComponent, self)._customized_validate()
        validation_result.merge_with(self._validate_import())
        return validation_result

    def _validate_import(self):
        validation_result = self._create_empty_validation_result()
        if self.inputs:
            msg = f"inputs field is not a valid filed in task type {DataTransferTaskType.IMPORT_DATA}."
            validation_result.append_error(message=msg, yaml_path=f"inputs")
        return validation_result


class DataTransferExportComponent(DataTransferComponent):  # pylint: disable=too-many-instance-attributes
    """DataTransfer export component version, used to define a data transfer component.


    :param task: task type in data transfer component, possible value is "copy_data", "import_data" and "export_data".
    :type task: str
    :param source: The data source of file system or database
    :type source: dict
    :param outputs: Mapping of outputs data bindings used in the job.
    :type outputs: dict
    """

    def __init__(
        self,
        *,
        task: str = None,
        inputs: Optional[Dict] = None,
        sink: Optional[Dict] = None,
        **kwargs,
    ):

        super().__init__(
            task=task,
            inputs=inputs,
            **kwargs,
        )

        sink = sink if sink else {}
        self._sink = self._build_source_sink(sink, is_source=False)

    @classmethod
    def _build_source_sink(cls, io_dict: Union[Dict, Source, Sink], is_source: bool):
        component_io = {}
        for name, port in io_dict.items():
            if is_source:
                component_io[name] = port if isinstance(port, Source) else Source(**port)
            else:
                component_io[name] = port if isinstance(port, Sink) else Sink(**port)
        return component_io

    @classmethod
    def _create_schema_for_validation(cls, context, task_type=None) -> Union[PathAwareSchema, Schema]:
        return DataTransferExportComponentSchema(context=context)

    @property
    def sink(self) -> Dict:
        """Sink of the component.

        :return: Sink of the component.
        :rtype: dict
        """
        return self._sink

    def _customized_validate(self):
        validation_result = super(DataTransferComponent, self)._customized_validate()
        validation_result.merge_with(self._validate_export())
        return validation_result

    def _validate_export(self):
        validation_result = self._create_empty_validation_result()
        if self.outputs:
            msg = f"outputs field is not a valid filed in task type {DataTransferTaskType.EXPORT_DATA}."
            validation_result.append_error(message=msg, yaml_path=f"outputs")
        return validation_result
