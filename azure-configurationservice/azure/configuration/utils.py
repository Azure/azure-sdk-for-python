# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from datetime import datetime, timezone


def get_endpoint_from_connection_string(connection_string):
    endpoint, _, _ = parse_connection_string(connection_string)
    return endpoint


def parse_connection_string(connection_string):
    # connection_string looks like Endpoint=https://xxxxx;Id=xxxxx;Secret=xxxx
    segments = connection_string.split(';')
    if len(segments) != 3:
        raise ValueError('Invalid connection string.')
    
    endpoint = ''
    id_ = ''
    secret = ''
    for segment in segments:
        segment = segment.strip()
        if segment.startswith('Endpoint'):
            endpoint = str(segment[17:])
        elif segment.startswith('Id'):
            id_ = str(segment[3:])
        elif segment.startswith('Secret'):
            secret = str(segment[7:])
        else:
            raise ValueError('Invalid connection string.')
    
    if not endpoint or not id_ or not secret:
        raise ValueError('Invalid connection string.')

    return endpoint, id_, secret


def get_current_utc_time():
    return str(datetime.now(timezone.utc).strftime("%b, %d %Y %H:%M:%S ")) + "GMT"