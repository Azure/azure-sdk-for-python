session_token_header = 'x-ms-session-token'
request_context_header = 'request-context'
session_token_request_context = 'session-token'
feed_range_request_context = 'feed-range'


def add_request_context(last_response_headers, options) -> dict[str, str]:
    request_context = {}
    request_context[session_token_request_context] = last_response_headers[session_token_header]
    if 'partitionKey' in options:
        last_response_headers['partitionKey']
    last_response_headers[request_context_header] = request_context
    return last_response_headers
