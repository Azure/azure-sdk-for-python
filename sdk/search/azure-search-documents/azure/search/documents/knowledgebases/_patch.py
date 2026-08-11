# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, IO, Optional, Union

from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.tracing.decorator import distributed_trace

from ._client import KnowledgeBaseRetrievalClient as _KnowledgeBaseRetrievalClient
from . import models
from ._stream import KnowledgeBaseRetrievalEvent, KnowledgeBaseRetrievalEventData, KnowledgeBaseRetrievalStream


class KnowledgeBaseRetrievalClient(_KnowledgeBaseRetrievalClient):
    """KnowledgeBaseRetrievalClient.

    :param endpoint: The endpoint URL of the search service. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a key
     credential type or a token credential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
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

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        audience = kwargs.pop("audience", None)
        if audience:
            kwargs.setdefault("credential_scopes", [audience.rstrip("/") + "/.default"])
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)

    @distributed_trace
    def retrieve_stream(
        self,
        retrieval_request: Union[models.KnowledgeBaseRetrievalRequest, dict[str, Any], IO[bytes]],
        *,
        query_source_authorization: Optional[str] = None,
        query_work_iq_source_authorization: Optional[str] = None,
        **kwargs: Any,
    ) -> KnowledgeBaseRetrievalStream:
        """Retrieve relevant data and stream typed server-sent events.

        :param retrieval_request: The retrieval request to process. Required.
        :type retrieval_request: ~azure.search.documents.knowledgebases.models.KnowledgeBaseRetrievalRequest
         or dict or IO[bytes]
        :keyword query_source_authorization: Token identifying the user for which the query is
         executed. Default value is None.
        :paramtype query_source_authorization: str
        :keyword query_work_iq_source_authorization: User assertion token for a customer-owned Entra
         app registration configured on a Work IQ knowledge source. Default value is None.
        :paramtype query_work_iq_source_authorization: str
        :return: A stream of typed knowledge base retrieval events.
        :rtype: ~azure.search.documents.knowledgebases.KnowledgeBaseRetrievalStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        custom_cls = kwargs.pop("cls", None)
        callback_context: dict[str, Any] = {}

        def _wrap_stream(pipeline_response, raw_stream, response_headers):
            stream = KnowledgeBaseRetrievalStream(
                response=pipeline_response.http_response,
                raw_stream=raw_stream,
            )
            callback_context.update(pipeline_response=pipeline_response, response_headers=response_headers)
            return stream

        stream = super().retrieve_stream(
            retrieval_request,
            query_source_authorization=query_source_authorization,
            query_work_iq_source_authorization=query_work_iq_source_authorization,
            cls=_wrap_stream,
            **kwargs,
        )  # type: ignore[return-value]
        if not custom_cls:
            return stream
        try:
            return custom_cls(callback_context["pipeline_response"], stream, callback_context["response_headers"])
        except Exception:
            stream.close()
            raise


__all__: list[str] = [
    "KnowledgeBaseRetrievalClient",
    "KnowledgeBaseRetrievalEvent",
    "KnowledgeBaseRetrievalEventData",
    "KnowledgeBaseRetrievalStream",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    from . import types

    query_parameter_types = (
        types.AzureBlobKnowledgeSourceParams,
        types.FileKnowledgeSourceParams,
        types.IndexedOneLakeKnowledgeSourceParams,
        types.IndexedSharePointKnowledgeSourceParams,
        types.IndexedSqlKnowledgeSourceParams,
        types.SearchIndexKnowledgeSourceParams,
    )
    for parameter_type in query_parameter_types:
        parameter_type.__annotations__["queryHintOverrides"] = (
            "azure.search.documents.indexes.types.SearchIndexKnowledgeSourceQueryHints"
        )
    types.KnowledgeSourceAzureOpenAIVectorizer.__annotations__["azureOpenAIParameters"] = (
        "azure.search.documents.indexes.types.AzureOpenAIVectorizerParameters"
    )
    types.KnowledgeSourceIngestionParameters.__annotations__["ingestionSchedule"] = Optional[
        "azure.search.documents.indexes.types.IndexingSchedule"
    ]
