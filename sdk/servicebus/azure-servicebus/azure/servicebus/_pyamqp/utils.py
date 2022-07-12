#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import datetime
from base64 import b64encode
from hashlib import sha256
from hmac import HMAC
from typing import List, Union, Literal, Optional
from urllib.parse import urlencode, quote_plus
import time

from .types import AMQP_PRIMATIVE_TYPES, TYPE, VALUE, AMQPTypes, AMQPDefinedType
from ._encode import encode_payload
from .message import Message


TZ_UTC = datetime.timezone.utc


def utc_from_timestamp(timestamp: str) -> datetime.datetime:
    """Convert string timestamp to datetime.datetime with UTC timezone."""
    return datetime.datetime.fromtimestamp(timestamp, tz=TZ_UTC)


def utc_now() -> datetime.datetime:
    """Get current datetime.datetime with UTC timezone"""
    return datetime.datetime.now(tz=TZ_UTC)


def generate_sas_token(
        audience: str,
        policy: str,
        key: str,
        expiry: Optional[int] = None
    ) -> str:
    """Generate a sas token according to the given audience, policy, key and expiry.

    :param str audience:
    :param str policy:
    :param str key:
    :param int expiry: Absolute expiry time.
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


def add_batch(batch: Message, message: Message) -> None:
    """Add a message to a batch.

    This will encode the message and add the bytes to the array in the
    data field of the message.
    
    :param ~pyamqp.Message batch: The batch message to add to.
    :param ~pyamqp.Message message: The message to append to the batch.
    """
    output = bytearray()
    encode_payload(output, message)
    batch[5].append(output)


def _encode_str(data: Union[str, bytes], encoding: str) -> bytes:
    """Encode a string with supplied encoding, otherwise return data unaltered.
    
    :param Union[str, bytes] data: A segment of an AMQP data payload. Either string or bytes.
    :param str encoding: The encoding to use for any string data.
    :rtype: bytes
    """
    try:
        return data.encode(encoding)
    except AttributeError:
        return data


def normalized_data_body(
        data: Union[str, bytes, List[Union[str, bytes]]],
        **kwargs
    ) -> List[bytes]:
    """A helper method to normalize input into AMQP Data Body format.

    :param data: An AMQP data body to be formatted into a list of bytes. This might be bytes, string
     or already formatted into a list of strings/bytes.
    :keyword str encoding: The encoding to use for any string data. Default is UTF-8.
    :rtype: List[bytes]
    """
    encoding = kwargs.get("encoding", "utf-8")
    if isinstance(data, list):
        return [_encode_str(item, encoding) for item in data]
    else:
        return [_encode_str(data, encoding)]


def normalized_sequence_body(sequence):
    """A helper method to normalize input into AMQP Sequence Body format.
    """
    # TODO: Why is this returning a list of lists?
    if isinstance(sequence, list) and all([isinstance(b, list) for b in sequence]):
        return sequence
    elif isinstance(sequence, list):
        return [sequence]


def get_message_encoded_size(message: Message) -> int:
    """Get the size of a message once it has been encoded to an AMQP payload.
    
    :param ~pyamqp.Message message: The message to get the length of.
    :rtype: int
    """
    output = bytearray()
    encode_payload(output, message)
    return len(output)


def amqp_long_value(value: int) -> AMQPDefinedType[Literal[AMQPTypes.long], int]:
    """A helper method to wrap a Python int as AMQP long.

    :param int value: An integer to be defined as a long.
    :rtype: Dict[str, Union[Literal[AMQPTypes.long], int]]
    """
    # TODO: wrapping one line in a function is expensive, find if there's a better way to do it
    return {TYPE: AMQPTypes.long, VALUE: value}


def amqp_uint_value(value: int) -> AMQPDefinedType[Literal[AMQPTypes.uint], int]:
    """A helper method to wrap a Python int as AMQP uint.

    :param int value: An integer to be defined as a uint.
    :rtype: Dict[str, Union[Literal[AMQPTypes.uint], int]]
    """
    return {TYPE: AMQPTypes.uint, VALUE: value}


def amqp_string_value(value: Union[str, bytes]) -> AMQPDefinedType[Literal[AMQPTypes.string], Union[str, bytes]]:
    """A helper method to wrap a Python string or bytes as an AMQP string.

    This method will not encode string data to bytes, which will happen during
    AMQP encode.

    :param Union[str, bytes] value: Bytes or string or be defined as a string.
    :rtype: Dict[str, Union[Literal[AMQPTypes.string], int]]
    """
    return {TYPE: AMQPTypes.string, VALUE: value}


def amqp_symbol_value(value: Union[str, bytes]) -> AMQPDefinedType[Literal[AMQPTypes.symbol], Union[str, bytes]]:
    """A helper method to wrap a Python string/bytes as AMQP symbol.

    :param int value: An integer to be defined as a long.
    :rtype: Dict[str, Union[Literal[AMQPTypes.symbol], str, bytes]]
    """
    return {TYPE: AMQPTypes.symbol, VALUE: value}


def amqp_array_value(value: List[AMQP_PRIMATIVE_TYPES]) -> AMQPDefinedType[Literal[AMQPTypes.array], List[AMQP_PRIMATIVE_TYPES]]:
    """A helper method to wrap a Python list as an AMQP array.

    :param value: A list of homogeneous primary data types to define as an array.
    :paramtype value: List[AMQP_PRIMATIVE_TYPES]
    :rtype: Dict[str, Union[Literal[AMQPTypes.array], List[AMQP_PRIMATIVE_TYPES]]]
    """
    return {TYPE: AMQPTypes.array, VALUE: value}
