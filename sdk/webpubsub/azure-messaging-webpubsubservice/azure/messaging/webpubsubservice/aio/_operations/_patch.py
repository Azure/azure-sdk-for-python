# coding=utf-8
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from typing import Optional, Any, Dict, List
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from ._operations import WebPubSubServiceClientOperationsMixinGenerated, JSONType
from ..._operations._patch import get_token_by_key

class WebPubSubServiceClientOperationsMixin(WebPubSubServiceClientOperationsMixinGenerated):
    @distributed_trace_async
    async def get_client_access_token(
        self,
        *,
        user_id: Optional[str] = None,
        roles: Optional[List[str]] = None,
        minutes_to_expire: Optional[int] = 60,
        jwt_headers: Dict[str, Any] = None,
        **kwargs: Any
    ) -> JSONType:
        """Generate token for the client to connect Azure Web PubSub service.

        Generate token for the client to connect Azure Web PubSub service.

        :keyword user_id: User Id.
        :paramtype user_id: str
        :keyword roles: Roles that the connection with the generated token will have.
        :paramtype roles: list[str]
        :keyword minutes_to_expire: The expire time of the generated token.
        :paramtype minutes_to_expire: int
        :keyword dict[str, any] jwt_headers: Any headers you want to pass to jwt encoding.
        :keyword api_version: Api Version. The default value is "2021-10-01". Note that overriding this
         default value may result in unsupported behavior.
        :paramtype api_version: str
        :return: JSON object
        :rtype: JSONType
        :raises: ~azure.core.exceptions.HttpResponseError

        Example:
            .. code-block:: python

                >>> get_client_access_token()
                {
                    'baseUrl': 'wss://contoso.com/api/webpubsub/client/hubs/theHub',
                    'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ...',
                    'url': 'wss://contoso.com/api/webpubsub/client/hubs/theHub?access_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ...'
                }
        """
        endpoint = self._config.endpoint.lower()
        if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
            raise ValueError(
                "Invalid endpoint: '{}' has unknown scheme - expected 'http://' or 'https://'".format(
                    endpoint
                )
            )

        # Ensure endpoint has no trailing slash
        endpoint = endpoint.rstrip("/")

        # Switch from http(s) to ws(s) scheme
        client_endpoint = "ws" + endpoint[4:]
        hub = self._config.hub
        client_url = "{}/client/hubs/{}".format(client_endpoint, hub)
        if isinstance(self._config.credential, AzureKeyCredential):
            token = get_token_by_key(
                endpoint,
                hub,
                self._config.credential.key,
                user_id=user_id,
                roles=roles,
                minutes_to_expire=minutes_to_expire,
                jwt_headers=jwt_headers or {},
                **kwargs
            )
        else:
            access_token = await super().get_client_access_token(
                user_id=user_id,
                roles=roles,
                minutes_to_expire=minutes_to_expire,
                **kwargs
            )
            token = access_token.get('token')

        return {
            "baseUrl": client_url,
            "token": token,
            "url": "{}?access_token={}".format(client_url, token),
        }
    get_client_access_token.metadata = {'url': '/api/hubs/{hub}/:generateToken'}  # type: ignore

# This file is used for handwritten extensions to the generated code. Example:
# https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/customize_code/how-to-patch-sdk-code.md
def patch_sdk():
    pass

__all__ = ["WebPubSubServiceClientOperationsMixin"]
