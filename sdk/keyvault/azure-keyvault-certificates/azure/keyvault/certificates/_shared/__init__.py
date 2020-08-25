# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
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

class ParsedId():
    """Represents a key vault identifier and its parsed contents.

    :param str original_id: The originally received complete identifier
    :param str vault_url: The vault URL
    :param str collection: The collection name of the id.
    :param str name: The name extracted from the id
    :param str version: The version extracted from the id
    """

    def __init__(
        self,
        original_id,  # type: str
        vault_url,  # type: str
        collection,  # type: str
        name,  # type: str
        version=None  # type: Optional[str]
    ):
        self.original_id = original_id
        self.vault_url = vault_url
        self.collection = collection
        self.name = name
        self.version = version


def parse_key_vault_identifier(original_id):
    # type: (str) -> ParsedId
    try:
        parsed_uri = parse.urlparse(original_id)
    except Exception:  # pylint: disable=broad-except
        raise ValueError("'{}' is not not a valid ID".format(original_id))
    if not (parsed_uri.scheme and parsed_uri.hostname):
        raise ValueError("'{}' is not not a valid ID".format(original_id))

    path = list(filter(None, parsed_uri.path.split("/")))

    if len(path) < 2 or len(path) > 3:
        raise ValueError("'{}' is not not a valid vault ID".format(original_id))

    return ParsedId(
        original_id=original_id,
        vault_url="{}://{}".format(parsed_uri.scheme, parsed_uri.hostname),
        collection=path[0],
        name=path[1],
        version=path[2] if len(path) == 3 else None,
    )


try:
    # pylint:disable=unused-import
    from .async_challenge_auth_policy import AsyncChallengeAuthPolicy
    from .async_client_base import AsyncKeyVaultClientBase

    __all__.extend(["AsyncChallengeAuthPolicy", "AsyncKeyVaultClientBase"])
except (SyntaxError, ImportError):
    pass
