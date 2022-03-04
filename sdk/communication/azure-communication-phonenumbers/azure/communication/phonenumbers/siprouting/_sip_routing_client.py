# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING  # pylint: disable=unused-import

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

from azure.core.tracing.decorator import distributed_trace

from._models import SipTrunk
from ._generated.models import (
    SipConfiguration,
    SipTrunkRoute,
    SipTrunkInternal
)
from ._generated._sip_routing_service import SIPRoutingService
from .._shared.utils import (
    parse_connection_str,
    get_authentication_policy
)
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    from typing import List, Any
    from azure.core.credentials import TokenCredential


class SipRoutingClient(object):
    """A client to interact with the AzureCommunicationService SIP routing gateway.
    This client provides operations to retrieve and update SIP routing configuration.

    :param endpoint: The endpoint url for Azure Communication Service resource.
    :type endpoint: str
    :param credential: The credentials with which to authenticate.
    :type credential: TokenCredential
    """

    def __init__(
        self,
        endpoint,  # type: str
        credential,  # type: TokenCredential
        **kwargs  # type: Any
    ):  # type: (...) -> SipRoutingClient

        if not credential:
            raise ValueError("credential can not be None")
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(endpoint.rstrip("/"))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._endpoint = endpoint
        self._authentication_policy = get_authentication_policy(endpoint, credential)

        self._rest_service = SIPRoutingService(
            self._endpoint,
            authentication_policy=self._authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs
        )

    @classmethod
    def from_connection_string(
        cls,
        conn_str,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> SipRoutingClient
        """Factory method for creating client from connection string.

        :param str conn_str: Connection string containing endpoint and credentials.
        :returns: The newly created client.
        :rtype: ~azure.communication.siprouting.SipRoutingClient
        """
        endpoint, credential = parse_connection_str(conn_str)
        return cls(endpoint, credential, **kwargs)

    @distributed_trace
    def get_trunk(
        self,
        trunk_fqdn,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> SipTrunk
        """Getter for single SIP trunk.

        :param str trunk_fqdn: FQDN of the desired SIP trunk.
        :returns: SIP trunk with specified trunk_fqdn.
        :rtype: ~azure.communication.siprouting.models.SipTrunk
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError, LookupError
        """
        if trunk_fqdn is None:
            raise ValueError("Parameter 'trunk_fqdn' must not be None.")

        config = self._rest_service.get_sip_configuration(
            **kwargs)
        trunk = config.trunks[trunk_fqdn]

        if not trunk:
            raise LookupError("No entry found for FQDN:" + trunk_fqdn)

        return SipTrunk(fqdn=trunk_fqdn,sip_signaling_port=trunk.sip_signaling_port)

    @distributed_trace
    def get_route(
        self,
        route_name,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> SipTrunkRoute
        """Getter for single SIP route.

        :param str route_name: Name of the desired SIP route.
        :returns: SIP route with specified route_name.
        :rtype: ~azure.communication.siprouting.models.SipTrunkRoute
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError, LookupError
        """
        if route_name is None:
            raise ValueError("Parameter 'route_name' must not be None.")

        config = self._rest_service.get_sip_configuration(
            **kwargs)
        route = [x.name==route_name for x in config.routes]

        if not route:
            raise LookupError("No entry found for name:" + route_name)

        return route

    @distributed_trace
    def set_trunk(
        self,
        trunk,  # type: SipTrunk
        **kwargs  # type: Any
    ):  # type: (...) -> None
        """Modifies SIP trunk with the given FQDN. If it doesn't exist, adds a new trunk.

        :param trunk: Trunk object to be set.
        :type trunk: ~azure.communication.siprouting.models.SipTrunk
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if trunk is None:
            raise ValueError("Parameter 'trunk' must not be None.")

        self._patch_trunks_([trunk],**kwargs)

    @distributed_trace
    def set_route(
        self,
        route,  # type: SipTrunkRoute
        **kwargs  # type: Any
    ):  # type: (...) -> None
        """Modifies SIP route with the given route name. If it doesn't exist, appends new route to the list.

        :param route: Route object to be set.
        :type route: ~azure.communication.siprouting.models.SipTrunkRoute
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if route is None:
            raise ValueError("Parameter 'route' must not be None.")

        old_config = self._rest_service.get_sip_configuration(
            **kwargs
        )

        if any(x.name==route.name for x in old_config.routes):
            modified_routes = [route if x.name==route.name else x for x in old_config.routes]
        else:
            modified_routes = old_config.routes
            modified_routes.append(route)

        self._rest_service.patch_sip_configuration(
            body=SipConfiguration(routes=modified_routes),
            **kwargs)

    @distributed_trace
    def delete_trunk(
        self,
        trunk_fqdn,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> None
        """Deletes SIP trunk.

        :param trunk_fqdn: FQDN of the trunk to be deleted.
        :type trunk_fqdn: str
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if trunk_fqdn is None:
            raise ValueError("Parameter 'trunk_fqdn' must not be None.")

        self._rest_service.patch_sip_configuration(
            body=SipConfiguration(trunks={trunk_fqdn:None}),
            **kwargs)

    @distributed_trace
    def delete_route(
        self,
        route_name,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> None
        """Deletes SIP route.

        :param route_name: Name of the route to be deleted.
        :type route_name: str
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if route_name is None:
            raise ValueError("Parameter 'route_name' must not be None.")

        old_config = self._rest_service.get_sip_configuration(
            **kwargs
        )

        modified_routes = [x for x in old_config.routes if x.name != route_name]
        modified_config = SipConfiguration(routes=modified_routes)

        self._rest_service.patch_sip_configuration(
            body=modified_config, **kwargs
        )

    @distributed_trace
    def get_trunks(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> List[SipTrunk]
        """Getter for currently configured SIP trunks.

        :returns: Current SIP trunks configuration.
        :rtype: List[~azure.communication.siprouting.models.SipTrunk]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._get_trunks_(**kwargs)

    @distributed_trace
    def get_routes(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> List[SipTrunkRoute]
        """Getter for currently configured SIP routes.

        :returns: Current SIP routes configuration.
        :rtype: List[~azure.communication.siprouting.models.SipTrunkRoute]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        config = self._rest_service.get_sip_configuration(
            **kwargs
        )
        return config.routes

    @distributed_trace
    def replace_trunks(
        self,
        trunks,  # type: List[SipTrunk]
        **kwargs  # type: Any
    ):  # type: (...) -> List[SipTrunk]
        """Replaces the list of SIP trunks.

        :param trunks: New list of trunks to be set.
        :type trunks: List[SipTrunk]
        :returns:
        :rtype: List[~azure.communication.siprouting.models.SipTrunk]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if trunks is None:
            raise ValueError("Parameter 'trunks' must not be None.")

        old_trunks = self._get_trunks_(**kwargs)

        if len(old_trunks) > 0:
            self._rest_service.patch_sip_configuration(
                body=SipConfiguration(trunks={x.fqdn: None for x in old_trunks}), **kwargs
            )
        if len(trunks) > 0:
            self._patch_trunks_(trunks, **kwargs)
            
        return old_trunks

    @distributed_trace
    def replace_routes(
        self,
        routes,  # type: List[SipTrunkRoute]
        **kwargs  # type: Any
    ):  # type: (...) -> List[SipTrunkRoute]
        """Replaces the list of SIP routes.

        :param routes: New list of routes to be set.
        :type routes: List[SipTrunkRoute]
        :returns:
        :rtype: List[~azure.communication.siprouting.models.SipTrunkRoute]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if routes is None:
            raise ValueError("Parameter 'routes' must not be None.")

        old_config = self._rest_service.get_sip_configuration(
            **kwargs
        )

        self._rest_service.patch_sip_configuration(
            body=SipConfiguration(routes=routes), **kwargs
        )
        return old_config.routes

    def _get_trunks_(self, **kwargs):
        config = self._rest_service.get_sip_configuration(
            **kwargs)
        return [SipTrunk(fqdn=k,sip_signaling_port=v.sip_signaling_port) for k,v in config.trunks.items()]

    def _patch_trunks_(self,
        trunks,  # type: List[SipTrunk]
        **kwargs  # type: Any
        ):  # type: (...) -> SipTrunk
        trunks_internal = {x.fqdn: SipTrunkInternal(sip_signaling_port=x.sip_signaling_port) for x in trunks}
        modified_config = SipConfiguration(trunks=trunks_internal)

        new_config = self._rest_service.patch_sip_configuration(
            body=modified_config, **kwargs
        )
        return [SipTrunk(fqdn=k,sip_signaling_port=v.sip_signaling_port) for k,v in new_config.trunks.items()]
