# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Union

from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, ArmConstants, LONG_URI_FORMAT, AssetTypes
from azure.ai.ml._restclient.v2022_05_01.models import (
    ModelContainerData,
    ModelVersionDetails,
    ModelVersionData,
    FlavorData,
)


from azure.ai.ml._schema import ModelSchema
from azure.ai.ml._utils._arm_id_utils import AMLNamedArmId, AMLVersionedArmId
from azure.ai.ml._utils.utils import load_yaml, snake_to_pascal
from azure.ai.ml.entities._assets import Artifact
from .artifact import ArtifactStorageInfo
from azure.ai.ml.entities._util import load_from_dict, get_md5_string
from azure.ai.ml._utils._asset_utils import get_ignore_file, get_object_hash


class Model(Artifact):
    """Model for training and scoring.

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the resource.
    :type version: str
    :param type: The storage format for this entity. Used for NCD. Possible values include:
     "custom_model", "mlflow_model", "triton_model".
    :type type: str
    :param utc_time_created: Date and time when the model was created, in
        UTC ISO 8601 format. (e.g. '2020-10-19 17:44:02.096572')
    :type utc_time_created: str
    :param flavors: The flavors in which the model can be interpreted.
        (e.g. {sklearn: {sklearn_version: 0.23.2}, python_function: {loader_module: office.plrmodel, python_version: 3.6})
    :type flavors: Dict[str, Any]
    :param path: A remote uri or a local path pointing at a model.
        Example: "azureml://subscriptions/my-sub-id/resourcegroups/my-rg/workspaces/myworkspace/datastores/mydatastore/paths/path_on_datastore/"
    :type path: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: str = None,
        version: str = None,
        type: str = None,
        path: Union[str, PathLike] = None,
        utc_time_created: str = None,
        flavors: Dict[str, Dict[str, Any]] = None,
        description: str = None,
        tags: Dict = None,
        properties: Dict = None,
        **kwargs,
    ):
        self.job_name = kwargs.pop("job_name", None)
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
        if self._is_anonymous and self.path:
            _ignore_file = get_ignore_file(self.path)
            _upload_hash = get_object_hash(self.path, _ignore_file)
            self.name = get_md5_string(_upload_hash)

    @classmethod
    def load(
        cls,
        path: Union[PathLike, str],
        params_override: list = None,
        **kwargs,
    ) -> "Model":
        """Construct a model object from yaml file.

        :param path: Path to a local file as the source.
        :type path: str
        :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
        :type params_override: list
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict

        :return: Constructed model object.
        :rtype: Model
        """
        yaml_dict = load_yaml(path)
        return cls._load(data=yaml_dict, yaml_path=path, params_override=params_override, **kwargs)

        # For lack of bidirectional map in Python, defining the mapping in two ways in one dictionary

    @classmethod
    def _load(
        cls,
        data: Dict = None,
        yaml_path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "Model":
        params_override = params_override or []
        data = data or {}
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return load_from_dict(ModelSchema, data, context, **kwargs)

    def _to_dict(self) -> Dict:
        return ModelSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _from_rest_object(cls, model_rest_object: ModelVersionData) -> "Model":
        rest_model_version: ModelVersionDetails = model_rest_object.properties
        arm_id = AMLVersionedArmId(arm_id=model_rest_object.id)
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
            creation_context=model_rest_object.system_data,
            type=rest_model_version.model_type,
            job_name=rest_model_version.job_name,
        )
        return model

    @classmethod
    def _from_container_rest_object(cls, model_container_rest_object: ModelContainerData) -> "Model":
        model = Model(
            name=model_container_rest_object.name,
            version="1",
            id=model_container_rest_object.id,
            creation_context=model_container_rest_object.system_data,
        )
        model.latest_version = model_container_rest_object.properties.latest_version

        # Setting version to None since if version is not provided it is defaulted to "1".
        # This should go away once container concept is finalized.
        model.version = None
        return model

    def _to_rest_object(self) -> ModelVersionData:
        model_version = ModelVersionDetails(
            description=self.description,
            tags=self.tags,
            properties=self.properties,
            flavors={key: FlavorData(data=dict(value)) for key, value in self.flavors.items()}
            if self.flavors
            else None,  # flatten OrderedDict to dict
            model_type=self.type,
            model_uri=self.path,
            is_anonymous=self._is_anonymous,
        )
        model_version_resource = ModelVersionData(properties=model_version)

        return model_version_resource

    def _update_path(self, asset_artifact: ArtifactStorageInfo) -> None:

        # datastore_arm_id is nul for registry scenario, so capture the full_storage_path
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

    def _to_arm_resource_param(self, **kwargs):
        properties = self._to_rest_object().properties

        return {
            self._arm_type: {
                ArmConstants.NAME: self.name,
                ArmConstants.VERSION: self.version,
                ArmConstants.PROPERTIES_PARAMETER_NAME: self._serialize.body(properties, "ModelVersionDetails"),
            }
        }
