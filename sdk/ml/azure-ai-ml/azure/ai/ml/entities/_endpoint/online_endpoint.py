# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=no-member

import logging
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, Optional, Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    EndpointAuthMode,
    OnlineEndpointData,
)
from azure.ai.ml._restclient.v2022_02_01_preview.models import OnlineEndpointDetails as RestOnlineEndpoint
from azure.ai.ml._restclient.v2022_05_01.models import ManagedServiceIdentity as RestManagedServiceIdentityConfiguration
from azure.ai.ml._schema._endpoint import KubernetesOnlineEndpointSchema, ManagedOnlineEndpointSchema
from azure.ai.ml._utils.utils import dict_eq
from azure.ai.ml.constants._common import (
    AAD_TOKEN_YAML,
    AML_TOKEN_YAML,
    BASE_PATH_CONTEXT_KEY,
    KEY,
    PARAMS_OVERRIDE_KEY,
)
from azure.ai.ml.constants._endpoint import EndpointYamlFields
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._util import is_compute_in_override, load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    EndpointAuthKeys as RestEndpointAuthKeys,
    EndpointAuthToken as RestEndpointAuthToken
)

from ._endpoint_helpers import validate_endpoint_or_deployment_name, validate_identity_type_defined
from .endpoint import Endpoint

module_logger = logging.getLogger(__name__)


class OnlineEndpoint(Endpoint):
    """Online endpoint entity.

    :param name: Name of the resource.
    :type name: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param auth_mode: Possible values include: "aml_token", "key", defaults to "key"
    :type auth_mode: str, optional
    :param description: Description of the inference endpoint, defaults to None
    :type description: str, optional
    :param location: defaults to None
    :type location: str, optional
    :param traffic:  Traffic rules on how the traffic will be routed across deployments, defaults to {}
    :type traffic: Dict[str, int], optional
    :param mirror_traffic: Duplicated live traffic used to inference a single deployment, defaults to {}
    :type mirror_traffic: Dict[str, int], optional
    :param provisioning_state: str, provisioning state, readonly
    :type provisioning_state: str, optional
    :param identity: defaults to SystemAssigned
    :type identity: IdentityConfiguration, optional
    :param kind: Kind of the resource, we have two kinds: K8s and Managed online endpoints,
        defaults to None.
    :type kind: str, optional
    """

    def __init__(
        self,
        *,
        name: str = None,
        tags: Dict[str, Any] = None,
        properties: Dict[str, Any] = None,
        auth_mode: str = KEY,
        description: str = None,
        location: str = None,
        traffic: Dict[str, int] = None,
        mirror_traffic: Dict[str, int] = None,
        identity: IdentityConfiguration = None,
        scoring_uri: str = None,
        openapi_uri: str = None,
        provisioning_state: str = None,
        kind: str = None,
        **kwargs,
    ):
        self._provisioning_state = kwargs.pop("provisioning_state", None)

        super(OnlineEndpoint, self).__init__(
            name=name,
            properties=properties,
            tags=tags,
            auth_mode=auth_mode,
            description=description,
            location=location,
            scoring_uri=scoring_uri,
            openapi_uri=openapi_uri,
            provisioning_state=provisioning_state,
            **kwargs,
        )

        self.identity = identity
        self.traffic = dict(traffic) if traffic else {}
        self.mirror_traffic = dict(mirror_traffic) if mirror_traffic else {}
        self.kind = kind

    @property
    def provisioning_state(self) -> Optional[str]:
        """Endpoint provisioning state, readonly.

        :return: Endpoint provisioning state.
        :rtype: Optional[str]
        """
        return self._provisioning_state

    def _to_rest_online_endpoint(self, location: str) -> OnlineEndpointData:
        # pylint: disable=protected-access
        identity = (
            self.identity._to_online_endpoint_rest_object()
            if self.identity
            else RestManagedServiceIdentityConfiguration(type="SystemAssigned")
        )
        validate_endpoint_or_deployment_name(self.name)
        validate_identity_type_defined(self.identity)
        properties = RestOnlineEndpoint(
            description=self.description,
            auth_mode=OnlineEndpoint._yaml_auth_mode_to_rest_auth_mode(self.auth_mode),
            properties=self.properties,
            traffic=self.traffic,
            mirror_traffic=self.mirror_traffic,
        )

        if hasattr(self, "public_network_access") and self.public_network_access:
            properties.public_network_access = self.public_network_access
        return OnlineEndpointData(
            location=location,
            properties=properties,
            identity=identity,
            tags=self.tags,
        )

    def _to_rest_online_endpoint_traffic_update(self, location: str, no_validation: bool = False) -> OnlineEndpointData:
        if not no_validation:
            # validate_deployment_name_matches_traffic(self.deployments, self.traffic)
            validate_identity_type_defined(self.identity)
            # validate_uniqueness_of_deployment_names(self.deployments)
        properties = RestOnlineEndpoint(
            description=self.description,
            auth_mode=OnlineEndpoint._yaml_auth_mode_to_rest_auth_mode(self.auth_mode),
            endpoint=self.name,
            traffic=self.traffic,
            properties=self.properties,
        )
        return OnlineEndpointData(
            location=location,
            properties=properties,
            identity=self.identity,
            tags=self.tags,
        )

    @classmethod
    def _rest_auth_mode_to_yaml_auth_mode(cls, rest_auth_mode: str) -> str:
        switcher = {
            EndpointAuthMode.AML_TOKEN: AML_TOKEN_YAML,
            EndpointAuthMode.AAD_TOKEN: AAD_TOKEN_YAML,
            EndpointAuthMode.KEY: KEY,
        }

        return switcher.get(rest_auth_mode, rest_auth_mode)

    @classmethod
    def _yaml_auth_mode_to_rest_auth_mode(cls, yaml_auth_mode: str) -> str:
        yaml_auth_mode = yaml_auth_mode.lower()

        switcher = {
            AML_TOKEN_YAML: EndpointAuthMode.AML_TOKEN,
            AAD_TOKEN_YAML: EndpointAuthMode.AAD_TOKEN,
            KEY: EndpointAuthMode.KEY,
        }

        return switcher.get(yaml_auth_mode, yaml_auth_mode)

    @classmethod
    def _from_rest_object(cls, resource: OnlineEndpointData):  # pylint: disable=arguments-renamed
        auth_mode = cls._rest_auth_mode_to_yaml_auth_mode(resource.properties.auth_mode)
        # pylint: disable=protected-access
        identity = IdentityConfiguration._from_online_endpoint_rest_object(
            resource.identity) if resource.identity else None
        if resource.properties.compute:
            endpoint = KubernetesOnlineEndpoint(
                id=resource.id,
                name=resource.name,
                tags=resource.tags,
                properties=resource.properties.properties,
                compute=resource.properties.compute,
                auth_mode=auth_mode,
                description=resource.properties.description,
                location=resource.location,
                traffic=resource.properties.traffic,
                provisioning_state=resource.properties.provisioning_state,
                scoring_uri=resource.properties.scoring_uri,
                openapi_uri=resource.properties.swagger_uri,
                identity=identity,
                kind=resource.kind,
            )
        else:
            endpoint = ManagedOnlineEndpoint(
                id=resource.id,
                name=resource.name,
                tags=resource.tags,
                properties=resource.properties.properties,
                auth_mode=auth_mode,
                description=resource.properties.description,
                location=resource.location,
                traffic=resource.properties.traffic,
                mirror_traffic=resource.properties.mirror_traffic,
                provisioning_state=resource.properties.provisioning_state,
                scoring_uri=resource.properties.scoring_uri,
                openapi_uri=resource.properties.swagger_uri,
                identity=identity,
                kind=resource.kind,
                public_network_access=resource.properties.public_network_access,
            )

        return endpoint

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OnlineEndpoint):
            return NotImplemented
        if not other:
            return False
        # only compare mutable fields
        return (
            self.name.lower() == other.name.lower()
            and self.auth_mode.lower() == other.auth_mode.lower()
            and dict_eq(self.tags, other.tags)
            and self.description == other.description
            and dict_eq(self.traffic, other.traffic)
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @classmethod
    def _load(
        cls,
        data: Dict = None,
        yaml_path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "Endpoint":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path.cwd(),
            PARAMS_OVERRIDE_KEY: params_override,
        }

        if data.get(EndpointYamlFields.COMPUTE) or is_compute_in_override(params_override):
            return load_from_dict(KubernetesOnlineEndpointSchema, data, context)

        return load_from_dict(ManagedOnlineEndpointSchema, data, context)


class KubernetesOnlineEndpoint(OnlineEndpoint):
    """K8s Online endpoint entity.

    :param name: Name of the resource.
    :type name: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param auth_mode: Possible values include: "aml_token", "key", defaults to "key"
    :type auth_mode: str, optional
    :param description: Description of the inference endpoint, defaults to None
    :type description: str, optional
    :param location: defaults to None
    :type location: str, optional
    :param traffic:  Traffic rules on how the traffic will be routed across deployments, defaults to {}
    :type traffic: Dict[str, int], optional
    :param compute: Compute cluster id.
    :type compute: str, optional
    :param identity: defaults to SystemAssigned
    :type identity: IdentityConfiguration, optional
    :param kind: Kind of the resource, we have two kinds: K8s and Managed online endpoints, defaults to None.
    :type kind: str, optional
    """

    def __init__(
        self,
        *,
        name: str = None,
        tags: Dict[str, Any] = None,
        properties: Dict[str, Any] = None,
        auth_mode: str = KEY,
        description: str = None,
        location: str = None,
        traffic: Dict[str, int] = None,
        mirror_traffic: Dict[str, int] = None,
        compute: str = None,
        identity: IdentityConfiguration = None,
        kind: str = None,
        **kwargs,
    ):
        super(KubernetesOnlineEndpoint, self).__init__(
            name=name,
            properties=properties,
            tags=tags,
            auth_mode=auth_mode,
            description=description,
            location=location,
            traffic=traffic,
            mirror_traffic=mirror_traffic,
            identity=identity,
            kind=kind,
            **kwargs,
        )

        self.compute = compute

    def dump(
        self,
        dest: Union[str, PathLike, IO[AnyStr]] = None,  # pylint: disable=unused-argument
        **kwargs,  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        return KubernetesOnlineEndpointSchema(context=context).dump(self)

    def _to_rest_online_endpoint(self, location: str) -> OnlineEndpointData:
        resource = super()._to_rest_online_endpoint(location)
        resource.properties.compute = self.compute
        return resource

    def _to_rest_online_endpoint_traffic_update(self, location: str, no_validation: bool = False) -> OnlineEndpointData:
        resource = super()._to_rest_online_endpoint_traffic_update(location, no_validation)
        resource.properties.compute = self.compute
        return resource

    def _merge_with(self, other: "KubernetesOnlineEndpoint") -> None:
        if other:
            if self.name != other.name:
                msg = "The endpoint name: {} and {} are not matched when merging."
                raise ValidationException(
                    message=msg.format(self.name, other.name),
                    target=ErrorTarget.ONLINE_ENDPOINT,
                    no_personal_data_message=msg.format("[name1]", "[name2]"),
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
            super()._merge_with(other)
            self.compute = other.compute or self.compute

    def _to_dict(self) -> Dict:
        return KubernetesOnlineEndpointSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)


class ManagedOnlineEndpoint(OnlineEndpoint):
    """Managed Online endpoint entity.

    :param name: Name of the resource.
    :type name: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param auth_mode: Possible values include: "aml_token", "key", defaults to "key"
    :type auth_mode: str, optional
    :param description: Description of the inference endpoint, defaults to None
    :type description: str, optional
    :param location: defaults to None
    :type location: str, optional
    :param traffic:  Traffic rules on how the traffic will be routed across deployments, defaults to {}
    :type traffic: Dict[str, int], optional
    :param identity: defaults to SystemAssigned
    :type identity: IdentityConfiguration, optional
    :param kind: Kind of the resource, we have two kinds: K8s and Managed online endpoints, defaults to None.
    :type kind: str, optional,
    :param public_network_access: Whether to allow public endpoint connectivity
        Allowed values are: "enabled", "disabled"
    :type public_network_access: str
    """

    def __init__(
        self,
        *,
        name: str = None,
        tags: Dict[str, Any] = None,
        properties: Dict[str, Any] = None,
        auth_mode: str = KEY,
        description: str = None,
        location: str = None,
        traffic: Dict[str, int] = None,
        mirror_traffic: Dict[str, int] = None,
        identity: IdentityConfiguration = None,
        kind: str = None,
        public_network_access = None,
        **kwargs,
    ):
        self.public_network_access = public_network_access

        super(ManagedOnlineEndpoint, self).__init__(
            name=name,
            properties=properties,
            tags=tags,
            auth_mode=auth_mode,
            description=description,
            location=location,
            traffic=traffic,
            mirror_traffic=mirror_traffic,
            identity=identity,
            kind=kind,
            **kwargs,
        )

    def dump(
        self,
        dest: Union[str, PathLike, IO[AnyStr]] = None,  # pylint: disable=unused-argument
        **kwargs,  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        return ManagedOnlineEndpointSchema(context=context).dump(self)

    def _to_dict(self) -> Dict:
        return ManagedOnlineEndpointSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)


class EndpointAuthKeys(RestTranslatableMixin):
    """Keys for endpoint authentication.

    :ivar primary_key: The primary key.
    :vartype primary_key: str
    :ivar secondary_key: The secondary key.
    :vartype secondary_key: str
    """

    def __init__(
        self,
        **kwargs
    ):
        """
        :keyword primary_key: The primary key.
        :paramtype primary_key: str
        :keyword secondary_key: The secondary key.
        :paramtype secondary_key: str
        """
        self.primary_key = kwargs.get('primary_key', None)
        self.secondary_key = kwargs.get('secondary_key', None)

    @classmethod
    def _from_rest_object(cls, obj: RestEndpointAuthKeys) -> "EndpointAuthKeys":
        return cls(
            primary_key=obj.primary_key,
            secondary_key=obj.secondary_key
        )

    def _to_rest_object(self) -> RestEndpointAuthKeys:
        return RestEndpointAuthKeys(
            primary_key=self.primary_key,
            secondary_key=self.secondary_key
        )


class EndpointAuthToken(RestTranslatableMixin):
    """Endpoint authentication token.

    :ivar access_token: Access token for endpoint authentication.
    :vartype access_token: str
    :ivar expiry_time_utc: Access token expiry time (UTC).
    :vartype expiry_time_utc: long
    :ivar refresh_after_time_utc: Refresh access token after time (UTC).
    :vartype refresh_after_time_utc: long
    :ivar token_type: Access token type.
    :vartype token_type: str
    """

    def __init__(
        self,
        **kwargs
    ):
        """
        :keyword access_token: Access token for endpoint authentication.
        :paramtype access_token: str
        :keyword expiry_time_utc: Access token expiry time (UTC).
        :paramtype expiry_time_utc: long
        :keyword refresh_after_time_utc: Refresh access token after time (UTC).
        :paramtype refresh_after_time_utc: long
        :keyword token_type: Access token type.
        :paramtype token_type: str
        """
        self.access_token = kwargs.get('access_token', None)
        self.expiry_time_utc = kwargs.get('expiry_time_utc', 0)
        self.refresh_after_time_utc = kwargs.get('refresh_after_time_utc', 0)
        self.token_type = kwargs.get('token_type', None)

    @classmethod
    def _from_rest_object(cls, obj: RestEndpointAuthToken) -> "EndpointAuthToken":
        return cls(
            access_token=obj.access_token,
            expiry_time_utc=obj.expiry_time_utc,
            refresh_after_time_utc=obj.refresh_after_time_utc,
            token_type=obj.token_type,
        )

    def _to_rest_object(self) -> RestEndpointAuthToken:
        return RestEndpointAuthToken(
            access_token=self.access_token,
            expiry_time_utc=self.expiry_time_utc,
            refresh_after_time_utc=self.refresh_after_time_utc,
            token_type=self.token_type,
        )
