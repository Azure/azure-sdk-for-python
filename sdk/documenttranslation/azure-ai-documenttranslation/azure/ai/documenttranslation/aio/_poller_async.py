# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


import base64
import logging
import threading
import uuid
try:
    from urlparse import urlparse # type: ignore # pylint: disable=unused-import
except ImportError:
    from urllib.parse import urlparse

from typing import TYPE_CHECKING, TypeVar, Generic
from azure.core.exceptions import AzureError
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.common import with_current_context
from azure.core.polling import AsyncLROPoller, PollingMethod
if TYPE_CHECKING:
    from typing import Any, Callable, Union, List, Optional, Tuple
    from azure.core.paging import ItemPaged
    from .._models import TranslationStatusDetail, DocumentStatusDetail


PollingReturnType = TypeVar("PollingReturnType")

_LOGGER = logging.getLogger(__name__)


class AsyncDocumentTranslationPoller(AsyncLROPoller):

    @property
    def batch_id(self):
        return self.polling_method._operation._async_url.split("/batches/")[1]

    async def details(self, **kwargs):
        # type: (**Any) -> TranslationStatusDetail
        """
        :return: ~azure.ai.documenttranslation.TranslationStatusDetail
        """
        return await getattr(self._polling_method, '_client').get_operation_status(self.batch_id, **kwargs)

    @classmethod
    def from_continuation_token(cls, polling_method, continuation_token, **kwargs):
        # type: (PollingMethod[PollingReturnType], str, **Any) -> AsyncDocumentTranslationPoller[PollingReturnType]
        """

        :param PollingMethod polling_method:
        :param str continuation_token: batch ID
        :return: AsyncDocumentTranslationPoller
        """
        client, initial_response, deserialization_callback = polling_method.from_continuation_token(
            continuation_token, **kwargs
        )
        return cls(client, initial_response, deserialization_callback, polling_method)
