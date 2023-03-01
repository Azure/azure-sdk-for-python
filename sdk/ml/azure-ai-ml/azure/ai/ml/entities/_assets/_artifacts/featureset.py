# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, List, Optional


from azure.ai.ml._utils._arm_id_utils import get_arm_id_object_from_id
from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    FeaturesetVersion,
    FeaturesetVersionProperties,
    FeaturesetContainer,
    FeaturesetContainerProperties,
)
from azure.ai.ml.entities._assets import Artifact
from azure.ai.ml.entities import FeaturestoreEntity, FeaturesetSpecification, MaterializationSettings


class Featureset(Artifact):
    """Featureset

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
        description: Optional[str] = None,
        entities: List[str],
        specification: FeaturesetSpecification,
        materialization_settings: Optional[MaterializationSettings] = None,
        stage: Optional[str],
        tags: Optional[Dict] = None,
        properties: Optional[Dict[str, str]] = None,
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
        self.stage = stage
        self.entities = entities
        self.specification = specification
        self.materialization_settings = materialization_settings
        self.latest_version = None

    def _to_rest_object(self) -> FeaturesetVersion:
        featureset_version_properties = FeaturesetVersionProperties(
            description=self.description,
            properties=self.properties,
            tags=self.tags,
            entities=self.entities,
            materialization_settings=self.materialization_settings,
            specification=self.specification,
            stage=self.stage,
        )
        return FeaturesetVersion(properties=featureset_version_properties)

    @classmethod
    def _from_rest_object(cls, featureset_rest_object: FeaturesetVersion) -> "Featureset":
        if not featureset_rest_object:
            return None
        featureset_rest_object_details: FeaturesetVersionProperties = featureset_rest_object.properties
        arm_id_object = get_arm_id_object_from_id(featureset_rest_object.id)
        featureset = Featureset(
            id=featureset_rest_object.id,
            name=arm_id_object.asset_name,
            version=arm_id_object.asset_version,
            description=featureset_rest_object_details.description,
            tags=featureset_rest_object_details.tags,
            properties=featureset_rest_object_details.properties,
            entities=featureset_rest_object_details.entities,
            materialization_settings=MaterializationSettings._from_rest_object(
                featureset_rest_object_details.materialization_settings
            ),
            specification=FeaturesetSpecification._from_rest_object(featureset_rest_object_details.specification),
            stage=featureset_rest_object_details.stage,
        )
        return featureset

    @classmethod
    def _from_container_rest_object(cls, rest_obj: FeaturesetContainer) -> "Featureset":
        rest_object_details: FeaturesetContainerProperties = rest_obj.properties
        arm_id_object = get_arm_id_object_from_id(rest_obj.id)
        featureset = Featureset(
            name=arm_id_object.asset_name,
            version=arm_id_object.asset_version,
            description=rest_object_details.description,
            tags=rest_object_details.tags,
            properties=rest_object_details.properties,
        )
        featureset.latest_version = rest_object_details.latest_version
        return featureset
