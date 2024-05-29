# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, List, Optional, Union, cast

from azure.ai.ml._restclient.v2023_10_01.models import (
    FeaturesetContainer,
    FeaturesetContainerProperties,
    FeaturesetVersion,
    FeaturesetVersionProperties,
)
from azure.ai.ml._schema._feature_set.feature_set_schema import FeatureSetSchema
from azure.ai.ml._utils._arm_id_utils import AMLNamedArmId, get_arm_id_object_from_id
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, LONG_URI_FORMAT, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._assets import Artifact
from azure.ai.ml.entities._feature_set.feature_set_specification import FeatureSetSpecification
from azure.ai.ml.entities._feature_set.materialization_settings import MaterializationSettings
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from .artifact import ArtifactStorageInfo


class FeatureSet(Artifact):
    """Feature Set

    :param name: The name of the Feature Set resource.
    :type name: str
    :param version: The version of the Feature Set resource.
    :type version: str
    :param entities: Specifies list of entities.
    :type entities: list[str]
    :param specification: Specifies the feature set spec details.
    :type specification: ~azure.ai.ml.entities.FeatureSetSpecification
    :param stage: Feature set stage. Allowed values: Development, Production, Archived. Defatuls to Development.
    :type stage: Optional[str]
    :param description: The description of the Feature Set resource. Defaults to None.
    :type description: Optional[str]
    :param tags: Tag dictionary. Tags can be added, removed, and updated. Defaults to None.
    :type tags: Optional[dict[str, str]]
    :param materialization_settings: Specifies the materialization settings. Defaults to None.
    :type materialization_settings: Optional[~azure.ai.ml.entities.MaterializationSettings]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    :raises ValidationException: Raised if stage is specified and is not valid.

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_featurestore.py
            :start-after: [START configure_feature_set]
            :end-before: [END configure_feature_set]
            :language: Python
            :dedent: 8
            :caption: Instantiating a Feature Set object
    """

    def __init__(
        self,
        *,
        name: str,
        version: str,
        entities: List[str],
        specification: Optional[FeatureSetSpecification],
        stage: Optional[str] = "Development",
        description: Optional[str] = None,
        materialization_settings: Optional[MaterializationSettings] = None,
        tags: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            path=specification.path if specification is not None else None,
            **kwargs,
        )
        if stage and stage not in ["Development", "Production", "Archived"]:
            msg = f"Stage must be Development, Production, or Archived, found {stage}"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_type=ValidationErrorType.INVALID_VALUE,
                target=ErrorTarget.FEATURE_SET,
                error_category=ErrorCategory.USER_ERROR,
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
            materialization_settings=(
                self.materialization_settings._to_rest_object() if self.materialization_settings else None
            ),
            specification=self.specification._to_rest_object() if self.specification is not None else None,
            stage=self.stage,
        )
        return FeaturesetVersion(name=self.name, properties=featureset_version_properties)

    @classmethod
    def _from_rest_object(cls, featureset_rest_object: FeaturesetVersion) -> Optional["FeatureSet"]:
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
        **kwargs: Any,
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
        return dict(FeatureSetSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self))

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

            if self.specification is not None:
                self.specification.path = self.path

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> None:
        """Dump the asset content into a file in YAML format.

        :param dest: The local path or file stream to write the YAML content to.
            If dest is a file path, a new file will be created.
            If dest is an open file, the file will be written to directly.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        :raises FileExistsError: Raised if dest is a file path and the file already exists.
        :raises IOError: Raised if dest is an open file and the file is not writable.
        """

        import os
        import shutil

        from azure.ai.ml._utils.utils import is_url

        origin_spec_path = self.specification.path if self.specification is not None else None
        if isinstance(dest, (PathLike, str)) and self.specification is not None and not is_url(self.specification.path):
            if os.path.exists(dest):
                raise FileExistsError(f"File {dest} already exists.")
            relative_path = os.path.basename(cast(PathLike, self.specification.path))
            src_spec_path = (
                str(Path(self._base_path, self.specification.path)) if self.specification.path is not None else ""
            )
            dest_spec_path = str(Path(os.path.dirname(dest), relative_path))
            if os.path.exists(dest_spec_path):
                shutil.rmtree(dest_spec_path)
            shutil.copytree(src=src_spec_path, dst=dest_spec_path)
            self.specification.path = str(Path("./", relative_path))
        super().dump(dest=dest, **kwargs)

        if self.specification is not None:
            self.specification.path = origin_spec_path
