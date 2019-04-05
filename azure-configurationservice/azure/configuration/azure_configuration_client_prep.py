# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

"""
The methods in this module preprocess the parameters for the methods in
:class:`azure.configuration.AzureConfigurationClient` and
:class:`azure.configuration.aio.AzureConfigurationClientSync`
"""

import re
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


def escape_reserved(value):
    """
    Reserved characters
    *, \, ,
    If a reserved character is part of the value, then it must be escaped using \{Reserved Character}. 
    Non-reserved characters can also be escaped.

    """
    if not value:
        return '\0'  # '\0' will be encoded to %00 in the url.
    else:
        value_type = type(value)
        if value_type == str:
            # precede all reserved characters with a backslash.
            # But if a * is at the beginning or the end, don't add the backslash
            return re.sub(r'((?!^)\*(?!$)|\\|,)', r'\\\1', value)
        elif value_type == list:
            return [escape_reserved(s) for s in value]
        else:
            raise ValueError(value_type + " can not be escaped. It must be a string or list of strings")


def escape_and_tolist(value):
    if value:
        value = escape_reserved(value)
        if type(value) == str:
            return [value]
        else:
            return value
    else:
        return None

