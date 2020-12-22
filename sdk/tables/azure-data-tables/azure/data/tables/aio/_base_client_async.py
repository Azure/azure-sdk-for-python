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
from uuid import uuid4

from azure.core.exceptions import (
    ResourceNotFoundError,
    ClientAuthenticationError
)
from azure.core.pipeline.transport import AsyncHttpTransport, HttpRequest

from .._policies import StorageHeadersPolicy
from .._models import BatchErrorException, BatchTransactionResult

if TYPE_CHECKING:
    from azure.core.pipeline import Pipeline
    from azure.core.configuration import Configuration
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

    async def close(self):
        """ This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        await self._client.close()

    async def _batch_send(
        self, entities, # type: List[TableEntity]
        *reqs: 'HttpRequest',
        **kwargs
    ):
        """Given a series of request, do a Storage batch call.
        """
        # Pop it here, so requests doesn't feel bad about additional kwarg
        raise_on_any_failure = kwargs.pop("raise_on_any_failure", True)
        policies = [StorageHeadersPolicy()]

        changeset = HttpRequest('POST', None)
        changeset.set_multipart_mixed(
            *reqs,
            policies=policies,
            boundary="changeset_{}".format(uuid4())
        )
        request = self._client._client.post(  # pylint: disable=protected-access
            url='https://{}/$batch'.format(self._primary_hostname),
            headers={
                'x-ms-version': self.api_version,
                'DataServiceVersion': '3.0',
                'MaxDataServiceVersion': '3.0;NetFx',
            }
        )
        request.set_multipart_mixed(
            changeset,
            policies=policies,
            enforce_https=False,
            boundary="batch_{}".format(uuid4())
        )

        pipeline_response = await self._client._client._pipeline.run(  # pylint: disable=protected-access
            request, **kwargs
        )
        response = pipeline_response.http_response

        if response.status_code == 403:
            raise ClientAuthenticationError(
                message="There was an error authenticating with the service",
                response=response
            )
        if response.status_code == 404:
            raise ResourceNotFoundError(
                message="The resource could not be found",
                response=response
            )
        if response.status_code != 202:
            raise BatchErrorException(
                message="There is a failure in the batch operation.",
                response=response, parts=None
            )

        parts_iter = response.parts()
        parts = []
        async for p in parts_iter:
            parts.append(p)
        transaction_result = BatchTransactionResult(reqs, parts, entities)
        if raise_on_any_failure:
            if any(p for p in parts if not 200 <= p.status_code < 300):

                if any(p for p in parts if p.status_code == 404):
                    raise ResourceNotFoundError(
                        message="The resource could not be found",
                        response=response
                    )

                raise BatchErrorException(
                    message="There is a failure in the batch operation.",
                    response=response, parts=parts
                )
        return transaction_result


class AsyncTransportWrapper(AsyncHttpTransport):
    """Wrapper class that ensures that an inner client created
    by a `get_client` method does not close the outer transport for the parent
    when used in a context manager.
    """
    def __init__(self, async_transport):
        self._transport = async_transport

    async def send(self, request, **kwargs):
        return await self._transport.send(request, **kwargs)

    async def open(self):
        pass

    async def close(self):
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, *args):  # pylint: disable=arguments-differ
        pass
