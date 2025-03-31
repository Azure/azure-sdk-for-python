# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import TYPE_CHECKING

# This code violates no-typing-import-in-type-check

if TYPE_CHECKING:
    from typing import Any


def foo() -> Any:
    return 42