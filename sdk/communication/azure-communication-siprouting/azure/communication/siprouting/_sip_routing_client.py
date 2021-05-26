# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

from azure.core.tracing.decorator import distributed_trace
from ._generated._azure_communication_sip_routing_service import AzureCommunicationSIPRoutingService
from ._shared.utils import parse_connection_str
from ._generated.models import SipConfiguration, Trunk, TrunkRoute
from ._shared.user_credential import CommunicationTokenCredential


class SIPRoutingClient():
    """A client to interact with the AzureCommunicationService SIP routing gateway.

    This client provides operations to retrieve and update SIP routing configuration.
    :param endpoint: The endpoint url for Azure Communication Service resource.
    :type endpoint: str
    :param credential: The credentials with which to authenticate.
    :type credential: CommunicationTokenCredential 
    """

    def __init__(
            self,
            endpoint,  # type: str
            credential,  # type: CommunicationTokenCredential
            **kwargs  # type: any
    ):  # type: (...) -> SIPRoutingClient

        if not credential:
            raise ValueError("credential can not be None")

        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(endpoint.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._endpoint = endpoint

        self._rest_service = AzureCommunicationSIPRoutingService(
            self._endpoint,
            **kwargs
        )

    @classmethod
    def from_connection_string(
            cls,
            connection_string,  # type: str
            **kwargs  # type: any
    ):  # type: (...) -> SIPRoutingClient
        """Factory method for creating client from connection string.

        :param connection_string: Connection string containing endpoint and credentials
        :type connection_string: str
        :returns: The newly created client.
        :rtype: ~SIPRoutingClient
        """

        endpoint, credential = parse_connection_str(connection_string)
        return cls(endpoint, credential, **kwargs)

    @distributed_trace
    def get_sip_configuration(
            self,
            **kwargs  # type: any
    ):  # type: (...) -> SipConfiguration
        """Returns current SIP routing configuration.

        :returns: Current SIP routing configuration.
        :rtype: ~SipConfiguration
        """

        acs_resource_calling_configuration = self._rest_service.get_sip_configuration(
            **kwargs)
        return acs_resource_calling_configuration

    @distributed_trace
    def update_sip_trunk_configuration(
            self,
            online_pstn_gateways,  # type: dict[str,Trunk]
            online_pstn_routing_settings,  # type: list[TrunkRoute]
            **kwargs  # type: any
    ):  # type: (...) -> SipConfiguration
        """Updates SIP routing configuration with new SIP trunks and trunk routes.

        :param online_pstn_gateways: SIP trunks for routing calls
        :type trunks: dict[str, ~Trunk]
        :param online_pstn_routing_settings: Trunk routes for routing calls. Route's name is used as the key.
        :type routes: list[~TrunkRoute]

        :type connection_string: str
        :returns: Updated SIP configuration.
        :rtype: ~SipConfiguration
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not online_pstn_gateways:
            raise ValueError("Online PSTN gateways can not be null")

        if not online_pstn_routing_settings:
            raise ValueError("Online PSTN routing setting can not be null")

        updated_sip_configuration = SipConfiguration(
            trunks=online_pstn_gateways, routes=online_pstn_routing_settings)
        return self._rest_service.patch_sip_configuration(body=updated_sip_configuration, **kwargs)

    @distributed_trace
    def update_pstn_gateways(
            self,
            online_pstn_gateways,  # type: dict[str,Trunk]
            **kwargs  # type: any
    ):  # type: (...) -> SipConfiguration
        """Updates SIP routing configuration with new SIP trunks.

        :param online_pstn_gateways: SIP trunks for routing calls
        :type trunks: dict[str, ~Trunk]
        :returns: Updated SIP configuration.
        :rtype: ~SipConfiguration
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not online_pstn_gateways:
            raise ValueError("Online PSTN gateways can not be null")

        updated_sip_configuration = SipConfiguration(
            trunks=online_pstn_gateways)
        return self._rest_service.patch_sip_configuration(body=updated_sip_configuration, **kwargs)

    @distributed_trace
    def update_routing_settings(
            self,
            online_pstn_routing_settings,  # type: list[TrunkRoute]
            **kwargs  # type: any
    ):  # type: (...) -> SipConfiguration
        """Updates SIP routing configuration with new SIP trunk routes.

        :param online_pstn_routing_settings: Trunk routes for routing calls. Route's name is used as the key.
        :type routes: list[~TrunkRoute]
        :returns: Updated SIP configuration.
        :rtype: ~SipConfiguration
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not online_pstn_routing_settings:
            raise ValueError("Online PSTN routing setting can not be null")

        updated_sip_configuration = SipConfiguration(
            routes=online_pstn_routing_settings)
        return self._rest_service.patch_sip_configuration(body=updated_sip_configuration, **kwargs)
