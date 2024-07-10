# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,arguments-renamed

import logging
from abc import abstractmethod
from os import PathLike
from typing import IO, TYPE_CHECKING, Any, AnyStr, Dict, Optional, Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import BatchDeploymentData
from azure.ai.ml._restclient.v2022_05_01.models import OnlineDeploymentData
from azure.ai.ml._utils.utils import dump_yaml_to_file
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

# avoid circular import error
if TYPE_CHECKING:
    from azure.ai.ml.entities._assets._artifacts.model import Model
    from azure.ai.ml.entities._assets.environment import Environment

module_logger = logging.getLogger(__name__)


class Deployment(Resource, RestTranslatableMixin):
    """Endpoint Deployment base class.

    :param name: Name of the deployment resource, defaults to None
    :type name: typing.Optional[str]
    :keyword endpoint_name: Name of the Endpoint resource, defaults to None
    :paramtype endpoint_name: typing.Optional[str]
    :keyword description: Description of the deployment resource, defaults to None
    :paramtype description: typing.Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated, defaults to None
    :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword properties: The asset property dictionary, defaults to None
    :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword model: The Model entity, defaults to None
    :paramtype model: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Model]]
    :keyword code_configuration: Code Configuration, defaults to None
    :paramtype code_configuration: typing.Optional[CodeConfiguration]
    :keyword environment: The Environment entity, defaults to None
    :paramtype environment: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Environment]]
    :keyword environment_variables: Environment variables that will be set in deployment, defaults to None
    :paramtype environment_variables: typing.Optional[typing.Dict[str, str]]
    :keyword code_path: Folder path to local code assets. Equivalent to code_configuration.code.path
        , defaults to None
    :paramtype code_path: typing.Optional[typing.Union[str, PathLike]]
    :keyword scoring_script: Scoring script name. Equivalent to code_configuration.code.scoring_script
        , defaults to None
    :paramtype scoring_script: typing.Optional[typing.Union[str, PathLike]]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Deployment cannot be successfully validated.
        Exception details will be provided in the error message.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        endpoint_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        properties: Optional[Dict[str, Any]] = None,
        model: Optional[Union[str, "Model"]] = None,
        code_configuration: Optional[CodeConfiguration] = None,
        environment: Optional[Union[str, "Environment"]] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        code_path: Optional[Union[str, PathLike]] = None,
        scoring_script: Optional[Union[str, PathLike]] = None,
        **kwargs: Any,
    ):
        """Endpoint Deployment base class.

        Constructor of Endpoint Deployment base class.

        :param name: Name of the deployment resource, defaults to None
        :type name: typing.Optional[str]
        :keyword endpoint_name: Name of the Endpoint resource, defaults to None
        :paramtype endpoint_name: typing.Optional[str]
        :keyword description: Description of the deployment resource, defaults to None
        :paramtype description: typing.Optional[str]
        :keyword tags: Tag dictionary. Tags can be added, removed, and updated, defaults to None
        :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword properties: The asset property dictionary, defaults to None
        :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword model: The Model entity, defaults to None
        :paramtype model: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Model]]
        :keyword code_configuration: Code Configuration, defaults to None
        :paramtype code_configuration: typing.Optional[CodeConfiguration]
        :keyword environment: The Environment entity, defaults to None
        :paramtype environment: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Environment]]
        :keyword environment_variables: Environment variables that will be set in deployment, defaults to None
        :paramtype environment_variables: typing.Optional[typing.Dict[str, str]]
        :keyword code_path: Folder path to local code assets. Equivalent to code_configuration.code.path
            , defaults to None
        :paramtype code_path: typing.Optional[typing.Union[str, PathLike]]
        :keyword scoring_script: Scoring script name. Equivalent to code_configuration.code.scoring_script
            , defaults to None
        :paramtype scoring_script: typing.Optional[typing.Union[str, PathLike]]
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Deployment cannot be successfully validated.
            Exception details will be provided in the error message.
        """
        # MFE is case-insensitive for Name. So convert the name into lower case here.
        name = name.lower() if name else None
        self.endpoint_name = endpoint_name
        self._type: Optional[str] = kwargs.pop("type", None)

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
    def type(self) -> Optional[str]:
        """
        Type of deployment.

        :rtype: str
        """
        return self._type

    @property
    def code_path(self) -> Optional[Union[str, PathLike]]:
        """
        The code directory containing the scoring script.

        :rtype: Union[str, PathLike]
        """
        return self.code_configuration.code if self.code_configuration and self.code_configuration.code else None

    @code_path.setter
    def code_path(self, value: Union[str, PathLike]) -> None:
        if not self.code_configuration:
            self.code_configuration = CodeConfiguration()

        self.code_configuration.code = value

    @property
    def scoring_script(self) -> Optional[Union[str, PathLike]]:
        """
        The scoring script file path relative to the code directory.

        :rtype: Union[str, PathLike]
        """
        return self.code_configuration.scoring_script if self.code_configuration else None

    @scoring_script.setter
    def scoring_script(self, value: Union[str, PathLike]) -> None:
        if not self.code_configuration:
            self.code_configuration = CodeConfiguration()

        self.code_configuration.scoring_script = value  # type: ignore[misc]

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> None:
        """Dump the deployment content into a file in yaml format.

        :param dest: The destination to receive this deployment's content.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: typing.Union[os.PathLike, str, typing.IO[typing.AnyStr]]
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    @abstractmethod
    def _to_dict(self) -> Dict:
        pass

    @classmethod
    def _from_rest_object(
        cls, deployment_rest_object: Union[OnlineDeploymentData, BatchDeploymentData]
    ) -> Union[OnlineDeploymentData, BatchDeploymentData]:
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
                self.tags: dict = {**self.tags, **other.tags}
            if other.properties:
                self.properties: dict = {**self.properties, **other.properties}
            if other.environment_variables:
                self.environment_variables = {
                    **self.environment_variables,
                    **other.environment_variables,
                }
            self.code_configuration = other.code_configuration or self.code_configuration
            self.model = other.model or self.model
            self.environment = other.environment or self.environment
            self.endpoint_name = other.endpoint_name or self.endpoint_name
