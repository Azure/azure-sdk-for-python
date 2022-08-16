# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.identity._internal.msal_credentials import MsalCredential


def test_set_known_authority_host():
    known_authority_hosts = ["private.cloud"]
    credential = MsalCredential(
        client_id="CLIENT_ID",
        known_authority_hosts=known_authority_hosts,
    )
    app = credential._get_app()
    expected = frozenset(known_authority_hosts)
    assert app._known_authority_hosts == expected
