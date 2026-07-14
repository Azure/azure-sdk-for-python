# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access, redefined-builtin

import re
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, List, Optional, Union

from azure.ai.ml._schema.assets.package.model_package import ModelPackageSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import dump_yaml_to_file, snake_to_pascal
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._util import load_from_dict

from .base_environment_source import BaseEnvironment
from .inferencing_server import AzureMLBatchInferencingServer, AzureMLOnlineInferencingServer
from .model_configuration import ModelConfiguration


def _package_input_path_from_rest(path: Any) -> Any:
    """Reconstruct a package input path entity from its wire representation (dict or msrest model).

    :param path: The wire representation of the input path.
    :type path: Any
    :return: The reconstructed input path entity, or None.
    :rtype: Any
    """
    if path is None:
        return None
    input_path_type = path.get("inputPathType") if isinstance(path, dict) else getattr(path, "input_path_type", None)
    if input_path_type == "PathId":
        return PackageInputPathId._from_rest_object(path)
    if input_path_type == "PathVersion":
        return PackageInputPathVersion._from_rest_object(path)
    if input_path_type == "Url":
        return PackageInputPathUrl._from_rest_object(path)
    return None


@experimental
class PackageInputPathId:
    """Package input path specified with a resource ID.

    :param input_path_type: The type of the input path. Accepted values are "Url", "PathId", and "PathVersion".
    :type input_path_type: Optional[str]
    :param resource_id: The resource ID of the input path. e.g. "azureml://subscriptions/<>/resourceGroups/
        <>/providers/Microsoft.MachineLearningServices/workspaces/<>/data/<>/versions/<>".
    :type resource_id: Optional[str]
    """

    def __init__(
        self,
        *,
        input_path_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ) -> None:
        self.input_path_type = input_path_type
        self.resource_id = resource_id

    def _to_rest_object(self) -> Dict[str, Any]:
        rest: Dict[str, Any] = {"inputPathType": "PathId"}
        if self.resource_id is not None:
            rest["resourceId"] = self.resource_id
        return rest

    @classmethod
    def _from_rest_object(cls, package_input_path_id_rest_object: Any) -> "PackageInputPathId":
        obj = package_input_path_id_rest_object
        if isinstance(obj, dict):
            return PackageInputPathId(input_path_type=obj.get("inputPathType"), resource_id=obj.get("resourceId"))
        return PackageInputPathId(
            input_path_type=obj.input_path_type,
            resource_id=obj.resource_id,
        )


@experimental
class PackageInputPathVersion:
    """Package input path specified with a resource name and version.

    :param input_path_type: The type of the input path. Accepted values are "Url", "PathId", and "PathVersion".
    :type input_path_type: Optional[str]
    :param resource_name: The resource name of the input path.
    :type resource_name: Optional[str]
    :param resource_version: The resource version of the input path.
    :type resource_version: Optional[str]
    """

    def __init__(
        self,
        *,
        input_path_type: Optional[str] = None,
        resource_name: Optional[str] = None,
        resource_version: Optional[str] = None,
    ) -> None:
        self.input_path_type = input_path_type
        self.resource_name = resource_name
        self.resource_version = resource_version

    def _to_rest_object(self) -> Dict[str, Any]:
        rest: Dict[str, Any] = {"inputPathType": "PathVersion"}
        if self.resource_name is not None:
            rest["resourceName"] = self.resource_name
        if self.resource_version is not None:
            rest["resourceVersion"] = self.resource_version
        return rest

    @classmethod
    def _from_rest_object(cls, package_input_path_version_rest_object: Any) -> "PackageInputPathVersion":
        obj = package_input_path_version_rest_object
        if isinstance(obj, dict):
            return PackageInputPathVersion(
                input_path_type=obj.get("inputPathType"),
                resource_name=obj.get("resourceName"),
                resource_version=obj.get("resourceVersion"),
            )
        return PackageInputPathVersion(
            input_path_type=obj.input_path_type,
            resource_name=obj.resource_name,
            resource_version=obj.resource_version,
        )


@experimental
class PackageInputPathUrl:
    """Package input path specified with a url.

    :param input_path_type: The type of the input path. Accepted values are "Url", "PathId", and "PathVersion".
    :type input_path_type: Optional[str]
    :param url: The url of the input path. e.g. "azureml://subscriptions/<>/resourceGroups/
        <>/providers/Microsoft.MachineLearningServices/workspaces/data/<>/versions/<>".
    :type url: Optional[str]
    """

    def __init__(self, *, input_path_type: Optional[str] = None, url: Optional[str] = None) -> None:
        self.input_path_type = input_path_type
        self.url = url

    def _to_rest_object(self) -> Dict[str, Any]:
        rest: Dict[str, Any] = {"inputPathType": "Url"}
        if self.url is not None:
            rest["url"] = self.url
        return rest

    @classmethod
    def _from_rest_object(cls, package_input_path_url_rest_object: Any) -> "PackageInputPathUrl":
        obj = package_input_path_url_rest_object
        if isinstance(obj, dict):
            return PackageInputPathUrl(input_path_type=obj.get("inputPathType"), url=obj.get("url"))
        return PackageInputPathUrl(
            input_path_type=obj.input_path_type,
            url=obj.url,
        )


@experimental
class ModelPackageInput:
    """Model package input.

    :param type: The type of the input.
    :type type: Optional[str]
    :param path: The path of the input.
    :type path: Optional[Union[~azure.ai.ml.entities.PackageInputPathId, ~azure.ai.ml.entities.PackageInputPathUrl,
        ~azure.ai.ml.entities.PackageInputPathVersion]]
    :param mode: The input mode.
    :type mode: Optional[str]
    :param mount_path: The mount path for the input.
    :type mount_path: Optional[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START model_package_input_entity_create]
            :end-before: [END model_package_input_entity_create]
            :language: python
            :dedent: 8
            :caption: Create a Model Package Input object.
    """

    def __init__(
        self,
        *,
        type: Optional[str] = None,
        path: Optional[Union[PackageInputPathId, PackageInputPathUrl, PackageInputPathVersion]] = None,
        mode: Optional[str] = None,
        mount_path: Optional[str] = None,
    ) -> None:
        self.type = type
        self.path = path
        self.mode = mode
        self.mount_path = mount_path

    def _to_rest_object(self) -> Dict[str, Any]:
        rest: Dict[str, Any] = {}
        input_type = snake_to_pascal(self.type)
        if input_type is not None:
            rest["inputType"] = input_type
        if self.path is not None:
            rest["path"] = self.path._to_rest_object()
        mode = snake_to_pascal(self.mode)
        if mode is not None:
            rest["mode"] = mode
        if self.mount_path is not None:
            rest["mountPath"] = self.mount_path
        return rest

    @classmethod
    def _from_rest_object(cls, model_package_input_rest_object: Any) -> "ModelPackageInput":
        obj = model_package_input_rest_object
        if isinstance(obj, dict):
            return ModelPackageInput(
                type=obj.get("inputType"),
                path=_package_input_path_from_rest(obj.get("path")),
                mode=obj.get("mode"),
                mount_path=obj.get("mountPath"),
            )
        return ModelPackageInput(
            type=obj.input_type,
            path=obj.path._from_rest_object(),
            mode=obj.mode,
            mount_path=obj.mount_path,
        )


@experimental
class ModelPackage(Resource):
    """Model package.

    :param target_environment_name: The target environment name for the model package.
    :type target_environment_name: str
    :param inferencing_server: The inferencing server of the model package.
    :type inferencing_server: Union[~azure.ai.ml.entities.AzureMLOnlineInferencingServer,
        ~azure.ai.ml.entities.AzureMLBatchInferencingServer]
    :param base_environment_source: The base environment source of the model package.
    :type base_environment_source: Optional[~azure.ai.ml.entities.BaseEnvironment]
    :param target_environment_version: The version of the model package.
    :type target_environment_version: Optional[str]
    :param environment_variables: The environment variables of the model package.
    :type environment_variables: Optional[dict[str, str]]
    :param inputs: The inputs of the model package.
    :type inputs: Optional[list[~azure.ai.ml.entities.ModelPackageInput]]
    :param model_configuration: The model configuration.
    :type model_configuration: Optional[~azure.ai.ml.entities.ModelConfiguration]
    :param tags: The tags of the model package.
    :type tags: Optional[dict[str, str]]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START model_package_entity_create]
            :end-before: [END model_package_entity_create]
            :language: python
            :dedent: 8
            :caption: Create a Model Package object.
    """

    def __init__(
        self,
        *,
        target_environment: Union[str, Dict[str, str]],
        inferencing_server: Union[AzureMLOnlineInferencingServer, AzureMLBatchInferencingServer],
        base_environment_source: Optional[BaseEnvironment] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        inputs: Optional[List[ModelPackageInput]] = None,
        model_configuration: Optional[ModelConfiguration] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ):
        if isinstance(target_environment, dict):
            target_environment = target_environment["name"]
            env_version = None
        else:
            parse_id = re.match(r"azureml:(\w+):(\d+)$", target_environment)

            if parse_id:
                target_environment = parse_id.group(1)
                env_version = parse_id.group(2)
            else:
                env_version = None

        super().__init__(
            name=target_environment,
            tags=tags,
            **kwargs,
        )
        self.target_environment_id = target_environment
        self.base_environment_source = base_environment_source
        self.inferencing_server = inferencing_server
        self.model_configuration = model_configuration
        self.inputs = inputs
        self.environment_variables = environment_variables
        self.environment_version = env_version

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "ModelPackage":
        params_override = params_override or []
        data = data or {}
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        res: ModelPackage = load_from_dict(ModelPackageSchema, data, context, **kwargs)
        return res

    def dump(
        self,
        dest: Union[str, PathLike, IO[AnyStr]],
        **kwargs: Any,
    ) -> None:
        """Dumps the job content into a file in YAML format.

        :param dest: The local path or file stream to write the YAML content to.
            If dest is a file path, a new file will be created.
            If dest is an open file, the file will be written to directly.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        :raises FileExistsError: Raised if dest is a file path and the file already exists.
        :raises IOError: Raised if dest is an open file and the file is not writable.
        """
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False)

    def _to_dict(self) -> Dict:
        return dict(ModelPackageSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self))

    @classmethod
    def _from_rest_object(cls, model_package_rest_object: Any) -> Any:
        if isinstance(model_package_rest_object, dict):
            return model_package_rest_object.get("targetEnvironmentId")
        return model_package_rest_object.target_environment_id

    def _to_rest_object(self) -> Dict[str, Any]:
        code = None

        if (
            self.inferencing_server
            and hasattr(self.inferencing_server, "code_configuration")
            and self.inferencing_server.code_configuration
        ):
            self.inferencing_server.code_configuration._validate()
            code_id = (
                self.inferencing_server.code_configuration.code
                if isinstance(self.inferencing_server.code_configuration.code, str)
                else self.inferencing_server.code_configuration.code.id  # type: ignore[union-attr]
            )
            code = {"codeId": code_id}
            if self.inferencing_server.code_configuration.scoring_script is not None:
                code["scoringScript"] = self.inferencing_server.code_configuration.scoring_script
            self.inferencing_server.code_configuration = code  # type: ignore[assignment]

        package_request: Dict[str, Any] = {}
        if self.target_environment_id is not None:
            package_request["targetEnvironmentId"] = self.target_environment_id
        if self.base_environment_source is not None:
            package_request["baseEnvironmentSource"] = self.base_environment_source._to_rest_object()
        if self.inferencing_server is not None:
            package_request["inferencingServer"] = self.inferencing_server._to_rest_object()
        if self.model_configuration is not None:
            package_request["modelConfiguration"] = self.model_configuration._to_rest_object()
        if self.inputs:
            package_request["inputs"] = [model_input._to_rest_object() for model_input in self.inputs]
        if self.tags is not None:
            package_request["tags"] = self.tags
        if self.environment_variables is not None:
            package_request["environmentVariables"] = self.environment_variables

        return package_request
