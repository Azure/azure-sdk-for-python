# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=no-member

import logging
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, Optional, Union, cast

from azure.ai.ml._restclient.v2022_02_01_preview.models import EndpointAuthKeys as RestEndpointAuthKeys
from azure.ai.ml._restclient.v2022_02_01_preview.models import EndpointAuthMode
from azure.ai.ml._restclient.v2022_02_01_preview.models import EndpointAuthToken as RestEndpointAuthToken
from azure.ai.ml._restclient.v2022_02_01_preview.models import OnlineEndpointData
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
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._util import is_compute_in_override, load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.core.credentials import AccessToken

from ._endpoint_helpers import validate_endpoint_or_deployment_name, validate_identity_type_defined
from .endpoint import Endpoint

module_logger = logging.getLogger(__name__)


class OnlineEndpoint(Endpoint):
    """Online endpoint entity.

    :keyword name: Name of the resource, defaults to None
    :paramtype name: typing.Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated. defaults to None
    :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword properties: The asset property dictionary, defaults to None
    :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword auth_mode: Possible values include: "aml_token", "key", defaults to KEY
    :type auth_mode: typing.Optional[str]
    :keyword description: Description of the inference endpoint, defaults to None
    :paramtype description: typing.Optional[str]
    :keyword location: Location of the resource, defaults to None
    :paramtype location: typing.Optional[str]
    :keyword traffic: Traffic rules on how the traffic will be routed across deployments, defaults to None
    :paramtype traffic: typing.Optional[typing.Dict[str, int]]
    :keyword mirror_traffic: Duplicated live traffic used to inference a single deployment, defaults to None
    :paramtype mirror_traffic: typing.Optional[typing.Dict[str, int]]
    :keyword identity: Identity Configuration, defaults to SystemAssigned
    :paramtype identity: typing.Optional[IdentityConfiguration]
    :keyword scoring_uri: Scoring URI, defaults to None
    :paramtype scoring_uri: typing.Optional[str]
    :keyword openapi_uri: OpenAPI URI, defaults to None
    :paramtype openapi_uri: typing.Optional[str]
    :keyword provisioning_state: Provisioning state of an endpoint, defaults to None
    :paramtype provisioning_state: typing.Optional[str]
    :keyword kind: Kind of the resource, we have two kinds: K8s and Managed online endpoints, defaults to None
    :paramtype kind: typing.Optional[str]
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        properties: Optional[Dict[str, Any]] = None,
        auth_mode: str = KEY,
        description: Optional[str] = None,
        location: Optional[str] = None,
        traffic: Optional[Dict[str, int]] = None,
        mirror_traffic: Optional[Dict[str, int]] = None,
        identity: Optional[IdentityConfiguration] = None,
        scoring_uri: Optional[str] = None,
        openapi_uri: Optional[str] = None,
        provisioning_state: Optional[str] = None,
        kind: Optional[str] = None,
        **kwargs: Any,
    ):
        """Online endpoint entity.

        Constructor for an Online endpoint entity.

        :keyword name: Name of the resource, defaults to None
        :paramtype name: typing.Optional[str]
        :keyword tags: Tag dictionary. Tags can be added, removed, and updated. defaults to None
        :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword properties: The asset property dictionary, defaults to None
        :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword auth_mode: Possible values include: "aml_token", "key", defaults to KEY
        :type auth_mode: typing.Optional[str]
        :keyword description: Description of the inference endpoint, defaults to None
        :paramtype description: typing.Optional[str]
        :keyword location: Location of the resource, defaults to None
        :paramtype location: typing.Optional[str]
        :keyword traffic: Traffic rules on how the traffic will be routed across deployments, defaults to None
        :paramtype traffic: typing.Optional[typing.Dict[str, int]]
        :keyword mirror_traffic: Duplicated live traffic used to inference a single deployment, defaults to None
        :paramtype mirror_traffic: typing.Optional[typing.Dict[str, int]]
        :keyword identity: Identity Configuration, defaults to SystemAssigned
        :paramtype identity: typing.Optional[IdentityConfiguration]
        :keyword scoring_uri: Scoring URI, defaults to None
        :paramtype scoring_uri: typing.Optional[str]
        :keyword openapi_uri: OpenAPI URI, defaults to None
        :paramtype openapi_uri: typing.Optional[str]
        :keyword provisioning_state: Provisioning state of an endpoint, defaults to None
        :paramtype provisioning_state: typing.Optional[str]
        :keyword kind: Kind of the resource, we have two kinds: K8s and Managed online endpoints, defaults to None
        :type kind: typing.Optional[str]
        """
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
        self.traffic: Dict = dict(traffic) if traffic else {}
        self.mirror_traffic: Dict = dict(mirror_traffic) if mirror_traffic else {}
        self.kind = kind

    @property
    def provisioning_state(self) -> Optional[str]:
        """Endpoint provisioning state, readonly.

        :return: Endpoint provisioning state.
        :rtype: typing.Optional[str]
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
    def _yaml_auth_mode_to_rest_auth_mode(cls, yaml_auth_mode: Optional[str]) -> str:
        if yaml_auth_mode is None:
            return ""

        yaml_auth_mode = yaml_auth_mode.lower()

        switcher = {
            AML_TOKEN_YAML: EndpointAuthMode.AML_TOKEN,
            AAD_TOKEN_YAML: EndpointAuthMode.AAD_TOKEN,
            KEY: EndpointAuthMode.KEY,
        }

        return switcher.get(yaml_auth_mode, yaml_auth_mode)

    @classmethod
    def _from_rest_object(cls, obj: OnlineEndpointData) -> "OnlineEndpoint":
        auth_mode = cls._rest_auth_mode_to_yaml_auth_mode(obj.properties.auth_mode)
        # pylint: disable=protected-access
        identity = IdentityConfiguration._from_online_endpoint_rest_object(obj.identity) if obj.identity else None

        endpoint: Any = KubernetesOnlineEndpoint()

        if obj.system_data:
            properties_dict = {
                "createdBy": obj.system_data.created_by,
                "createdAt": obj.system_data.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
                "lastModifiedAt": obj.system_data.last_modified_at.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
            }
            properties_dict.update(obj.properties.properties)
        else:
            properties_dict = obj.properties.properties

        if obj.properties.compute:
            endpoint = KubernetesOnlineEndpoint(
                id=obj.id,
                name=obj.name,
                tags=obj.tags,
                properties=properties_dict,
                compute=obj.properties.compute,
                auth_mode=auth_mode,
                description=obj.properties.description,
                location=obj.location,
                traffic=obj.properties.traffic,
                provisioning_state=obj.properties.provisioning_state,
                scoring_uri=obj.properties.scoring_uri,
                openapi_uri=obj.properties.swagger_uri,
                identity=identity,
                kind=obj.kind,
            )
        else:
            endpoint = ManagedOnlineEndpoint(
                id=obj.id,
                name=obj.name,
                tags=obj.tags,
                properties=properties_dict,
                auth_mode=auth_mode,
                description=obj.properties.description,
                location=obj.location,
                traffic=obj.properties.traffic,
                mirror_traffic=obj.properties.mirror_traffic,
                provisioning_state=obj.properties.provisioning_state,
                scoring_uri=obj.properties.scoring_uri,
                openapi_uri=obj.properties.swagger_uri,
                identity=identity,
                kind=obj.kind,
                public_network_access=obj.properties.public_network_access,
            )

        return cast(OnlineEndpoint, endpoint)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OnlineEndpoint):
            return NotImplemented
        if not other:
            return False
        if self.auth_mode is None or other.auth_mode is None:
            return False

        if self.name is None and other.name is None:
            return (
                self.auth_mode.lower() == other.auth_mode.lower()
                and dict_eq(self.tags, other.tags)
                and self.description == other.description
                and dict_eq(self.traffic, other.traffic)
            )

        if self.name is not None and other.name is not None:
            # only compare mutable fields
            return (
                self.name.lower() == other.name.lower()
                and self.auth_mode.lower() == other.auth_mode.lower()
                and dict_eq(self.tags, other.tags)
                and self.description == other.description
                and dict_eq(self.traffic, other.traffic)
            )

        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "Endpoint":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path.cwd(),
            PARAMS_OVERRIDE_KEY: params_override,
        }

        if data.get(EndpointYamlFields.COMPUTE) or is_compute_in_override(params_override):
            res_kub: Endpoint = load_from_dict(KubernetesOnlineEndpointSchema, data, context)
            return res_kub

        res_managed: Endpoint = load_from_dict(ManagedOnlineEndpointSchema, data, context)
        return res_managed


class KubernetesOnlineEndpoint(OnlineEndpoint):
    """K8s Online endpoint entity.

    :keyword name: Name of the resource, defaults to None
    :paramtype name: typing.Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated, defaults to None
    :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword properties: The asset property dictionary, defaults to None
    :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword auth_mode: Possible values include: "aml_token", "key", defaults to KEY
    :type auth_mode: typing.Optional[str]
    :keyword description: Description of the inference endpoint, defaults to None
    :paramtype description: typing.Optional[str]
    :keyword location: Location of the resource, defaults to None
    :paramtype location: typing.Optional[str]
    :keyword traffic: Traffic rules on how the traffic will be routed across deployments, defaults to None
    :paramtype traffic: typing.Optional[typing.Dict[str, int]]
    :keyword mirror_traffic: Duplicated live traffic used to inference a single deployment, defaults to None
    :paramtype mirror_traffic: typing.Optional[typing.Dict[str, int]]
    :keyword compute: Compute cluster id, defaults to None
    :paramtype compute: typing.Optional[str]
    :keyword identity: Identity Configuration, defaults to SystemAssigned
    :paramtype identity: typing.Optional[IdentityConfiguration]
    :keyword kind: Kind of the resource, we have two kinds: K8s and Managed online endpoints, defaults to None
    :paramtype kind: typing.Optional[str]
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        properties: Optional[Dict[str, Any]] = None,
        auth_mode: str = KEY,
        description: Optional[str] = None,
        location: Optional[str] = None,
        traffic: Optional[Dict[str, int]] = None,
        mirror_traffic: Optional[Dict[str, int]] = None,
        compute: Optional[str] = None,
        identity: Optional[IdentityConfiguration] = None,
        kind: Optional[str] = None,
        **kwargs: Any,
    ):
        """K8s Online endpoint entity.

        Constructor for K8s Online endpoint entity.

        :keyword name: Name of the resource, defaults to None
        :paramtype name: typing.Optional[str]
        :keyword tags: Tag dictionary. Tags can be added, removed, and updated, defaults to None
        :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword properties: The asset property dictionary, defaults to None
        :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword auth_mode: Possible values include: "aml_token", "key", defaults to KEY
        :type auth_mode: typing.Optional[str]
        :keyword description: Description of the inference endpoint, defaults to None
        :paramtype description: typing.Optional[str]
        :keyword location: Location of the resource, defaults to None
        :paramtype location: typing.Optional[str]
        :keyword traffic: Traffic rules on how the traffic will be routed across deployments, defaults to None
        :paramtype traffic: typing.Optional[typing.Dict[str, int]]
        :keyword mirror_traffic: Duplicated live traffic used to inference a single deployment, defaults to None
        :paramtype mirror_traffic: typing.Optional[typing.Dict[str, int]]
        :keyword compute: Compute cluster id, defaults to None
        :paramtype compute: typing.Optional[str]
        :keyword identity: Identity Configuration, defaults to SystemAssigned
        :paramtype identity: typing.Optional[IdentityConfiguration]
        :keyword kind: Kind of the resource, we have two kinds: K8s and Managed online endpoints, defaults to None
        :type kind: typing.Optional[str]
        """
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
        dest: Optional[Union[str, PathLike, IO[AnyStr]]] = None,  # pylint: disable=unused-argument
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        res: dict = KubernetesOnlineEndpointSchema(context=context).dump(self)
        return res

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
        res: dict = KubernetesOnlineEndpointSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res


class ManagedOnlineEndpoint(OnlineEndpoint):
    """Managed Online endpoint entity.

    :keyword name: Name of the resource, defaults to None
    :paramtype name: typing.Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated, defaults to None
    :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword properties: The asset property dictionary, defaults to None
    :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword auth_mode: Possible values include: "aml_token", "key", defaults to KEY
    :type auth_mode: str
    :keyword description: Description of the inference endpoint, defaults to None
    :paramtype description: typing.Optional[str]
    :keyword location: Location of the resource, defaults to None
    :paramtype location: typing.Optional[str]
    :keyword traffic: Traffic rules on how the traffic will be routed across deployments, defaults to None
    :paramtype traffic: typing.Optional[typing.Dict[str, int]]
    :keyword mirror_traffic: Duplicated live traffic used to inference a single deployment, defaults to None
    :paramtype mirror_traffic: typing.Optional[typing.Dict[str, int]]
    :keyword identity: Identity Configuration, defaults to SystemAssigned
    :paramtype identity: typing.Optional[IdentityConfiguration]
    :keyword kind: Kind of the resource, we have two kinds: K8s and Managed online endpoints, defaults to None.
    :paramtype kind: typing.Optional[str]
    :keyword public_network_access: Whether to allow public endpoint connectivity, defaults to None
        Allowed values are: "enabled", "disabled"
    :type public_network_access: typing.Optional[str]
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        properties: Optional[Dict[str, Any]] = None,
        auth_mode: str = KEY,
        description: Optional[str] = None,
        location: Optional[str] = None,
        traffic: Optional[Dict[str, int]] = None,
        mirror_traffic: Optional[Dict[str, int]] = None,
        identity: Optional[IdentityConfiguration] = None,
        kind: Optional[str] = None,
        public_network_access: Optional[str] = None,
        **kwargs: Any,
    ):
        """Managed Online endpoint entity.

        Constructor for Managed Online endpoint entity.

        :keyword name: Name of the resource, defaults to None
        :paramtype name: typing.Optional[str]
        :keyword tags: Tag dictionary. Tags can be added, removed, and updated, defaults to None
        :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword properties: The asset property dictionary, defaults to None
        :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword auth_mode: Possible values include: "aml_token", "key", defaults to KEY
        :type auth_mode: str
        :keyword description: Description of the inference endpoint, defaults to None
        :paramtype description: typing.Optional[str]
        :keyword location: Location of the resource, defaults to None
        :paramtype location: typing.Optional[str]
        :keyword traffic: Traffic rules on how the traffic will be routed across deployments, defaults to None
        :paramtype traffic: typing.Optional[typing.Dict[str, int]]
        :keyword mirror_traffic: Duplicated live traffic used to inference a single deployment, defaults to None
        :paramtype mirror_traffic: typing.Optional[typing.Dict[str, int]]
        :keyword identity: Identity Configuration, defaults to SystemAssigned
        :paramtype identity: typing.Optional[IdentityConfiguration]
        :keyword kind: Kind of the resource, we have two kinds: K8s and Managed online endpoints, defaults to None.
        :type kind: typing.Optional[str]
        :keyword public_network_access: Whether to allow public endpoint connectivity, defaults to None
            Allowed values are: "enabled", "disabled"
        :type public_network_access: typing.Optional[str]
        """
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
        dest: Optional[Union[str, PathLike, IO[AnyStr]]] = None,  # pylint: disable=unused-argument
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        res: dict = ManagedOnlineEndpointSchema(context=context).dump(self)
        return res

    def _to_dict(self) -> Dict:
        res: dict = ManagedOnlineEndpointSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res


class EndpointAuthKeys(RestTranslatableMixin):
    """Keys for endpoint authentication.

    :ivar primary_key: The primary key.
    :vartype primary_key: str
    :ivar secondary_key: The secondary key.
    :vartype secondary_key: str
    """

    def __init__(self, **kwargs: Any):
        """Constructor for keys for endpoint authentication.

        :keyword primary_key: The primary key.
        :paramtype primary_key: str
        :keyword secondary_key: The secondary key.
        :paramtype secondary_key: str
        """
        self.primary_key = kwargs.get("primary_key", None)
        self.secondary_key = kwargs.get("secondary_key", None)

    @classmethod
    def _from_rest_object(cls, obj: RestEndpointAuthKeys) -> "EndpointAuthKeys":
        return cls(primary_key=obj.primary_key, secondary_key=obj.secondary_key)

    def _to_rest_object(self) -> RestEndpointAuthKeys:
        return RestEndpointAuthKeys(primary_key=self.primary_key, secondary_key=self.secondary_key)


class EndpointAuthToken(RestTranslatableMixin):
    """Endpoint authentication token.

    :ivar access_token: Access token for endpoint authentication.
    :vartype access_token: str
    :ivar expiry_time_utc: Access token expiry time (UTC).
    :vartype expiry_time_utc: float
    :ivar refresh_after_time_utc: Refresh access token after time (UTC).
    :vartype refresh_after_time_utc: float
    :ivar token_type: Access token type.
    :vartype token_type: str
    """

    def __init__(self, **kwargs: Any):
        """Constuctor for Endpoint authentication token.

        :keyword access_token: Access token for endpoint authentication.
        :paramtype access_token: str
        :keyword expiry_time_utc: Access token expiry time (UTC).
        :paramtype expiry_time_utc: float
        :keyword refresh_after_time_utc: Refresh access token after time (UTC).
        :paramtype refresh_after_time_utc: float
        :keyword token_type: Access token type.
        :paramtype token_type: str
        """
        self.access_token = kwargs.get("access_token", None)
        self.expiry_time_utc = kwargs.get("expiry_time_utc", 0)
        self.refresh_after_time_utc = kwargs.get("refresh_after_time_utc", 0)
        self.token_type = kwargs.get("token_type", None)

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


class EndpointAadToken:
    """Endpoint aad token.

    :ivar access_token: Access token for aad authentication.
    :vartype access_token: str
    :ivar expiry_time_utc: Access token expiry time (UTC).
    :vartype expiry_time_utc: float
    """

    def __init__(self, obj: AccessToken):
        """Constructor for Endpoint aad token.

        :param obj: Access token object
        :type obj: AccessToken
        """
        self.access_token = obj.token
        self.expiry_time_utc = obj.expires_on
