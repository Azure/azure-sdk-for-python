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
from azure.communication.siprouting._generated.models import (
    SipConfiguration
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
    from typing import Any
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

    @overload
    @distributed_trace_async
    async def update_sip_configuration(
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
    @distributed_trace_async
    async def update_sip_configuration(
        self,
        **kwargs
    ):  # type: (**Any) -> SipConfiguration
        """Updates SIP routing configuration with new SIP trunks and SIP trunk routes.

        :keyword trunks: SIP trunks for routing calls
        :paramtype trunks: Dict[str, ~azure.communication.siprouting.models.Trunk]
        :keyword routes: Trunk routes for routing calls. Route's name is used as the key.
        :paramtype routes: list[~azure.communication.siprouting.models.TrunkRoute]
        :returns: Updated SIP configuration.
        :rtype: ~azure.communication.siprouting.models.SipConfiguration
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @distributed_trace_async
    async def update_sip_configuration(
        self,
        *args, # type: SipConfiguration
        **kwargs # type: any
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

        return await self._rest_service.patch_sip_configuration(
            body=configuration, **kwargs
        )

    async def close(self) -> None:
        await self._rest_service.close()

    async def __aenter__(self) -> "SipRoutingClient":
        await self._rest_service.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._rest_service.__aexit__(*args)
