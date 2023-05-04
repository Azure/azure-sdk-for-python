# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access, redefined-builtin

from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, List, Dict, Optional, Union


from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    PackageRequest,
    PackageResponse,
    ModelPackageInput as RestModelPackageInput,
    PackageInputPathId as RestPackageInputPathId,
    PackageInputPathVersion as RestPackageInputPathVersion,
    PackageInputPathUrl as RestPackageInputPathUrl,
    CodeConfiguration,
)

from azure.ai.ml.entities._resource import Resource
from azure.ai.ml._schema.assets.package.model_package import ModelPackageSchema
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.constants._common import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
)
from azure.ai.ml._utils.utils import snake_to_pascal, dump_yaml_to_file
from azure.ai.ml._utils._experimental import experimental
from .model_configuration import ModelConfiguration
from .inferencing_server import AzureMLOnlineInferencingServer, AzureMLBatchInferencingServer
from .base_environment_source import BaseEnvironment


@experimental
class PackageInputPathId:

    """Package input path specified with a resource id.

    :param input_path_type: The type of the input path. Possible values include: "Url", "PathId", "PathVersion".
    :type input_path_type: str
    :param resource_id: The resource id of the input path. e.g. azureml://subscriptions/<>/resourceGroups/
    <>/providers/Microsoft.MachineLearningServices/workspaces/<>/data/<>/versions/<>
    :type resource_id: str
    """

    def __init__(self, input_path_type: Optional[str] = None, resource_id: Optional[str] = None):
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

    :param input_path_type: The type of the input path. Possible values include: "Url", "PathId", "PathVersion".
    :type input_path_type: str
    :param resource_name: The resource name of the input path.
    :type resource_name: str
    :param resource_version: The resource version of the input path.
    :type resource_version: str
    """

    def __init__(
        self,
        *,
        input_path_type: Optional[str] = None,
        resource_name: Optional[str] = None,
        resource_version: Optional[str] = None,
    ):
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

    :param input_path_type: The type of the input path. Possible values include: "Url", "PathId", "PathVersion".
    :type input_path_type: str
    :param url: The url of the input path. e.g. azureml://subscriptions/<>/resourceGroups/
    <>/providers/Microsoft.MachineLearningServices/workspaces/data/<>/versions/<>
    :type url: str
    """

    def __init__(self, *, input_path_type: Optional[str] = None, url: Optional[str] = None):
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
    :type type: str
    :param path: The path of the input.
    :type path: azure.ai.ml.entities.PackageInputPathId
     or azure.ai.ml.entities.PackageInputPathUrl or azure.ai.ml.entities.PackageInputPathVersion
    :param mode: The mode of the input.
    :type mode: str
    :param mount_path: The mount path of the input.
    :type mount_path: str
    """

    def __init__(
        self,
        *,
        type: Optional[str] = None,
        path: Optional[Union[PackageInputPathId, PackageInputPathUrl, PackageInputPathVersion]] = None,
        mode: Optional[str] = None,
        mount_path: Optional[str] = None,
    ):
        self.type = type
        self.path = path
        self.mode = mode
        self.mount_path = mount_path

    def _to_rest_object(self) -> RestModelPackageInput:
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

    :param target_environment_name: The name of the model package.
    :type target_environment_name: str
    :param inferencing_server: The inferencing server of the model package.
    :type inferencing_server: azure.ai.ml.entities.InferencingServer
    :param base_environment_source: The base environment source of the model package.
    :type base_environment_source: azure.ai.ml.entities.BaseEnvironmentSource
    :param target_environment_version: The version of the model package.
    :type target_environment_version: str
    :param environment_variables: The environment variables of the model package.
    :type environment_variables: dict
    :param inputs: The inputs of the model package.
    :type inputs: list[azure.ai.ml.entities.ModelPackageInput]
    :param model_configuration: The model configuration of the model package.
    :type model_configuration: azure.ai.ml.entities.ModelConfiguration
    :param tags: The tags of the model package.
    :type tags: dict
    """

    def __init__(
        self,
        *,
        target_environment_name: str,
        inferencing_server: Union[AzureMLOnlineInferencingServer, AzureMLBatchInferencingServer],
        base_environment_source: BaseEnvironment = None,
        target_environment_version: Optional[str] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        inputs: Optional[List[ModelPackageInput]] = None,
        model_configuration: Optional[ModelConfiguration] = None,
        tags: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            name=target_environment_name,
            target_environment_name=target_environment_name,
            target_environment_version=target_environment_version,
            base_environment_source=base_environment_source,
            inferencing_server=inferencing_server,
            model_configuration=model_configuration,
            inputs=inputs,
            tags=tags,
            environment_variables=environment_variables,
        )

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "ModelPackage":
        params_override = params_override or []
        data = data or {}
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return load_from_dict(ModelPackageSchema, data, context, **kwargs)

    def dump(
        self,
        dest: Union[str, PathLike, IO[AnyStr]],
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        """Dump the model package spec into a file in yaml format.

        :param path: Path to a local file as the target, new file will be created, raises exception if the file exists.
        :type path: str
        """
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False)

    def _to_dict(self) -> Dict:
        return ModelPackageSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)  # pylint: disable=no-member

    @classmethod
    def _from_rest_object(cls, model_package_rest_object: PackageResponse) -> "ModelPackageResponse":
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
                code_id=code_id, scoring_script=self.inferencing_server.code_configuration.scoring_script
            )
            self.inferencing_server.code_configuration = code

        package_request = PackageRequest(
            target_environment_name=self.name,
            base_environment_source=self.base_environment_source._to_rest_object()
            if self.base_environment_source
            else None,
            inferencing_server=self.inferencing_server._to_rest_object() if self.inferencing_server else None,
            model_configuration=self.model_configuration._to_rest_object() if self.model_configuration else None,
            inputs=[input._to_rest_object() for input in self.inputs] if self.inputs else None,
            tags=self.tags,
            environment_variables=self.environment_variables,
        )

        return package_request
