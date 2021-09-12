# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import time
try:
    from unittest import mock
except ImportError:
    import mock

import pytest

from azure.common.credentials import _CliCredentials
import azure.common.credentials


class MockCliCredentials:
    def _token_retriever(self, resource):
        return "NOTUSED", "TOKEN-" + resource, {'expiresIn': 42}

    def signed_session(self, session=None):
        return session


class MockCliProfile:
    def __init__(self):
        self.received_resource = None

    def get_login_credentials(self, resource):
        self.received_resource = resource
        return MockCliCredentials(), "NOTUSED", "NOTUSED"


def test_cli_credentials_mgmt():

    cli_profile = MockCliProfile()

    cred = _CliCredentials(cli_profile, "http://resource.id")

    # Mgmt scenario
    session = cred.signed_session("session")
    assert cli_profile.received_resource == "http://resource.id"
    assert session == "session"

    # Trying to mock azure-core not here
    with mock.patch('azure.common.credentials._AccessToken', None):
        # Should not crash
        cred.signed_session("session")


def test_cli_credentials_accesstoken():

    cli_profile = MockCliProfile()

    cred = _CliCredentials(cli_profile, "http://resource.id")

    # Track2 scenario
    access_token = cred.get_token("http://resource.id/.default")
    assert cli_profile.received_resource == "http://resource.id"
    assert access_token.token == "TOKEN-" + cli_profile.received_resource
    assert access_token.expires_on <= int(time.time() + 42)

    access_token = cred.get_token("http://resource.newid")
    assert cli_profile.received_resource == "http://resource.newid"

    # Trying to mock azure-core not here
    with mock.patch('azure.common.credentials._AccessToken', None):
        with pytest.raises(ImportError):
            cred.get_token("http://resource.yetid")