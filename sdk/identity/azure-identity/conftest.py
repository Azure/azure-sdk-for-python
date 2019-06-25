# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
import sys

import pytest
from azure.identity.constants import EnvironmentVariables

# IMDS tests must be run explicitly
collect_ignore_glob = ["*imds*"]  # pylint:disable=invalid-name

# Ignore collection of async tests on unsupported platforms
if sys.version_info < (3, 5):
    collect_ignore_glob.append("*_async.py")


@pytest.fixture()
def live_identity_settings():  # pylint:disable=inconsistent-return-statements
    """Fixture for live Identity tests. Skips them when environment configuration is incomplete."""

    missing_variables = [
        v
        for v in (
            EnvironmentVariables.AZURE_CLIENT_ID,
            EnvironmentVariables.AZURE_CLIENT_SECRET,
            EnvironmentVariables.AZURE_TENANT_ID,
        )
        if not os.environ.get(v)
    ]
    if any(missing_variables):
        pytest.skip("Environment has no value for {}".format(missing_variables))
    else:
        return {
            "client_id": os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
            "client_secret": os.environ[EnvironmentVariables.AZURE_CLIENT_SECRET],
            "tenant_id": os.environ[EnvironmentVariables.AZURE_TENANT_ID],
        }


@pytest.fixture()
def live_certificate_settings(live_identity_settings):  # pylint:disable=inconsistent-return-statements,redefined-outer-name
    """Fixture for live tests needing a certificate.
    Skips them when environment configuration is incomplete.
    """

    pem_content = os.environ.get("PEM_CONTENT")
    if not pem_content:
        pytest.skip("Environment has no value for 'PEM_CONTENT'")
        return

    pem_path = os.path.join(os.path.dirname(__file__), "certificate.pem")
    try:
        with open(pem_path, "w") as pem_file:
            pem_file.write(pem_content)
        return dict(live_identity_settings, cert_path=pem_path)
    except IOError as ex:
        pytest.skip("Failed to write file '{}': {}".format(pem_path, ex))
