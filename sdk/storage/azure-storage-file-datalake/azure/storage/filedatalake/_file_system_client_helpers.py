# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Union
from urllib.parse import quote, unquote


def _format_url(scheme: str, hostname: str, file_system_name: Union[str, bytes], query_str: str) -> str:
    if isinstance(file_system_name, str):
        file_system_name = file_system_name.encode('UTF-8')
    return f"{scheme}://{hostname}/{quote(file_system_name)}{query_str}"


def _undelete_path_options(deleted_path_name, deletion_id, url):
    quoted_path = quote(unquote(deleted_path_name.strip('/')))
    url_and_token = url.replace('.dfs.', '.blob.').split('?')
    try:
        url = url_and_token[0] + '/' + quoted_path + url_and_token[1]
    except IndexError:
        url = url_and_token[0] + '/' + quoted_path
    undelete_source = quoted_path + f'?deletionid={deletion_id}' if deletion_id else None
    return quoted_path, url, undelete_source
