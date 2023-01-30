# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import copy
import logging
from pathlib import Path
from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import JobBase
from azure.ai.ml._schema.job.data_transfer_job import DataTransferJobSchema
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, LOCAL_COMPUTE_PROPERTY, LOCAL_COMPUTE_TARGET, TYPE
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job._input_output_helpers import (
    from_rest_data_outputs,
    from_rest_inputs_to_dataset_literal,
    to_rest_data_outputs,
    to_rest_dataset_literal_inputs,
    validate_inputs_for_command,
)
from azure.ai.ml.entities._job.job_service import JobService
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from ..job import Job
from ..job_io_mixin import JobIOMixin
from ..parameterized_command import ParameterizedCommand

module_logger = logging.getLogger(__name__)


class DataTransferJob(Job, ParameterizedCommand, JobIOMixin):
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
        **kwargs,
    ):
        kwargs[TYPE] = JobType.DATA_TRANSFER
        self._parameters = kwargs.pop("parameters", {})

        super().__init__(**kwargs)

    @property
    def parameters(self) -> Dict[str, str]:
        """MLFlow parameters.

        :return: MLFlow parameters logged in job.
        :rtype: Dict[str, str]
        """
        return self._parameters

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return DataTransferJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

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
        pass

    def _to_rest_object(self) -> JobBase:
        # Todo: need update rest api
        self._validate()


class DataTransferCopyJob(DataTransferJob):
    def __init__(
        self,
        *,
        inputs: Optional[Dict[str, Union[Input, str]]] = None,
        outputs: Optional[Dict[str, Union[Output]]] = None,
        task: str = None,
        data_copy_mode: str = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.outputs = outputs
        self.inputs = inputs
        self.task = task
        self.data_copy_mode = data_copy_mode

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "CommandJob":
        loaded_data = load_from_dict(DataTransferJobSchema, data, context, additional_message, **kwargs)
        return DataTransferCopyJob(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

    def _to_component(self, context: Optional[Dict] = None, **kwargs):
        """Translate a data transfer copy job to component.

        :param context: Context of data transfer job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated data transfer copy component.
        """
        from azure.ai.ml.entities._component.datatransfer_component import DataTransferCopyComponent

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
            task=self.task,
            data_copy_mode=self.data_copy_mode
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
    def __init__(self):
        pass


class DataTransferExportJob(DataTransferJob):
    def __init__(self):
        pass
