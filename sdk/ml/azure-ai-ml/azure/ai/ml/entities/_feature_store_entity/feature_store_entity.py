# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from azure.ai.ml._restclient.v2023_10_01.models import (
    FeaturestoreEntityContainer,
    FeaturestoreEntityContainerProperties,
    FeaturestoreEntityVersion,
    FeaturestoreEntityVersionProperties,
)
from azure.ai.ml._schema._feature_store_entity.feature_store_entity_schema import FeatureStoreEntitySchema
from azure.ai.ml._utils._arm_id_utils import get_arm_id_object_from_id
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._assets.asset import Asset
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from .data_column import DataColumn


class FeatureStoreEntity(Asset):
    """Feature Store Entity

    :param name: The name of the feature store entity resource.
    :type name: str
    :param version: The version of the feature store entity resource.
    :type version: str
    :param index_columns: Specifies index columns of the feature-store entity resource.
    :type index_columns: list[~azure.ai.ml.entities.DataColumn]
    :param stage: The feature store entity stage. Allowed values: Development, Production, Archived.
        Defaults to "Development".
    :type stage: Optional[str]
    :param description: The description of the feature store entity resource. Defaults to None.
    :type description: Optional[str]
    :param tags: Tag dictionary. Tags can be added, removed, and updated. Defaults to None.
    :type tags: Optional[dict[str, str]]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    :raises ValidationException: Raised if stage is specified and is not valid.

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_featurestore.py
            :start-after: [START configure_feature_store_entity]
            :end-before: [END configure_feature_store_entity]
            :language: Python
            :dedent: 8
            :caption: Configuring a Feature Store Entity
    """

    def __init__(
        self,
        *,
        name: str,
        version: str,
        index_columns: List[DataColumn],
        stage: Optional[str] = "Development",
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            **kwargs,
        )
        if stage and stage not in ["Development", "Production", "Archived"]:
            msg = f"Stage must be Development, Production, or Archived, found {stage}"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_type=ValidationErrorType.INVALID_VALUE,
                target=ErrorTarget.FEATURE_STORE_ENTITY,
                error_category=ErrorCategory.USER_ERROR,
            )
        self.index_columns = index_columns
        self.version = version
        self.latest_version = None
        self.stage = stage

    def _to_rest_object(self) -> FeaturestoreEntityVersion:
        feature_store_entity_version_properties = FeaturestoreEntityVersionProperties(
            description=self.description,
            index_columns=[column._to_rest_object() for column in self.index_columns],
            tags=self.tags,
            properties=self.properties,
            stage=self.stage,
        )
        return FeaturestoreEntityVersion(properties=feature_store_entity_version_properties)

    @classmethod
    def _from_rest_object(cls, rest_obj: FeaturestoreEntityVersion) -> "FeatureStoreEntity":
        rest_object_details: FeaturestoreEntityVersionProperties = rest_obj.properties
        arm_id_object = get_arm_id_object_from_id(rest_obj.id)
        featurestoreEntity = FeatureStoreEntity(
            name=arm_id_object.asset_name,
            version=arm_id_object.asset_version,
            index_columns=[DataColumn._from_rest_object(column) for column in rest_object_details.index_columns],
            stage=rest_object_details.stage,
            description=rest_object_details.description,
            tags=rest_object_details.tags,
        )
        return featurestoreEntity

    @classmethod
    def _from_container_rest_object(cls, rest_obj: FeaturestoreEntityContainer) -> "FeatureStoreEntity":
        rest_object_details: FeaturestoreEntityContainerProperties = rest_obj.properties
        arm_id_object = get_arm_id_object_from_id(rest_obj.id)
        featurestoreEntity = FeatureStoreEntity(
            name=arm_id_object.asset_name,
            description=rest_object_details.description,
            tags=rest_object_details.tags,
            index_columns=[],
            version="",
        )
        featurestoreEntity.latest_version = rest_object_details.latest_version
        return featurestoreEntity

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "FeatureStoreEntity":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        loaded_schema = load_from_dict(FeatureStoreEntitySchema, data, context, **kwargs)
        return FeatureStoreEntity(**loaded_schema)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = FeatureStoreEntitySchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res
