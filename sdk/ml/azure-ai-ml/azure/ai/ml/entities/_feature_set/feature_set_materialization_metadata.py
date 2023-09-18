# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from datetime import datetime, timedelta
from typing import Dict, Optional

from azure.ai.ml._restclient.v2023_08_01_preview.models import JobBase as RestJobBase
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._system_data import SystemData

from .materialization_type import MaterializationType

FeaturestoreJobTypeMap: Dict[str, MaterializationType] = {
    "BackfillMaterialization": MaterializationType.BACKFILL_MATERIALIZATION,
    "RecurrentMaterialization": MaterializationType.RECURRENT_MATERIALIZATION,
}


@experimental
class FeatureSetMaterializationMetadata(RestTranslatableMixin):
    def __init__(
        self,
        *,
        type: MaterializationType,  # pylint: disable=redefined-builtin
        feature_window_start_time: Optional[datetime],
        feature_window_end_time: Optional[datetime],
        name: Optional[str],
        display_name: Optional[str],
        creation_context: Optional[SystemData],
        duration: Optional[timedelta],
        status: Optional[str],
        tags: Optional[Dict[str, str]],
        **kwargs  # pylint: disable=unused-argument
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
    def _from_rest_object(cls, obj: RestJobBase) -> "FeatureSetMaterializationMetadata":
        if not obj:
            return None
        job_properties = obj.properties
        job_type = job_properties.properties.get("azureml.FeatureStoreJobType", None)
        feature_window_start_time = job_properties.properties.get("azureml.FeatureWindowStart", None)
        feature_window_end_time = job_properties.properties.get("azureml.FeatureWindowEnd", None)

        # Currently, the window start/end time that user set from cli is with format: "%Y-%m-%dT%H:%M:%SZ"
        # but during the job processing flow, the time format changed to "%m/%d/%Y %H:%M:%S %z"
        time_format = "%m/%d/%Y %H:%M:%S %z"
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
