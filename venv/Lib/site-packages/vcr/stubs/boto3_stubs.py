"""Stubs for boto3"""
import six

try:
    # boto using awsrequest
    from botocore.awsrequest import AWSHTTPConnection as HTTPConnection
    from botocore.awsrequest import AWSHTTPSConnection as VerifiedHTTPSConnection

except ImportError:  # pragma: nocover
    # boto using vendored requests
    # urllib3 defines its own HTTPConnection classes, which boto3 goes ahead and assumes
    # you're using.  It includes some polyfills for newer features missing in older pythons.
    try:
        from urllib3.connectionpool import HTTPConnection, VerifiedHTTPSConnection
    except ImportError:  # pragma: nocover
        from requests.packages.urllib3.connectionpool import HTTPConnection, VerifiedHTTPSConnection

from ..stubs import VCRHTTPConnection, VCRHTTPSConnection


class VCRRequestsHTTPConnection(VCRHTTPConnection, HTTPConnection):
    _baseclass = HTTPConnection


class VCRRequestsHTTPSConnection(VCRHTTPSConnection, VerifiedHTTPSConnection):
    _baseclass = VerifiedHTTPSConnection

    def __init__(self, *args, **kwargs):
        if six.PY3:
            kwargs.pop("strict", None)  # apparently this is gone in py3

        # need to temporarily reset here because the real connection
        # inherits from the thing that we are mocking out.  Take out
        # the reset if you want to see what I mean :)
        from vcr.patch import force_reset

        with force_reset():
            self.real_connection = self._baseclass(*args, **kwargs)
            # Make sure to set those attributes as it seems `AWSHTTPConnection` does not
            # set them, making the connection to fail !
            self.real_connection.assert_hostname = kwargs.get("assert_hostname", False)
            self.real_connection.cert_reqs = kwargs.get("cert_reqs", "CERT_NONE")

        self._sock = None
