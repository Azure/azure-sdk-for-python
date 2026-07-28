import socket
from unittest.mock import MagicMock, patch

from azure.eventhub._pyamqp._transport import (
    DEFAULT_SOCKET_SETTINGS,
    _AbstractTransport,
)
from azure.eventhub._pyamqp._platform import KNOWN_TCP_OPTS, SOL_TCP
from azure.eventhub._pyamqp.aio._transport_async import AsyncTransport


def test_get_defaults_returns_only_configured_settings():
    t = _AbstractTransport.__new__(_AbstractTransport)
    result = t._get_tcp_socket_defaults()
    for name, expected_val in DEFAULT_SOCKET_SETTINGS.items():
        if name not in KNOWN_TCP_OPTS:
            continue
        enum = getattr(socket, name, 18 if name == "TCP_USER_TIMEOUT" else None)
        if enum is not None:
            assert enum in result
            assert result[enum] == expected_val
    # no extra keys beyond what DEFAULT_SOCKET_SETTINGS defines
    assert len(result) <= len(DEFAULT_SOCKET_SETTINGS)


def test_get_defaults_skips_platform_unsupported_opts():
    # Simulate a platform (e.g. Windows) that only supports TCP_NODELAY
    t = _AbstractTransport.__new__(_AbstractTransport)
    with patch(
        "azure.eventhub._pyamqp._transport.KNOWN_TCP_OPTS",
        {"TCP_NODELAY"},
    ):
        result = t._get_tcp_socket_defaults()
    assert len(result) == 1
    assert result[socket.TCP_NODELAY] == DEFAULT_SOCKET_SETTINGS["TCP_NODELAY"]


def test_sync_set_socket_options_applies_defaults():
    t = _AbstractTransport.__new__(_AbstractTransport)
    t.sock = MagicMock(spec=socket.socket)
    t._set_socket_options(None)
    defaults = t._get_tcp_socket_defaults()
    assert t.sock.setsockopt.call_count == len(defaults)
    for enum, val in defaults.items():
        t.sock.setsockopt.assert_any_call(SOL_TCP, enum, val)


def test_async_set_socket_options_applies_defaults():
    t = AsyncTransport.__new__(AsyncTransport)
    mock_sock = MagicMock(spec=socket.socket)
    t._set_socket_options(mock_sock, None)
    defaults = t._get_tcp_socket_defaults()
    assert mock_sock.setsockopt.call_count == len(defaults)
    for enum, val in defaults.items():
        mock_sock.setsockopt.assert_any_call(SOL_TCP, enum, val)
