#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import datetime
from base64 import b64encode
from hashlib import sha256
from hmac import HMAC
from urllib.parse import urlencode, quote_plus
import time

from .types import TYPE, VALUE, AMQPTypes
from ._encode import encode_payload


def utc_from_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)


def utc_now():
    return datetime.datetime.now(tz=datetime.timezone.utc)


def encode(value, encoding='UTF-8'):
    return value.encode(encoding) if isinstance(value, str) else value


def generate_sas_token(audience, policy, key, expiry=None):
    """
    Generate a sas token according to the given audience, policy, key and expiry

    :param str audience:
    :param str policy:
    :param str key:
    :param int expiry: abs expiry time
    :rtype: str
    """
    if not expiry:
        expiry = int(time.time()) + 3600  # Default to 1 hour.

    encoded_uri = quote_plus(audience)
    encoded_policy = quote_plus(policy).encode("utf-8")
    encoded_key = key.encode("utf-8")

    ttl = int(expiry)
    sign_key = '%s\n%d' % (encoded_uri, ttl)
    signature = b64encode(HMAC(encoded_key, sign_key.encode('utf-8'), sha256).digest())
    result = {
        'sr': audience,
        'sig': signature,
        'se': str(ttl)
    }
    if policy:
        result['skn'] = encoded_policy
    return 'SharedAccessSignature ' + urlencode(result)


def add_batch(batch, message):
    # Add a message to a batch
    output = bytearray()
    encode_payload(output, message)
    batch[5].append(output)


def encode_str(data, encoding='utf-8'):
    try:
        return data.encode(encoding)
    except AttributeError:
        return data


def normalized_data_body(data, **kwargs):
    # A helper method to normalize input into AMQP Data Body format
    encoding = kwargs.get("encoding", "utf-8")
    if isinstance(data, list):
        return [encode_str(item, encoding) for item in data]
    return [encode_str(data, encoding)]


def normalized_sequence_body(sequence):
    # A helper method to normalize input into AMQP Sequence Body format
    if isinstance(sequence, list) and all([isinstance(b, list) for b in sequence]):
        return sequence
    if isinstance(sequence, list):
        return [sequence]


def get_message_encoded_size(message):
    output = bytearray()
    encode_payload(output, message)
    return len(output)
