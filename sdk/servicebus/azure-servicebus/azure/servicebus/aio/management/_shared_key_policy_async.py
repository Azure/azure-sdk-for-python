# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import six
from azure.core.pipeline.policies import SansIOHTTPPolicy
from ...aio._base_handler_async import ServiceBusSharedKeyCredential


class AsyncServiceBusSharedKeyCredentialPolicy(SansIOHTTPPolicy):
    def __init__(
        self, endpoint: str, credential: ServiceBusSharedKeyCredential, name: str
    ) -> None:
        super(AsyncServiceBusSharedKeyCredentialPolicy, self).__init__()
        self._credential = credential
        self._endpoint = endpoint
        if not name:
            raise ValueError("name can not be None or empty")
        if not isinstance(name, six.string_types):
            raise TypeError("name must be a string.")
        self._name = name
        self._token_expiry_on = 0
        self._token = None

    async def _update_token(self):  # pylint: disable=invalid-overridden-method
        if (
            self._token_expiry_on + 60 <= time.time()
        ):  # Update token if it's expiring in 60 seconds
            access_token, self._token_expiry_on = await self._credential.get_token(
                self._endpoint
            )
            self._token = access_token.decode("utf-8")

    async def on_request(self, request):  # pylint: disable=invalid-overridden-method
        await self._update_token()
        request.http_request.headers[self._name] = self._token
