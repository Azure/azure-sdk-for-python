#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging

import six
from uamqp import c_uamqp, compat, constants, utils

_logger = logging.getLogger(__name__)


class Address(object):
    """Represents an AMQP endpoint.

    :ivar address: The endpoint URL.
    :vartype address: str
    :ivar durable: Whether the endpoint is durable.
    :vartype: bool
    :ivar expiry_policy: The endpoint expiry policy
    :ivar timeout: The endpoint timeout in seconds.
    :vartype timeout: float
    :ivar dynamic: Whether the endpoint is dynamic.
    :vartype dynamic: bool
    :ivar distribution_mode: The endpoint distribution mode.
    :vartype distribution_mode: str
    :param address: An AMQP endpoint URL.
    :type address: str or bytes
    :param encoding: The encoding used if address is supplied
     as a str rather than bytes. Default is UTF-8.
    """

    def __init__(self, address, encoding='UTF-8'):
        address = address.encode(encoding) if isinstance(address, six.text_type) else address
        self.parsed_address = self._validate_address(address)
        self._encoding = encoding
        self._address = None
        addr = self.parsed_address.path
        if self.parsed_address.hostname:
            addr = self.parsed_address.hostname + addr
        if self.parsed_address.scheme:
            addr = self.parsed_address.scheme + b"://" + addr
        self._c_address = c_uamqp.string_value(addr)

    @classmethod
    def from_c_obj(cls, c_value, encoding='UTF-8'):
        address = c_value.address
        py_obj = cls(address, encoding=encoding)
        py_obj._address = c_value  # pylint: disable=protected-access
        return py_obj


    def __repr__(self):
        """Get the Address as a URL.

        :rtype: bytes
        """
        return self.parsed_address.geturl()

    def __str__(self):
        """Get the Address as a URL.

        :rtype: str
        """
        return self.parsed_address.geturl().decode(self._encoding)

    @property
    def hostname(self):
        return self.parsed_address.hostname.decode(self._encoding)

    @property
    def scheme(self):
        return self.parsed_address.scheme.decode(self._encoding)

    @property
    def username(self):
        if self.parsed_address.username:
            return self.parsed_address.username.decode(self._encoding)
        return None

    @property
    def password(self):
        if self.parsed_address.password:
            return self.parsed_address.password.decode(self._encoding)
        return None

    @property
    def address(self):
        return self._address.address.decode(self._encoding)

    @property
    def durable(self):
        return self._address.durable

    @durable.setter
    def durable(self, value):
        self._address.durable = value

    @property
    def expiry_policy(self):
        return self._address.expiry_policy

    @expiry_policy.setter
    def expiry_policy(self, value):
        self._address.expiry_policy = value

    @property
    def timeout(self):
        return self._address.timeout

    @timeout.setter
    def timeout(self, value):
        self._address.timeout = value

    @property
    def dynamic(self):
        return self._address.dynamic

    @dynamic.setter
    def dynamic(self, value):
        self._address.dynamic = value

    @property
    def distribution_mode(self):
        return self._address.distribution_mode.decode(self._encoding)

    @distribution_mode.setter
    def distribution_mode(self, value):
        mode = value.encode(self._encoding) if isinstance(value, six.text_type) else value
        self._address.distribution_mode = mode

    def _validate_address(self, address):
        """Confirm that supplied address is a valid URL and
        has an `amqp` or `amqps` scheme.

        :param address: The endpiont URL.
        :type address: str
        :rtype: ~urllib.parse.ParseResult
        """
        parsed = compat.urlparse(address)
        if not parsed.path:
            raise ValueError("Invalid {} address: {}".format(
                self.__class__.__name__, parsed))
        return parsed


class Source(Address):
    """Represents an AMQP Source endpoint.

    :ivar address: The endpoint URL.
    :vartype address: str
    :ivar durable: Whether the endpoint is durable.
    :vartype: bool
    :ivar expiry_policy: The endpoint expiry policy
    :ivar timeout: The endpoint timeout in seconds.
    :vartype timeout: float
    :ivar dynamic: Whether the endpoint is dynamic.
    :vartype dynamic: bool
    :ivar distribution_mode: The endpoint distribution mode.
    :vartype distribution_mode: str

    :param address: An AMQP endpoint URL.
    :type address: str or bytes
    :param encoding: The encoding used if address is supplied
     as a str rather than bytes. Default is UTF-8.
    """

    def __init__(self, address, encoding='UTF-8'):
        super(Source, self).__init__(address, encoding)
        self.filter_key = constants.STRING_FILTER
        self._address = c_uamqp.create_source()
        self._address.address = self._c_address

    def get_filter(self, name=constants.STRING_FILTER):
        """Get the filter on the source.

        :param name: The name of the filter. This will be encoded as
         an AMQP Symbol. By default this is set to b'apache.org:selector-filter:string'.
        :type name: bytes
        """
        try:
            filter_key = c_uamqp.symbol_value(name)
            return self._address.filter_set[filter_key].value
        except (TypeError, KeyError):
            return None

    def set_filter(self, value, name=constants.STRING_FILTER, descriptor=constants.STRING_FILTER):
        """Set a filter on the endpoint. Only one filter
        can be applied to an endpoint.

        :param value: The filter to apply to the endpoint. Set to None for a NULL filter.
        :type value: bytes or str or None
        :param name: The name of the filter. This will be encoded as
         an AMQP Symbol. By default this is set to b'apache.org:selector-filter:string'.
        :type name: bytes
        :param descriptor: The descriptor used if the filter is to be encoded as a described value.
         This will be encoded as an AMQP Symbol. By default this is set to b'apache.org:selector-filter:string'.
         Set to None if the filter should not be encoded as a described value.
        :type descriptor: bytes or None
        """
        value = value.encode(self._encoding) if isinstance(value, six.text_type) else value
        filter_set = c_uamqp.dict_value()
        filter_key = c_uamqp.symbol_value(name)
        filter_value = utils.data_factory(value, encoding=self._encoding)
        if value is not None and descriptor is not None:
            descriptor = c_uamqp.symbol_value(descriptor)
            filter_value = c_uamqp.described_value(descriptor, filter_value)

        filter_set[filter_key] = filter_value
        self._address.filter_set = filter_set


class Target(Address):
    """Represents an AMQP Target endpoint.

    :ivar address: The endpoint URL.
    :vartype address: str
    :ivar durable: Whether the endpoint is durable.
    :vartype: bool
    :ivar expiry_policy: The endpoint expiry policy
    :ivar timeout: The endpoint timeout in seconds.
    :vartype timeout: float
    :ivar dynamic: Whether the endpoint is dynamic.
    :vartype dynamic: bool
    :ivar distribution_mode: The endpoint distribution mode.
    :vartype distribution_mode: str

    :param address: An AMQP endpoint URL.
    :type address: str or bytes
    :param encoding: The encoding used if address is supplied
     as a str rather than bytes. Default is UTF-8.
    """

    def __init__(self, address, encoding='UTF-8'):
        super(Target, self).__init__(address, encoding)
        self._address = c_uamqp.create_target()
        self._address.address = self._c_address
