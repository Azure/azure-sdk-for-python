# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.exceptions import HttpResponseError, map_error
from azure.keyvault.keys._shared.exceptions import error_map
import pytest

from keys_helpers import mock_response


def test_error_map():
    """error_map should map all error codes to a subclass of HttpResponseError"""

    error_code = "oops"
    error_message = "something went wrong"
    error_body = {"error": {"code": error_code, "message": error_message}}  # Key Vault error responses look like this

    for status_code in range(400, 600):
        response = mock_response(status_code=status_code, json_payload=error_body)

        with pytest.raises(HttpResponseError) as ex:
            map_error(status_code, response, error_map)

        # the concrete error should include error information returned by Key Vault
        assert error_code in ex.value.message
        assert error_message in ex.value.message
