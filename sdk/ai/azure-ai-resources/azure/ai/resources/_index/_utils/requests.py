# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Request utilities."""
import json


def create_session_with_retry(retry=3):
    """
    Create requests.session with retry.

    :type retry: int
    rtype: Response
    """
    import requests
    from requests.adapters import HTTPAdapter

    retry_policy = _get_retry_policy(num_retry=retry)

    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry_policy))
    session.mount("http://", HTTPAdapter(max_retries=retry_policy))
    return session


def _get_retry_policy(num_retry=3):
    """
    Request retry policy with increasing backoff.

    :return: Returns the msrest or requests REST client retry policy.
    :rtype: urllib3.Retry
    """
    from urllib3 import Retry

    status_forcelist = [413, 429, 500, 502, 503, 504]
    backoff_factor = 0.4
    retry_policy = Retry(
        total=num_retry,
        read=num_retry,
        connect=num_retry,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        # By default this is True. We set it to false to get the full error trace, including url and
        # status code of the last retry. Otherwise, the error message is 'too many 500 error responses',
        # which is not useful.
        raise_on_status=False
    )
    return retry_policy


def send_post_request(url, headers, payload):
    """Send a POST request."""
    with create_session_with_retry() as session:
        response = session.post(url, data=json.dumps(payload), headers=headers)
        # Raise an exception if the response contains an HTTP error status code
        response.raise_for_status()

    return response
