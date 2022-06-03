# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Union
from pathlib import Path
from os import PathLike

from azure.ai.ml.entities._assets import Artifact
from .artifact import ArtifactStorageInfo
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    ArmConstants,
)
from azure.ai.ml._restclient.v2022_05_01.models import (
    CodeVersionData,
    CodeVersionDetails,
)
from azure.ai.ml._schema import CodeAssetSchema
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._utils._arm_id_utils import AMLVersionedArmId


class Code(Artifact):
    """Code for training and scoring.

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the resource.
    :type version: str
    :param path: A local path or a remote uri. A datastore remote uri example is like,
        "azureml://subscriptions/my-sub-id/resourcegroups/my-rg/workspaces/myworkspace/datastores/mydatastore/paths/path_on_datastore/"
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
        description: str = None,
        tags: Dict = None,
        properties: Dict = None,
        path: Union[str, PathLike] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            properties=properties,
            path=path,
            **kwargs,
        )
        self._arm_type = ArmConstants.CODE_VERSION_TYPE

    @classmethod
    def load(
        cls,
        path: Union[PathLike, str],
        params_override: list = None,
        **kwargs,
    ) -> "Code":
        """Construct a code object from yaml file.

        :param path: Path to a local file as the source.
        :type path: str
        :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
        :type params_override: list
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict

        :return: Constructed code object.
        :rtype: Code
        """
        yaml_dict = load_yaml(path)
        return cls._load(data=yaml_dict, yaml_path=path, params_override=params_override, **kwargs)

    @classmethod
    def _load(
        cls,
        data: Dict = None,
        yaml_path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "Code":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return load_from_dict(CodeAssetSchema, data, context, **kwargs)

    def _to_dict(self) -> Dict:
        return CodeAssetSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _from_rest_object(cls, code_rest_object: CodeVersionData) -> "Code":
        rest_code_version: CodeVersionDetails = code_rest_object.properties
        arm_id = AMLVersionedArmId(arm_id=code_rest_object.id)
        code = Code(
            id=code_rest_object.id,
            name=arm_id.asset_name,
            version=arm_id.asset_version,
            path=rest_code_version.code_uri,
            description=rest_code_version.description,
            tags=rest_code_version.tags,
            properties=rest_code_version.properties,
            creation_context=code_rest_object.system_data,
            is_anonymous=rest_code_version.is_anonymous,
        )
        return code

    def _to_rest_object(self) -> CodeVersionData:
        code_version = CodeVersionDetails(code_uri=self.path, is_anonymous=self._is_anonymous)
        code_version_resource = CodeVersionData(properties=code_version)

        return code_version_resource

    def _update_path(self, asset_artifact: ArtifactStorageInfo) -> None:
        """Updates an an artifact with the remote path of a local upload"""
        if asset_artifact.is_file:
            # Code paths cannot be pointers to single files. It must be a pointer to a container
            # Skipping the setter to avoid being resolved as a local path
            self._path = asset_artifact.subdir_path
        else:
            self._path = asset_artifact.full_storage_path

    def _to_arm_resource_param(self, **kwargs):
        from azure.ai.ml.constants import ArmConstants

        properties = self._to_rest_object().properties

        return {
            self._arm_type: {
                ArmConstants.NAME: self.name,
                ArmConstants.VERSION: self.version,
                ArmConstants.PROPERTIES_PARAMETER_NAME: self._serialize.body(properties, "CodeVersionDetails"),
            }
        }
