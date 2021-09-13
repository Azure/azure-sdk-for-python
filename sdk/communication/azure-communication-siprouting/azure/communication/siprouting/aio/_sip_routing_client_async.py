# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import List, Dict, Any  # pylint: disable=unused-import

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

from azure.core.tracing.decorator_async import distributed_trace_async
from azure.communication.siprouting._generated.models import (
    SipConfiguration,
    SipConfigurationPatch,
    Trunk,
    TrunkRoute,
)
from .._generated.aio._azure_communication_sip_routing_service import (
    AzureCommunicationSIPRoutingService,
)
from .._authentication._client_utils import (
    parse_connection_str,
    get_authentication_policy,
)
from .._authentication._user_credential_async import CommunicationTokenCredential
from .._version import SDK_MONIKER


class SipRoutingClient(object):
    """A client to interact with the AzureCommunicationService SIP routing gateway asynchronously.
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

        self._rest_service = AzureCommunicationSIPRoutingService(
            self._endpoint,
            authentication_policy=self._authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs
        )

    @classmethod
    def from_connection_string(
        cls,
        connection_string,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> SipRoutingClient
        """Factory method for creating client from connection string.

        :param connection_string: Connection string containing endpoint and credentials
        :type connection_string: str
        :returns: The newly created client.
        :rtype: ~azure.communication.siprouting.models.SipRoutingClient
        """

        endpoint, credential = parse_connection_str(connection_string)
        return cls(endpoint, credential, **kwargs)

    @distributed_trace_async
    async def get_sip_configuration(
        self, **kwargs  # type: Any
    ):  # type: (...) -> SipConfiguration
        """Returns current SIP routing configuration.

        :returns: Current SIP routing configuration.
        :rtype: ~azure.communication.siprouting.models.SipConfiguration
        """

        acs_resource_calling_configuration = (
            await self._rest_service.get_sip_configuration(**kwargs)
        )

        return acs_resource_calling_configuration

    @distributed_trace_async
    async def update_sip_configuration(
        self,
        sip_configuration,  # type: SipConfiguration
        **kwargs  # type: Any
    ):  # type: (...) -> SipConfiguration
        """Updates SIP routing configuration with new SIP trunks and trunk routes.

        :param sip_configuration: SIP trunks for routing calls
        :type sip_configuration: ~azure.communication.siprouting.models.SipConfiguration
        :returns: Updated SIP configuration.
        :rtype: ~azure.communication.siprouting.models.SipConfiguration
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not sip_configuration:
            raise ValueError("SIP configuration can not be null")

        if not sip_configuration.trunks:
            raise ValueError("SIP trunks can not be null")

        if not sip_configuration.routes:
            raise ValueError("SIP routes can not be null")

        updated_sip_configuration = SipConfigurationPatch(
            trunks=sip_configuration.trunks, routes=sip_configuration.routes
        )
        return await self._rest_service.patch_sip_configuration(
            body=updated_sip_configuration, **kwargs
        )

    @distributed_trace_async
    async def update_sip_trunks(
        self,
        sip_trunks,  # type: Dict[str,Trunk]
        **kwargs  # type: Any
    ):  # type: (...) -> SipConfiguration
        """Updates SIP routing configuration with new SIP trunks.

        :param sip_trunks: SIP trunks for routing calls
        :type sip_trunks: Dict[str, ~azure.communication.siprouting.models.Trunk]
        :returns: Updated SIP configuration.
        :rtype: ~azure.communication.siprouting.models.SipConfiguration
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not sip_trunks:
            raise ValueError("SIP trunks can not be null")

        updated_sip_configuration = SipConfigurationPatch(trunks=sip_trunks)
        return await self._rest_service.patch_sip_configuration(
            body=updated_sip_configuration, **kwargs
        )

    @distributed_trace_async
    async def update_sip_routes(
        self,
        sip_routes,  # type: List[TrunkRoute]
        **kwargs  # type: Any
    ):  # type: (...) -> SipConfiguration
        """Updates SIP routing configuration with new SIP trunk routes.

        :param sip_routes: Trunk routes for routing calls. Route's name is used as the key.
        :type sip_routes: List[~azure.communication.siprouting.models.TrunkRoute]
        :returns: Updated SIP configuration.
        :rtype: ~azure.communication.siprouting.models.SipConfiguration
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not sip_routes:
            raise ValueError("SIP routes can not be null")

        updated_sip_configuration = SipConfigurationPatch(routes=sip_routes)
        return await self._rest_service.patch_sip_configuration(
            body=updated_sip_configuration, **kwargs
        )

    async def close(self) -> None:
        await self._rest_service.close()

    async def __aenter__(self) -> "SipRoutingClient":
        await self._rest_service.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._rest_service.__aexit__(*args)
