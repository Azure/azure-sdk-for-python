# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access, too-many-instance-attributes

import os
from pathlib import Path
from typing import Dict, Optional, Union

import yaml

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2023_04_01_preview.models import BuildContext as RestBuildContext
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    EnvironmentContainer,
    EnvironmentVersion,
    EnvironmentVersionProperties,
)
from azure.ai.ml._schema import EnvironmentSchema
from azure.ai.ml._utils._arm_id_utils import AMLVersionedArmId
from azure.ai.ml._utils._asset_utils import get_ignore_file, get_object_hash
from azure.ai.ml._utils.utils import dump_yaml, is_url, load_file, load_yaml
from azure.ai.ml.constants._common import ANONYMOUS_ENV_NAME, BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, ArmConstants
from azure.ai.ml.entities._assets.asset import Asset
from azure.ai.ml.entities._assets.intellectual_property import IntellectualProperty
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import get_md5_string, load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException


class BuildContext:
    """Docker build context for Environment.

    :param path: The local or remote path to the the docker build context directory.
    :type path: Union[str, os.PathLike]
    :param dockerfile_path: The path to the dockerfile relative to root of docker build context directory.
    :type dockerfile_path: str
    """

    def __init__(
        self,
        *,
        dockerfile_path: Optional[str] = None,
        path: Optional[Union[str, os.PathLike]] = None,
    ):
        self.dockerfile_path = dockerfile_path
        self.path = path

    def _to_rest_object(self) -> RestBuildContext:
        return RestBuildContext(context_uri=self.path, dockerfile_path=self.dockerfile_path)

    @classmethod
    def _from_rest_object(cls, rest_obj: RestBuildContext) -> None:
        return BuildContext(
            path=rest_obj.context_uri,
            dockerfile_path=rest_obj.dockerfile_path,
        )

    def __eq__(self, other) -> bool:
        return self.dockerfile_path == other.dockerfile_path and self.path == other.path

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class Environment(Asset):
    """Environment for training.

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the asset.
    :type version: str
    :param description: Description of the resource.
    :type description: str
    :param image: URI of a custom base image.
    :type image: str
    :param build: Docker build context to create the environment. Mutually exclusive with "image"
    :type build: BuildContext
    :param conda_file: Path to configuration file listing conda packages to install.
    :type conda_file: Optional[str, os.Pathlike]
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param datastore: The datastore to upload the local artifact to.
    :type datastore: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        image: Optional[str] = None,
        build: Optional[BuildContext] = None,
        conda_file: Optional[Union[str, os.PathLike]] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        datastore: Optional[str] = None,
        **kwargs,
    ):
        inference_config = kwargs.pop("inference_config", None)
        os_type = kwargs.pop("os_type", None)
        self._intellectual_property = kwargs.pop("intellectual_property", None)

        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            properties=properties,
            **kwargs,
        )

        self.conda_file = conda_file
        self.image = image
        self.build = build
        self.inference_config = inference_config
        self.os_type = os_type
        self._arm_type = ArmConstants.ENVIRONMENT_VERSION_TYPE
        self._conda_file_path = (
            _resolve_path(base_path=self.base_path, input=conda_file)
            if isinstance(conda_file, (os.PathLike, str))
            else None
        )
        self.path = None
        self.datastore = datastore
        self._upload_hash = None

        self._translated_conda_file = None
        if self.conda_file:
            self._translated_conda_file = dump_yaml(self.conda_file, sort_keys=True)  # service needs str representation

        if self.build and self.build.path and not is_url(self.build.path):
            path = Path(self.build.path)
            if not path.is_absolute():
                path = Path(self.base_path, path).resolve()
            self.path = path

        if self._is_anonymous:
            if self.path:
                self._ignore_file = get_ignore_file(path)
                self._upload_hash = get_object_hash(path, self._ignore_file)
                self._generate_anonymous_name_version(source="build")
            elif self.image:
                self._generate_anonymous_name_version(
                    source="image", conda_file=self._translated_conda_file, inference_config=self.inference_config
                )

    @property
    def conda_file(self) -> Dict:
        """Conda environment specification.

        :return: Conda dependencies loaded from `conda_file` param.
        :rtype: Dict
        """
        return self._conda_file

    @conda_file.setter
    def conda_file(self, value: Union[str, os.PathLike, Dict]) -> None:
        """Set conda environment specification.

        :param value: A path to a local conda dependencies yaml file or a loaded yaml dictionary of dependencies.
        :type value: Union[str, os.PathLike, Dict]
        :return: None
        """
        if not isinstance(value, Dict):
            value = _deserialize(self.base_path, value, is_conda=True)
        self._conda_file = value

    @classmethod
    def _load(
        cls,
        data: Optional[dict] = None,
        yaml_path: Optional[Union[os.PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "Environment":
        params_override = params_override or []
        data = data or {}
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return load_from_dict(EnvironmentSchema, data, context, **kwargs)

    def _to_rest_object(self) -> EnvironmentVersion:
        self.validate()
        environment_version = EnvironmentVersionProperties()
        if self.conda_file:
            environment_version.conda_file = self._translated_conda_file
        if self.image:
            environment_version.image = self.image
        if self.build:
            environment_version.build = self.build._to_rest_object()
        if self.os_type:
            environment_version.os_type = self.os_type
        if self.tags:
            environment_version.tags = self.tags
        if self._is_anonymous:
            environment_version.is_anonymous = self._is_anonymous
        if self.inference_config:
            environment_version.inference_config = self.inference_config
        if self.description:
            environment_version.description = self.description
        if self.properties:
            environment_version.properties = self.properties

        environment_version_resource = EnvironmentVersion(properties=environment_version)

        return environment_version_resource

    @classmethod
    def _from_rest_object(cls, env_rest_object: EnvironmentVersion) -> "Environment":
        rest_env_version = env_rest_object.properties
        arm_id = AMLVersionedArmId(arm_id=env_rest_object.id)

        environment = Environment(
            id=env_rest_object.id,
            name=arm_id.asset_name,
            version=arm_id.asset_version,
            description=rest_env_version.description,
            tags=rest_env_version.tags,
            creation_context=SystemData._from_rest_object(env_rest_object.system_data)
            if env_rest_object.system_data
            else None,
            is_anonymous=rest_env_version.is_anonymous,
            image=rest_env_version.image,
            os_type=rest_env_version.os_type,
            inference_config=rest_env_version.inference_config,
            build=BuildContext._from_rest_object(rest_env_version.build) if rest_env_version.build else None,
            properties=rest_env_version.properties,
            intellectual_property=IntellectualProperty._from_rest_object(rest_env_version.intellectual_property)
            if rest_env_version.intellectual_property
            else None,
        )

        if rest_env_version.conda_file:
            translated_conda_file = yaml.safe_load(rest_env_version.conda_file)
            environment.conda_file = translated_conda_file
            environment._translated_conda_file = rest_env_version.conda_file

        return environment

    @classmethod
    def _from_container_rest_object(cls, env_container_rest_object: EnvironmentContainer) -> "Environment":
        env = Environment(
            name=env_container_rest_object.name,
            version="1",
            id=env_container_rest_object.id,
            creation_context=SystemData._from_rest_object(env_container_rest_object.system_data),
        )
        env.latest_version = env_container_rest_object.properties.latest_version

        # Setting version to None since if version is not provided it is defaulted to "1".
        # This should go away once container concept is finalized.
        env.version = None
        return env

    def _to_arm_resource_param(self, **kwargs):  # pylint: disable=unused-argument
        properties = self._to_rest_object().properties

        return {
            self._arm_type: {
                ArmConstants.NAME: self.name,
                ArmConstants.VERSION: self.version,
                ArmConstants.PROPERTIES_PARAMETER_NAME: self._serialize.body(properties, "EnvironmentVersion"),
            }
        }

    def _to_dict(self) -> Dict:
        return EnvironmentSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)  # pylint: disable=no-member

    def validate(self):
        if self.name is None:
            msg = "Environment name is required"
            err = ValidationException(
                message=msg,
                target=ErrorTarget.ENVIRONMENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )
            log_and_raise_error(err)
        if self.image is None and self.build is None:
            msg = "Docker image or Dockerfile is required for environments"
            err = ValidationException(
                message=msg,
                target=ErrorTarget.ENVIRONMENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )
            log_and_raise_error(err)
        if self.image and self.build:
            msg = "Docker image or Dockerfile should be provided not both"
            err = ValidationException(
                message=msg,
                target=ErrorTarget.ENVIRONMENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
            log_and_raise_error(err)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Environment):
            return NotImplemented
        return (
            self.name == other.name
            and self.id == other.id
            and self.version == other.version
            and self.description == other.description
            and self.tags == other.tags
            and self.properties == other.properties
            and self.base_path == other.base_path
            and self.image == other.image
            and self.build == other.build
            and self.conda_file == other.conda_file
            and self.inference_config == other.inference_config
            and self._is_anonymous == other._is_anonymous
            and self.os_type == other.os_type
            and self._intellectual_property == other._intellectual_property
        )

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def _generate_anonymous_name_version(
        self, source: str, conda_file: Optional[str] = None, inference_config: Optional[Dict] = None
    ):
        hash_str = ""
        if source == "image":
            hash_str = hash_str.join(get_md5_string(self.image))
            if inference_config:
                hash_str = hash_str.join(get_md5_string(yaml.dump(inference_config, sort_keys=True)))
            if conda_file:
                hash_str = hash_str.join(get_md5_string(conda_file))
        if source == "build":
            if not self.build.dockerfile_path:
                hash_str = hash_str.join(get_md5_string(self._upload_hash))
            else:
                hash_str = hash_str.join(get_md5_string(self._upload_hash)).join(
                    get_md5_string(self.build.dockerfile_path)
                )
        version_hash = get_md5_string(hash_str)
        self.version = version_hash
        self.name = ANONYMOUS_ENV_NAME


# TODO: Remove _DockerBuild and _DockerConfiguration classes once local endpoint moves to using updated env
class _DockerBuild:
    """Helper class to encapsulate Docker build info for Environment."""

    def __init__(
        self,
        base_path: Optional[Union[str, os.PathLike]] = None,
        dockerfile: Optional[str] = None,
    ):
        self.dockerfile = _deserialize(base_path, dockerfile)

    @classmethod
    def _to_rest_object(cls):
        return None

    def _from_rest_object(self, rest_obj) -> None:
        self.dockerfile = rest_obj.dockerfile

    def __eq__(self, other) -> bool:
        return self.dockerfile == other.dockerfile

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


def _deserialize(
    base_path: Union[str, os.PathLike],
    input: Union[str, os.PathLike, Dict],  # pylint: disable=redefined-builtin
    is_conda: bool = False,
) -> Union[str, Dict]:
    """Deserialize user input files for conda and docker.

    :param base_path: The base path for all files supplied by user.
    :type base_path: Union[str, os.PathLike]
    :param input: Input to be deserialized. Will be either dictionary of file contents or path to file.
    :type input: Union[str, os.PathLike, Dict[str, str]]
    :param is_conda: If file is conda file, it will be returned as dictionary
    :type is_conda: bool
    :return: Union[str, Dict]
    """

    if input:
        path = _resolve_path(base_path=base_path, input=input)
        if is_conda:
            data = load_yaml(path)
        else:
            data = load_file(path)
        return data
    return input


def _resolve_path(
    base_path: Union[str, os.PathLike], input: Union[str, os.PathLike, Dict]
):  # pylint: disable=redefined-builtin
    """Deserialize user input files for conda and docker.

    :param base_path: The base path for all files supplied by user.
    :type base_path: Union[str, os.PathLike]
    :param input: Input to be deserialized. Will be either dictionary of file contents or path to file.
    :type input: Union[str, os.PathLike, Dict[str, str]]
    """

    path = Path(input)
    if not path.is_absolute():
        path = Path(base_path, path).resolve()
    return path
