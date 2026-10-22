# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import datetime
import requests
from azure.core.credentials import AccessToken


class StaticAccessTokenCredential(object):
    request_url: str

    def __init__(self, apikey, region):
        self.request_url = "https://{0}.api.cognitive.microsoft.com/sts/v1.0/issueToken?Subscription-Key={1}".format(
            region, apikey
        )

    def get_token(self, *audience, **kwargs):
        response = requests.post(self.request_url)
        access_token = response.content.decode("UTF-8")
        expires_on = datetime.datetime.now() + datetime.timedelta(days=1)
        return AccessToken(access_token, expires_on)
