# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

from devtools_testutils import is_live


def get_connection_str():
    if not is_live():
        return "endpoint=https://sanitized.communication.azure.com/;accesskey=fake==="
    return os.getenv("COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING") or os.getenv(
        "COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING"
    )


# class ChatURIReplacer(RecordingProcessor):
#     """Replace the identity in request uri"""
#     def process_request(self, request):
#         import re
#         request.uri = re.sub('/chat/threads/([^/?]+)', '/chat/threads/sanitized', request.uri)
#         request.uri = re.sub('/messages/([^/?]+)', '/messages/sanitized', request.uri)
#         request.uri = re.sub(r'syncState=([\d\w]+)', 'syncState=sanitized', request.uri)
#         return request

#     def process_response(self, response):
#         import re
#         if 'url' in response:
#             response['url'] = re.sub('/chat/threads/([^/?]+)', '/chat/threads/sanitized', response['url'])
#             response['url'] = re.sub('/messages/([^/?]+)', '/messages/sanitized', response['url'])
#             response['url'] = re.sub(r'syncState=([\d\w]+)', 'syncState=sanitized', response['url'])
#         return response
