# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, List
from urllib.parse import urlparse

from azure.core.async_paging import AsyncItemPaged, AsyncList

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from .._models import SipTrunk, SipTrunkRoute
from .._generated.models import SipConfiguration, SipTrunkInternal, SipTrunkRouteInternal
from .._generated.aio._client import SIPRoutingService
from ..._shared.auth_policy_utils import get_authentication_policy
from ..._shared.utils import parse_connection_str
from ..._version import SDK_MONIKER

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class SipRoutingClient(object):
    """A client to interact with the SIP routing gateway asynchronously.
    This client provides operations to retrieve and update SIP routing configuration.

    :param endpoint: The endpoint url for Azure Communication Service resource.
    :type endpoint: str
    :param credential: The credentials with which to authenticate.
    :type credential: AsyncTokenCredential
    :keyword api_version: Api Version. Default value is "2021-05-01-preview". Note that overriding
     this default value may result in unsupported behavior.
    :paramtype api_version: str
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
        self._authentication_policy = get_authentication_policy(endpoint, credential, is_async=True)

        self._rest_service = SIPRoutingService(
            self._endpoint, authentication_policy=self._authentication_policy, sdk_moniker=SDK_MONIKER, **kwargs
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
    async def get_trunk(
        self,
        trunk_fqdn,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> SipTrunk
        """Retrieve a single SIP trunk.

        :param trunk_fqdn: FQDN of the desired SIP trunk.
        :type trunk_fqdn: str
        :returns: SIP trunk with specified trunk_fqdn. If it doesn't exist, throws KeyError.
        :rtype: ~azure.communication.siprouting.models.SipTrunk
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError, KeyError
        """
        if trunk_fqdn is None:
            raise ValueError("Parameter 'trunk_fqdn' must not be None.")

        config = await self._rest_service.sip_routing.get(**kwargs)

        trunk = config.trunks[trunk_fqdn]
        return SipTrunk(fqdn=trunk_fqdn, sip_signaling_port=trunk.sip_signaling_port)

    @distributed_trace_async
    async def set_trunk(
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

        await self._update_trunks_([trunk], **kwargs)

    @distributed_trace_async
    async def delete_trunk(
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

        await self._rest_service.sip_routing.update(body=SipConfiguration(trunks={trunk_fqdn: None}), **kwargs)

    @distributed_trace
    def list_trunks(
        self, **kwargs  # type: Any
    ):  # type: (...) -> AsyncItemPaged[SipTrunk]
        """Retrieves list of currently configured SIP trunks.

        :returns: Current SIP trunks configuration.
        :rtype: AsyncItemPaged[~azure.communication.siprouting.models.SipTrunk]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        async def extract_data(config):
            list_of_elem = [SipTrunk(fqdn=k, sip_signaling_port=v.sip_signaling_port) for k, v in config.trunks.items()]
            return None, AsyncList(list_of_elem)

        # pylint: disable=unused-argument
        async def get_next(nextLink=None):
            return await self._rest_service.sip_routing.get(**kwargs)

        return AsyncItemPaged(get_next, extract_data)

    @distributed_trace
    def list_routes(
        self, **kwargs  # type: Any
    ):  # type: (...) -> AsyncItemPaged[SipTrunkRoute]
        """Retrieves list of currently configured SIP routes.

        :returns: Current SIP routes configuration.
        :rtype: AsyncItemPaged[~azure.communication.siprouting.models.SipTrunkRoute]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        async def extract_data(config):
            list_of_elem = [
                SipTrunkRoute(description=x.description, name=x.name, number_pattern=x.number_pattern, trunks=x.trunks)
                for x in config.routes
            ]
            return None, AsyncList(list_of_elem)

        # pylint: disable=unused-argument
        async def get_next(nextLink=None):
            return await self._rest_service.sip_routing.get(**kwargs)

        return AsyncItemPaged(get_next, extract_data)

    @distributed_trace_async
    async def set_trunks(
        self,
        trunks,  # type: List[SipTrunk]
        **kwargs  # type: Any
    ):  # type: (...) -> None
        """Overwrites the list of SIP trunks.

        :param trunks: New list of trunks to be set.
        :type trunks: List[SipTrunk]
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if trunks is None:
            raise ValueError("Parameter 'trunks' must not be None.")

        trunks_dictionary = {x.fqdn: SipTrunkInternal(sip_signaling_port=x.sip_signaling_port) for x in trunks}
        config = SipConfiguration(trunks=trunks_dictionary)

        old_trunks = await self._list_trunks_(**kwargs)

        for x in old_trunks:
            if x.fqdn not in [o.fqdn for o in trunks]:
                config.trunks[x.fqdn] = None

        if len(config.trunks) > 0:
            await self._rest_service.sip_routing.update(body=config, **kwargs)

    @distributed_trace_async
    async def set_routes(
        self,
        routes,  # type: List[SipTrunkRoute]
        **kwargs  # type: Any
    ):  # type: (...) -> None
        """Overwrites the list of SIP routes.

        :param routes: New list of routes to be set.
        :type routes: List[SipTrunkRoute]
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if routes is None:
            raise ValueError("Parameter 'routes' must not be None.")

        routes_internal = [
            SipTrunkRouteInternal(
                description=x.description, name=x.name, number_pattern=x.number_pattern, trunks=x.trunks
            )
            for x in routes
        ]
        await self._rest_service.sip_routing.update(body=SipConfiguration(routes=routes_internal), **kwargs)

    async def _list_trunks_(self, **kwargs):
        config = await self._rest_service.sip_routing.get(**kwargs)
        return [SipTrunk(fqdn=k, sip_signaling_port=v.sip_signaling_port) for k, v in config.trunks.items()]

    async def _update_trunks_(
        self,
        trunks,  # type: List[SipTrunk]
        **kwargs  # type: Any
    ):  # type: (...) -> SipTrunk
        trunks_internal = {x.fqdn: SipTrunkInternal(sip_signaling_port=x.sip_signaling_port) for x in trunks}
        modified_config = SipConfiguration(trunks=trunks_internal)

        new_config = await self._rest_service.sip_routing.update(body=modified_config, **kwargs)
        return [SipTrunk(fqdn=k, sip_signaling_port=v.sip_signaling_port) for k, v in new_config.trunks.items()]

    async def close(self) -> None:
        await self._rest_service.close()

    async def __aenter__(self) -> "SipRoutingClient":
        await self._rest_service.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._rest_service.__aexit__(*args)
