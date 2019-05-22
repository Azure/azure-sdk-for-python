# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Iterable  # pylint:disable=unused-import
from typing_extensions import Protocol


class SupportsGetToken(Protocol):
    """Protocol for classes able to provide OAuth tokens.

    :param str scopes: Lets you specify the type of access needed.
    """
    # pylint:disable=too-few-public-methods
    def get_token(self, scopes):
        # type: (Iterable[str]) -> str
        pass
