# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from unittest.mock import patch, call
from azure.appconfiguration.provider._discovery import _get_known_domain, _request_record, _find_replicas
from dns.resolver import NXDOMAIN, YXDOMAIN, LifetimeTimeout, NoNameservers, Answer  # cspell:disable-line

AZCONFIG_IO = ".azconfig.io" # cspell:disable-line
APPCONFIG_IO = ".appconfig.io" # cspell:disable-line

class FakeAnswer:

    def __init__(self, priority, weight, port, target):
        self.priority = priority
        self.weight = weight
        self.port = port
        self.target = target


@pytest.mark.usefixtures("caplog")
class TestDiscovery:

    def test_get_known_domain(self):
        fake_endpoint = "https://fake.endpoint"
        assert _get_known_domain(fake_endpoint) is None
        fake_endpoint = "https://fake.endpoint." + AZCONFIG_IO # cspell:disable-line
        assert _get_known_domain(fake_endpoint) == AZCONFIG_IO # cspell:disable-line
        fake_endpoint = "https://fake.endpoint" + AZCONFIG_IO + ".test" # cspell:disable-line
        assert _get_known_domain(fake_endpoint) == AZCONFIG_IO + ".test" # cspell:disable-line
        fake_endpoint = "https://fake.endpoint" + APPCONFIG_IO
        assert _get_known_domain(fake_endpoint) == APPCONFIG_IO

    def test_request_record(self):
        origin_request = "_origin._tcp.fake.endpoint"
        with patch("azure.appconfiguration.provider._discovery.dns.resolver.resolve") as mock_dns:
            mock_dns.return_value = []
            assert len(_request_record(origin_request)) == 0

            mock_dns.return_value = [1, 2, 3]
            assert len(_request_record(origin_request)) == 3

            mock_dns.side_effect = NXDOMAIN # cspell:disable-line
            assert len(_request_record(origin_request)) == 0

            mock_dns.side_effect = YXDOMAIN # cspell:disable-line
            assert len(_request_record(origin_request)) == 0

            mock_dns.side_effect = LifetimeTimeout
            assert not _request_record(origin_request)

            mock_dns.side_effect = NoNameservers
            assert not _request_record(origin_request)

    def test_find_replicas(self):
        origin = "fake.endpoint"
        with patch("azure.appconfiguration.provider._discovery._request_record") as mock_origin:
            mock_origin.return_value = None
            assert not _find_replicas(origin)
            mock_origin.assert_called_once_with("_alt0._tcp.fake.endpoint")

            mock_origin.reset_mock()
            mock_origin.return_value = []
            assert len(_find_replicas(origin)) == 0
            mock_origin.assert_called_once_with("_alt0._tcp.fake.endpoint")

            mock_origin.reset_mock()
            mock_origin.side_effect = [[FakeAnswer(1, 99, 5000, "fake.endpoint.")], []]
            result = _find_replicas(origin)
            assert len(result) == 1
            assert result[0].priority == 1
            assert result[0].weight == 99
            assert result[0].port == 5000
            assert result[0].target == "fake.endpoint"
            assert mock_origin.call_count == 2
            mock_origin.assert_has_calls([call("_alt0._tcp.fake.endpoint"), call("_alt1._tcp.fake.endpoint")])

            mock_origin.reset_mock()
            mock_origin.side_effect = [
                [FakeAnswer(1, 99, 5000, "fake.endpoint."), FakeAnswer(2, 98, 5001, "fake.endpoint.")],
                [],
            ]
            result = _find_replicas(origin)
            assert len(result) == 2
            assert mock_origin.call_count == 2
            mock_origin.assert_has_calls([call("_alt0._tcp.fake.endpoint"), call("_alt1._tcp.fake.endpoint")])

            mock_origin.reset_mock()
            mock_origin.side_effect = [
                [FakeAnswer(1, 99, 5000, "fake.endpoint."), FakeAnswer(2, 98, 5001, "fake.endpoint.")],
                [FakeAnswer(3, 99, 5000, "fake.endpoint.")],
                [],
            ]
            result = _find_replicas(origin)
            assert len(result) == 3
            assert mock_origin.call_count == 3
            mock_origin.assert_has_calls(
                [call("_alt0._tcp.fake.endpoint"), call("_alt1._tcp.fake.endpoint"), call("_alt2._tcp.fake.endpoint")]
            )
