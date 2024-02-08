# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from typing import Any, Dict, Optional

from azure.ai.ml._restclient.v2023_10_01.models import Feature as RestFeature
from azure.ai.ml._restclient.v2023_10_01.models import FeatureProperties
from azure.ai.ml.entities._feature_store_entity.data_column_type import DataColumnType
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class Feature(RestTranslatableMixin):
    """Feature

    :param name: The name of the feature.
    :type name: str
    :param data_type: The data type of the feature.
    :type data_type: ~azure.ai.ml.entities.DataColumnType
    :param description: The description of the feature. Defaults to None.
    :type description: Optional[str]
    :param tags: Tag dictionary. Tags can be added, removed, and updated. Defaults to None.
    :type tags: Optional[dict[str, str]]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: str,
        data_type: DataColumnType,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ):
        self.name = name
        self.data_type = data_type
        self.description = description
        self.tags = tags

    @classmethod
    def _from_rest_object(cls, obj: RestFeature) -> Optional["Feature"]:
        if not obj:
            return None
        feature_rest_object_details: FeatureProperties = obj.properties
        return Feature(
            name=feature_rest_object_details.feature_name,
            data_type=feature_rest_object_details.data_type,
            description=feature_rest_object_details.description,
            tags=feature_rest_object_details.tags,
        )
