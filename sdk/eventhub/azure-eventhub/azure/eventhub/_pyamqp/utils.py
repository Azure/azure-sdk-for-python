# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import datetime
from base64 import b64encode
from hashlib import sha256
from hmac import HMAC
from urllib.parse import urlencode, quote_plus
import time
from datetime import timezone
from .types import TYPE, VALUE, AMQPTypes
from ._encode import encode_payload

TZ_UTC: timezone = timezone.utc
# Number of seconds between the Unix epoch (1/1/1970) and year 1 CE.
# This is the lowest value that can be represented by an AMQP timestamp.
CE_ZERO_SECONDS: int = -62_135_596_800


def utc_from_timestamp(timestamp: float) -> datetime.datetime:
    """
    :param float timestamp: Timestamp in seconds to be converted to datetime.
    :rtype: datetime.datetime
    :returns: A datetime object representing the timestamp in UTC.
    """
    # The AMQP timestamp is the number of seconds since the Unix epoch.
    # AMQP brokers represent the lowest value as -62_135_596_800 (the
    # number of seconds between the Unix epoch (1/1/1970) and year 1 CE) as
    # a sentinel for a time which is not set.
    if timestamp == CE_ZERO_SECONDS:
        return datetime.datetime.min.replace(tzinfo=TZ_UTC)
    return datetime.datetime.fromtimestamp(timestamp, tz=TZ_UTC)


def utc_now():
    return datetime.datetime.now(tz=TZ_UTC)


def encode(value, encoding="UTF-8"):
    return value.encode(encoding) if isinstance(value, str) else value


def generate_sas_token(audience, policy, key, expiry=None):
    """
    Generate a sas token according to the given audience, policy, key and expiry

    :param str audience:
    :param str policy:
    :param str key:
    :param int expiry: abs expiry time
    :return: A sas token
    :rtype: str
    """
    if not expiry:
        expiry = int(time.time()) + 3600  # Default to 1 hour.

    encoded_uri = quote_plus(audience)
    encoded_policy = quote_plus(policy).encode("utf-8")
    encoded_key = key.encode("utf-8")

    ttl = int(expiry)
    sign_key = "%s\n%d" % (encoded_uri, ttl)
    signature = b64encode(HMAC(encoded_key, sign_key.encode("utf-8"), sha256).digest())
    result = {"sr": audience, "sig": signature, "se": str(ttl)}
    if policy:
        result["skn"] = encoded_policy
    return "SharedAccessSignature " + urlencode(result)


def add_batch(batch, message):
    # Add a message to a batch
    output = bytearray()
    encode_payload(output, message)
    batch[5].append(output)


def encode_str(data, encoding="utf-8"):
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


def normalized_sequence_body(sequence):  # pylint:disable=inconsistent-return-statements
    # A helper method to normalize input into AMQP Sequence Body format
    if isinstance(sequence, list) and all((isinstance(b, list) for b in sequence)):
        return sequence
    if isinstance(sequence, list):
        return [sequence]


def get_message_encoded_size(message):
    output = bytearray()
    encode_payload(output, message)
    return len(output)


def amqp_long_value(value):
    # A helper method to wrap a Python int as AMQP long
    # TODO: wrapping one line in a function is expensive, find if there's a better way to do it
    return {TYPE: AMQPTypes.long, VALUE: value}


def amqp_uint_value(value):
    # A helper method to wrap a Python int as AMQP uint
    return {TYPE: AMQPTypes.uint, VALUE: value}


def amqp_string_value(value):
    return {TYPE: AMQPTypes.string, VALUE: value}


def amqp_symbol_value(value):
    return {TYPE: AMQPTypes.symbol, VALUE: value}


def amqp_array_value(value):
    return {TYPE: AMQPTypes.array, VALUE: value}
