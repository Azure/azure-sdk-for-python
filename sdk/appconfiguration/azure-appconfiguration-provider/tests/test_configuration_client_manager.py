# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from unittest.mock import patch, call, Mock, MagicMock
import pytest
from azure.appconfiguration.provider._client_manager import ConfigurationClientManager, _ConfigurationClientWrapper
from azure.appconfiguration.provider._models import SettingSelector, FeatureFlagSelector


def _create_mock_credential():
    """Create a mock credential that satisfies token credential checks."""
    credential = MagicMock()
    credential.get_token = MagicMock()
    return credential


class MockClient:

    def __init__(self, endpoint, connection_string, credential, retry_total, retry_backoff):
        self.endpoint = endpoint
        self.connection_string = connection_string
        self.credential = credential
        self.retry_total = retry_total
        self.retry_backoff = retry_backoff


class _FakePagedIterator:
    """Mimics an ItemPaged page iterator, exposing a mutable ``etag`` reflecting the last-yielded page."""

    def __init__(self, pages):
        self._pages = iter(pages)
        self.etag = None

    def __iter__(self):
        return self

    def __next__(self):
        page, etag = next(self._pages)
        self.etag = etag
        return page


@pytest.mark.usefixtures("caplog")
class TestConfigurationClientManager(unittest.TestCase):

    @patch("azure.appconfiguration.provider._client_manager.find_auto_failover_endpoints")
    @patch("azure.appconfiguration.provider._client_manager._ConfigurationClientWrapper.from_connection_string")
    def test_create_client_manager_connection_string(self, mock_client, mock_update_failover_endpoints):
        endpoint = "https://fake.endpoint"

        # No connection string or credential was provided
        with self.assertRaises(ValueError) as ex:
            ConfigurationClientManager(None, endpoint, None, "", 0, 0, True, 0, 0, False)
            assert (
                str(ex.exception) == "Please pass either endpoint and credential, or a connection string with a value."
            )
        mock_update_failover_endpoints.assert_not_called()
        mock_client.assert_not_called()

        connection_string = "Endpoint=https://fake.endpoint/;Id=fake_id;Secret=fake_secret"

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # No auto failover endpoints found
        mock_update_failover_endpoints.return_value = []
        manager = ConfigurationClientManager(connection_string, endpoint, None, "", 0, 0, True, 0, 0, False)
        manager.refresh_clients()
        assert len(manager._replica_clients) == 1
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        mock_client.assert_called_once_with(endpoint, connection_string, "", 0, 0)

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # A single auto failover endpoint found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2"]
        manager = ConfigurationClientManager(connection_string, endpoint, None, "", 0, 0, True, 0, 0, False)
        manager.refresh_clients()
        assert len(manager._replica_clients) == 2
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        connection_string2 = "Endpoint=https://fake.endpoint2/;Id=fake_id;Secret=fake_secret"
        mock_client.assert_has_calls(
            [
                call(endpoint, connection_string, "", 0, 0),
                call().endpoint.__eq__("https://fake.endpoint2"),
                call("https://fake.endpoint2", connection_string2, "", 0, 0),
            ]
        )

    @patch("azure.appconfiguration.provider._client_manager.find_auto_failover_endpoints")
    @patch("azure.appconfiguration.provider._client_manager._ConfigurationClientWrapper.from_credential")
    def test_create_client_manager_endpoint(self, mock_client, mock_update_failover_endpoints):
        endpoint = "https://fake.endpoint"

        # No connection string or credential was provided
        with self.assertRaises(ValueError) as ex:
            ConfigurationClientManager(None, endpoint, None, "", 0, 0, True, 0, 0, False)
            assert (
                str(ex.exception) == "Please pass either endpoint and credential, or a connection string with a value."
            )
        mock_update_failover_endpoints.assert_not_called()
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # No auto failover endpoints found
        mock_update_failover_endpoints.return_value = []
        manager = ConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, False)
        manager.refresh_clients()
        assert len(manager._replica_clients) == 1
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        mock_client.assert_called_once_with(endpoint, "fake-credential", "", 0, 0)

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # A single auto failover endpoint found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2"]
        manager = ConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, False)
        manager.refresh_clients()
        assert len(manager._replica_clients) == 2
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        mock_client.assert_has_calls(
            [
                call(endpoint, "fake-credential", "", 0, 0),
                call().endpoint.__eq__("https://fake.endpoint2"),
                call("https://fake.endpoint2", "fake-credential", "", 0, 0),
            ]
        )

    @patch("azure.appconfiguration.provider._client_manager.find_auto_failover_endpoints")
    @patch("azure.appconfiguration.provider._client_manager._ConfigurationClientWrapper.from_credential")
    def test_refresh_clients_credential(
        self, mock_client, mock_update_failover_endpoints
    ):  # pylint: disable=too-many-statements
        endpoint = "https://fake.endpoint"

        mock_client.return_value = MockClient("https://fake.endpoint", "", "fake-credential", 0, 0)
        mock_update_failover_endpoints.return_value = []
        manager = ConfigurationClientManager(None, endpoint, "fake-credential", "", 0, 0, True, 0, 0, False)
        manager_disabled_refresh = ConfigurationClientManager(
            None, endpoint, "fake-credential", "", 0, 0, False, 0, 0, False
        )

        # Reset the mocks as they are called during initialization
        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # Refresh period reached but disabled
        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        manager_disabled_refresh.refresh_clients()
        mock_update_failover_endpoints.assert_not_called()
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # No auto failover endpoints found
        mock_update_failover_endpoints.return_value = []
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # A single auto failover endpoint found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2"]
        mock_client.return_value = MockClient("https://fake.endpoint2", "", "fake-credential", 0, 0)
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 2
        mock_client.assert_called_once_with("https://fake.endpoint2", "fake-credential", "", 0, 0)

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # No new auto failover endpoints found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2"]
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 2
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # An additional auto failover endpoint found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2", "https://fake.endpoint3"]
        mock_client.return_value = MockClient("https://fake.endpoint3", "", "fake-credential", 0, 0)
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 3
        mock_client.assert_called_once_with("https://fake.endpoint3", "fake-credential", "", 0, 0)

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # A replica no longer exists
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint3"]
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 2
        mock_client.assert_not_called()

    @patch("azure.appconfiguration.provider._client_manager.find_auto_failover_endpoints")
    @patch("azure.appconfiguration.provider._client_manager._ConfigurationClientWrapper.from_connection_string")
    def test_refresh_clients_connection_string(
        self, mock_client, mock_update_failover_endpoints
    ):  # pylint: disable=too-many-statements
        endpoint = "https://fake.endpoint"

        mock_client.return_value = MockClient(
            "https://fake.endpoint", "Endpoint=https://fake.endpoint/;Id=fake_id;Secret=fake_secret", None, 0, 0
        )
        mock_update_failover_endpoints.return_value = []
        manager = ConfigurationClientManager(
            "Endpoint=https://fake.endpoint/;Id=fake_id;Secret=fake_secret", endpoint, None, "", 0, 0, True, 0, 0, False
        )
        manager_disabled_refresh = ConfigurationClientManager(
            "Endpoint=https://fake.endpoint/;Id=fake_id;Secret=fake_secret",
            endpoint,
            None,
            "",
            0,
            0,
            False,
            0,
            0,
            False,
        )

        # Reset the mocks as they are called during initialization
        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # Refresh period reached but disabled
        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        manager_disabled_refresh.refresh_clients()
        mock_update_failover_endpoints.assert_not_called()
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # No auto failover endpoints found
        mock_update_failover_endpoints.return_value = []
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # A single auto failover endpoint found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2"]
        mock_client.return_value = MockClient(
            "https://fake.endpoint2", "Endpoint=https://fake.endpoint/;Id=fake_id;Secret=fake_secret", None, 0, 0
        )
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 2
        mock_client.assert_called_once_with(
            "https://fake.endpoint2", "Endpoint=https://fake.endpoint2/;Id=fake_id;Secret=fake_secret", "", 0, 0
        )

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # No new auto failover endpoints found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2"]
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 2
        mock_client.assert_not_called()

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # An additional auto failover endpoint found
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint2", "https://fake.endpoint3"]
        mock_client.return_value = MockClient(
            "https://fake.endpoint3", "Endpoint=https://fake.endpoint3/;Id=fake_id;Secret=fake_secret", None, 0, 0
        )
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 3
        mock_client.assert_called_once_with(
            "https://fake.endpoint3", "Endpoint=https://fake.endpoint3/;Id=fake_id;Secret=fake_secret", "", 0, 0
        )

        mock_update_failover_endpoints.reset_mock()
        mock_client.reset_mock()

        # A replica no longer exists
        mock_update_failover_endpoints.return_value = ["https://fake.endpoint3"]
        manager._next_update_time = 0
        manager.refresh_clients()
        mock_update_failover_endpoints.assert_called_once_with(endpoint, True)
        assert len(manager._replica_clients) == 2
        mock_client.assert_not_called()

    @patch("azure.appconfiguration.provider._client_manager.find_auto_failover_endpoints")
    def test_calculate_backoff(self, mock_update_failover_endpoints):
        endpoint = "https://fake.endpoint"
        mock_update_failover_endpoints.return_value = []
        credential = _create_mock_credential()
        manager = ConfigurationClientManager(None, endpoint, credential, "", 0, 0, True, 30, 600, False)
        manager_invalid = ConfigurationClientManager(None, endpoint, credential, "", 0, 0, True, 600, 30, False)

        assert manager._calculate_backoff(0) == 30000.0
        assert 30000.0 <= manager._calculate_backoff(1) <= 60000.0
        assert 30000.0 <= manager._calculate_backoff(2) <= 120000.0
        assert 30000.0 <= manager._calculate_backoff(3) <= 240000.0
        assert 30000.0 <= manager._calculate_backoff(4) <= 480000.0
        assert 30000.0 <= manager._calculate_backoff(5) <= 600000.0
        assert 30000.0 <= manager._calculate_backoff(6) <= 600000.0
        assert 30000.0 <= manager._calculate_backoff(7) <= 600000.0
        assert 30000.0 <= manager._calculate_backoff(8) <= 600000.0
        assert 30000.0 <= manager._calculate_backoff(9) <= 600000.0
        assert 30000.0 <= manager._calculate_backoff(10) <= 600000.0

        assert manager_invalid._calculate_backoff(0) == 600000


def test_check_page_etags_snapshot_first_then_keys():
    """Refresh enabled without watch settings: snapshot selector first, then normal keys."""
    mock_client = Mock()
    wrapper = _ConfigurationClientWrapper("https://fake.endpoint", mock_client)

    selects = [
        SettingSelector(snapshot_name="my-snapshot"),
        SettingSelector(key_filter="app/*"),
    ]
    page_etags = [[], ["etag1"]]

    mock_response = Mock()
    mock_response.by_page.return_value = iter([])
    mock_client.list_configuration_settings.return_value = mock_response

    result = wrapper.check_page_etags(selects, page_etags)

    assert result is False
    # Only the non-snapshot selector should trigger a service call
    mock_client.list_configuration_settings.assert_called_once_with(
        key_filter="app/*", label_filter="\0", tags_filter=None
    )


def test_check_page_etags_keys_first_then_snapshot():
    """Refresh enabled without watch settings: normal keys first, then snapshot selector."""
    mock_client = Mock()
    wrapper = _ConfigurationClientWrapper("https://fake.endpoint", mock_client)

    selects = [
        SettingSelector(key_filter="app/*"),
        SettingSelector(snapshot_name="my-snapshot"),
    ]
    page_etags = [["etag1"], []]

    mock_response = Mock()
    mock_response.by_page.return_value = iter([])
    mock_client.list_configuration_settings.return_value = mock_response

    result = wrapper.check_page_etags(selects, page_etags)

    assert result is False
    # Only the non-snapshot selector should trigger a service call
    mock_client.list_configuration_settings.assert_called_once_with(
        key_filter="app/*", label_filter="\0", tags_filter=None
    )


def test_load_enhanced_feature_flags_no_feature_flag_client():
    """When no feature flag client is configured, no service calls are made."""
    mock_client = Mock()
    wrapper = _ConfigurationClientWrapper("https://fake.endpoint", mock_client)

    selects = [SettingSelector(key_filter="app/*"), SettingSelector(key_filter="other/*")]

    feature_flags, page_etags = wrapper.load_enhanced_feature_flags(selects)

    assert feature_flags == []
    assert page_etags == [[], []]


def test_load_enhanced_feature_flags_assumes_pre_filtered_selectors():
    mock_client = Mock()
    mock_feature_flag_client = Mock()
    wrapper = _ConfigurationClientWrapper("https://fake.endpoint", mock_client, mock_feature_flag_client)

    selects = [FeatureFlagSelector(name_filter="app/*")]

    flag1 = Mock(name="flag1")
    mock_response = Mock()
    mock_response.by_page.return_value = _FakePagedIterator([([flag1], "etag1")])
    mock_feature_flag_client.list_feature_flags.return_value = mock_response

    feature_flags, page_etags = wrapper.load_enhanced_feature_flags(selects)

    assert feature_flags == [flag1]
    assert page_etags == [["etag1"]]
    mock_feature_flag_client.list_feature_flags.assert_called_once_with(
        name_filter="app/*", label_filter="\0", tags_filter=None
    )


def test_load_enhanced_feature_flags_multiple_pages():
    """Multiple pages should be aggregated and each page's etag collected."""
    mock_client = Mock()
    mock_feature_flag_client = Mock()
    wrapper = _ConfigurationClientWrapper("https://fake.endpoint", mock_client, mock_feature_flag_client)

    selects = [FeatureFlagSelector(name_filter="app/*")]

    flag1 = Mock(name="flag1")
    flag2 = Mock(name="flag2")

    class FakeIterator:
        """Mimics an ItemPaged iterator, exposing a mutable ``etag`` reflecting the last-yielded page."""

        def __init__(self, pages):
            self._pages = iter(pages)
            self.etag = None

        def __iter__(self):
            return self

        def __next__(self):
            page, etag = next(self._pages)
            self.etag = etag
            return page

    mock_response = Mock()
    mock_response.by_page.return_value = FakeIterator([([flag1], "etag1"), ([flag2], "etag2")])
    mock_feature_flag_client.list_feature_flags.return_value = mock_response

    feature_flags, page_etags = wrapper.load_enhanced_feature_flags(selects)

    assert feature_flags == [flag1, flag2]
    assert page_etags == [["etag1", "etag2"]]


def test_check_enhanced_feature_flag_etags_no_feature_flag_client():
    """When no feature flag client is configured, no changes are reported."""
    mock_client = Mock()
    wrapper = _ConfigurationClientWrapper("https://fake.endpoint", mock_client)

    selects = [SettingSelector(key_filter="app/*")]

    result = wrapper.check_enhanced_feature_flag_etags(selects, [["etag1"]])

    assert result is False


def test_check_enhanced_feature_flag_etags_no_change():
    """When the returned pages are empty, no changes are reported."""
    mock_client = Mock()
    mock_feature_flag_client = Mock()
    wrapper = _ConfigurationClientWrapper("https://fake.endpoint", mock_client, mock_feature_flag_client)

    selects = [FeatureFlagSelector(name_filter="app/*")]
    page_etags = [["etag1"]]

    mock_response = Mock()
    mock_response.by_page.return_value = iter([])
    mock_feature_flag_client.list_feature_flags.return_value = mock_response

    result = wrapper.check_enhanced_feature_flag_etags(selects, page_etags)

    assert result is False
    mock_feature_flag_client.list_feature_flags.assert_called_once_with(
        name_filter="app/*", label_filter="\0", tags_filter=None
    )
    mock_response.by_page.assert_called_once_with(match_conditions=["etag1"])


def test_check_enhanced_feature_flag_etags_change_detected():
    """When a page is returned, a change should be reported."""
    mock_client = Mock()
    mock_feature_flag_client = Mock()
    wrapper = _ConfigurationClientWrapper("https://fake.endpoint", mock_client, mock_feature_flag_client)

    selects = [FeatureFlagSelector(name_filter="app/*")]
    page_etags = [["etag1"]]

    mock_response = Mock()
    mock_response.by_page.return_value = iter([[Mock()]])
    mock_feature_flag_client.list_feature_flags.return_value = mock_response

    result = wrapper.check_enhanced_feature_flag_etags(selects, page_etags)

    assert result is True


def test_check_enhanced_feature_flag_etags_assumes_pre_filtered_selectors():
    """The enhanced feature flag endpoint does not support snapshots. Filtering out selectors with a
    snapshot_name is the caller's responsibility (done once at startup via
    ConfigurationProviderBase._enhanced_feature_flag_selectors), so this method should simply process whatever
    selectors it is given."""
    mock_client = Mock()
    mock_feature_flag_client = Mock()
    wrapper = _ConfigurationClientWrapper("https://fake.endpoint", mock_client, mock_feature_flag_client)

    selects = [FeatureFlagSelector(name_filter="app/*")]
    page_etags = [["etag1"]]

    mock_response = Mock()
    mock_response.by_page.return_value = iter([])
    mock_feature_flag_client.list_feature_flags.return_value = mock_response

    result = wrapper.check_enhanced_feature_flag_etags(selects, page_etags)

    assert result is False
    mock_feature_flag_client.list_feature_flags.assert_called_once_with(
        name_filter="app/*", label_filter="\0", tags_filter=None
    )


def test_check_enhanced_feature_flag_etags_missing_page_etags_triggers_refresh():
    """Missing etag state for a selector should trigger a refresh instead of failing."""
    mock_client = Mock()
    mock_feature_flag_client = Mock()
    wrapper = _ConfigurationClientWrapper("https://fake.endpoint", mock_client, mock_feature_flag_client)

    selects = [FeatureFlagSelector(name_filter="app/*"), FeatureFlagSelector(name_filter="other/*")]
    # Only one entry provided for two selectors; the first selector's page hasn't changed.
    mock_response = Mock()
    mock_response.by_page.return_value = iter([])
    mock_feature_flag_client.list_feature_flags.return_value = mock_response
    page_etags = [["etag1"]]

    result = wrapper.check_enhanced_feature_flag_etags(selects, page_etags)

    assert result is True
