# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from abc import abstractmethod
from os import PathLike
from typing import IO, Any, AnyStr, Dict, Optional, Union

from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

module_logger = logging.getLogger(__name__)


class Endpoint(Resource):  # pylint: disable=too-many-instance-attributes
    """Endpoint base class.

    :param auth_mode: The authentication mode, defaults to None
    :type auth_mode: str
    :param location: The location of the endpoint, defaults to None
    :type location: str
    :param name: Name of the resource.
    :type name: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: typing.Optional[typing.Dict[str, str]]
    :param properties: The asset property dictionary.
    :type properties: typing.Optional[typing.Dict[str, str]]
    :param description: Description of the resource.
    :type description: typing.Optional[str]
    :keyword traffic: Traffic rules on how the traffic will be routed across deployments, defaults to {}
    :paramtype traffic: typing.Optional[typing.Dict[str, int]]
    :keyword scoring_uri: str, Endpoint URI, readonly
    :paramtype scoring_uri: typing.Optional[str]
    :keyword openapi_uri: str, Endpoint Open API URI, readonly
    :paramtype openapi_uri: typing.Optional[str]
    :keyword provisioning_state: str, provisioning state, readonly
    :paramtype provisioning_state: typing.Optional[str]
    """

    def __init__(
        self,
        auth_mode: Optional[str] = None,
        location: Optional[str] = None,
        name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ):
        """Endpoint base class.

        Constructor for Endpoint base class.

        :param auth_mode: The authentication mode, defaults to None
        :type auth_mode: str
        :param location: The location of the endpoint, defaults to None
        :type location: str
        :param name: Name of the resource.
        :type name: str
        :param tags: Tag dictionary. Tags can be added, removed, and updated.
        :type tags: typing.Optional[typing.Dict[str, str]]
        :param properties: The asset property dictionary.
        :type properties: typing.Optional[typing.Dict[str, str]]
        :param description: Description of the resource.
        :type description: typing.Optional[str]
        :keyword traffic: Traffic rules on how the traffic will be routed across deployments, defaults to {}
        :paramtype traffic: typing.Optional[typing.Dict[str, int]]
        :keyword scoring_uri: str, Endpoint URI, readonly
        :paramtype scoring_uri: typing.Optional[str]
        :keyword openapi_uri: str, Endpoint Open API URI, readonly
        :paramtype openapi_uri: typing.Optional[str]
        :keyword provisioning_state: str, provisioning state, readonly
        :paramtype provisioning_state: typing.Optional[str]
        """
        # MFE is case-insensitive for Name. So convert the name into lower case here.
        if name:
            name = name.lower()
        self._scoring_uri: Optional[str] = kwargs.pop("scoring_uri", None)
        self._openapi_uri: Optional[str] = kwargs.pop("openapi_uri", None)
        self._provisioning_state: Optional[str] = kwargs.pop("provisioning_state", None)
        super().__init__(name, description, tags, properties, **kwargs)
        self.auth_mode = auth_mode
        self.location = location

    @property
    def scoring_uri(self) -> Optional[str]:
        """URI to use to perform a prediction, readonly.

        :return: The scoring URI
        :rtype: typing.Optional[str]
        """
        return self._scoring_uri

    @property
    def openapi_uri(self) -> Optional[str]:
        """URI to check the open api definition of the endpoint.

        :return: The open API URI
        :rtype: typing.Optional[str]
        """
        return self._openapi_uri

    @property
    def provisioning_state(self) -> Optional[str]:
        """Endpoint provisioning state, readonly.

        :return: Endpoint provisioning state.
        :rtype: typing.Optional[str]
        """
        return self._provisioning_state

    @abstractmethod
    def dump(self, dest: Optional[Union[str, PathLike, IO[AnyStr]]] = None, **kwargs: Any) -> Dict:
        pass

    @classmethod
    @abstractmethod
    def _from_rest_object(cls, obj: Any) -> Any:
        pass

    def _merge_with(self, other: Any) -> None:
        if other:
            if self.name != other.name:
                msg = "The endpoint name: {} and {} are not matched when merging."
                raise ValidationException(
                    message=msg.format(self.name, other.name),
                    target=ErrorTarget.ENDPOINT,
                    no_personal_data_message=msg.format("[name1]", "[name2]"),
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
            self.description = other.description or self.description
            if other.tags:
                if self.tags is not None:
                    self.tags = {**self.tags, **other.tags}
            if other.properties:
                self.properties = {**self.properties, **other.properties}
            self.auth_mode = other.auth_mode or self.auth_mode
            if hasattr(other, "traffic"):
                self.traffic = other.traffic  # pylint: disable=attribute-defined-outside-init
            if hasattr(other, "mirror_traffic"):
                self.mirror_traffic = other.mirror_traffic  # pylint: disable=attribute-defined-outside-init
            if hasattr(other, "defaults"):
                self.defaults = other.defaults  # pylint: disable=attribute-defined-outside-init
