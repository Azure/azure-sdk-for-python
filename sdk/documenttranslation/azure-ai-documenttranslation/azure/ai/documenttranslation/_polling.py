# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import logging
from typing import TYPE_CHECKING, TypeVar
from azure.core.polling import LROPoller, PollingMethod
if TYPE_CHECKING:
    from typing import Any


PollingReturnType = TypeVar("PollingReturnType")

_LOGGER = logging.getLogger(__name__)


class DocumentTranslationPoller(LROPoller):
    # TODO - this is temporary class. we will generate with the custom poller

    @property
    def batch_id(self):
        return self._polling_method._operation._async_url.split("/batches/")[1]

    @classmethod
    def from_continuation_token(cls, polling_method, continuation_token, **kwargs):
        # type: (PollingMethod[PollingReturnType], str, **Any) -> DocumentTranslationPoller[PollingReturnType]
        """
        :param polling_method:
        :type polling_method: ~azure.core.polling.PollingMethod
        :param str continuation_token:
        :return: DocumentTranslationPoller
        """
        client, initial_response, deserialization_callback = polling_method.from_continuation_token(
            continuation_token, **kwargs
        )
        return cls(client, initial_response, deserialization_callback, polling_method)
