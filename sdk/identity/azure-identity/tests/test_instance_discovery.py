# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.identity._internal.msal_credentials import MsalCredential
from azure.core.exceptions import ServiceRequestError


def test_instance_discovery():
    credential = MsalCredential(
        client_id="CLIENT_ID",
        disable_instance_discovery=True,
    )
    app = credential._get_app()
    assert not app._instance_discovery

    credential = MsalCredential(
        client_id="CLIENT_ID",
        disable_instance_discovery=False,
    )
    app = credential._get_app()
    assert app._instance_discovery


def test_unknown_authority():
    credential = MsalCredential(
        client_id="CLIENT_ID",
        authority="unknown.authority",
    )
    with pytest.raises(ValueError) as ex:
        credential._get_app()
        assert "disable_instance_discovery" in str(ex)

    credential = MsalCredential(
        client_id="CLIENT_ID",
        authority="unknown.authority",
        disable_instance_discovery=True,
    )

    with pytest.raises(ServiceRequestError):
        # Instance discovery is disabled, so the credential should not attempt to validate the authority, and instead
        # attempt to use the authority as given. This is fail since unknown.authority is not resolvable.
        credential._get_app()
