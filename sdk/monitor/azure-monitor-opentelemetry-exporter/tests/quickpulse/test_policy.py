# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import weakref
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._quickpulse._policy import _QuickpulseRedirectPolicy


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
        redirect_location = policy.get_redirect_location(pipeline_resp_mock)
 
    def test_get_redirect_location_invalid_url(self):
        policy = _QuickpulseRedirectPolicy()
        pipeline_resp_mock = mock.Mock()
        http_resp_mock = mock.Mock()
        headers = {
            "x-ms-qps-service-endpoint-redirect-v2": "invalid_url"
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
        self.assertEqual(redirect_location, "invalid_url")
        self.assertEqual(client_mock._base_url,"previous_url")

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
        self.assertEqual(redirect_location, "https://eastus.livediagnostics.monitor.azure.com/QuickPulseService.svc")
        self.assertIsNone(policy._qp_client_ref)
