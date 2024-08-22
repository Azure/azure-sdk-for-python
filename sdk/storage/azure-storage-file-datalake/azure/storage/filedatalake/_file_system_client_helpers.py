# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Union
from urllib.parse import quote

def _format_url(scheme: str, hostname: str, file_system_name: Union[str, bytes], query_str: str) -> str:
    if isinstance(file_system_name, str):
        file_system_name = file_system_name.encode('UTF-8')
    return f"{scheme}://{hostname}/{quote(file_system_name)}{query_str}"
