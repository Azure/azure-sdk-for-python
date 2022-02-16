# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, overload  # pylint: disable=unused-import

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

from azure.core.tracing.decorator_async import distributed_trace_async
from .._models import SipTrunk
from .._generated.models import (
    SipConfiguration,
    SipTrunkRoute,
    SipTrunkInternal
)
from .._generated.aio._sip_routing_service import (
    SIPRoutingService,
)
from ..._shared.utils import (
    parse_connection_str,
    get_authentication_policy
)
from ..._version import SDK_MONIKER

if TYPE_CHECKING:
    from typing import List, Any
    from azure.core.credentials_async import AsyncTokenCredential


class SipRoutingClient(object):
    """A client to interact with the SIP routing gateway asynchronously.
    This client provides operations to retrieve and update SIP routing configuration.

    :param endpoint: The endpoint url for Azure Communication Service resource.
    :type endpoint: str
    :param credential: The credentials with which to authenticate.
    :type credential: AsyncTokenCredential
    """

    def __init__(
        self,
        endpoint,  # type: str
        credential,  # type: AsyncTokenCredential
        **kwargs  # type: Any
    ):  # type: (...) -> SipRoutingClient

        if not credential:
            raise ValueError("credential can not be None")
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError as attribute_error:
            raise ValueError("Host URL must be a string") from attribute_error

        parsed_url = urlparse(endpoint.rstrip("/"))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._endpoint = endpoint
        self._authentication_policy = get_authentication_policy(
            endpoint, credential, is_async=True
        )

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
    ):  # type: (...) -> SipRoutingClient
        """Factory method for creating client from connection string.

        :param conn_str: Connection string containing endpoint and credentials
        :type conn_str: str
        :returns: The newly created client.
        :rtype: ~azure.communication.siprouting.models.SipRoutingClient
        """

        endpoint, credential = parse_connection_str(conn_str)
        return cls(endpoint, credential, **kwargs)

    @distributed_trace_async
    async def get_routes(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> List[SipTrunkRoute]
        """Returns list of currently configured SIP routes.

        :returns: Current SIP routes configuration.
        :rtype: List[~azure.communication.siprouting.models.SipTrunkRoute]
        """
        config = await self._rest_service.get_sip_configuration(
            **kwargs
        )
        return config.routes

    @distributed_trace_async
    async def get_trunks(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> List[SipTrunk]
        """Returns list of currently configured SIP trunks.

        :returns: Current SIP trunks configuration.
        :rtype: List[~azure.communication.siprouting.models.SipTrunk]
        """
        return await self._get_trunks_(**kwargs)

    @distributed_trace_async
    async def replace_routes(
        self,
        routes,  # type: List[SipTrunkRoute]
        **kwargs  # type: Any
    ):  # type: (...) -> List[SipTrunkRoute]
        """Replaces the list of SIP routes.

        :param routes: New list of routes to be set.
        :type routes: List[SipTrunkRoute]
        :returns:
        :rtype: List[~azure.communication.siprouting.models.SipTrunkRoute]
        """
        old_config = await self._rest_service.get_sip_configuration(
            **kwargs
        )
        await self._rest_service.patch_sip_configuration(
            body=SipConfiguration(routes=routes),
            **kwargs
            )
        return old_config.routes

    @distributed_trace_async
    async def replace_trunks(
        self,
        trunks,  # type: List[SipTrunk]
        **kwargs  # type: Any
    ):  # type: (...) -> List[SipTrunk]
        """Replaces the list of SIP trunks.

        :param trunks: New list of trunks to be set.
        :type trunks: List[SipTrunk]
        :returns:
        :rtype: List[~azure.communication.siprouting.models.SipTrunk]
        """
        old_trunks = await self._get_trunks_(**kwargs)

        if len(old_trunks) > 0:
            await self._rest_service.patch_sip_configuration(
                body=SipConfiguration(trunks={x.fqdn: None for x in old_trunks}), **kwargs
            )
        await self._patch_trunks_(trunks, **kwargs)
        return old_trunks

    @distributed_trace_async
    async def delete_route(
        self,
        route_name,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> None
        """Deletes a route.

        :param route_name: Name of the route to be deleted.
        :type route_name: str
        :returns: None
        :rtype: None
        """
        old_config = await self._rest_service.get_sip_configuration(
            **kwargs
        )

        modified_routes = [x for x in old_config.routes if x.name != route_name]
        modified_config = SipConfiguration(routes=modified_routes)

        await self._rest_service.patch_sip_configuration(
            body=modified_config, **kwargs
        )

    @distributed_trace_async
    async def delete_trunk(
        self,
        trunk_fqdn,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> None
        """Deletes a trunk.

        :param trunk_fqdn: FQDN of the trunk to be deleted.
        :type trunk_fqdn: str
        :returns: None
        :rtype: None
        """
        await self._rest_service.patch_sip_configuration(
            body=SipConfiguration(trunks={trunk_fqdn:None}),
            **kwargs)

    @distributed_trace_async
    async def set_route(
        self,
        route,  # type: SipTrunkRoute
        **kwargs  # type: Any
    ):  # type: (...) -> SipTrunkRoute
        """Sets route. Modifies route with the same name if it exists, otherwise adds a new route.

        :param route: Route object to be set.
        :type route: ~azure.communication.siprouting.models.SipTrunkRoute
        :returns:
        :rtype: ~azure.communication.siprouting.models.SipTrunkRoute
        """
        old_config = await self._rest_service.get_sip_configuration(
            **kwargs
        )

        if any(x.name==route.name for x in old_config.routes):
            modified_routes = [route if x.name==route.name else x for x in old_config.routes]
        else:
            modified_routes = old_config.routes
            modified_routes.append(route)

        await self._rest_service.patch_sip_configuration(
            body=SipConfiguration(routes=modified_routes), **kwargs
        )
        return __find_route__(old_config.routes,route.name)

    @distributed_trace_async
    async def set_trunk(
        self,
        trunk,  # type: SipTrunk
        **kwargs  # type: Any
    ):  # type: (...) -> SipTrunk
        """Sets trunk. Modifies trunk with the same FQDN if it exists, otherwise adds a new trunk.

        :param trunk: Trunk object to be set.
        :type trunk: ~azure.communication.siprouting.models.SipTrunk
        :returns:
        :rtype: ~azure.communication.siprouting.models.SipTrunk
        """
        old_trunks = await self._get_trunks_(**kwargs)
        await self._patch_trunks_([trunk],**kwargs)

        return __find_trunk__(old_trunks, trunk.fqdn)

    async def _get_trunks_(self, **kwargs):
        config = await self._rest_service.get_sip_configuration(
            **kwargs
        )
        return [SipTrunk(fqdn=k,sip_signaling_port=v.sip_signaling_port) for k,v in config.trunks.items()]

    async def _patch_trunks_(self,
        trunks,  # type: List[SipTrunk]
        **kwargs  # type: Any
        ):  # type: (...) -> SipTrunk
        trunks_internal = {x.fqdn: SipTrunkInternal(sip_signaling_port=x.sip_signaling_port) for x in trunks}
        modified_config = SipConfiguration(trunks=trunks_internal)

        new_config = await self._rest_service.patch_sip_configuration(
            body=modified_config, **kwargs
        )
        return [SipTrunk(fqdn=k,sip_signaling_port=v.sip_signaling_port) for k,v in new_config.trunks.items()]

    async def close(self) -> None:
        await self._rest_service.close()

    async def __aenter__(self) -> "SipRoutingClient":
        await self._rest_service.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._rest_service.__aexit__(*args)

def __find_trunk__(trunks, trunk_fqdn):
    for x in trunks:
        if x.fqdn == trunk_fqdn:
            return x
    return None

def __find_route__(routes, route_name):
    for x in routes:
        if x.name == route_name:
            return x
    return None
