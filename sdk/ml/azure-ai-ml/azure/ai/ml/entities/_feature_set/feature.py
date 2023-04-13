# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from typing import Dict, Optional

from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    Feature as RestFeature,
)

from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._feature_store_entity.data_column_type import DataColumnType
from azure.ai.ml._utils._experimental import experimental


@experimental
class Feature(RestTranslatableMixin):
    def __init__(
        self,
        *,
        name: str,
        data_type: DataColumnType,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        self.name = name
        self.data_type = data_type
        self.description = description
        self.tags = tags

    @classmethod
    def _from_rest_object(cls, obj: RestFeature) -> "Feature":
        return Feature(
            name=obj.feature_name,
            data_type=obj.data_type,
            description=obj.description,
            tags=obj.tags,
        )
