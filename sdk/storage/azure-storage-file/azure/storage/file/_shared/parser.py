# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys

from .models import UserDelegationKey

if sys.version_info < (3,):
    def _str(value):
        if isinstance(value, unicode):  # pylint: disable=undefined-variable
            return value.encode('utf-8')

        return str(value)
else:
    _str = str


def _to_utc_datetime(value):
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')


def _parse_to_internal_user_delegation_key(service_user_delegation_key):
    internal_user_delegation_key = UserDelegationKey()
    internal_user_delegation_key.signed_oid = service_user_delegation_key.signed_oid
    internal_user_delegation_key.signed_tid = service_user_delegation_key.signed_tid
    internal_user_delegation_key.signed_start = _to_utc_datetime(service_user_delegation_key.signed_start)
    internal_user_delegation_key.signed_expiry = _to_utc_datetime(service_user_delegation_key.signed_expiry)
    internal_user_delegation_key.signed_service = service_user_delegation_key.signed_service
    internal_user_delegation_key.signed_version = service_user_delegation_key.signed_version
    internal_user_delegation_key.value = service_user_delegation_key.value
    return internal_user_delegation_key
