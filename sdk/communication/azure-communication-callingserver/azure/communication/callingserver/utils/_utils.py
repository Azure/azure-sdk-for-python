# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import validators

class CallingServerUtils(object):

    @staticmethod
    def is_valid_url(
        url, # type: str
    ): # type: (...) -> bool
        result = validators.url(url)

        if isinstance(result, validators.utils.ValidationFailure):
            return False

        return True