# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from os import PathLike

from typing import Dict, List, Optional, Union

from azure.ai.ml._utils._arm_id_utils import get_arm_id_object_from_id
from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    FeaturestoreEntityVersion,
    FeaturestoreEntityVersionProperties,
    FeaturestoreEntityContainer,
    FeaturestoreEntityContainerProperties,
)
from azure.ai.ml._utils._experimental import experimental

from azure.ai.ml.entities._assets.asset import Asset
from .data_column import DataColumn


@experimental
class FeaturestoreEntity(Asset):
    def __init__(
        self,
        *,
        name: str,
        version: str,
        index_columns: List[DataColumn],
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs,
    ):
        """FeaturestoreEntity

        :param name: Name of the resource.
        :type name: str
        :param version: Version of the resource.
        :type version: str
        :param index_columns: Specifies index columns.
        :type index_columns: list[~azure.mgmt.machinelearningservices.models.IndexColumn]
        :param description: Description of the resource.
        :type description: str
        :param tags: Tag dictionary. Tags can be added, removed, and updated.
        :type tags: dict[str, str]
        :param properties: The asset property dictionary.
        :type properties: dict[str, str]
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            properties=properties,
            **kwargs,
        )
        self.index_columns = index_columns
        self.version = version
        self.latest_version = None

    def _to_rest_object(self) -> FeaturestoreEntityVersion:
        feature_store_entity_version_properties = FeaturestoreEntityVersionProperties(
            description=self.description,
            index_columns=[column._to_rest_object() for column in self.index_columns],
            tags=self.tags,
            properties=self.properties,
        )
        return FeaturestoreEntityVersion(properties=feature_store_entity_version_properties)

    @classmethod
    def _from_rest_object(cls, rest_obj: FeaturestoreEntityVersion) -> "FeaturestoreEntity":
        rest_object_details: FeaturestoreEntityVersionProperties = rest_obj.properties
        arm_id_object = get_arm_id_object_from_id(rest_obj.id)
        featurestoreEntity = FeaturestoreEntity(
            name=arm_id_object.asset_name,
            version=arm_id_object.asset_version,
            index_columns=[DataColumn._from_rest_object(column) for column in rest_object_details.index_columns],
            description=rest_object_details.description,
            tags=rest_object_details.tags,
            properties=rest_object_details.properties,
        )
        return featurestoreEntity

    @classmethod
    def _from_container_rest_object(cls, rest_obj: FeaturestoreEntityContainer) -> "FeaturestoreEntity":
        rest_object_details: FeaturestoreEntityContainerProperties = rest_obj.properties
        arm_id_object = get_arm_id_object_from_id(rest_obj.id)
        featurestoreEntity = FeaturestoreEntity(
            name=arm_id_object.asset_name,
            description=rest_object_details.description,
            tags=rest_object_details.tags,
            properties=rest_object_details.properties,
            index_columns=[],
        )
        featurestoreEntity.latest_version = rest_object_details.latest_version
        return featurestoreEntity

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "FeaturestoreEntity":

        return None

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return None
