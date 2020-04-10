# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import sys
import datetime
import logging
import threading
import time
import functools
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

from uamqp import authentication

from ..exceptions import AutoLockRenewFailed, AutoLockRenewTimeout
from .._version import VERSION as sdk_version
from .constants import (
    JWT_TOKEN_SCOPE,
    TOKEN_TYPE_JWT,
    TOKEN_TYPE_SASTOKEN
)

_log = logging.getLogger(__name__)


class UTC(datetime.tzinfo):
    """Time Zone info for handling UTC"""

    def utcoffset(self, dt):
        """UTF offset for UTC is 0."""
        return datetime.timedelta(0)

    def tzname(self, dt):
        """Timestamp representation."""
        return "Z"

    def dst(self, dt):
        """No daylight saving for UTC."""
        return datetime.timedelta(hours=1)


try:
    from datetime import timezone  # pylint: disable=ungrouped-imports

    TZ_UTC = timezone.utc  # type: ignore
except ImportError:
    TZ_UTC = UTC()  # type: ignore


def utc_from_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, tz=TZ_UTC)


def utc_now():
    return datetime.datetime.now(tz=TZ_UTC)


def get_running_loop():
    try:
        import asyncio  # pylint: disable=import-error
        return asyncio.get_running_loop()
    except AttributeError:  # 3.5 / 3.6
        loop = None
        try:
            loop = asyncio._get_running_loop()  # pylint: disable=protected-access
        except AttributeError:
            _log.warning('This version of Python is deprecated, please upgrade to >= v3.5.3')
        if loop is None:
            _log.warning('No running event loop')
            loop = asyncio.get_event_loop()
        return loop
    except RuntimeError:
        # For backwards compatibility, create new event loop
        _log.warning('No running event loop')
        return asyncio.get_event_loop()


def parse_conn_str(conn_str):
    endpoint = None
    shared_access_key_name = None
    shared_access_key = None
    entity_path = None
    for element in conn_str.split(';'):
        key, _, value = element.partition('=')
        if key.lower() == 'endpoint':
            endpoint = value.rstrip('/')
        elif key.lower() == 'sharedaccesskeyname':
            shared_access_key_name = value
        elif key.lower() == 'sharedaccesskey':
            shared_access_key = value
        elif key.lower() == 'entitypath':
            entity_path = value
    if not all([endpoint, shared_access_key_name, shared_access_key]):
        raise ValueError("Invalid connection string")
    return endpoint, shared_access_key_name, shared_access_key, entity_path


def build_uri(address, entity):
    parsed = urlparse(address)
    if parsed.path:
        return address
    if not entity:
        raise ValueError("No Service Bus entity specified")
    address += "/" + str(entity)
    return address


def create_properties():
    properties = {}
    properties["product"] = "servicebus.python"
    properties["version"] = sdk_version
    properties["framework"] = "Python {}.{}.{}".format(*sys.version_info[0:3])
    properties["platform"] = sys.platform
    return properties


def renewable_start_time(renewable):
    try:
        return renewable.received_timestamp_utc
    except AttributeError:
        pass
    try:
        return renewable._session_start  # pylint: disable=protected-access
    except AttributeError:
        raise TypeError("Registered object is not renewable.")


def create_authentication(client):
    # pylint: disable=protected-access
    try:
        # ignore mypy's warning because token_type is Optional
        token_type = client._credential.token_type  # type: ignore
    except AttributeError:
        token_type = TOKEN_TYPE_JWT
    if token_type == TOKEN_TYPE_SASTOKEN:
        auth = authentication.JWTTokenAuth(
            client._auth_uri,
            client._auth_uri,
            functools.partial(client._credential.get_token, client._auth_uri),
            token_type=token_type,
            timeout=client._config.auth_timeout,
            http_proxy=client._config.http_proxy,
            transport_type=client._config.transport_type,
        )
        auth.update_token()
        return auth
    return authentication.JWTTokenAuth(
        client._auth_uri,
        client._auth_uri,
        functools.partial(client._credential.get_token, JWT_TOKEN_SCOPE),
        token_type=token_type,
        timeout=client._config.auth_timeout,
        http_proxy=client._config.http_proxy,
        transport_type=client._config.transport_type,
    )


class AutoLockRenew(object):
    """Auto renew locks for messages and sessions using a background thread pool.

    :param executor: A user-specified thread pool. This cannot be combined with
     setting `max_workers`.
    :type executor: ~concurrent.futures.ThreadPoolExecutor
    :param max_workers: Specify the maximum workers in the thread pool. If not
     specified the number used will be derived from the core count of the environment.
     This cannot be combined with `executor`.
    :type max_workers: int

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START auto_lock_renew_message_sync]
            :end-before: [END auto_lock_renew_message_sync]
            :language: python
            :dedent: 4
            :caption: Automatically renew a message lock

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START auto_lock_renew_session_sync]
            :end-before: [END auto_lock_renew_session_sync]
            :language: python
            :dedent: 4
            :caption: Automatically renew a session lock

    """

    def __init__(self, executor=None, max_workers=None):
        self.executor = executor or ThreadPoolExecutor(max_workers=max_workers)
        self._shutdown = threading.Event()
        self.sleep_time = 1
        self.renew_period = 10

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.shutdown()

    def _renewable(self, renewable):
        if self._shutdown.is_set():
            return False
        if hasattr(renewable, 'settled') and renewable.settled:
            return False
        if renewable.expired:
            return False
        return True

    def _auto_lock_renew(self, renewable, starttime, timeout):
        _log.debug("Running lock auto-renew thread for %r seconds", timeout)
        try:
            while self._renewable(renewable):
                if (utc_now() - starttime) >= datetime.timedelta(seconds=timeout):
                    _log.debug("Reached auto lock renew timeout - letting lock expire.")
                    raise AutoLockRenewTimeout("Auto-renew period ({} seconds) elapsed.".format(timeout))
                if (renewable.locked_until_utc - utc_now()) <= datetime.timedelta(seconds=self.renew_period):
                    _log.debug("%r seconds or less until lock expires - auto renewing.", self.renew_period)
                    renewable.renew_lock()
                time.sleep(self.sleep_time)
        except AutoLockRenewTimeout as e:
            renewable.auto_renew_error = e
        except Exception as e:  # pylint: disable=broad-except
            _log.debug("Failed to auto-renew lock: %r. Closing thread.", e)
            error = AutoLockRenewFailed(
                "Failed to auto-renew lock",
                inner_exception=e)
            renewable.auto_renew_error = error

    def register(self, renewable, timeout=300):
        """Register a renewable entity for automatic lock renewal.

        :param renewable: A locked entity that needs to be renewed.
        :type renewable: ~azure.servicebus.ReceivedMessage or
         ~azure.servicebus.Session
        :param float timeout: A time in seconds that the lock should be maintained for.
         Default value is 300 (5 minutes).
        """
        starttime = renewable_start_time(renewable)
        self.executor.submit(self._auto_lock_renew, renewable, starttime, timeout)

    def shutdown(self, wait=True):
        """Shutdown the thread pool to clean up any remaining lock renewal threads.

        :param wait: Whether to block until thread pool has shutdown. Default is `True`.
        :type wait: bool
        """
        self.executor.shutdown(wait=wait)
