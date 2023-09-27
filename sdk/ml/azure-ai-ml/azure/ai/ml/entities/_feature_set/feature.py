# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from typing import Dict, Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import Feature as RestFeature, FeatureProperties

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
        if not obj:
            return None
        feature_rest_object_details: FeatureProperties = obj.properties
        return Feature(
            name=feature_rest_object_details.feature_name,
            data_type=feature_rest_object_details.data_type,
            description=feature_rest_object_details.description,
            tags=feature_rest_object_details.tags,
        )
