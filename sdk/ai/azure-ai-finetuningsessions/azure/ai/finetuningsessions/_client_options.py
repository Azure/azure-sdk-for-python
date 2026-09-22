# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Preserved client defaults expressed through generated constructor options.

Both public client subclasses use this helper instead of editing generated
configuration or replacing a caller-supplied policy list or pipeline.
"""

from typing import Any
from urllib.parse import urlparse

from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline import policies
from azure.core.pipeline.policies import AzureKeyCredentialPolicy

from ._version import VERSION


#: Hostnames that count as "local dev" for the purpose of allowing plain http://.
_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


def _is_local_endpoint(endpoint: str) -> bool:
    """Return True when ``endpoint`` is an HTTP URL for a loopback host.

    Used to bound ``allow_insecure_http``: skipping HTTPS enforcement is only
    ever appropriate against a local dev server, never against a real regional
    ``loom_api`` reached on the direct (non-APIM) path.
    """
    try:
        parsed = urlparse(endpoint)
    except ValueError:
        return False
    hostname = parsed.hostname
    return parsed.scheme.casefold() == "http" and hostname is not None and hostname.casefold() in _LOCAL_HOSTS


def _is_http_endpoint(endpoint: str) -> bool:
    """Return True when ``endpoint`` explicitly uses plaintext HTTP."""
    try:
        return urlparse(endpoint).scheme.casefold() == "http"
    except ValueError:
        return False


class _InsecureBearerTokenCredentialPolicy(policies.BearerTokenCredentialPolicy):
    """BearerTokenCredentialPolicy that skips HTTPS enforcement (for local/http:// dev)."""

    def on_request(self, request: Any) -> None:
        request.context.options["enforce_https"] = False
        super().on_request(request)


class _InsecureAsyncBearerTokenCredentialPolicy(policies.AsyncBearerTokenCredentialPolicy):
    """Async bearer policy that permits loopback HTTP for local development."""

    async def on_request(self, request: Any) -> None:
        request.context.options["enforce_https"] = False
        await super().on_request(request)


def _prepare_client_options(
    endpoint: str,
    credential: Any,
    options: dict[str, Any],
    *,
    allow_insecure_http: bool = False,
    asynchronous: bool = False,
) -> dict[str, Any]:
    """Translate the frozen configuration behavior into supported policy kwargs."""
    if endpoint is None:
        raise ValueError("Parameter 'endpoint' must not be None.")
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if (
        allow_insecure_http
        and not isinstance(credential, AzureKeyCredential)
        and _is_http_endpoint(endpoint)
        and not _is_local_endpoint(endpoint)
    ):
        raise ValueError(
            "allow_insecure_http=True with an HTTP endpoint is only supported "
            "for local endpoints "
            f"(http://localhost, 127.0.0.1, [::1]); got {endpoint!r}."
        )

    kwargs = dict(options)
    kwargs.setdefault("sdk_moniker", "finetuning-sessions/{}".format(VERSION))
    kwargs.setdefault("credential_scopes", ["https://ai.azure.com/.default"])
    if credential and not kwargs.get("authentication_policy"):
        if isinstance(credential, AzureKeyCredential):
            kwargs["authentication_policy"] = AzureKeyCredentialPolicy(credential, name="api-key")
        else:
            policy_cls: Any
            if asynchronous:
                policy_cls = (
                    _InsecureAsyncBearerTokenCredentialPolicy
                    if allow_insecure_http and _is_local_endpoint(endpoint)
                    else policies.AsyncBearerTokenCredentialPolicy
                )
            else:
                policy_cls = (
                    _InsecureBearerTokenCredentialPolicy
                    if allow_insecure_http and _is_local_endpoint(endpoint)
                    else policies.BearerTokenCredentialPolicy
                )
            policy_options = dict(kwargs)
            credential_scopes = policy_options.pop("credential_scopes")
            if not asynchronous:
                policy_options.pop("api_version", None)
            kwargs["authentication_policy"] = policy_cls(credential, *credential_scopes, **policy_options)
    return kwargs


def _patch_configuration(module: Any, *, asynchronous: bool = False) -> None:
    """Keep the preview's private configuration imports regeneration-safe.

    Public clients use constructor options. This hook also preserves existing
    direct configuration callers, including the unmodified upstream tests.
    """
    generated = module.FineTuningSessionClientConfiguration
    if getattr(generated, "_preview_configuration", False):
        return

    class FineTuningSessionClientConfiguration(generated):  # type: ignore[misc,valid-type]
        _preview_configuration = True

        def __init__(self, endpoint: str, credential: Any, *, allow_insecure_http: bool = False, **kwargs: Any) -> None:
            options = _prepare_client_options(
                endpoint,
                credential,
                kwargs,
                allow_insecure_http=allow_insecure_http,
                asynchronous=asynchronous,
            )
            super().__init__(endpoint=endpoint, credential=credential, **options)
            self.allow_insecure_http = allow_insecure_http
            if not asynchronous:
                self.api_version = kwargs.get("api_version", "v1")

    module.FineTuningSessionClientConfiguration = FineTuningSessionClientConfiguration
    module._is_local_endpoint = _is_local_endpoint
    module._is_http_endpoint = _is_http_endpoint
    module._LOCAL_HOSTS = _LOCAL_HOSTS
    if asynchronous:
        module._InsecureAsyncBearerTokenCredentialPolicy = _InsecureAsyncBearerTokenCredentialPolicy
    else:
        module._InsecureBearerTokenCredentialPolicy = _InsecureBearerTokenCredentialPolicy
