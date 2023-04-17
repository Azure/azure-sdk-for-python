# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from .._serialization import Serializer

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    map_error,
)
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpResponse
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from .. import models as _models
from ._operations import AuthenticationOperations as AuthenticationOperationsGenerated

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False
# fmt: off




def build_exchange_aad_access_token_for_acr_refresh_token_request(
    **kwargs  # type: Any
):
    # type: (...) -> HttpRequest
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    api_version = kwargs.pop('api_version', _params.pop('api-version', "2021-07-01"))  # type: str
    content_type = kwargs.pop('content_type', _headers.pop('Content-Type', None))  # type: Optional[str]
    accept = _headers.pop('Accept', "application/json")

    # Construct URL
    _url = kwargs.pop("template_url", "/oauth2/exchange")

    # Construct parameters
    _params['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

    # Construct headers
    if content_type is not None:
        _headers['Content-Type'] = _SERIALIZER.header("content_type", content_type, 'str')
    _headers['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="POST",
        url=_url,
        params=_params,
        headers=_headers,
        **kwargs
    )


def build_exchange_acr_refresh_token_for_acr_access_token_request(
    **kwargs  # type: Any
):
    # type: (...) -> HttpRequest
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    api_version = kwargs.pop('api_version', _params.pop('api-version', "2021-07-01"))  # type: str
    content_type = kwargs.pop('content_type', _headers.pop('Content-Type', None))  # type: Optional[str]
    accept = _headers.pop('Accept', "application/json")

    # Construct URL
    _url = kwargs.pop("template_url", "/oauth2/token")

    # Construct parameters
    _params['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

    # Construct headers
    if content_type is not None:
        _headers['Content-Type'] = _SERIALIZER.header("content_type", content_type, 'str')
    _headers['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="POST",
        url=_url,
        params=_params,
        headers=_headers,
        **kwargs
    )

# fmt: on


class AuthenticationOperations(AuthenticationOperationsGenerated):
    @distributed_trace
    def exchange_aad_access_token_for_acr_refresh_token(
        self,
        grant_type,  # type: Union[str, "_models.PostContentSchemaGrantType"]
        service,  # type: str
        tenant=None,  # type: Optional[str]
        refresh_token=None,  # type: Optional[str]
        access_token=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> _models.AcrRefreshToken
        """Exchange AAD tokens for an ACR refresh Token.
        :param grant_type: Can take a value of access_token_refresh_token, or access_token, or
         refresh_token.
        :type grant_type: str or ~container_registry.models.PostContentSchemaGrantType
        :param service: Indicates the name of your Azure container registry.
        :type service: str
        :param tenant: AAD tenant associated to the AAD credentials. Default value is None.
        :type tenant: str
        :param refresh_token: AAD refresh token, mandatory when grant_type is
         access_token_refresh_token or refresh_token. Default value is None.
        :type refresh_token: str
        :param access_token: AAD access token, mandatory when grant_type is access_token_refresh_token
         or access_token. Default value is None.
        :type access_token: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: AcrRefreshToken, or the result of cls(response)
        :rtype: ~container_registry.models.AcrRefreshToken
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

        api_version = kwargs.pop("api_version", _params.pop("api-version", "2021-07-01"))  # type: str
        content_type = kwargs.pop(
            "content_type", _headers.pop("Content-Type", "application/x-www-form-urlencoded")
        )  # type: Optional[str]
        cls = kwargs.pop("cls", None)  # type: ClsType[_models.AcrRefreshToken]

        # Construct form data
        _data = {
            "grant_type": grant_type,
            "service": service,
            "tenant": tenant,
            "refresh_token": refresh_token,
            "access_token": access_token,
        }

        request = build_exchange_aad_access_token_for_acr_refresh_token_request(
            api_version=api_version,
            content_type=content_type,
            data=_data,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "url": self._serialize.url("self._config.url", self._config.url, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore

        pipeline_response = self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.AcrErrors, pipeline_response)
            raise HttpResponseError(response=response, model=error)
        deserialized = self._deserialize("AcrRefreshToken", pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})
        return deserialized

    @distributed_trace
    def exchange_acr_refresh_token_for_acr_access_token(
        self,
        service,  # type: str
        scope,  # type: str
        refresh_token,  # type: str
        grant_type="refresh_token",  # type: Union[str, "_models.TokenGrantType"]
        **kwargs  # type: Any
    ):
        # type: (...) -> _models.AcrAccessToken
        """Exchange ACR Refresh token for an ACR Access Token.
        :param service: Indicates the name of your Azure container registry.
        :type service: str
        :param scope: Which is expected to be a valid scope, and can be specified more than once for
         multiple scope requests. You obtained this from the Www-Authenticate response header from the
         challenge.
        :type scope: str
        :param refresh_token: Must be a valid ACR refresh token.
        :type refresh_token: str
        :param grant_type: Grant type is expected to be refresh_token. Default value is
         "refresh_token".
        :type grant_type: str or ~container_registry.models.TokenGrantType
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: AcrAccessToken, or the result of cls(response)
        :rtype: ~container_registry.models.AcrAccessToken
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

        api_version = kwargs.pop("api_version", _params.pop("api-version", "2021-07-01"))  # type: str
        content_type = kwargs.pop(
            "content_type", _headers.pop("Content-Type", "application/x-www-form-urlencoded")
        )  # type: Optional[str]
        cls = kwargs.pop("cls", None)  # type: ClsType[_models.AcrAccessToken]

        # Construct form data
        _data = {
            "service": service,
            "scope": scope,
            "refresh_token": refresh_token,
            "grant_type": grant_type,
        }

        request = build_exchange_acr_refresh_token_for_acr_access_token_request(
            api_version=api_version,
            content_type=content_type,
            data=_data,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "url": self._serialize.url("self._config.url", self._config.url, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore

        pipeline_response = self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.AcrErrors, pipeline_response)
            raise HttpResponseError(response=response, model=error)
        deserialized = self._deserialize("AcrAccessToken", pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})
        return deserialized


__all__ = [
    "AuthenticationOperations"
]  # type: List[str]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
