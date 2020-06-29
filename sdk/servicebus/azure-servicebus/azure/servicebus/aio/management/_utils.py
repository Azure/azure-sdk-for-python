# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import cast
from xml.etree.ElementTree import ElementTree


import urllib.parse as urlparse

from azure.servicebus.management import _constants as constants
from ...management._handle_response_error import _handle_response_error


async def extract_data_template(feed_class, convert, feed_element):
    deserialized = feed_class.deserialize(feed_element)
    list_of_qd = [convert(x) if convert else x for x in deserialized.entry]
    next_link = None
    if deserialized.link and len(deserialized.link) == 2:
        next_link = deserialized.link[1].href
    return next_link, iter(list_of_qd)


async def get_next_template(list_func, *args, **kwargs):
    if args:
        next_link = args[0]
    else:
        next_link = kwargs.pop("next_link")

    start_index = kwargs.pop("start_index", 0)
    max_page_size = kwargs.pop("max_page_size", 100)
    api_version = constants.API_VERSION
    if next_link:
        queries = urlparse.parse_qs(urlparse.urlparse(next_link).query)
        start_index = int(queries['$skip'][0])
        max_page_size = int(queries['$top'][0])
        api_version = queries['api-version'][0]
    with _handle_response_error():
        feed_element = cast(
            ElementTree,
            await list_func(
                skip=start_index, top=max_page_size,
                api_version=api_version,
                **kwargs
            )
        )
    return feed_element
