# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.core.credentials import AccessToken, AzureKeyCredential
from azure.core.paging import ItemPaged
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from ._api_version import RemoteRenderingApiVersion, validate_api_version
from ._generated import RemoteRenderingRestClient

from ._generated.models import (AssetConversion, AssetConversionInputSettings,
                                AssetConversionOutputSettings,
                                AssetConversionSettings,
                                CreateAssetConversionSettings,
                                CreateRenderingSessionSettings,
                                RenderingSession, RenderingSessionSize,
                                UpdateSessionSettings)
from ._polling import ConversionPolling, SessionPolling
from ._shared.authentication_endpoint import construct_endpoint_url
from ._shared.mixed_reality_token_credential import get_mixedreality_credential
from ._shared.mixedreality_account_key_credential import \
    MixedRealityAccountKeyCredential
from ._shared.static_access_token_credential import StaticAccessTokenCredential
from ._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Union

    from azure.core.credentials import TokenCredential


class RemoteRenderingClient(object):
    """A client for the Azure Remote Rendering Service.

    This client offers functionality to convert assets to the format expected by the runtime, and also to manage the
    lifetime of remote rendering sessions.

    :param str endpoint:
        The rendering service endpoint. This determines the region in which the rendering session is created and
        asset conversions are performed.
    :param str account_id: The Azure Remote Rendering account identifier.
    :param str account_domain:
        The Azure Remote Rendering account domain. For example, for an account created in the eastus region, this
        will have the form "eastus.mixedreality.azure.com"
    :param credential: Authentication for the Azure Remote
        Rendering account. Can be of the form of an AzureKeyCredential, TokenCredential or an AccessToken acquired
        from the Mixed Reality Secure Token Service (STS).
    :type credential: Union[TokenCredential, AzureKeyCredential, AccessToken]
    :keyword api_version:
        The API version of the service to use for requests. It defaults to the latest service version.
        Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str or ~azure.mixedreality.remoterenderings.RemoteRenderingApiVersion
    """

    def __init__(self, endpoint, account_id, account_domain, credential, **kwargs):
        # type: (str, str, str, Union[TokenCredential, AccessToken], Any) -> None
        self._api_version = kwargs.pop(
            "api_version", RemoteRenderingApiVersion.V2021_01_01
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

        if isinstance(credential, AccessToken):
            cred = StaticAccessTokenCredential(credential)  # type: TokenCredential
        elif isinstance(credential, AzureKeyCredential):
            cred = MixedRealityAccountKeyCredential(
                account_id=account_id, account_key=credential)
        else:
            cred = credential

        self.polling_interval = kwargs.pop("polling_interval", 5)
        endpoint_url = kwargs.pop(
            'authentication_endpoint_url', construct_endpoint_url(account_domain))
        # otherwise assume it is a TokenCredential and simply pass it through
        pipeline_credential = get_mixedreality_credential(
            account_id=account_id, account_domain=account_domain, credential=cred, endpoint_url=endpoint_url)

        if pipeline_credential is None:
            raise ValueError("credential is not of type TokenCredential, AzureKeyCredential or AccessToken")

        authentication_policy = BearerTokenCredentialPolicy(
            pipeline_credential, endpoint_url + '/.default')

        self._account_id = account_id

        self._client = RemoteRenderingRestClient(
            endpoint=endpoint,
            authentication_policy=authentication_policy,
            sdk_moniker=SDK_MONIKER,
            api_version=self._api_version,
            **kwargs)

    @distributed_trace
    def begin_asset_conversion(self, conversion_id, input_settings, output_settings, **kwargs):
        # type: (str, AssetConversionInputSettings, AssetConversionOutputSettings, Any) -> LROPoller[AssetConversion]
        """
        Start a new asset conversion with the given options.
        :param str conversion_id:
            An ID uniquely identifying the conversion for the remote rendering account. The ID is case sensitive, can
            contain any combination of alphanumeric characters including hyphens and underscores, and cannot contain
            more than 256 characters.
        :param ~azure.mixedreality.remoterendering.AssetConversionInputSettings input_settings: Options for the
            input of the conversion.
        :param ~azure.mixedreality.remoterendering.AssetConversionOutputSettings output_settings: Options for the
            output of the conversion.
        :return: A poller for the created asset conversion
        :rtype: ~azure.core.polling.LROPoller[AssetConversion]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        polling_interval = kwargs.pop("polling_interval", self.polling_interval)

        initial_state = self._client.remote_rendering.create_conversion(
            account_id=self._account_id,
            conversion_id=conversion_id,
            body=CreateAssetConversionSettings(settings=AssetConversionSettings(
                input_settings=input_settings, output_settings=output_settings)),
            **kwargs)

        polling_method = ConversionPolling(account_id=self._account_id, polling_interval=polling_interval)
        return LROPoller(client=self._client,
                         initial_response=initial_state,
                         deserialization_callback=lambda: None,
                         polling_method=polling_method)

    @distributed_trace
    def get_asset_conversion(self, conversion_id, **kwargs):
        # type: (str, Any) -> AssetConversion
        """
        Retrieve the state of a previously created conversion.
        :param str conversion_id:
            The identifier of the conversion to retrieve.
        :return: Information about the ongoing conversion process.
        :rtype: ~azure.mixedreality.remoterendering.models.AssetConversion
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._client.remote_rendering.get_conversion(
            account_id=self._account_id, conversion_id=conversion_id, **kwargs)

    @distributed_trace
    def get_asset_conversion_poller(self, **kwargs):
        # type: (Any) -> LROPoller[AssetConversion]
        """
        Returns a poller for an existing conversion by conversion id or a continuation token retrieved from a previous
        poller.
        :keyword conversion_id: The conversion id of a previously created conversion.
        :paramtype conversion_id: str
        :keyword continuation_token:
            A continuation token retrieved from a poller of a conversion.
        :paramtype continuation_token: str
        :return: A poller for the created asset conversion
        :rtype: ~azure.core.polling.LROPoller[AssetConversion]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        conversion_id = kwargs.pop("conversion_id", None)  # type: Union[str,None]
        continuation_token = kwargs.pop("continuation_token", None)  # type: Union[str,None]

        if conversion_id is None and continuation_token is None:
            raise ValueError(
                "Either conversion_id or continuation_token needs to be supplied.")

        if conversion_id is not None and continuation_token is not None:
            raise ValueError(
                "Parameters conversion_id and continuation_token are mutual exclusive. Supply only one of the two.")

        polling_interval = kwargs.pop("polling_interval", self.polling_interval)
        polling_method = ConversionPolling(account_id=self._account_id, polling_interval=polling_interval)
        if continuation_token is not None:
            return LROPoller.from_continuation_token(continuation_token=continuation_token,
                                                     polling_method=polling_method,
                                                     client=self._client)

        if conversion_id is not None:
            initial_state = self._client.remote_rendering.get_conversion(
                account_id=self._account_id,
                conversion_id=conversion_id,
                **kwargs)

        return LROPoller(client=self._client,
                         initial_response=initial_state,
                         deserialization_callback=lambda: None,
                         polling_method=polling_method)

    @distributed_trace
    def list_asset_conversions(self, **kwargs):
        # type: (...) -> ItemPaged[AssetConversion]
        """ Gets conversions for the remote rendering account.
        :rtype: ItemPaged[AssetConversion]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._client.remote_rendering.list_conversions(account_id=self._account_id, **kwargs)  # type: ignore

    @distributed_trace
    def begin_rendering_session(self, session_id, size, lease_time_minutes, **kwargs):
        # type: (str, Union[str, RenderingSessionSize], int, Any) -> LROPoller[RenderingSession]
        """
        :param str session_id: An ID uniquely identifying the rendering session for the given account. The ID is case
            sensitive, can contain any combination of alphanumeric characters including hyphens and underscores, and
            cannot contain more than 256 characters.
        :param size: Size of the server used for the rendering session. Remote Rendering with Standard size server has
            a maximum scene size of 20 million polygons. Remote Rendering with Premium size does not enforce a hard
            maximum, but performance may be degraded if your content exceeds the rendering capabilities of the service.
        :param int lease_time_minutes: The time in minutes the session will run after reaching the 'Ready' state.
        :type size: str or ~azure.mixedreality.remoterendering.RenderingSessionSize
        :return: A poller for the created rendering session
        :rtype: LROPoller[RenderingSession]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        settings = CreateRenderingSessionSettings(
            size=size, lease_time_minutes=lease_time_minutes)
        initial_state = self._client.remote_rendering.create_session(
            account_id=self._account_id,
            session_id=session_id,
            body=settings,
            **kwargs)
        polling_interval = kwargs.pop("polling_interval", self.polling_interval)
        polling_method = SessionPolling(account_id=self._account_id, polling_interval=polling_interval)
        return LROPoller(client=self._client,
                         initial_response=initial_state,
                         deserialization_callback=lambda: None,
                         polling_method=polling_method)

    @distributed_trace
    def get_rendering_session(self, session_id, **kwargs):
        # type: (str, Any) -> RenderingSession
        '''
        Returns the properties of a previously generated rendering session.
        :param str session_id: The identifier of the rendering session.
        :return: Properties of the rendering session
        :rtype:  ~azure.mixedreality.remoterendering.models.RenderingSession
        :raises ~azure.core.exceptions.HttpResponseError:
        '''
        return self._client.remote_rendering.get_session(
            account_id=self._account_id,
            session_id=session_id,
            **kwargs)

    def get_rendering_session_poller(self, **kwargs):
        # type: (Any) -> LROPoller[RenderingSession]
        """
        Returns a poller for an existing rendering session by session id or a continuation token retrieved from a
        previous poller.
        :keyword session_id: The conversion id of a previously created conversion.
        :paramtype session_id: str
        :keyword continuation_token:
            A continuation token retrieved from a poller of a session.
        :paramtype continuation_token: str
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        session_id = kwargs.pop("session_id", None)  # type: Union[str,None]
        continuation_token = kwargs.pop("continuation_token", None)  # type: Union[str,None]

        if session_id is None and continuation_token is None:
            raise ValueError(
                "Either session_id or continuation_token needs to be supplied.")

        if session_id is not None and continuation_token is not None:
            raise ValueError(
                "Parameters session_id and continuation_token are mutual exclusive. Supply only one of the two.")

        polling_interval = kwargs.pop("polling_interval", self.polling_interval)
        if continuation_token is not None:
            polling_method = SessionPolling(account_id=self._account_id, polling_interval=polling_interval)
            return LROPoller.from_continuation_token(continuation_token=continuation_token,
                                                     polling_method=polling_method,
                                                     client=self._client)

        if session_id is not None:
            initial_state = self._client.remote_rendering.get_session(
                account_id=self._account_id,
                session_id=session_id,
                **kwargs)

        polling_method = SessionPolling(account_id=self._account_id, polling_interval=polling_interval)
        return LROPoller(client=self._client,
                         initial_response=initial_state,
                         deserialization_callback=lambda: None,
                         polling_method=polling_method)

    @distributed_trace
    def stop_rendering_session(self, session_id, **kwargs):
        # type:  (str, Any) -> None
        """
        :param str session_id: The identifier of the session to be stopped.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._client.remote_rendering.stop_session(
            account_id=self._account_id, session_id=session_id, **kwargs)

    @distributed_trace
    def update_rendering_session(self, session_id, **kwargs):
        # type: (str, Any) -> RenderingSession
        """
        Updates an already existing rendering session.
        :param str session_id: The identifier of the session to be updated.
        :keyword lease_time_minutes: The new lease time of the rendering session. Has to be strictly larger than
            the previous lease time.
        :paramtype lease_time_minutes: int
        :return: The properties of the updated session
        :rtype: ~azure.mixedreality.remoterendering.models.RenderingSession
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        lease_time_minutes = kwargs.pop("lease_time_minutes", None)  # type: Union[int,None]
        if lease_time_minutes is not None:
            return self._client.remote_rendering.update_session(account_id=self._account_id,
                                                                session_id=session_id,
                                                                body=UpdateSessionSettings(
                                                                    lease_time_minutes=lease_time_minutes),
                                                                **kwargs)

        # if no param to update has been provided the unchanged session is returned
        return self._client.remote_rendering.get_session(account_id=self._account_id,
                                                         session_id=session_id,
                                                         **kwargs)

    @distributed_trace
    def list_rendering_sessions(self, **kwargs):
        # type: (...) -> ItemPaged[RenderingSession]
        """
        List rendering sessions in the 'Ready' or 'Starting' state. Does not return stopped or failed rendering
            sessions.
        :rtype: ItemPaged[RenderingSession]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._client.remote_rendering.list_sessions(account_id=self._account_id, **kwargs)  # type: ignore

    def close(self):
        # type: () -> None
        self._client.close()

    def __enter__(self):
        # type: () -> RemoteRenderingClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
