# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from pathlib import Path
from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import JobBase
from azure.ai.ml._schema.job.data_transfer_job import (
    DataTransferCopyJobSchema,
    DataTransferExportJobSchema,
    DataTransferImportJobSchema,
)
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.constants._component import (
    DataTransferBuiltinComponentUri,
    DataTransferTaskType,
    ExternalDataType,
)
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._inputs_outputs.external_data import Database, FileSystem
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import (
    ErrorCategory,
    ErrorTarget,
    ValidationErrorType,
    ValidationException,
)

from ..job import Job
from ..job_io_mixin import JobIOMixin

module_logger = logging.getLogger(__name__)


class DataTransferJob(Job, JobIOMixin):
    """DataTransfer job.

    :param name: Name of the job.
    :type name: str
    :param description: Description of the job.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param display_name: Display name of the job.
    :type display_name: str
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param experiment_name:  Name of the experiment the job will be created under.
        If None is provided, default will be set to current directory name.
    :type experiment_name: str
    :param services: Information on services associated with the job, readonly.
    :type services: dict[str, JobService]
    :param inputs: Inputs to the command.
    :type inputs: dict[str, Union[azure.ai.ml.Input, str, bool, int, float]]
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: dict[str, azure.ai.ml.Output]
    :param compute: The compute target the job runs on.
    :type compute: str
    :param task: task type in data transfer component, possible value is "copy_data".
    :type task: str
    :param data_copy_mode: data copy mode in copy task, possible value is "merge_with_overwrite", "fail_if_conflict".
    :type data_copy_mode: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        task: str,
        **kwargs,
    ):
        kwargs[TYPE] = JobType.DATA_TRANSFER
        self._parameters = kwargs.pop("parameters", {})
        super().__init__(**kwargs)
        self.task = task

    @property
    def parameters(self) -> Dict[str, str]:
        """MLFlow parameters.

        :return: MLFlow parameters logged in job.
        :rtype: Dict[str, str]
        """
        return self._parameters

    def _validate(self) -> None:
        if self.compute is None:
            msg = "compute is required"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )

    @classmethod
    def _load_from_rest(cls, obj: JobBase) -> "DataTransferJob":
        # Todo: need update rest api
        raise NotImplementedError("Not support submit standalone job for now")

    def _to_rest_object(self) -> JobBase:
        # Todo: need update rest api
        raise NotImplementedError("Not support submit standalone job for now")

    @classmethod
    def _build_source_sink(cls, io_dict: Union[Dict, Database, FileSystem]):
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


class DataTransferCopyJob(DataTransferJob):
    def __init__(
        self,
        *,
        inputs: Optional[Dict[str, Union[Input, str]]] = None,
        outputs: Optional[Dict[str, Union[Output]]] = None,
        data_copy_mode: str = None,
        **kwargs,
    ):
        kwargs["task"] = DataTransferTaskType.COPY_DATA
        super().__init__(**kwargs)

        self.outputs = outputs
        self.inputs = inputs
        self.data_copy_mode = data_copy_mode

    def _to_dict(self) -> Dict:
        return DataTransferCopyJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "DataTransferCopyJob":
        loaded_data = load_from_dict(DataTransferCopyJobSchema, data, context, additional_message, **kwargs)
        return DataTransferCopyJob(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

    def _to_component(self, context: Optional[Dict] = None, **kwargs):
        """Translate a data transfer copy job to component.

        :param context: Context of data transfer job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated data transfer copy component.
        """
        from azure.ai.ml.entities._component.datatransfer_component import (
            DataTransferCopyComponent,
        )

        pipeline_job_dict = kwargs.get("pipeline_job_dict", {})
        context = context or {BASE_PATH_CONTEXT_KEY: Path("./")}

        # Create anonymous command component with default version as 1
        return DataTransferCopyComponent(
            tags=self.tags,
            is_anonymous=True,
            base_path=context[BASE_PATH_CONTEXT_KEY],
            description=self.description,
            inputs=self._to_inputs(inputs=self.inputs, pipeline_job_dict=pipeline_job_dict),
            outputs=self._to_outputs(outputs=self.outputs, pipeline_job_dict=pipeline_job_dict),
            data_copy_mode=self.data_copy_mode,
        )

    def _to_node(self, context: Optional[Dict] = None, **kwargs):
        """Translate a data transfer copy job to a pipeline node.

        :param context: Context of data transfer job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated data transfer component.
        """
        from azure.ai.ml.entities._builders import DataTransferCopy

        component = self._to_component(context, **kwargs)

        return DataTransferCopy(
            component=component,
            compute=self.compute,
            # Need to supply the inputs with double curly.
            inputs=self.inputs,
            outputs=self.outputs,
            description=self.description,
            tags=self.tags,
            display_name=self.display_name,
        )


class DataTransferImportJob(DataTransferJob):
    def __init__(
        self,
        *,
        outputs: Optional[Dict[str, Union[Output]]] = None,
        source: Optional[Union[Dict, Database, FileSystem]] = None,
        **kwargs,
    ):
        kwargs["task"] = DataTransferTaskType.IMPORT_DATA
        super().__init__(**kwargs)

        self.outputs = outputs
        self.source = self._build_source_sink(source)

    def _to_dict(self) -> Dict:
        return DataTransferImportJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "DataTransferImportJob":
        loaded_data = load_from_dict(DataTransferImportJobSchema, data, context, additional_message, **kwargs)
        return DataTransferImportJob(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

    def _to_component(self, context: Optional[Dict] = None, **kwargs):
        """Translate a data transfer import job to component.

        :param context: Context of data transfer job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated data transfer import component.
        """

        if self.source.type == ExternalDataType.DATABASE:
            component = DataTransferBuiltinComponentUri.IMPORT_DATABASE
        else:
            component = DataTransferBuiltinComponentUri.IMPORT_FILE_SYSTEM

        return component

    def _to_node(self, context: Optional[Dict] = None, **kwargs):
        """Translate a data transfer import job to a pipeline node.

        :param context: Context of data transfer job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated data transfer import node.
        """
        from azure.ai.ml.entities._builders import DataTransferImport

        component = self._to_component(context, **kwargs)

        return DataTransferImport(
            component=component,
            compute=self.compute,
            source=self.source,
            outputs=self.outputs,
            description=self.description,
            tags=self.tags,
            display_name=self.display_name,
            properties=self.properties,
        )


class DataTransferExportJob(DataTransferJob):
    def __init__(
        self,
        *,
        inputs: Optional[Dict[str, Union[Input]]] = None,
        sink: Optional[Union[Dict, Database, FileSystem]] = None,
        **kwargs,
    ):
        kwargs["task"] = DataTransferTaskType.EXPORT_DATA
        super().__init__(**kwargs)

        self.inputs = inputs
        self.sink = self._build_source_sink(sink)

    def _to_dict(self) -> Dict:
        return DataTransferExportJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "DataTransferExportJob":
        loaded_data = load_from_dict(DataTransferExportJobSchema, data, context, additional_message, **kwargs)
        return DataTransferExportJob(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

    def _to_component(self, context: Optional[Dict] = None, **kwargs):
        """Translate a data transfer export job to component.

        :param context: Context of data transfer job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated data transfer export component.
        """
        if self.sink.type == ExternalDataType.DATABASE:
            component = DataTransferBuiltinComponentUri.EXPORT_DATABASE
        else:
            msg = "Sink is a required field for export data task and we don't support exporting file system for now."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.DATA_TRANSFER_JOB,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        return component

    def _to_node(self, context: Optional[Dict] = None, **kwargs):
        """Translate a data transfer export job to a pipeline node.

        :param context: Context of data transfer job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated data transfer export node.
        """
        from azure.ai.ml.entities._builders import DataTransferExport

        component = self._to_component(context, **kwargs)

        return DataTransferExport(
            component=component,
            compute=self.compute,
            sink=self.sink,
            inputs=self.inputs,
            description=self.description,
            tags=self.tags,
            display_name=self.display_name,
            properties=self.properties,
        )
