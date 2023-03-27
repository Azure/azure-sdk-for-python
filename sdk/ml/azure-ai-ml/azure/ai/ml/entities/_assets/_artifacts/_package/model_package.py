# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, List, Dict, Optional, Union


from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    PackageRequest,
    PackageResponse,
    InferencingServer,
    ModelPackageInput as RestModelPackageInput,
    PackageInputPathId as RestPackageInputPathId,
    PackageInputPathVersion as RestPackageInputPathVersion,
    PackageInputPathUrl as RestPackageInputPathUrl,
    BaseEnvironmentSource,
    ModelConfiguration,
    CodeConfiguration,
)
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml._schema.assets.package.model_package import ModelPackageSchema
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.constants._common import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
)
from azure.ai.ml._utils.utils import snake_to_pascal
from azure.ai.ml._utils._experimental import experimental


@experimental
class PackageInputPathId:
    def __init__(self, input_path_type: Optional[str] = None, resource_id: Optional[str] = None, **kwargs):
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
    def __init__(
        self,
        input_path_type: Optional[str] = None,
        resource_name: Optional[str] = None,
        resource_version: Optional[str] = None,
        **kwargs,
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
    def __init__(self, input_path_type: Optional[str] = None, url: Optional[str] = None, **kwargs):
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

    :param type: The storage format for this entity. Used for NCD. Possible values include:
     "custom_model", "mlflow_model", "triton_model".
    :type type: str
    :param path: A remote uri or a local path pointing at a model.
        Example: "azureml://subscriptions/{}/resourcegroups/{}/workspaces/{}/datastores/{}/paths/path_on_datastore/"
    :type path: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        type: Optional[str] = None,
        path: Optional[Union[PackageInputPathId, PackageInputPathUrl, PackageInputPathVersion]] = None,
        mode: Optional[str] = None,
        mount_path: Optional[str] = None,
        **kwargs,
    ):
        self.type = type
        self.path = path
        self.mode = mode
        self.mount_path = mount_path

    def _to_rest_object(self) -> RestModelPackageInput:
        # import debugpy
        # debugpy.connect(("localhost", 5678))
        # debugpy.breakpoint()
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
        e.g. {sklearn: {sklearn_version: 0.23.2}, python_function: {loader_module: office.plrmodel, python_version: 3.6}
    :type flavors: Dict[str, Any]
    :param path: A remote uri or a local path pointing at a model.
        Example: "azureml://subscriptions/{}/resourcegroups/{}/workspaces/{}/datastores/{}/paths/path_on_datastore/"
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
        name: Optional[str] = None,
        version: Optional[str] = None,
        inferencing_server: Optional[InferencingServer] = None,
        base_environment_source: Optional[BaseEnvironmentSource] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        inputs: Optional[List[ModelPackageInput]] = None,
        model_configuration: Optional[ModelConfiguration] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        name = kwargs.pop("target_environment_name", None)

        super().__init__(
            name=name,
            target_environment_name=name,
            target_environment_version=version,
            base_environment_source=base_environment_source,
            inferencing_server=inferencing_server,
            model_configuration=model_configuration,
            inputs=inputs,
            tags=tags,
            environment_variables=environment_variables,
            **kwargs,
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
