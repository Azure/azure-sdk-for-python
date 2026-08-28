from unittest.mock import MagicMock, patch

import pytest
from azure.core.exceptions import HttpResponseError

from conftest import _wait_for_data_plane_access


def _http_error(status_code):
    response = MagicMock()
    response.status_code = status_code
    response.reason = "Forbidden"
    return HttpResponseError(response=response)


def test_wait_for_data_plane_access_succeeds_immediately():
    client = MagicMock()
    client.list_configuration_settings.return_value = iter([])

    with patch("conftest.time.sleep") as sleep:
        _wait_for_data_plane_access(client)

    sleep.assert_not_called()


def test_wait_for_data_plane_access_retries_forbidden_response():
    client = MagicMock()
    client.list_configuration_settings.side_effect = [_http_error(403), iter([])]

    with patch("conftest.time.sleep") as sleep:
        _wait_for_data_plane_access(client)

    sleep.assert_called_once_with(1)


def test_wait_for_data_plane_access_does_not_retry_other_errors():
    client = MagicMock()
    client.list_configuration_settings.side_effect = _http_error(500)

    with patch("conftest.time.sleep") as sleep, pytest.raises(HttpResponseError):
        _wait_for_data_plane_access(client)

    sleep.assert_not_called()


def test_wait_for_data_plane_access_times_out():
    client = MagicMock()
    client.list_configuration_settings.side_effect = _http_error(403)

    with patch("conftest.time.monotonic", side_effect=[0, 2]), patch("conftest.time.sleep") as sleep, pytest.raises(
        TimeoutError
    ):
        _wait_for_data_plane_access(client, timeout=1)

    sleep.assert_not_called()
