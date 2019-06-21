# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys

if sys.version_info >= (3,):
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

from ._constants import (
    SERVICE_HOST_BASE,
    DEFAULT_PROTOCOL,
    DEV_ACCOUNT_NAME,
    DEV_ACCOUNT_SECONDARY_NAME,
    DEV_ACCOUNT_KEY,
    DEV_BLOB_HOST,
    DEV_QUEUE_HOST,
)
from ._error import (
    _ERROR_STORAGE_MISSING_INFO,
)

_EMULATOR_ENDPOINTS = {
    'blob': DEV_BLOB_HOST,
    'queue': DEV_QUEUE_HOST,
    'file': '',
}

_CONNECTION_ENDPOINTS = {
    'blob': 'BlobEndpoint',
    'queue': 'QueueEndpoint',
    'file': 'FileEndpoint',
}

_CONNECTION_ENDPOINTS_SECONDARY = {
    'blob': 'BlobSecondaryEndpoint',
    'queue': 'QueueSecondaryEndpoint',
    'file': 'FileSecondaryEndpoint',
}


class _ServiceParameters(object):
    def __init__(self, service, account_name=None, account_key=None, sas_token=None, token_credential=None,
                 is_emulated=False, protocol=DEFAULT_PROTOCOL, endpoint_suffix=SERVICE_HOST_BASE, 
                 custom_domain=None, custom_domain_secondary=None):

        self.account_name = account_name
        self.account_key = account_key
        self.sas_token = sas_token
        self.token_credential = token_credential
        self.protocol = protocol or DEFAULT_PROTOCOL
        self.is_emulated = is_emulated

        if is_emulated:
            self.account_name = DEV_ACCOUNT_NAME
            self.protocol = 'http'

            # Only set the account key if a sas_token is not present to allow sas to be used with the emulator
            self.account_key = DEV_ACCOUNT_KEY if not self.sas_token else None

            self.primary_endpoint = '{}/{}'.format(_EMULATOR_ENDPOINTS[service], DEV_ACCOUNT_NAME)
            self.secondary_endpoint = '{}/{}'.format(_EMULATOR_ENDPOINTS[service], DEV_ACCOUNT_SECONDARY_NAME)
        else:
            # Strip whitespace from the key
            if self.account_key:
                self.account_key = self.account_key.strip()

            endpoint_suffix = endpoint_suffix or SERVICE_HOST_BASE

            # Setup the primary endpoint
            if custom_domain:
                parsed_url = urlparse(custom_domain)

                # Trim any trailing slashes from the path
                path = parsed_url.path.rstrip('/')

                self.primary_endpoint = parsed_url.netloc + path
                self.protocol = self.protocol if parsed_url.scheme is '' else parsed_url.scheme
            else:
                if not self.account_name:
                    raise ValueError(_ERROR_STORAGE_MISSING_INFO)
                self.primary_endpoint = '{}.{}.{}'.format(self.account_name, service, endpoint_suffix)

            # Setup the secondary endpoint
            if custom_domain_secondary:
                if not custom_domain:
                    raise ValueError(_ERROR_STORAGE_MISSING_INFO)   

                parsed_url = urlparse(custom_domain_secondary)

                # Trim any trailing slashes from the path
                path = parsed_url.path.rstrip('/')

                self.secondary_endpoint = parsed_url.netloc + path
            else:
                if self.account_name:
                    self.secondary_endpoint = '{}-secondary.{}.{}'.format(self.account_name, service, endpoint_suffix)
                else:
                    self.secondary_endpoint = None

    @staticmethod
    def get_service_parameters(service, account_name=None, account_key=None, sas_token=None, token_credential= None,
                               is_emulated=None, protocol=None, endpoint_suffix=None, custom_domain=None,
                               request_session=None, connection_string=None, socket_timeout=None):
        if connection_string:
            params = _ServiceParameters._from_connection_string(connection_string, service)
        elif is_emulated:
            params = _ServiceParameters(service, is_emulated=True)
        elif account_name:
            if protocol.lower() != 'https' and token_credential is not None:
                raise ValueError("Token credential is only supported with HTTPS.")
            params = _ServiceParameters(service,
                                        account_name=account_name,
                                        account_key=account_key,
                                        sas_token=sas_token,
                                        token_credential=token_credential,
                                        is_emulated=is_emulated,
                                        protocol=protocol,
                                        endpoint_suffix=endpoint_suffix,
                                        custom_domain=custom_domain)
        else:
            raise ValueError(_ERROR_STORAGE_MISSING_INFO)

        params.request_session = request_session
        params.socket_timeout = socket_timeout
        return params

    @staticmethod
    def _from_connection_string(connection_string, service):
        # Split into key=value pairs removing empties, then split the pairs into a dict
        config = dict(s.split('=', 1) for s in connection_string.split(';') if s)

        # Authentication
        account_name = config.get('AccountName')
        account_key = config.get('AccountKey')
        sas_token = config.get('SharedAccessSignature')

        # Emulator
        is_emulated = config.get('UseDevelopmentStorage')

        # Basic URL Configuration
        protocol = config.get('DefaultEndpointsProtocol')
        endpoint_suffix = config.get('EndpointSuffix')

        # Custom URLs
        endpoint = config.get(_CONNECTION_ENDPOINTS[service])
        endpoint_secondary = config.get(_CONNECTION_ENDPOINTS_SECONDARY[service])

        return _ServiceParameters(service,
                                  account_name=account_name,
                                  account_key=account_key,
                                  sas_token=sas_token,
                                  is_emulated=is_emulated,
                                  protocol=protocol,
                                  endpoint_suffix=endpoint_suffix,
                                  custom_domain=endpoint,
                                  custom_domain_secondary=endpoint_secondary)
