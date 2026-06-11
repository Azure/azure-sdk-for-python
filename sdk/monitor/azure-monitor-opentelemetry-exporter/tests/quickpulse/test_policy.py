# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import weakref
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._quickpulse._policy import (
    _QuickpulseRedirectPolicy,
    _is_redirect_target_allowed,
)


# pylint: disable=line-too-long
class TestQuickpulseRedirectPolicy(unittest.TestCase):
    def test_get_redirect_location(self):
        policy = _QuickpulseRedirectPolicy()
        pipeline_resp_mock = mock.Mock()
        http_resp_mock = mock.Mock()
        headers = {
            "x-ms-qps-service-endpoint-redirect-v2": "https://eastus.livediagnostics.monitor.azure.com/QuickPulseService.svc"
        }
        http_resp_mock.headers = headers
        pipeline_resp_mock.http_response = http_resp_mock
        policy = _QuickpulseRedirectPolicy()
        qp_client_mock = mock.Mock()
        client_mock = mock.Mock()
        client_mock._base_url = "previous_url"
        qp_client_mock._client = client_mock
        qp_client_ref = weakref.ref(qp_client_mock)
        policy._qp_client_ref = qp_client_ref
        redirect_location = policy.get_redirect_location(pipeline_resp_mock)
        self.assertEqual(
            redirect_location,
            "https://eastus.livediagnostics.monitor.azure.com/QuickPulseService.svc",
        )
        self.assertEqual(
            client_mock._base_url,
            "https://eastus.livediagnostics.monitor.azure.com",
        )

    def test_get_redirect_location_no_header(self):
        policy = _QuickpulseRedirectPolicy()
        pipeline_resp_mock = mock.Mock()
        http_resp_mock = mock.Mock()
        headers = {}
        http_resp_mock.headers = headers
        pipeline_resp_mock.http_response = http_resp_mock
        policy = _QuickpulseRedirectPolicy()
        self.assertIsNone(policy.get_redirect_location(pipeline_resp_mock))

    def test_get_redirect_location_invalid_url(self):
        policy = _QuickpulseRedirectPolicy()
        pipeline_resp_mock = mock.Mock()
        http_resp_mock = mock.Mock()
        headers = {"x-ms-qps-service-endpoint-redirect-v2": "invalid_url"}
        http_resp_mock.headers = headers
        pipeline_resp_mock.http_response = http_resp_mock
        policy = _QuickpulseRedirectPolicy()
        qp_client_mock = mock.Mock()
        client_mock = mock.Mock()
        client_mock._base_url = "previous_url"
        qp_client_mock._client = client_mock
        qp_client_ref = weakref.ref(qp_client_mock)
        policy._qp_client_ref = qp_client_ref
        redirect_location = policy.get_redirect_location(pipeline_resp_mock)
        self.assertEqual(redirect_location, "invalid_url")
        self.assertEqual(client_mock._base_url, "previous_url")

    def test_get_redirect_location_no_client(self):
        policy = _QuickpulseRedirectPolicy()
        pipeline_resp_mock = mock.Mock()
        http_resp_mock = mock.Mock()
        headers = {
            "x-ms-qps-service-endpoint-redirect-v2": "https://eastus.livediagnostics.monitor.azure.com/QuickPulseService.svc"
        }
        http_resp_mock.headers = headers
        pipeline_resp_mock.http_response = http_resp_mock
        policy = _QuickpulseRedirectPolicy()
        redirect_location = policy.get_redirect_location(pipeline_resp_mock)
        self.assertEqual(
            redirect_location,
            "https://eastus.livediagnostics.monitor.azure.com/QuickPulseService.svc",
        )
        self.assertIsNone(policy._qp_client_ref)

    def test_get_redirect_location_rejects_untrusted_host(self):
        policy = _QuickpulseRedirectPolicy()
        pipeline_resp_mock = mock.Mock()
        http_resp_mock = mock.Mock()
        headers = {"x-ms-qps-service-endpoint-redirect-v2": "https://evil.attacker.com/exfiltrate"}
        http_resp_mock.headers = headers
        pipeline_resp_mock.http_response = http_resp_mock
        qp_client_mock = mock.Mock()
        client_mock = mock.Mock()
        client_mock._base_url = "https://original.livediagnostics.monitor.azure.com"
        qp_client_mock._client = client_mock
        qp_client_ref = weakref.ref(qp_client_mock)
        policy._qp_client_ref = qp_client_ref
        redirect_location = policy.get_redirect_location(pipeline_resp_mock)
        # Redirect should be rejected and return None
        self.assertIsNone(redirect_location)
        # Base URL must not be changed
        self.assertEqual(client_mock._base_url, "https://original.livediagnostics.monitor.azure.com")

    def test_get_redirect_location_rejects_http_scheme(self):
        policy = _QuickpulseRedirectPolicy()
        pipeline_resp_mock = mock.Mock()
        http_resp_mock = mock.Mock()
        headers = {
            "x-ms-qps-service-endpoint-redirect-v2": "http://eastus.livediagnostics.monitor.azure.com/QuickPulseService.svc"
        }
        http_resp_mock.headers = headers
        pipeline_resp_mock.http_response = http_resp_mock
        qp_client_mock = mock.Mock()
        client_mock = mock.Mock()
        client_mock._base_url = "https://original.livediagnostics.monitor.azure.com"
        qp_client_mock._client = client_mock
        qp_client_ref = weakref.ref(qp_client_mock)
        policy._qp_client_ref = qp_client_ref
        redirect_location = policy.get_redirect_location(pipeline_resp_mock)
        # HTTP downgrade should be rejected
        self.assertIsNone(redirect_location)
        self.assertEqual(client_mock._base_url, "https://original.livediagnostics.monitor.azure.com")

    def test_get_redirect_location_allows_visualstudio_domain(self):
        policy = _QuickpulseRedirectPolicy()
        pipeline_resp_mock = mock.Mock()
        http_resp_mock = mock.Mock()
        headers = {
            "x-ms-qps-service-endpoint-redirect-v2": "https://rt.services.visualstudio.com/QuickPulseService.svc"
        }
        http_resp_mock.headers = headers
        pipeline_resp_mock.http_response = http_resp_mock
        qp_client_mock = mock.Mock()
        client_mock = mock.Mock()
        client_mock._base_url = "https://original.livediagnostics.monitor.azure.com"
        qp_client_mock._client = client_mock
        qp_client_ref = weakref.ref(qp_client_mock)
        policy._qp_client_ref = qp_client_ref
        redirect_location = policy.get_redirect_location(pipeline_resp_mock)
        self.assertEqual(
            redirect_location,
            "https://rt.services.visualstudio.com/QuickPulseService.svc",
        )
        self.assertEqual(client_mock._base_url, "https://rt.services.visualstudio.com")

    def test_get_redirect_location_rejects_spoofed_suffix(self):
        """Attacker uses a domain that contains an allowed suffix but is not actually that domain."""
        policy = _QuickpulseRedirectPolicy()
        pipeline_resp_mock = mock.Mock()
        http_resp_mock = mock.Mock()
        # Reject a host like "monitor.azure.com.evil.com": it starts with the allowed-looking
        # "monitor.azure.com" string, but the actual hostname is a subdomain of "evil.com".
        headers = {"x-ms-qps-service-endpoint-redirect-v2": "https://monitor.azure.com.evil.com/exfiltrate"}
        http_resp_mock.headers = headers
        pipeline_resp_mock.http_response = http_resp_mock
        qp_client_mock = mock.Mock()
        client_mock = mock.Mock()
        client_mock._base_url = "https://original.livediagnostics.monitor.azure.com"
        qp_client_mock._client = client_mock
        qp_client_ref = weakref.ref(qp_client_mock)
        policy._qp_client_ref = qp_client_ref
        redirect_location = policy.get_redirect_location(pipeline_resp_mock)
        self.assertIsNone(redirect_location)
        self.assertEqual(client_mock._base_url, "https://original.livediagnostics.monitor.azure.com")

    def test_get_redirect_location_rejects_userinfo_bypass(self):
        """Reject redirect URLs that use userinfo (@) to disguise the real host."""
        policy = _QuickpulseRedirectPolicy()
        pipeline_resp_mock = mock.Mock()
        http_resp_mock = mock.Mock()
        # URL with userinfo: urlparse sees "evil.com" as the real host, not the allowed domain.
        headers = {
            "x-ms-qps-service-endpoint-redirect-v2": "https://eastus.livediagnostics.monitor.azure.com:443@evil.com/exfiltrate"
        }
        http_resp_mock.headers = headers
        pipeline_resp_mock.http_response = http_resp_mock
        qp_client_mock = mock.Mock()
        client_mock = mock.Mock()
        client_mock._base_url = "https://original.livediagnostics.monitor.azure.com"
        qp_client_mock._client = client_mock
        qp_client_ref = weakref.ref(qp_client_mock)
        policy._qp_client_ref = qp_client_ref
        redirect_location = policy.get_redirect_location(pipeline_resp_mock)
        self.assertIsNone(redirect_location)
        self.assertEqual(client_mock._base_url, "https://original.livediagnostics.monitor.azure.com")


class TestIsRedirectTargetAllowed(unittest.TestCase):
    def test_allowed_domains(self):
        self.assertTrue(_is_redirect_target_allowed("eastus.livediagnostics.monitor.azure.com"))
        self.assertTrue(_is_redirect_target_allowed("global.livediagnostics.monitor.azure.com"))
        self.assertTrue(_is_redirect_target_allowed("rt.services.visualstudio.com"))
        self.assertTrue(_is_redirect_target_allowed("westus.in.applicationinsights.azure.com"))
        self.assertTrue(_is_redirect_target_allowed("settings.monitor.azure.com"))
        self.assertTrue(_is_redirect_target_allowed("eastus.monitor.azure.us"))
        self.assertTrue(_is_redirect_target_allowed("eastus.monitor.azure.cn"))

    def test_allowed_domains_with_port(self):
        self.assertTrue(_is_redirect_target_allowed("eastus.livediagnostics.monitor.azure.com:443"))

    def test_disallowed_domains(self):
        self.assertFalse(_is_redirect_target_allowed("evil.attacker.com"))
        self.assertFalse(_is_redirect_target_allowed("monitor.azure.com.evil.com"))
        self.assertFalse(_is_redirect_target_allowed("localhost"))
        self.assertFalse(_is_redirect_target_allowed("192.168.1.1"))
        self.assertFalse(_is_redirect_target_allowed("attacker.com"))

    def test_disallowed_userinfo_bypass(self):
        self.assertFalse(_is_redirect_target_allowed("eastus.livediagnostics.monitor.azure.com:443@evil.com"))
        self.assertFalse(_is_redirect_target_allowed("user:pass@evil.com"))
