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


class InvalidSchemaError(ValueError):
    """Error during schema validation.

    :param str message: The message object stringified as 'message' attribute
    :keyword error: The original exception, if any.

    :ivar str message: A stringified version of the message parameter
    :ivar dict details: The error details related to the schema. Depending on the error,
     this may include information like: `schema_id`, `schema_definition`, `message_content`.
    """

    def __init__(self, message, *args, **kwargs):
        self.message = str(message)
        self.details = kwargs.pop("details", {})
        super(InvalidSchemaError, self).__init__(self.message, *args)


class InvalidContentError(ValueError):
    """Error during encoding or decoding content with a schema.

    :param str message: The message object stringified as 'message' attribute
    :keyword error: The original exception, if any.

    :ivar str message: A stringified version of the message parameter
    :ivar dict details: The error details. Depending on the error, this may include information like:
        `schema_id`, `schema_definition`, `message_content`.
    """

    def __init__(self, message, *args, **kwargs):
        self.message = str(message)
        self.details = kwargs.pop("details", {})
        super(InvalidContentError, self).__init__(self.message, *args)
