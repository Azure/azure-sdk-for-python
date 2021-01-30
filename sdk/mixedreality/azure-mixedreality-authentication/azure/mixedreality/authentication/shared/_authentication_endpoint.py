# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

def construct_endpoint_url(account_domain):
    # type: (str) -> str
    return 'https://sts.' + account_domain
