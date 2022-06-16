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
from .._generated.aio._form_recognizer_client import (
    FormRecognizerClient as FormRecognizer,
)
from .._api_versions import validate_api_version
from .._helpers import (
    _get_deserialize,
    get_authentication_policy,
    POLLING_INTERVAL,
    QuotaExceededPolicy,
)
from .._user_agent import USER_AGENT

if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential
    from azure.core.credentials_async import AsyncTokenCredential


class FormRecognizerClientBaseAsync:
    def __init__(
        self,
        endpoint: str,
        credential: Union["AzureKeyCredential", "AsyncTokenCredential"],
        **kwargs: Any
    ) -> None:

        try:
            endpoint = endpoint.rstrip("/")
        except AttributeError:
            raise ValueError("Parameter 'endpoint' must be a string.")

        self._endpoint = endpoint
        self._credential = credential
        self._api_version = kwargs.pop("api_version", None)
        if not self._api_version:
            raise ValueError("'api_version' must be specified.")
        if self._api_version.startswith("v"):  # v2.0 released with this option
            self._api_version = self._api_version[1:]

        client_kind = kwargs.pop("client_kind")
        validate_api_version(self._api_version, client_kind)

        authentication_policy = get_authentication_policy(credential)
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)

        http_logging_policy = HttpLoggingPolicy(**kwargs)
        http_logging_policy.allowed_header_names.update(
            {
                "Operation-Location",
                "Location",
                "x-envoy-upstream-service-time",
                "apim-request-id",
                "Strict-Transport-Security",
                "x-content-type-options",
                "ms-azure-ai-errorcode",
                "x-ms-cs-error-code",
            }
        )
        http_logging_policy.allowed_query_params.update(
            {
                "includeTextDetails",
                "locale",
                "language",
                "includeKeys",
                "op",
                "pages",
                "readingOrder",
                "stringIndexType",
                "api-version",
            }
        )

        self._client = FormRecognizer(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            api_version=self._api_version,
            sdk_moniker=USER_AGENT,
            authentication_policy=kwargs.get(
                "authentication_policy", authentication_policy
            ),
            http_logging_policy=kwargs.get("http_logging_policy", http_logging_policy),
            per_retry_policies=kwargs.get("per_retry_policies", QuotaExceededPolicy()),
            polling_interval=polling_interval,
            **kwargs
        )
        self._deserialize = _get_deserialize(self._api_version)
        self._generated_models = self._client.models(self._api_version)
