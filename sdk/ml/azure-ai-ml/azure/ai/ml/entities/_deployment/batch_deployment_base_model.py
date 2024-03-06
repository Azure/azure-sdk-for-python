# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,arguments-renamed

import logging
from abc import abstractmethod
from os import PathLike
from typing import IO, Any, AnyStr, Dict, Optional, Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import BatchDeploymentData
from azure.ai.ml._restclient.v2022_05_01.models import OnlineDeploymentData
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.exceptions import (
    DeploymentException,
    ErrorCategory,
    ErrorTarget,
)

module_logger = logging.getLogger(__name__)


class BatchDeploymentBaseModel(Resource, RestTranslatableMixin):
    """Endpoint Deployment base class.

    :param name: Name of the deployment resource, defaults to None
    :type name: typing.Optional[str]
    :keyword endpoint_name: Name of the Endpoint resource, defaults to None
    :paramtype endpoint_name: typing.Optional[str]
    :keyword description: Description of the deployment resource, defaults to None
    :paramtype description: typing.Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated, defaults to None
    :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        endpoint_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        type: Optional[str] = None,
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
        """
        # MFE is case-insensitive for Name. So convert the name into lower case here.
        name = name.lower() if name else None

        super().__init__(name, description, tags, **kwargs)

        self.endpoint_name = endpoint_name
        self.type = type


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
    # How do which api and rest objects do we want to except for this _from_rest function ?


    # @classmethod
    # def _from_rest_object(
    #     cls, deployment_rest_object: Union[OnlineDeploymentData, BatchDeploymentData]
    # ) -> Union[OnlineDeploymentData, BatchDeploymentData]:
    #     from azure.ai.ml.entities._deployment.batch_deployment import BatchDeployment
    #     from azure.ai.ml.entities._deployment.online_deployment import OnlineDeployment

    #     if isinstance(deployment_rest_object, OnlineDeploymentData):
    #         return OnlineDeployment._from_rest_object(deployment_rest_object)
    #     if isinstance(deployment_rest_object, BatchDeploymentData):
    #         return BatchDeployment._from_rest_object(deployment_rest_object)

    #     msg = f"Unsupported deployment type {type(deployment_rest_object)}"
    #     raise DeploymentException(
    #         message=msg,
    #         target=ErrorTarget.DEPLOYMENT,
    #         no_personal_data_message=msg,
    #         error_category=ErrorCategory.SYSTEM_ERROR,
    #     )

    def _to_rest_object(self) -> Any:
        pass

