# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

DEFAULT_OAUTH_SCOPE = "/.default"
STORAGE_OAUTH_SCOPE = "https://storage.azure.com/.default"

def _build_audience_url(account_name: str) -> str:
    """Creates the fully qualified audience URL scoped to the Storage account name provided.

    :param str account_name: The account name of the Storage account to scope the audience to.
    :returns: The fully qualified audience URL scoped to the Storage account name provided.
    :rtype: str
    """

    return f'https://{account_name}.queue.core.windows.net/{DEFAULT_OAUTH_SCOPE}'
