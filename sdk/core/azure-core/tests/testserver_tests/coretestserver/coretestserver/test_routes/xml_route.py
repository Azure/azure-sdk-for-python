# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import xml.etree.ElementTree as ET
from flask import (
    Response,
    Blueprint,
    request,
)
from .helpers import assert_with_message

xml_api = Blueprint('xml_api', __name__)

@xml_api.route('/basic', methods=['GET', 'PUT'])
def basic():
    basic_body = """<?xml version='1.0' encoding='UTF-8'?>
<slideshow
        title="Sample Slide Show"
        date="Date of publication"
        author="Yours Truly">
    <slide type="all">
        <title>Wake up to WonderWidgets!</title>
    </slide>
    <slide type="all">
        <title>Overview</title>
        <item>Why WonderWidgets are great</item>
        <item></item>
        <item>Who buys WonderWidgets</item>
    </slide>
</slideshow>"""

    if request.method == 'GET':
        return Response(basic_body, status=200)
    elif request.method == 'PUT':
        assert_with_message("content length", str(len(request.data)), request.headers["Content-Length"])
        parsed_xml = ET.fromstring(request.data.decode("utf-8"))
        assert_with_message("tag", "slideshow", parsed_xml.tag)
        attributes = parsed_xml.attrib
        assert_with_message("title attribute", "Sample Slide Show", attributes['title'])
        assert_with_message("date attribute", "Date of publication", attributes['date'])
        assert_with_message("author attribute", "Yours Truly", attributes['author'])
        return Response(status=200)
    return Response("You have passed in method '{}' that is not 'GET' or 'PUT'".format(request.method), status=400)
