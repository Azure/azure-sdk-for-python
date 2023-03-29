# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING  # pylint: disable=unused-import
from urllib.parse import urlparse

from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged

from._models import SipTrunk, SipTrunkRoute
from ._generated.models import (
    SipConfiguration,
    SipTrunkInternal,
    SipTrunkRouteInternal
)
from ._generated._client import SIPRoutingService
from .._shared.utils import (
    parse_connection_str,
    get_authentication_policy
)
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    from typing import Optional, Iterable, List, Any
    from azure.core.credentials import TokenCredential


class SipRoutingClient(object):
    """A client to interact with the AzureCommunicationService SIP routing gateway.
    This client provides operations to retrieve and manage SIP routing configuration.

    :param endpoint: The endpoint url for Azure Communication Service resource.
    :type endpoint: str
    :param credential: The credentials with which to authenticate.
    :type credential: TokenCredential
    :keyword api_version: Api Version. Default value is "2021-05-01-preview". Note that overriding
     this default value may result in unsupported behavior.
    :paramtype api_version: str
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
        """Retrieve a single SIP trunk.

        :param trunk_fqdn: FQDN of the desired SIP trunk.
        :type trunk_fqdn: str
        :returns: SIP trunk with specified trunk_fqdn. If it doesn't exist, throws KeyError.
        :rtype: ~azure.communication.siprouting.models.SipTrunk
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError, KeyError
        """
        if trunk_fqdn is None:
            raise ValueError("Parameter 'trunk_fqdn' must not be None.")

        config = self._rest_service.sip_routing.get(
            **kwargs)

        trunk = config.trunks[trunk_fqdn]
        return SipTrunk(fqdn=trunk_fqdn,sip_signaling_port=trunk.sip_signaling_port)

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

        self._update_trunks_([trunk],**kwargs)

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

        self._rest_service.sip_routing.update(
            body=SipConfiguration(trunks={trunk_fqdn:None}),
            **kwargs)

    @distributed_trace
    def list_trunks(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> ItemPaged[SipTrunk]
        """Retrieves the currently configured SIP trunks.

        :returns: Current SIP trunks configuration.
        :rtype: ItemPaged[~azure.communication.siprouting.models.SipTrunk]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        def extract_data(config):
            list_of_elem = [SipTrunk(
                fqdn=k,
                sip_signaling_port=v.sip_signaling_port) for k,v in config.trunks.items()]
            return None, list_of_elem

        # pylint: disable=unused-argument
        def get_next(nextLink=None):
            return self._rest_service.sip_routing.get(
                **kwargs
                )

        return ItemPaged(get_next, extract_data)

    @distributed_trace
    def list_routes(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> ItemPaged[SipTrunkRoute]
        """Retrieves the currently configured SIP routes.

        :returns: Current SIP routes configuration.
        :rtype: ItemPaged[~azure.communication.siprouting.models.SipTrunkRoute]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        def extract_data(config):
            list_of_elem =  [SipTrunkRoute(
                description=x.description,
                name=x.name,
                number_pattern=x.number_pattern,
                trunks=x.trunks) for x in config.routes]
            return None, list_of_elem

        # pylint: disable=unused-argument
        def get_next(nextLink=None):
            return  self._rest_service.sip_routing.get(
                **kwargs
            )

        return ItemPaged(get_next, extract_data)

    @distributed_trace
    def set_trunks(
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

        old_trunks = self._list_trunks_(**kwargs)

        for x in old_trunks:
            if x.fqdn not in [o.fqdn for o in trunks]:
                config.trunks[x.fqdn] = None

        if len(config.trunks) > 0:
            self._rest_service.sip_routing.update(
                body=config, **kwargs
            )

    @distributed_trace
    def set_routes(
        self,
        routes,  # type: List[SipTrunkRoute]
        **kwargs  # type: Any
    ):  # type: (...) ->  None
        """Overwrites the list of SIP routes.

        :param routes: New list of routes to be set.
        :type routes: List[SipTrunkRoute]
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if routes is None:
            raise ValueError("Parameter 'routes' must not be None.")

        routes_internal = [SipTrunkRouteInternal(
            description=x.description,
            name=x.name,
            number_pattern=x.number_pattern,
            trunks=x.trunks
            ) for x in routes]
        self._rest_service.sip_routing.update(
            body=SipConfiguration(routes=routes_internal), **kwargs
        )

    def _list_trunks_(self, **kwargs):
        config = self._rest_service.sip_routing.get(
            **kwargs)
        return [SipTrunk(fqdn=k,sip_signaling_port=v.sip_signaling_port) for k,v in config.trunks.items()]

    def _update_trunks_(self,
        trunks,  # type: List[SipTrunk]
        **kwargs  # type: Any
        ):  # type: (...) -> SipTrunk
        trunks_internal = {x.fqdn: SipTrunkInternal(sip_signaling_port=x.sip_signaling_port) for x in trunks}
        modified_config = SipConfiguration(trunks=trunks_internal)

        new_config = self._rest_service.sip_routing.update(
            body=modified_config, **kwargs
        )
        return [SipTrunk(fqdn=k,sip_signaling_port=v.sip_signaling_port) for k,v in new_config.trunks.items()]

    def close(self) -> None:
        self._rest_service.close()

    def __enter__(self) -> "SipRoutingClient":
        self._rest_service.__enter__()
        return self

    def __exit__(self, *args) -> None:
        self._rest_service.__exit__(*args)
