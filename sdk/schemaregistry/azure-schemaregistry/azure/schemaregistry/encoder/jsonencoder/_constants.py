# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class JsonSchemaDraftIdentifier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """
    The JSON schema draft identifiers available for validation.
    """

    DRAFT2020_12 = "https://json-schema.org/draft/2020-12/schema"
    DRAFT2019_09 = "https://json-schema.org/draft/2019-09/schema"
    DRAFT_07 = "http://json-schema.org/draft-07/schema"
    DRAFT_06 = "http://json-schema.org/draft-06/schema"
    DRAFT_04 = "http://json-schema.org/draft-04/schema"
    DRAFT_03 = "http://json-schema.org/draft-03/schema"

JSON_MIME_TYPE = "application/json;serialization=Json"
