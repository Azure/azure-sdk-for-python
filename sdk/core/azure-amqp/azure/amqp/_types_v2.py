#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from typing_extensions import (
    Generic,
    TypeVar,
    TypedDict,
    AnyStr,
    Union,
    Mapping,
    MutableSequence,
    Tuple,
    List,
    Protocol,
    NotRequired,
    runtime_checkable
)
import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass


try:
    dataclass_decorator = dataclass(order=True, slots=True)
except TypeError:
    # slots not supported < Python 3.10
    dataclass_decorator = dataclass(order=True)


TYPE_KEY = '_amqp_type'
VALUE_KEY = '_amqp_value'


class AMQPTypes(Enum):
    null = 'NULL'
    boolean = 'BOOL'
    ubyte = 'UBYTE'
    byte = 'BYTE'
    ushort = 'USHORT'
    short = 'SHORT'
    uint = 'UINT'
    int = 'INT'
    ulong = 'ULONG'
    long = 'LONG'
    float = 'FLOAT'
    double = 'DOUBLE'
    timestamp = 'TIMESTAMP'
    uuid = 'UUID'
    binary = 'BINARY'
    string = 'STRING'
    symbol = 'SYMBOL'
    list = 'LIST'
    map = 'MAP'
    array = 'ARRAY'
    described = 'DESCRIBED'
    fields = "FIELDS"
    annotations = "ANNOTATIONS"
    message_id = "MESSAGE_ID"
    app_properties = "APPLICATION_PROPERTIES"
    node_properties = "NODE_PROPERTIES"
    filter_set = "FILTER_SET"


AMQPType = TypeVar("AMQPType", bound=AMQPTypes)
AMQPValue = TypeVar("AMQPValue")


class AMQPDefinition(TypedDict, Generic[AMQPType, AMQPValue]):
    _amqp_type: AMQPType
    _amqp_value: AMQPValue


AMQP_BASIC_TYPES = Union[None, bool, str, bytes, bytearray, float, int, uuid.UUID, datetime]
AMQP_FULL_TYPES = Union[
    AMQP_BASIC_TYPES,
    Mapping[Union[AMQPDefinition, AMQP_BASIC_TYPES], "AMQP_FULL_TYPES"],
    MutableSequence["AMQP_FULL_TYPES"],
    Tuple[Union[AMQPDefinition, AMQP_BASIC_TYPES], "AMQP_FULL_TYPES"]
]
AMQP_DEFINED_TYPES = Union[AMQP_FULL_TYPES, AMQPDefinition]


class ConstructorBytes:  # pylint: disable=no-init
    null = b'\x40'
    bool = b'\x56'
    bool_true = b'\x41'
    bool_false = b'\x42'
    ubyte = b'\x50'
    byte = b'\x51'
    ushort = b'\x60'
    short = b'\x61'
    uint_0 = b'\x43'
    uint_small = b'\x52'
    int_small = b'\x54'
    uint_large = b'\x70'
    int_large = b'\x71'
    ulong_0 = b'\x44'
    ulong_small = b'\x53'
    long_small = b'\x55'
    ulong_large = b'\x80'
    long_large = b'\x81'
    float = b'\x72'
    double = b'\x82'
    timestamp = b'\x83'
    uuid = b'\x98'
    binary_small = b'\xA0'
    binary_large = b'\xB0'
    string_small = b'\xA1'
    string_large = b'\xB1'
    symbol_small = b'\xA3'
    symbol_large = b'\xB3'
    list_0 = b'\x45'
    list_small = b'\xC0'
    list_large = b'\xD0'
    map_small = b'\xC1'
    map_large = b'\xD1'
    array_small = b'\xE0'
    array_large = b'\xF0'
    descriptor = b'\x00'


AMQP_NONE = {TYPE_KEY: AMQPTypes.null, VALUE_KEY: None}


def amqp_long_value(value: int) -> AMQPDefinition[AMQPTypes.long, int]:
    return {TYPE_KEY: AMQPTypes.long, VALUE_KEY: value}


def amqp_uint_value(value: int) -> AMQPDefinition[AMQPTypes.uint, int]:
    return {TYPE_KEY: AMQPTypes.uint, VALUE_KEY: value}


def amqp_string_value(value: AnyStr) -> AMQPDefinition[AMQPTypes.string, AnyStr]:
    return {TYPE_KEY: AMQPTypes.string, VALUE_KEY: value}


def amqp_symbol_value(value: AnyStr) -> AMQPDefinition[AMQPTypes.symbol, AnyStr]:
    return {TYPE_KEY: AMQPTypes.symbol, VALUE_KEY: value}


def amqp_array_value(value: MutableSequence[AMQP_DEFINED_TYPES]):
    return {TYPE_KEY: AMQPTypes.array, VALUE_KEY: value}

@runtime_checkable
class Performative(Protocol):
    _code: int

    def _describe(self) -> AMQPDefinition[AMQPTypes.described, Tuple[AMQPDefinition[AMQPTypes.ulong, int], AMQPDefinition[AMQPTypes.list, List[AMQPDefinition]]]]:
        ...


__all__ = [
    'TYPE_KEY',
    'VALUE_KEY',
    'AMQP_NONE',
    'AMQP_BASIC_TYPES',
    'AMQP_FULL_TYPES',
    'AMQP_DEFINED_TYPES',
    'AMQPDefinition',
    'AMQPTypes',
    'Performative',
    'ConstructorBytes',
    'amqp_long_value',
    'amqp_array_value',
    'amqp_string_value',
    'amqp_symbol_value',
    'amqp_uint_value',
    'dataclass_decorator'
]
