# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import itertools
import os

from azure.identity import CredentialUnavailableError, EnvironmentCredential
from azure.identity._constants import EnvironmentVariables
import pytest

from helpers import mock


ALL_VARIABLES = {
    _
    for _ in EnvironmentVariables.CLIENT_SECRET_VARS
    + EnvironmentVariables.CERT_VARS
    + EnvironmentVariables.USERNAME_PASSWORD_VARS
}


def test_error_raise():
    """get_token should raise CredentialUnavailableError for incomplete configuration."""

    with mock.patch.dict(os.environ, {}, clear=True):
        with pytest.raises(CredentialUnavailableError) as ex:
            EnvironmentCredential().get_token("scope")

    for a, b in itertools.combinations(ALL_VARIABLES, 2):  # all credentials require at least 3 variables set
        with mock.patch.dict(os.environ, {a: "a", b: "b"}, clear=True):
            with pytest.raises(CredentialUnavailableError) as ex:
                EnvironmentCredential().get_token("scope")
