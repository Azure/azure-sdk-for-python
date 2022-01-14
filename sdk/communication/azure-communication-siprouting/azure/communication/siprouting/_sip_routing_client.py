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
    SipConfiguration
)

from ._generated._azure_communication_sip_routing_service import (
    AzureCommunicationSIPRoutingService,
)

from ._authentication._client_utils import (
    parse_connection_str,
    get_authentication_policy
)
from ._version import SDK_MONIKER

if TYPE_CHECKING:
    from typing import Dict, Any
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

        self._rest_service = AzureCommunicationSIPRoutingService(
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

        acs_resource_calling_configuration = self._rest_service.get_sip_configuration(
            **kwargs
        )

        return acs_resource_calling_configuration

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

        configuration = args[0] if args else None

        if not configuration:
            configuration = SipConfiguration(
                trunks=kwargs.pop("trunks", {}),
                routes=kwargs.pop("routes", {}))

        return self._rest_service.patch_sip_configuration(
            body=configuration, **kwargs
        )
