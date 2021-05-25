from ._generated._azure_communication_sip_routing_service import AzureCommunicationSIPRoutingService
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore


class SIPRoutingClient():
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

    def get_sip_configuration(
            self,
            cancellation_token):
        acs_resource_calling_configuration = self._rest_service.get_sip_configuration()
        return acs_resource_calling_configuration
