# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from os import PathLike
from pathlib import Path

from typing import Dict, List, Optional, Union

from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    FeaturesetVersion,
    FeaturesetVersionProperties,
    FeaturesetContainer,
    FeaturesetContainerProperties,
)
from azure.ai.ml._schema._feature_set.feature_set_schema import FeatureSetSchema
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._utils._arm_id_utils import AMLNamedArmId, get_arm_id_object_from_id
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import (
    BASE_PATH_CONTEXT_KEY,
    LONG_URI_FORMAT,
    PARAMS_OVERRIDE_KEY,
)
from azure.ai.ml.entities._assets import Artifact
from azure.ai.ml.entities._feature_set.feature_set_specification import FeatureSetSpecification
from azure.ai.ml.entities._feature_set.materialization_settings import MaterializationSettings

from .artifact import ArtifactStorageInfo


@experimental
class FeatureSet(Artifact):
    def __init__(
        self,
        *,
        name: str,
        version: str,
        entities: List[str],
        specification: FeatureSetSpecification,
        stage: Optional[str] = None,
        description: Optional[str] = None,
        materialization_settings: Optional[MaterializationSettings] = None,
        tags: Optional[Dict] = None,
        **kwargs,
    ):
        """FeatureSet

        :param name: Name of the resource.
        :type name: str
        :param version: Version of the resource.
        :type version: str
        :param entities: Specifies list of entities.
        :type entities: list[str]
        :param specification: Specifies the feature spec details.
        :type specification: ~azure.ai.ml.entities.FeatureSetSpecification
        :param description: Description of the resource.
        :type description: str
        :param tags: Tag dictionary. Tags can be added, removed, and updated.
        :type tags: dict[str, str]
        :param materialization_settings: Specifies the materialization settings.
        :type materialization_settings: ~azure.ai.ml.entities.MaterializationSettings
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            path=specification.path,
            **kwargs,
        )
        self.entities = entities
        self.specification = specification
        self.stage = stage
        self.materialization_settings = materialization_settings
        self.latest_version = None

    def _to_rest_object(self) -> FeaturesetVersion:
        featureset_version_properties = FeaturesetVersionProperties(
            description=self.description,
            properties=self.properties,
            tags=self.tags,
            entities=self.entities,
            materialization_settings=self.materialization_settings._to_rest_object()
            if self.materialization_settings
            else None,
            specification=self.specification._to_rest_object(),
            stage=self.stage,
        )
        return FeaturesetVersion(name=self.name, properties=featureset_version_properties)

    @classmethod
    def _from_rest_object(cls, featureset_rest_object: FeaturesetVersion) -> "FeatureSet":
        if not featureset_rest_object:
            return None
        featureset_rest_object_details: FeaturesetVersionProperties = featureset_rest_object.properties
        arm_id_object = get_arm_id_object_from_id(featureset_rest_object.id)
        featureset = FeatureSet(
            id=featureset_rest_object.id,
            name=arm_id_object.asset_name,
            version=arm_id_object.asset_version,
            description=featureset_rest_object_details.description,
            tags=featureset_rest_object_details.tags,
            entities=featureset_rest_object_details.entities,
            materialization_settings=MaterializationSettings._from_rest_object(
                featureset_rest_object_details.materialization_settings
            ),
            specification=FeatureSetSpecification._from_rest_object(featureset_rest_object_details.specification),
            stage=featureset_rest_object_details.stage,
            properties=featureset_rest_object_details.properties,
        )
        return featureset

    @classmethod
    def _from_container_rest_object(cls, rest_obj: FeaturesetContainer) -> "FeatureSet":
        rest_object_details: FeaturesetContainerProperties = rest_obj.properties
        arm_id_object = get_arm_id_object_from_id(rest_obj.id)
        featureset = FeatureSet(
            name=arm_id_object.asset_name,
            description=rest_object_details.description,
            tags=rest_object_details.tags,
            entities=[],
            specification=FeatureSetSpecification(),
            version="",
        )
        featureset.latest_version = rest_object_details.latest_version
        return featureset

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "FeatureSet":
        data = data or {}
        params_override = params_override or []
        base_path = Path(yaml_path).parent if yaml_path else Path("./")
        context = {
            BASE_PATH_CONTEXT_KEY: base_path,
            PARAMS_OVERRIDE_KEY: params_override,
        }
        loaded_schema = load_from_dict(FeatureSetSchema, data, context, **kwargs)
        feature_set = FeatureSet(base_path=base_path, **loaded_schema)
        return feature_set

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return FeatureSetSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _update_path(self, asset_artifact: ArtifactStorageInfo) -> None:
        # if datastore_arm_id is null, capture the full_storage_path
        if not asset_artifact.datastore_arm_id and asset_artifact.full_storage_path:
            self.path = asset_artifact.full_storage_path
        else:
            aml_datastore_id = AMLNamedArmId(asset_artifact.datastore_arm_id)
            self.path = LONG_URI_FORMAT.format(
                aml_datastore_id.subscription_id,
                aml_datastore_id.resource_group_name,
                aml_datastore_id.workspace_name,
                aml_datastore_id.asset_name,
                asset_artifact.relative_path,
            )
            self.specification.path = self.path
