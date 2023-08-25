#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from typing_extensions import Generic, TypeVar, TypedDict
from enum import Enum


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
    type: AMQPType
    value: AMQPValue


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
