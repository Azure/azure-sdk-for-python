# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from azure.ai.ml._restclient.v2022_02_01_preview.models import CommandJob as RestCommandJob
from azure.ai.ml._restclient.v2022_02_01_preview.models import JobBaseData
from azure.ai.ml._schema.job.import_job import ImportJobSchema
from azure.ai.ml._utils.utils import is_private_preview_enabled
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.entities._inputs_outputs import Output
from azure.ai.ml.entities._job._input_output_helpers import (
    from_rest_data_outputs,
    from_rest_inputs_to_dataset_literal,
    to_rest_data_outputs,
    to_rest_dataset_literal_inputs,
)
from azure.ai.ml.entities._job.job_io_mixin import JobIOMixin
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import MlException

from .job import Job

# avoid circular import error
if TYPE_CHECKING:
    from azure.ai.ml.entities._builders import Import
    from azure.ai.ml.entities._component.import_component import ImportComponent

module_logger = logging.getLogger(__name__)


class ImportSource(ABC):
    def __init__(
        self,
        *,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
        connection: Optional[str] = None,
    ):
        self.type = type
        self.connection = connection

    @abstractmethod
    def _to_job_inputs(self) -> Dict[str, Optional[str]]:
        pass

    @classmethod
    def _from_job_inputs(cls, job_inputs: Dict[str, str]) -> "ImportSource":
        """Translate job inputs to import source.

        :param job_inputs: The job inputs
        :type job_inputs: Dict[str, str]
        :return: The import source
        :rtype: ImportSource
        """
        type = job_inputs.get("type")  # pylint: disable=redefined-builtin
        connection = job_inputs.get("connection")
        query = job_inputs.get("query")
        path = job_inputs.get("path")

        import_source = (
            DatabaseImportSource(type=type, connection=connection, query=query)
            if query is not None
            else FileImportSource(type=type, connection=connection, path=path)
        )
        return import_source


class DatabaseImportSource(ImportSource):
    def __init__(
        self,
        *,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
        connection: Optional[str] = None,
        query: Optional[str] = None,
    ):
        ImportSource.__init__(
            self,
            type=type,
            connection=connection,
        )
        self.query = query

    def _to_job_inputs(self) -> Dict[str, Optional[str]]:
        """Translate source to command Inputs.

        :return: The job inputs dict
        :rtype: Dict[str, str]
        """
        inputs = {
            "type": self.type,
            "connection": self.connection,
            "query": self.query,
        }
        return inputs


class FileImportSource(ImportSource):
    def __init__(
        self,
        *,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
        connection: Optional[str] = None,
        path: Optional[str] = None,
    ):
        ImportSource.__init__(
            self,
            type=type,
            connection=connection,
        )
        self.path = path

    def _to_job_inputs(self) -> Dict[str, Optional[str]]:
        """Translate source to command Inputs.

        :return: The job inputs dict
        :rtype: Dict[str, str]
        """
        inputs = {
            "type": self.type,
            "connection": self.connection,
            "path": self.path,
        }
        return inputs


class ImportJob(Job, JobIOMixin):
    """Import job.

    :param name: Name of the job.
    :type name: str
    :param description: Description of the job.
    :type description: str
    :param display_name: Display name of the job.
    :type display_name: str
    :param experiment_name:  Name of the experiment the job will be created under.
        If None is provided, default will be set to current directory name.
    :type experiment_name: str
    :param source: Input source parameters to the import job.
    :type source: azure.ai.ml.entities.DatabaseImportSource or FileImportSource
    :param output: output data binding used in the job.
    :type output: azure.ai.ml.Output
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        display_name: Optional[str] = None,
        experiment_name: Optional[str] = None,
        source: Optional[ImportSource] = None,
        output: Optional[Output] = None,
        **kwargs: Any,
    ):
        kwargs[TYPE] = JobType.IMPORT

        Job.__init__(
            self,
            name=name,
            display_name=display_name,
            description=description,
            experiment_name=experiment_name,
            **kwargs,
        )

        self.source = source
        self.output = output

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = ImportJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    def _to_rest_object(self) -> JobBaseData:
        # TODO: Remove in PuP
        if not is_private_preview_enabled():
            msg = JobType.IMPORT + " job not supported."
            raise MlException(message=msg, no_personal_data_message=msg)

        _inputs = self.source._to_job_inputs() if self.source is not None else None  # pylint: disable=protected-access
        if self.compute is None:
            msg = "compute cannot be None."
            raise MlException(message=msg, no_personal_data_message=msg)

        properties = RestCommandJob(
            display_name=self.display_name,
            description=self.description,
            compute_id=self.compute,
            experiment_name=self.experiment_name,
            inputs=to_rest_dataset_literal_inputs(_inputs, job_type=self.type),  # pylint: disable=protected-access
            outputs=to_rest_data_outputs({"output": self.output}),
            # TODO: Remove in PuP with native import job/component type support in MFE/Designer
            # No longer applicable once new import job type is ready on MFE in PuP
            # command and environment are required as we use command type for import
            # command can be random string and the particular environment name here is defined as default in MFE
            #   public const string DefaultEnvironmentName = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu";
            # which is considered valid environment in MFE unless MFE changes current default logic
            # but chance should be very low in PrP
            command="import",
            environment_id=self.compute.replace(
                "/computes/DataFactory", "/environments/AzureML-sklearn-0.24-ubuntu18.04-py37-cpu"
            ),
        )
        result = JobBaseData(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> "ImportJob":
        loaded_data = load_from_dict(ImportJobSchema, data, context, additional_message, **kwargs)
        return ImportJob(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

    @classmethod
    def _load_from_rest(cls, obj: JobBaseData) -> "ImportJob":
        rest_command_job: RestCommandJob = obj.properties
        outputs = from_rest_data_outputs(rest_command_job.outputs)
        inputs = from_rest_inputs_to_dataset_literal(rest_command_job.inputs)

        import_job = ImportJob(
            name=obj.name,
            id=obj.id,
            display_name=rest_command_job.display_name,
            description=rest_command_job.description,
            experiment_name=rest_command_job.experiment_name,
            status=rest_command_job.status,
            creation_context=obj.system_data,
            source=ImportSource._from_job_inputs(inputs),  # pylint: disable=protected-access
            output=outputs["output"] if "output" in outputs else None,
        )
        return import_job

    def _to_component(self, context: Optional[Dict] = None, **kwargs: Any) -> "ImportComponent":
        """Translate a import job to component.

        :param context: Context of import job YAML file.
        :type context: dict
        :return: Translated import component.
        :rtype: ImportComponent
        """
        from azure.ai.ml.entities._component.import_component import ImportComponent

        pipeline_job_dict = kwargs.get("pipeline_job_dict", {})
        context = context or {BASE_PATH_CONTEXT_KEY: Path("import/")}

        _inputs = self.source._to_job_inputs() if self.source is not None else None  # pylint: disable=protected-access

        # Create anonymous command component with default version as 1
        return ImportComponent(
            is_anonymous=True,
            base_path=context[BASE_PATH_CONTEXT_KEY],
            description=self.description,
            source=self._to_inputs(
                inputs=_inputs,  # pylint: disable=protected-access
                pipeline_job_dict=pipeline_job_dict,
            ),
            output=self._to_outputs(outputs={"output": self.output}, pipeline_job_dict=pipeline_job_dict)["output"],
        )

    def _to_node(self, context: Optional[Dict] = None, **kwargs: Any) -> "Import":
        """Translate a import job to a pipeline node.

        :param context: Context of import job YAML file.
        :type context: dict
        :return: Translated import node.
        :rtype: Import
        """
        from azure.ai.ml.entities._builders import Import

        component = self._to_component(context, **kwargs)
        _inputs = self.source._to_job_inputs() if self.source is not None else None  # pylint: disable=protected-access
        return Import(
            component=component,
            compute=self.compute,
            inputs=_inputs,  # pylint: disable=protected-access
            outputs={"output": self.output},
            description=self.description,
            display_name=self.display_name,
            properties=self.properties,
        )
