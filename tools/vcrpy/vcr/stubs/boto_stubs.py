"""Stubs for boto"""

from boto.https_connection import CertValidatingHTTPSConnection
from ..stubs import VCRHTTPSConnection


class VCRCertValidatingHTTPSConnection(VCRHTTPSConnection):
    _baseclass = CertValidatingHTTPSConnection
