# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from collections import defaultdict
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode, quote
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

                # Convert keys to lowercase, drop empty keys
                lowered_params = [(key.lower(), value) for key, value in query_params if key]

                # Sort all params by key, and for duplicate keys, non-empty values lexicographically, empty values last

                grouped = defaultdict(list)
                for k, v in lowered_params:
                    grouped[k].append(v)
                normalized_params = []
                for k in sorted(grouped.keys()):
                    values = grouped[k]
                    if len(values) > 1:
                        # Empty values last, space values second to last, other non-empty values sorted
                        # lexicographically first
                        def sort_key(v):
                            if v == "":
                                return (2, "")  # empty string last
                            if v == " ":
                                return (1, v)  # space second to last
                            return (0, v)  # other non-empty values first

                        values = sorted(values, key=sort_key)
                    normalized_params.extend([(k, v) for v in values])

                # Rebuild the query string, encoding spaces as %20 instead of +
                new_query = urlencode(normalized_params, quote_via=quote)

                # Rebuild the URL with normalized query parameters
                new_url = urlunparse(
                    (
                        parsed_url.scheme,
                        parsed_url.netloc,
                        parsed_url.path,
                        parsed_url.params,
                        new_query,
                        parsed_url.fragment,
                    )
                )

                # Update the request URL
                request.http_request.url = new_url
        except Exception:  # pylint: disable=broad-except
            # If URL normalization fails, continue with the original URL
            # This ensures the policy doesn't break existing functionality
            pass

        return self.next.send(request)
