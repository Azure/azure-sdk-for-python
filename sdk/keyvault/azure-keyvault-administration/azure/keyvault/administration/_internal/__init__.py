# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections import namedtuple

try:
    import urllib.parse as parse
except ImportError:
    # pylint:disable=import-error
    import urlparse as parse  # type: ignore

from .challenge_auth_policy import ChallengeAuthPolicy, ChallengeAuthPolicyBase
from .client_base import KeyVaultClientBase
from .http_challenge import HttpChallenge
from . import http_challenge_cache as HttpChallengeCache


__all__ = [
    "ChallengeAuthPolicy",
    "ChallengeAuthPolicyBase",
    "HttpChallenge",
    "HttpChallengeCache",
    "KeyVaultClientBase",
]

_VaultId = namedtuple("VaultId", ["vault_url", "collection", "name", "version"])


def parse_vault_id(url):
    try:
        parsed_uri = parse.urlparse(url)
    except Exception:  # pylint: disable=broad-except
        raise ValueError("'{}' is not not a valid url".format(url))
    if not (parsed_uri.scheme and parsed_uri.hostname):
        raise ValueError("'{}' is not not a valid url".format(url))

    path = list(filter(None, parsed_uri.path.split("/")))

    if len(path) < 2 or len(path) > 3:
        raise ValueError("'{}' is not not a valid vault url".format(url))

    return _VaultId(
        vault_url="{}://{}".format(parsed_uri.scheme, parsed_uri.hostname),
        collection=path[0],
        name=path[1],
        version=path[2] if len(path) == 3 else None,
    )


BackupLocation = namedtuple("BackupLocation", "container_url,folder_name")


def parse_blob_storage_url(blob_storage_url):
    # type: (str) -> BackupLocation
    """Parse the blob container URL and folder name from a backup's blob storage URL.

    For example, https://<account>.blob.core.windows.net/backup/mhsm-account-2020090117323313 parses to
    (container_url="https://<account>.blob.core.windows.net/backup", folder_name="mhsm-account-2020090117323313").
    """

    try:
        folder_name = blob_storage_url.rstrip("/").split("/")[-1]
        container_url = blob_storage_url[: blob_storage_url.rindex(folder_name) - 1]
        return BackupLocation(container_url, folder_name)
    except:  # pylint:disable=broad-except
        raise ValueError(
            '"blob_storage_url" should be the URL of a blob holding a Key Vault backup, for example '
            '"https://<account>.blob.core.windows.net/backup/mhsm-account-2020090117323313"'
        )


try:
    # pylint:disable=unused-import
    from .async_challenge_auth_policy import AsyncChallengeAuthPolicy
    from .async_client_base import AsyncKeyVaultClientBase

    __all__.extend(["AsyncChallengeAuthPolicy", "AsyncKeyVaultClientBase"])
except (SyntaxError, ImportError):
    pass
