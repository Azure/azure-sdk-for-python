# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Union, Any, TYPE_CHECKING, List
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller
from ._generated import BatchDocumentTranslationClient as _BatchDocumentTranslationClient
from ._helpers import get_authentication_policy
from ._user_agent import USER_AGENT
from ._poller import DocumentTranslationPoller
if TYPE_CHECKING:
    from azure.core.paging import ItemPaged
    from azure.core.credentials import AzureKeyCredential, TokenCredential
    from ._models import TranslationStatusDetail, DocumentStatusDetail, BatchDocumentInput, FileFormat


class DocumentTranslationClient(object):
    """DocumentTranslationClient

    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Union[AzureKeyCredential, TokenCredential], **Any) -> None
        """

        :param str endpoint:
        :param credential:
        :type credential: Union[AzureKeyCredential, TokenCredential]
        :keyword str api_version:
        """
        self._endpoint = endpoint
        self._credential = credential
        self._api_version = kwargs.pop('api_version', None)

        authentication_policy = get_authentication_policy(credential)
        self._client = _BatchDocumentTranslationClient(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            api_version=self._api_version,
            sdk_moniker=USER_AGENT,
            authentication_policy=authentication_policy,
            polling_interval=30,  # TODO what is appropriate polling interval
            **kwargs
        )

    @distributed_trace
    def begin_translation(self, batch, **kwargs):
        # type: (List[BatchDocumentInput], **Any) -> DocumentTranslationPoller[ItemPaged[DocumentStatusDetail]]
        """

        :param batch:
        :type batch: List[~azure.ai.documenttranslation.BatchDocumentInput]
        :return: An iterable of DocumentStatusDetail
        :rtype: DocumentTranslationPoller[ItemPaged[DocumentStatusDetail]]
        """

        return self._client.document_translation.begin_submit_batch_request(
            inputs=batch,
            polling=True,
            **kwargs
        )

    @distributed_trace
    def get_translation_status(self, batch_id, **kwargs):
        # type: (str, **Any) -> TranslationStatusDetail
        """

        :param batch_id: guid id for batch
        :type batch_id: str
        :rtype: ~azure.ai.documenttranslation.TranslationStatusDetail
        """

        return self._client.document_translation.get_operation_status(batch_id, **kwargs)

    @distributed_trace
    def cancel_translation(self, batch_id, **kwargs):
        # type: (str, **Any) -> None
        """

        :param batch_id: guid id for batch
        :type batch_id: str
        :rtype: None
        """

        self._client.document_translation.cancel_operation(batch_id, **kwargs)

    @distributed_trace
    def list_submitted_translations(self, **kwargs):
        # type: (**Any) -> ItemPaged[TranslationStatusDetail]
        """

        :keyword int results_per_page:
        :keyword int skip:
        :rtype: ~azure.core.polling.ItemPaged[TranslationStatusDetail]
        """
        return self._client.document_translation.get_operations(**kwargs)

    @distributed_trace
    def list_documents_statuses(self, batch_id, **kwargs):
        # type: (str, **Any) -> ItemPaged[DocumentStatusDetail]
        """

        :param batch_id: guid id for batch
        :type batch_id: str
        :keyword int results_per_page:
        :keyword int skip:
        :rtype: ~azure.core.paging.ItemPaged[DocumentStatusDetail]
        """

        return self._client.document_translation.get_operation_documents_status(batch_id, **kwargs)

    @distributed_trace
    def get_document_status(self, batch_id, document_id, **kwargs):
        # type: (str, str, **Any) -> DocumentStatusDetail
        """

        :param batch_id: guid id for batch
        :type batch_id: str
        :param document_id: guid id for document
        :type document_id: str
        :rtype: ~azure.ai.documenttranslation.DocumentStatusDetail
        """
        return self._client.document_translation.get_document_status(batch_id, document_id, **kwargs)

    @distributed_trace
    def get_supported_storage_sources(self, **kwargs):
        # type: (**Any) -> List[str]
        """

        :rtype: List[str]
        """
        return self._client.document_translation.get_document_storage_source(**kwargs)

    @distributed_trace
    def get_supported_glossary_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """

        :rtype: List[FileFormat]
        """

        return self._client.document_translation.get_glossary_formats(**kwargs)

    @distributed_trace
    def get_supported_document_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """

        :rtype: List[FileFormat]
        """

        return self._client.document_translation.get_document_formats(**kwargs)
