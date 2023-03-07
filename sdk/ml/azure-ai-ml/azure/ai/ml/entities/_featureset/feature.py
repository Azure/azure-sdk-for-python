# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Optional

from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    Feature as RestFeature,
)

from azure.ai.ml.entities._featurestore_entity.data_column_type import DataColumnType


class Feature(object):
    def __init__(self, *, name: str, data_type: DataColumnType, description: Optional[str], **kwargs):
        self.name = name
        self.type = data_type
        self.description = description

    def _from_rest_object(cls, restObj: RestFeature) -> "Feature":
        return Feature(name=restObj.feature_name, type=restObj.data_type, description=restObj.description)
