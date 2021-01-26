# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# This function is a minimal port borrowed from the JavaScript implementation at
# https://github.com/microsoft/CorrelationVector-JavaScript/blob/6da3f9e6150581756aba54b98dcd1e7329ef36bd/cV.js.
# License is MIT: https://github.com/microsoft/CorrelationVector-JavaScript/blob/6da3f9e6150581756aba54b98dcd1e7329ef36bd/LICENSE

import random

BASE_64_CHAR_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
CV_BASE_LENGTH = 22

def _generate_cv_base():
    # type: () -> str
    """
    Seed function to randomly generate a 16 character base64 encoded string for
    the Correlation Vector's base value.
    """
    result = ''

    for i in range(CV_BASE_LENGTH):
        random_index = random.randint(0, len(BASE_64_CHAR_SET) - 1)
        result += BASE_64_CHAR_SET[random_index]

    return result
