import unittest
from unittest.mock import Mock, MagicMock

from azure.core.exceptions import (
    HttpResponseError,
    ClientAuthenticationError,
    ResourceNotFoundError,
    ResourceExistsError,
    ResourceModifiedError,
)
from azure.batch._patch import BatchExceptionPolicy, BatchErrorFormat


class TestBatchErrorFormat(unittest.TestCase):
    def test_batch_error_format_with_values(self):
        odata_error = {
            "code": 401,
            "message": {"lang": "en-us", "value": "Property value is invalid"},
            "values": [
                {"key": "property1", "value": "error_details"},
                {"key": "property2", "value": "more_error_details"},
            ],
        }

        batch_error = BatchErrorFormat(odata_error)
        self.assertEqual(batch_error.details[0].code, "property1")
        self.assertEqual(batch_error.details[1].code, "property2")

    def test_batch_error_format_without_values(self):
        odata_error = {
            "error": {"code": "InvalidProperty", "message": {"lang": "en-us", "value": "Property value is invalid"}}
        }
        batch_error = BatchErrorFormat(odata_error)
        self.assertFalse(hasattr(batch_error, "values"))

    def test_invalid_odata_error(self):
        odata_error = {"code": "InvalidProperty", "message": "This is not an object"}

        with self.assertRaises(TypeError):
            BatchErrorFormat(odata_error)


class TestResponseHandler(unittest.TestCase):
    def test_client_authentication_error(self):
        mock_http_response = Mock()
        mock_http_response.status_code = 401
        mock_http_response.json.return_value = {
            "code": 401,
            "message": "Authentication failed",
        }

        mock_request_headers = Mock()
        mock_request_headers.get.return_value = None
        mock_http_request = Mock()
        mock_http_request.headers = mock_request_headers

        mock_response = Mock()
        mock_response.http_response = mock_http_response
        mock_request = Mock()
        mock_request.http_request = mock_http_request

        policy = BatchExceptionPolicy()

        with self.assertRaises(ClientAuthenticationError):
            policy.on_response(mock_request, mock_response)

    def test_resource_not_found_error(self):
        mock_http_response = Mock()
        mock_http_response.status_code = 404
        mock_http_response.json.return_value = {
            "code": 404,
            "message": "Resource not found",
        }

        mock_request_headers = Mock()
        mock_request_headers.get.return_value = None
        mock_http_request = Mock()
        mock_http_request.headers = mock_request_headers

        mock_response = Mock()
        mock_response.http_response = mock_http_response
        mock_request = Mock()
        mock_request.http_request = mock_http_request

        policy = BatchExceptionPolicy()

        with self.assertRaises(ResourceNotFoundError):
            policy.on_response(mock_request, mock_response)

    def test_if_match_resource_not_found(self):
        mock_http_response = Mock()
        mock_http_response.status_code = 500
        mock_http_response.json.return_value = {
            "code": 500,
            "message": "Server error",
        }

        mock_request_headers = Mock()
        mock_request_headers.get.side_effect = lambda header: "*" if header == "If-Match" else None
        mock_http_request = Mock()
        mock_http_request.headers = mock_request_headers

        mock_response = Mock()
        mock_response.http_response = mock_http_response
        mock_request = Mock()
        mock_request.http_request = mock_http_request

        policy = BatchExceptionPolicy()

        with self.assertRaises(ResourceNotFoundError):
            policy.on_response(mock_request, mock_response)

    def test_if_none_match_resource_not_found(self):
        mock_http_response = Mock()
        mock_http_response.status_code = 500
        mock_http_response.json.return_value = {
            "code": 500,
            "message": "Server error",
        }

        mock_request_headers = Mock()
        mock_request_headers.get.side_effect = lambda header: "*" if header == "If-None-Match" else None
        mock_http_request = Mock()
        mock_http_request.headers = mock_request_headers

        mock_response = Mock()
        mock_response.http_response = mock_http_response
        mock_request = Mock()
        mock_request.http_request = mock_http_request

        policy = BatchExceptionPolicy()

        with self.assertRaises(ResourceNotFoundError):
            policy.on_response(mock_request, mock_response)

    def test_if_match_takes_precedence_over_if_none_match(self):
        mock_http_response = Mock()
        mock_http_response.status_code = 400
        mock_http_response.json.return_value = {
            "code": 400,
            "message": "Bad request",
        }

        mock_request_headers = Mock()

        def get_header(header):
            if header == "If-Match":
                return "foobar"
            elif header == "If-None-Match":
                return "*"
            return None

        mock_request_headers.get.side_effect = get_header
        mock_http_request = Mock()
        mock_http_request.headers = mock_request_headers

        mock_response = Mock()
        mock_response.http_response = mock_http_response
        mock_request = Mock()
        mock_request.http_request = mock_http_request

        policy = BatchExceptionPolicy()

        with self.assertRaises(ResourceModifiedError):
            policy.on_response(mock_request, mock_response)

    def test_header_takes_precedence_over_status_code(self):
        mock_http_response = Mock()
        mock_http_response.status_code = 401
        mock_http_response.json.return_value = {
            "code": 401,
            "message": "Authentication failed",
        }

        mock_request_headers = Mock()
        mock_request_headers.get.side_effect = lambda header: "*" if header == "If-Match" else None
        mock_http_request = Mock()
        mock_http_request.headers = mock_request_headers

        mock_response = Mock()
        mock_response.http_response = mock_http_response
        mock_request = Mock()
        mock_request.http_request = mock_http_request

        policy = BatchExceptionPolicy()

        with self.assertRaises(ResourceNotFoundError):
            policy.on_response(mock_request, mock_response)
