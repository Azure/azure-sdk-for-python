# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from datetime import datetime, timedelta
from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    FeaturesetJob as RestFeaturesetJob,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml._utils._experimental import experimental

from .materialization_type import _MaterializationType

FeaturestoreJobTypeMap: Dict[str, _MaterializationType] = {
    "BackfillMaterialization": _MaterializationType.BackfillMaterialization,
    "RecurrentMaterialization": _MaterializationType.RecurrentMaterialization,
}


@experimental
class _FeatureSetMaterializationResponse(RestTranslatableMixin):
    def __init__(
        self,
        *,
        type: Union[_MaterializationType, str],  # pylint: disable=redefined-builtin
        feature_window_start_time: Optional[Union[str, datetime]],
        feature_window_end_time: Optional[Union[str, datetime]],
        name: Optional[str],
        display_name: Optional[str],
        creation_context: Optional[SystemData],
        duration: Optional[Union[str, timedelta]],
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
    def _from_rest_object(cls, obj: RestFeaturesetJob) -> "_FeatureSetMaterializationResponse":
        if not obj:
            return None
        return _FeatureSetMaterializationResponse(
            type=FeaturestoreJobTypeMap.get(obj.type, obj.type),
            feature_window_start_time=obj.feature_window.feature_window_start,
            feature_window_end_time=obj.feature_window.feature_window_end,
            name=obj.job_id,
            display_name=obj.display_name,
            creation_context=SystemData(created_at=obj.created_date),
            duration=obj.duration,
            status=obj.status,
            tags=obj.tags,
        )
