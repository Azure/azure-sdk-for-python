# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import cast
from xml.etree.ElementTree import ElementTree


import urllib.parse as urlparse

from ...management import _constants as constants
from ...management._handle_response_error import _handle_response_error

# This module defines functions get_next_template and extract_data_template.
# Application code uses functools.partial to substantialize their params and builds an
# azure.core.async_paging.AsyncItemPaged instance with the two substantialized functions.

# The following is an ATOM feed XML list of QueueDescription with page size = 2.
# Tag <feed> has 2 (the page size) children <entry> tags.
# Tag <link rel="next" .../> tells the link to the next page.
# The whole XML will be deserialized into an XML ElementTree.
# Then model class QueueDescriptionFeed deserializes the ElementTree into a QueueDescriptionFeed instance.
# (QueueDescriptionFeed is defined in file ../../management/_generated/models/_models.py and _models_py3.py)
# Function get_next_template gets the next page of XML data like this one and returns the ElementTree.
# Function extract_data_template deserialize data from the ElementTree and provide link to the next page.
# azure.core.async_paging.AsyncItemPaged orchestrates the data flow between them.

# <feed xmlns="http://www.w3.org/2005/Atom">
# 	<title type="text">Queues</title>
# 	<id>https://servicebusname.servicebus.windows.net/$Resources/queues?$skip=0&amp;$top=2&amp;api-version=2017-04</id>
# 	<updated>2020-06-30T23:49:41Z</updated>
# 	<link rel="self" href="https://servicebusname.servicebus.windows.net/$Resources/queues?
# 	$skip=0&amp;$top=2&amp;api-version=2017-04"/>
# 	<link rel="next" href="https://servicebusname.servicebus.windows.net/$Resources/queues?
# 	%24skip=2&amp;%24top=2&amp;api-version=2017-04"/>
#
# 	<entry xml:base="https://servicebusname.servicebus.windows.net/$Resources/queues?
# 	$skip=0&amp;$top=2&amp;api-version=2017-04">
# 		<id>https://servicebusname.servicebus.windows.net/5?api-version=2017-04</id>
# 		<title type="text">5</title>
# 		<published>2020-06-05T00:24:34Z</published>
# 		<updated>2020-06-25T05:57:29Z</updated>
# 		<author>
# 			<name>servicebusname</name>
# 		</author>
# 		<link rel="self" href="../5?api-version=2017-04"/>
# 		<content type="application/xml">
# 			<QueueDescription xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
# 			xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
# 			...
# 			</QueueDescription>
# 		</content>
# 	</entry>
# 	<entry xml:base="https://servicebusname.servicebus.windows.net/$Resources/queues?
# 	$skip=0&amp;$top=2&amp;api-version=2017-04">
# 		<id>https://servicebusname.servicebus.windows.net/6?api-version=2017-04</id>
# 		<title type="text">6</title>
# 		<published>2020-06-15T19:49:35Z</published>
# 		<updated>2020-06-15T19:49:35Z</updated>
# 		<author>
# 			<name>servicebusname</name>
# 		</author>
# 		<link rel="self" href="../6?api-version=2017-04"/>
# 		<content type="application/xml">
# 			<QueueDescription xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
# 			xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
# 			...
# 			</QueueDescription>
# 		</content>
# 	</entry>
# </feed>


async def extract_data_template(feed_class, convert, feed_element):
    """A function that will be partialized to build a function used by AsyncItemPaged.

    It deserializes the ElementTree returned from function `get_next_template`, returns data in an iterator and
    the link to next page.

    azure.core.async_paging.AsyncItemPaged will use the returned next page to call a partial function created
    from `get_next_template` to fetch data of next page.

    """
    deserialized = feed_class.deserialize(feed_element)
    list_of_qd = [convert(x) if convert else x for x in deserialized.entry]
    next_link = None
    # when the response xml has two <link> tags, the 2nd if the next-page link.
    if deserialized.link and len(deserialized.link) == 2:
        next_link = deserialized.link[1].href
    return next_link, iter(
        list_of_qd
    )  # when next_page is None, AsyncPagedItem will stop fetch next page data.


async def extract_rule_data_template(feed_class, convert, feed_element):
    """Special version of function extrat_data_template for Rule.

    Pass both the XML entry element and the rule instance to function `convert`. Rule needs to extract
    KeyValue from XML Element and set to Rule model instance manually. The autorest/msrest serialization/deserialization
    doesn't work for this special part.
    After autorest is enhanced, this method can be removed.
    Refer to autorest issue https://github.com/Azure/autorest/issues/3535
    """
    deserialized = feed_class.deserialize(feed_element)
    next_link = None
    if deserialized.link and len(deserialized.link) == 2:
        next_link = deserialized.link[1].href
    if deserialized.entry:
        list_of_entities = [
            convert(*x) if convert else x
            for x in zip(
                feed_element.findall(constants.ATOM_ENTRY_TAG), deserialized.entry
            )
        ]
    else:
        list_of_entities = []
    return next_link, iter(list_of_entities)


async def get_next_template(
    list_func, *args, start_index=0, max_page_size=100, **kwargs
):
    """Call list_func to get the XML data and deserialize it to XML ElementTree.

    azure.core.async_paging.AsyncItemPaged will call `extract_data_template` and use the returned
    XML ElementTree to call a partial function created from `extrat_data_template`.

    """
    api_version = constants.API_VERSION
    if args[0]:  # It's next link. It's None for the first page.
        queries = urlparse.parse_qs(urlparse.urlparse(args[0]).query)
        start_index = int(queries[constants.LIST_OP_SKIP][0])
        max_page_size = int(queries[constants.LIST_OP_TOP][0])
        api_version = queries[constants.API_VERSION_PARAM_NAME][0]
    with _handle_response_error():
        feed_element = cast(
            ElementTree,
            await list_func(
                skip=start_index, top=max_page_size, api_version=api_version, **kwargs
            ),
        )
    return feed_element
