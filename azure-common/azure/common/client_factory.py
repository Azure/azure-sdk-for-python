#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import io
import json
import os
import sys
try:
    from inspect import getfullargspec as get_arg_spec
except ImportError:
    from inspect import getargspec as get_arg_spec

import adal
from msrestazure.azure_active_directory import AdalAuthentication

from .credentials import get_azure_cli_credentials
from .cloud import get_cli_active_cloud


def _instantiate_client(client_class, **kwargs):
    """Instantiate a client from kwargs, removing the subscription_id/tenant_id argument if unsupported.
    """
    args = get_arg_spec(client_class.__init__).args
    for key in ['subscription_id', 'tenant_id']:
        if key not in kwargs:
            continue
        if key not in args:
            del kwargs[key]
        elif sys.version_info < (3, 0) and isinstance(kwargs[key], unicode):
            kwargs[key] = kwargs[key].encode('utf-8')
    return client_class(**kwargs)


def _client_resource(client_class, cloud):
    """Return a tuple of the resource (used to get the right access token), and the base URL for the client.
    Either or both can be None to signify that the default value should be used.
    """
    if client_class.__name__ == 'GraphRbacManagementClient':
        return cloud.endpoints.active_directory_graph_resource_id, cloud.endpoints.active_directory_graph_resource_id
    if client_class.__name__ == 'KeyVaultClient':
        vault_host = cloud.suffixes.keyvault_dns[1:]
        vault_url = 'https://{}'.format(vault_host)
        return vault_url, None
    return None, None


def get_client_from_cli_profile(client_class, **kwargs):
    """Return a SDK client initialized with current CLI credentials, CLI default subscription and CLI default cloud.

    This method will fill automatically the following client parameters:
    - credentials
    - subscription_id
    - base_url

    Parameters provided in kwargs will override CLI parameters and be passed directly to the client.

    :Example:

    .. code:: python

        from azure.common.client_factory import get_client_from_cli_profile
        from azure.mgmt.compute import ComputeManagementClient
        client = get_client_from_cli_profile(ComputeManagementClient)

    .. versionadded:: 1.1.6

    :param client_class: A SDK client class
    :return: An instantiated client
    :raises: ImportError if azure-cli-core package is not available
    """
    cloud = get_cli_active_cloud()
    parameters = {}
    if 'credentials' not in kwargs or 'subscription_id' not in kwargs:
        resource, _ = _client_resource(client_class, cloud)
        credentials, subscription_id, tenant_id = get_azure_cli_credentials(resource=resource,
                                                                            with_tenant=True)
        parameters.update({
            'credentials': kwargs.get('credentials', credentials),
            'subscription_id': kwargs.get('subscription_id', subscription_id)
        })

    args = get_arg_spec(client_class.__init__).args
    if 'adla_job_dns_suffix' in args and 'adla_job_dns_suffix' not in kwargs:  # Datalake
        # Let it raise here with AttributeError at worst, this would mean this cloud does not define
        # ADL endpoint and no manual suffix was given
        parameters['adla_job_dns_suffix'] = cloud.suffixes.azure_datalake_analytics_catalog_and_job_endpoint
    elif 'base_url' in args and 'base_url' not in kwargs:
        _, base_url = _client_resource(client_class, cloud)
        if base_url:
            parameters['base_url'] = base_url
        else:
            parameters['base_url'] = cloud.endpoints.resource_manager
    if 'tenant_id' in args and 'tenant_id' not in kwargs:
        parameters['tenant_id'] = tenant_id
    parameters.update(kwargs)
    return _instantiate_client(client_class, **parameters)


def get_client_from_json_dict(client_class, config_dict, **kwargs):
    """Return a SDK client initialized with a JSON auth dict.

    The easiest way to obtain this content is to call the following CLI commands:

    .. code:: bash

        az ad sp create-for-rbac --sdk-auth

    This method will fill automatically the following client parameters:
    - credentials
    - subscription_id
    - base_url
    - tenant_id

    Parameters provided in kwargs will override parameters and be passed directly to the client.

    :Example:

    .. code:: python

        from azure.common.client_factory import get_client_from_auth_file
        from azure.mgmt.compute import ComputeManagementClient
        config_dict = {
            "clientId": "ad735158-65ca-11e7-ba4d-ecb1d756380e",
            "clientSecret": "b70bb224-65ca-11e7-810c-ecb1d756380e",
            "subscriptionId": "bfc42d3a-65ca-11e7-95cf-ecb1d756380e",
            "tenantId": "c81da1d8-65ca-11e7-b1d1-ecb1d756380e",
            "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
            "resourceManagerEndpointUrl": "https://management.azure.com/",
            "activeDirectoryGraphResourceId": "https://graph.windows.net/",
            "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
            "galleryEndpointUrl": "https://gallery.azure.com/",
            "managementEndpointUrl": "https://management.core.windows.net/"
        }
        client = get_client_from_json_dict(ComputeManagementClient, config_dict)

    .. versionadded:: 1.1.7

    :param client_class: A SDK client class
    :param dict config_dict: A config dict.
    :return: An instantiated client
    """
    is_graphrbac = client_class.__name__ == 'GraphRbacManagementClient'
    parameters = {
        'subscription_id': config_dict.get('subscriptionId'),
        'base_url': config_dict.get('resourceManagerEndpointUrl'),
        'tenant_id': config_dict.get('tenantId')  # GraphRbac
    }
    if is_graphrbac:
        parameters['base_url'] = config_dict['activeDirectoryGraphResourceId']

    if 'credentials' not in kwargs:
        # Get the right resource for Credentials
        if is_graphrbac:
            resource = config_dict['activeDirectoryGraphResourceId']
        else:
            resource = config_dict['resourceManagerEndpointUrl']
        authority_url = (config_dict['activeDirectoryEndpointUrl'] + '/' +
                         config_dict['tenantId'])
        context = adal.AuthenticationContext(authority_url, api_version=None)
        parameters['credentials'] = AdalAuthentication(
            context.acquire_token_with_client_credentials,
            resource,
            config_dict['clientId'],
            config_dict['clientSecret']
        )

    parameters.update(kwargs)
    return _instantiate_client(client_class, **parameters)

def get_client_from_auth_file(client_class, auth_path=None, **kwargs):
    """Return a SDK client initialized with auth file.

    The easiest way to obtain this file is to call the following CLI commands:

    .. code:: bash

        az ad sp create-for-rbac --sdk-auth

    You can specific the file path directly, or fill the environment variable AZURE_AUTH_LOCATION.
    File must be UTF-8.

    This method will fill automatically the following client parameters:
    - credentials
    - subscription_id
    - base_url

    Parameters provided in kwargs will override parameters and be passed directly to the client.

    :Example:

    .. code:: python

        from azure.common.client_factory import get_client_from_auth_file
        from azure.mgmt.compute import ComputeManagementClient
        client = get_client_from_auth_file(ComputeManagementClient)

    Example of file:

    .. code:: json

        {
            "clientId": "ad735158-65ca-11e7-ba4d-ecb1d756380e",
            "clientSecret": "b70bb224-65ca-11e7-810c-ecb1d756380e",
            "subscriptionId": "bfc42d3a-65ca-11e7-95cf-ecb1d756380e",
            "tenantId": "c81da1d8-65ca-11e7-b1d1-ecb1d756380e",
            "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
            "resourceManagerEndpointUrl": "https://management.azure.com/",
            "activeDirectoryGraphResourceId": "https://graph.windows.net/",
            "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
            "galleryEndpointUrl": "https://gallery.azure.com/",
            "managementEndpointUrl": "https://management.core.windows.net/"
        }

    .. versionadded:: 1.1.7

    :param client_class: A SDK client class
    :param str auth_path: Path to the file.
    :return: An instantiated client
    :raises: KeyError if AZURE_AUTH_LOCATION is not an environment variable and no path is provided
    :raises: FileNotFoundError if provided file path does not exists
    :raises: json.JSONDecodeError if provided file is not JSON valid
    :raises: UnicodeDecodeError if file is not UTF8 compliant
    """
    auth_path = auth_path or os.environ['AZURE_AUTH_LOCATION']

    with io.open(auth_path, 'r', encoding='utf-8-sig') as auth_fd:
        config_dict = json.load(auth_fd)
    return get_client_from_json_dict(client_class, config_dict, **kwargs)
