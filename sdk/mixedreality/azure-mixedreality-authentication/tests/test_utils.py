# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.mixedreality.authentication._utils import generate_cv_base, retrieve_jwt_expiration_timestamp


class TestUtils:
    def test_generate_cv_base(self):
        cv = generate_cv_base()

        assert cv is not None
        assert len(cv) == 22

    def test_generate_cv_base_are_random(self):
        cv1 = generate_cv_base()
        cv2 = generate_cv_base()

        assert cv1 is not None
        assert cv2 is not None
        assert cv1 != cv2

    def test_retrieve_jwt_expiration_timestamp_with_padding(self):
        # Note: The trailing "." on the end indicates an empty signature indicating that this JWT is not signed.
        jwt_value = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJlbWFpbCI6IkJvYkBjb250b3NvLmNvbSIsImdpdmVuX25hbWUiOiJCb2IiLCJpc3MiOiJodHRwOi8vRGVmYXVsdC5Jc3N1ZXIuY29tIiwiYXVkIjoiaHR0cDovL0RlZmF1bHQuQXVkaWVuY2UuY29tIiwiaWF0IjoiMTYxMDgxMjI1MCIsIm5iZiI6IjE2MTA4MTI1NTAiLCJleHAiOiIxNjEwODk4NjUwIn0=."
        expected_expiration_timestamp = 1610898650 # 1/17/2021 3:50:50 PM UTC

        actual = retrieve_jwt_expiration_timestamp(jwt_value)

        assert actual is not None
        assert actual == expected_expiration_timestamp

    def test_retrieve_jwt_expiration_timestamp_no_padding(self):
        # Note: The trailing "." on the end indicates an empty signature indicating that this JWT is not signed.
        #       The trailing "=" has been removed to test without base64 padding, which is apparently expected for JWT.
        jwt_value = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJlbWFpbCI6IkJvYkBjb250b3NvLmNvbSIsImdpdmVuX25hbWUiOiJCb2IiLCJpc3MiOiJodHRwOi8vRGVmYXVsdC5Jc3N1ZXIuY29tIiwiYXVkIjoiaHR0cDovL0RlZmF1bHQuQXVkaWVuY2UuY29tIiwiaWF0IjoiMTYxMDgxMjI1MCIsIm5iZiI6IjE2MTA4MTI1NTAiLCJleHAiOiIxNjEwODk4NjUwIn0."
        expected_expiration_timestamp = 1610898650 # 1/17/2021 3:50:50 PM UTC

        actual = retrieve_jwt_expiration_timestamp(jwt_value)

        assert actual is not None
        assert actual == expected_expiration_timestamp

    def test_retrieve_jwt_expiration_timestamp_invalid_parameter(self):
        with pytest.raises(ValueError):
            retrieve_jwt_expiration_timestamp(None)

    def test_retrieve_jwt_expiration_timestamp_invalid_structure(self):
        # JWT value with missing signature section on the end.
        jwt_value = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJlbWFpbCI6IkJvYkBjb250b3NvLmNvbSIsImdpdmVuX25hbWUiOiJCb2IiLCJpc3MiOiJodHRwOi8vRGVmYXVsdC5Jc3N1ZXIuY29tIiwiYXVkIjoiaHR0cDovL0RlZmF1bHQuQXVkaWVuY2UuY29tIiwiaWF0IjoiMTYxMDgxMjI1MCIsIm5iZiI6IjE2MTA4MTI1NTAiLCJleHAiOiIxNjEwODk4NjUwIn0="

        with pytest.raises(ValueError):
            retrieve_jwt_expiration_timestamp(jwt_value)

    def test_retrieve_jwt_expiration_timestamp_invalid_payload(self):
        # JWT value with missing payload.
        jwt_value = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.."

        with pytest.raises(ValueError):
            retrieve_jwt_expiration_timestamp(jwt_value)

    def test_retrieve_jwt_expiration_timestamp_invalid_exp(self):
        # JWT value with missing expiration field.
        jwt_value = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJlbWFpbCI6IkJvYkBjb250b3NvLmNvbSIsImdpdmVuX25hbWUiOiJCb2IiLCJpc3MiOiJodHRwOi8vRGVmYXVsdC5Jc3N1ZXIuY29tIiwiYXVkIjoiaHR0cDovL0RlZmF1bHQuQXVkaWVuY2UuY29tIiwiaWF0IjoiMTYxMDgxMjI1MCIsIm5iZiI6IjE2MTA4MTI1NTAifQ==."

        with pytest.raises(ValueError):
            retrieve_jwt_expiration_timestamp(jwt_value)
