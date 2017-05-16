#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

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
