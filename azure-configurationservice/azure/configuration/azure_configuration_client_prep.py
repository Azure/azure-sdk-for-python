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

"""
The methods in this module preprocess the parameters for the methods in
:class:`azure.configuration.AzureConfigurationClient` and
:class:`azure.configuration.aio.AzureConfigurationClientSync`
"""


from requests.structures import CaseInsensitiveDict


def prep_get_configuration_setting(key, **kwargs):
    if not key:
        raise ValueError("key is mandatory to get a ConfigurationSetting object")
    return kwargs.get("headers")


def prep_add_configuration_setting(configuration_setting, **kwargs):
    if configuration_setting is None:
        raise ValueError("Object configuration_setting can not be None")
    if not configuration_setting.key:
        raise ValueError("key is mandatory to add a new ConfigurationSetting object")

    custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
    custom_headers["if-none-match"] = quote_etag('*')
    return custom_headers


def prep_update_configuration_setting(key, etag=None, **kwargs):
    # type: (str, str, dict) -> CaseInsensitiveDict
    if not key:
        raise ValueError("key is mandatory to update a ConfigurationSetting")

    custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
    if etag:
        custom_headers["if-match"] = quote_etag(etag)
    elif "if-match" not in custom_headers:
        custom_headers["if-match"] = quote_etag('*')

    return custom_headers


def prep_set_configuration_setting(configuration_setting, **kwargs):
    if configuration_setting is None:
        raise ValueError("Object configuration_setting can not be None")
    if not configuration_setting.key:
        raise ValueError("key is mandatory to set a new ConfigurationSetting object")

    custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
    etag = configuration_setting.etag
    if etag:
        custom_headers["if-match"] = quote_etag(etag)

    return custom_headers


def prep_delete_configuration_setting(key: str, etag:str = None, **kwargs: dict) -> CaseInsensitiveDict:
    if not key:
        raise ValueError("key is mandatory to delete a ConfigurationSetting object")

    custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
    if etag:
        custom_headers["if-match"] = quote_etag(etag)

    return custom_headers


def prep_lock_configuration_setting(key, **kwargs):
    if not key:
        raise ValueError("key is mandatory to lock a ConfigurationSetting object")

    return kwargs.get("header")


def prep_unlock_configuration_setting(key, **kwargs):
    if not key:
        raise ValueError("key is mandatory to unlock a ConfigurationSetting object")

    return kwargs.get("header")


def quote_etag(etag):
    return '"' + etag + '"'

