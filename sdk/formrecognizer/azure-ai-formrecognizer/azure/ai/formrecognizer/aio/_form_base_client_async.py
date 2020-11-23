# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import (
    Any,
    Union,
    TYPE_CHECKING,
)
from azure.core.pipeline.policies import HttpLoggingPolicy
from .._generated.aio._form_recognizer_client import FormRecognizerClient as FormRecognizer
from .._api_versions import FormRecognizerApiVersion, validate_api_version
from .._helpers import _get_deserialize, get_authentication_policy, POLLING_INTERVAL
from .._user_agent import USER_AGENT
if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential
    from azure.core.credentials_async import AsyncTokenCredential


class FormRecognizerClientBaseAsync(object):

    def __init__(
            self,
            endpoint: str,
            credential: Union["AzureKeyCredential", "AsyncTokenCredential"],
            **kwargs: Any
    ) -> None:
        self._endpoint = endpoint
        self._credential = credential
        self.api_version = kwargs.pop('api_version', FormRecognizerApiVersion.V2_1_PREVIEW)
        validate_api_version(self.api_version)

        authentication_policy = get_authentication_policy(credential)
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)

        http_logging_policy = HttpLoggingPolicy(**kwargs)
        http_logging_policy.allowed_header_names.update(
            {
                "Operation-Location",
                "x-envoy-upstream-service-time",
                "apim-request-id",
                "Strict-Transport-Security",
                "x-content-type-options"
            }
        )
        http_logging_policy.allowed_query_params.update(
            {
                "includeTextDetails",
                "locale",
                "language",
                "includeKeys",
                "op"
            }
        )
        self._client = FormRecognizer(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            api_version=self.api_version,
            sdk_moniker=USER_AGENT,
            authentication_policy=authentication_policy,
            http_logging_policy=http_logging_policy,
            polling_interval=polling_interval,
            **kwargs
        )
        self._deserialize = _get_deserialize(self.api_version)
        self._generated_models = self._client.models(self.api_version)
