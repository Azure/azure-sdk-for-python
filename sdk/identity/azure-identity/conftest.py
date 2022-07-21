# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import sys

from unittest import mock
import pytest
import six
from devtools_testutils import test_proxy, add_general_regex_sanitizer, is_live, add_body_key_sanitizer
from azure.identity._constants import DEVELOPER_SIGN_ON_CLIENT_ID, EnvironmentVariables

RECORD_IMDS = "--record-imds"


def pytest_addoption(parser):
    parser.addoption("--manual", action="store_true", default=False, help="run manual tests")
    parser.addoption(RECORD_IMDS, action="store_true", default=False, help="record IMDS live tests")


def pytest_configure(config):
    config.addinivalue_line("markers", "manual: mark test as requiring manual interaction")
    config.addinivalue_line("markers", "prints: mark test as printing important information to stdout")


def pytest_collection_modifyitems(config, items):
    stdout_captured = config.getoption("capture") != "no"
    run_manual_tests = config.getoption("--manual")
    if not stdout_captured and run_manual_tests:
        return

    # skip manual tests or tests which print to stdout, as appropriate
    skip_manual = pytest.mark.skip(reason="run pytest with '--manual' to run manual tests")
    skip_prints = pytest.mark.skip(reason="this test prints to stdout, run pytest with '-s' to make output visible")
    for test in items:
        if not run_manual_tests and "manual" in test.keywords:
            test.add_marker(skip_manual)
        elif stdout_captured and "prints" in test.keywords:
            test.add_marker(skip_prints)


@pytest.fixture(scope="class")
def record_imds_test(request):
    """Fixture to control recording IMDS managed identity tests

    Recorded IMDS tests run as expected in playback. However, because they require particular live environments, a
    custom pytest option ("--record-imds") controls whether they're included in a live test run.
    """
    if is_live() and not request.session.config.getoption(RECORD_IMDS):
        pytest.skip('Run "pytest {}" to record a live run of this test'.format(RECORD_IMDS))


@pytest.fixture()
def live_service_principal():
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


def get_certificate_parameters(content, password_protected_content, password, extension):
    # type: (bytes, bytes, str, str) -> dict
    current_directory = os.path.dirname(__file__)
    parameters = {
        "cert_bytes": six.ensure_binary(content),
        "cert_path": os.path.join(current_directory, "certificate." + extension),
        "cert_with_password_bytes": six.ensure_binary(password_protected_content),
        "cert_with_password_path": os.path.join(current_directory, "certificate-with-password." + extension),
        "password": password,
    }

    try:
        with open(parameters["cert_path"], "wb") as f:
            f.write(parameters["cert_bytes"])
        with open(parameters["cert_with_password_path"], "wb") as f:
            f.write(parameters["cert_with_password_bytes"])
    except IOError as ex:
        pytest.skip("Failed to write a file: {}".format(ex))

    return parameters


@pytest.fixture()
def live_pem_certificate(live_service_principal):
    content = os.environ.get("PEM_CONTENT")
    password_protected_content = os.environ.get("PEM_CONTENT_PASSWORD_PROTECTED")
    password = os.environ.get("CERTIFICATE_PASSWORD")

    if content and password_protected_content and password:
        parameters = get_certificate_parameters(content, password_protected_content, password, "pem")
        return dict(live_service_principal, **parameters)

    pytest.skip("Missing PEM certificate configuration")


@pytest.fixture()
def live_pfx_certificate(live_service_principal):
    # PFX bytes arrive base64 encoded because Key Vault secrets have string values
    encoded_content = os.environ.get("PFX_CONTENT")
    encoded_password_protected_content = os.environ.get("PFX_CONTENT_PASSWORD_PROTECTED")
    password = os.environ.get("CERTIFICATE_PASSWORD")

    if encoded_content and encoded_password_protected_content and password:
        import base64

        content = base64.b64decode(six.ensure_binary(encoded_content))
        password_protected_content = base64.b64decode(six.ensure_binary(encoded_password_protected_content))

        parameters = get_certificate_parameters(content, password_protected_content, password, "pfx")
        return dict(live_service_principal, **parameters)

    pytest.skip("Missing PFX certificate configuration")


@pytest.fixture()
def live_user_details():
    user_details = {
        "client_id": DEVELOPER_SIGN_ON_CLIENT_ID,
        "username": os.environ.get(EnvironmentVariables.AZURE_USERNAME),
        "password": os.environ.get(EnvironmentVariables.AZURE_PASSWORD),
        "tenant": os.environ.get("USER_TENANT"),
    }
    if None in user_details.values():
        pytest.skip("To test username/password authentication, set $AZURE_USERNAME, $AZURE_PASSWORD, $USER_TENANT")
    else:
        return user_details


@pytest.fixture()
def event_loop():
    """Ensure the event loop used by pytest-asyncio on Windows is ProactorEventLoop, which supports subprocesses.

    This is necessary because SelectorEventLoop, which does not support subprocesses, is the default on Python < 3.8.
    """

    try:
        import asyncio
    except:
        return

    if sys.platform.startswith("win"):
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()

    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    if EnvironmentVariables.MSI_ENDPOINT in os.environ:
        url = os.environ.get(EnvironmentVariables.MSI_ENDPOINT)
        PLAYBACK_URL = "https://msi-endpoint/token"
        add_general_regex_sanitizer(regex=url, value=PLAYBACK_URL)
    if "USER_ASSIGNED_IDENTITY_CLIENT_ID" in os.environ:
        PLAYBACK_CLIENT_ID = "client-id"
        user_assigned_identity_client_id = os.environ.get("USER_ASSIGNED_IDENTITY_CLIENT_ID")
        add_general_regex_sanitizer(regex=user_assigned_identity_client_id, value=PLAYBACK_CLIENT_ID)
    if "CAE_ARM_URL" in os.environ and "CAE_TENANT_ID" in os.environ and "CAE_USERNAME" in os.environ:
        try:
            from six.moves.urllib_parse import urlparse
            arm_url = os.environ["CAE_ARM_URL"]
            real = urlparse(arm_url)
            add_general_regex_sanitizer(regex=real.netloc, value="management.azure.com")
            add_general_regex_sanitizer(regex=os.environ["CAE_TENANT_ID"], value="tenant")
            add_general_regex_sanitizer(regex=os.environ["CAE_USERNAME"], value="username")
        except Exception:
            pass
    if "OBO_TENANT_ID" in os.environ and "OBO_USERNAME" in os.environ:
        add_general_regex_sanitizer(regex=os.environ["OBO_TENANT_ID"], value="tenant")
        add_general_regex_sanitizer(regex=os.environ["OBO_USERNAME"], value="username")
    add_body_key_sanitizer(json_path="$..access_token", value="access_token")


@pytest.fixture(scope="session", autouse=True)
def patch_async_sleep():
    async def immediate_return(_):
        return

    if not is_live():
        with mock.patch("asyncio.sleep", immediate_return):
            yield

    else:
        yield


@pytest.fixture(scope="session", autouse=True)
def patch_sleep():
    def immediate_return(_):
        return

    if not is_live():
        with mock.patch("time.sleep", immediate_return):
            yield

    else:
        yield
