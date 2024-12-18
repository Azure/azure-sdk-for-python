# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (
    Any, Dict, List, Optional, Tuple, Union,
    TYPE_CHECKING
)
from urllib.parse import quote, unquote, urlparse

from ._serialize import get_access_conditions, get_source_conditions
from ._shared.base_client import parse_query
from ._shared.response_handlers import return_response_headers

if TYPE_CHECKING:
    from urllib.parse import ParseResult


def _parse_url(account_url: str, share_name: str, file_path: str) -> "ParseResult":
    try:
        if not account_url.lower().startswith('http'):
            account_url = "https://" + account_url
    except AttributeError as exc:
        raise ValueError("Account URL must be a string.") from exc
    parsed_url = urlparse(account_url.rstrip('/'))
    if not (share_name and file_path):
        raise ValueError("Please specify a share name and file name.")
    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {account_url}")
    return parsed_url


def _from_file_url(
    file_url: str,
    snapshot: Optional[Union[str, Dict[str, Any]]] = None
) -> Tuple[str, str, str, Optional[Union[str, Dict[str, Any]]]]:
    try:
        if not file_url.lower().startswith('http'):
            file_url = "https://" + file_url
    except AttributeError as exc:
        raise ValueError("File URL must be a string.") from exc
    parsed_url = urlparse(file_url.rstrip('/'))

    if not (parsed_url.netloc and parsed_url.path):
        raise ValueError(f"Invalid URL: {file_url}")
    account_url = parsed_url.netloc.rstrip('/') + "?" + parsed_url.query

    path_share, _, path_file = parsed_url.path.lstrip('/').partition('/')
    path_snapshot, _ = parse_query(parsed_url.query)
    snapshot = snapshot or path_snapshot
    share_name = unquote(path_share)
    file_path = '/'.join([unquote(p) for p in path_file.split('/')])

    return account_url, share_name, file_path, snapshot


def _format_url(
    scheme: str,
    hostname: str,
    share_name: Union[str, bytes],
    file_path: List[str],
    query_str: str
) -> str:
    if isinstance(share_name, str):
        share_name = share_name.encode('UTF-8')
    return (f"{scheme}://{hostname}/{quote(share_name)}"
            f"/{'/'.join([quote(p, safe='~') for p in file_path])}{query_str}")


def _upload_range_from_url_options(
    source_url: str,
    offset: int,
    length: int,
    source_offset: int,
    **kwargs: Any
) -> Dict[str, Any]:
    if offset is None:
        raise ValueError("offset must be provided.")
    if length is None:
        raise ValueError("length must be provided.")
    if source_offset is None:
        raise ValueError("source_offset must be provided.")

    # Format range
    end_range = offset + length - 1
    destination_range = f'bytes={offset}-{end_range}'
    source_range = f'bytes={source_offset}-{source_offset + length - 1}'
    source_authorization = kwargs.pop('source_authorization', None)
    source_mod_conditions = get_source_conditions(kwargs)
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    file_last_write_mode = kwargs.pop('file_last_write_mode', None)

    options = {
        'copy_source_authorization': source_authorization,
        'copy_source': source_url,
        'content_length': 0,
        'source_range': source_range,
        'range': destination_range,
        'file_last_written_mode': file_last_write_mode,
        'source_modified_access_conditions': source_mod_conditions,
        'lease_access_conditions': access_conditions,
        'timeout': kwargs.pop('timeout', None),
        'cls': return_response_headers
    }

    options.update(kwargs)
    return options


def _get_ranges_options(
    snapshot: Optional[str],
    offset: Optional[int] = None,
    length: Optional[int] = None,
    previous_sharesnapshot: Optional[Union[str, Dict[str, Any]]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    access_conditions = get_access_conditions(kwargs.pop('lease', None))

    content_range = None
    if offset:
        if length:
            end_range = offset + length - 1  # Reformat to an inclusive range index
            content_range = f'bytes={offset}-{end_range}'
        else:
            content_range = f'bytes={offset}-'

    options = {
        'sharesnapshot': snapshot,
        'lease_access_conditions': access_conditions,
        'timeout': kwargs.pop('timeout', None),
        'range': content_range
    }

    if previous_sharesnapshot:
        if hasattr(previous_sharesnapshot, 'snapshot'):
            options['prevsharesnapshot'] = previous_sharesnapshot.snapshot
        elif isinstance(previous_sharesnapshot, Dict):
            options['prevsharesnapshot'] = previous_sharesnapshot['snapshot']
        else:
            options['prevsharesnapshot'] = previous_sharesnapshot

    options.update(kwargs)
    return options
