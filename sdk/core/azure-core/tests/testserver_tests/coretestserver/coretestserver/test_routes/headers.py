# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from flask import (
    Response,
    Blueprint,
    request
)

headers_api = Blueprint('headers_api', __name__)

@headers_api.route("/case-insensitive", methods=['GET'])
def case_insensitive():
    return Response(
        status=200,
        headers={
            "lowercase-header": "lowercase",
            "ALLCAPS-HEADER": "ALLCAPS",
            "CamelCase-Header": "camelCase",
        }
    )

@headers_api.route("/empty", methods=['GET'])
def empty():
    return Response(
        status=200,
        headers={}
    )

@headers_api.route("/duplicate/numbers", methods=['GET'])
def duplicate_numbers():
    return Response(
        status=200,
        headers=[("a", "123"), ("a", "456"), ("b", "789")]
    )

@headers_api.route("/duplicate/case-insensitive", methods=['GET'])
def duplicate_case_insensitive():
    return Response(
        status=200,
        headers=[("Duplicate-Header", "one"), ("Duplicate-Header", "two"), ("duplicate-header", "three")]
    )

@headers_api.route("/duplicate/commas", methods=['GET'])
def duplicate_commas():
    return Response(
        status=200,
        headers=[("Set-Cookie", "a,  b"), ("Set-Cookie", "c")]
    )

@headers_api.route("/ordered", methods=['GET'])
def ordered():
    return Response(
        status=200,
        headers={"a": "a", "b": "b", "c": "c"},
    )
