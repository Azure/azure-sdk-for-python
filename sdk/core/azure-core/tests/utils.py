# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

def create_http_response(http_response, *args):
    if hasattr(http_response, "content"):
        return http_response(request=args[0], internal_response=args[1])
    return http_response(*args)

def is_rest_http_request(http_request):
    return hasattr(http_request, "content")

def is_rest_http_response(http_response):
    return hasattr(http_response, "content")
