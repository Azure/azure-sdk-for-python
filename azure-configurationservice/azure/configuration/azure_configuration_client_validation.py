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


def validate_get_configuration_setting(key):
    if not key:
        raise ValueError("key is mandatory to get a ConfigurationSetting object")


def validate_add_configuration_setting(configuration_setting, **kwargs):
    if configuration_setting is None:
        raise ValueError("Object configuration_setting can not be None")
    if not configuration_setting.key:
        raise ValueError("key is mandatory to add a new ConfigurationSetting object")

    custom_headers = kwargs.get("headers")
    if custom_headers:
        for header_key, header_value in custom_headers.items():
            if header_key.lower() == "if-non-match":
                custom_headers[header_key] = '"*"'
                break
        else:
            custom_headers["If-None-Match"] = '"*"'
    else:
        custom_headers = {"If-None-Match": '"*"'}

    return custom_headers


def validate_update_configuration_setting(key, etag=None, **kwargs):
    # type: (str, str, dict) -> dict
    if key is None:
        raise ValueError("key is mandatory to update a ConfigurationSetting")

    return populate_http_header_if_match(etag, **kwargs)


def validate_set_configuration_setting(configuration_setting, **kwargs):
    if configuration_setting is None:
        raise ValueError("Object configuration_setting can not be None")
    key = configuration_setting.key
    if key is None:
        raise ValueError("key is mandatory to set a new ConfigurationSetting object")

    return populate_http_header_if_match(configuration_setting.etag, **kwargs)


def validate_delete_configuration_setting(key, etag=None, **kwargs):
    if key is None:
        raise ValueError("key is mandatory to delete a ConfigurationSetting object")

    return populate_http_header_if_match(etag, **kwargs)


def validate_lock_configuration_setting(key):
    if key is None:
        raise ValueError("key is mandatory to lock a ConfigurationSetting object")


def validate_unlock_configuration_setting(key):
    if key is None:
        raise ValueError("key is mandatory to unlock a ConfigurationSetting object")


def populate_http_header_if_match(etag, **kwargs):
    custom_headers = kwargs.get("headers")
    if custom_headers:
        for header_key, header_value in custom_headers.items():
            if header_key.lower() == "if-match":
                custom_headers[header_key] = '"' + etag + '"' if etag else header_value
                break
        else:
            if etag:
                custom_headers["If-Match"] = '"' + etag + '"'
    elif etag:
        custom_headers = {"If-Match": '"'+etag+'"'}

    return custom_headers

