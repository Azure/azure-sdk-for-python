# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


from typing import Any, Callable, Union

from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AccessToken, AzureKeyCredential
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.polling import AsyncLROPoller
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.credentials_async import AsyncTokenCredential

from .._api_version import validate_api_version, DEFAULT_VERSION
from .._generated.aio import RemoteRenderingRestClient
from .._generated.models import (AssetConversion, AssetConversionInputSettings,
                                 AssetConversionOutputSettings,
                                 AssetConversionSettings,
                                 CreateAssetConversionSettings,
                                 CreateRenderingSessionSettings,
                                 RenderingSession, RenderingSessionSize,
                                 UpdateSessionSettings)
from .._shared.aio.mixed_reality_token_credential import \
    get_mixedreality_credential
from .._shared.aio.mixedreality_account_key_credential import \
    MixedRealityAccountKeyCredential
from .._shared.aio.static_access_token_credential import \
    StaticAccessTokenCredential
from .._shared.authentication_endpoint import construct_endpoint_url
from .._version import SDK_MONIKER
from ._polling_async import ConversionPollingAsync, SessionPollingAsync

class RemoteRenderingClient(object):
    """A client for the Azure Remote Rendering Service.

    This client offers functionality to convert assets to the format expected by the runtime, and also to manage the
    lifetime of remote rendering sessions.

    :param endpoint:
        The rendering service endpoint. This determines the region in which the rendering session is created and
        asset conversions are performed.
    :type endpoint: str
    :param account_id: The Azure Remote Rendering account identifier.
    :type account_id: str
    :param account_domain:
        The Azure Remote Rendering account domain. For example, for an account created in the eastus region, this
        will have the form "eastus.mixedreality.azure.com"
    :type account_domain: str
    :param credential: Authentication for the Azure Remote
        Rendering account. Can be of the form of an AzureKeyCredential, AsyncTokenCredential or an AccessToken acquired
        from the Mixed Reality Secure Token Service (STS).
    :type credential: Union[AzureKeyCredential, AsyncTokenCredential, AccessToken]
    :keyword api_version:
        The API version of the service to use for requests. It defaults to the latest service version.
        Setting to an older version may result in reduced feature compatibility.
    :type api_version: str or ~azure.mixedreality.remoterenderings.RemoteRenderingApiVersion
    :keyword polling_interval:
        Seconds to wait between each check, whether the session is ready yet.
    :type polling_interval: int
    :keyword authentication_endpoint_url:
        Overwrite for the authentication endpoint. Usually using account_domain for the authentication domain is enough.
        If used, specify the whole authentication url including the schema.
    :type authentication_endpoint_url: str
    """

    def __init__(self,
                 endpoint: str,
                 account_id: str,
                 account_domain: str,
                 credential: Union[AzureKeyCredential, 'AsyncTokenCredential', AccessToken],
                 **kwargs) -> None:

        self._api_version = kwargs.pop(
            "api_version", DEFAULT_VERSION
        )
        validate_api_version(self._api_version)

        if not endpoint:
            raise ValueError("endpoint cannot be None")

        if not account_id:
            raise ValueError("account_id cannot be None")

        if not account_domain:
            raise ValueError("account_domain cannot be None")

        if not credential:
            raise ValueError("credential cannot be None")

        self.polling_interval = kwargs.pop("polling_interval", 5)
        endpoint_url = kwargs.pop('authentication_endpoint_url', construct_endpoint_url(account_domain))

        cred: Any

        if isinstance(credential, AccessToken):
            cred = StaticAccessTokenCredential(credential)
        elif isinstance(credential, AzureKeyCredential):
            cred = MixedRealityAccountKeyCredential(account_id=account_id, account_key=credential)
        else:
            cred = credential

        pipeline_credential = get_mixedreality_credential(
                                account_id=account_id,
                                account_domain=account_domain,
                                credential=cred,
                                endpoint_url=endpoint_url)

        if pipeline_credential is None:
            raise ValueError("credential is not of type TokenCredential, AzureKeyCredential or AccessToken")

        authentication_policy = AsyncBearerTokenCredentialPolicy(
            pipeline_credential, endpoint_url + '/.default')

        self._account_id = account_id

        self._client = RemoteRenderingRestClient(
            endpoint=endpoint,
            authentication_policy=authentication_policy,
            sdk_moniker=SDK_MONIKER,
            api_version=self._api_version,
            **kwargs)

    @distributed_trace_async
    async def begin_asset_conversion(self,
                                     conversion_id: str,
                                     input_settings: AssetConversionInputSettings,
                                     output_settings: AssetConversionOutputSettings,
                                     **kwargs) -> AsyncLROPoller[AssetConversion]:
        """Start a new asset conversion with the given options.

        :param str conversion_id:
            An ID uniquely identifying the conversion for the remote rendering account. The ID is case sensitive, can
            contain any combination of alphanumeric characters including hyphens and underscores, and cannot contain
            more than 256 characters.
        :param ~azure.mixedreality.remoterendering.AssetConversionInputSettings input_settings: Options for the
            input of the conversion.
        :param ~azure.mixedreality.remoterendering.AssetConversionOutputSettings output_settings: Options for the
            output of the conversion.
        :return: A poller for the created asset conversion
        :rtype: ~azure.core.polling.AsyncLROPoller[AssetConversion]
        """
        polling_interval = kwargs.pop("polling_interval", self.polling_interval)
        polling_method = ConversionPollingAsync(account_id=self._account_id, polling_interval=polling_interval)
        settings = AssetConversionSettings(input_settings=input_settings, output_settings=output_settings)
        initial_state = await self._client.remote_rendering.create_conversion(account_id=self._account_id,
                                                                              conversion_id=conversion_id,
                                                                              body=CreateAssetConversionSettings(
                                                                                  settings=settings),
                                                                              **kwargs)
        deserialization_method: Callable[[Any], Any] = lambda _: None

        return AsyncLROPoller(client=self._client,
                              initial_response=initial_state,
                              deserialization_callback=deserialization_method,
                              polling_method=polling_method)

    @distributed_trace_async
    async def get_asset_conversion(self, conversion_id: str, **kwargs) -> AssetConversion:
        """Retrieve the state of a previously created conversion.

        :param str conversion_id:
            The identifier of the conversion to retrieve.
        :return: Information about the ongoing conversion process.
        :rtype: ~azure.mixedreality.remoterendering.AssetConversion
        """
        return await self._client.remote_rendering.get_conversion(account_id=self._account_id,
                                                                  conversion_id=conversion_id,
                                                                  **kwargs)

    @distributed_trace_async
    async def get_asset_conversion_poller(self, **kwargs) -> AsyncLROPoller[AssetConversion]: # pylint:disable=docstring-keyword-should-match-keyword-only
        """Returns a poller for an existing conversion by conversion id or a continuation
        token retrieved from a previous poller.

        :keyword str conversion_id: The conversion id of a previously created conversion.
        :keyword str continuation_token: A continuation token retrieved from a poller of a conversion.
        :return: A poller for the created asset conversion
        :rtype: ~azure.core.polling.AsyncLROPoller[AssetConversion]
        """

        conversion_id: Union[str,None] = kwargs.pop("conversion_id", None)
        continuation_token: Union[str,None] = kwargs.pop("continuation_token", None)

        if conversion_id is None and continuation_token is None:
            raise ValueError(
                "Either conversion_id or continuation_token needs to be supplied.")

        if conversion_id is not None and continuation_token is not None:
            raise ValueError(
                "Parameters conversion_id and continuation_token are mutual exclusive. Supply only one of the two.")
        polling_interval = kwargs.pop("polling_interval", self.polling_interval)
        polling_method = ConversionPollingAsync(account_id=self._account_id, polling_interval=polling_interval)
        if continuation_token is not None:
            initial_state = await ConversionPollingAsync.initial_response_from_continuation_token(
                continuation_token,
                client=self._client,
                **kwargs)

        if conversion_id is not None:
            initial_state = await self._client.remote_rendering.get_conversion(
                account_id=self._account_id,
                conversion_id=conversion_id,
                **kwargs)

        deserialization_method: Callable[[Any], Any] = lambda _: None

        return AsyncLROPoller(client=self._client,
                              initial_response=initial_state,
                              deserialization_callback=deserialization_method,
                              polling_method=polling_method)

    @distributed_trace_async
    async def list_asset_conversions(self, **kwargs) -> AsyncItemPaged[AssetConversion]:
        """Returns list of conversions for the remote rendering account.

        :rtype: AsyncItemPaged[AssetConversion]
        :return: List of conversions for the remote rendering account.
        """
        return self._client.remote_rendering.list_conversions(account_id=self._account_id, **kwargs) # type: ignore

    @distributed_trace_async
    async def begin_rendering_session(self,
                                      session_id: str,
                                      size: Union[str, RenderingSessionSize],
                                      lease_time_minutes: int,
                                      **kwargs) -> AsyncLROPoller[RenderingSession]:
        """

        :param session_id: An ID uniquely identifying the rendering session for the given account. The ID is case
            sensitive, can contain any combination of alphanumeric characters including hyphens and underscores, and
            cannot contain more than 256 characters.
        :type session_id: str
        :param size: Size of the server used for the rendering session. Remote Rendering with Standard size server has
            a maximum scene size of 20 million polygons. Remote Rendering with Premium size does not enforce a hard
            maximum, but performance may be degraded if your content exceeds the rendering capabilities of the service.
        :type size: str or ~azure.mixedreality.remoterendering.RenderingSessionSize
        :param lease_time_minutes: The time in minutes the session will run after reaching the 'Ready' state.
        :type lease_time_minutes: int
        :return: A poller for the created rendering session
        :rtype: AsyncLROPoller[RenderingSession]
        """
        polling_interval = kwargs.pop("polling_interval", self.polling_interval)
        polling_method = SessionPollingAsync(account_id=self._account_id, polling_interval=polling_interval)
        settings = CreateRenderingSessionSettings(
            size=size, lease_time_minutes=lease_time_minutes)
        initial_state = await self._client.remote_rendering.create_session(account_id=self._account_id,
                                                                           session_id=session_id,
                                                                           body=settings,
                                                                           **kwargs)

        deserialization_method: Callable[[Any], Any] = lambda _: None

        return AsyncLROPoller(client=self._client,
                              initial_response=initial_state,
                              deserialization_callback=deserialization_method,
                              polling_method=polling_method)

    @distributed_trace_async
    async def get_rendering_session(self, session_id: str, **kwargs) -> RenderingSession:
        '''Returns the properties of a previously generated rendering session.

        :param str session_id: The identifier of the rendering session.
        :return: Properties of the rendering session
        :rtype:  ~azure.mixedreality.remoterendering.RenderingSession
        '''
        return await self._client.remote_rendering.get_session(self._account_id, session_id=session_id, **kwargs)

    @distributed_trace_async
    async def get_rendering_session_poller(self, **kwargs) -> AsyncLROPoller[RenderingSession]: # pylint:disable=docstring-keyword-should-match-keyword-only
        """Returns a poller for an existing rendering session by session id or a continuation token retrieved from a
        previous poller.

        :keyword str session_id: The conversion id of a previously created conversion.
        :keyword str continuation_token: A continuation token retrieved from a poller of a session.
        :return: A poller for the created rendering session
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.mixedreality.remoterendering.RenderingSession]
        """

        session_id: Union[str,None] = kwargs.pop("session_id", None)
        continuation_token: Union[str,None] = kwargs.pop("continuation_token", None)

        if session_id is None and continuation_token is None:
            raise ValueError(
                "Either session_id or continuation_token needs to be supplied.")

        if session_id is not None and continuation_token is not None:
            raise ValueError(
                "Parameters session_id and continuation_token are mutual exclusive. Supply only one of the two.")
        polling_interval = kwargs.pop("polling_interval", self.polling_interval)
        polling_method = SessionPollingAsync(account_id=self._account_id, polling_interval=polling_interval)
        if continuation_token is not None:
            initial_state = await SessionPollingAsync.initial_response_from_continuation_token(
                continuation_token=continuation_token,
                client=self._client, **kwargs)

        if session_id is not None:
            initial_state = await self._client.remote_rendering.get_session(
                account_id=self._account_id,
                session_id=session_id,
                **kwargs)

        deserialization_method: Callable[[Any], Any] = lambda _: None

        return AsyncLROPoller(client=self._client,
                              initial_response=initial_state,
                              deserialization_callback=deserialization_method,
                              polling_method=polling_method)

    @distributed_trace_async
    async def update_rendering_session(self, session_id: str, **kwargs) -> RenderingSession: # pylint:disable=docstring-keyword-should-match-keyword-only
        """Updates an already existing rendering session.

        :param str session_id: The identifier of the session to be updated.
        :keyword int lease_time_minutes: The new lease time of the rendering session. Has to be strictly larger than
            the previous lease time.
        :return: The updated rendering session
        :rtype: ~azure.mixedreality.remoterendering.models.RenderingSession
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        lease_time_minutes: Union[int,None] = kwargs.pop("lease_time_minutes", None)
        if lease_time_minutes is not None:
            return await self._client.remote_rendering.update_session(account_id=self._account_id,
                                                                      session_id=session_id,
                                                                      body=UpdateSessionSettings(
                                                                          lease_time_minutes=lease_time_minutes),
                                                                      **kwargs)

        # if no param to update has been provided the unchanged session is returned
        return await self._client.remote_rendering.get_session(self._account_id, session_id=session_id, **kwargs)

    @distributed_trace_async
    async def stop_rendering_session(self, session_id: str, **kwargs) -> None:
        """

        :param str session_id: The identifier of the session to be stopped.
        :return: None
        :rtype: None
        """
        return await self._client.remote_rendering.stop_session(account_id=self._account_id,
                                                                session_id=session_id,
                                                                **kwargs)

    @distributed_trace_async
    async def list_rendering_sessions(
            self,
            **kwargs) -> AsyncItemPaged[RenderingSession]:
        """Returns list of rendering sessions in the 'Ready' or 'Starting' state.
        Does not return stopped or failed rendering sessions.

        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.mixedreality.remoterendering.RenderingSession]
        :return: List of rendering sessions in the 'Ready' or 'Starting' state.
        """
        return self._client.remote_rendering.list_sessions(account_id=self._account_id, **kwargs) # type: ignore

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "RemoteRenderingClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)
