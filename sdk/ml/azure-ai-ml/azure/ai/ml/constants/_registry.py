# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta


class StorageAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Storage account types."""

    STANDARD_LRS = "Standard_LRS".lower()
    STANDARD_GRS = "Standard_GRS".lower()
    STANDARD_RAGRS = "Standard_RAGRS".lower()
    STANDARD_ZRS = "Standard_ZRS".lower()
    STANDARD_GZRS = "Standard_GZRS".lower()
    STANDARD_RAGZRS = "Standard_RAGZRS".lower()
    PREMIUM_LRS = "Premium_LRS".lower()
    PREMIUM_ZRS = "Premium_ZRS".lower()


# When will other values be allowed?
class AcrAccountSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Azure Container Registry SKUs."""

    PREMIUM = "Premium".lower()


# based on /subscriptions/{SubscriptionId}/resourceGroups/{ResourceGroupName}/
# # ...providers/Microsoft.Storage/storageAccounts/{StorageAccountName}
STORAGE_ACCOUNT_FORMAT = re.compile(
    ("/subscriptions/(.*)/resourceGroups/(.*)/providers/Microsoft.Storage/storageAccounts/(.*)")
)
# based on /subscriptions/{SubscriptionId}/resourceGroups/{ResourceGroupName}/
# # ...providers/Microsoft.ContainerRegistry/registries/{AcrName}\
ACR_ACCOUNT_FORMAT = re.compile(
    ("/subscriptions/(.*)/resourceGroups/(.*)/providers/Microsoft.ContainerRegistry/registries/(.*)")
)
