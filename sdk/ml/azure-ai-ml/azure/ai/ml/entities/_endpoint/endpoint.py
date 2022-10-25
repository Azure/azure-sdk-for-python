# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from abc import abstractmethod
from os import PathLike
from typing import IO, Any, AnyStr, Dict, Optional, Union

from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

module_logger = logging.getLogger(__name__)


class Endpoint(Resource):  # pylint: disable=too-many-instance-attributes
    """Endpoint base class.

    :param auth_mode: the authentication mode, defaults to None
    :type auth_mode: str, optional
    :param location: defaults to None
    :type location: str, optional
    :param traffic: Traffic rules on how the traffic will be routed across deployments, defaults to {}
    :type traffic: Dict[str, int], optional
    :param name: Name of the resource.
    :type name: str, optional
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param scoring_uri: str, Endpoint URI, readonly
    :type scoring_uri: str, optional
    :param openapi_uri: str, Endpoint Open API URI, readonly
    :type openapi_uri: str, optional
    :param provisioning_state: str, provisioning state, readonly
    :type provisioning_state: str, optional
    :param description: Description of the resource.
    :type description: str, optional
    """

    def __init__(
        self,
        auth_mode: str = None,
        location: str = None,
        name: str = None,
        tags: Dict[str, str] = None,
        properties: Dict[str, Any] = None,
        description: str = None,
        **kwargs,
    ):
        # MFE is case-insensitive for Name. So convert the name into lower case here.
        if name:
            name = name.lower()
        self._scoring_uri = kwargs.pop("scoring_uri", None)
        self._openapi_uri = kwargs.pop("openapi_uri", None)
        self._provisioning_state = kwargs.pop("provisioning_state", None)
        super().__init__(name, description, tags, properties, **kwargs)
        self.auth_mode = auth_mode
        self.location = location

    @property
    def scoring_uri(self) -> Optional[str]:
        """URI to use to perform a prediction, readonly.

        :return: The scoring URI
        :rtype: Optional[str]
        """
        return self._scoring_uri

    @property
    def openapi_uri(self) -> Optional[str]:
        """URI to check the open api definition of the endpoint.

        :return: The open API URI
        :rtype: Optional[str]
        """
        return self._openapi_uri

    @property
    def provisioning_state(self) -> Optional[str]:
        """Endpoint provisioning state, readonly.

        :return: Endpoint provisioning state.
        :rtype: Optional[str]
        """
        return self._provisioning_state

    @abstractmethod
    def dump(self, dest: Union[str, PathLike, IO[AnyStr]] = None, **kwargs) -> None:
        pass

    @abstractmethod
    def _from_rest_object(self, obj: Any) -> Any:
        pass

    def _merge_with(self, other: "Endpoint") -> None:
        if other:
            if self.name != other.name:
                msg = "The endpoint name: {} and {} are not matched when merging."
                raise ValidationException(
                    message=msg.format(self.name, other.name),
                    target=ErrorTarget.ENDPOINT,
                    no_personal_data_message=msg.format("[name1]", "[name2]"),
                    error_category=ErrorCategory.USER_ERROR,
                )
            self.description = other.description or self.description
            if other.tags:
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
