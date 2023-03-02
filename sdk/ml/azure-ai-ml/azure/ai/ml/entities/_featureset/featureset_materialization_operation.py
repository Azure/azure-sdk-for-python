# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from datetime import datetime, timedelta
from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    FeaturesetJob as RestFeaturesetJob,
    FeatureWindow,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental

from .materialization_type import MaterializationType
from .creation_context import CreationContext


@experimental
class FeaturesetMaterializationOperation(RestTranslatableMixin):
    def __init__(
        self,
        *,
        type: MaterializationType,
        feature_window_start_time: Optional[Union[str, datetime]],
        feature_window_end_time: Optional[Union[str, datetime]],
        name: Optional[str],
        display_name: Optional[str],
        creation_context: Optional[CreationContext],
        duration: Optional[Union[str, timedelta]],
        status: Optional[str],
        tags: Optional[Dict[str, str]],
        **kwargs
    ):
        """
        :param type: Specifies the feature store job type. Possible values include:
         "RecurrentMaterialization", "BackfillMaterialization".
        :type type: str or ~azure.ai.ml.entities.MaterializationType
        :param feature_window_start_time: Specifies the backfill feature window start time to be materialized.
        :type feature_window_start_time: str or ~datetime.datetime
        :param feature_window_end_time: Specifies the backfill feature window end time to be materialized.
        :type feature_window_end_time: str or ~datetime.datetime
        :param created_date: Specifies the created date.
        :type created_date: str or ~datetime.datetime
        :param display_name: Specifies the display name.
        :type display_name: str
        :param duration: Specifies the duration.
        :type duration: ~datetime.timedelta
        :param experiment_id: Specifies the experiment id.
        :type experiment_id: str
        :param job_id: Specifies the job id.
        :type job_id: str
        :param status: Specifies the job status. Possible values include: "NotStarted", "Starting",
         "Provisioning", "Preparing", "Queued", "Running", "Finalizing", "CancelRequested", "Completed",
         "Failed", "Canceled", "NotResponding", "Paused", "Unknown", "Scheduled".
        :type status: str
        :param tags: A set of tags. Specifies the tags if any.
        :type tags: dict[str, str]
        """
        self.type = type
        self.feature_window_start_time = feature_window_start_time
        self.feature_window_end_time = feature_window_end_time
        self.name = job_name
        self.display_name = display_name
        self.creation_context = creation_context
        self.duration = duration
        self.status = status
        self.tags = tags

    @classmethod
    def _from_rest_object(cls, obj: RestFeaturesetJob) -> "FeaturesetMaterializationOperation":
        if not obj:
            return None
        return FeaturesetMaterializationOperation(
            type=obj.type,
            feature_window_start_time=obj.feature_window.feature_window_start,
            feature_window_end_time=obj.feature_window.feature_window_end,
            name=obj.job_id,
            display_name=obj.display_name,
            creation_context=CreationContext(created_time=obj.created_date),
            duration=obj.duration,
            status=obj.status,
            tags=obj.tags,
        )
