# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Dict

from azure.ai.ml._restclient.runhistory.models import Run
from azure.ai.ml._restclient.v2022_02_01_preview.models import SystemData
from azure.ai.ml._schema.job import BaseJobSchema
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, TYPE, JobType
from azure.ai.ml.entities._util import load_from_dict

from .job import Job

module_logger = logging.getLogger(__name__)

"""
TODO[Joe]: This class is temporarily created to handle "Base" job type from the service.
    We will be working on a more granular job type for pipeline child jobs in the future.
    Spec Ref: https://github.com/Azure/azureml_run_specification/pull/340
    MFE PR: https://msdata.visualstudio.com/DefaultCollection/Vienna/_workitems/edit/1167303/
"""


class _BaseJob(Job):
    """Base Job, only used in pipeline child jobs.

    :param name: Name of the resource.
    :type name: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param experiment_name:  Name of the experiment the job will be created under, if None is provided, default will be set to current directory name.
    :type experiment_name: str
    :param services: Information on services associated with the job, readonly.
    :type services: dict[str, JobService]
    :param compute: The compute target the job runs on.
    :type compute: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(self, **kwargs):
        kwargs[TYPE] = JobType.BASE

        super().__init__(**kwargs)

    def _to_dict(self) -> Dict:
        return BaseJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "_BaseJob":
        loaded_data = load_from_dict(BaseJobSchema, data, context, additional_message, **kwargs)
        return _BaseJob(**loaded_data)

    @classmethod
    def _load_from_rest(cls, obj: Run) -> "_BaseJob":
        creation_context = SystemData(
            created_by=obj.created_by,
            created_by_type=obj.created_from,
            created_at=obj.created_utc,
            last_modified_by=obj.last_modified_by,
            last_modified_at=obj.last_modified_utc,
        )
        base_job = _BaseJob(
            name=obj.run_id,
            display_name=obj.display_name,
            description=obj.description,
            tags=obj.tags,
            properties=obj.properties,
            experiment_name=obj.experiment_id,
            services=obj.services,
            status=obj.status,
            creation_context=creation_context,
            compute=f"{obj.compute.target}" if obj.compute else None,
        )

        return base_job
