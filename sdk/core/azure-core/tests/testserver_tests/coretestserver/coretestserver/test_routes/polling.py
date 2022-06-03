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
from .helpers import get_base_url, assert_with_message

polling_api = Blueprint('polling_api', __name__)


@polling_api.route('/post/location-and-operation-location', methods=['POST'])
def post_with_location_and_operation_location_initial():
    base_url = get_base_url(request)
    return Response(
        '{"properties":{"provisioningState": "InProgress"}}',
        headers={
            'location': '{}/polling/location-url'.format(base_url),
            'operation-location': '{}/polling/operation-location-url'.format(base_url),
        },
        status=202
    )

@polling_api.route('/location-url', methods=['GET'])
def location_url():
    return Response(
        '{"location_result": true}',
        status=200
    )

@polling_api.route('/location-no-body-url', methods=['GET'])
def location_no_body_url():
    return Response(
        status=200
    )

@polling_api.route('/operation-location-url', methods=['GET'])
def operation_location_url():
    return Response(
        '{"status": "Succeeded"}',
        status=200
    )

@polling_api.route('/post/location-and-operation-location-no-body', methods=['POST'])
def post_with_location_and_operation_location_initial_no_body():
    base_url = get_base_url(request)
    return Response(
        '{"properties":{"provisioningState": "InProgress"}}',
        headers={
            'location': '{}/polling/location-no-body-url'.format(base_url),
            'operation-location': '{}/polling/operation-location-url'.format(base_url),
        },
        status=202
    )

@polling_api.route('/post/resource-location', methods=['POST'])
def resource_location():
    base_url = get_base_url(request)
    return Response(
        '',
        status=202,
        headers={
            'operation-location': '{}/polling/post/resource-location/operation-location-url'.format(base_url),
        }
    )

@polling_api.route('/post/resource-location/operation-location-url', methods=['GET'])
def resource_location_operation_location():
    base_url = get_base_url(request)
    resource_location = '{}/polling/location-url'.format(base_url)
    return Response(
        '{"status": "Succeeded", "resourceLocation": "' + resource_location + '"}',
        status=200,
    )

@polling_api.route('/no-polling', methods=['PUT'])
def no_polling():
    return Response(
        '{"properties":{"provisioningState": "Succeeded"}}',
        status=201
    )

@polling_api.route('/operation-location', methods=["DELETE", "POST", "PUT", "PATCH", "GET"])
def operation_location():
    base_url = get_base_url(request)
    return Response(
        status=201,
        headers={
            'operation-location': '{}/polling/operation-location-url'.format(base_url),
        }
    )

@polling_api.route('/bad-operation-location', methods=["PUT", "PATCH", "DELETE", "POST"])
def bad_operation_location():
    return Response(
        status=201,
        headers={
            'operation-location': 'http://localhost:5000/does-not-exist',
        }
    )

@polling_api.route('/location', methods=["PUT", "PATCH", "DELETE", "POST"])
def location():
    base_url = get_base_url(request)
    return Response(
        status=201,
        headers={
            'location': '{}/polling/location-url'.format(base_url),
        }
    )

@polling_api.route('/bad-location', methods=["PUT", "PATCH", "DELETE", "POST"])
def bad_location():
    return Response(
        status=201,
        headers={
            'location': 'http://localhost:5000/does-not-exist',
        }
    )

@polling_api.route('/initial-body-invalid', methods=["PUT"])
def initial_body_invalid():
    base_url = get_base_url(request)
    return Response(
        "",
        status=201,
        headers={
            'location': '{}/polling/location-url'.format(base_url),
        }
    )

@polling_api.route('/request-id', methods=["POST"])
def request_id():
    base_url = get_base_url(request)
    return Response(
        "",
        status=201,
        headers={
            'location': '{}/polling/request-id-location'.format(base_url),
        }
    )

@polling_api.route('/request-id-location', methods=["GET"])
def request_id_location():
    assert_with_message("request id", request.headers['X-Ms-Client-Request-Id'], "123456789")
    return Response(
        '{"status": "Succeeded"}',
        status=200
    )

@polling_api.route('/polling-with-options', methods=["PUT"])
def polling_with_options_first():
    base_url = get_base_url(request)
    return Response(
        '{"properties":{"provisioningState": "InProgress"}}',
        headers={
            'location': '{}/polling/final-get-with-location'.format(base_url),
            'operation-location': '{}/polling/post/resource-location/operation-location-url'.format(base_url),
        },
        status=202
    )

@polling_api.route('/final-get-with-location', methods=["GET"])
def polling_with_options_final_get_with_location():
    return Response(
        '{"returnedFrom": "locationHeaderUrl"}',
        status=200
    )
