# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from datetime import datetime
from typing import Any, Optional

from azure.ai.ml._restclient.v2023_10_01.models import FeatureWindow as RestFeatureWindow
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class FeatureWindow(RestTranslatableMixin):
    """Feature window
    :keyword feature_window_end: Specifies the feature window end time.
    :paramtype feature_window_end: ~datetime.datetime
    :keyword feature_window_start: Specifies the feature window start time.
    :paramtype feature_window_start: ~datetime.datetime
    """

    # pylint: disable=unused-argument
    def __init__(self, *, feature_window_start: datetime, feature_window_end: datetime, **kwargs: Any) -> None:
        self.feature_window_start = feature_window_start
        self.feature_window_end = feature_window_end

    def _to_rest_object(self) -> RestFeatureWindow:
        return RestFeatureWindow(
            feature_window_start=self.feature_window_start, feature_window_end=self.feature_window_end
        )

    @classmethod
    def _from_rest_object(cls, obj: RestFeatureWindow) -> Optional["FeatureWindow"]:
        if not obj:
            return None
        return FeatureWindow(feature_window_start=obj.feature_window_start, feature_window_end=obj.feature_window_end)
