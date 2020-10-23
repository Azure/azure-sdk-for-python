# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------


class _PagingOption(str, Enum):
    """Known paging options from Swagger."""

    TOKEN_INPUT_PARAMETER = "continuation-token-input-parameter"  # for token paging, which parameter will hold continuation token

class BadStatus(Exception):
    pass


class BadResponse(Exception):
    pass


class OperationFailed(Exception):
    pass

def _raise_if_bad_http_status_and_method(response):
    # type: (ResponseType) -> None
    """Check response status code is valid.

    Must be 200, 201, 202, or 204.

    :raises: BadStatus if invalid status.
    """
    code = response.status_code
    if code in {200, 201, 202, 204}:
        return
    raise BadStatus(
        "Invalid return status {!r} for {!r} operation".format(
            code, response.request.method
        )
    )


class PagingMethodABC():
    def __init__(
        self,
        client,
        extract_data,
        initial_request=None,
        path_format_arguments=None,
        **kwargs
    ):
        self._client = client
        self.extract_data = extract_data
        self._initial_request = initial_request
        self._path_format_arguments = path_format_arguments
        self._did_a_call_already = False

    def get_initial_page(self):
        raise NotImplementedError("This method needs to be implemented")

    def get_next_link(self, continuation_token: str):
        raise NotImplementedError("This method needs to be implemented")

    def get_next_request_parameters(self):
        raise NotImplementedError("This method needs to be implemented")

    def get_next(self, continuation_token: str):
        if not self._did_a_call_already:
            response = self.get_initial_page()
        else:
            next_link = self.get_next_link(continuation_token)
            if self._path_format_arguments:
                next_link = self._client.format_url(next_link, **self._path_format_arguments)
            request_params = self.get_next_request_parameters()
            request = self._client.get(next_link, **request_params)
            response = self._client._pipeline.run(self._initial_request, stream=False)


        self._did_a_call_already = True
        code = response.http_response.status_code
        if not (200 <= code <= 299):
            raise HttpResponseError(response=response.http_response)

        return response

class PagingMethod(PagingMethodABC):
    """This is the most common paging method. It uses the continuation token
    as the next link
    """

    def get_initial_page(self):
        # TODO: allow stream calls as well
        response = self._client._pipeline.run(self._initial_request, stream=False)
        return response

    def get_next_link(self, continuation_token: str):
        return continuation_token

    def get_next_request_parameters(self):
        query_parameters = self._initial_request.query
        header_parameters = self._initial_request.headers
        body_parameters = self._initial_request.body
        return {
            "params": query_parameters,
            "headers": header_parameters,
            "content": body_parameters
        }


class PagingMethodWithSeparateNextOperation(PagingMethodABC):
    """Use this paging method if the swagger defines a separate next operation
    """
    def __init__(
        self,
        client,
        extract_data,
        prepare_request_to_separate_next_operation,
        initial_request,
        path_format_arguments=None,
        **kwargs
    ):
        super(PagingMethodWithSeparateNextOperation, self).__init__(
            client=client,
            extract_data=extract_data,
            initial_request=initial_request,
            path_format_arguments=path_format_arguments
        )
        self._prepare_request_to_separate_next_operation
        self._next_request = None

    def get_initial_page(self):
        # TODO: allow stream calls as well
        response = self._client._pipeline.run(self._initial_request, stream=False)
        return response

    def get_next_link(self, continuation_token: str):
        self._next_request = self._prepare_request_to_separate_next_operation(continuation_token)
        return self._next_request.url

    def get_next_request_parameters(self):
        query_parameters = self._next_request.query or self._initial_request.query
        header_parameters = self._next_request.headers or self._initial_request.headers
        body_parameters =self._next_request.body or  self._initial_request.body
        return {
            "params": query_parameters,
            "headers": header_parameters,
            "content": body_parameters
        }

class PagingMethodContinuationToken(PagingMethodABC):
    def __init__(
        self,
        client,
        extract_data,
        initial_request,
        continuation_token_input_parameter,
        path_format_arguments=None,
        **kwargs
    ):
        super(PagingMethodContinuationToken, self).__init__(
            client=client,
            extract_data=extract_data,
            initial_request=initial_request,
            path_format_arguments=path_format_arguments
        )
        self._continuation_token_input_parameter = continuation_token_input_parameter

    def get_initial_page(self):
        # TODO: allow stream calls as well
        response = self._client._pipeline.run(self._initial_request, stream=False)
        return response

    def get_next_link(self, continuation_token: str):
        return self._initial_request.url

    def _add_continuation_token_param(self, request_parameters):
        set_continuation_token = False
        for api_parameter_type, api_parameters in request_parameters:
            for param_name, param_value in api_parameters.items():
                if param_name == self._continuation_token_input_parameter:
                    request_params[api_parameter_type][param_name] = self._continuation_token
                    set_continuation_token = True
                    break

        if not set_continuation_token:
            raise ValueError(
                "The value provided in paging_options for the input parameter that accepts "
                "the continuation token {} is not present in the API parameters".format(self._paging_options[_PagingOption.TOKEN_INPUT_PARAMETER])
            )

    def get_next_request_parameters(self):
        query_parameters = self._initial_request.query
        header_parameters = self._initial_request.headers
        body_parameters = self._initial_request.body
        request_parameters = {
            "params": query_parameters,
            "headers": header_parameters,
            "content": body_parameters
        }
        self._add_continuation_token_param(request_parameters)
        return request_parameters

class PagingMethodWithInitialResponse(PagingMethodABC):
    def __init__(
        self,
        client,
        extract_data,
        initial_response,
        path_format_arguments=None,
        **kwargs
    ):
        super(PagingMethodContinuationToken, self).__init__(
            client=client,
            extract_data=extract_data,
            path_format_arguments=path_format_arguments
        )
        self._initial_response = initial_response

    def get_initial_page(self):
        return self._initial_response