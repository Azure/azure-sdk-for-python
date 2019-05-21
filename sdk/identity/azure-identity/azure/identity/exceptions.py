# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------


# TODO: probably a better base for this in azure-core
class AuthenticationError(Exception):
    def __init__(self, message):
        # type: (str) -> None
        self.message = message

    def __str__(self):
        return self.message
