from ._generated._azure_communication_sip_routing_service import AzureCommunicationSIPRoutingService
from ._shared.utils import parse_connection_str
from ._generated.models import SipConfiguration

from azure.core.tracing.decorator import distributed_trace

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore


class SIPRoutingClient(object):
    def __init__(
            self,
            endpoint,  # type: str
            credential, 
            **kwargs  # type: any
    ):
        # type: (...) -> None
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
    def from_connection_string(cls, connection_string, **kwargs):
        # type: (str, **Any) -> None
        """Factory method for creating client from connection string
        
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
            **kwargs):

        acs_resource_calling_configuration = self._rest_service.get_sip_configuration(kwargs)
        return acs_resource_calling_configuration

    @distributed_trace
    def update_sip_trunk_configuration(
            self,
            online_pstn_gateways,
            online_pstn_routing_settings,
            **kwargs
            ):

        if not online_pstn_gateways:
            raise ValueError("Online PSTN gateways can not be null")

        if not online_pstn_routing_settings:
            raise ValueError("Online PSTN routing setting can not be null")

        updated_sip_configuration = SipConfiguration(trunks = online_pstn_gateways, routes = online_pstn_routing_settings)
        return self._rest_service.patch_sip_configuration(updated_sip_configuration, kwargs)

    @distributed_trace
    def update_pstn_gateways(
            self,
            online_pstn_gateways,
            **kwargs
            ):

        if not online_pstn_gateways:
            raise ValueError("Online PSTN gateways can not be null")

        updated_sip_configuration = SipConfiguration(trunks = online_pstn_gateways)
        return self._rest_service.patch_sip_configuration(updated_sip_configuration, kwargs)

    @distributed_trace
    def update_routing_settings(
            self,
            online_pstn_routing_settings,
            **kwargs
            ):

        if not online_pstn_routing_settings:
            raise ValueError("Online PSTN routing setting can not be null")

        updated_sip_configuration = SipConfiguration(routes = online_pstn_routing_settings)
        return self._rest_service.patch_sip_configuration(updated_sip_configuration, kwargs)
