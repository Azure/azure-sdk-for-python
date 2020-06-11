#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# pylint: disable=super-init-not-called,arguments-differ

import six
from uamqp import c_uamqp, compat, utils


class AMQPType(object):
    """Base type for specific AMQP encoded type definitions.

    :ivar value: The Python value of the AMQP type.
    :ivar c_data: The C AMQP encoded object.
    """

    def __init__(self, value):
        self._c_type = self._c_wrapper(value)

    @property
    def value(self):
        return self._c_type.value

    @property
    def c_data(self):
        return self._c_type

    def _c_wrapper(self, value):
        raise NotImplementedError()


class AMQPSymbol(AMQPType):
    """An AMQP symbol object.

    :ivar value: The Python value of the AMQP type.
    :vartype value: bytes
    :ivar c_data: The C AMQP encoded object.
    :vartype c_data: c_uamqp.SymbolValue
    :param value: The value to encode as an AMQP symbol.
    :type value: bytes or str
    :param encoding: The encoding to be used if a str is provided.
     The default is 'UTF-8'.
    :type encoding: str
    """

    def __init__(self, value, encoding='UTF-8'):
        self._c_type = self._c_wrapper(value, encoding)

    def _c_wrapper(self, value, encoding='UTF-8'):
        value = value.encode(encoding) if isinstance(value, six.text_type) else value
        return c_uamqp.symbol_value(value)


class AMQPChar(AMQPType):
    """An AMQP char object.

    :ivar value: The Python value of the AMQP type.
    :vartype value: bytes
    :ivar c_data: The C AMQP encoded object.
    :vartype c_data: c_uamqp.CharValue
    :param value: The value to encode as an AMQP char.
    :type value: bytes or str
    :param encoding: The encoding to be used if a str is provided.
     The default is 'UTF-8'.
    :type encoding: str
    """

    def __init__(self, value, encoding='UTF-8'):
        self._c_type = self._c_wrapper(value, encoding)

    def _c_wrapper(self, value, encoding='UTF-8'):
        if len(value) > 1:
            raise ValueError("Value must be a single character.")
        value = value.encode(encoding) if isinstance(value, six.text_type) else value
        return c_uamqp.char_value(value)


class AMQPLong(AMQPType):
    """An AMQP long object.

    :ivar value: The Python value of the AMQP type.
    :vartype value: int
    :ivar c_data: The C AMQP encoded object.
    :vartype c_data: uamqp.c_uamqp.LongValue
    :param value: The value to encode as an AMQP ulong.
    :type value: int
    :raises: ValueError if value is not within allowed range.
    """

    def _c_wrapper(self, value):
        try:
            return c_uamqp.long_value(compat.long(value))
        except TypeError:
            raise ValueError("Value must be an integer")
        except OverflowError:
            raise ValueError("Value {} is too large for a Long value.".format(value))


class AMQPuLong(AMQPType):
    """An AMQP unsigned long object.

    :ivar value: The Python value of the AMQP uLong.
    :vartype value: int
    :ivar c_data: The C AMQP encoded object.
    :vartype c_data: uamqp.c_uamqp.ULongValue
    :param value: The value to encode as an AMQP unsigned Long.
    :type value: list
    :raises: ValueError if value is not within allowed range.
    """

    def _c_wrapper(self, value):
        try:
            return c_uamqp.ulong_value(compat.long(value))
        except TypeError:
            raise ValueError("Value must be an integer")
        except OverflowError:
            raise ValueError("Value {} is too large for an unsigned Long value.".format(value))


class AMQPByte(AMQPType):
    """An AMQP byte object.

    :ivar value: The Python value of the AMQP type.
    :vartype value: int
    :ivar c_data: The C AMQP encoded object.
    :vartype c_data: uamqp.c_uamqp.ByteValue
    :param value: The value to encode as an AMQP ulong.
    :type value: int
    :raises: ValueError if value is not within allowed range.
    """

    def _c_wrapper(self, value):
        try:
            return c_uamqp.byte_value(int(value))
        except TypeError:
            raise ValueError("Value must be an integer")
        except OverflowError:
            raise ValueError("Value {} is too large for a Byte value.".format(value))


class AMQPuByte(AMQPType):
    """An AMQP unsigned byte object.

    :ivar value: The Python value of the AMQP uByte.
    :vartype value: int
    :ivar c_data: The C AMQP encoded object.
    :vartype c_data: uamqp.c_uamqp.UByteValue
    :param value: The value to encode as an AMQP unsigned Byte.
    :type value: list
    :raises: ValueError if value is not within allowed range.
    """

    def _c_wrapper(self, value):
        try:
            return c_uamqp.ubyte_value(int(value))
        except TypeError:
            raise ValueError("Value must be an integer")
        except OverflowError:
            raise ValueError("Value {} is too large for an unsigned Byte value.".format(value))


class AMQPInt(AMQPType):
    """An AMQP int object.

    :ivar value: The Python value of the AMQP type.
    :vartype value: int
    :ivar c_data: The C AMQP encoded object.
    :vartype c_data: uamqp.c_uamqp.IntValue
    :param value: The value to encode as an AMQP int.
    :type value: int
    :raises: ValueError if value is not within allowed range.
    """

    def _c_wrapper(self, value):
        try:
            return c_uamqp.int_value(int(value))
        except TypeError:
            raise ValueError("Value must be an integer")
        except OverflowError:
            raise ValueError("Value {} is too large for an Int value.".format(value))


class AMQPuInt(AMQPType):
    """An AMQP unsigned int object.

    :ivar value: The Python value of the AMQP uInt.
    :vartype value: int
    :ivar c_data: The C AMQP encoded object.
    :vartype c_data: uamqp.c_uamqp.UIntValue
    :param value: The value to encode as an AMQP unsigned int.
    :type value: list
    :raises: ValueError if value is not within allowed range.
    """

    def _c_wrapper(self, value):
        try:
            return c_uamqp.uint_value(int(value))
        except TypeError:
            raise ValueError("Value must be an integer")
        except OverflowError:
            raise ValueError("Value {} is too large for an unsigned int value.".format(value))


class AMQPArray(AMQPType):
    """An AMQP Array object. All the values in the array
    must be of the same type.

    :ivar value: The Python values of the AMQP array.
    :vartype value: list
    :ivar c_data: The C AMQP encoded object.
    :vartype c_data: uamqp.c_uamqp.ArrayValue
    :param value: The value to encode as an AMQP array.
    :type value: int
    :raises: ValueError if all values are not the same type.
    """

    def _c_wrapper(self, value_array):
        if value_array:
            value_type = type(value_array[0])
            if not all(isinstance(x, value_type) for x in value_array):
                raise ValueError("All Array values must be the same type.")

        c_array = c_uamqp.array_value()
        for value in value_array:
            c_array.append(utils.data_factory(value))
        return c_array


class AMQPDescribed(AMQPType):
    """An AMQP Described object. All the values in the array
    must be of the same type.

    :ivar value: The Python values of the AMQP array.
    :vartype value: list
    :ivar c_data: The C AMQP encoded object.
    :vartype c_data: uamqp.c_uamqp.ArrayValue
    :param value: The value to encode as an AMQP array.
    :type value: int
    :raises: ValueError if all values are not the same type.
    """

    def __init__(self, descriptor, described):
        self._c_type = self._c_wrapper(descriptor, described)

    def _c_wrapper(self, descriptor, described):
        descriptor = utils.data_factory(descriptor)
        described = utils.data_factory(described)
        return c_uamqp.described_value(descriptor, described)
