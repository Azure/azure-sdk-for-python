# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import abc
import time
from typing import TYPE_CHECKING

import isodate
import six
from msal import TokenCache

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError, DecodeError
from azure.core.pipeline.policies import ContentDecodePolicy

from .._internal import _scopes_to_resource
from .._internal.pipeline import build_pipeline

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports
    from typing import Union

    from azure.core.pipeline import PipelineResponse
    from azure.core.pipeline.policies import HTTPPolicy, SansIOHTTPPolicy
    from azure.core.pipeline.transport import HttpRequest

    PolicyType = Union[HTTPPolicy, SansIOHTTPPolicy]


class ManagedIdentityClientBase(ABC):
    # pylint:disable=missing-client-constructor-parameter-credential
    def __init__(self, request_factory, **kwargs):
        # type: (Callable[[str, dict], HttpRequest], Optional[str], Optional[Dict], **Any) -> None
        self._cache = kwargs.pop("_cache", None) or TokenCache()
        self._content_callback = kwargs.pop("_content_callback", None)
        self._pipeline = self._build_pipeline(**kwargs)
        self._request_factory = request_factory

    def _process_response(self, response, request_time, resource):
        # type: (PipelineResponse, int, str) -> AccessToken

        content = response.context.get(ContentDecodePolicy.CONTEXT_NAME)
        if not content:
            try:
                content = ContentDecodePolicy.deserialize_from_text(
                    response.http_response.text(), mime_type="application/json"
                )
            except DecodeError as ex:
                if response.http_response.content_type.startswith("application/json"):
                    message = "Failed to deserialize JSON from response"
                else:
                    message = 'Unexpected content type "{}"'.format(response.http_response.content_type)
                six.raise_from(
                    ClientAuthenticationError(message=message, response=response.http_response),
                    ex,
                )

        if not content:
            raise ClientAuthenticationError(message="No token received.", response=response.http_response)

        if not ("access_token" in content or "token" in content) or not (
            "expires_in" in content or "expires_on" in content or "expiresOn" in content
        ):
            if content and "access_token" in content:
                content["access_token"] = "****"
            if content and "token" in content:
                content["token"] = "****"
            raise ClientAuthenticationError(
                message='Unexpected response "{}"'.format(content),
                response=response.http_response,
            )

        if self._content_callback:
            self._content_callback(content)

        if "expires_in" in content or "expires_on" in content:
            expires_on = int(content.get("expires_on") or int(content["expires_in"]) + request_time)
        else:
            expires_on = int(isodate.parse_datetime(content["expiresOn"]).timestamp())
        content["expires_on"] = expires_on

        access_token = content.get("access_token") or content["token"]
        token = AccessToken(access_token, content["expires_on"])

        # caching is the final step because TokenCache.add mutates its "event"
        self._cache.add(
            event={"response": content, "scope": [content.get("resource") or resource]},
            now=request_time,
        )

        return token

    def get_cached_token(self, *scopes):
        # type: (*str) -> Optional[AccessToken]
        resource = _scopes_to_resource(*scopes)
        tokens = self._cache.find(TokenCache.CredentialType.ACCESS_TOKEN, target=[resource])
        for token in tokens:
            expires_on = int(token["expires_on"])
            if expires_on > time.time():
                return AccessToken(token["secret"], expires_on)
        return None

    @abc.abstractmethod
    def request_token(self, *scopes, **kwargs):
        pass

    @abc.abstractmethod
    def _build_pipeline(self, **kwargs):
        pass


class ManagedIdentityClient(ManagedIdentityClientBase):
    def __enter__(self):
        self._pipeline.__enter__()
        return self

    def __exit__(self, *args):
        self._pipeline.__exit__(*args)

    def close(self):
        # type: () -> None
        self.__exit__()

    def request_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        resource = _scopes_to_resource(*scopes)
        request = self._request_factory(resource)
        request_time = int(time.time())
        response = self._pipeline.run(request, retry_on_methods=[request.method], **kwargs)
        token = self._process_response(response=response, request_time=request_time, resource=resource)
        return token

    def _build_pipeline(self, **kwargs):
        return build_pipeline(**kwargs)
