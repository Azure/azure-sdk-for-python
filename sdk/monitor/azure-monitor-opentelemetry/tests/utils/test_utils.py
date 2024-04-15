# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from importlib import reload
from os import environ
from unittest import TestCase
from unittest.mock import patch

from azure.monitor.opentelemetry import _utils

TEST_VALUE = "TEST_VALUE"
TEST_IKEY = "1234abcd-ab12-34cd-ab12-a23456abcdef"
TEST_CONN_STR = f"InstrumentationKey={TEST_IKEY};IngestionEndpoint=https://centralus-2.in.applicationinsights.azure.com/;LiveEndpoint=https://centralus.livediagnostics.monitor.azure.com/"


def clear_env_var(env_var):
    if env_var in environ:
        del environ[env_var]


class TestUtils(TestCase):
    @patch.dict(
        "os.environ",
        {"ApplicationInsightsAgent_EXTENSION_VERSION": TEST_VALUE},
    )
    def test_extension_version(self):
        reload(_utils)
        self.assertEqual(_utils._EXTENSION_VERSION, TEST_VALUE)

    def test_extension_version_default(self):
        clear_env_var("ApplicationInsightsAgent_EXTENSION_VERSION")
        reload(_utils)
        self.assertEqual(_utils._EXTENSION_VERSION, "disabled")

    @patch.dict(
        "os.environ", {"APPLICATIONINSIGHTS_CONNECTION_STRING": TEST_CONN_STR}
    )
    def test_ikey(self):
        reload(_utils)
        self.assertEqual(
            _utils._get_customer_ikey_from_env_var(), TEST_IKEY
        )

    def test_ikey_defaults(self):
        clear_env_var("APPLICATIONINSIGHTS_CONNECTION_STRING")
        reload(_utils)
        self.assertEqual(
            _utils._get_customer_ikey_from_env_var(), "unknown"
        )

    @patch.dict("os.environ", {"WEBSITE_SITE_NAME": TEST_VALUE})
    def test_diagnostics_enabled(self):
        reload(_utils)
        self.assertTrue(_utils._IS_DIAGNOSTICS_ENABLED)

    def test_diagnostics_disabled(self):
        clear_env_var("WEBSITE_SITE_NAME")
        reload(_utils)
        self.assertFalse(_utils._IS_DIAGNOSTICS_ENABLED)

    @patch(
        "azure.monitor.opentelemetry._utils.platform.system",
        return_value="Linux",
    )
    def test_log_path_linux(self, mock_system):
        self.assertEqual(
            _utils._get_log_path(), "/var/log/applicationinsights"
        )

    @patch(
        "azure.monitor.opentelemetry._utils.platform.system",
        return_value="Linux",
    )
    def test_status_log_path_linux(self, mock_system):
        self.assertEqual(
            _utils._get_log_path(status_log_path=True),
            "/var/log/applicationinsights",
        )

    @patch(
        "azure.monitor.opentelemetry._utils.platform.system",
        return_value="Windows",
    )
    @patch("pathlib.Path.home", return_value="\\HOME\\DIR")
    def test_log_path_windows(self, mock_system, mock_home):
        self.assertEqual(
            _utils._get_log_path(),
            "\\HOME\\DIR\\LogFiles\\ApplicationInsights",
        )

    @patch(
        "azure.monitor.opentelemetry._utils.platform.system",
        return_value="Windows",
    )
    @patch("pathlib.Path.home", return_value="\\HOME\\DIR")
    def test_status_log_path_windows(self, mock_system, mock_home):
        self.assertEqual(
            _utils._get_log_path(status_log_path=True),
            "\\HOME\\DIR\\LogFiles\\ApplicationInsights\\status",
        )

    @patch(
        "azure.monitor.opentelemetry._utils.platform.system",
        return_value="Window",
    )
    def test_log_path_other(self, mock_platform):
        self.assertIsNone(_utils._get_log_path())

    @patch(
        "azure.monitor.opentelemetry._utils.platform.system",
        return_value="linux",
    )
    def test_status_log_path_other(self, mock_platform):
        self.assertIsNone(_utils._get_log_path(status_log_path=True))

    @patch.dict("os.environ", {"key": "value"})
    def test_env_var_or_default(self):
        self.assertEqual(_utils._env_var_or_default("key"), "value")

    @patch.dict("os.environ", {})
    def test_env_var_or_default_empty(self):
        self.assertEqual(_utils._env_var_or_default("key"), "")

    @patch.dict("os.environ", {})
    def test_env_var_or_default_empty_with_defaults(self):
        self.assertEqual(
            _utils._env_var_or_default("key", default_val="value"), "value"
        )
