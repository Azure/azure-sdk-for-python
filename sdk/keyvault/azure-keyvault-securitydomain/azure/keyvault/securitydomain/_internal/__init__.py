# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections import namedtuple

from urllib.parse import urlparse

from .async_polling import AsyncSecurityDomainClientDownloadPollingMethod, AsyncSecurityDomainClientUploadPollingMethod
from .challenge_auth_policy import ChallengeAuthPolicy
from .http_challenge import HttpChallenge
from . import http_challenge_cache
from .polling import (
    SecurityDomainClientDownloadPolling,
    SecurityDomainClientDownloadPollingMethod,
    SecurityDomainClientUploadPolling,
    SecurityDomainClientUploadPollingMethod,
)

HttpChallengeCache = http_challenge_cache  # to avoid aliasing pylint error (C4745)

__all__ = [
    "AsyncSecurityDomainClientDownloadPollingMethod",
    "AsyncSecurityDomainClientUploadPollingMethod",
    "ChallengeAuthPolicy",
    "HttpChallenge",
    "HttpChallengeCache",
    "SecurityDomainClientDownloadPolling",
    "SecurityDomainClientDownloadPollingMethod",
    "SecurityDomainClientUploadPolling",
    "SecurityDomainClientUploadPollingMethod",
]

_VaultId = namedtuple("_VaultId", ["vault_url", "collection", "name", "version"])


def parse_vault_id(url: str) -> "_VaultId":
    try:
        parsed_uri = urlparse(url)
    except Exception as exc:  # pylint: disable=broad-except
        raise ValueError(f"'{url}' is not a valid url") from exc
    if not (parsed_uri.scheme and parsed_uri.hostname):
        raise ValueError(f"'{url}' is not a valid url")

    path = list(filter(None, parsed_uri.path.split("/")))

    if len(path) < 2 or len(path) > 3:
        raise ValueError(f"'{url}' is not a valid vault url")

    return _VaultId(
        vault_url=f"{parsed_uri.scheme}://{parsed_uri.hostname}",
        collection=path[0],
        name=path[1],
        version=path[2] if len(path) == 3 else None,
    )


try:
    # pylint:disable=unused-import
    from .async_challenge_auth_policy import AsyncChallengeAuthPolicy

    __all__.extend(["AsyncChallengeAuthPolicy"])
except (SyntaxError, ImportError):
    pass
