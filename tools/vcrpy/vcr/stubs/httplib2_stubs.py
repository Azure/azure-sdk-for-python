"""Stubs for httplib2"""

from httplib2 import HTTPConnectionWithTimeout, HTTPSConnectionWithTimeout
from ..stubs import VCRHTTPConnection, VCRHTTPSConnection


class VCRHTTPConnectionWithTimeout(VCRHTTPConnection, HTTPConnectionWithTimeout):
    _baseclass = HTTPConnectionWithTimeout

    def __init__(self, *args, **kwargs):
        """I overrode the init because I need to clean kwargs before calling
        HTTPConnection.__init__."""

        # Delete the keyword arguments that HTTPConnection would not recognize
        safe_keys = {"host", "port", "strict", "timeout", "source_address"}
        unknown_keys = set(kwargs.keys()) - safe_keys
        safe_kwargs = kwargs.copy()
        for kw in unknown_keys:
            del safe_kwargs[kw]

        self.proxy_info = kwargs.pop("proxy_info", None)
        VCRHTTPConnection.__init__(self, *args, **safe_kwargs)
        self.sock = self.real_connection.sock


class VCRHTTPSConnectionWithTimeout(VCRHTTPSConnection, HTTPSConnectionWithTimeout):
    _baseclass = HTTPSConnectionWithTimeout

    def __init__(self, *args, **kwargs):

        # Delete the keyword arguments that HTTPSConnection would not recognize
        safe_keys = {
            "host",
            "port",
            "key_file",
            "cert_file",
            "strict",
            "timeout",
            "source_address",
            "ca_certs",
            "disable_ssl_certificate_validation",
        }
        unknown_keys = set(kwargs.keys()) - safe_keys
        safe_kwargs = kwargs.copy()
        for kw in unknown_keys:
            del safe_kwargs[kw]
        self.proxy_info = kwargs.pop("proxy_info", None)
        if "ca_certs" not in kwargs or kwargs["ca_certs"] is None:
            try:
                import httplib2

                self.ca_certs = httplib2.CA_CERTS
            except ImportError:
                self.ca_certs = None
        else:
            self.ca_certs = kwargs["ca_certs"]

        self.disable_ssl_certificate_validation = kwargs.pop("disable_ssl_certificate_validation", None)
        VCRHTTPSConnection.__init__(self, *args, **safe_kwargs)
        self.sock = self.real_connection.sock
