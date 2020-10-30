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

from .exceptions import HttpResponseError

class PagingMethodABC():

    # making requests

    def get_initial_page(self):
        """Gets the page from the first request to the service
        """
        raise NotImplementedError("This method needs to be implemented")

    def get_next_link(self, continuation_token: str):
        """Gets the next link to make a request against
        """
        raise NotImplementedError("This method needs to be implemented")

    def get_next_request_parameters(self):
        """Gets parameters to make next request
        """
        raise NotImplementedError("This method needs to be implemented")

    def get_next(self, continuation_token: str):
        """Gets next page
        """
        raise NotImplementedError("This method needs to be implemented")

    def finished(self, continuation_token):
        """When paging is finished
        """
        raise NotImplementedError("This method needs to be implemented")


    # extracting data from response

    def get_list_elements(self, pipeline_response, deserialized):
        """Extract the list elements from the current page to return to users
        """
        raise NotImplementedError("This method needs to be implemented")

    def mutate_list(self, pipeline_response, list_of_elem):
        """Mutate list of elements in current page, i.e. if users passed in a cls calback
        """
        raise NotImplementedError("This method needs to be implemented")

    def get_continuation_token(self, pipeline_response, deserialized):
        """Get the continuation token from the current page
        """
        raise NotImplementedError("This method needs to be implemented")

    def extract_data(self, pipeline_response):
        """Return the continuation token and current list of elements to PageIterator
        """
        raise NotImplementedError("This method needs to be implemented")


class BasicPagingMethod(PagingMethodABC):
    """This is the most common paging method. It uses the continuation token
    as the next link
    """

    def __init__(
        self,
        client,
        deserialize_output,
        initial_request=None,
        initial_response=None,
        cls=None,
        path_format_arguments=None,
        item_name="value",
        continuation_token_name="next_link",
        **kwargs
    ):
        self._client = client
        self._deserialize_output = deserialize_output
        self._initial_request = initial_request
        self._cls = cls
        self._path_format_arguments = path_format_arguments
        self._initial_response = initial_response
        self._item_name = item_name
        self._continuation_token_name = continuation_token_name
        self._did_a_call_already = False

    def get_initial_page(self):
        # TODO: allow stream calls as well
        if self._initial_response:
            self._initial_request = self._initial_response.http_response.request
            return self._initial_response
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

    def get_next(self, continuation_token):
        if not self._did_a_call_already:
            response = self.get_initial_page()
            self._initial_response = response
        else:
            next_link = self.get_next_link(continuation_token)
            if self._path_format_arguments:
                next_link = self._client.format_url(next_link, **self._path_format_arguments)
            request_params = self.get_next_request_parameters()
            request = self._client.get(next_link, **request_params)
            response = self._client._pipeline.run(request, stream=False)


        self._did_a_call_already = True
        code = response.http_response.status_code
        if not (200 <= code <= 299):
            raise HttpResponseError(response=response.http_response)

        return response

    def finished(self, continuation_token):
        return continuation_token is None and self._did_a_call_already

    def get_list_elements(self, pipeline_response, deserialized):
        if not hasattr(deserialized, self._item_name):
            raise ValueError(
                "The response object does not have property '{}' to extract element list from".format(self._item_name)
            )
        return getattr(deserialized, self._item_name)

    def mutate_list(self, pipeline_response, list_of_elem):
        if self._cls:
            list_of_elem = self._cls(list_of_elem)
        return iter(list_of_elem)

    def get_continuation_token(self, pipeline_response, deserialized):
        if not self._continuation_token_name:
            return None
        if not hasattr(deserialized, self._continuation_token_name):
            raise ValueError(
                "The response object does not have property '{}' to extract continuation token from".format(self._continuation_token_name)
            )
        return getattr(deserialized, self._continuation_token_name)

    def extract_data(self, pipeline_response):
        deserialized = self._deserialize_output(pipeline_response)
        list_of_elem = self.get_list_elements(pipeline_response, deserialized)
        list_of_elem = self.mutate_list(pipeline_response, list_of_elem)
        continuation_token = self.get_continuation_token(pipeline_response, deserialized)
        return continuation_token, list_of_elem


class SeperateNextOperationPagingMethod(BasicPagingMethod):
    """Use this paging method if the swagger defines a separate next operation
    """

    def __init__(
        self,
        client,
        deserialize_output,
        prepare_request_to_separate_next_operation,
        initial_request=None,
        initial_response=None,
        cls=None,
        path_format_arguments=None,
        item_name="value",
        continuation_token_name="next_link",
        **kwargs
    ):
        super(SeperateNextOperationPagingMethod, self).__init__(
            client=client,
            deserialize_output=deserialize_output,
            initial_request=initial_request,
            initial_response=initial_response,
            cls=cls,
            path_format_arguments=path_format_arguments,
            item_name=item_name,
            continuation_token_name=continuation_token_name,
        )
        self._prepare_request_to_separate_next_operation = prepare_request_to_separate_next_operation
        self._next_request = None

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

class ContinuationTokenPagingMethod(BasicPagingMethod):
    def __init__(
        self,
        client,
        deserialize_output,
        continuation_token_input_parameter,
        initial_request=None,
        initial_response=None,
        cls=None,
        path_format_arguments=None,
        item_name="value",
        continuation_token_name="next_link",
        **kwargs
    ):
        super(ContinuationTokenPagingMethod, self).__init__(
            client=client,
            deserialize_output=deserialize_output,
            initial_request=initial_request,
            initial_response=initial_response,
            cls=cls,
            path_format_arguments=path_format_arguments,
            item_name=item_name,
            continuation_token_name=continuation_token_name,
        )
        self._continuation_token_input_parameter = continuation_token_input_parameter

    def get_next_link(self, continuation_token: str):
        return self._initial_response.request.url

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
