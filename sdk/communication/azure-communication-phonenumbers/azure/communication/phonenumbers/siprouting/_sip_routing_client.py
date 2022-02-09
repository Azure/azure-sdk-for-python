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

from azure.core.tracing.decorator import distributed_trace
from ._generated.models import (
    SipConfiguration,
    SipTrunkRoute,
    SipTrunkInternal
)
from._models import SipTrunk

from ._generated._sip_routing_service import (
    SIPRoutingService,
)

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

        :param str conn_str: Connection String containing endpoint and credentials.
        :returns: The newly created client.
        :rtype: ~azure.communication.siprouting.SipRoutingClient
        """
        endpoint, credential = parse_connection_str(conn_str)
        return cls(endpoint, credential, **kwargs)

    @distributed_trace
    def get_sip_configuration(
        self, **kwargs  # type: Any
    ):  # type: (...) -> SipConfiguration
        """Returns current SIP routing configuration.

        :returns: Current SIP routing configuration.
        :rtype: ~azure.communication.siprouting.models.SipConfiguration
        """

        configuration = self._rest_service.get_sip_configuration(
            **kwargs
        )

        return configuration

    @overload
    @distributed_trace
    def update_sip_configuration(
        self,
        configuration, # type: SipConfiguration
        **kwargs # type: any
    ):  # type: (...) -> SipConfiguration
        """Updates SIP routing configuration with new SIP trunks and trunk routes.

        :param configuration: new SIP configuration
        :type configuration: ~azure.communication.siprouting.models.SipConfiguration
        :returns: Updated SIP configuration.
        :rtype: ~azure.communication.siprouting.models.SipConfiguration
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @overload
    @distributed_trace
    def update_sip_configuration(
        self,
        **kwargs
    ):  # type: (...) -> SipConfiguration
        """Updates SIP routing configuration with new SIP trunks and SIP trunk routes.

        :keyword trunks: SIP trunks for routing calls
        :paramtype trunks: Dict[str, ~azure.communication.siprouting.models.Trunk]
        :keyword routes: Trunk routes for routing calls. Route's name is used as the key.
        :paramtype routes: list[~azure.communication.siprouting.models.TrunkRoute]
        :returns: Updated SIP configuration.
        :rtype: ~azure.communication.siprouting.models.SipConfiguration
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @distributed_trace
    def update_sip_configuration(
        self,
        *args,
        **kwargs
    ):  # type: (...) -> SipConfiguration
        """Updates SIP routing configuration with new SIP trunks and SIP trunk routes.

        :param args: new SIP configuration
        :type args: ~azure.communication.siprouting.models.SipConfiguration
        :keyword trunks: SIP trunks for routing calls
        :paramtype trunks: Dict[str, ~azure.communication.siprouting.models.Trunk]
        :keyword routes: Trunk routes for routing calls. Route's name is used as the key.
        :paramtype routes: list[~azure.communication.siprouting.models.TrunkRoute]
        :returns: Updated SIP configuration.
        :rtype: ~azure.communication.siprouting.models.SipConfiguration
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if len(args) > 1:
            raise TypeError("There can only be one positional argument, which is the SIP configuration.")
        if args and "configuration" in kwargs:
            raise TypeError(
            "You have already supplied the configuration as a positional parameter, "
            "you can not supply it as a keyword argument as well."
        )

        if not args and not kwargs:
            raise ValueError

        configuration = args[0] if args else None

        if not configuration:
            configuration = SipConfiguration(
                trunks=kwargs.pop("trunks", {}),
                routes=kwargs.pop("routes", {}))

        return self._rest_service.patch_sip_configuration(
            body=configuration, **kwargs
        )

    @distributed_trace
    def get_routes(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> List[SipTrunkRoute]
        """Returns list of currently configured SIP routes.

        :returns: Current SIP routes configuration.
        :rtype: List[~azure.communication.siprouting.models.SipTrunkRoute]
        """
        config = self._rest_service.get_sip_configuration(
            **kwargs
        )
        return config.routes

    @distributed_trace
    def get_trunks(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> List[SipTrunk]
        """Returns list of currently configured SIP trunks.

        :returns: Current SIP trunks configuration.
        :rtype: List[~azure.communication.siprouting.models.SipTrunk]
        """
        return self.__get_trunks__(**kwargs)

    @distributed_trace
    def replace_routes(
        self,
        routes,  # type: List[SipTrunkRoute]
        **kwargs  # type: Any
    ):  # type: (...) -> List[SipTrunkRoute]
        """Replaces the list of SIP routes.

        :returns: 
        :rtype: List[~azure.communication.siprouting.models.SipTrunkRoute]
        """
        old_config = self._rest_service.get_sip_configuration(
            **kwargs
        )
        self._rest_service.patch_sip_configuration(
            body=SipConfiguration(routes=routes), **kwargs
        )
        return old_config.routes

    @distributed_trace
    def replace_trunks(
        self,
        trunks,  # type: List[SipTrunk]
        **kwargs  # type: Any
    ):  # type: (...) -> List[SipTrunk]
        """Replaces the list of SIP trunks.

        :returns: 
        :rtype: List[~azure.communication.siprouting.models.SipTrunk]
        """
        old_trunks = self.__get_trunks__(**kwargs)
        self.__patch_trunks__(trunks, **kwargs)
        return old_trunks

    @distributed_trace
    def delete_route(
        self,
        route_name,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> SipTrunkRoute
        """Returns list of currently configured SIP routes.

        :returns: Current SIP routes configuration.
        :rtype: List[~azure.communication.siprouting.models.SipTrunkRoute]
        """
        old_config = self._rest_service.get_sip_configuration(
            **kwargs
        )
        
        modified_routes = [x for x in old_config.routes if x.name != route_name]
        modified_config = SipConfiguration(routes=modified_routes)

        self._rest_service.patch_sip_configuration(
            body=modified_config, **kwargs
        )
        return [x for x in old_config.routes if x.name == route_name]

    @distributed_trace
    def delete_trunk(
        self,
        trunk_name,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> SipTrunk
        """Returns list of currently configured SIP routes.

        :returns: Current SIP routes configuration.
        :rtype: ~azure.communication.siprouting.models.SipTrunk
        """
        old_trunks = self.__get_trunks__(
            **kwargs)
        self.__patch_trunks__(
            {trunk_name: None},
            **kwargs)

        return [x for x in old_trunks if x.fqdn == trunk_name]

    @distributed_trace
    def set_route(
        self,
        route,  # type: SipTrunkRoute
        **kwargs  # type: Any
    ):  # type: (...) -> SipTrunkRoute
        """Returns list of currently configured SIP routes.

        :returns: Current SIP routes configuration.
        :rtype: ~azure.communication.siprouting.models.SipTrunk
        """
        old_config = self._rest_service.get_sip_configuration(
            **kwargs
        )

        if (any(x.name==route.name for x in old_config.routes)):
            modified_routes = [route if x.name==route.name else x for x in old_config.routes]
        else:
            modified_routes = [old_config.routes,route]

        self._rest_service.patch_sip_configuration(
            body=SipConfiguration(routes=modified_routes), **kwargs
        )

        return [x for x in old_config.routes if x.name == route.name]

    @distributed_trace
    def set_trunk(
        self,
        trunk,  # type: SipTrunk
        **kwargs  # type: Any
    ):  # type: (...) -> SipTrunk
        """Returns list of currently configured SIP routes.

        :returns: Current SIP routes configuration.
        :rtype: ~azure.communication.siprouting.models.SipTrunk
        """
        old_trunks = self.__get_trunks__(**kwargs)
        self.__patch_trunks__([trunk],**kwargs)

        return [x for x in old_trunks if x.fqdn == trunk.fqdn]

    def __get_trunks__(self, **kwargs):
        config = self._rest_service.get_sip_configuration(
            **kwargs  # type: Any
        )
        return [SipTrunk(x.key,x.value) for x in config.trunks.items()]

    def __patch_trunks__(self,
        trunks,  # type: List[SipTrunk]
        **kwargs  # type: Any
        ):  # type: (...) -> SipTrunk
        trunks_internal = {x.fqdn: SipTrunkInternal(x.sip_signaling_port) for x in trunks}
        modified_config = SipConfiguration(trunks=trunks_internal)

        new_config = self._rest_service.patch_sip_configuration(
            body=modified_config, **kwargs
        )
        return [SipTrunk(x.key,x.value) for x in new_config.trunks.items()]
         