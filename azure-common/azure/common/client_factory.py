#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import io
import os
import adal
import inspect
import json
from msrestazure.azure_active_directory import AdalAuthentication

from .credentials import get_azure_cli_credentials, get_cli_profile
from .cloud import get_cli_active_cloud

def _instanciate_client(clientclass, **kwargs):
    """Instanciate client from kwargs, remove parameters not needed by the Client.
    """
    args = inspect.getargspec(clientclass.__init__).args
    if 'subscription_id' not in args:
        del kwargs['subscription_id']
    return clientclass(**kwargs)


def get_client_from_cli_profile(clientclass, **kwargs):
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

    :param clientclass: A SDK client class
    :return: An instanciated client
    :raises: ImportError if azure-cli-core package is not available
    """

    parameters = {}
    if 'credentials' not in kwargs or 'subscription_id' not in kwargs:
        credentials, subscription_id = get_azure_cli_credentials()
        parameters.update({
            'credentials': kwargs.get('credentials', credentials),
            'subscription_id': kwargs.get('subscription_id', subscription_id)
        })
    if 'base_url' not in kwargs:
        cloud = get_cli_active_cloud()
        # api_version_profile = cloud.profile # TBC using _shared
        parameters['base_url'] = cloud.endpoints.resource_manager
    parameters.update(kwargs)
    return _instanciate_client(clientclass, **parameters)

def get_client_from_json_dict(clientclass, config_dict, **kwargs):
    """Return a SDK client initialized with a JSON auth dict.

    The easiest way to obtain this content is to call the following CLI commands:

    .. code:: bash

        az ad sp create-for-rbac --sdk-auth

    This method will fill automatically the following client parameters:
    - credentials
    - subscription_id
    - base_url

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

    :param clientclass: A SDK client class
    :param dict config_dict: A config dict.
    :return: An instanciated client
    """
    parameters = {
        'subscription_id': config_dict.get('subscriptionId'),
        'base_url': config_dict.get('resourceManagerEndpointUrl'),
    }

    if 'credentials' not in kwargs:
        authority_url = (config_dict['activeDirectoryEndpointUrl'] + '/' + 
                         config_dict['tenantId'])
        context = adal.AuthenticationContext(authority_url, api_version=None)
        parameters['credentials'] = AdalAuthentication(
            context.acquire_token_with_client_credentials,
            config_dict['managementEndpointUrl'],
            config_dict['clientId'],
            config_dict['clientSecret']
        )

    parameters.update(kwargs)
    return _instanciate_client(clientclass, **parameters)

def get_client_from_auth_file(clientclass, auth_path=None, **kwargs):
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

    :param clientclass: A SDK client class
    :param str auth_path: Path to the file.
    :return: An instanciated client
    :raises: KeyError if AZURE_AUTH_LOCATION is not an environment variable and no path is provided
    :raises: FileNotFoundError if provided file path does not exists
    :raises: json.JSONDecodeError if provided file is not JSON valid
    :raises: UnicodeDecodeError if file is not UTF8 compliant
    """
    auth_path = auth_path or os.environ['AZURE_AUTH_LOCATION']

    with io.open(auth_path, 'r', encoding='utf-8') as auth_fd:
        config_dict = json.load(auth_fd)
    return get_client_from_json_dict(clientclass, config_dict, **kwargs)
