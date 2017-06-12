#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import io
import os
import adal
from msrestazure.azure_active_directory import AdalAuthentication

from .credentials import get_azure_cli_credentials, get_cli_profile
from .cloud import get_cli_active_cloud

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
    return clientclass(**parameters)

def get_client_from_auth_file(clientclass, auth_path=None, **kwargs):
    """Return a SDK client initialized with auth information in azureauth.properties.

    The path will be given using the environment variable AZURE_AUTH_LOCATION.
    File must be UTF-8 compliant.

    This method will fill automatically the following client parameters:
    - credentials
    - subscription_id
    - base_url

    Parameters provided in kwargs will override CLI parameters and be passed directly to the client.

    :Example:

    .. code:: python

        from azure.common.client_factory import get_client_from_auth_file
        from azure.mgmt.compute import ComputeManagementClient
        client = get_client_from_auth_file(ComputeManagementClient)

    Example of file:

    .. code:: text

        # sample management library properties file
        subscription=15dbcfa8-4b93-4c9a-881c-6189d39f04d4
        client=a2ab11af-01aa-4759-8345-7803287dbd39
        key=password
        tenant=43413cc1-5886-4711-9804-8cfea3d1c3ee
        managementURI=https://management.core.windows.net/
        baseURL=https://management.azure.com/
        authURL=https://login.windows.net/
        graphURL=https://graph.windows.net/

    .. versionadded:: 1.1.7

    :param clientclass: A SDK client class
    :param str auth_path: Path to azureauth.properties
    :return: An instanciated client
    :raises: KeyError if AZURE_AUTH_LOCATION is not an environment variable and no path is provided
    :raises: FileNotFoundError if provided file path does not exists
    """
    auth_path = auth_path or os.environ['AZURE_AUTH_LOCATION']

    with io.open(auth_path, 'r', encoding='utf-8') as auth_fd:
        content_list = [line.strip() for line in auth_fd.readlines() if line[0] != '#' and '=' in line]
    config_dict = dict([tuple(line.split('=', 1)) for line in content_list])

    parameters = {
        'subscription_id': config_dict.get('subscription'),
        'base_url': config_dict.get('baseURL'),
    }

    if 'credentials' not in kwargs:
        authority_url = (config_dict['authURL'] + '/' + 
                         config_dict['tenant'])
        context = adal.AuthenticationContext(authority_url, api_version=None)
        parameters['credentials'] = AdalAuthentication(
            context.acquire_token_with_client_credentials,
            config_dict['managementURI'],
            config_dict['client'],
            config_dict['key']
        )

    parameters.update(kwargs)
    return clientclass(**parameters)
