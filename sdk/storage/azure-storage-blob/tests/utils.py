# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# --------------------------------------------------------------------------

import random
import string


def get_resource_name(prefix, name_length=8):
    return prefix + "".join(
        random.choices(string.ascii_lowercase + string.digits, k=name_length)
    )
