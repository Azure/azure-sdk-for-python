# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import TYPE_CHECKING

# This code violates no-typing-import-in-type-check

if TYPE_CHECKING:
    from typing import Any

if TYPE_CHECKING:
    import typing_extensions

# test_allowed_imports
if TYPE_CHECKING:
    from math import PI
