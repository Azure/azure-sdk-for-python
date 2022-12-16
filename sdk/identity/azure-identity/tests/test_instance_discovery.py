# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.identity._internal.msal_credentials import MsalCredential


def test_instance_discovery():
    credential = MsalCredential(
        client_id="CLIENT_ID",
        instance_discovery=False,
    )
    app = credential._get_app()
    assert not app._instance_discovery

    credential = MsalCredential(
        client_id="CLIENT_ID",
        instance_discovery=True,
    )
    app = credential._get_app()
    assert app._instance_discovery
