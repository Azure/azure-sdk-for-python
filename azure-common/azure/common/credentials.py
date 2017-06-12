#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

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