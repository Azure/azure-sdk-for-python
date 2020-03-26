# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Any, NamedTuple
    from typing_extensions import Protocol

    AccessToken = NamedTuple("AccessToken", [("token", str), ("expires_on", int)])

    class TokenCredential(Protocol):
        """Protocol for classes able to provide OAuth tokens.

        :param str scopes: Lets you specify the type of access needed.
        """

        # pylint:disable=too-few-public-methods
        def get_token(self, *scopes, **kwargs):
            # type: (*str, **Any) -> AccessToken
            pass


else:
    from collections import namedtuple

    AccessToken = namedtuple("AccessToken", ["token", "expires_on"])
