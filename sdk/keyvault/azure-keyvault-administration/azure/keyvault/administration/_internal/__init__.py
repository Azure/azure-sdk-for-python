# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections import namedtuple

from six.moves.urllib_parse import urlparse

from .challenge_auth_policy import ChallengeAuthPolicy
from .client_base import KeyVaultClientBase
from .http_challenge import HttpChallenge
from . import http_challenge_cache

HttpChallengeCache = http_challenge_cache  # to avoid aliasing pylint error (C4745)

__all__ = [
    "ChallengeAuthPolicy",
    "HttpChallenge",
    "HttpChallengeCache",
    "KeyVaultClientBase",
]

_VaultId = namedtuple("_VaultId", ["vault_url", "collection", "name", "version"])


def parse_vault_id(url):
    try:
        parsed_uri = urlparse(url)
    except Exception:  # pylint: disable=broad-except
        raise ValueError("'{}' is not a valid url".format(url))
    if not (parsed_uri.scheme and parsed_uri.hostname):
        raise ValueError("'{}' is not a valid url".format(url))

    path = list(filter(None, parsed_uri.path.split("/")))

    if len(path) < 2 or len(path) > 3:
        raise ValueError("'{}' is not a valid vault url".format(url))

    return _VaultId(
        vault_url="{}://{}".format(parsed_uri.scheme, parsed_uri.hostname),
        collection=path[0],
        name=path[1],
        version=path[2] if len(path) == 3 else None,
    )


BackupLocation = namedtuple("BackupLocation", ["container_url", "folder_name"])


def parse_folder_url(folder_url):
    # type: (str) -> BackupLocation
    """Parse the blob container URL and folder name from a backup's blob storage URL.

    For example, https://<account>.blob.core.windows.net/backup/mhsm-account-2020090117323313 parses to
    (container_url="https://<account>.blob.core.windows.net/backup", folder_name="mhsm-account-2020090117323313").
    """

    try:
        parsed = urlparse(folder_url)

        # the first segment of the path is the container name
        stripped_path = parsed.path.strip("/")
        container = stripped_path.split("/")[0]

        # the rest of the path is the folder name
        folder_name = stripped_path[len(container) + 1 :]

        # this intentionally discards any SAS token in the URL--methods require the SAS token as a separate parameter
        container_url = "{}://{}/{}".format(parsed.scheme, parsed.netloc, container)

        return BackupLocation(container_url, folder_name)
    except:  # pylint:disable=broad-except
        raise ValueError(
            '"folder_url" should be the URL of a blob holding a Key Vault backup, for example '
            '"https://<account>.blob.core.windows.net/backup/mhsm-account-2020090117323313"'
        )


try:
    # pylint:disable=unused-import
    from .async_challenge_auth_policy import AsyncChallengeAuthPolicy
    from .async_client_base import AsyncKeyVaultClientBase

    __all__.extend(["AsyncChallengeAuthPolicy", "AsyncKeyVaultClientBase"])
except (SyntaxError, ImportError):
    pass
