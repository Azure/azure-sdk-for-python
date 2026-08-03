# pylint: disable=line-too-long,useless-suppression
# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import datetime
import functools
from typing import Any, Dict, List, Optional, Union
from azure.core import MatchConditions
from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import ResourceNotFoundError, ResourceNotModifiedError
from azure.core.rest import AsyncHttpResponse, HttpRequest
from ._sync_token_async import AsyncSyncTokenPolicy
from .._azure_appconfiguration_error import ResourceReadOnlyError
from .._azure_appconfiguration_requests import AppConfigRequestsCredentialsPolicy
from .._query_param_policy import QueryParamPolicy
from .._generated.aio import AzureAppConfigurationClient as AzureAppConfigurationClientGenerated
from .._generated.models import FeatureFlagFields, LabelFields
from .._models import (
    FeatureFlag,
    ConfigurationSettingLabel,
    AsyncFeatureFlagPaged,
    FeatureFlagPropertiesPagedAsync,
)
from .._audience import get_audience, DEFAULT_SCOPE_SUFFIX
from .._utils import parse_connection_string
from .._audience_error_handling_policy import AudienceErrorHandlingPolicy


class FeatureFlagClient:
    """Represents a client that manages feature flags in the Azure App Configuration service.

    :param str base_url: Base url of the service.
    :param credential: An object which can provide secrets for the app configuration service
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: Api Version. Default value is "2023-11-01". Note that overriding this default
        value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword audience: The audience to use for authentication with Microsoft Entra. Defaults to the public Azure App
        Configuration audience. See the supported audience list at https://aka.ms/appconfig/client-token-audience
    :paramtype audience: str


    This is the async version of :class:`~azure.appconfiguration.FeatureFlagClient`

    """

    # pylint:disable=protected-access
    def __init__(self, base_url: str, credential: AsyncTokenCredential, **kwargs: Any) -> None:
        try:
            if not base_url.lower().startswith("http"):
                base_url = f"https://{base_url}"
        except AttributeError as exc:
            raise ValueError("Base URL must be a string.") from exc

        if not credential:
            raise ValueError("Missing credential")

        self._sync_token_policy = AsyncSyncTokenPolicy()
        self._query_param_policy = QueryParamPolicy()

        audience = kwargs.pop("audience", None)

        audience_policy = AudienceErrorHandlingPolicy(bool(audience))
        per_call_policies = [self._query_param_policy, self._sync_token_policy, audience_policy]

        if audience is None:
            audience = get_audience(base_url)

        # Ensure all scopes end with /.default and strip any trailing slashes before adding suffix
        audience_scope = audience.rstrip("/") + "/" + DEFAULT_SCOPE_SUFFIX
        kwargs["credential_scopes"] = [audience_scope]

        if isinstance(credential, AzureKeyCredential):
            id_credential = kwargs.pop("id_credential")
            kwargs.update(
                {
                    "authentication_policy": AppConfigRequestsCredentialsPolicy(credential, base_url, id_credential),
                }
            )
        elif hasattr(credential, "get_token"):  # AsyncFakeCredential is not an instance of AsyncTokenCredential
            kwargs.update(
                {
                    "authentication_policy": AsyncBearerTokenCredentialPolicy(
                        credential, *kwargs["credential_scopes"], **kwargs
                    ),
                }
            )
        else:
            raise TypeError(
                f"Unsupported credential: {type(credential)}. Use an instance of token credential from azure.identity"
            )
        # mypy doesn't compare the credential type hint with the API surface in patch.py
        self._impl = AzureAppConfigurationClientGenerated(
            base_url, credential, per_call_policies=per_call_policies, **kwargs  # type: ignore[arg-type]
        )

    @classmethod
    def from_connection_string(cls, connection_string: str, **kwargs: Any) -> "FeatureFlagClient":
        """Create FeatureFlagClient from a Connection String.
        This is the async version of :class:`~azure.appconfiguration.FeatureFlagClient`

        :param str connection_string: Connection String
            (one of the access keys of the Azure App Configuration resource)
            used to access the Azure App Configuration.
        :return: A FeatureFlagClient authenticated with the connection string
        :rtype: ~azure.appconfiguration.aio.FeatureFlagClient

        Example

        .. code-block:: python

            from azure.appconfiguration.aio import FeatureFlagClient

            connection_str = "<my connection string>"
            async_client = FeatureFlagClient.from_connection_string(connection_str)
        """
        endpoint, id_credential, secret = parse_connection_string(connection_string)
        # AzureKeyCredential type is for internal use, it's not exposed in public API.
        return cls(
            credential=AzureKeyCredential(secret),  # type: ignore[arg-type]
            base_url=endpoint,
            id_credential=id_credential,
            **kwargs,
        )

    @distributed_trace_async
    async def send_request(self, request: HttpRequest, *, stream: bool = False, **kwargs: Any) -> AsyncHttpResponse:
        """Runs a network request using the client's existing pipeline.

        The request URL can be relative to the vault URL. The service API version used for the request is the same as
        the client's unless otherwise specified. This method does not raise if the response is an error; to raise an
        exception, call `raise_for_status()` on the returned response object. For more information about how to send
        custom requests with this method, see https://aka.ms/azsdk/dpcodegen/python/send_request.

        :param request: The network request you want to make.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.AsyncHttpResponse
        """
        return await self._impl.send_request(request, stream=stream, **kwargs)

    @distributed_trace
    def list_feature_flags(
        self,
        *,
        name_filter: Optional[str] = None,
        label_filter: Optional[str] = None,
        tags_filter: Optional[List[str]] = None,
        accept_datetime: Optional[Union[datetime, str]] = None,
        fields: Optional[List[Union[str, FeatureFlagFields]]] = None,
        **kwargs: Any,
    ) -> AsyncFeatureFlagPaged:
        """
        Find the FeatureFlag objects, optionally filtered by name, label, tags and accept_datetime.

        :keyword name_filter: Filter results based on their feature flag names. '*' can be used as wildcard at the end
            of the filter. Default is `None`.
        :paramtype name_filter: str or None
        :keyword label_filter: Filter results based on their labels. Default is `None`.
        :paramtype label_filter: str or None
        :keyword tags_filter: Filter results based on their tags. Default is `None`.
        :paramtype tags_filter: list[str] or None
        :keyword accept_datetime: Retrieve FeatureFlag that existed at this datetime
        :paramtype accept_datetime: ~datetime.datetime or str or None
        :keyword fields: Specify which fields to include in the results. If not specified, will include all fields.
        :paramtype fields: list[str] or list[~azure.appconfiguration.FeatureFlagFields] or None
        :return: An async iterator of :class:`~azure.appconfiguration.FeatureFlag`
        :rtype: ~azure.appconfiguration.AsyncFeatureFlagPaged
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example

        .. code-block:: python

            # List feature flags
            feature_flags = async_client.list_feature_flags()
            async for flag in feature_flags:
                print(flag.name, flag.enabled)

            # Detect changes across pages using etags
            feature_flags = async_client.list_feature_flags(name_filter="sample_*")
            match_conditions = [page.etag async for page in feature_flags.by_page()]

            feature_flags = async_client.list_feature_flags(name_filter="sample_*")
            async for page in feature_flags.by_page(match_conditions=match_conditions):
                # Only pages that changed are returned
                async for flag in page:
                    print(flag.name, flag.enabled)
        """
        if isinstance(accept_datetime, datetime):
            accept_datetime = str(accept_datetime)

        command = functools.partial(self._impl.get_feature_flags_in_one_page, **kwargs)  # type: ignore[attr-defined]  # pylint: disable=no-member
        return AsyncFeatureFlagPaged(
            command,
            name=name_filter,
            label=label_filter,
            accept_datetime=accept_datetime,
            tags=tags_filter,
            select=fields,
            page_iterator_class=FeatureFlagPropertiesPagedAsync,
        )

    @distributed_trace_async
    async def get_feature_flag(
        self,
        name: str,
        label: Optional[str] = None,
        *,
        etag: Optional[str] = None,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        accept_datetime: Optional[Union[datetime, str]] = None,
        **kwargs: Any,
    ) -> Optional["FeatureFlag"]:
        """
        Get a feature flag from the service, identified by `name` and optionally `label`.

        :param name: The feature flag name.
        :type name: str
        :param label: The label of the feature flag. Defaults to None.
        :type label: str or None
        :keyword etag: Check if the feature flag is changed. Set None to skip checking etag.
        :paramtype etag: str or None
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword accept_datetime: Retrieve the FeatureFlag that existed at this datetime.
        :paramtype accept_datetime: ~datetime.datetime or str or None
        :return: The FeatureFlag if found; None otherwise.
        :rtype: ~azure.appconfiguration.FeatureFlag or None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example

        .. code-block:: python

            feature_flag = await async_client.get_feature_flag(name="MyFeatureFlag")
        """
        if isinstance(accept_datetime, datetime):
            accept_datetime = str(accept_datetime)

        try:
            generated_feature_flag = await self._impl.feature_flag_client.get_feature_flag(
                name=name,
                label=label,
                etag=etag,
                match_condition=match_condition,
                accept_datetime=accept_datetime,
                **kwargs,
            )
            return FeatureFlag._from_generated(generated_feature_flag)
        except (ResourceNotFoundError, ResourceNotModifiedError):
            return None

    @distributed_trace_async
    async def add_feature_flag(self, feature_flag: "FeatureFlag", **kwargs: Any) -> "FeatureFlag":
        """Add a FeatureFlag instance into the Azure App Configuration service.

        :param feature_flag: The FeatureFlag object to be added
        :type feature_flag: ~azure.appconfiguration.FeatureFlag
        :return: The FeatureFlag object returned from the App Configuration service
        :rtype: ~azure.appconfiguration.FeatureFlag
        :raises: :class:`~azure.core.exceptions.HttpResponseError`, \
            :class:`~azure.core.exceptions.ClientAuthenticationError`, \
            :class:`~azure.core.exceptions.ResourceExistsError`

        Example

        .. code-block:: python

            feature_flag = FeatureFlag(
                name="MyFeatureFlag",
                enabled=True
            )
            added_feature_flag = await async_client.add_feature_flag(feature_flag)
        """
        generated_feature_flag = feature_flag._to_generated()
        generated_result = await self._impl.feature_flag_client.put_feature_flag(
            entity=generated_feature_flag,
            name=feature_flag.name,
            label=feature_flag.label,
            match_condition=MatchConditions.IfMissing,
            **kwargs,
        )
        return FeatureFlag._from_generated(generated_result)

    @distributed_trace_async
    async def set_feature_flag(
        self,
        feature_flag: "FeatureFlag",
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        *,
        etag: Optional[str] = None,
        **kwargs: Any,
    ) -> "FeatureFlag":
        """
        Create or update a feature flag via the dedicated feature flag endpoint.

        :param feature_flag: A FeatureFlag object.
        :type feature_flag: ~azure.appconfiguration.FeatureFlag
        :param match_condition: The match condition to use upon the etag.
        :type match_condition: ~azure.core.MatchConditions
        :keyword etag: The etag of the feature flag. If provided, the feature flag will be updated only if the etag matches.
        :paramtype etag: str or None
        :return: The updated FeatureFlag.
        :rtype: ~azure.appconfiguration.FeatureFlag
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        error_map: Dict[int, Any] = {409: ResourceReadOnlyError}

        if etag is None:
            etag = feature_flag.etag

        generated_feature_flag = feature_flag._to_generated()
        result = await self._impl.feature_flag_client.put_feature_flag(
            name=feature_flag.name,
            entity=generated_feature_flag,
            label=feature_flag.label,
            etag=etag,
            match_condition=match_condition,
            error_map=error_map,
            **kwargs,
        )

        return FeatureFlag._from_generated(result)

    @distributed_trace_async
    async def delete_feature_flag(
        self,
        name: str,
        label: Optional[str] = None,
        *,
        etag: Optional[str] = None,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> Union[None, "FeatureFlag"]:
        """Delete a FeatureFlag if it exists

        :param name: The feature flag name to delete
        :type name: str
        :param label: Label used to identify the FeatureFlag. Default is `None`.
        :type label: str or None
        :keyword etag: Check if the FeatureFlag is changed. Set None to skip checking etag
        :paramtype etag: str or None
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: The deleted FeatureFlag returned from the service, or None if it doesn't exist.
        :rtype: ~azure.appconfiguration.FeatureFlag or None
        :raises: :class:`~azure.appconfiguration.ResourceReadOnlyError`, \
            :class:`~azure.core.exceptions.HttpResponseError`, \
            :class:`~azure.core.exceptions.ClientAuthenticationError`, \
            :class:`~azure.core.exceptions.ResourceModifiedError`, \
            :class:`~azure.core.exceptions.ResourceNotModifiedError`, \
            :class:`~azure.core.exceptions.ResourceNotFoundError`, \
            :class:`~azure.core.exceptions.ResourceExistsError`

        Example

        .. code-block:: python

            # in async function
            deleted_feature_flag = await async_client.delete_feature_flag(name="MyFeatureFlag")
        """
        error_map: Dict[int, Any] = {409: ResourceReadOnlyError}
        generated_feature_flag = await self._impl.feature_flag_client.delete_feature_flag(
            name=name,
            label=label,
            etag=etag,
            match_condition=match_condition,
            error_map=error_map,
            **kwargs,
        )
        if generated_feature_flag:
            return FeatureFlag._from_generated(generated_feature_flag)
        return None

    @distributed_trace
    def list_feature_flag_revisions(
        self,
        *,
        name_filter: Optional[str] = None,
        label_filter: Optional[str] = None,
        tags_filter: Optional[List[str]] = None,
        accept_datetime: Optional[Union[datetime, str]] = None,
        fields: Optional[List[Union[str, FeatureFlagFields]]] = None,
        **kwargs: Any,
    ) -> AsyncItemPaged["FeatureFlag"]:
        """
        Find the FeatureFlag revision history, optionally filtered by name, label, and tags.

        :keyword name_filter: Filter results based on their feature flag names. '*' can be used as wildcard at the end
            of the filter. Default is `None`.
        :paramtype name_filter: str or None
        :keyword label_filter: Filter results based on their labels. Default is `None`.
        :paramtype label_filter: str or None
        :keyword tags_filter: Filter results based on their tags. Default is `None`.
        :paramtype tags_filter: list[str] or None
        :keyword accept_datetime: Retrieve FeatureFlag revisions that existed at this datetime
        :paramtype accept_datetime: ~datetime.datetime or str or None
        :keyword fields: Specify which fields to include in the results. If not specified, will include all fields.
        :paramtype fields: list[str] or list[~azure.appconfiguration.FeatureFlagFields] or None
        :return: An async iterator of :class:`~azure.appconfiguration.FeatureFlag`
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.appconfiguration.FeatureFlag]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        if isinstance(accept_datetime, datetime):
            accept_datetime = str(accept_datetime)

        # Build kwargs for the underlying call
        impl_kwargs = dict(kwargs)
        if accept_datetime is not None:
            impl_kwargs["accept_datetime"] = accept_datetime

        # Call the generated method and wrap results to convert to SDK FeatureFlag
        def convert_to_sdk(objs):
            return [FeatureFlag._from_generated(obj) for obj in objs]  # pylint:disable=protected-access

        return self._impl.feature_flag_client.get_feature_flag_revisions(  # type: ignore[return-value]
            name=name_filter,
            label=label_filter,
            tags=tags_filter,
            select=fields,
            cls=convert_to_sdk,
            **impl_kwargs,
        )

    @distributed_trace
    def list_labels(
        self,
        *,
        name: Optional[str] = None,
        after: Optional[str] = None,
        accept_datetime: Optional[Union[datetime, str]] = None,
        fields: Optional[List[Union[str, LabelFields]]] = None,
        **kwargs: Any,
    ) -> AsyncItemPaged[ConfigurationSettingLabel]:
        """Gets a list of feature flag labels.

        :keyword name: A filter for the name of the returned labels.  '*' can be used as wildcard
            in the beginning or end of the filter. For more information about supported filters, see
            https://learn.microsoft.com/azure/azure-app-configuration/rest-api-labels?pivots=v23-11#supported-filters.
        :paramtype name: str or None
        :keyword after: Instructs the server to return elements that appear after the element referred to
            by the specified token.
        :paramtype after: str or None
        :keyword accept_datetime: Requests the server to respond with the state of the resource at the
            specified time.
        :paramtype accept_datetime: ~datetime.datetime or str or None
        :keyword fields: Specify which fields to include in the results. If not specified, will include all fields.
            Available fields see :class:`~azure.appconfiguration.LabelFields`.
        :paramtype fields: list[str] or list[~azure.appconfiguration.LabelFields] or None
        :return: An async iterator of labels.
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.appconfiguration.ConfigurationSettingLabel]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        if isinstance(accept_datetime, datetime):
            accept_datetime = str(accept_datetime)
        return self._impl.get_labels(  # type: ignore[return-value]
            name=name,
            after=after,
            accept_datetime=accept_datetime,
            select=fields,
            resource_type="ff",
            cls=lambda objs: [ConfigurationSettingLabel(name=x.name) for x in objs],
            **kwargs,
        )

    async def update_sync_token(self, token: str) -> None:
        """Add a sync token to the internal list of tokens.

        :param str token: The sync token to be added to the internal list of tokens
        """

        await self._sync_token_policy.add_token(token)

    async def close(self) -> None:
        """Close all connections made by the client"""
        await self._impl._client.close()

    async def __aenter__(self) -> "FeatureFlagClient":
        await self._impl.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._impl.__aexit__(*args)
