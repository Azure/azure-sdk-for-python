# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint:skip-file (avoids crash due to six.with_metaclass https://github.com/PyCQA/astroid/issues/713)
from enum import Enum
from six import with_metaclass

from azure.core import CaseInsensitiveEnumMeta

class ContainerRegistryAudience(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Supported container registry audience"""

    ARM_CHINA = "https://management.chinacloudapi.cn"
    ARM_GERMANY = "https://management.microsoftazure.de"
    ARM_GOVERNMENT = "https://management.usgovcloudapi.net"
    ARM_PUBLIC_CLOUD = "https://management.azure.com"
