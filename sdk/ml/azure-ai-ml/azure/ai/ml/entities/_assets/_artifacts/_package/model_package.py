# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access, redefined-builtin

import re
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, List, Optional, Union

from azure.ai.ml._restclient.v2023_08_01_preview.models import CodeConfiguration
from azure.ai.ml._restclient.v2023_08_01_preview.models import ModelPackageInput as RestModelPackageInput
from azure.ai.ml._restclient.v2023_08_01_preview.models import PackageInputPathId as RestPackageInputPathId
from azure.ai.ml._restclient.v2023_08_01_preview.models import PackageInputPathUrl as RestPackageInputPathUrl
from azure.ai.ml._restclient.v2023_08_01_preview.models import PackageInputPathVersion as RestPackageInputPathVersion
from azure.ai.ml._restclient.v2023_08_01_preview.models import PackageRequest, PackageResponse
from azure.ai.ml._schema.assets.package.model_package import ModelPackageSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import dump_yaml_to_file, snake_to_pascal
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._util import load_from_dict

from .base_environment_source import BaseEnvironment
from .inferencing_server import AzureMLBatchInferencingServer, AzureMLOnlineInferencingServer
from .model_configuration import ModelConfiguration


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

    def _to_rest_object(self) -> RestPackageInputPathId:
        return RestPackageInputPathId(
            input_path_type=self.input_path_type,
            resource_id=self.resource_id,
        )

    @classmethod
    def _from_rest_object(cls, package_input_path_id_rest_object: RestPackageInputPathId) -> "PackageInputPathId":
        return PackageInputPathId(
            input_path_type=package_input_path_id_rest_object.input_path_type,
            resource_id=package_input_path_id_rest_object.resource_id,
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

    def _to_rest_object(self) -> RestPackageInputPathVersion:
        return RestPackageInputPathVersion(
            input_path_type=self.input_path_type,
            resource_name=self.resource_name,
            resource_version=self.resource_version,
        )

    @classmethod
    def _from_rest_object(
        cls, package_input_path_version_rest_object: RestPackageInputPathVersion
    ) -> "PackageInputPathVersion":
        return PackageInputPathVersion(
            input_path_type=package_input_path_version_rest_object.input_path_type,
            resource_name=package_input_path_version_rest_object.resource_name,
            resource_version=package_input_path_version_rest_object.resource_version,
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

    def _to_rest_object(self) -> RestPackageInputPathUrl:
        return RestPackageInputPathUrl(
            input_path_type=self.input_path_type,
            url=self.url,
        )

    @classmethod
    def _from_rest_object(cls, package_input_path_url_rest_object: RestPackageInputPathUrl) -> "PackageInputPathUrl":
        return PackageInputPathUrl(
            input_path_type=package_input_path_url_rest_object.input_path_type,
            url=package_input_path_url_rest_object.url,
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

    def _to_rest_object(self) -> RestModelPackageInput:
        if self.path is None:
            return RestModelPackageInput(
                input_type=snake_to_pascal(self.type),
                path=None,
                mode=snake_to_pascal(self.mode),
                mount_path=self.mount_path,
            )
        return RestModelPackageInput(
            input_type=snake_to_pascal(self.type),
            path=self.path._to_rest_object(),
            mode=snake_to_pascal(self.mode),
            mount_path=self.mount_path,
        )

    @classmethod
    def _from_rest_object(cls, model_package_input_rest_object: RestModelPackageInput) -> "ModelPackageInput":
        return ModelPackageInput(
            type=model_package_input_rest_object.input_type,
            path=model_package_input_rest_object.path._from_rest_object(),
            mode=model_package_input_rest_object.mode,
            mount_path=model_package_input_rest_object.mount_path,
        )


@experimental
class ModelPackage(Resource, PackageRequest):
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
            target_environment_id=target_environment,
            base_environment_source=base_environment_source,
            inferencing_server=inferencing_server,
            model_configuration=model_configuration,
            inputs=inputs,
            tags=tags,
            environment_variables=environment_variables,
        )
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
        # pylint: disable=unused-argument
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
        return dict(ModelPackageSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self))  # pylint: disable=no-member

    @classmethod
    def _from_rest_object(cls, model_package_rest_object: PackageResponse) -> Any:
        target_environment_id = model_package_rest_object.target_environment_id
        return target_environment_id

    def _to_rest_object(self) -> PackageRequest:
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
                else self.inferencing_server.code_configuration.code.id
            )
            code = CodeConfiguration(
                code_id=code_id,
                scoring_script=self.inferencing_server.code_configuration.scoring_script,
            )
            self.inferencing_server.code_configuration = code

        package_request = PackageRequest(
            target_environment_id=self.target_environment_id,
            base_environment_source=(
                self.base_environment_source._to_rest_object() if self.base_environment_source else None
            ),
            inferencing_server=self.inferencing_server._to_rest_object() if self.inferencing_server else None,
            model_configuration=self.model_configuration._to_rest_object() if self.model_configuration else None,
            inputs=[input._to_rest_object() for input in self.inputs] if self.inputs else None,
            tags=self.tags,
            environment_variables=self.environment_variables,
        )

        return package_request
