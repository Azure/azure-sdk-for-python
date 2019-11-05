# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List, Type, Tuple,
    TYPE_CHECKING
)
import logging

from azure.core.pipeline import AsyncPipeline
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies.distributed_tracing import DistributedTracingPolicy
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    AsyncBearerTokenCredentialPolicy,
    AsyncRedirectPolicy)

from .constants import STORAGE_OAUTH_SCOPE, DEFAULT_SOCKET_TIMEOUT
from .authentication import SharedKeyCredentialPolicy
from .base_client import create_configuration
from .policies import (
    StorageContentValidation,
    StorageRequestHook,
    StorageHosts,
    StorageHeadersPolicy,
    QueueMessagePolicy)
from .policies_async import AsyncStorageResponseHook

from .._generated.models import StorageErrorException
from .response_handlers import process_storage_error

if TYPE_CHECKING:
    from azure.core.pipeline import Pipeline
    from azure.core.pipeline.transport import HttpRequest
    from azure.core import Configuration
_LOGGER = logging.getLogger(__name__)


class AsyncStorageAccountHostsMixin(object):

    def __enter__(self):
        raise TypeError("Async client only supports 'async with'.")

    def __exit__(self, *args):
        pass

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self._client.__aexit__(*args)

    def _create_pipeline(self, credential, **kwargs):
        # type: (Any, **Any) -> Tuple[Configuration, Pipeline]
        self._credential_policy = None
        if hasattr(credential, 'get_token'):
            self._credential_policy = AsyncBearerTokenCredentialPolicy(credential, STORAGE_OAUTH_SCOPE)
        elif isinstance(credential, SharedKeyCredentialPolicy):
            self._credential_policy = credential
        elif credential is not None:
            raise TypeError("Unsupported credential: {}".format(credential))
        config = kwargs.get('_configuration') or create_configuration(**kwargs)
        if kwargs.get('_pipeline'):
            return config, kwargs['_pipeline']
        config.transport = kwargs.get('transport')  # type: ignore
        if 'connection_timeout' not in kwargs:
            kwargs['connection_timeout'] = DEFAULT_SOCKET_TIMEOUT[0] # type: ignore
        if not config.transport:
            try:
                from azure.core.pipeline.transport import AioHttpTransport
            except ImportError:
                raise ImportError("Unable to create async transport. Please check aiohttp is installed.")
            config.transport = AioHttpTransport(**kwargs)
        policies = [
            QueueMessagePolicy(),
            config.headers_policy,
            config.user_agent_policy,
            StorageContentValidation(),
            StorageRequestHook(**kwargs),
            self._credential_policy,
            ContentDecodePolicy(),
            AsyncRedirectPolicy(**kwargs),
            StorageHosts(hosts=self._hosts, **kwargs), # type: ignore
            config.retry_policy,
            config.logging_policy,
            AsyncStorageResponseHook(**kwargs),
            DistributedTracingPolicy(),
        ]
        return config, AsyncPipeline(config.transport, policies=policies)

    async def _batch_send(
        self, *reqs: 'HttpRequest',
        **kwargs
    ):
        """Given a series of request, do a Storage batch call.
        """
        request = self._client._client.post(  # pylint: disable=protected-access
            url='https://{}/?comp=batch'.format(self.primary_hostname),
            headers={
                'x-ms-version': self._client._config.version  # pylint: disable=protected-access
            }
        )

        request.set_multipart_mixed(
            *reqs,
            policies=[
                StorageHeadersPolicy(),
                self._credential_policy
            ]
        )

        pipeline_response = await self._pipeline.run(
            request, **kwargs
        )
        response = pipeline_response.http_response

        try:
            if response.status_code not in [202]:
                raise HttpResponseError(response=response)
            return response.parts()  # Return an AsyncIterator
        except StorageErrorException as error:
            process_storage_error(error)
