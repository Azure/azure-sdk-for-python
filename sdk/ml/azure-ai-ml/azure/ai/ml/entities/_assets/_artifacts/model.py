# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    FlavorData,
    ModelContainer,
    ModelVersion,
    ModelVersionProperties,
)
from azure.ai.ml._schema import ModelSchema
from azure.ai.ml._utils._arm_id_utils import AMLNamedArmId, AMLVersionedArmId
from azure.ai.ml._utils._asset_utils import get_ignore_file, get_object_hash
from azure.ai.ml.constants._common import (
    BASE_PATH_CONTEXT_KEY,
    LONG_URI_FORMAT,
    PARAMS_OVERRIDE_KEY,
    ArmConstants,
    AssetTypes,
)
from azure.ai.ml.entities._assets import Artifact
from azure.ai.ml.entities._assets.intellectual_property import IntellectualProperty
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import get_md5_string, load_from_dict

from .artifact import ArtifactStorageInfo


class Model(Artifact):  # pylint: disable=too-many-instance-attributes
    """Model for training and scoring.

    :param name: The name of the model. Defaults to a random GUID.
    :type name: Optional[str]
    :param version: The version of the model. Defaults to "1" if either no name or an unregistered name is provided.
        Otherwise, defaults to autoincrement from the last registered version of the model with that name.
    :type version: Optional[str]
    :param type: The storage format for this entity, used for NCD (Novel Class Discovery). Accepted values are
        "custom_model", "mlflow_model", or "triton_model". Defaults to "custom_model".
    :type type: Optional[str]
    :param utc_time_created: The date and time when the model was created, in
        UTC ISO 8601 format. (e.g. '2020-10-19 17:44:02.096572').
    :type utc_time_created: Optional[str]
    :param flavors: The flavors in which the model can be interpreted. Defaults to None.
    :type flavors: Optional[dict[str, Any]]
    :param path: A remote uri or a local path pointing to a model. Defaults to None.
    :type path: Optional[str]
    :param description: The description of the resource. Defaults to None
    :type description: Optional[str]
    :param tags: Tag dictionary. Tags can be added, removed, and updated. Defaults to None.
    :type tags: Optional[dict[str, str]]
    :param properties: The asset property dictionary. Defaults to None.
    :type properties: Optional[dict[str, str]]
    :param stage: The stage of the resource. Defaults to None.
    :type stage: Optional[str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: Optional[dict]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START model_entity_create]
            :end-before: [END model_entity_create]
            :language: python
            :dedent: 8
            :caption: Creating a Model object.
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
        path: Optional[Union[str, PathLike]] = None,
        utc_time_created: Optional[str] = None,
        flavors: Optional[Dict[str, Dict[str, Any]]] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        stage: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.job_name = kwargs.pop("job_name", None)
        self._intellectual_property = kwargs.pop("intellectual_property", None)
        super().__init__(
            name=name,
            version=version,
            path=path,
            description=description,
            tags=tags,
            properties=properties,
            **kwargs,
        )
        self.utc_time_created = utc_time_created
        self.flavors = dict(flavors) if flavors else None
        self._arm_type = ArmConstants.MODEL_VERSION_TYPE
        self.type = type or AssetTypes.CUSTOM_MODEL
        self.stage = stage
        if self._is_anonymous and self.path:
            _ignore_file = get_ignore_file(self.path)
            _upload_hash = get_object_hash(self.path, _ignore_file)
            self.name = get_md5_string(_upload_hash)

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "Model":
        params_override = params_override or []
        data = data or {}
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        res: Model = load_from_dict(ModelSchema, data, context, **kwargs)
        return res

    def _to_dict(self) -> Dict:
        return dict(ModelSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self))  # pylint: disable=no-member

    @classmethod
    def _from_rest_object(cls, model_rest_object: ModelVersion) -> "Model":
        rest_model_version: ModelVersionProperties = model_rest_object.properties
        arm_id = AMLVersionedArmId(arm_id=model_rest_object.id)
        model_stage = rest_model_version.stage if hasattr(rest_model_version, "stage") else None
        if hasattr(rest_model_version, "flavors"):
            flavors = {key: flavor.data for key, flavor in rest_model_version.flavors.items()}
        model = Model(
            id=model_rest_object.id,
            name=arm_id.asset_name,
            version=arm_id.asset_version,
            path=rest_model_version.model_uri,
            description=rest_model_version.description,
            tags=rest_model_version.tags,
            flavors=flavors,
            properties=rest_model_version.properties,
            stage=model_stage,
            # pylint: disable=protected-access
            creation_context=SystemData._from_rest_object(model_rest_object.system_data),
            type=rest_model_version.model_type,
            job_name=rest_model_version.job_name,
            intellectual_property=(
                IntellectualProperty._from_rest_object(rest_model_version.intellectual_property)
                if rest_model_version.intellectual_property
                else None
            ),
        )
        return model

    @classmethod
    def _from_container_rest_object(cls, model_container_rest_object: ModelContainer) -> "Model":
        model = Model(
            name=model_container_rest_object.name,
            version="1",
            id=model_container_rest_object.id,
            # pylint: disable=protected-access
            creation_context=SystemData._from_rest_object(model_container_rest_object.system_data),
        )
        model.latest_version = model_container_rest_object.properties.latest_version

        # Setting version to None since if version is not provided it is defaulted to "1".
        # This should go away once container concept is finalized.
        model.version = None
        return model

    def _to_rest_object(self) -> ModelVersion:
        model_version = ModelVersionProperties(
            description=self.description,
            tags=self.tags,
            properties=self.properties,
            flavors=(
                {key: FlavorData(data=dict(value)) for key, value in self.flavors.items()} if self.flavors else None
            ),  # flatten OrderedDict to dict
            model_type=self.type,
            model_uri=self.path,
            stage=self.stage,
            is_anonymous=self._is_anonymous,
        )
        model_version_resource = ModelVersion(properties=model_version)

        return model_version_resource

    def _update_path(self, asset_artifact: ArtifactStorageInfo) -> None:
        # datastore_arm_id is null for registry scenario, so capture the full_storage_path
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

    def _to_arm_resource_param(self, **kwargs: Any) -> Dict:  # pylint: disable=unused-argument
        properties = self._to_rest_object().properties

        return {
            self._arm_type: {
                ArmConstants.NAME: self.name,
                ArmConstants.VERSION: self.version,
                ArmConstants.PROPERTIES_PARAMETER_NAME: self._serialize.body(properties, "ModelVersionProperties"),
            }
        }
