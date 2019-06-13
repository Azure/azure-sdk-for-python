# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing_extensions import Protocol


class TokenCredential(Protocol):
    """Protocol for classes able to provide OAuth tokens.

    :param str scopes: Lets you specify the type of access needed.
    """
    # pylint:disable=too-few-public-methods
    def get_token(self, *scopes):
        # type: (*str) -> str
        pass
