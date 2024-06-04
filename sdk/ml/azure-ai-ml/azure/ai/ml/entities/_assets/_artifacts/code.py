# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2022_05_01.models import CodeVersionData, CodeVersionDetails
from azure.ai.ml._schema import CodeAssetSchema
from azure.ai.ml._utils._arm_id_utils import AMLVersionedArmId
from azure.ai.ml._utils._asset_utils import IgnoreFile, get_content_hash, get_content_hash_version, get_ignore_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, ArmConstants
from azure.ai.ml.entities._assets import Artifact
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import load_from_dict

from .artifact import ArtifactStorageInfo


class Code(Artifact):
    """Code for training and scoring.

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the resource.
    :type version: str
    :param path: A local path or a remote uri. A datastore remote uri example is like,
        "azureml://subscriptions/{}/resourcegroups/{}/workspaces/{}/datastores/{}/paths/path_on_datastore/"
    :type path: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param ignore_file: Ignore file for the resource.
    :type ignore_file: IgnoreFile
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        path: Optional[Union[str, PathLike]] = None,
        ignore_file: Optional[IgnoreFile] = None,
        **kwargs: Any,
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
        if self.path and os.path.isabs(self.path):
            # Only calculate hash for local files
            self._ignore_file = get_ignore_file(self.path) if ignore_file is None else ignore_file
            self._hash_sha256 = get_content_hash(self.path, self._ignore_file)

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "Code":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        res: Code = load_from_dict(CodeAssetSchema, data, context, **kwargs)
        return res

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = CodeAssetSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

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
            # pylint: disable=protected-access
            creation_context=SystemData._from_rest_object(code_rest_object.system_data),
            is_anonymous=rest_code_version.is_anonymous,
        )
        return code

    def _to_rest_object(self) -> CodeVersionData:
        properties = {}
        if hasattr(self, "_hash_sha256"):
            properties["hash_sha256"] = self._hash_sha256
            properties["hash_version"] = get_content_hash_version()
        code_version = CodeVersionDetails(code_uri=self.path, is_anonymous=self._is_anonymous, properties=properties)
        code_version_resource = CodeVersionData(properties=code_version)

        return code_version_resource

    def _update_path(self, asset_artifact: ArtifactStorageInfo) -> None:
        """Update an artifact with the remote path of a local upload.

        :param asset_artifact: The asset storage info of the artifact
        :type asset_artifact: ArtifactStorageInfo
        """
        if asset_artifact.is_file:
            # Code paths cannot be pointers to single files. It must be a pointer to a container
            # Skipping the setter to avoid being resolved as a local path
            self._path = asset_artifact.subdir_path  # pylint: disable=attribute-defined-outside-init
        else:
            self._path = asset_artifact.full_storage_path  # pylint: disable=attribute-defined-outside-init

    # pylint: disable=unused-argument
    def _to_arm_resource_param(self, **kwargs: Any) -> Dict:
        properties = self._to_rest_object().properties

        return {
            self._arm_type: {
                ArmConstants.NAME: self.name,
                ArmConstants.VERSION: self.version,
                ArmConstants.PROPERTIES_PARAMETER_NAME: self._serialize.body(properties, "CodeVersionDetails"),
            }
        }
