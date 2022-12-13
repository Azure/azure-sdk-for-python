# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch  # type: ignore

from azure.identity._credentials.application import AzureApplicationCredential
from azure.identity import (
    AzureCliCredential,
    AzureDeveloperCliCredential,
    AzurePowerShellCredential,
    AuthorizationCodeCredential,
    CertificateCredential,
    ClientSecretCredential,
    DeviceCodeCredential,
    EnvironmentCredential,
    InteractiveBrowserCredential,
    OnBehalfOfCredential,
    SharedTokenCacheCredential,
    UsernamePasswordCredential,
    VisualStudioCodeCredential,
)
from azure.identity._constants import EnvironmentVariables

import pytest

from test_certificate_credential import PEM_CERT_PATH
from test_vscode_credential import GET_USER_SETTINGS


class CredentialFixture:
    def __init__(self, cls, default_kwargs=None, ctor_patch_factory=None):
        self.cls = cls
        self._default_kwargs = default_kwargs or {}
        self._ctor_patch_factory = ctor_patch_factory or MagicMock

    def get_credential(self, **kwargs):
        patch = self._ctor_patch_factory()
        with patch:
            return self.cls(**dict(self._default_kwargs, **kwargs))


FIXTURES = (
    CredentialFixture(
        AuthorizationCodeCredential,
        {kwarg: "..." for kwarg in ("tenant_id", "client_id", "authorization_code", "redirect_uri")},
    ),
    CredentialFixture(
        CertificateCredential, {"tenant_id": "...", "client_id": "...", "certificate_path": PEM_CERT_PATH}
    ),
    CredentialFixture(ClientSecretCredential, {kwarg: "..." for kwarg in ("tenant_id", "client_id", "client_secret")}),
    CredentialFixture(DeviceCodeCredential),
    CredentialFixture(
        EnvironmentCredential,
        ctor_patch_factory=lambda: patch.dict(
            EnvironmentCredential.__module__ + ".os.environ",
            {var: "..." for var in EnvironmentVariables.CLIENT_SECRET_VARS},
        ),
    ),
    CredentialFixture(InteractiveBrowserCredential),
    CredentialFixture(
        OnBehalfOfCredential,
        {kwarg: "..." for kwarg in ("tenant_id", "client_id", "client_secret", "user_assertion")},
    ),
    CredentialFixture(UsernamePasswordCredential, {"client_id": "...", "username": "...", "password": "..."}),
    CredentialFixture(VisualStudioCodeCredential, ctor_patch_factory=lambda: patch(GET_USER_SETTINGS, lambda: {})),
)

all_fixtures = pytest.mark.parametrize("fixture", FIXTURES, ids=lambda fixture: fixture.cls.__name__)


@all_fixtures
def test_close(fixture):
    transport = MagicMock()
    credential = fixture.get_credential(transport=transport)
    assert not transport.__enter__.called
    assert not transport.__exit__.called

    credential.close()
    assert not transport.__enter__.called
    assert transport.__exit__.call_count == 1


@all_fixtures
def test_context_manager(fixture):
    transport = MagicMock()
    credential = fixture.get_credential(transport=transport)

    with credential:
        assert transport.__enter__.call_count == 1
        assert not transport.__exit__.called

    assert transport.__enter__.call_count == 1
    assert transport.__exit__.call_count == 1


@all_fixtures
def test_exit_args(fixture):
    transport = MagicMock()
    credential = fixture.get_credential(transport=transport)
    expected_args = ("type", "value", "traceback")
    credential.__exit__(*expected_args)
    transport.__exit__.assert_called_once_with(*expected_args)


@pytest.mark.parametrize(
    "cls",
    (
        AzureCliCredential,
        AzureDeveloperCliCredential,
        AzureApplicationCredential,
        AzurePowerShellCredential,
        EnvironmentCredential,
        SharedTokenCacheCredential,
    ),
)
def test_no_op(cls):
    """Credentials that don't allow custom transports, or require initialization or optional config, should have no-op methods"""
    with patch.dict("os.environ", {}, clear=True):
        credential = cls()

    with credential:
        pass
    credential.close()
