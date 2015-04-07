# Copyright (c) Microsoft Corporation.  All rights reserved.

"""HTTPS Connection.
"""


import socket
import ssl


try:
    from httplib import HTTPConnection, HTTPS_PORT
except:
    from http.client import HTTPConnection, HTTPS_PORT


class HTTPSConnection(HTTPConnection):
    """This class allows communication via SSL."""

    default_port = HTTPS_PORT

    def __init__(self, host, port=None, ssl_configuration=None, strict=None,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None):
        """
        :Parameters:
            - `host`: str, the host address.
            - `port`: int, the port number.
            - `ssl_configuration`: documents.SSLConfiguration, where you specify certs files.
            - `strict`: bool, the strict.
            - `timeout`: int, the connection timeout in milliseconds.
            - `source_address`: str, the source address.
        """
        HTTPConnection.__init__(self, host, port, strict, timeout, source_address)
        self._ssl_configuration = ssl_configuration

    def connect(self):
        """Connects to to host via HTTPS."""
        sock = socket.create_connection((self.host, self.port), self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        cert_reqs = ssl.CERT_NONE

        if self._ssl_configuration:
            if self._ssl_configuration.SSLCaCerts:
                cert_reqs = ssl.CERT_REQUIRED

            self.sock = ssl.wrap_socket(sock,
                                        keyfile=self._ssl_configuration.SSLKeyFile,
                                        certfile=self._ssl_configuration.SSLCertFile,
                                        cert_reqs=cert_reqs,
                                        ca_certs=self._ssl_configuration.SSLCaCerts)
        else:
            self.sock = ssl.wrap_socket(sock,
                                        keyfile=None,
                                        certfile=None,
                                        cert_reqs=ssl.CERT_NONE,
                                        ca_certs=None)