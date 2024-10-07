# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from unittest.mock import patch, call
from azure.appconfiguration.provider._discovery import (
    _get_known_domain,
    _request_record,
    _find_replicas,
    _find_origin,
    find_auto_failover_endpoints,
)
from dns.resolver import NXDOMAIN, YXDOMAIN, LifetimeTimeout, NoNameservers  # cspell:disable-line

AZCONFIG_IO = ".azconfig.io"  # cspell:disable-line
APPCONFIG_IO = ".appconfig.io"  # cspell:disable-line


class FakeAnswer:

    def __init__(self, priority, weight, port, target):
        self.priority = priority
        self.weight = weight
        self.port = port
        self.target = target.rstrip(".")


@pytest.mark.usefixtures("caplog")
class TestDiscovery:

    def test_get_known_domain(self):
        fake_endpoint = "https://fake.endpoint"
        assert _get_known_domain(fake_endpoint) is None
        fake_endpoint = "https://fake.endpoint." + AZCONFIG_IO  # cspell:disable-line
        assert _get_known_domain(fake_endpoint) == AZCONFIG_IO  # cspell:disable-line
        fake_endpoint = "https://fake.endpoint" + AZCONFIG_IO + ".test"  # cspell:disable-line
        assert _get_known_domain(fake_endpoint) == AZCONFIG_IO + ".test"  # cspell:disable-line
        fake_endpoint = "https://fake.endpoint" + APPCONFIG_IO
        assert _get_known_domain(fake_endpoint) == APPCONFIG_IO

    @patch("azure.appconfiguration.provider._discovery.dns.resolver.resolve")
    def test_request_record(self, mock_dns):
        origin_request = "_origin._tcp.fake.endpoint"
        mock_dns.return_value = []
        assert len(_request_record(origin_request)) == 0

        mock_dns.return_value = [1, 2, 3]
        assert len(_request_record(origin_request)) == 3

        mock_dns.side_effect = NXDOMAIN  # cspell:disable-line
        assert len(_request_record(origin_request)) == 0

        mock_dns.side_effect = YXDOMAIN  # cspell:disable-line
        assert len(_request_record(origin_request)) == 0

        mock_dns.side_effect = LifetimeTimeout
        assert not _request_record(origin_request)

        mock_dns.side_effect = NoNameservers
        assert not _request_record(origin_request)

    @patch("azure.appconfiguration.provider._discovery._request_record")
    def test_find_replicas(self, mock_request_record):
        origin = "fake.endpoint"
        mock_request_record.return_value = None
        assert not _find_replicas(origin)
        mock_request_record.assert_called_once_with("_alt0._tcp.fake.endpoint")

        mock_request_record.reset_mock()
        mock_request_record.return_value = []
        assert len(_find_replicas(origin)) == 0
        mock_request_record.assert_called_once_with("_alt0._tcp.fake.endpoint")

        mock_request_record.reset_mock()
        mock_request_record.side_effect = [[FakeAnswer(1, 99, 5000, "fake.endpoint.")], []]
        result = _find_replicas(origin)
        assert len(result) == 1
        assert result[0].priority == 1
        assert result[0].weight == 99
        assert result[0].port == 5000
        assert result[0].target == "fake.endpoint"
        assert mock_request_record.call_count == 2
        mock_request_record.assert_has_calls([call("_alt0._tcp.fake.endpoint"), call("_alt1._tcp.fake.endpoint")])

        mock_request_record.reset_mock()
        mock_request_record.side_effect = [
            [FakeAnswer(1, 99, 5000, "fake.endpoint."), FakeAnswer(2, 98, 5001, "fake.endpoint.")],
            [],
        ]
        result = _find_replicas(origin)
        assert len(result) == 2
        assert mock_request_record.call_count == 2
        mock_request_record.assert_has_calls([call("_alt0._tcp.fake.endpoint"), call("_alt1._tcp.fake.endpoint")])

        mock_request_record.reset_mock()
        mock_request_record.side_effect = [
            [FakeAnswer(1, 99, 5000, "fake.endpoint."), FakeAnswer(2, 98, 5001, "fake.endpoint.")],
            [FakeAnswer(3, 99, 5000, "fake.endpoint.")],
            [],
        ]
        result = _find_replicas(origin)
        assert len(result) == 3
        assert mock_request_record.call_count == 3
        mock_request_record.assert_has_calls(
            [call("_alt0._tcp.fake.endpoint"), call("_alt1._tcp.fake.endpoint"), call("_alt2._tcp.fake.endpoint")]
        )

    @patch("azure.appconfiguration.provider._discovery._request_record")
    def test_find_origin(self, mock_request_record):
        endpoint = "https://fake.endpoint"
        mock_request_record.return_value = None
        assert not _find_origin(endpoint)
        mock_request_record.assert_called_once_with("_origin._tcp.fake.endpoint")

        mock_request_record.reset_mock()
        mock_request_record.return_value = []
        assert not _find_origin(endpoint)
        mock_request_record.assert_called_once_with("_origin._tcp.fake.endpoint")

        mock_request_record.reset_mock()
        mock_request_record.return_value = [FakeAnswer(1, 99, 5000, "fake.endpoint.")]
        result = _find_origin(endpoint)
        assert result.priority == 1
        assert result.weight == 99
        assert result.port == 5000
        assert result.target == "fake.endpoint"
        mock_request_record.assert_called_once_with("_origin._tcp.fake.endpoint")

        mock_request_record.reset_mock()
        mock_request_record.return_value = [
            FakeAnswer(1, 99, 5000, "fake.endpoint1."),
            FakeAnswer(2, 98, 5001, "fake.endpoint2."),
        ]
        result = _find_origin(endpoint)
        assert result.priority == 1
        assert result.weight == 99
        assert result.port == 5000
        assert result.target == "fake.endpoint1"
        mock_request_record.assert_called_once_with("_origin._tcp.fake.endpoint")

    @patch("azure.appconfiguration.provider._discovery._find_origin")
    @patch("azure.appconfiguration.provider._discovery._find_replicas")
    def test_find_auto_failover_endpoints(self, mock_find_replicas, mock_find_origin):
        endpoint = "https://fake.appconfig.io"

        assert len(find_auto_failover_endpoints(endpoint, False)) == 0
        mock_find_origin.assert_not_called()
        mock_find_replicas.assert_not_called()

        mock_find_origin.reset_mock()
        mock_find_replicas.reset_mock()
        assert len(find_auto_failover_endpoints("bad.endpoint", True)) == 0
        mock_find_origin.assert_not_called()
        mock_find_replicas.assert_not_called()

        mock_find_origin.reset_mock()
        mock_find_replicas.reset_mock()
        mock_find_origin.return_value = FakeAnswer(1, 99, 5000, "fake.appconfig.io")
        mock_find_replicas.return_value = []
        assert not find_auto_failover_endpoints(endpoint, True)

        mock_find_origin.reset_mock()
        mock_find_replicas.reset_mock()
        mock_find_origin.return_value = FakeAnswer(1, 99, 5000, "fake.appconfig.io")
        mock_find_replicas.return_value = [FakeAnswer(2, 98, 5001, "fake1.appconfig.io.")]
        result = find_auto_failover_endpoints(endpoint, True)
        assert len(result) == 1
        assert result[0] == "https://fake1.appconfig.io"
        mock_find_origin.assert_called_once_with(endpoint)
        mock_find_replicas.assert_called_once_with("fake.appconfig.io")

        mock_find_origin.reset_mock()
        mock_find_replicas.reset_mock()
        mock_find_origin.return_value = FakeAnswer(1, 99, 5000, "fake.appconfig.io")
        mock_find_replicas.return_value = [
            FakeAnswer(2, 98, 5001, "fake1.appconfig.io."),
            FakeAnswer(3, 97, 5002, "fake2.appconfig.io."),
        ]
        result = find_auto_failover_endpoints(endpoint, True)
        assert len(result) == 2
        assert result[0] == "https://fake1.appconfig.io"
        assert result[1] == "https://fake2.appconfig.io"
        mock_find_origin.assert_called_once_with(endpoint)
        mock_find_replicas.assert_called_once_with("fake.appconfig.io")

        mock_find_origin.reset_mock()
        mock_find_replicas.reset_mock()
        mock_find_origin.return_value = FakeAnswer(1, 99, 5000, "fake.appconfig.io")
        mock_find_replicas.return_value = [
            FakeAnswer(2, 98, 5001, "fake1.appconfig.io."),
            FakeAnswer(3, 97, 5002, "fake2.appconfig.io."),
        ]
        result = find_auto_failover_endpoints("https://fake1.appconfig.io", True)
        assert len(result) == 2
        assert result[0] == "https://fake.appconfig.io"
        assert result[1] == "https://fake2.appconfig.io"
        mock_find_origin.assert_called_once_with("https://fake1.appconfig.io")
        mock_find_replicas.assert_called_once_with("fake.appconfig.io")
