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
    QueueMessagePolicy)
from .policies_async import AsyncStorageResponseHook

if TYPE_CHECKING:
    from azure.core.pipeline import Pipeline
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
        credential_policy = None
        if hasattr(credential, 'get_token'):
            credential_policy = AsyncBearerTokenCredentialPolicy(credential, STORAGE_OAUTH_SCOPE)
        elif isinstance(credential, SharedKeyCredentialPolicy):
            credential_policy = credential
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
            credential_policy,
            ContentDecodePolicy(),
            AsyncRedirectPolicy(**kwargs),
            StorageHosts(hosts=self._hosts, **kwargs), # type: ignore
            config.retry_policy,
            config.logging_policy,
            AsyncStorageResponseHook(**kwargs),
            DistributedTracingPolicy(),
        ]
        return config, AsyncPipeline(config.transport, policies=policies)
