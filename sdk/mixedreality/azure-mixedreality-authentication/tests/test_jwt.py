# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.mixedreality.authentication.utils._jwt import _retrieve_jwt_expiration_timestamp

class TestJwt:
    def test_retrieve_jwt_expiration_timestamp(self):
        # Note: The trailing "." on the end indicates an empty signature indicating that this JWT is not signed.
        jwt_value = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJlbWFpbCI6IkJvYkBjb250b3NvLmNvbSIsImdpdmVuX25hbWUiOiJCb2IiLCJpc3MiOiJodHRwOi8vRGVmYXVsdC5Jc3N1ZXIuY29tIiwiYXVkIjoiaHR0cDovL0RlZmF1bHQuQXVkaWVuY2UuY29tIiwiaWF0IjoiMTYxMDgxMjI1MCIsIm5iZiI6IjE2MTA4MTI1NTAiLCJleHAiOiIxNjEwODk4NjUwIn0=."
        expected_expiration_timestamp = 1610898650 # 1/17/2021 3:50:50 PM UTC

        actual = _retrieve_jwt_expiration_timestamp(jwt_value)

        assert actual is not None
        assert actual == expected_expiration_timestamp

    def test_retrieve_jwt_expiration_timestamp_invalid_parameter(self):
        with pytest.raises(ValueError):
            _retrieve_jwt_expiration_timestamp(None)

    def test_retrieve_jwt_expiration_timestamp_invalid_structure(self):
        # JWT value with missing signature section on the end.
        jwt_value = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJlbWFpbCI6IkJvYkBjb250b3NvLmNvbSIsImdpdmVuX25hbWUiOiJCb2IiLCJpc3MiOiJodHRwOi8vRGVmYXVsdC5Jc3N1ZXIuY29tIiwiYXVkIjoiaHR0cDovL0RlZmF1bHQuQXVkaWVuY2UuY29tIiwiaWF0IjoiMTYxMDgxMjI1MCIsIm5iZiI6IjE2MTA4MTI1NTAiLCJleHAiOiIxNjEwODk4NjUwIn0="

        with pytest.raises(ValueError):
            _retrieve_jwt_expiration_timestamp(jwt_value)

    def test_retrieve_jwt_expiration_timestamp_invalid_payload(self):
        # JWT value with missing payload.
        jwt_value = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.."

        with pytest.raises(ValueError):
            _retrieve_jwt_expiration_timestamp(jwt_value)

    def test_retrieve_jwt_expiration_timestamp_invalid_exp(self):
        # JWT value with missing expiration field.
        jwt_value = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJlbWFpbCI6IkJvYkBjb250b3NvLmNvbSIsImdpdmVuX25hbWUiOiJCb2IiLCJpc3MiOiJodHRwOi8vRGVmYXVsdC5Jc3N1ZXIuY29tIiwiYXVkIjoiaHR0cDovL0RlZmF1bHQuQXVkaWVuY2UuY29tIiwiaWF0IjoiMTYxMDgxMjI1MCIsIm5iZiI6IjE2MTA4MTI1NTAifQ==."

        with pytest.raises(ValueError):
            _retrieve_jwt_expiration_timestamp(jwt_value)
