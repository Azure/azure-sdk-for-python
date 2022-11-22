# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,arguments-renamed

import logging
from abc import abstractmethod
from os import PathLike
from typing import IO, Any, AnyStr, Dict, Union

from azure.ai.ml._restclient.v2021_10_01.models import OnlineDeploymentData
from azure.ai.ml._restclient.v2022_02_01_preview.models import BatchDeploymentData
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.exceptions import (
    DeploymentException,
    ErrorCategory,
    ErrorTarget,
    ValidationErrorType,
    ValidationException,
)

from .code_configuration import CodeConfiguration

module_logger = logging.getLogger(__name__)


class Deployment(Resource, RestTranslatableMixin):
    """Endpoint Deployment base class.

    :param name: Name of the resource.
    :type name: str
    :param description: Description of the resource.
    :type description: str, optional
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param model: the Model entity, defaults to None
    :type model: Union[str, Model], optional
    :param code_configuration: the CodeConfiguration entity, defaults to None
    :type code_configuration: CodeConfiguration, optional
    :param environment: the Environment entity, defaults to None
    :type environment: Union[str, Environment], optional
    :param environment_variables: Environment variables that will be set in deployment.
    :type environment_variables: dict, optional
    :param code_path: Folder path to local code assets. Equivalent to code_configuration.code.path.
    :type code_path: Union[str, PathLike], optional
    :param scoring_script: Scoring script name. Equivalent to code_configuration.code.scoring_script.
    :type scoring_script: Union[str, PathLike], optional
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Deployment cannot be successfully validated.
        Details will be provided in the error message.
    """

    def __init__(
        self,
        name: str = None,
        endpoint_name: str = None,
        description: str = None,
        tags: Dict[str, Any] = None,
        properties: Dict[str, Any] = None,
        model: Union[str, "Model"] = None,
        code_configuration: CodeConfiguration = None,
        environment: Union[str, "Environment"] = None,
        environment_variables: Dict[str, str] = None,
        code_path: Union[str, PathLike] = None,
        scoring_script: Union[str, PathLike] = None,
        **kwargs,
    ):
        # MFE is case-insensitive for Name. So convert the name into lower case here.
        name = name.lower() if name else None
        self.endpoint_name = endpoint_name
        self._type = kwargs.pop("type", None)

        if code_configuration and (code_path or scoring_script):
            msg = "code_path and scoring_script are not allowed if code_configuration is provided."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.DEPLOYMENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        super().__init__(name, description, tags, properties, **kwargs)

        self.model = model
        self.code_configuration = code_configuration
        if not self.code_configuration and (code_path or scoring_script):
            self.code_configuration = CodeConfiguration(code=code_path, scoring_script=scoring_script)

        self.environment = environment
        self.environment_variables = dict(environment_variables) if environment_variables else {}

    @property
    def type(self) -> str:
        return self._type

    @property
    def code_path(self) -> Union[str, PathLike]:
        return self.code_configuration.code if self.code_configuration and self.code_configuration.code else None

    @code_path.setter
    def code_path(self, value: Union[str, PathLike]) -> None:
        if not self.code_configuration:
            self.code_configuration = ResourceConfiguration()

        self.code_configuration.code = value

    @property
    def scoring_script(self) -> Union[str, PathLike]:
        return self.code_configuration.scoring_script if self.code_configuration else None

    @scoring_script.setter
    def scoring_script(self, value: Union[str, PathLike]) -> None:
        if not self.code_configuration:
            self.code_configuration = ResourceConfiguration()

        self.code_configuration.scoring_script = value

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs) -> None:
        """Dump the deployment content into a file in yaml format.

        :param dest: The destination to receive this deployment's content.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    @abstractmethod
    def _to_dict(self) -> Dict:
        pass

    @classmethod
    def _from_rest_object(cls, deployment_rest_object: Union[OnlineDeploymentData, BatchDeploymentData]):
        from azure.ai.ml.entities._deployment.batch_deployment import BatchDeployment
        from azure.ai.ml.entities._deployment.online_deployment import OnlineDeployment

        if isinstance(deployment_rest_object, OnlineDeploymentData):
            return OnlineDeployment._from_rest_object(deployment_rest_object)
        if isinstance(deployment_rest_object, BatchDeploymentData):
            return BatchDeployment._from_rest_object(deployment_rest_object)

        msg = f"Unsupported deployment type {type(deployment_rest_object)}"
        raise DeploymentException(
            message=msg,
            target=ErrorTarget.DEPLOYMENT,
            no_personal_data_message=msg,
            error_category=ErrorCategory.SYSTEM_ERROR,
        )

    def _to_rest_object(self) -> Any:
        pass

    def _merge_with(self, other: "Deployment") -> None:
        if other:
            if self.name != other.name:
                msg = "The deployment name: {} and {} are not matched when merging."
                raise ValidationException(
                    message=msg.format(self.name, other.name),
                    target=ErrorTarget.DEPLOYMENT,
                    no_personal_data_message=msg.format("[name1]", "[name2]"),
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
            if other.tags:
                self.tags = {**self.tags, **other.tags}
            if other.properties:
                self.properties = {**self.properties, **other.properties}
            if other.environment_variables:
                self.environment_variables = {
                    **self.environment_variables,
                    **other.environment_variables,
                }
            self.code_configuration = other.code_configuration or self.code_configuration
            self.model = other.model or self.model
            self.environment = other.environment or self.environment
            self.endpoint_name = other.endpoint_name or self.endpoint_name
