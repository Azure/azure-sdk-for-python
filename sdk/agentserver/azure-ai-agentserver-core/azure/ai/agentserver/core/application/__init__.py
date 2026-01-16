# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

__all__ = [
    "PackageMetadata",
    "set_current_app"
]

from ._package_metadata import PackageMetadata, set_current_app