# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Regeneration-safe client options preserved from the existing SDK.

Authentication policy selection belongs in the handwritten client constructor,
not in generated configuration files. The loopback-only HTTP opt-in preserves
the existing sync and async credential safeguards.
"""

from typing import Any
from urllib.parse import urlparse

from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline import policies

_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


def _is_local_endpoint(endpoint: str) -> bool:
    try:
        parsed = urlparse(endpoint)
        hostname = parsed.hostname
    except ValueError:
        return False
    return parsed.scheme.casefold() == "http" and hostname is not None and hostname.casefold() in _LOCAL_HOSTS


class _InsecureBearerTokenCredentialPolicy(policies.BearerTokenCredentialPolicy):
    def on_request(self, request: Any) -> None:
        request.context.options["enforce_https"] = False
        super().on_request(request)


class _InsecureAsyncBearerTokenCredentialPolicy(policies.AsyncBearerTokenCredentialPolicy):
    async def on_request(self, request: Any) -> None:
        request.context.options["enforce_https"] = False
        await super().on_request(request)


def prepare_client_options(
    endpoint: str,
    credential: Any,
    *,
    allow_insecure_http: bool,
    asynchronous: bool = False,
    use_legacy_routes: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """Preserve credential policies; use_legacy_routes is a compatibility no-op.

    All SDK operations use /fine_tuning/sessions regardless of this flag.
    Consume it here rather than forwarding it to the pipeline or transport.
    """
    if endpoint is None:
        raise ValueError("Parameter 'endpoint' must not be None.")
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    try:
        is_http = urlparse(endpoint).scheme.casefold() == "http"
    except ValueError:
        is_http = False
    if (
        allow_insecure_http
        and not isinstance(credential, AzureKeyCredential)
        and is_http
        and not _is_local_endpoint(endpoint)
    ):
        raise ValueError(
            "allow_insecure_http=True with an HTTP endpoint is only supported for local endpoints "
            f"(http://localhost, 127.0.0.1, [::1]); got {endpoint!r}."
        )

    if not kwargs.get("authentication_policy"):
        if isinstance(credential, AzureKeyCredential):
            kwargs["authentication_policy"] = policies.AzureKeyCredentialPolicy(credential, name="api-key")
        else:
            insecure = allow_insecure_http and _is_local_endpoint(endpoint)
            if asynchronous:
                policy_type = (
                    _InsecureAsyncBearerTokenCredentialPolicy if insecure else policies.AsyncBearerTokenCredentialPolicy
                )
            else:
                policy_type = _InsecureBearerTokenCredentialPolicy if insecure else policies.BearerTokenCredentialPolicy
            kwargs["authentication_policy"] = policy_type(
                credential, *kwargs.get("credential_scopes", ["https://ai.azure.com/.default"]), **kwargs
            )
    return kwargs
