#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from enum import Enum
from uuid import uuid
from datetime import datetime
from typing import (
    NamedTuple,
    Generic,
    Literal,
    TypeVar,
    Union,
    Dict,
    List,
    Optional,
    Tuple
)
from typing_extensions import TypedDict



TYPE = 'TYPE'
VALUE = 'VALUE'

AMQP_PRIMATIVE_TYPES = Union[int, str, bytes, None, bool, float, uuid, datetime]
AMQP_STRUCTURED_TYPES = Union[
    AMQP_PRIMATIVE_TYPES,
    Dict[AMQP_PRIMATIVE_TYPES, AMQP_PRIMATIVE_TYPES],
    List[AMQP_PRIMATIVE_TYPES]
]


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


class FieldDefinition(Enum):
    fields = "fields"
    annotations = "annotations"
    message_id = "message-id"
    app_properties = "application-properties"
    node_properties = "node-properties"
    filter_set = "filter-set"


class ObjDefinition(Enum):
    source = "source"
    target = "target"
    delivery_state = "delivery-state"
    error = "error"


class FIELD(NamedTuple):
    type: Union[AMQPTypes, FieldDefinition, ObjDefinition]
    multiple: bool


class Performative(NamedTuple):
    """Base for performatives."""
    _code: int = 0x00000000
    _definition: List[Optional[FIELD]] = []


T = TypeVar('T', AMQPTypes)
V = TypeVar('V', AMQP_STRUCTURED_TYPES)


class AMQPDefinedType(TypedDict, Generic[T, V]):
    """A wrapper for data that is going to be passed into the AMQP encoder."""
    TYPE: Optional[T]
    VALUE: Optional[V]


class AMQPFieldType(TypedDict, Generic[V]):
    """A wrapper for data that will be encoded as AMQP fields."""
    TYPE: Literal[AMQPTypes.map]
    VALUE: List[Tuple[AMQPDefinedType[Literal[AMQPTypes.symbol], bytes], V]]


class AMQPAnnotationsType(TypedDict, Generic[V]):
    """A wrapper for data that will be encoded as AMQP annotations."""
    TYPE: Literal[AMQPTypes.map]
    VALUE: List[Tuple[AMQPDefinedType[Union[Literal[AMQPTypes.symbol], Literal[AMQPTypes.ulong]], Union[int, bytes]], V]]


NullDefinedType = AMQPDefinedType[Literal[AMQPTypes.null], None]
