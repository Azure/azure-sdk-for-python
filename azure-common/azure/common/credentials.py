#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os.path

def get_cli_profile():
    """Return a CLI profile class.

    .. versionadded:: 1.1.6

    :return: A CLI Profile
    :rtype: azure.cli.core._profile.Profile
    :raises: ImportError if azure-cli-core package is not available
    """

    try:
        from azure.cli.core._profile import Profile
        from azure.cli.core._session import ACCOUNT
        from azure.cli.core._environment import get_config_dir
    except ImportError:
        raise ImportError("You need to install 'azure-cli-core' to load CLI credentials")


    azure_folder = get_config_dir()
    ACCOUNT.load(os.path.join(azure_folder, 'azureProfile.json'))
    return Profile(storage=ACCOUNT)

def get_azure_cli_credentials():
    """Return Credentials and default SubscriptionID of current loaded profile of the CLI.

    Credentials will be the "az login" command: 
    https://docs.microsoft.com/cli/azure/authenticate-azure-cli

    Default subscription ID is either the only one you have, or you can define it:
    https://docs.microsoft.com/cli/azure/manage-azure-subscriptions-azure-cli

    .. versionadded:: 1.1.6

    :return: tuple of Credentials and SubscriptionID
    :rtype: tuple
    """
    profile = get_cli_profile()
    cred, subscription_id, _ = profile.get_login_credentials()
    return cred, subscription_id


try:
    from msrest.authentication import (
        BasicAuthentication,
        BasicTokenAuthentication,
        OAuthTokenAuthentication
    )
except ImportError:
    raise ImportError("You need to install 'msrest' to use this feature")

try:
    from msrestazure.azure_active_directory import (
        InteractiveCredentials,
        ServicePrincipalCredentials,
        UserPassCredentials
    )
except ImportError:
    raise ImportError("You need to install 'msrestazure' to use this feature")
