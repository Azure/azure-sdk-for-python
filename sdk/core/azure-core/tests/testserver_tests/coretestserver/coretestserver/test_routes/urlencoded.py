# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from flask import (
    Response,
    Blueprint,
    request,
)
from .helpers import assert_with_message

urlencoded_api = Blueprint('urlencoded_api', __name__)

@urlencoded_api.route('/pet/add/<pet_id>', methods=['POST'])
def basic(pet_id):
    assert_with_message("pet_id", "1", pet_id)
    assert_with_message("content type", "application/x-www-form-urlencoded", request.content_type)
    assert_with_message("content length", 47, request.content_length)
    assert len(request.form) == 4
    assert_with_message("pet_type", "dog", request.form["pet_type"])
    assert_with_message("pet_food", "meat", request.form["pet_food"])
    assert_with_message("name", "Fido", request.form["name"])
    assert_with_message("pet_age", "42", request.form["pet_age"])
    return Response(status=200)
