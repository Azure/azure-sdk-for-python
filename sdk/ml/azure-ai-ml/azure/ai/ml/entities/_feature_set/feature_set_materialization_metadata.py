# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from azure.ai.ml._restclient.v2023_10_01.models import JobBase as RestJobBase
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._system_data import SystemData

from .materialization_type import MaterializationType

FeaturestoreJobTypeMap: Dict[str, MaterializationType] = {
    "BackfillMaterialization": MaterializationType.BACKFILL_MATERIALIZATION,
    "RecurrentMaterialization": MaterializationType.RECURRENT_MATERIALIZATION,
}


class FeatureSetMaterializationMetadata(RestTranslatableMixin):
    """Feature Set Materialization Metadata

    :param type: The type of the materialization job.
    :type type: MaterializationType
    :param feature_window_start_time: The feature window start time for the feature set materialization job.
    :type feature_window_start_time: Optional[datetime]
    :param feature_window_end_time: The feature window end time for the feature set materialization job.
    :type feature_window_end_time: Optional[datetime]
    :param name: The name of the feature set materialization job.
    :type name: Optional[str]
    :param display_name: The display name for the feature set materialization job.
    :type display_name: Optional[str]
    :param creation_context: The creation context of the feature set materialization job.
    :type creation_context: Optional[~azure.ai.ml.entities.SystemData]
    :param duration: current time elapsed for feature set materialization job.
    :type duration: Optional[~datetime.timedelta]
    :param status: The status of the feature set materialization job.
    :type status: Optional[str]
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: Optional[dict[str, str]]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        # pylint: disable=redefined-builtin
        type: Optional[MaterializationType],
        feature_window_start_time: Optional[datetime],
        feature_window_end_time: Optional[datetime],
        name: Optional[str],
        display_name: Optional[str],
        creation_context: Optional[SystemData],
        duration: Optional[timedelta],
        status: Optional[str],
        tags: Optional[Dict[str, str]],
        # pylint: disable=unused-argument
        **kwargs: Any,
    ):
        self.type = type
        self.feature_window_start_time = feature_window_start_time
        self.feature_window_end_time = feature_window_end_time
        self.name = name
        self.display_name = display_name
        self.creation_context = creation_context
        self.duration = duration
        self.status = status
        self.tags = tags

    @classmethod
    def _from_rest_object(cls, obj: RestJobBase) -> Optional["FeatureSetMaterializationMetadata"]:
        if not obj:
            return None
        job_properties = obj.properties
        job_type = job_properties.properties.get("azureml.FeatureStoreJobType", None)
        feature_window_start_time = job_properties.properties.get("azureml.FeatureWindowStart", None)
        feature_window_end_time = job_properties.properties.get("azureml.FeatureWindowEnd", None)

        time_format = "%Y-%m-%dT%H:%M:%SZ"
        feature_window_start_time = (
            datetime.strptime(feature_window_start_time, time_format) if feature_window_start_time else None
        )
        feature_window_end_time = (
            datetime.strptime(feature_window_end_time, time_format) if feature_window_end_time else None
        )

        return FeatureSetMaterializationMetadata(
            type=FeaturestoreJobTypeMap.get(job_type),
            feature_window_start_time=feature_window_start_time,
            feature_window_end_time=feature_window_end_time,
            name=obj.name,
            display_name=job_properties.display_name,
            creation_context=SystemData(created_at=obj.system_data.created_at),
            status=job_properties.status,
            tags=job_properties.tags,
            duration=None,
        )
