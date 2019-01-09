#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import sys
import datetime
import logging
import threading
import time
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

from azure.servicebus.common.errors import AutoLockRenewFailed, AutoLockRenewTimeout
from azure.servicebus import __version__ as sdk_version

_log = logging.getLogger(__name__)


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
        return renewable.received_timestamp
    except AttributeError:
        pass
    try:
        return renewable.session_start
    except AttributeError:
        raise TypeError("Registered object is not renewable.")


class AutoLockRenew(object):

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
                if (datetime.datetime.now() - starttime) >= datetime.timedelta(seconds=timeout):
                    _log.debug("Reached auto lock renew timeout - letting lock expire.")
                    raise AutoLockRenewTimeout("Auto-renew period ({} seconds) elapsed.".format(timeout))
                if (renewable.locked_until - datetime.datetime.now()) <= datetime.timedelta(seconds=self.renew_period):
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
        starttime = renewable_start_time(renewable)
        self.executor.submit(self._auto_lock_renew, renewable, starttime, timeout)

    def shutdown(self, wait=True):
        self.executor.shutdown(wait=wait)
