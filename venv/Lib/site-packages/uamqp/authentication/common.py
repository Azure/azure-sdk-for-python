#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# pylint: disable=super-init-not-called,no-self-use

import logging

import certifi
import six
from uamqp import c_uamqp, constants
from uamqp.constants import TransportType

_logger = logging.getLogger(__name__)


class AMQPAuth(object):
    """AMQP authentication mixin.

    :param hostname: The AMQP endpoint hostname.
    :type hostname: str or bytes
    :param port: The TLS port - default for AMQP is 5671.
    :type port: int
    :param verify: The path to a user-defined certificate.
    :type verify: str
    :param http_proxy: HTTP proxy configuration. This should be a dictionary with
     the following keys present: 'proxy_hostname' and 'proxy_port'. Additional optional
     keys are 'username' and 'password'.
    :type http_proxy: dict
    :param transport_type: The transport protocol type - default is ~uamqp.TransportType.Amqp.
     ~uamqp.TransportType.AmqpOverWebsocket is applied when http_proxy is set or the
     transport type is explicitly requested.
    :type transport_type: ~uamqp.TransportType
    :param encoding: The encoding to use if hostname is provided as a str.
     Default is 'UTF-8'.
    :type encoding: str
    """

    def __init__(self, hostname, port=constants.DEFAULT_AMQPS_PORT, verify=None, http_proxy=None,
                 transport_type=TransportType.Amqp, encoding='UTF-8'):
        self._encoding = encoding
        self.hostname = self._encode(hostname)
        self.cert_file = verify
        self.sasl = _SASL()
        self.set_io(self.hostname, port, http_proxy, transport_type)

    def _build_proxy_config(self, hostname, port, proxy_settings):
        config = c_uamqp.HTTPProxyConfig()
        config.hostname = hostname
        config.port = port
        for key, value in proxy_settings.items():
            proxy_settings[key] = self._encode(value)
        config.proxy_hostname = proxy_settings['proxy_hostname']
        config.proxy_port = proxy_settings['proxy_port']
        username = proxy_settings.get('username')
        if username:
            config.username = username
        password = proxy_settings.get('password')
        if password:
            config.password = password
        return config

    def _encode(self, value):
        return value.encode(self._encoding) if isinstance(value, six.text_type) else value

    def set_io(self, hostname, port, http_proxy, transport_type):
        if transport_type == TransportType.AmqpOverWebsocket or http_proxy is not None:
            self.set_wsio(hostname, constants.DEFAULT_AMQP_WSS_PORT, http_proxy)
        else:
            self.set_tlsio(hostname, port)

    def set_wsio(self, hostname, port, http_proxy):
        """Setup the default underlying Web Socket IO layer.

        :param hostname: The endpoint hostname.
        :type hostname: bytes
        :param port: The WSS port.
        :type port: int
        """
        _wsio_config = c_uamqp.WSIOConfig()

        _wsio_config.hostname = hostname
        _wsio_config.port = port

        _default_tlsio = c_uamqp.get_default_tlsio()
        _tlsio_config = c_uamqp.TLSIOConfig()
        _tlsio_config.hostname = hostname
        _tlsio_config.port = port

        if http_proxy:
            proxy_config = self._build_proxy_config(hostname, port, http_proxy)
            _tlsio_config.set_proxy_config(proxy_config)

        _wsio_config.set_tlsio_config(_default_tlsio, _tlsio_config)

        _underlying_xio = c_uamqp.xio_from_wsioconfig(_wsio_config)  # pylint: disable=attribute-defined-outside-init

        cert = self.cert_file or certifi.where()
        with open(cert, 'rb') as cert_handle:
            cert_data = cert_handle.read()
            try:
                _underlying_xio.set_certificates(cert_data)
            except ValueError:
                _logger.warning('Unable to set external certificates.')

        self.sasl_client = _SASLClient(_underlying_xio, self.sasl)  # pylint: disable=attribute-defined-outside-init
        self.consumed = False  # pylint: disable=attribute-defined-outside-init

    def set_tlsio(self, hostname, port):
        """Setup the default underlying TLS IO layer. On Windows this is
        Schannel, on Linux and MacOS this is OpenSSL.

        :param hostname: The endpoint hostname.
        :type hostname: bytes
        :param port: The TLS port.
        :type port: int
        """
        _default_tlsio = c_uamqp.get_default_tlsio()
        _tlsio_config = c_uamqp.TLSIOConfig()
        _tlsio_config.hostname = hostname
        _tlsio_config.port = int(port)

        _underlying_xio = c_uamqp.xio_from_tlsioconfig(_default_tlsio, _tlsio_config) # pylint: disable=attribute-defined-outside-init

        cert = self.cert_file or certifi.where()
        with open(cert, 'rb') as cert_handle:
            cert_data = cert_handle.read()
            try:
                _underlying_xio.set_certificates(cert_data)
            except ValueError:
                _logger.warning('Unable to set external certificates.')
        self.sasl_client = _SASLClient(_underlying_xio, self.sasl) # pylint: disable=attribute-defined-outside-init
        self.consumed = False # pylint: disable=attribute-defined-outside-init

    def close(self):
        """Close the authentication layer and cleanup
        all the authentication wrapper objects.
        """
        self.sasl_client.close()
        self.sasl.close()


class SASLPlain(AMQPAuth):
    """SASL Plain AMQP authentication.
    This is SASL authentication using a basic username and password.

    :param hostname: The AMQP endpoint hostname.
    :type hostname: str or bytes
    :param username: The authentication username.
    :type username: bytes or str
    :param password: The authentication password.
    :type password: bytes or str
    :param port: The TLS port - default for AMQP is 5671.
    :type port: int
    :param verify: The path to a user-defined certificate.
    :type verify: str
    :param http_proxy: HTTP proxy configuration. This should be a dictionary with
     the following keys present: 'proxy_hostname' and 'proxy_port'. Additional optional
     keys are 'username' and 'password'.
    :type http_proxy: dict
    :param transport_type: The transport protocol type - default is ~uamqp.TransportType.Amqp.
     ~uamqp.TransportType.AmqpOverWebsocket is applied when http_proxy is set or the
     transport type is explicitly requested.
    :type transport_type: ~uamqp.TransportType
    :param encoding: The encoding to use if hostname and credentials
     are provided as a str. Default is 'UTF-8'.
    :type encoding: str
    """

    def __init__(
            self, hostname, username, password, port=constants.DEFAULT_AMQPS_PORT,
            verify=None, http_proxy=None, transport_type=TransportType.Amqp, encoding='UTF-8'):
        self._encoding = encoding
        self.hostname = self._encode(hostname)
        self.username = self._encode(username)
        self.password = self._encode(password)
        self.cert_file = verify
        self.sasl = _SASLPlain(self.username, self.password)
        self.set_io(self.hostname, port, http_proxy, transport_type)


class SASLAnonymous(AMQPAuth):
    """SASL Annoymous AMQP authentication mixin.
    SASL connection with no credentials. If intending to use annoymous
    auth to set up a CBS session once connected, use SASTokenAuth
    or the CBSAuthMixin instead.

    :param hostname: The AMQP endpoint hostname.
    :type hostname: str or bytes
    :param port: The TLS port - default for AMQP is 5671.
    :type port: int
    :param verify: The path to a user-defined certificate.
    :type verify: str
    :param http_proxy: HTTP proxy configuration. This should be a dictionary with
     the following keys present: 'proxy_hostname' and 'proxy_port'. Additional optional
     keys are 'username' and 'password'.
    :type http_proxy: dict
    :param transport_type: The transport protocol type - default is ~uamqp.TransportType.Amqp.
     ~uamqp.TransportType.AmqpOverWebsocket is applied when http_proxy is set or the
     transport type is explicitly requested.
    :type transport_type: ~uamqp.TransportType
    :param encoding: The encoding to use if hostname is provided as a str.
     Default is 'UTF-8'.
    :type encoding: str
    """

    def __init__(self, hostname, port=constants.DEFAULT_AMQPS_PORT, verify=None,
                 http_proxy=None, transport_type=TransportType.Amqp, encoding='UTF-8'):
        self._encoding = encoding
        self.hostname = self._encode(hostname)
        self.cert_file = verify
        self.sasl = _SASLAnonymous()
        self.set_io(self.hostname, port, http_proxy, transport_type)


class _SASLClient(object):

    def __init__(self, io, sasl):
        """Create a SASLClient.

        This will own the input "io" and be responsible for its destruction.
        """
        self._underlying_io = io
        self._sasl = sasl
        self._io_config = c_uamqp.SASLClientIOConfig(io, self._sasl.mechanism)
        self._xio = c_uamqp.xio_from_saslioconfig(self._io_config)

    def get_client(self):
        return self._xio

    def close(self):
        self._xio.destroy()
        self._underlying_io.destroy()


class _SASL(object):

    def __init__(self):
        self._interface = self._get_interface()  # pylint: disable=assignment-from-none
        self.mechanism = self._get_mechanism()

    def _get_interface(self):
        return None

    def _get_mechanism(self):
        return c_uamqp.get_sasl_mechanism()

    def close(self):
        self.mechanism.destroy()

class _SASLAnonymous(_SASL):

    def _get_interface(self):
        return c_uamqp.saslanonymous_get_interface()

    def _get_mechanism(self):
        return c_uamqp.get_sasl_mechanism(self._interface)


class _SASLPlain(_SASL):

    def __init__(self, authcid, passwd, authzid=None):
        self._sasl_config = c_uamqp.SASLPlainConfig()
        self._sasl_config.authcid = authcid
        self._sasl_config.passwd = passwd
        if authzid:
            self._sasl_config.authzid = authzid
        super(_SASLPlain, self).__init__()

    def _get_interface(self):
        return c_uamqp.saslplain_get_interface()

    def _get_mechanism(self):
        return c_uamqp.get_plain_sasl_mechanism(self._interface, self._sasl_config)
