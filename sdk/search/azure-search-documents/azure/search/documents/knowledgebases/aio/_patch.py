# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, cast, IO, Optional, Union

from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator_async import distributed_trace_async

from ._client import KnowledgeBaseRetrievalClient as _KnowledgeBaseRetrievalClient
from .. import models, types
from .._stream import AsyncKnowledgeBaseRetrievalStream, KnowledgeBaseRetrievalEvent, KnowledgeBaseRetrievalEventData


class KnowledgeBaseRetrievalClient(_KnowledgeBaseRetrievalClient):
    """KnowledgeBaseRetrievalClient.

    :param endpoint: The endpoint URL of the search service. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a key
     credential type or a token credential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :param knowledge_base_name: The name of the knowledge base. Required.
    :type knowledge_base_name: str
    :keyword api_version: The API version to use for this operation. Known values are
        listed on the :class:`~azure.search.documents.ApiVersion` enum. Default value is
        ``ApiVersion.V2026_08_01_PREVIEW``. Note that overriding this default value may
        result in unsupported behavior.
    :paramtype api_version: str or ~azure.search.documents.ApiVersion
    :keyword str audience: Sets the Audience to use for authentication with Microsoft Entra ID. The
     audience is not considered when using a shared key. If audience is not provided, the public cloud
     audience will be assumed.
    """

    def __init__(
        self, endpoint: str, credential: Union[AzureKeyCredential, AsyncTokenCredential], **kwargs: Any
    ) -> None:
        audience = kwargs.pop("audience", None)
        if audience:
            kwargs.setdefault("credential_scopes", [audience.rstrip("/") + "/.default"])
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)

    @distributed_trace_async
    async def retrieve_stream(  # type: ignore[override]
        self,
        retrieval_request: Union[models.KnowledgeBaseRetrievalRequest, dict[str, Any], IO[bytes]],
        *,
        query_source_authorization: Optional[str] = None,
        query_work_iq_source_authorization: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncKnowledgeBaseRetrievalStream:
        """Retrieve relevant data and asynchronously stream typed server-sent events.

        :param retrieval_request: The retrieval request to process. Required.
        :type retrieval_request: ~azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalRequest
         or dict or IO[bytes]
        :keyword query_source_authorization: Token identifying the user for which the query is
         executed. Default value is None.
        :paramtype query_source_authorization: str
        :keyword query_work_iq_source_authorization: User assertion token for a customer-owned Entra
         app registration configured on a Work IQ knowledge source. Default value is None.
        :paramtype query_work_iq_source_authorization: str
        :keyword content_type: Body parameter content type. Default value is "application/json".
        :paramtype content_type: str
        :return: An asynchronous stream of typed knowledge base retrieval events.
        :rtype: ~azure.search.documents.knowledgebases.aio.AsyncKnowledgeBaseRetrievalStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        custom_cls = kwargs.pop("cls", None)
        callback_context: dict[str, Any] = {}

        def _wrap_stream(pipeline_response, raw_stream, response_headers):
            stream = AsyncKnowledgeBaseRetrievalStream(
                response=pipeline_response.http_response,
                raw_stream=raw_stream,
            )
            callback_context.update(pipeline_response=pipeline_response, response_headers=response_headers)
            return stream

        typed_retrieval_request = cast(
            Union[models.KnowledgeBaseRetrievalRequest, types.KnowledgeBaseRetrievalRequest, IO[bytes]],
            retrieval_request,
        )
        stream = cast(
            AsyncKnowledgeBaseRetrievalStream,
            await super().retrieve_stream(
                typed_retrieval_request,
                query_source_authorization=query_source_authorization,
                query_work_iq_source_authorization=query_work_iq_source_authorization,
                content_type=content_type,
                cls=_wrap_stream,
                **kwargs,
            ),
        )
        if not custom_cls:
            return stream
        try:
            return cast(
                AsyncKnowledgeBaseRetrievalStream,
                custom_cls(callback_context["pipeline_response"], stream, callback_context["response_headers"]),
            )
        except Exception:
            await stream.close()
            raise


__all__: list[str] = [
    "AsyncKnowledgeBaseRetrievalStream",
    "KnowledgeBaseRetrievalClient",
    "KnowledgeBaseRetrievalEvent",
    "KnowledgeBaseRetrievalEventData",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
