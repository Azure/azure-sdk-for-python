import os
from devtools_testutils import is_live

def email_decorator_async(func, **kwargs):
    async def wrapper(self, *args, **kwargs):
        if is_live():
            self.communication_connection_string = os.environ["COMMUNICATION_CONNECTION_STRING"]
            self.sender_address = os.environ["SENDER_ADDRESS"]
            self.recipient_address = os.environ["RECIPIENT_ADDRESS"]
        else:
            self.communication_connection_string = "endpoint=https://someEndpoint/;accesskey=someAccessKeyw=="
            self.sender_address = "someSender@contoso.com"
            self.recipient_address = "someRecipient@domain.com"
    
        EXPONENTIAL_BACKOFF = 1.5
        RETRY_COUNT = 0

        try:
            return await func(self, *args, **kwargs)
        except HttpResponseError as exc:
            if exc.status_code != 429:
                raise
            print("Retrying: {} {}".format(RETRY_COUNT, EXPONENTIAL_BACKOFF))
            while RETRY_COUNT < 6:
                if is_live():
                    time.sleep(EXPONENTIAL_BACKOFF)
                try:
                    return await func(self, *args, **kwargs)
                except HttpResponseError as exc:
                    print("Retrying: {} {}".format(RETRY_COUNT, EXPONENTIAL_BACKOFF))
                    EXPONENTIAL_BACKOFF **= 2
                    RETRY_COUNT += 1
                    if exc.status_code != 429 or RETRY_COUNT >= 6:
                        raise
    
    return wrapper
