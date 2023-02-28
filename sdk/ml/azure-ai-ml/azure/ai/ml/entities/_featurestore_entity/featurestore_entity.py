# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, List, Optional

from azure.ai.ml._utils._arm_id_utils import get_arm_id_object_from_id
from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    FeaturestoreEntityVersion,
    FeaturestoreEntityVersionProperties,
)
from azure.ai.ml._utils._experimental import experimental

from azure.ai.ml.entities._assets.asset import Asset
from .data_column import DataColumn


@experimental
class FeaturestoreEntity(Asset):
    """FeaturestoreEntity

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the resource.
    :type version: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param path: The path to the asset on the datastore. This can be local or remote
    :type path: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        index_columns: List[DataColumn],
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            properties=properties,
            **kwargs,
        )
        self.index_columns = index_columns

    @classmethod
    def _from_rest_object(cls, rest_obj: FeaturestoreEntityVersion) -> "FeaturestoreEntity":
        rest_object_details: FeaturestoreEntityVersionProperties = rest_obj.properties
        arm_id_object = get_arm_id_object_from_id(rest_obj.id)
        featurestoreEntity = FeaturestoreEntity(
            name=arm_id_object.asset_name,
            version=arm_id_object.asset_version,
            description=rest_object_details.description,
            tags=rest_object_details.tags,
            properties=rest_object_details.properties,
        )
        return featurestoreEntity
