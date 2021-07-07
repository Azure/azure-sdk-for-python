"""Stubs for urllib3"""

from urllib3.connectionpool import HTTPConnection, VerifiedHTTPSConnection
from ..stubs import VCRHTTPConnection, VCRHTTPSConnection

# urllib3 defines its own HTTPConnection classes. It includes some polyfills
# for newer features missing in older pythons.


class VCRRequestsHTTPConnection(VCRHTTPConnection, HTTPConnection):
    _baseclass = HTTPConnection


class VCRRequestsHTTPSConnection(VCRHTTPSConnection, VerifiedHTTPSConnection):
    _baseclass = VerifiedHTTPSConnection
