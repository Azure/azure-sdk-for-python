# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: download_media.py

DESCRIPTION:
    This sample demonstrates receiving media from a Whatsapp message from business phone number. The NotificationMessageClient is 
    authenticated using a connection string.
USAGE:
    python download_media.py

    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS resource
"""

import os
import sys
from io import RawIOBase

sys.path.append("..")


class DownloadMediaSample(object):

    connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")

    def download_media(self):

        from azure.communication.messages import NotificationMessagesClient

        messaging_client = NotificationMessagesClient.from_connection_string(self.connection_string)
        input_media_id: str = "de7558b5-e169-4d47-9ba4-37a95c28f390"

        # calling send() with whatsapp message details
        media_stream = messaging_client.download_media(input_media_id)
        length: int = 0
        for byte in media_stream:
            length = length + 1
        print("WhatsApp Media stream downloaded.It's length is {}".format(length))


if __name__ == "__main__":
    sample = DownloadMediaSample()
    sample.download_media()
