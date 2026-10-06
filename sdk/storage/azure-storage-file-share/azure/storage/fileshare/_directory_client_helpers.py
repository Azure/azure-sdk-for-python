# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Dict, Optional, Tuple, Union, TYPE_CHECKING
from urllib.parse import quote, unquote, urlparse

from ._shared.base_client import parse_query
from ._file_client_helpers import _format_file_id_url, _parse_file_id

if TYPE_CHECKING:
    from urllib.parse import ParseResult


def _parse_url(account_url: str, share_name: str) -> "ParseResult":
    try:
        if not account_url.lower().startswith("http"):
            account_url = "https://" + account_url
    except AttributeError as exc:
        raise ValueError("Account URL must be a string.") from exc
    parsed_url = urlparse(account_url.rstrip("/"))
    if not share_name:
        raise ValueError("Please specify a share name.")
    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {account_url}")
    return parsed_url


def _format_url(
    scheme: str,
    hostname: str,
    share_name: Union[str, bytes],
    dir_path: str,
    query_str: str,
    file_id: Optional[str] = None,
) -> str:
    if isinstance(share_name, str):
        share_name = share_name.encode("UTF-8")
    if file_id:
        return _format_file_id_url(scheme, hostname, share_name, file_id, query_str)
    directory_path = ""
    if dir_path:
        directory_path = "/" + quote(dir_path, safe="~")
    return f"{scheme}://{hostname}/{quote(share_name)}{directory_path}{query_str}"


def _from_directory_url(
    directory_url: str, snapshot: Optional[Union[str, Dict[str, Any]]] = None
) -> Tuple[str, str, str, Optional[Union[str, Dict[str, Any]]], Optional[str]]:
    try:
        if not directory_url.lower().startswith("http"):
            directory_url = "https://" + directory_url
    except AttributeError as exc:
        raise ValueError("Directory URL must be a string.") from exc
    parsed_url = urlparse(directory_url.rstrip("/"))
    if not parsed_url.path and not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {directory_url}")
    account_url = parsed_url.netloc.rstrip("/") + "?" + parsed_url.query
    path_snapshot, _ = parse_query(parsed_url.query)
    file_id = _parse_file_id(parsed_url)
    share_name, _, path_dir = parsed_url.path.lstrip("/").partition("/")
    share_name = unquote(share_name)
    snapshot = snapshot or path_snapshot

    return account_url, share_name, path_dir, snapshot, file_id
