# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (
    Any, Dict, Optional, Tuple, Union,
    TYPE_CHECKING
)
from urllib.parse import quote, unquote, urlparse

from ._deserialize import deserialize_permission_key
from ._generated.models import SharePermission
from ._parser import _parse_snapshot
from ._shared.base_client import parse_query

if TYPE_CHECKING:
    from urllib.parse import ParseResult


def _parse_url(account_url: str, share_name: str) -> "ParseResult":
    try:
        if not account_url.lower().startswith('http'):
            account_url = "https://" + account_url
    except AttributeError as exc:
        raise ValueError("Account URL must be a string.") from exc
    parsed_url = urlparse(account_url.rstrip('/'))
    if not share_name:
        raise ValueError("Please specify a share name.")
    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {account_url}")
    return parsed_url


def _format_url(scheme: str, hostname: str, share_name: Union[str, bytes], query_str: str) -> str:
    if isinstance(share_name, str):
        share_name = share_name.encode('UTF-8')
    return f"{scheme}://{hostname}/{quote(share_name)}{query_str}"


def _from_share_url(share_url: str, snapshot: Optional[Union[str, Dict[str, Any]]]) -> Tuple[str, str, Optional[str]]:
    try:
        if not share_url.lower().startswith('http'):
            share_url = "https://" + share_url
    except AttributeError as exc:
        raise ValueError("Share URL must be a string.") from exc
    parsed_url = urlparse(share_url.rstrip('/'))
    if not (parsed_url.path and parsed_url.netloc):
        raise ValueError(f"Invalid URL: {share_url}")

    share_path = parsed_url.path.lstrip('/').split('/')
    account_path = ""
    if len(share_path) > 1:
        account_path = "/" + "/".join(share_path[:-1])
    account_url = f"{parsed_url.scheme}://{parsed_url.netloc.rstrip('/')}{account_path}?{parsed_url.query}"

    share_name = unquote(share_path[-1])
    path_snapshot, _ = parse_query(parsed_url.query)
    path_snapshot = _parse_snapshot(snapshot, path_snapshot)

    if not share_name:
        raise ValueError("Invalid URL. Please provide a URL with a valid share name")

    return account_url, share_name, path_snapshot


def _create_permission_for_share_options(file_permission: str, **kwargs: Any) -> Dict[str, Any]:
    options = {
        'share_permission': SharePermission(permission=file_permission),
        'cls': deserialize_permission_key,
        'timeout': kwargs.pop('timeout', None),
    }
    options.update(kwargs)
    return options
