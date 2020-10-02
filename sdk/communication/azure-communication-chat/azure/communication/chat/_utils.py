# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

def _to_utc_datetime(value):
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')
