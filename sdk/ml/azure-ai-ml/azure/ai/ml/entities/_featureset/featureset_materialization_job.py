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

from .materialization_type import MaterializationType


class FeaturesetMaterializationJob(RestTranslatableMixin):
    def __init__(
        self,
        *,
        type: MaterializationType,
        feature_window_start_time: Optional[Union[str, datetime]],
        feature_window_end_time: Optional[Union[str, datetime]],
        job_name: Optional[str],
        experiment_name: Optional[str],
        display_name: Optional[str],
        created_time: Optional[Union[str, datetime]],
        duration: Optional[Union[str, timedelta]],
        job_status: Optional[str],
        tags: Optional[Dict],
        ** kwargs
    ):
        """
        :keyword path: Specifies the spec path.
        :paramtype path: str
        """
        self.type = type
        self.feature_window_start_time = feature_window_start_time
        self.feature_window_end_time = feature_window_end_time
        self.job_name = job_name
        self.experiment_name = experiment_name
        self.display_name = display_name
        self.created_time = created_time
        self.duration = duration
        self.job_status = job_status
        self.tags = tags

    def _to_rest_object(self) -> "RestFeaturesetJob":
        return RestFeaturesetJob(
            feature_window=FeatureWindow(
                feature_window_start=self.feature_window_start_time,
                feature_window_end=self.feature_window_end_time
            ),
            created_date=self.created_time,  # str to datetime
            display_name=self.display_name,
            duration=self.duration, # str to timedelta
            

        )

    @classmethod
    def _from_rest_object(cls, obj: RestFeaturesetJob) -> "FeaturesetMaterializationJob":
        if not obj:
            return None
        return FeaturesetMaterializationJob(path=obj.path)
