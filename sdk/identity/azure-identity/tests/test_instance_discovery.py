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
        use_env_settings=False,
    )
    with pytest.raises(ValueError) as ex:
        credential._get_app()
        assert "disable_instance_discovery" in str(ex)

    credential = MsalCredential(
        client_id="CLIENT_ID",
        authority="unknown.authority",
        disable_instance_discovery=True,
        use_env_settings=False,
    )

    with pytest.raises(ServiceRequestError):
        # Instance discovery is disabled, so the credential should use the authority as given rather than validate it.
        credential._get_app()
