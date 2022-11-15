# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from devtools_testutils import is_live

def email_decorator(func, **kwargs):
    def wrapper(self, *args, **kwargs):
        if is_live():
            self.communication_connection_string = os.environ["COMMUNICATION_CONNECTION_STRING_EMAIL"]
            self.sender_address = os.environ["SENDER_ADDRESS"]
            self.recipient_address = os.environ["RECIPIENT_ADDRESS"]
        else:
            self.communication_connection_string = "endpoint=https://someEndpoint/;accesskey=someAccessKeyw=="
            self.sender_address = "someSender@contoso.com"
            self.recipient_address = "someRecipient@domain.com"
    
        func(self, *args, **kwargs)

    return wrapper
