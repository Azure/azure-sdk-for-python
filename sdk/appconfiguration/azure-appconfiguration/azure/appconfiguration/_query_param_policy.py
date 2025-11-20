# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from azure.core.pipeline.policies import HTTPPolicy


class QueryParamPolicy(HTTPPolicy):
    """Policy to normalize query parameters by converting keys to lowercase and sorting alphabetically.
    
    This policy ensures query parameter keys are converted to lowercase and sorted alphabetically
    to support Azure Front Door as a CDN.
    """

    def send(self, request):
        """Normalize query parameters before sending the request.
        
        :param request: The pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The pipeline response
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        try:
            # Parse the current URL
            parsed_url = urlparse(request.http_request.url)
            
            if parsed_url.query:
                # Parse query parameters
                query_params = parse_qsl(parsed_url.query, keep_blank_values=True)
                
                # Convert keys to lowercase and sort alphabetically
                normalized_params = sorted(
                    [(key.lower(), value) for key, value in query_params],
                    key=lambda x: x[0]
                )
                
                # Rebuild the query string
                new_query = urlencode(normalized_params)
                
                # Rebuild the URL with normalized query parameters
                new_url = urlunparse((
                    parsed_url.scheme,
                    parsed_url.netloc,
                    parsed_url.path,
                    parsed_url.params,
                    new_query,
                    parsed_url.fragment
                ))
                
                # Update the request URL
                request.http_request.url = new_url
        except Exception:  # pylint: disable=broad-except
            # If URL normalization fails, continue with the original URL
            # This ensures the policy doesn't break existing functionality
            pass
        
        return self.next.send(request)
